#!./.venv/bin/python

import asyncio
import websockets
import json
import argparse
import re
import requests
from requests.auth import HTTPBasicAuth
import time
import subprocess
import os

user = 'kismet'
password = 'kismet'


python_file_path = os.path.abspath(__file__)
angypython_dir = os.path.dirname(python_file_path)
angypack_dir = os.path.dirname(angypython_dir)
SERVICE_DIR = "/etc/systemd/system"
WORKING_DIR = f"{angypack_dir}/logs"
OUTPUT_DIR = f"{angypack_dir}/output"
LOG_DIR = os.path.expanduser(f'{WORKING_DIR}/handshakes')


def is_mac_address(s):
    """
    Check if the string is a valid MAC address.
    A MAC address has the format: XX:XX:XX:XX:XX:XX where X is a hexadecimal digit.
    """
    
    mac_regex = r'^([0-9a-fA-F]{2}[-:.]){5}[0-9a-fA-F]{2}$'
    
    return bool(re.match(mac_regex, s))

async def find_target(target, type):
    uri = f"ws://localhost:2501/eventbus/events.ws?user={user}&password={password}"
    async with websockets.connect(uri) as ws:

        print("Connected.")
        req = {"SUBSCRIBE": "DOT11_ADVERTISED_SSID"}
        await ws.send(json.dumps(req))
        async for msg in ws:
            json_data = json.loads(msg)
            ad_bssid_data = json_data.get("DOT11_NEW_SSID_BASEDEV")
            ad_ssid_data = json_data.get("DOT11_ADVERTISED_SSID")
            ssid = ad_ssid_data.get("dot11.advertisedssid.ssid")
            bssid = ad_bssid_data.get("kismet.device.base.macaddr")
            if type == 's':
                if target.lower() in ssid.lower():
                    return ssid
            elif type == 'b':
                if target.lower() in bssid.lower():
                    return bssid

def scan_target(target, type):
    
    if type == 's':
        url1 = "http://localhost:2501/phy/phy80211/ssids/views/ssids.json"
    elif type == 'b':
        url1 = f"http://localhost:2501/devices/by-mac/{target}/devices.json"

    response1 = requests.get(
        f'{url1}',
        auth=HTTPBasicAuth(user,password)
    )

    response1.raise_for_status()
    ssid_bssid_pairs = []

    def scan_by_key(key):
        response2 = requests.get(
            f'http://localhost:2501/devices/by-key/{key}/device.json',
            auth=HTTPBasicAuth(user,password)
        )
        response2.raise_for_status()
        data1 = response2.json()
        keydata = response2.json().get("dot11.device")
        bssid = keydata.get("dot11.device.last_bssid")
        channel = data1.get("kismet.device.base.channel")
        rssidata = response2.json().get("kismet.device.base.signal")
        rssi = rssidata.get("kismet.common.signal.last_signal")
        manuf = data1.get("kismet.device.base.manuf")
        sec = data1.get("kismet.device.base.crypt")
        locdata = data1.get("kismet.device.base.location", None)
        if locdata is not None:
            avg_loc = locdata.get("kismet.common.location.avg_loc")
            geopoint = avg_loc.get("kismet.common.location.geopoint")
            lat = geopoint[0]
            lon = geopoint[1]
        else:
            lat = "no fix"
            lon = "no fix"
        clientnum = keydata.get("dot11.device.num_associated_clients")
        ssid_bssid_pairs.append((ssid, bssid, channel, rssi, time_diff, manuf, sec, clientnum, lat, lon))

    
   
    if response1.status_code == 200:
        
        data = response1.json()
        
        if type == 's':
            for item in data:
                last_time = item.get("dot11.ssidgroup.last_time")
                current_time = int(time.time())
                time_diff = current_time - last_time
                queried_ssid = item.get("dot11.ssidgroup.ssid")
                if target.lower() in queried_ssid.lower():
                    ssid = queried_ssid
                    devkeys = item.get("dot11.ssidgroup.advertising_devices")
                    for devkey in devkeys:
                        devkey = devkey.strip("[]'")
                        scan_by_key(devkey)
        elif type == 'b':
            for item in data:
                dot11device = item.get("dot11.device").get("dot11.device.last_beaconed_ssid_record")
                last_time = item.get("kismet.device.base.last_time")
                current_time = int(time.time())
                time_diff = current_time - last_time
                ssid = dot11device.get("dot11.advertisedssid.ssid")
                devkey = item.get("kismet.device.base.key")
                devkey = devkey.strip("[]'")
                scan_by_key(devkey)

    return ssid_bssid_pairs


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('target')
    args = parser.parse_args()
    print(args)
    target = args.target


    subprocess.run(['rm', '-f', f"{OUTPUT_DIR}/foundtargets.txt"], check=True)
    subprocess.run(['systemctl', 'start', "targetreport"], check=True)

    if is_mac_address(target):
        if not scan_target(target,'b'):
            ssid = asyncio.run(find_target(target,'b'))
            scan_results = scan_target(target,'b')
        else:
            scan_results = scan_target(target,'b')
    else:
        if not scan_target(target,'s'):
            ssid = asyncio.run(find_target(target,'s'))
            scan_results = scan_target(target,'s')
        else:
            scan_results = scan_target(target,'s')


    for i in scan_results:
        tssid = i[0]
        tbssid = i[1]
        tchan = i[2]
        trssi = i[3]
        tdiff = i[4]
        tmanuf = i[5]
        tsec = i[6]
        tclient = i[7]
        tlat = i[8]
        tlon = i[9]

        tprint = f"""{tssid} 
    Channel {tchan}
    {tbssid}
    {tmanuf}
    {tsec}
    {tclient} clients
    {tlat}, {tlon}
    {trssi} dbm
    Last seen {tdiff} seconds ago
    """
        
        with open(f'{OUTPUT_DIR}/foundtargets.txt', 'a') as file:
            file.writelines(tprint)

