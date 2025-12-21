#!/usr/bin/env python3
"""
MiniKB CLI - Command-line tool for configuring 6-key + encoder mini keyboard
USB ID: 1189:8890 (Acer Communications & Multimedia)

Usage:
    python3 minikb_cli.py --list-keys           # Show available keys
    python3 minikb_cli.py --default             # Apply default config (F13-F21)
    python3 minikb_cli.py --button1 F13 --button2 F14 ...
    python3 minikb_cli.py --config config.json  # Apply from file
"""

import argparse
import json
import sys

try:
    import usb.core
    import usb.util
except ImportError:
    print("Error: pyusb not installed. Run: pip install pyusb")
    sys.exit(1)

# USB device identifiers
VENDOR_ID = 0x1189
PRODUCT_ID = 0x8890
ENDPOINT_OUT = 0x02

# Button identifiers
BUTTONS = {
    'button1': 0x01,
    'button2': 0x02,
    'button3': 0x03,
    'button4': 0x04,
    'button5': 0x05,
    'button6': 0x06,
    'knob_left': 0x0d,
    'knob_press': 0x0e,
    'knob_right': 0x0f,
}

# USB HID Key codes
HID_KEYCODES = {
    'none': 0x00,
    'a': 0x04, 'b': 0x05, 'c': 0x06, 'd': 0x07, 'e': 0x08,
    'f': 0x09, 'g': 0x0a, 'h': 0x0b, 'i': 0x0c, 'j': 0x0d,
    'k': 0x0e, 'l': 0x0f, 'm': 0x10, 'n': 0x11, 'o': 0x12,
    'p': 0x13, 'q': 0x14, 'r': 0x15, 's': 0x16, 't': 0x17,
    'u': 0x18, 'v': 0x19, 'w': 0x1a, 'x': 0x1b, 'y': 0x1c, 'z': 0x1d,
    '1': 0x1e, '2': 0x1f, '3': 0x20, '4': 0x21, '5': 0x22,
    '6': 0x23, '7': 0x24, '8': 0x25, '9': 0x26, '0': 0x27,
    'enter': 0x28, 'escape': 0x29, 'backspace': 0x2a, 'tab': 0x2b,
    'space': 0x2c, 'minus': 0x2d, 'equal': 0x2e,
    'f1': 0x3a, 'f2': 0x3b, 'f3': 0x3c, 'f4': 0x3d, 'f5': 0x3e, 'f6': 0x3f,
    'f7': 0x40, 'f8': 0x41, 'f9': 0x42, 'f10': 0x43, 'f11': 0x44, 'f12': 0x45,
    'printscreen': 0x46, 'scrolllock': 0x47, 'pause': 0x48,
    'insert': 0x49, 'home': 0x4a, 'pageup': 0x4b,
    'delete': 0x4c, 'end': 0x4d, 'pagedown': 0x4e,
    'right': 0x4f, 'left': 0x50, 'down': 0x51, 'up': 0x52,
    'f13': 0x68, 'f14': 0x69, 'f15': 0x6a, 'f16': 0x6b,
    'f17': 0x6c, 'f18': 0x6d, 'f19': 0x6e, 'f20': 0x6f,
    'f21': 0x70, 'f22': 0x71, 'f23': 0x72, 'f24': 0x73,
    'mute': 0x7f, 'volumeup': 0x80, 'volumedown': 0x81,
    'cut': 0x7b, 'copy': 0x7c, 'paste': 0x7d,
    'playpause': 0xe8, 'stop': 0xe9, 'prev': 0xea, 'next': 0xeb,
}


class MiniKBDevice:
    """USB communication with the mini keyboard"""

    def __init__(self):
        self.device = None

    def connect(self):
        """Find and connect to the device"""
        self.device = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
        if self.device is None:
            raise RuntimeError(f"Device {VENDOR_ID:04x}:{PRODUCT_ID:04x} not found")

        try:
            if self.device.is_kernel_driver_active(0):
                self.device.detach_kernel_driver(0)
        except (usb.core.USBError, NotImplementedError):
            pass

        try:
            self.device.set_configuration()
        except usb.core.USBError:
            pass

        self._send_packet(bytes([0x03] + [0x00] * 64))
        print(f"Connected to device {VENDOR_ID:04x}:{PRODUCT_ID:04x}")

    def _send_packet(self, data):
        """Send a 65-byte packet to the device"""
        if len(data) < 65:
            data = data + bytes(65 - len(data))
        self.device.write(ENDPOINT_OUT, data, timeout=1000)

    def set_key(self, button_id, keycode):
        """Program a button with a specific keycode"""
        # Start sequence
        self._send_packet(bytes([0x03, 0xa1, 0x01] + [0x00] * 62))

        if keycode == 0x00:
            self._send_packet(bytes([0x03, button_id, 0x10] + [0x00] * 62))
        else:
            self._send_packet(bytes([0x03, button_id, 0x11, 0x01] + [0x00] * 61))
            self._send_packet(bytes([0x03, button_id, 0x11, 0x01, 0x01, 0x00, keycode] + [0x00] * 58))

        # End sequence
        self._send_packet(bytes([0x03, 0xaa, 0xaa] + [0x00] * 62))


def main():
    parser = argparse.ArgumentParser(description='MiniKB CLI - Configure 6-key + encoder keyboard')

    parser.add_argument('--list-keys', action='store_true', help='List available key names')
    parser.add_argument('--default', action='store_true', help='Apply default config (F13-F21)')
    parser.add_argument('--config', type=str, help='Load config from JSON file')

    for btn in BUTTONS.keys():
        parser.add_argument(f'--{btn}', type=str, help=f'Key for {btn}')

    args = parser.parse_args()

    if args.list_keys:
        print("Available keys:")
        for name in sorted(HID_KEYCODES.keys()):
            print(f"  {name}")
        return

    # Build config
    config = {}

    if args.default:
        config = {
            'button1': 'f13', 'button2': 'f14', 'button3': 'f15',
            'button4': 'f16', 'button5': 'f17', 'button6': 'f18',
            'knob_left': 'f19', 'knob_press': 'f20', 'knob_right': 'f21',
        }
    elif args.config:
        with open(args.config, 'r') as f:
            config = json.load(f)
    else:
        for btn in BUTTONS.keys():
            val = getattr(args, btn, None)
            if val:
                config[btn] = val.lower()

    if not config:
        parser.print_help()
        return

    # Connect and apply
    device = MiniKBDevice()
    try:
        device.connect()

        for btn_name, key_name in config.items():
            btn_id = BUTTONS.get(btn_name.lower().replace(' ', '_').replace('-', '_'))
            keycode = HID_KEYCODES.get(key_name.lower(), 0x00)

            if btn_id:
                device.set_key(btn_id, keycode)
                print(f"  {btn_name} -> {key_name} (0x{keycode:02x})")

        print("Configuration applied successfully!")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
