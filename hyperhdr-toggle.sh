#!/bin/bash
# Toggle HyperHDR service via systemd

if systemctl --user is-active --quiet hyperhdr.service; then
    # HyperHDR is running → stop it
    systemctl --user stop hyperhdr.service
    notify-send "HyperHDR" "Stopped" -i video-display
else
    # HyperHDR is not running → start it
    systemctl --user start hyperhdr.service
    notify-send "HyperHDR" "Started" -i video-display
fi
