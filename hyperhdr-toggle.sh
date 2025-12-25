#!/bin/bash
# Toggle HyperHDR service via systemd

if systemctl --user is-active --quiet hyperhdr.service || pgrep -x hyperhdr > /dev/null; then
    # HyperHDR is running (either systemd or manual) → stop everything
    systemctl --user stop hyperhdr.service 2>/dev/null
    pkill -x hyperhdr 2>/dev/null
    notify-send "HyperHDR" "Stopped" -i video-display
else
    # HyperHDR is not running → start via systemd
    systemctl --user start hyperhdr.service
    notify-send "HyperHDR" "Started" -i video-display
fi
