import uasyncio
import webapp
import os
import constants
import json
import _thread
from machine import Pin, Timer
import time
from counter import Counter

configs = {}
try:
    os.stat(constants.CONFIGS_FILE)

    # File was found, attempt to connect to wifi...
    with open(constants.CONFIGS_FILE) as f:
        wifi_current_attempt = 1
        configs = json.load(f)

except Exception:
    configs = {}


pulses_per_kwh = configs.get("pulsesPerKwh", constants.PULSES_FOR_KWH)
counter = Counter(pulses_per_kwh, 1222)
exit_counter_core_flag = False


def start_pulse():
    global counter, exit_counter_core_flag

    pulse = Pin(13, Pin.IN, Pin.PULL_UP)

    print("Electric meter started!")
    print("Current value %s" % counter)

    while not exit_counter_core_flag:
        before = pulse.value()
        time.sleep_ms(100)
        after = pulse.value()

        if before == 0 and after == 1:
            counter.inc()

            print("Counter: %d" % counter.value)
            print("Electric meter: %s" % (counter))
    _thread.exit()


_thread.start_new_thread(start_pulse, ())
# start_pulse()


def on_close():
    global exit_counter_core_flag
    exit_counter_core_flag = True
    time.sleep(1)


try:
    loop = uasyncio.get_event_loop()
    loop.create_task(webapp.start(configs, counter, on_close))
    loop.run_forever()
except KeyboardInterrupt:
    on_close()
