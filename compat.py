import sys
import yaml

from packaging.version import Version
from packaging.specifiers import SpecifierSet, InvalidSpecifier

def load_file(driver):
    yaml_file = f"{driver}.yaml"

    with open(yaml_file, 'r') as file:
        return yaml.safe_load(file)

def check_compatibility(driver_d, driver_v, server_v):
    target_driver_v = Version(driver_v)

    for entry in driver_d['compatibility']:
        raw_range = entry['driver_version']

        try:
            spec = SpecifierSet(raw_range)
        except InvalidSpecifier:
            print(f"Skipping invalid range in YAML: {entry['driver_version']}")
            continue

        if target_driver_v in spec:
            matrix = entry['server_versions']
            for status in ['supported', 'partial', 'untested', 'unsupported']:
                if server_v in matrix.get(status, []):
                    return status

            return "unknown"

    return "version_not_in_manifest"


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python check.py <driver_name> <driver_version> <server_version>")
        sys.exit(1)

    driver_data = load_file(sys.argv[1])
    res = check_compatibility(driver_data, sys.argv[2], sys.argv[3])
    print(res)
