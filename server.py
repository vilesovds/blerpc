from http.server import BaseHTTPRequestHandler, HTTPServer
from jsonrpcserver import methods
from bleserver import GattRPCServer
from scan import *
from weight_scale import *
import time
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
    
class TestHttpServer(BaseHTTPRequestHandler):
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
    HTTPServer(('localhost', 5001), TestHttpServer).serve_forever()