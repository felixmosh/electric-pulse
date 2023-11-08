import uasyncio
import webapp
import os
import constants
import json
import _thread
from machine import Pin
import time
from counter import Counter
import asyncio

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
initial_value = 2040
counter = Counter(pulses_per_kwh, initial_value)
exit_counter_core_flag = False


async def send_to_remote(counter: Counter, configs):
    delay_min = configs.get("reportInterval", 60)
    while True:
        await asyncio.sleep(delay_min * 60)
        print("Send value to remote: %s" % counter)


def start_pulse():
    global counter, exit_counter_core_flag

    pulse = Pin(13, Pin.IN, Pin.PULL_UP)

    print("Electric meter started!")
    print("Current value %s" % counter)

    while not exit_counter_core_flag:
        if pulse.value() == 0:
            time.sleep_ms(25)
            if pulse.value() == 1:
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
    loop.create_task(send_to_remote(counter, configs))
    loop.run_forever()
except KeyboardInterrupt:
    on_close()
