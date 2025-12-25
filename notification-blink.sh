#!/bin/bash
# KDE Plasma notification LED blink script
# Monitors KDE notifications and blinks MiniKB RGB

# Add .cargo/bin to PATH (where ch57x-keyboard-tool is installed)
export PATH="$HOME/.cargo/bin:$PATH"

# Tool path
TOOL="$HOME/.cargo/bin/ch57x-keyboard-tool"

# Check if ch57x-keyboard-tool is available
if ! command -v ch57x-keyboard-tool &> /dev/null; then
    echo "Error: ch57x-keyboard-tool not found in PATH" >&2
    echo "PATH: $PATH" >&2
    exit 1
fi

# LED blink function
blink_led() {
    echo "[$(date '+%H:%M:%S')] Blinking LED..." >&2
    $TOOL led 2 2>&1 || echo "Failed to set LED 2" >&2
    sleep 1
    $TOOL led 0 2>&1 || echo "Failed to set LED 0" >&2
}

echo "Monitoring KDE notifications..."
echo "LED will blink on each notification"

# Monitor D-Bus for KDE notifications
# Using stdbuf to disable buffering for real-time monitoring
stdbuf -oL dbus-monitor "interface='org.freedesktop.Notifications',member='Notify'" 2>&1 |
while IFS= read -r line; do
    echo "[$(date '+%H:%M:%S')] DBus: $line" >&2

    # When we see a Notify method call, blink the LED
    if echo "$line" | grep -qE "(member=Notify|method call.*Notify)"; then
        echo "[$(date '+%H:%M:%S')] Notification detected!" >&2
        blink_led &
    fi
done
