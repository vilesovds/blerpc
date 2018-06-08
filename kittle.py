import pygatt
import time
from binascii import hexlify
from pygatt.backends import BLEBackend, Characteristic, BLEAddressType
import logging
logging.basicConfig()
logging.getLogger('pygatt').setLevel(logging.DEBUG)

adapter = pygatt.GATTToolBackend()
new_data = False
def handle_data(handle, value):
    """
    handle -- integer, characteristic read handle the data was received on
    value -- bytearray, the data returned in the notification
    """
    global new_data
    print("Received data: %s" % hexlify(value))
    new_data = True

try:
    adapter.start()
    counter = 0
    device = adapter.connect('D0:12:5E:44:17:55',address_type=BLEAddressType.random)
#    device.char_write_handle(0x000e,[0x55,0x01,0xaa],True)
    device.subscribe("6e400003-b5a3-f393-e0a9-e50e24dcca9e",
                     callback=handle_data)
# auth
    #device.char_write_handle(0x000e,[0xaa,0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x08,0xff,counter,0x55],True)
    device.char_write_handle(0x000e,[0x55,counter,0xff,0xb5,0x4c,0x75,0xb1,0xb4,0x0c,0x88,0xef,0xaa])
    counter+=1
    while not new_data:
        time.sleep(0.1)
    new_data = False
    device.char_write_handle(0x000e,[0x55,counter,0x06,0xaa],True)
    counter+=1
    while not new_data:
        time.sleep(0.1)
    new_data = False
    device.char_write_handle(0x000e,[0x55,counter,0x50,0x00,0xaa],True)
    counter+=1
    while not new_data:
        time.sleep(0.1)
    new_data=False
    while(1):
        device.char_write_handle(0x000e,[0x55,counter,0x06,0xaa],True)
        counter+=1
        while not new_data:
           time.sleep(1)
        new_data=False

finally:
    adapter.stop()
