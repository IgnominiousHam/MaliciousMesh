#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="$SCRIPT_DIR/../output"
MESHTASTIC_CMD=$SCRIPT_DIR/../angypython/.venv/bin/meshtastic


FILENAME="$OUTPUT_DIR/foundtargets.txt"
chunk_size=9

interval=60
last_print_time=$(date +%s)

while [[ ! -e $FILENAME ]]; do
   current_time=$(date +%s)
   if (( current_time - last_print_time >= interval )); then
      systemctl stop meshtastic_listener
      $MESHTASTIC_CMD --sendtext "Still hunting..." --port /dev/lora
      systemctl start meshtastic_listener
      last_print_time=$current_time
   fi
done


counter=0
current_chunk=""


systemctl stop meshtastic_listener

while IFS= read -r line; do
    if (( counter != chunk_size - 1 )); then
      current_chunk+="$line"$'\n'
    else
      current_chunk+="$line"
    fi

    ((counter++))

    if ((counter == chunk_size)); then
        $MESHTASTIC_CMD --sendtext "$current_chunk" --port /dev/lora
        current_chunk=""  
        counter=0         
    fi
done < "$FILENAME"

if ((counter > 0)); then
  $MESHTASTIC_CMD --sendtext "$current_chunk" --port /dev/lora
fi

systemctl start meshtastic_listener
