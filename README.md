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

### GUI Mode (Recommended)
```bash
# Run GUI
python3 minikb_gui.py

# Or use the run script
./run.sh

# If permission denied, run with sudo
sudo python3 minikb_gui.py
```

### YAML Config Mode (ch57x-keyboard-tool compatible)

The GUI now supports loading YAML configs in the same format as `ch57x-keyboard-tool`!

**Load YAML:**
1. Click "Load Config" button in GUI
2. Select your `mapping.yaml` file
3. Config will be uploaded directly to device

**Or use CLI:**
```bash
# Using ch57x-keyboard-tool (recommended)
ch57x-keyboard-tool upload < mapping.yaml
ch57x-keyboard-tool led 1  # Set RGB mode
```

See `mapping.yaml` for example configuration.

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

## YAML Configuration

The project supports YAML configs compatible with [ch57x-keyboard-tool](https://github.com/kriomant/ch57x-keyboard-tool).

**Install ch57x-keyboard-tool:**
```bash
cargo install ch57x-keyboard-tool
```

**Example mapping.yaml:**
```yaml
orientation: normal
rows: 2
columns: 3
knobs: 1

layers:
  - buttons:
      - [a, b, c]
      - [d, e, f]
    knobs:
      - ccw: volumedown
        press: mute
        cw: volumeup
```

**Features:**
- Modifier support: `ctrl-c`, `ctrl-shift-t`, etc.
- Media keys: `volumeup`, `volumedown`, `mute`, `play`, `next`, `previous`
- Function keys: `f1`-`f24`
- RGB control: `ch57x-keyboard-tool led 0-3`

## Related

- ch57x-keyboard-tool: https://github.com/kriomant/ch57x-keyboard-tool
- Setup guide: https://xaviesteve.com/7047/setup-macropad-aliexpress-linux/
- Original C implementation: `../hid-minikb-libusb/`
- Based on: https://github.com/devkev/hid-minikb-libusb
