import pygatt
from jsonrpcserver import methods
from bleserver import BleRPCServer
from pygatt.backends import BLEAddressType
from scan import *
from weight_scale import *
from kettle import *
import time

import asyncio
import websockets


@methods.add
def ping(context=None):
    return 'pong'

@methods.add
def connect(address,timeout,type,context):
    if type==1:
        address_type=BLEAddressType.public
    else:
        address_type=BLEAddressType.random
    context.device = context.adapter.connect(str(address),timeout=timeout,address_type=address_type)
    return 'OK'

@methods.add
def disconnect(address,context):
    context.adapter.disconnect(connected_device=address)
    return True

@asyncio.coroutine    
def main(websocket, path):
    request = yield from websocket.recv()
    response = methods.dispatch(request,context=bleserver)
    if not response.is_notification:
        yield from websocket.send(str(response))

if __name__ == '__main__':
    bleserver = BleRPCServer()
    start_server = websockets.serve(main, '0.0.0.0', 5000)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

