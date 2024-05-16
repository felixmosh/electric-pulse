import asyncio
from machine import Pin, reset
import requests
import json
import _thread
import time
from app.lib.phew import disconnect_from_wifi, logging
import app.webapp as webapp
import app.constants as constants
from app.ota_updater import OTAUpdater
from app.counter import Counter

exit_counter_core_flag = False
counter = Counter(0)


def on_close():
    global exit_counter_core_flag
    exit_counter_core_flag = True
    time.sleep(1)


def start_pulse():
    global exit_counter_core_flag, counter
    pulse = Pin(5, Pin.IN, Pin.PULL_UP)

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


def update_initial_val_and_save(counter: Counter, configs: dict):
    configs["initialValue"] = counter.kwh()

    with open(constants.CONFIGS_FILE, "w") as f:
        json.dump(configs, f)
        f.close()


async def send_to_remote(counter: Counter, configs: dict, ota: OTAUpdater):
    delay_min = configs.get("reportInterval", 1)
    api = configs.get("api", {})
    url = access_token = api.get("endpoint", None)
    access_token = api.get("accessToken", None)

    if not url:
        logging.info("Api url is not defined")
        return
    if not access_token:
        logging.info("Api access_token is not defined")
        return

    logging.info(f"Remote server configured properly, url={url}")

    while True:
        await asyncio.sleep(delay_min * 60)
        try:
            update_initial_val_and_save(counter, configs)
            logging.info("Value saved locally: %s" % counter)
            resp = requests.post(
                f"{url}/api/meter/readings/add",
                headers={
                    "content-type": "application/json",
                    "authorization": f"Bearer {access_token}",
                },
                data=json.dumps(
                    {"value": counter.value, "version": ota.current_version}
                ),
                timeout=20,
            ).json()
            logging.info(resp)
            logging.info("Sent value to remote: %s" % counter)

            if ota.check_and_download():
                logging.info(f"New version found: {ota.latest_version}")
                raise KeyboardInterrupt

        except Exception as error:
            logging.error("An exception occurred: %s" % error)


def start(configs: dict, ota: OTAUpdater):
    global exit_counter_core_flag, counter

    counter.pulses_per_kwh = configs.get("pulsesPerKwh", constants.PULSES_FOR_KWH)
    counter.value = configs.setdefault("initialValue", 0) * counter.pulses_per_kwh

    # start_pulse()
    try:
        _thread.start_new_thread(start_pulse, ())
        loop = asyncio.get_event_loop()
        loop.create_task(webapp.start(configs, counter, on_close))
        loop.create_task(send_to_remote(counter, configs, ota))
        loop.run_forever()
    except KeyboardInterrupt as e:
        logging.info("External stop")
    except Exception as e:
        logging.error("Fatal error: %s" % e)
    finally:
        on_close()
        disconnect_from_wifi()
        reset()
