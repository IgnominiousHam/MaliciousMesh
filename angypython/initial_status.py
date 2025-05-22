#!./.venv/bin/python
import subprocess
import meshtastic
import meshtastic.serial_interface


INTERFACES = subprocess.run("iwconfig 2>/dev/null | grep '^[a-zA-Z0-9]' | awk '{print $1}' | grep -v '.*mon$' | grep -v '^wlan0$'", shell=True, text=True, capture_output=True).stdout.strip()
SERVICES = subprocess.run("systemctl list-units --type=service --state=active --no-pager --no-legend | awk '{print $1}' | grep '^angry'", shell=True, text=True, capture_output=True).stdout.strip() 
printint = f"""INTERFACES:
{INTERFACES}

SERVICES:
{SERVICES}"""

#subprocess.run(["systemctl", "stop", "meshtastic_listener"], check=True)
interface = meshtastic.serial_interface.SerialInterface('/dev/lora')
interface.sendText(printint)
#subprocess.run(["systemctl", "start", "meshtastic_listener"], check=True)
