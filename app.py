import uasyncio
import webapp
import os
import constants
import json
import _thread

counter = {"current": 0, "prev": 0}

configs = None
try:
    os.stat(constants.CONFIGS_FILE)

    # File was found, attempt to connect to wifi...
    with open(constants.CONFIGS_FILE) as f:
        wifi_current_attempt = 1
        configs = json.load(f)

except Exception:
    configs = None

_thread.start_new_thread(
    pulse.start, (configs.get("pulsesPerKwh", constants.PULSES_FOR_KWH), i)
)

loop = uasyncio.get_event_loop()
loop.create_task(webapp.start(configs))
loop.run_forever()
