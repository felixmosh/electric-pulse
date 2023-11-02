from phew import access_point, connect_to_wifi, is_connected_to_wifi, dns, server
from phew.template import render_template
import constants
import json
import machine
import os
import utime
import _thread
import uasyncio

onboard_led = machine.Pin("LED", machine.Pin.OUT)


def blink(times=1):
    global onboard_led

    for _x in range(times):
        onboard_led.value(1)
        utime.sleep(0.25)
        onboard_led.value(0)
        utime.sleep(0.25)


def machine_reset():
    utime.sleep(1)
    print("Resetting...")
    machine.reset()


@server.route("/assets/<filename>")
def static_assets(request, filename=""):
    if filename:
        allowed_extensions = [".js", ".css"]
        is_allowed_ext = False
        for extension in allowed_extensions:
            if filename.endswith(extension):
                is_allowed_ext = True
                break

        if is_allowed_ext:
            return server.FileResponse(f"{constants.ASSETS_PATH}/{filename}")

    return "Not found.", 404


def setup_mode():
    print("Entering setup mode...")

    @server.route("/")
    def ap_index(request):
        if request.headers.get("host").lower() != constants.AP_DOMAIN.lower():
            return server.redirect(constants.AP_DOMAIN.lower())

        return server.FileResponse(f"{constants.AP_TEMPLATE_PATH}/index.html")

    @server.route("/configure", ["POST"])
    def ap_configure(request):
        print("Saving config... %s" % json.dumps(request.data))

        with open(constants.CONFIGS_FILE, "w") as f:
            json.dump(request.data, f)
            f.close()

        # Reboot from new thread after we have responded to the user.
        _thread.start_new_thread(machine_reset, ())
        return {"status": 1}

    @server.catchall()
    def ap_catch_all(request):
        if request.headers.get("host") != constants.AP_DOMAIN:
            return render_template(
                f"{constants.AP_TEMPLATE_PATH}/redirect.html",
                domain=constants.AP_DOMAIN,
            )

        return "Not found.", 404

    ap = access_point(constants.APP_NAME)
    ip = ap.ifconfig()[0]
    dns.run_catchall(ip)


def application_mode(configs):
    global onboard_led
    print("Entering application mode.")

    auth_middleware = None
    ui = configs.get("ui")
    if ui.get("username") and ui.get("password"):
        auth_middleware = server.basic_auth(
            username=ui.get("username"),
            password=ui.get("password"),
            realm=constants.APP_NAME,
        )

    @server.route("/", middleware=auth_middleware)
    def app_index(request):
        return server.FileResponse(f"{constants.APP_TEMPLATE_PATH}/index.html")

    @server.route("/toggle", middleware=auth_middleware)
    def app_toggle_led(request):
        onboard_led.toggle()
        return "OK"

    @server.route("/temperature", middleware=auth_middleware)
    def app_get_temperature(request):
        # Not particularly reliable but uses built in hardware.
        # Demos how to incorporate senasor data into this application.
        # The front end polls this route and displays the output.
        # Replace code here with something else for a 'real' sensor.
        # Algorithm used here is from:
        # https://www.coderdojotc.org/micropython/advanced-labs/03-internal-temperature/
        sensor_temp = machine.ADC(4)
        reading = sensor_temp.read_u16() * (3.3 / (65535))
        temperature = 27 - (reading - 0.706) / 0.001721
        return f"{round(temperature, 1)}"

    @server.route("/reset", middleware=auth_middleware)
    def app_reset(request):
        # Deleting the WIFI configuration file will cause the device to reboot as
        # the access point and request new configuration.
        os.remove(constants.CONFIGS_FILE)
        # Reboot from new thread after we have responded to the user.
        _thread.start_new_thread(machine_reset, ())
        return render_template(
            f"{constants.APP_TEMPLATE_PATH}/reset.html",
            access_point_ssid=constants.APP_NAME,
        )

    @server.catchall()
    def app_catch_all(request):
        return "Not found.", 404


def start(configs):
    # Figure out which mode to start up in...
    if configs is not None and "wifi" in configs:
        wifi_current_attempt = 1

        while wifi_current_attempt <= constants.WIFI_MAX_ATTEMPTS:
            blink(wifi_current_attempt)
            wifi = configs.get("wifi")
            ssid = wifi.get("ssid")
            wifi_password = wifi.get("password")
            print(f"Connecting to wifi, ssid {ssid}, attempt {wifi_current_attempt}")

            ip_address = connect_to_wifi(ssid, wifi_password)

            if is_connected_to_wifi():
                print(f"Connected to wifi, IP address {ip_address}")
                break
            else:
                wifi_current_attempt += 1

        if is_connected_to_wifi():
            application_mode(configs)
        else:
            # Bad configuration, delete the credentials file, reboot
            # into setup mode to get new credentials from the user.
            print("Bad wifi connection!")
            print(configs)
            os.remove(constants.CONFIGS_FILE)
            machine_reset()
    else:
        # Either no wifi configuration file found, or something went wrong,
        # so go into setup mode.
        blink(constants.WIFI_MAX_ATTEMPTS + 1)
        setup_mode()

    # Start the web server...
    return server.start()
