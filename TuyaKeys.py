#!./venv/bin/python3

# Python Script to extract Local API Keys from Tuya Cloud API
# Streamlines Local Tuya Setup

import json
import pandas as pd
from tuya_connector import TuyaOpenAPI

# Add your ACCESS_ID and ACCESS_SECRET to auth_template.py and save it as auth.py
from auth import ACCESS_ID, ACCESS_SECRET, API_ENDPOINT

# Instantiate the Tuya API Session
openapi = TuyaOpenAPI(API_ENDPOINT, ACCESS_ID, ACCESS_SECRET)
openapi.connect()

#Load input.CSV into a Dataframe
input_df = pd.read_csv('input.csv')
# Convert the "device_id" Column of the Dataframe into a list for our lookups later
devices = input_df.device_id.to_list()

# print(devices)

def get_local_keys(device_id):
    params = {'device_ids': device_id}
    data = openapi.get(f"/v2.0/cloud/thing/{device_id}")
    if data['success'] == False:
        print(f'Something went wrong with cloud/thing/{device_id}')
        return None

    factory_device = { 'mac': 'NOT FOUND', 'sn': 'NOT FOUND' }
    # Get RAW mac Address Data from Tuya API
    try:
        factory_data = openapi.get(f"/v1.0/devices/factory-infos", params=params)
        factory_device = factory_data['result'][0]
    except TypeError as tex:
        print(f' {device_id} Something went wrong with /v1.0/devices/factory-infos {tex}')
    except KeyError as kex:
        print(f' {device_id} Something went wrong with /v1.0/devices/factory-infos {kex}')
    except IndexError as iex:
        print(f' {device_id} Something went wrong with /v1.0/devices/factory-infos {iex}')

    pin_data = ''
    try:
        pin_data = openapi.get(f'/v1.1/devices/{device_id}/specifications')['result']
    except KeyError:
        print(f"No Pin data for this device: {device_id}")

    with open(f'pinouts-{device_id}.json', 'w') as outfile:
        json.dump(pin_data, outfile, indent=4)

    result = data['result']
    output_data = {
        'device_id': device_id,
        'bind_space_id': result.get('bind_space_id', ''),
        'category': result.get('category'),
        'custom_name': result.get('custom_name', ''),
        'icon': result.get('icon', ''),
        'id': result.get('id', ''),
        'ip': result.get('ip', ''),
        'is_online': result.get('is_online', ''),
        'lat': result.get('lat', ''),
        'local_key': result.get('local_key', ''),
        'lon': result.get('lon', ''),
        'mac': factory_device.get('mac',''),
        'model': result.get('model', ''),
        'name': result.get('name', ''),
        'product_id': result.get('product_id', ''),
        'product_name': result.get('product_name', ''),
        'sn': factory_device.get('sn', ''),
        'sub': result.get('sub', ''),
        'time_zone': result.get('time_zone', ''),
        'uuid': result.get('uuid', '')
    }

    print(f"{output_data['device_id']}\t{output_data['local_key']}\t{output_data['mac']}\t{output_data['uuid']}\t{output_data['custom_name']}")

    try:
        for index, pin in enumerate(pin_data['functions']):
            output_data[f'Function {index} code'] = pin['code']
            output_data[f'Function {index} pin'] = pin['dp_id']
            output_data[f'Function {index} type'] = pin['type']
            output_data[f'Function {index} values'] = pin['values']
    except TypeError as te:
        print(f" {device_id} Function Error {te}")
    except KeyError as kex:
        print(f" {device_id} KeyError {kex}")

    try:
        for index, pin in enumerate(pin_data['status']):
            output_data[f'Status {index} code'] = pin['code']
            output_data[f'Status {index} pin'] = pin['dp_id']
            output_data[f'Status {index} type'] = pin['type']
            output_data[f'Status {index} values'] = pin['values']
    except TypeError as te:
        print(f" {device_id} Status Error {te}")
    except KeyError as kex:
        print(f" {device_id} Status KeyError {kex}")

    return output_data

device_list = []

for device in devices:
    device_list.append(get_local_keys(device))

df = pd.DataFrame(device_list)
df.to_csv('./local_tuya.csv', index=False)