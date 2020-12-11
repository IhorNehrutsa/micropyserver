"""
Example 1

Needed ESP8266 or ESP32 board

@see https://github.com/troublegum/micropyserver
"""
import esp
import network
import usocket as socket
import uasyncio as asyncio
import time
import machine
from amicropyserver import aMicroPyServer

wlan_id = "your wi-fi"
wlan_pass = "your password"

wlan_id = "MikroTik_mAP"
wlan_pass = "1qazxsw2"

# wlan_id = "telecard208"
# wlan_pass = "208208208"

# wlan_id = "TP-LINK-359734"
# wlan_pass = "+380482359734"

wlan = network.WLAN(network.STA_IF)
if wlan.isconnected():
    print("  wlan.ifconfig():", wlan.ifconfig())
    wlan.disconnect()
    if not wlan.isconnected():
        print('wlan disconnected')
    
wlan.active(False)  # Comment out this line to throw an exception when wlan.ifconfig('dhcp') will execute 
#wlan.config (dhcp_hostname = "espressif12345")
wlan.active(True)
try:
    print("try: wlan.ifconfig('dhcp')", end=' ')
    wlan.ifconfig('dhcp')
    print("- Ok")
except Exception as e:
    print("")
    print(e)
    print(e.args[0])
    try:
        print("EspError:", EspError.err_to_name(EspError(), 0x5004))
    except:
        print(" Approve pull request #6638, https://github.com/micropython/micropython/pull/6638")
        print('  to see the "EspError: ESP_ERR_TCPIP_ADAPTER_DHCP_ALREADY_STARTED"')
    print("")
        
while not wlan.isconnected():
    wlan.connect(wlan_id, wlan_pass)

    print("  wlan.ifconfig():", wlan.ifconfig())
    print("  wlan.status():", wlan.status())
    
    machine.idle()
    time.sleep(1)

print("")
print("wlan.ifconfig():", wlan.ifconfig())
print("wlan.status():", wlan.status())
print("wlan.isconnected():", wlan.isconnected())
print("wlan.config('mac')", wlan.config('mac'))
print("wlan.config('essid')", wlan.config('essid'))
try:
    print("wlan.config('channel')", end=" ")
    print(wlan.config('channel'))
except Exception as e:
    print(e)
try:
    print("wlan.config('hidden')", end=" ")
    print(wlan.config('hidden'))
except Exception as e:
    print(e)
try:
    print("wlan.config('authmode')", end=" ")
    print(wlan.config('authmode'))
except Exception as e:
    print(e)
print("wlan.config('dhcp_hostname')", wlan.config('dhcp_hostname'))
wlan.config (dhcp_hostname = "espressif12345")
print("wlan.config('dhcp_hostname')", wlan.config('dhcp_hostname'))

print(socket.getaddrinfo(wlan.ifconfig()[0], 80)[0][-1])
print(socket.getaddrinfo('www.micropython.org', 80)[0][-1])
print(socket.getaddrinfo('micropython.org', 80)[0][-1])
print(socket.getaddrinfo('google.com', 80)[0][-1])
print(socket.getaddrinfo('127.0.0.1', 80)[0][-1])
try:
    #print("try: socket.getaddrinfo(wlan.config('dhcp_hostname'), 80)[0][-1]", end=' ')
    #print(socket.getaddrinfo(wlan.config('dhcp_hostname'), 80)[0][-1])
    print(socket.getaddrinfo('espressif12345', 80)[0][-1])
    #print("- Ok")
except Exception as e:
    print("")
    print(e)
    print(e.args[0])
    try:
        print("EspError:", EspError.err_to_name(EspError(), 202))
    except:
        print(" Approve pull request #6638, https://github.com/micropython/micropython/pull/6638")
        print('  to see the "EspError: ESP_ERR_TCPIP_ADAPTER_DHCP_ALREADY_STARTED"')
    print("")

while 1:
    time.sleep(1)


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
