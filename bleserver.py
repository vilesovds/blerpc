
import pygatt
from queue import Queue
import logging
from pygatt.backends import BLEBackend, Characteristic, BLEAddressType

logging.basicConfig()
logging.getLogger('pygatt').setLevel(logging.DEBUG)


class BleRPCServer(object):
    def __init__(self):
        self.adapter = pygatt.GATTToolBackend()
        self.adapter.start()
        self.notifications_queue = Queue()

    def connect(address, timeout, type=BLEAddressType.random):
        self.device = self.adapter.connect(address, address_type=type)

    def notify_enable(self, uuid):
        self.device.subscribe(uuid, callback=self.handle_data)

    def indication_enable(self, uuid):
        self.device.subscribe(uuid, callback=self.handle_data, indication=True)
        
    def handle_data(self, handle, value):
        logging.debug("notification on handle: {}\n".format(handle))
        logging.debug('queueing data')
        logging.debug(value)
        self.notifications_queue.put(value)
