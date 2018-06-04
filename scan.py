from jsonrpcserver import methods 
from bleserver import GattRPCServer
import logging

@methods.add 
def scan(seconds,context):
    ret = []
    service = context.discoverservice 
    devices = service.discover(seconds)
    for address, name in list(devices.items()):
        logging.debug("name: {}, address: {}".format(name, address))
        ret.append({'address':address,'name':name})
    return ret