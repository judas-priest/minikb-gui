#!/bin/bash
# Toggle HyperHDR service via systemd

LOG="/tmp/hyperhdr-toggle.log"
echo "=== $(date) ===" >> "$LOG"

# Ensure systemd can find user session
export XDG_RUNTIME_DIR="/run/user/$(id -u)"
export DBUS_SESSION_BUS_ADDRESS="unix:path=${XDG_RUNTIME_DIR}/bus"

# Debug: check what pgrep sees
echo "PATH: $PATH" >> "$LOG"
PGREP_OUT=$(/usr/bin/pgrep -x hyperhdr 2>&1)
PGREP_RET=$?
echo "pgrep -x result: $PGREP_RET, output: '$PGREP_OUT'" >> "$LOG"

# Try without -x flag
PGREP_OUT2=$(/usr/bin/pgrep hyperhdr 2>&1)
PGREP_RET2=$?
echo "pgrep (no -x) result: $PGREP_RET2, output: '$PGREP_OUT2'" >> "$LOG"
echo "USER: $USER, UID: $(id -u)" >> "$LOG"

# Check if running (use pgrep without -x flag)
if [ $PGREP_RET2 -eq 0 ]; then
    # HyperHDR is running → stop everything
    echo "Stopping hyperhdr" >> "$LOG"
    systemctl --user stop hyperhdr.service 2>/dev/null || true
    pkill -x hyperhdr 2>/dev/null || true
    sleep 0.2
    notify-send "HyperHDR" "Stopped" -i video-display
else
    # HyperHDR is not running → start via systemd
    echo "Starting hyperhdr" >> "$LOG"
    systemctl --user start hyperhdr.service 2>&1 >> "$LOG"
    sleep 0.2
    notify-send "HyperHDR" "Started" -i video-display
fi
