#!/bin/bash
# KDE Plasma notification LED blink script
# Monitors KDE notifications and blinks MiniKB RGB

# Check if ch57x-keyboard-tool is available
if ! command -v ch57x-keyboard-tool &> /dev/null; then
    echo "Error: ch57x-keyboard-tool not found in PATH"
    exit 1
fi

# LED blink function
blink_led() {
    ch57x-keyboard-tool led 2  # Turn on (rainbow mode)
    sleep 1
    ch57x-keyboard-tool led 0  # Turn off
}

echo "Monitoring KDE notifications..."
echo "LED will blink on each notification"

# Monitor D-Bus for KDE notifications
dbus-monitor "interface='org.freedesktop.Notifications',member='Notify'" |
while read -r line; do
    # When we see a Notify call, blink the LED
    if echo "$line" | grep -q "member=Notify"; then
        blink_led &
    fi
done
