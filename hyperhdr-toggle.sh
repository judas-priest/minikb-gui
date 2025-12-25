#!/bin/bash
# Toggle HyperHDR process

if pgrep -x hyperhdr > /dev/null; then
    # HyperHDR is running → kill it
    pkill -x hyperhdr
    notify-send "HyperHDR" "Stopped" -i video-display
else
    # HyperHDR is not running → start it
    hyperhdr &
    notify-send "HyperHDR" "Started" -i video-display
fi
