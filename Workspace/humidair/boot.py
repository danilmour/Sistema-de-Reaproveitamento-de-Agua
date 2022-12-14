try:
    import usocket as socket
except:
    import socket
from machine import Pin
import network
import esp
import gc

esp.osdebug(None)

gc.collect()

ssid = '6ea6en6'
password = 'a4ae33324a96'

station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
    pass

print('Connection successful')
print(station.ifconfig())