#!/bin/bash
# Toggle HyperHDR process

LOCKFILE="/tmp/hyperhdr-toggle.lock"

# Prevent concurrent execution
if [ -e "$LOCKFILE" ]; then
    exit 0
fi

touch "$LOCKFILE"
trap "rm -f $LOCKFILE" EXIT

if pgrep -x hyperhdr > /dev/null; then
    # HyperHDR is running → kill it
    pkill -x hyperhdr
    sleep 0.5  # Wait for process to die
    notify-send "HyperHDR" "Stopped" -i video-display
else
    # HyperHDR is not running → start it
    hyperhdr > /dev/null 2>&1 &
    sleep 0.5  # Wait for process to start
    notify-send "HyperHDR" "Started" -i video-display
fi
