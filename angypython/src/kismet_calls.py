from requests.auth import HTTPBasicAuth
import requests
import time

user = "kismet"
password = "kismet"

def kismet_scan(interface):
    url1 = "http://localhost:2501/phy/phy80211/ssids/views/ssids.json"

    response1 = requests.get(
        f'{url1}',
        auth=HTTPBasicAuth(user, password)
    )

    response1.raise_for_status()
    ssid_bssid_pairs = []
    if response1.status_code == 200:
        data = response1.json()
        
        ssid_bssid_pairs = []
        for item in data:
            last_time = item.get("dot11.ssidgroup.last_time")
            current_time = int(time.time())
            time_diff = current_time - last_time
            if time_diff >= 120:
                continue
            ssid = item.get("dot11.ssidgroup.ssid")
            devkeys = item.get("dot11.ssidgroup.advertising_devices")
            for devkey in devkeys:
                devkey = devkey.strip("[]'")
                response2 = requests.get(
                    f'http://localhost:2501/devices/by-key/{devkey}/device.json',
                    auth=HTTPBasicAuth(user, password)
                )
                response2.raise_for_status()
                data1 = response2.json()
                keydata = response2.json().get("dot11.device")
                bssid = keydata.get("dot11.device.last_bssid")
                channel = data1.get("kismet.device.base.channel")
                ssid_bssid_pairs.append((ssid, bssid, channel))
    voila = []
    for ssid, bssid, channel in ssid_bssid_pairs:
        if ssid != '' and ssid not in voila:
            voila.append(f'{ssid.strip()}')
    chunk_size = 10
    for i in range(0, len(voila), chunk_size):
        chunk = voila[i:i + chunk_size]
        readable_chunk = '\n'.join(chunk)
        interface.sendText(f"{readable_chunk}")

def kismet_scan_target(queried_ssid):
    url1 = "http://localhost:2501/phy/phy80211/ssids/views/ssids.json"

    response1 = requests.get(
        f'{url1}',
        auth=HTTPBasicAuth(user, password)
    )

    response1.raise_for_status()
    ssid_bssid_pairs = []
    if response1.status_code == 200:
        data = response1.json()
        
        ssid_bssid_pairs = []
        for item in data:
            last_time = item.get("dot11.ssidgroup.last_time")
            current_time = int(time.time())
            time_diff = current_time - last_time
            ssid = item.get("dot11.ssidgroup.ssid")
            if queried_ssid.lower() in ssid.lower():
                devkeys = item.get("dot11.ssidgroup.advertising_devices")
                for devkey in devkeys:
                    devkey = devkey.strip("[]'")
                    response2 = requests.get(
                        f'http://localhost:2501/devices/by-key/{devkey}/device.json',
                        auth=HTTPBasicAuth(user, password)
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
    return ssid_bssid_pairs
