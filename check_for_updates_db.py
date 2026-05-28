from bson.codec_options import CodecOptions
from datetime import datetime, timezone
from packaging.version import parse
from pymongo import MongoClient

import requests
import os

ORG = "mongodb"

DRIVER_REPOS = [
    "mongo-csharp-driver",
    "mongo-c-driver",
    "mongo-cxx-driver",
    "mongo-go-driver",
    "mongo-java-driver",
    "mongo-php-library",
    "mongo-python-driver",
    "mongo-ruby-driver",
    "mongo-rust-driver",
    "node-mongodb-native",
]

client = MongoClient(os.environ["MONGO_URI"])
options = CodecOptions(tz_aware = True)
db = client["compat"]
coll_checkpoint = db.get_collection("checkpoints", options)
coll_releases = db.get_collection("releases", options)

for repo in DRIVER_REPOS:
    url = f"https://api.github.com/repos/{ORG}/{repo}/releases"
    last_published_at = None

    # It seems the GitHub API will send a compressed response by default,
    # but no harm requesting it explicitly
    headers = {
        "Accept-Encoding": "gzip",
    }

    print(f"#### {repo}")

    resp = requests.get(url, headers=headers)
    resp.raise_for_status()

    result = coll_checkpoint.find_one({"name": repo})

    if result:
        checkpoint_published_at = result["last_published_at"]
    else:
        checkpoint_published_at = datetime(1970, 1, 1, tzinfo=timezone.utc)

    # GitHub returns releases newest-first. We filter to only unseen releases, then
    # reverse so we process oldest-first. This lets us advance the checkpoint
    # incrementally -- if parsing fails mid-way, we break and retry from there on
    # the next run rather than skipping the failed entry.
    new_releases = [r for r in resp.json() if datetime.fromisoformat(r["published_at"]) > checkpoint_published_at]

    for r in reversed(new_releases):
        try:
            if r["prerelease"] == True:
                last_published_at = datetime.fromisoformat(r["published_at"])
                continue

            if repo in ("mongo-java-driver", "mongo-cxx-driver"):
                tmp_version = r["tag_name"].lstrip("r")
            else:
                tmp_version = r["tag_name"]

            version = parse(tmp_version)

            coll_releases.insert_one({"name": repo, "version": str(version), "published_at": datetime.fromisoformat(r["published_at"])})
            print(f"[{version}] newer version found")
            last_published_at = datetime.fromisoformat(r["published_at"])
        except Exception as e:
	        print(f"[{r['tag_name']}] failed to parse: {e}")
	        break  # stop so we don't skip over the failed entry

    if last_published_at is not None:
        coll_checkpoint.update_one({"name": repo}, {"$set": {"last_published_at": last_published_at}}, upsert=True)
