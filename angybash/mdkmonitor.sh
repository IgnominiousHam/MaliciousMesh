#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MESHTASTIC_CMD="$SCRIPT_DIR/../angypython/.venv/bin/meshtastic"
OUTPUT_DIR="$SCRIPT_DIR/../output"

file="$OUTPUT_DIR/prioritymdk4.txt"

while true; do
  sleep 60
  line_count=$(wc -l < "$file")
  systemctl stop meshtastic_listener
  $MESHTASTIC_CMD --sendtext "$line_count clients being deauthed." --port "/dev/lora"
  systemctl start meshtastic_listener
  > "$file"
done
