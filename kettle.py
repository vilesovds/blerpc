from jsonrpcserver import methods
from bleserver2 import *
from queue import Queue, Empty
from datetime import datetime
import logging

DEFAULT_TIMEOUT=5 #wait answer timeout by default

#protocol specific
START_BYTE = 0x55
END_BYTE = 0xaa
TEMP_POSITION=8
CMD_ANSWER_POSITION = 2
KETTLE_NOTIFY_UUID="6e400003-b5a3-f393-e0a9-e50e24dcca9e"
KETTLE_WRITE_HANDLE=0x000e
HEAT_ON_CMD = 0x03
GET_STATE_CMD = 0x06
AUTH_CMD = 0xFF

counter = 0 #commands counter

def parce_temp(data):
    """ Get temperature from state answer bytes"""
    if data[CMD_ANSWER_POSITION]==GET_STATE_CMD:
        return data[TEMP_POSITION]
    else:
        return 'None'

@methods.add
def kettle_get_temp(timeout,context):
    global counter
    context.device.char_write_handle(KETTLE_WRITE_HANDLE,[START_BYTE,counter,GET_STATE_CMD,END_BYTE])
    counter+=1
    try:
        data = context.notifications_queue.get(block=True, timeout=timeout)
        return parce_temp(data)
    except Empty:
        return 'None'

@methods.add
def kettle_heat_on(context):
    global counter
    context.device.char_write_handle(KETTLE_WRITE_HANDLE,[START_BYTE,counter,HEAT_ON_CMD,END_BYTE])
    counter+=1
    try:
        data = context.notifications_queue.get(block=True, timeout=DEFAULT_TIMEOUT)
        if data[CMD_ANSWER_POSITION]!=HEAT_ON_CMD:
            return 'Error'
    except Empty:
        return 'Timeout'
    return 'OK'

@methods.add
def kettle_auth(context):
    global counter
    context.device.char_write_handle(KETTLE_WRITE_HANDLE,[START_BYTE,counter,AUTH_CMD,0xb5,0x4c,0x75,0xb1,0xb4,0x0c,0x88,0xef,END_BYTE])
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
