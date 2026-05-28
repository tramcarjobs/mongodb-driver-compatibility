from flask import Flask, Response
from pymongo import MongoClient
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString

from compat import check_compatibility, load_file

import os

app = Flask(__name__)

client = MongoClient(os.environ["MONGO_URI"])
db = client["compat"]
coll_releases = db.get_collection("releases")

try:
    driver_data = {
        "c": load_file("c"),
        "cxx": load_file("cxx"),
        "csharp": load_file("csharp"),
        "go": load_file("go"),
        "java": load_file("java"),
        "nodejs": load_file("nodejs"),
        "php": load_file("php"),
        "pymongo": load_file("pymongo"),
        "ruby": load_file("ruby"),
        "rust": load_file("rust"),
    }
except FileNotFoundError as e:
    raise RuntimeError(f"Missing compatibility file: {e}") from e

@app.route("/rss.xml")
def rss():
    releases = coll_releases.find({}, {"_id": 0}).sort("published_at", -1).limit(10)

    xml = build_rss(list(releases))

    return Response(xml, mimetype="application/rss+xml")

@app.route("/<driver>/<driver_version>/<server_version>")
def compat(driver, driver_version, server_version):
    data = driver_data.get(driver)

    if data is None:
        return { "status": "unknown driver" }, 404

    res = check_compatibility(data, driver_version, server_version)

    return { "status": res }

def build_rss(releases):
    rss = Element("rss", version="2.0", attrib={"xmlns:atom": "http://www.w3.org/2005/Atom"})
    channel = SubElement(rss, "channel")

    SubElement(channel, "title").text = "MongoDB Driver Releases"
    SubElement(channel, "link").text = "https://github.com/tramcarjobs/mongodb-driver-compatibility"
    SubElement(channel, "description").text = "New MongoDB driver releases"
    SubElement(channel, "atom:link", attrib={"href": "https://github.com/tramcarjobs/mongodb-driver-compatibility/rss.xml", "rel": "self", "type": "application/rss+xml"})

    for release in releases:
        item = SubElement(channel, "item")
        SubElement(item, "title").text = f"{release['name']} {release['version']}"
        SubElement(item, "pubDate").text = release["published_at"].strftime("%a, %d %b %Y %H:%M:%S +0000")
        SubElement(item, "guid", isPermaLink="false").text = f"{release['name']}-{release['version']}"

    xml = parseString(tostring(rss)).toprettyxml(indent="  ")
    return xml
