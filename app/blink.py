import machine
import time

onboard_led = machine.Pin("LED", machine.Pin.OUT)


def blink(times=1, type="short"):
    global onboard_led

    blink_delay = 0.25
    if type == "long":
        blink_delay = 0.75

    for _x in range(times):
        onboard_led.value(1)
        time.sleep(blink_delay)
        onboard_led.value(0)
        time.sleep(0.25)
