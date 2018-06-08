from jsonrpcserver import methods
from jsonrpcserver.exceptions import InvalidParams, ServerError
from bleserver import *
from queue import Queue, Empty
from datetime import datetime
import logging

WEIGHT_SCALE_UUID='0000181d-0000-1000-8000-00805f9b34fb'
MI_WEIGHT_SCALE_NAME='MI_SCALE'
MI_SCALE_SERVICE_DESCRIPTOR_HANDLE = 0x20

MI_SCALE_FLAG_UNITS = 0x01
MI_SCALE_FLAG_DATETIME = 0x02
MI_SCALE_FLAG_STABLE = 0x20

MI_SCALE_FLAG_REMOVED = 0x80
def is_weight_scale(requester):
    ret = False
    primary = requester.discover_primary()
    #find weight scale service
    for prim in primary:
        if WEIGHT_SCALE_UUID == prim['uuid']:
            ret = True
            break
    return ret
@methods.add
def is_mi_scale(address, context):
    requester = context.requester
    try:
        requester.do_connect(address)
    except RuntimeError:
        raise ServerError()
        return False 
    #get device name
    data = requester.read_by_uuid("00002a00-0000-1000-8000-00805f9b34fb")[0]
    try:
        name = data.decode("utf-8")
    except AttributeError:
        name = data
    if is_weight_scale(requester) and name == MI_WEIGHT_SCALE_NAME:
        return True
    else:
        return False

def bleDataToDateTime(data):
    d = datetime.today()
    
    year = data[0]
    year += data[1]<<8
    
    month = data[2]
    day = data[3]
    
    
    hours = data[4]
    minutes = data[5]
    seconds = data[6]
    
    if year and month and day:
        d = datetime(year,month,day,hours,minutes,seconds)
    else:
        d.hour = hours
        d.minute = minutes
        d.second = seconds
    
    return d

def parce_weight(data):
    status = 'Unstable'
    flags = data[3]
    logging.debug('flags {:d}'.format(flags))
    if flags & MI_SCALE_FLAG_REMOVED : return {'status':'Removed'} #no 
    if flags & MI_SCALE_FLAG_DATETIME: #have datetime
        datetimedata = data[6:13]
    if flags & MI_SCALE_FLAG_STABLE: status = 'Stable'
    #get mass data
    mass = data[4] #low byte
    mass += data[5]<<8 #high byte
    if flags & MI_SCALE_FLAG_UNITS: # pound (lb) and inch (in) 
        wunits = "lb"
        mass = mass*0.01  
    else: #Kg and sm
        wunits = "kg"
        mass = mass *0.005
    logging.debug("Mass {0:f} {1:s}".format(mass,wunits))
    return {'status':status,'mass':mass,'weight_units':wunits,'datetime':bleDataToDateTime(datetimedata).isoformat()}

@methods.add
def mi_scale_get_weight_data(timeout,context):
    requester = context.requester
    results = []
    while(True):
        try:
            data = requester.indications_queue.get(block=True, timeout=timeout)
            parced  = parce_weight(data)
            results.append(parced)
            print(parced)
        except Empty:
            break;
    if 0 ==len(results):
       return 'None'
    else:
       return results 
    
@methods.add
def mi_scale_start_indication(address, context):
    requester = context.requester
    try:
        requester.do_connect(address)
    except RuntimeError:
        raise ServerError()
        return False 
    requester.set_interested_handle(0xFFFF)
    #indication enable
    requester.write16_by_handle(MI_SCALE_SERVICE_DESCRIPTOR_HANDLE,0x0002)
    return 'OK'

