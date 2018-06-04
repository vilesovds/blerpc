from gattlib import GATTRequester
from gattlib import DiscoveryService
from queue import Queue
import logging

class Requester(GATTRequester):
    def __init__(self, indications_queue, device):
        self.device=device
        GATTRequester.__init__(self, '00:00:00:00:00:00',False,device)
        self.indications_queue = indications_queue
        #self._connected = False
        self.interested_handle = 0xFFFF
    def do_connect(self,address):
        if self.is_connected() and address != self._address:
            self.disconnect()
            #self._connected = False
        self._address = address
        if not self.is_connected():
            self.change_address(address)
            self.connect(True)
            self.indications_queue.queue.clear()
            #self._connected = True
        return True
    def set_interested_handle(self, handle):
        self.interested_handle = handle
    def on_indication(self, handle, data):
        logging.debug("- indication on handle: {}\n".format(handle))
        if self.interested_handle==0xFFFF or self.interested_handle == handle:
            logging.debug('queueing data')
            logging.debug(data)
            self.indications_queue.put(data)

class GattRPCServer(object):
    def __init__(self,device='hci0'):
        logging.basicConfig(level=logging.DEBUG)
    
        self.discoverservice = DiscoveryService(device)
        self.indications_queue=Queue()
        self.requester = Requester(self.indications_queue, device)