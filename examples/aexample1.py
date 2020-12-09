"""
Example 1

Needed ESP8266 or ESP32 board

@see https://github.com/troublegum/micropyserver
"""
import esp
import network
from amicropyserver import aMicroPyServer
import uasyncio as asyncio

wlan_id = "MikroTik_mAP"  # "your wi-fi"
wlan_pass = "1qazxsw2"  # "your password"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    wlan.connect(wlan_id, wlan_pass)


def show_index_page(request):
    server.send("THIS IS INDEX PAGE")


def show_info_page(request):
    server.send("THIS IS INFO PAGE")


server = aMicroPyServer()
server.add_route("/info", show_info_page)
server.add_route("/", show_index_page)

try:
    asyncio.run(server.start())
except KeyboardInterrupt:
    print('Interrupted')  # This mechanism doesn't work on Unix build.
finally:
    _ = asyncio.new_event_loop()
