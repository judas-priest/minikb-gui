#!/bin/bash
# Toggle HyperHDR service via systemd

# Ensure systemd can find user session
export XDG_RUNTIME_DIR="/run/user/$(id -u)"
export DBUS_SESSION_BUS_ADDRESS="unix:path=${XDG_RUNTIME_DIR}/bus"

# Check if running (use simpler pgrep check)
if pgrep -x hyperhdr > /dev/null 2>&1; then
    # HyperHDR is running → stop everything
    systemctl --user stop hyperhdr.service 2>/dev/null || true
    pkill -x hyperhdr 2>/dev/null || true
    sleep 0.2
    notify-send "HyperHDR" "Stopped" -i video-display
else
    # HyperHDR is not running → start via systemd
    systemctl --user start hyperhdr.service 2>/dev/null
    sleep 0.2
    notify-send "HyperHDR" "Started" -i video-display
fi
