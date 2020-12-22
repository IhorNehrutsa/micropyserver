"""
Example 1

Needed ESP8266 or ESP32 board

@see https://github.com/troublegum/micropyserver
"""
import network
from amicropyserver import aMicroPyServer
from machine import Pin
import uasyncio as asyncio

PIN_NUMBER = 2
#wlan_id = "your wi-fi"
#wlan_pass = "your password"

wlan = network.WLAN(network.STA_IF)
#wlan.active(True)
#if not wlan.isconnected():
#    wlan.connect(wlan_id, wlan_pass)

print("wlan.ifconfig():", wlan.ifconfig())
print("wlan.isconnected():", wlan.isconnected())

pin = Pin(PIN_NUMBER, Pin.OUT, value=0)

async def show_index_page(swriter, request):
    await server.send(swriter, "THIS IS INDEX PAGE")


async def show_info_page(swriter, request):
    await server.send(swriter, "THIS IS INFO PAGE")


async def show_pin_page(swriter, request):
    if request.startswith("GET /on HTTP"):
        pin.value(1)
    elif request.startswith("GET /off HTTP"):
        pin.value(0)
    await server.send(swriter, "PIN IS " + ("ON" if pin.value() == 1 else "OFF"))


server = aMicroPyServer(host=wlan.ifconfig()[0], backlog=1)
server.add_route("/info", show_info_page)
server.add_route("/", show_index_page)
server.add_route("/on", show_pin_page)
server.add_route("/off", show_pin_page)


try:
    asyncio.run(server.start())
except KeyboardInterrupt:
    print('Interrupted')  # This mechanism doesn't work on Unix build.
finally:
    asyncio.run(server.close())
    _ = asyncio.new_event_loop()
