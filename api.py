from flask import Flask

from compat import check_compatibility, load_file

app = Flask(__name__)

try:
    driver_data = {
        "c": load_file("c"),
        "cxx": load_file("cxx"),
        "csharp": load_file("csharp"),
        "go": load_file("go"),
        "java": load_file("java"),
        "nodejs": load_file("nodejs"),
        "pymongo": load_file("pymongo"),
        "ruby": load_file("ruby"),
        "rust": load_file("rust"),
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
