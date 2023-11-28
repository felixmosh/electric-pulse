import math


class Counter:
    def __init__(self, pulses_per_kwh, initial_val=0):
        self.pulses_per_kwh = pulses_per_kwh
        self.value = initial_val

    def inc(self):
        self.value += 1

    def __str__(self):
        return "%.2f kWh" % (math.floor(self.value / self.pulses_per_kwh * 100) / 100)
