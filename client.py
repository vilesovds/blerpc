from jsonrpcclient.http_client import HTTPClient
client  = HTTPClient('http://localhost:5001/')
response = client.request('scan',3)
print(response)
for gadget in response:
    if gadget['name'] == 'MI_SCALE':
        found=True
        address = str(gadget['address'])
        break
if not found:
    print('Mi scale not found')
    quit()

response = client.request('connect',address)
print(response)

response = client.request('is_mi_scale',address)
print(response)
if response!=True:
    print('It is not Mi Scale device')
    quit()

response = client.request('mi_scale_start_indication',address)
print(response)
input("stand on weight scale and press enter")
while True:
    response = client.request('mi_scale_get_weight_data',10)
    if 'Removed' == response['status']: break
    if 'Empty' != response:
        s = 'Mass: {0:.2f} {1:s}'.format(response['mass'],response['weight_units'])
        print(s)
        if response['status'] == 'Stable':
            result = s
if result:    
    print('resulted ',result)
#bye-bye
response = client.request('disconnect')
print(response)


