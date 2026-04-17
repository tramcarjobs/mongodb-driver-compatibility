import sys
import yaml

from packaging.version import Version
from packaging.specifiers import SpecifierSet, InvalidSpecifier

def check_compatibility(driver_v, server_v, yaml_file):
    try:
        with open(yaml_file, 'r') as file:
            data = yaml.safe_load(file)

        target_driver_v = Version(driver_v)

        for entry in data['compatibility']:
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
    except FileNotFoundError:
        return "error: yaml file not found"
    except Exception as e:
        return f"error: {str(e)}"


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python check.py <driver_name> <driver_version> <server_version>")
        sys.exit(1)

    res = check_compatibility(sys.argv[2], sys.argv[3], f"{sys.argv[1]}.yaml")
    print(res)
