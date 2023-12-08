import network
import time
import webrepl

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("MySSID", "NotMyPasswordSorry")
for i in range(10):
    if wlan.isconnected():
        break
    time.sleep(1)

print(wlan.ifconfig())

webrepl.start()
