#!/bin/bash
# Toggle HyperHDR service via systemd

# Ensure systemd can find user session
export XDG_RUNTIME_DIR="/run/user/$(id -u)"
export DBUS_SESSION_BUS_ADDRESS="unix:path=${XDG_RUNTIME_DIR}/bus"

# Toggle: if active → stop, if inactive → start
if systemctl --user is-active --quiet hyperhdr.service; then
    systemctl --user stop hyperhdr.service
    sleep 3
    notify-send "HyperHDR" "Stopped" -i video-display
else
    # Kill any manual instances before starting via systemd (exact match only)
    pkill -9 -x hyperhdr 2>/dev/null
    sleep 1
    systemctl --user start hyperhdr.service
    sleep 3
    notify-send "HyperHDR" "Started" -i video-display
fi
