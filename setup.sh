#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ANGRYHEAD_PATH="$SCRIPT_DIR/angybash/angryhead.sh"
PYTHON_VENV_PATH="$SCRIPT_DIR/angypython/.venv/bin/python"
MDKMONITOR_PATH="$SCRIPT_DIR/angybash/mdkmonitor.sh"
OUTPUT_DIR="$SCRIPT_DIR/output"
LOG_DIR="$SCRIPT_DIR/logs"
MESHTASTIC_LISTENER_PATH="$SCRIPT_DIR/angypython/meshtastic_listener.py"
TARGETREPORT_PATH="$SCRIPT_DIR/angybash/targetreport.sh"
INITIAL_STATUS_PATH="$SCRIPT_DIR/angypython/initial_status.py"
SCANS_DIR="$LOG_DIR/scans"


read -p "Non-root user: " USER
read -p "Static IP: " INPUT_IP

SERVICE_NAME="angry2.4@.service"
DEST_PATH="/etc/systemd/system/$SERVICE_NAME"
cat > "$DEST_PATH" <<EOF
[Unit]
Description=Angry Oxide Service for %i
After=network.target

[Service]
ExecStart=/bin/bash $ANGRYHEAD_PATH -i %i -c 1,3,6,9,11 -d 1
WorkingDirectory=$LOG_DIR
User=root

[Install]
WantedBy=multi-user.target
EOF

SERVICE_NAME="angry2all@.service"
DEST_PATH="/etc/systemd/system/$SERVICE_NAME"
cat > "$DEST_PATH" <<EOF
[Unit]
Description=Angry Oxide Service
After=network.target

[Service]
ExecStart=/bin/bash $ANGRYHEAD_PATH -i %i -c 1,2,3,4,5,6,7,8,9,10,11,12,13 -d 10 
WorkingDirectory=$LOG_DIR
User=root

[Install]
WantedBy=multi-user.target
EOF

SERVICE_NAME="angry5@.service"
DEST_PATH="/etc/systemd/system/$SERVICE_NAME"
cat > "$DEST_PATH" <<EOF
[Unit]
Description=Angry Oxide Service
After=network.target

[Service]
ExecStart=/bin/bash $ANGRYHEAD_PATH -i %i -c 36,44,149,157 
WorkingDirectory=$LOG_DIR
User=root

[Install]
WantedBy=multi-user.target
EOF

SERVICE_NAME="angry5all@.service"
DEST_PATH="/etc/systemd/system/$SERVICE_NAME"
cat > "$DEST_PATH" <<EOF
[Unit]
Description=Angry Oxide Service
After=network.target

[Service]
ExecStart=/bin/bash $ANGRYHEAD_PATH -i %i -c 52,56,60,64,149,153,157,161,165 -d 10  
WorkingDirectory=$LOG_DIR
User=root

[Install]
WantedBy=multi-user.target
EOF

SERVICE_NAME="angrypassive@.service"
DEST_PATH="/etc/systemd/system/$SERVICE_NAME"
cat > "$DEST_PATH" <<EOF
[Unit]
Description=Angry Oxide Service
After=network.target

[Service]
ExecStart=/bin/bash $ANGRYHEAD_PATH -i %i -c 1,2,3,4,5,6,7,8,9,10,11,36,40,44,48,52,56,60,64,100,104,108,112,116,120,124,128,132,136,140,149,153,157,161,165 -p
WorkingDirectory=$LOG_DIR
User=root

[Install]
WantedBy=multi-user.target
EOF

SERVICE_NAME="mdkmonitor.service"
DEST_PATH="/etc/systemd/system/$SERVICE_NAME"
cat > "$DEST_PATH" <<EOF
[Unit]
Description=mdkmonitor
After=network.target

[Service]
ExecStart=/bin/bash $MDKMONITOR_PATH
User=root

[Install]
WantedBy=multi-user.target
EOF

SERVICE_NAME="delete-output.service"
DEST_PATH="/etc/systemd/system/$SERVICE_NAME"
cat > "$DEST_PATH" <<EOF
[Unit]
Description=Delete a file on boot
After=network.target

[Service]
Type=oneshot
ExecStart=/bin/sh -c "/bin/rm -f $OUTPUT_DIR/*"
RemainAfterExit=true
User=root

[Install]
WantedBy=multi-user.target
EOF

SERVICE_NAME="meshtastic_listener.service"
DEST_PATH="/etc/systemd/system/$SERVICE_NAME"
cat > "$DEST_PATH" <<EOF
[Unit]
Description=Meshtastic Listener Service
After=initial-status.service

[Service]
Type=simple
User=root
ExecStart=$PYTHON_VENV_PATH $MESHTASTIC_LISTENER_PATH
Restart=always

[Install]
WantedBy=multi-user.target
EOF

SERVICE_NAME="set-static-ip.service"
DEST_PATH="/etc/systemd/system/$SERVICE_NAME"
cat > "$DEST_PATH" <<EOF
[Unit]
Description=Set static IP for eth0
After=network.target

[Service]
Type=oneshot
ExecStart=ifconfig eth0 $INPUT_IP
RemainAfterExit=true
User=root

[Install]
WantedBy=multi-user.target
EOF


SERVICE_NAME="angrykismet@.service"
DEST_PATH="/etc/systemd/system/$SERVICE_NAME"
cat > "$DEST_PATH" <<EOF
[Unit]
Description=Kismet
After=network.target

[Service]
ExecStart=kismet -c %i -p $SCANS_DIR
RemainAfterExit=yes
User=$USER

[Install]
WantedBy=multi-user.target
EOF

SERVICE_NAME="targetreport.service"
DEST_PATH="/etc/systemd/system/$SERVICE_NAME"
cat > "$DEST_PATH" <<EOF
[Unit]
Description=targetreport
After=network.target

[Service]
ExecStart=/bin/bash $TARGETREPORT_PATH
User=root

[Install]
WantedBy=multi-user.target
EOF

SERVICE_NAME="initial-status.service"
DEST_PATH="/etc/systemd/system/$SERVICE_NAME"
cat > "$DEST_PATH" <<EOF
[Unit]
Description=status
After=network.target

[Service]
Type=oneshot
ExecStart=$PYTHON_VENV_PATH $INITIAL_STATUS_PATH
RemainAfterExit=true
User=root

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable meshtastic_listener
systemctl enable set-static-ip
systemctl enable delete-output
systemctl enable initial-status

wget -O - https://www.kismetwireless.net/repos/kismet-release.gpg.key --quiet | gpg --dearmor | sudo tee /usr/share/keyrings/kismet-archive-keyring.gpg >/dev/null
echo 'deb [signed-by=/usr/share/keyrings/kismet-archive-keyring.gpg] https://www.kismetwireless.net/repos/apt/release/bookworm bookworm main' | sudo tee /etc/apt/sources.list.d/kismet.list >/dev/null
sudo apt update
sudo apt install kismet mdk4 gpsd gpsd-clients virtualenv -y
sudo usermod -aG kismet $USER

mkdir -p ~/angryoxide
cd ~/angryoxide
wget https://github.com/Ragnt/AngryOxide/releases/download/v0.8.32/angryoxide-linux-aarch64-gnu.tar.gz
tar -xf angryoxide-linux-aarch64-gnu.tar.gz
chmod +x install.sh
./install.sh

cat > "/etc/default/gpsd" <<EOF
# Devices gpsd should collect to at boot time.
# They need to be read/writeable, either by user gpsd or the group dialout.
DEVICES="/dev/gps"

# Other options you want to pass to gpsd
GPSD_OPTIONS="-n -b"

# Automatically hot add/remove USB GPS devices via gpsdctl
USBAUTO="false"
EOF

cat > "/etc/udev/rules.d/99-lora+gps.rules" <<EOF
SUBSYSTEM=="tty", ATTRS{serial}=="FABQe108Y20", SYMLINK+="gps"
SUBSYSTEM=="tty", ATTRS{serial}=="0001", SYMLINK+="lora"
EOF

cat > "/etc/NetworkManager/conf.d/unmanaged-stuff.conf" <<EOF
[keyfile]
unmanaged-devices=except:interface-name:wlan0
EOF

mkdir -p /home/$USER/.kismet/
cat > "/home/$USER/.kismet/kismet_httpd.conf" <<EOF
httpd_password=kismet
httpd_username=kismet
EOF

virtualenv $SCRIPT_DIR/angypython/.venv
source $SCRIPT_DIR/angypython/.venv/bin/activate
pip install -r $SCRIPT_DIR/angypython/requirements.txt
deactivate

echo "All done, rebooting..."
sleep 3
reboot

