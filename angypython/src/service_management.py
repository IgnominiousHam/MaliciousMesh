import subprocess
import os 
import sys

def stop_service(matching_services):
    for service in matching_services:
        service_name = service.split()[0]  
        subprocess.run(["sudo", "systemctl", "stop", service_name], check=True)
        print(f"Stopped systemd service: {service_name}")

def start_interface_service(interface, serv):
    try:
        subprocess.run(["sudo", "systemctl", "start", f"{serv}@{interface}"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error starting services: {e}")

def stop_interface_service(interface):
    """Stop the systemd service controlling the interface."""
    try:
        services = subprocess.check_output(["systemctl", "list-units", "--type=service", "--all"], text=True)
        matching_services = [line for line in services.splitlines() if f"angry" in line and f"@{interface}" in line]
        stop_service(matching_services)
    except subprocess.CalledProcessError as e:
        print(f"Error stopping services: {e}")

def stop_kismet_service():
    """Stop the systemd service controlling the interface."""
    try:
        services = subprocess.check_output(["systemctl", "list-units", "--type=service", "--all"], text=True)
        matching_services = [line for line in services.splitlines() if f"angrykismet" in line]
        stop_service(matching_services)
    except subprocess.CalledProcessError as e:
        print(f"Error stopping services: {e}")

def stop_all_service():
    """Stop the systemd service controlling the interface."""
    try:
        services = subprocess.check_output(["systemctl", "list-units", "--type=service", "--all"], text=True)
        matching_services = [line for line in services.splitlines() if f"angry" in line]
        stop_service(matching_services)
    except subprocess.CalledProcessError as e:
        print(f"Error stopping services: {e}")

def create_t_service(interface, ssid, channel=None):
    python_file_path = os.path.abspath(__file__)
    src_dir = os.path.dirname(python_file_path)
    angypython_dir = os.path.dirname(src_dir)
    angypack_dir = os.path.dirname(angypython_dir)
    SERVICE_DIR = "/etc/systemd/system"
    WORKING_DIR = f"{angypack_dir}/logs"
    service_name = f"angrytarget@{interface}.service"
    service_file = os.path.join(SERVICE_DIR, service_name)

    if channel:
        exec_start = f"/bin/bash {angypack_dir}/angybash/angryhead.sh -i {interface} -t \"{ssid}\" -c \"{channel}\" -l"
    else:
        exec_start = f"/bin/bash {angypack_dir}/angybash/angryhead.sh -i {interface} -a -t \"{ssid}\" -l"

    service_content = f"""[Unit]
Description=Angry Oxide Service for {interface}
After=meshtasticd.service

[Service]
ExecStart={exec_start}
WorkingDirectory={WORKING_DIR}
User=root
Group=root

[Install]
WantedBy=multi-user.target
"""

    with open(service_file, 'w') as f:
        f.write(service_content)

    subprocess.run(["systemctl", "start", service_name], check=True)
    print(f"Service {service_name} created and started successfully.")

def remove_t_service(interface):
    SERVICE_DIR = "/etc/systemd/system"
    service_name = f"angrytarget@{interface}.service"
    service_file = os.path.join(SERVICE_DIR, service_name)

    if not os.path.exists(service_file):
        print(f"Error: Service {service_name} does not exist.")
    else:
        subprocess.run(["systemctl", "stop", service_name], check=True)
        os.remove(service_file)
        print(f"Service {service_name} stopped and removed successfully.")

def create_td_service(interface, target, flag):
    python_file_path = os.path.abspath(__file__)
    src_dir = os.path.dirname(python_file_path)
    angypython_dir = os.path.dirname(src_dir)
    angypack_dir = os.path.dirname(angypython_dir)
    SERVICE_DIR = "/etc/systemd/system"

    service_name = f"angrymdk4@{interface}.service"
    service_file = os.path.join(SERVICE_DIR, service_name)

    if flag == "e":
        exec_start = f"/bin/bash {angypack_dir}/angybash/mdk4wrapper.sh -i {interface} -t \"{target}\" -e E"
    elif flag == "b":
        exec_start = f"/bin/bash {angypack_dir}/angybash/mdk4wrapper.sh -i {interface} -t \"{target}\" -e B"

    service_content = f"""[Unit]
Description=MDK4 Deauthentication Attack for {interface} on SSID {target}
After=network.target

[Service]
ExecStart={exec_start}
User=root
Group=root

[Install]
WantedBy=multi-user.target
"""

    with open(service_file, "w") as f:
        f.write(service_content)

    subprocess.run(["systemctl", "start", service_name], check=True)

    result = subprocess.run(["systemctl", "list-units", "--full", "--quiet", "--type=service", "mdkmonitor.service"])
    if result.returncode == 0:
        subprocess.run(["systemctl", "start", "mdkmonitor"], check=True)
    else:
        print("Warning: mdkmonitor service not found.")

def remove_td_service(interface):
    SERVICE_DIR = "/etc/systemd/system"
    service_name = f"angrymdk4@{interface}.service"
    service_file = os.path.join(SERVICE_DIR, service_name)

    if not os.path.exists(service_file):
        print(f"Error: Service {service_name} does not exist.")
 
    else:
        subprocess.run(["systemctl", "stop", service_name], check=True)
        subprocess.run(["systemctl", "stop", "mdkmonitor"], check=True)

        os.remove(service_file)


def create_tfind_service(parts):
    python_file_path = os.path.abspath(__file__)
    src_dir = os.path.dirname(python_file_path)
    angypython_dir = os.path.dirname(src_dir)
    angypack_dir = os.path.dirname(angypython_dir)
    SERVICE_DIR = "/etc/systemd/system"
    SERVICE_FILE_PATH = f'{SERVICE_DIR}/angrytargethunt.service'
    service_content = f"""[Unit]
Description=targethunt
After=network.target

[Service]
Type=oneshot
ExecStart={angypython_dir}/.venv/bin/python {angypython_dir}/targethunt.py "{parts}"
User=root

[Install]
WantedBy=multi-user.target
"""

    with open(SERVICE_FILE_PATH, 'w') as f:
        f.write(service_content)

    print(f"Looking for {parts}...")

    subprocess.run(["systemctl", "daemon-reload"], check=True)
    subprocess.run(["systemctl", "start", "angrytargethunt"], check=True)

def remove_tfind_service():
    SERVICE_FILE_PATH = f'/etc/systemd/system/angrytargethunt.service'
    subprocess.run(["systemctl", "stop", "angrytargethunt"], check=True)
    subprocess.run(["systemctl", "stop", "targetreport"], check=True)
    os.remove(SERVICE_FILE_PATH)

def create_tc_service(interface, channel):
    python_file_path = os.path.abspath(__file__)
    src_dir = os.path.dirname(python_file_path)
    angypython_dir = os.path.dirname(src_dir)
    angypack_dir = os.path.dirname(angypython_dir)
    SERVICE_DIR = "/etc/systemd/system"
    WORKING_DIR = f"{angypack_dir}/logs"
    SERVICE_TEMPLATE_PATH = f"{SERVICE_DIR}/angrychannel@.service"
    SERVICE_NAME_TEMPLATE = "angrychannel@{interface}"
    service_unit = f"""[Unit]
Description=angrychannel
After=network.target

[Service]
ExecStart={angypack_dir}/angybash/angryhead.sh -i %i -c {channel} -p
WorkingDirectory="{WORKING_DIR}"
User=root

[Install]
WantedBy=multi-user.target
"""

    with open(SERVICE_TEMPLATE_PATH, 'w') as f:
        f.write(service_unit)

    service_name = SERVICE_NAME_TEMPLATE.format(interface=interface)

    print(f"Camping {interface} on channel {channel}...")

    subprocess.run(["systemctl", "daemon-reload"], check=True)
    subprocess.run(["systemctl", "start", service_name], check=True)

    print(f"Service {service_name} created and started successfully.")
    
