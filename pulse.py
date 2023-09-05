from machine import Pin
import time
import constants

led = Pin("LED", Pin.OUT)
pulse = Pin(13, Pin.IN, Pin.PULL_UP)

counter = 0
counter_old = 0


def blink():
    global led

    led.value(1)
    time.sleep(0.15)
    led.value(0)
    time.sleep(0.15)


def pulse_interrupt_handler(_pin):
    global counter
    counter += 1


def main():
    global counter, counter_old, pulse

    print("Eelectric meter started!")
    for _x in range(5):
        blink()

    pulse.irq(trigger=Pin.IRQ_FALLING, handler=pulse_interrupt_handler)
    
    while True:
        if counter != counter_old:
            counter_old = counter
            print("Counter: %d" % counter)
            print("Electric meter: %.2f kWh" % (counter / constants.PULSES_FOR_KWH))

            blink()


main()
