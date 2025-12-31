#!/bin/bash
# Toggle internal display (laptop screen) in KDE Plasma 6
# Supports optional third monitor in the middle
# Layout: eDP-1 (left) → THIRD (middle, if present) → HDMI-A-1 (right)

INTERNAL="eDP-1"
EXTERNAL="HDMI-A-1"

# Get all connected outputs (strip ANSI color codes)
OUTPUTS=$(kscreen-doctor -o 2>&1 | sed 's/\x1b\[[0-9;]*m//g')

# Find third monitor (connected, not internal and not external)
THIRD=""
for output in $(echo "$OUTPUTS" | grep "^Output:" | awk '{print $3}'); do
    if [ "$output" != "$INTERNAL" ] && [ "$output" != "$EXTERNAL" ]; then
        # Check if connected
        if echo "$OUTPUTS" | grep -A 2 "Output:.*$output" | grep -q "connected"; then
            THIRD="$output"
            break
        fi
    fi
done

# Check if internal is currently enabled
INTERNAL_ENABLED=$(echo "$OUTPUTS" | grep -A 1 "Output:.*$INTERNAL" | grep -q "enabled" && echo "yes" || echo "no")

# Get resolution widths
get_width() {
    local output=$1
    echo "$OUTPUTS" | grep -A 20 "Output:.*$output" | grep "Geometry:" | head -n1 | sed 's/.*Geometry: [0-9]*,[0-9]* \([0-9]*\)x.*/\1/'
}

if [ "$INTERNAL_ENABLED" = "yes" ]; then
    # Internal is ON → turn it OFF
    if [ -n "$THIRD" ]; then
        # Also disable third monitor
        kscreen-doctor output.$INTERNAL.disable output.$THIRD.disable output.$EXTERNAL.position.0,0 2>&1
        notify-send "Display" "Internal + middle screen disabled" -i video-display
    else
        kscreen-doctor output.$INTERNAL.disable output.$EXTERNAL.position.0,0 2>&1
        notify-send "Display" "Internal screen disabled" -i video-display
    fi
else
    # Internal is OFF → turn it ON
    INTERNAL_WIDTH=$(get_width "$INTERNAL")
    [ -z "$INTERNAL_WIDTH" ] && INTERNAL_WIDTH=1920

    if [ -n "$THIRD" ]; then
        # Third monitor present - enable it in the middle
        THIRD_WIDTH=$(get_width "$THIRD")
        [ -z "$THIRD_WIDTH" ] && THIRD_WIDTH=1920

        MIDDLE_POS=$INTERNAL_WIDTH
        EXTERNAL_POS=$((INTERNAL_WIDTH + THIRD_WIDTH))

        kscreen-doctor \
            output.$INTERNAL.enable output.$INTERNAL.position.0,0 \
            output.$THIRD.enable output.$THIRD.position.$MIDDLE_POS,0 \
            output.$EXTERNAL.position.$EXTERNAL_POS,0 2>&1
        notify-send "Display" "3 screens: Internal | $THIRD | External" -i video-display
    else
        # No third monitor - just internal + external
        kscreen-doctor output.$INTERNAL.enable output.$INTERNAL.position.0,0 output.$EXTERNAL.position.$INTERNAL_WIDTH,0 2>&1
        notify-send "Display" "Internal screen enabled (extended right)" -i video-display
    fi
fi
