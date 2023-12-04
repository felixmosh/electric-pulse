# electric-pulse
An electric pulse meter written on micropython, deployed with pi-pico w.

<img src='https://github.com/felixmosh/electric-pulse/assets/9304194/15ed22d7-46cf-4123-8d21-7fa3a5b6f437)https://github.com/felixmosh/electric-pulse/assets/9304194/15ed22d7-46cf-4123-8d21-7fa3a5b6f437' width='350'>


### Features
It has several features such as:
1. AccessPoint mode for config the meter
2. OTA updates based on Github Releases


### General info
The electric meter has 2 wire entries, which works like a switch, each time there is a "pulse" (close & open) of the switch, it means that there was an electric usage.
The meter in the image produces 800 (you can configure that to suite your meter) such pulses for 1kWh.

Then the device sends the counted value to a configured remote server once in X (can be configured) minutes.
