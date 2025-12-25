#!/bin/bash
# Toggle internal display (laptop screen) in KDE Plasma 6
# eDP-1 on left, HDMI-A-1 extended to the right

INTERNAL="eDP-1"
EXTERNAL="HDMI-A-1"

# Check current state of internal display
OUTPUTS=$(kscreen-doctor -o 2>&1)

if echo "$OUTPUTS" | grep "$INTERNAL" | grep -q "enabled"; then
    # Internal is ON → turn it OFF
    # Move external to primary position (0,0)
    kscreen-doctor output.$INTERNAL.disable output.$EXTERNAL.position.0,0 2>&1
    notify-send "Display" "Internal screen disabled" -i video-display
else
    # Internal is OFF → turn it ON
    # Get internal display resolution to position external to the right
    # Strip ANSI color codes and extract width from "Geometry: X,Y WIDTHxHEIGHT"
    INTERNAL_WIDTH=$(kscreen-doctor -o 2>&1 | sed 's/\x1b\[[0-9;]*m//g' | grep -A 20 "$INTERNAL" | grep "Geometry:" | head -n1 | sed 's/.*Geometry: [0-9]*,[0-9]* \([0-9]*\)x.*/\1/')

    # Default to 1920 if detection fails
    if [ -z "$INTERNAL_WIDTH" ]; then
        INTERNAL_WIDTH=1920
    fi

    # Enable internal at 0,0, position external to the right
    kscreen-doctor output.$INTERNAL.enable output.$INTERNAL.position.0,0 output.$EXTERNAL.position.$INTERNAL_WIDTH,0 2>&1
    notify-send "Display" "Internal screen enabled (extended right)" -i video-display
fi
