# MiniKB GUI

GUI application for configuring 6-key + encoder mini keyboard (USB ID: 1189:8890).

## Features

- Configure all 6 keys and encoder (left/right rotation + press)
- Supports all standard USB HID keycodes including F13-F24
- Save/load configurations to JSON files
- User-friendly tkinter interface

## Requirements

- Python 3.6+
- pyusb
- tkinter (usually included with Python)
- libusb (system library)

## Installation

### Quick Install
```bash
chmod +x install.sh
./install.sh
```

### Manual Install

1. Install dependencies:
```bash
# Debian/Ubuntu
sudo apt install python3-tk libusb-1.0-0

# Install Python package
pip3 install pyusb
```

2. Install udev rules (for non-root access):
```bash
sudo cp 99-minikb.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger
```

3. Add yourself to plugdev group:
```bash
sudo usermod -a -G plugdev $USER
# Log out and log back in
```

## Usage

```bash
# Run GUI
python3 minikb_gui.py

# Or use the run script
./run.sh

# If permission denied, run with sudo
sudo python3 minikb_gui.py
```

## Configuration

The application saves configuration to `~/.minikb_config.json`.

### Key Mapping

| Button   | Default Key |
|----------|-------------|
| Button 1 | F13         |
| Button 2 | F14         |
| Button 3 | F15         |
| Button 4 | F16         |
| Button 5 | F17         |
| Button 6 | F18         |
| Knob Left | F19        |
| Knob Press | F20       |
| Knob Right | F21       |

## Troubleshooting

### Device not found
- Check if device is connected: `lsusb | grep 1189`
- Verify USB ID matches: `1189:8890`

### Permission denied
- Install udev rules and add yourself to plugdev group
- Or run with sudo

### pyusb not found
```bash
pip3 install pyusb
```

## Related

- Original C implementation: `../hid-minikb-libusb/`
- Based on: https://github.com/devkev/hid-minikb-libusb
