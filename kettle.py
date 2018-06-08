from jsonrpcserver import methods
from bleserver2 import *
from queue import Queue, Empty
from datetime import datetime
import logging

TEMP_POSITION=8
KETTLE_NOTIFY_UUID="6e400003-b5a3-f393-e0a9-e50e24dcca9e"
HEAT_ON_CMD = 0x03
GET_STATE_CMD
DEFAULT_TIMEOUT=5 #wait answer timeout by default
counter = 0 #commands counter

def parce_temp(data):
    if data[2]==GET_STATE_CMD:
        return data[TEMP_POSITION]
    else:
        return 'None'

@methods.add
def kettle_get_temp(timeout,context):
    global counter
    context.device.char_write_handle(0x000e,[0x55,counter,GET_STATE_CMD,0xaa])
    counter+=1
    try:
        data = context.notifications_queue.get(block=True, timeout=timeout)
        return parce_temp(data)
    except Empty:
        return 'None'

@methods.add
def kettle_heat_on(context):
    global counter
    context.device.char_write_handle(0x000e,[0x55,counter,HEAT_ON_CMD,0xaa])
    counter+=1
    try:
        data = context.notifications_queue.get(block=True, timeout=DEFAULT_TIMEOUT)
        if data[2]!=HEAT_ON_CMD:
            return 'Error'
    except Empty:
        return 'Timeout'
    return 'OK'

@methods.add
def kettle_auth(context):
    global counter
    context.device.char_write_handle(0x000e,[0x55,counter,0xff,0xb5,0x4c,0x75,0xb1,0xb4,0x0c,0x88,0xef,0xaa])
    counter+=1
    while True:
        try:
            data = context.notifications_queue.get(block=True, timeout=DEFAULT_TIMEOUT)
            break
        except Empty:
            return 'No auth'
#todo parce data
    return 'OK'

@methods.add
def kettle_start_notifications(context):
   context.notify_enable(KETTLE_NOTIFY_UUID)
   return 'OK'
