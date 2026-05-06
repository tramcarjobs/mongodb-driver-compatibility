from flask import Flask

from compat import check_compatibility, load_file

app = Flask(__name__)

try:
    driver_data = {
        "c": load_file("c"),
        "java": load_file("java"),
    }
except FileNotFoundError as e:
    raise RuntimeError(f"Missing compatibility file: {e}") from e

@app.route("/<driver>/<driver_version>/<server_version>")
def compat(driver, driver_version, server_version):
    data = driver_data.get(driver)

    if data is None:
        return "<p>unknown driver</p>", 404

    res = check_compatibility(data, driver_version, server_version)

    return f"<p>{res}</p>"
