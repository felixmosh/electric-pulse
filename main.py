import os
import json
import app.constants as constants
from app.blink import blink
from app.lib.phew import logging
from app.ota_updater import OTAUpdater
import machine

configs = {}
version = "v0.0.0"

blink(3)

try:
    os.stat(constants.CONFIGS_FILE)

    # File was found, attempt to connect to wifi...
    with open(constants.CONFIGS_FILE, "r") as f:
        configs: dict = json.load(f)
        f.close()

    if constants.VERSION_FILE in os.listdir("./"):
        with open(constants.VERSION_FILE, "r") as f:
            version = f.readline()
            f.close()

except Exception:
    pass

logging.info(f"Firmware version: {version}")
configs["version"] = version

ota = OTAUpdater(constants.RELEASE_REPO, current_version=version)

if ota.apply_update():
    print("Resetting...")
    machine.reset()
else:
    import app.index as app

    app.start(configs, ota)
