#!/bin/bash
# Installation script for MiniKB GUI

set -e

echo "=== MiniKB GUI Installer ==="

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required"
    exit 1
fi

# Install Python dependencies
echo "[1/3] Installing Python dependencies..."
pip3 install --user pyusb

# Install udev rules
echo "[2/3] Installing udev rules..."
if [ -f "99-minikb.rules" ]; then
    sudo cp 99-minikb.rules /etc/udev/rules.d/
    sudo udevadm control --reload-rules
    sudo udevadm trigger
    echo "udev rules installed successfully"
else
    echo "Warning: 99-minikb.rules not found, skipping"
fi

# Add user to plugdev group
echo "[3/3] Adding user to plugdev group..."
sudo usermod -a -G plugdev $USER

echo ""
echo "=== Installation Complete ==="
echo ""
echo "IMPORTANT: Log out and log back in for group changes to take effect!"
echo ""
echo "To run the GUI:"
echo "  python3 minikb_gui.py"
echo ""
echo "Or with sudo if udev rules don't work:"
echo "  sudo python3 minikb_gui.py"
