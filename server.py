from http.server import BaseHTTPRequestHandler, HTTPServer
from jsonrpcserver import methods
from bleserver import GattRPCServer
from scan import *
from weight_scale import *
import time

import asyncio
import websockets
#from jsonrpcserver.aio import methods
#from jsonrpcserver.response import NotificationResponse


DEVICE = 'hci0'

@methods.add
def ping(context=None):
    return 'pong'

@methods.add
def connect(address,context):
    return context.requester.do_connect(str(address))
@methods.add
def disconnect(context):
    context.requester.disconnect()
    while context.requester.is_connected():
        time.sleep(1)    
    return True

@asyncio.coroutine    
def main(websocket, path):
    request = yield from websocket.recv()
    response = methods.dispatch(request,context=bleserver)
    if not response.is_notification:
        yield from websocket.send(str(response))

class TestHttpServer(BaseHTTPRequestHandler):
    def do_OPTIONS(self):           
        self.send_response(200, "ok")       
        self.send_header('Access-Control-Allow-Origin', '*')                
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With")
    def do_POST(self):
        # Process request
        request = self.rfile.read(int(self.headers['Content-Length'])).decode()
        response = methods.dispatch(request,context=bleserver)
        # Return response
        self.send_response(response.http_status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(str(response).encode())


if __name__ == '__main__':
    bleserver = GattRPCServer(DEVICE)
    #HTTPServer(('localhost', 5001), TestHttpServer).serve_forever()
    
    start_server = websockets.serve(main, 'localhost', 5000)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
    #asyncio.get_event_loop().run_until_complete(start_server)
    #asyncio.get_event_loop().run_forever()
