# MongoDB Driver Compatibility

This project is an initial attempt to "codify" MongoDB's [Client Library Compatibility Tables](https://www.mongodb.com/docs/drivers/compatibility/).

The `compat.py` Python script provides a basic implementation of how to use this data:

```
python3 -m venv .venv3
source .venv3/bin/activate
pip install -r requirements.txt
python3 compat.py <driver_name> <driver_version> <server_version>
```

The `check_for_updates.py` Python script monitors different driver releases for updates.
