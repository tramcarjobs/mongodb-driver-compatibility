from flask import Flask

from compat import check_compatibility

app = Flask(__name__)

@app.route("/<driver>/<driver_version>/<server_version>")
def compat(driver, driver_version, server_version):
    res = check_compatibility(driver_version, server_version, f"{driver}.yaml")
    return f"<p>{res}</p>"
