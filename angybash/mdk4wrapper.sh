#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="$SCRIPT_DIR/../output"


INTERFACE="panel"
TARGET=""

while getopts "i:t:e:" opt; do
  case ${opt} in
    i ) INTERFACE="$OPTARG" ;;
    t ) TARGET="$OPTARG" ;;
    e ) EFLAG="-$OPTARG" ;;
  esac
done


touch "$OUTPUT_DIR/mdk4output_$INTERFACE.txt"
touch "$OUTPUT_DIR/prioritymdk4.txt"


cmd=("mdk4" "$INTERFACE" "d" "-x")
if [ -n "$TARGET" ]; then
  cmd+=("$EFLAG" "$TARGET")
fi

"${cmd[@]}" | tee -a "$OUTPUT_DIR/mdk4output_$INTERFACE.txt" | \

while read -r line; do
  if [ -n "$line" ]; then
    mac=$(echo "$line" | stdbuf -oL sed -e 's/\x1b\[[0-9;]*m//g' | awk '/Disconnecting/ {print $2}')
    if ! grep -qx "$mac" "$OUTPUT_DIR/prioritymdk4.txt"; then
      echo "$mac" >> "$OUTPUT_DIR/prioritymdk4.txt"
    fi
  fi
done
