from jsonrpcserver import methods 
from bleserver2 import BleRPCServer
import logging

@methods.add 
def scan(timeout,context): 
    return context.adapter.scan(timeout=timeout, run_as_root=True)
