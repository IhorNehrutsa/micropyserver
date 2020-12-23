"""
Example 1

Needed ESP8266 or ESP32 board

@see https://github.com/troublegum/micropyserver
"""
import esp
import network
from micropyserver import MicroPyServer
from machine import Pin

PIN_NUMBER = 2
wlan_id = "your wi-fi"
wlan_pass = "your password"

wlan = network.WLAN(network.STA_IF)
# wlan.active(True)
# if not wlan.isconnected():
#     wlan.connect(wlan_id, wlan_pass)

print("wlan.ifconfig():", wlan.ifconfig())
print("wlan.isconnected():", wlan.isconnected())

pin = Pin(PIN_NUMBER, Pin.OUT, value=0)


def show_index_page(request):
    server.send("THIS IS INDEX PAGE")


def show_info_page(request):
    server.send("THIS IS INFO PAGE")


def show_pin_page(request):
    if request.startswith("GET /on HTTP"):
        pin.value(1)
    elif request.startswith("GET /off HTTP"):
        pin.value(0)
    server.send("PIN IS " + ("ON" if pin.value() == 1 else "OFF"))


server = MicroPyServer()
server.add_route("/info", show_info_page)
server.add_route("/", show_index_page)
server.add_route("/on", show_pin_page)
server.add_route("/off", show_pin_page)
server.start()
