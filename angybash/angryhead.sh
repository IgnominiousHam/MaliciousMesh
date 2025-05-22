#!/bin/bash

INTERFACE="wlan1"
CHANNELS="1,3,6,9,11"
PASSIVE_MODE=""
DWELL_TIME="2"
AUTOHUNT=""
TARGET=""
LOCKED_LOGGING=""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/../logs"
OUTPUT_DIR="$SCRIPT_DIR/../output"
MESHTASTIC_CMD=$SCRIPT_DIR/../angypython/.venv/bin/meshtastic

DATE=$(date +'%Y-%m-%d')


while getopts "i:c:pd:at:l" opt; do
  case ${opt} in
    i ) INTERFACE="$OPTARG" ;;
    c ) CHANNELS="$OPTARG" ;;
    p ) PASSIVE_MODE="--noactive --notransmit" ;;
    d ) DWELL_TIME="$OPTARG" ;;
    a ) AUTOHUNT="--autohunt" ;;
    t ) TARGET="$OPTARG" ;;
    l ) LOCKED_LOGGING="y" ;;
    * ) echo "Usage: $0 -i <interface> -c <channels> [-p]"; exit 1 ;;
  esac
done 

sleep 5

SSID_HISTORY="$LOG_DIR/ssid_history.txt"
WAYPOINT_FILE="$LOG_DIR/waypoint_number.txt"
mkdir -p "$LOG_DIR/handshakes"
touch "$SSID_HISTORY"
touch "$WAYPOINT_FILE"
touch "$OUTPUT_DIR/priorityoutput.txt"
touch "$OUTPUT_DIR/headlessoutput_${INTERFACE}.txt"

while true; do
  if ip link show "$INTERFACE" | grep -q "state"; then
     systemctl stop meshtastic_listener
     $MESHTASTIC_CMD --sendtext "$INTERFACE is feeling a bit angry..." --port /dev/lora
     systemctl start meshtastic_listener
     break
  fi
done

if [[ ! -f "$WAYPOINT_FILE" ]]; then
   echo "1" > "$WAYPOINT_FILE"
fi

mkdir -p $LOG_DIR/"$DATE"
cd $LOG_DIR/"$DATE"

cmd=("sudo" "angryoxide" "-i" "$INTERFACE" "-c" "$CHANNELS" "--dwell" "$DWELL_TIME" $PASSIVE_MODE $AUTOHUNT  --headless --notar)
if [ -n "$TARGET" ]; then
    cmd+=("-t" "$TARGET")  
fi
if [ -z "$LOCKED_LOGGING" ]; then
  while true; do
    "${cmd[@]}" | \
    tee -a "${OUTPUT_DIR}/headlessoutput_${INTERFACE}.txt" | \
    stdbuf -oL sed -e 's/\x1b\[[0-9;]*m//g' | \
    stdbuf -oL awk -v iface="$INTERFACE" '
      /22000/ {
        gsub(/.*\(/, "", $0);
        gsub(/\)/, "", $0);
        ssid = $0;  
        print strftime("[%Y-%m-%d %H:%M:%S]"), iface, ssid;
        fflush();
      }
    ' | tee -a $OUTPUT_DIR/priorityoutput.txt | \
    while read -r line; do
      mv $LOG_DIR/"$DATE"/*.hc22000 $LOG_DIR/handshakes/
      if [[ "$line" =~ \| ]]; then 
        continue
      fi

      ssid=$(echo "$line" | sed 's/^\[[^]]*\] [^ ]* //')  
      cleaned_ssid=$(echo "$ssid" | sed 's/^[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\} //')

      if ! grep -qx "$cleaned_ssid" "$SSID_HISTORY"; then
        systemctl stop meshtastic_listener
        $MESHTASTIC_CMD --sendtext "$cleaned_ssid" --port /dev/lora
        echo "$cleaned_ssid" >> "$SSID_HISTORY"
        gps_data=$(timeout 3 gpspipe -w -n 10 | grep -m 1 '"lat"')
        latitude=$(echo "$gps_data" | grep -oP '"lat":\s*\K[-+]?[0-9]*\.?[0-9]+')
        longitude=$(echo "$gps_data" | grep -oP '"lon":\s*\K[-+]?[0-9]*\.?[0-9]+')
      
        if [[ -n "$latitude" && -n "$longitude" ]]; then
          waypoint_date=$(date -d "+1 year" +'%Y-%m-%dT%H:%M:%S')
          waypoint_number=$(cat "$WAYPOINT_FILE")

          $SCRIPT_DIR/../angypython/.venv/bin/python3 $SCRIPT_DIR/../angypython/waypoint.py --port /dev/lora create "$waypoint_number" "$cleaned_ssid" "$cleaned_ssid" "$waypoint_date" "$latitude" "$longitude" 
          waypoint_number=$((waypoint_number + 1))
          echo "$waypoint_number" > "$WAYPOINT_FILE"

        else
          echo "Failed to get GPS coordinates. Skipping waypoint creation."
        fi
        systemctl start meshtastic_listener
      fi  
    done
    
    sleep 1
  done
else
  while true; do
  "${cmd[@]}" | \
  tee -a "$OUTPUT_DIR/headlessoutput_${INTERFACE}.txt" | \
  stdbuf -oL sed -n 's/.*hc22000 Written: \([0-9a-f]\{12\}\) => \([0-9a-f]\{12\}\).*/\1 \2/p' | \
  tee -a $OUTPUT_DIR/prioritytarget.txt | \
  while read -r line; do
    cleanedmac=$(echo $line | sed 's/\([0-9a-f]\{2\}\)\([0-9a-f]\{2\}\)\([0-9a-f]\{2\}\)\([0-9a-f]\{2\}\)\([0-9a-f]\{2\}\)\([0-9a-f]\{2\}\)/\1:\2:\3:\4:\5:\6/' | sed 's/\([0-9a-f]\{2\}\)\([0-9a-f]\{2\}\)\([0-9a-f]\{2\}\)\([0-9a-f]\{2\}\)\([0-9a-f]\{2\}\)\([0-9a-f]\{2\}\)/\1:\2:\3:\4:\5:\6/' | tr 'a-f' 'A-F')
    systemctl stop meshtastic_listener
    $MESHTASTIC_CMD --sendtext "$cleanedmac" --port /dev/lora
    systemctl start meshtastic_listener
  done

  done
fi
