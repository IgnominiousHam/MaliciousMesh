# 🦆 MaliciousMesh

**MaliciousMesh** is a modular wireless penetration testing and surveying toolkit that integrates [Meshtastic](https://meshtastic.org/) and [AngryOxide](https://github.com/angyroot/angryoxide) to perform advanced Wi-Fi reconnaissance, mesh-based alerting, and passive/active target detection. It also includes wireless survey capabilities using [Kismet](https://kismetwireless.net/).

> ⚠️ This project is intended **solely for authorized penetration testing and wireless network auditing**. Do not use this software on networks you do not own or have explicit permission to test.

---

## 🔧 Features

- 📡 **Wi-Fi Scanning & Auditing** via `angryoxide`
- 🎯 **Autonomous Target Detection** with GPS waypoint tagging
- 🔗 **Real-time Mesh Alerts** via `meshtastic` (LoRa)
- 🗺 **Site Surveying & Mapping** with `kismet`
- ⚙️ **Systemd Integration** for persistent, modular services
- 🔒 Headless mode for embedded/off-grid operation

---

## 🚀 Getting Started

### 🔩 Prerequisites

- Raspberry Pi 4 with Raspberry Pi OS Lite (may work with another distro, haven't tested)
- LoRa radios flashed with Meshtastic firmware and on the same private channel
- External NIC for the Pi
- Internet connection on the Pi (just for setup)

### 🔨 Installation

```bash
git clone https://github.com/IgnominiousHam/MaliciousMesh.git
cd MaliciousMesh

# Set up environment
sudo bash ./setup.sh     

# (Optional) Enable systemd services
sudo systemctl enable angry2.4@wlan1
```

---

## 🛰 Meshtastic Usage

### 🔁 Non-Targeted Services

`status` - summarizes available interfaces, GPS status, and active services

`s wlan1 2` - angryoxide, 2.4 GHZ, low dwell time

`s wlan1 2*` - angryoxide, 2.4 GHZ, high dwell time

`s wlan1 5` - angryoxide, 5 GHZ, low dwell time

`s wlan1 5*` - angryoxide, 5 GHZ, high dwell time

`s wlan1 kismet` - kismet, 2.4-5 GHZ survey

`s wlan1 stop` - stop services

### 🌐 Targeted services

`t wlan1 ssid` - angryoxide, autohunt for given ssid

`t wlan1 #chan ssid` - angryoxide, lock to channel and target ssid

`td wlan1 ssid` - angryoxide + mdk4, autohunt and deauth

`td wlan1 #chan ssid` - angryoxide + mdk4, lock to channel and deauth

`t wlan1 stop` - stop target service and remove created service file

`td wlan1 stopd` - stop deauth service but maintain targeting

`td wlan1 stop` - stop both deauth and target services

`ssid` - retrive hash for given ssid

### 🗺 Scans

`scan` - must have kismet active, queries kismet for nearby ssids

`nmscan` - uses nmcli to scan for nearby ssids

`tscan ssid` - must have kismet active, gives report on given ssid

`tfind ssid` - must have kismet active, searches for ssid then gives report once it's found

---

## 🧪 Logs & Output

 - Survey logs are located in the logs/scans directory
 - Angryoxide pcaps are placed in their respective logs/#date folders
 - Handshakes are sent to logs/handshakes

---

⚠️ Legal Notice

This tool is intended for ethical hacking, educational use, and authorized penetration testing only.

By using MaliciousMesh, you agree to the following:

    You have permission to test any network you scan.

    You take full responsibility for how this tool is used.

    The authors are not liable for misuse.

🧠 Credits

    Meshtastic

    AngryOxide

    Kismet




---

Would you like a shorter version, a PDF-exportable one, or badges like "Made with Python", "License", etc., at the top?

