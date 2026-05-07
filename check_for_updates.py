from packaging.version import parse

import json
import requests

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

    try:
        with open(f"{repo}.json", "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {
            "last_published_at": "1970-01-01 00:00:00Z",
            "versions": {}
        }

    # GitHub returns releases newest-first. We filter to only unseen releases, then
    # reverse so we process oldest-first. This lets us advance the checkpoint
    # incrementally -- if parsing fails mid-way, we break and retry from there on
    # the next run rather than skipping the failed entry.
    new_releases = [r for r in resp.json() if r["published_at"] > data["last_published_at"]]

    for r in reversed(new_releases):
        try:
            if r["prerelease"] == True:
                continue

            if repo in ("mongo-java-driver", "mongo-cxx-driver"):
                tmp_version = r["tag_name"].lstrip("r")
            else:
                tmp_version = r["tag_name"]

            version = parse(tmp_version)

            maj_min = f"{version.major}.{version.minor}"
            if maj_min in data["versions"]:
                if version > parse(data["versions"][maj_min]["latest"]):
                    data["versions"][maj_min]["latest"] = str(version)
                    data["versions"][maj_min]["published_at"] = r["published_at"]
            else:
                data["versions"][maj_min] = {
                    "published_at": r["published_at"],
                    "latest": str(version)
                }
            print(f"[{version}] newer version found")
            last_published_at = r["published_at"]
        except Exception as e:
	        print(f"[{r['tag_name']}] failed to parse: {e}")
	        break  # stop so we don't skip over the failed entry

    if last_published_at is not None:
        data["last_published_at"] = last_published_at
        with open(f"{repo}.json", "w") as file:
            json.dump(data, file, indent=4)
