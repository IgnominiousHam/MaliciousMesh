import re
import gpsd
import subprocess

def send_message_in_chunks(content, interface):
    """Send the log content to Meshtastic in chunks if it exceeds the limit."""
    MESHTASTIC_MESSAGE_LIMIT = 150  
    for i in range(0, len(content), MESHTASTIC_MESSAGE_LIMIT):
        chunk = content[i:i+MESHTASTIC_MESSAGE_LIMIT]
        meshtastic_message = f"{chunk}"
        interface.sendText(meshtastic_message)
        print(f"Sent message to Meshtastic: {meshtastic_message}")


def is_mac_address(s):
    """
    Check if the string is a valid MAC address.
    A MAC address has the format: XX:XX:XX:XX:XX:XX where X is a hexadecimal digit.
    """
    mac_regex = r'^([0-9a-fA-F]{2}[-:.]){5}[0-9a-fA-F]{2}$'
    
    return bool(re.match(mac_regex, s))

def extract_ssids(file_path, interface):
    with open(file_path, 'r') as file:
       entries = file.readlines()

    ssids = []
    for line in entries:
        ssid_line = line.strip() 
        if ssid_line.startswith('SSID:'):
            ssid = ssid_line.split("SSID:")[1].strip()
            if '--' not in ssid:
                ssids.append(ssid)

    chunk_size = 10
    for i in range(0, len(ssids), chunk_size):
        chunk = ssids[i:i + chunk_size]
        readablechunk = "\n".join(chunk)
        interface.sendText(f"{readablechunk}")

def get_gps_data():
    try:
        # Get GPS position
        gpsd.connect()
        packet = gpsd.get_current()

        if packet.mode >= 2: 
            location = (packet.lat, packet.lon)
            print(f"GPS Fix acquired:")
            print(f"Latitude: {packet.lat}, Longitude: {packet.lon}")
            return location
        else:
            print("Waiting for GPS fix...")
            return "No GPS fix"
        
    except Exception as e:
        print(f"Error: {e}")
        return f"Error: {e}"

def run_nmcli(nmcli_file_path):
    with open(nmcli_file_path, 'w') as f:
        subprocess.run(['nmcli', '-f', 'SSID,BSSID', '-m', 'multiline', '-c', 'no', 'dev', 'wifi', 'list', '--rescan', 'yes'], stdout=f)
