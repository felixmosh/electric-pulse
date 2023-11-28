import os
import json
import app.constants as constants
from app.lib.phew import logging
import app.index as app

configs = {}
version = "0.0.0"

try:
    os.stat(constants.CONFIGS_FILE)

    # File was found, attempt to connect to wifi...
    with open(constants.CONFIGS_FILE) as f:
        configs = json.load(f)
        f.close()

    with open(constants.VERSION_FILE) as f:
        version = f.readline()
        f.close()

except Exception:
    configs = {}

logging.info(f"Firmware version: {version}")

app.start(configs)
