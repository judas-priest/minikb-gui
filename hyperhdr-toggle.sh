#!/bin/bash
# Toggle HyperHDR (direct process control, no systemd)

# Check if hyperhdr is running
if pgrep hyperhdr > /dev/null 2>&1; then
    # Running → kill it
    pkill -9 hyperhdr
    rm -f /tmp/hyperhdr-domain 2>/dev/null
    sleep 1
    notify-send "HyperHDR" "Stopped" -i video-display
else
    # Not running → start it
    rm -f /tmp/hyperhdr-domain 2>/dev/null
    hyperhdr > /dev/null 2>&1 &
    sleep 2
    notify-send "HyperHDR" "Started" -i video-display
fi
