#!/bin/bash
# Toggle internal display (laptop screen) in KDE Plasma 6
# Simulates Super+P display switching

# Get list of outputs
OUTPUTS=$(kscreen-doctor -o 2>/dev/null)

# Find internal display (usually eDP-1, LVDS-1, or eDP)
INTERNAL=$(echo "$OUTPUTS" | grep -E "eDP|LVDS" | head -n1 | cut -d' ' -f3)

if [ -z "$INTERNAL" ]; then
    notify-send "Display Toggle" "Internal display not found" -u critical
    exit 1
fi

# Check current state
if echo "$OUTPUTS" | grep "$INTERNAL" | grep -q "enabled"; then
    # Currently enabled, disable it
    kscreen-doctor output.$INTERNAL.disable
    notify-send "Display" "Internal screen disabled" -i video-display
else
    # Currently disabled, enable it
    kscreen-doctor output.$INTERNAL.enable
    notify-send "Display" "Internal screen enabled" -i video-display
fi
