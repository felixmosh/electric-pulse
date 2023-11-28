import asyncio
from machine import Pin
import requests
import json
import _thread
import time
from app.lib.phew import logging
import app.webapp as webapp
import app.constants as constants
from app.counter import Counter

exit_counter_core_flag = False
counter = Counter(0)


def on_close():
    global exit_counter_core_flag
    exit_counter_core_flag = True
    time.sleep(1)


def start_pulse():
    global exit_counter_core_flag, counter
    pulse = Pin(13, Pin.IN, Pin.PULL_UP)

    logging.info("Electric meter started!")
    logging.info("Current value %s" % counter)

    while not exit_counter_core_flag:
        if pulse.value() == 0:
            time.sleep_ms(25)
            if pulse.value() == 1:
                counter.inc()

                print("Counter: %d" % counter.value)
                print("Electric meter: %s" % (counter))
    _thread.exit()


async def send_to_remote(counter: Counter, configs):
    delay_min = configs.get("reportInterval", 1)
    api = configs.get("api", {})
    url = access_token = api.get("endpoint", None)
    access_token = api.get("accessToken", None)

    if url is None:
        print("Api url is not defined")
        return
    if access_token is None:
        print("Api access_token is not defined")
        return

    print(f"Remote server configured properly, url={url}")

    while True:
        await asyncio.sleep(delay_min * 60)
        post_data = {"value": counter.value}
        try:
            resp = requests.post(
                f"{url}/api/meter/readings/add",
                headers={
                    "content-type": "application/json",
                    "authorization": f"Bearer {access_token}",
                },
                data=json.dumps(post_data),
            ).json()
            logging.info(resp)
            logging.info("Sent value to remote: %s" % counter)
        except Exception as error:
            logging.error("An exception occurred:", error)


def start(configs):
    global exit_counter_core_flag, counter

    counter.pulses_per_kwh = configs.get("pulsesPerKwh", constants.PULSES_FOR_KWH)
    counter.value = configs.get("initialValue", 0) * counter.pulses_per_kwh

    _thread.start_new_thread(start_pulse, ())
    # start_pulse()

    try:
        loop = asyncio.get_event_loop()
        loop.create_task(webapp.start(configs, counter, on_close))
        loop.create_task(send_to_remote(counter, configs))
        loop.run_forever()
    except KeyboardInterrupt:
        on_close()
