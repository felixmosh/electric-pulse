import machine
import time

onboard_led = machine.Pin("LED", machine.Pin.OUT)


def blink(times=1):
    global onboard_led

    for _x in range(times):
        onboard_led.value(1)
        time.sleep(0.25)
        onboard_led.value(0)
        time.sleep(0.25)
