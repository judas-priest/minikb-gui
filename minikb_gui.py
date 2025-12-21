#!/usr/bin/env python3
"""
MiniKB GUI - Configuration tool for 6-key + encoder mini keyboard
USB ID: 1189:8890 (Acer Communications & Multimedia)
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import threading
import time
from datetime import datetime

try:
    import usb.core
    import usb.util
    USB_AVAILABLE = True
except ImportError:
    USB_AVAILABLE = False
    print("Warning: pyusb not installed. Run: pip install pyusb")

# USB device identifiers
VENDOR_ID = 0x1189
PRODUCT_ID = 0x8890
ENDPOINT_OUT = 0x02
ENDPOINT_IN = 0x81  # Interrupt IN endpoint for reading keypresses

# Button identifiers for the device (6 keys + encoder with button)
BUTTONS = {
    'Button 1': 0x01,
    'Button 2': 0x02,
    'Button 3': 0x03,
    'Button 4': 0x04,
    'Button 5': 0x05,
    'Button 6': 0x06,
    'Knob Left': 0x0d,
    'Knob Press': 0x0e,
    'Knob Right': 0x0f,
}

# Reverse lookup for button names
BUTTON_ID_TO_NAME = {v: k for k, v in BUTTONS.items()}

# USB HID Key codes
HID_KEYCODES = {
    'None': 0x00,
    'A': 0x04, 'B': 0x05, 'C': 0x06, 'D': 0x07, 'E': 0x08,
    'F': 0x09, 'G': 0x0a, 'H': 0x0b, 'I': 0x0c, 'J': 0x0d,
    'K': 0x0e, 'L': 0x0f, 'M': 0x10, 'N': 0x11, 'O': 0x12,
    'P': 0x13, 'Q': 0x14, 'R': 0x15, 'S': 0x16, 'T': 0x17,
    'U': 0x18, 'V': 0x19, 'W': 0x1a, 'X': 0x1b, 'Y': 0x1c, 'Z': 0x1d,
    '1': 0x1e, '2': 0x1f, '3': 0x20, '4': 0x21, '5': 0x22,
    '6': 0x23, '7': 0x24, '8': 0x25, '9': 0x26, '0': 0x27,
    'Enter': 0x28, 'Escape': 0x29, 'Backspace': 0x2a, 'Tab': 0x2b,
    'Space': 0x2c, 'Minus': 0x2d, 'Equal': 0x2e,
    'Left Bracket': 0x2f, 'Right Bracket': 0x30, 'Backslash': 0x31,
    'Semicolon': 0x33, 'Apostrophe': 0x34, 'Grave': 0x35,
    'Comma': 0x36, 'Period': 0x37, 'Slash': 0x38,
    'Caps Lock': 0x39,
    'F1': 0x3a, 'F2': 0x3b, 'F3': 0x3c, 'F4': 0x3d, 'F5': 0x3e, 'F6': 0x3f,
    'F7': 0x40, 'F8': 0x41, 'F9': 0x42, 'F10': 0x43, 'F11': 0x44, 'F12': 0x45,
    'Print Screen': 0x46, 'Scroll Lock': 0x47, 'Pause': 0x48,
    'Insert': 0x49, 'Home': 0x4a, 'Page Up': 0x4b,
    'Delete': 0x4c, 'End': 0x4d, 'Page Down': 0x4e,
    'Right Arrow': 0x4f, 'Left Arrow': 0x50, 'Down Arrow': 0x51, 'Up Arrow': 0x52,
    'Num Lock': 0x53,
    'Numpad /': 0x54, 'Numpad *': 0x55, 'Numpad -': 0x56, 'Numpad +': 0x57,
    'Numpad Enter': 0x58,
    'Numpad 1': 0x59, 'Numpad 2': 0x5a, 'Numpad 3': 0x5b,
    'Numpad 4': 0x5c, 'Numpad 5': 0x5d, 'Numpad 6': 0x5e,
    'Numpad 7': 0x5f, 'Numpad 8': 0x60, 'Numpad 9': 0x61,
    'Numpad 0': 0x62, 'Numpad .': 0x63,
    'F13': 0x68, 'F14': 0x69, 'F15': 0x6a, 'F16': 0x6b,
    'F17': 0x6c, 'F18': 0x6d, 'F19': 0x6e, 'F20': 0x6f,
    'F21': 0x70, 'F22': 0x71, 'F23': 0x72, 'F24': 0x73,
    'Mute': 0x7f, 'Volume Up': 0x80, 'Volume Down': 0x81,
    'Cut': 0x7b, 'Copy': 0x7c, 'Paste': 0x7d,
    'Media Play/Pause': 0xe8, 'Media Stop': 0xe9,
    'Media Prev': 0xea, 'Media Next': 0xeb,
    'Media Mute': 0xef, 'Media Vol Up': 0xed, 'Media Vol Down': 0xee,
}

# Reverse lookup
KEYCODE_TO_NAME = {v: k for k, v in HID_KEYCODES.items()}

# Modifier key names
MODIFIER_NAMES = {
    0x01: 'L-Ctrl',
    0x02: 'L-Shift',
    0x04: 'L-Alt',
    0x08: 'L-Meta',
    0x10: 'R-Ctrl',
    0x20: 'R-Shift',
    0x40: 'R-Alt',
    0x80: 'R-Meta',
}


# RGB LED presets (R, G, B values 0-255)
RGB_PRESETS = {
    'Off': (0, 0, 0),
    'Red': (255, 0, 0),
    'Green': (0, 255, 0),
    'Blue': (0, 0, 255),
    'White': (255, 255, 255),
    'Cyan': (0, 255, 255),
    'Magenta': (255, 0, 255),
    'Yellow': (255, 255, 0),
    'Orange': (255, 128, 0),
    'Purple': (128, 0, 255),
    'Pink': (255, 128, 128),
    'Warm White': (255, 200, 150),
}


class MiniKBDevice:
    """USB communication with the mini keyboard"""

    def __init__(self):
        self.device = None
        self.was_kernel_driver_active = {}
        self.interface_claimed = []
        self.rgb_log_callback = None

    def connect(self):
        """Find and connect to the device"""
        if not USB_AVAILABLE:
            raise RuntimeError("pyusb not installed")

        self.device = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
        if self.device is None:
            raise RuntimeError(f"Device {VENDOR_ID:04x}:{PRODUCT_ID:04x} not found")

        # Detach kernel driver from all interfaces
        cfg = self.device.get_active_configuration()
        if cfg is None:
            self.device.set_configuration()
            cfg = self.device.get_active_configuration()

        for intf in cfg:
            intf_num = intf.bInterfaceNumber
            try:
                if self.device.is_kernel_driver_active(intf_num):
                    self.device.detach_kernel_driver(intf_num)
                    self.was_kernel_driver_active[intf_num] = True
            except (usb.core.USBError, NotImplementedError):
                pass

            try:
                usb.util.claim_interface(self.device, intf_num)
                self.interface_claimed.append(intf_num)
            except usb.core.USBError:
                pass

        # Find and cache all endpoints
        self._all_endpoints = self.find_all_in_endpoints()
        print(f"Found {len(self._all_endpoints)} IN endpoint(s)")
        for ep_addr, ep_size, intf in self._all_endpoints:
            print(f"  -> 0x{ep_addr:02x} size={ep_size} interface={intf}")

        # Send init packet
        self._send_packet(bytes([0x03] + [0x00] * 64))
        return True

    def disconnect(self):
        """Disconnect from the device"""
        if self.device:
            # Release interfaces
            for intf_num in self.interface_claimed:
                try:
                    usb.util.release_interface(self.device, intf_num)
                except usb.core.USBError:
                    pass

            # Reattach kernel drivers
            for intf_num, was_active in self.was_kernel_driver_active.items():
                if was_active:
                    try:
                        self.device.attach_kernel_driver(intf_num)
                    except (usb.core.USBError, NotImplementedError):
                        pass

            usb.util.dispose_resources(self.device)

        self.device = None
        self.was_kernel_driver_active = {}
        self.interface_claimed = []
        self._all_endpoints = []

    def _send_packet(self, data):
        """Send a 65-byte packet to the device"""
        if len(data) < 65:
            data = data + bytes(65 - len(data))
        self.device.write(ENDPOINT_OUT, data, timeout=1000)

    def find_all_in_endpoints(self):
        """Find all interrupt IN endpoints"""
        endpoints = []
        cfg = self.device.get_active_configuration()
        print(f"Device configuration: {cfg.bConfigurationValue}")
        for intf in cfg:
            print(f"  Interface {intf.bInterfaceNumber}: class={intf.bInterfaceClass}, subclass={intf.bInterfaceSubClass}")
            for ep in intf:
                direction = "IN" if usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_IN else "OUT"
                ep_type = {0: "CTRL", 1: "ISO", 2: "BULK", 3: "INTR"}[usb.util.endpoint_type(ep.bmAttributes)]
                print(f"    Endpoint 0x{ep.bEndpointAddress:02x}: {direction} {ep_type}, size={ep.wMaxPacketSize}")
                if usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_IN:
                    if usb.util.endpoint_type(ep.bmAttributes) == usb.util.ENDPOINT_TYPE_INTR:
                        endpoints.append((ep.bEndpointAddress, ep.wMaxPacketSize, intf.bInterfaceNumber))
        return endpoints if endpoints else [(ENDPOINT_IN, 64, 0)]

    def find_in_endpoint(self):
        """Find the first interrupt IN endpoint (legacy)"""
        endpoints = self.find_all_in_endpoints()
        if endpoints:
            return endpoints[0][0], endpoints[0][1]
        return ENDPOINT_IN, 64

    def read_input(self, timeout=100):
        """Read input from all IN endpoints (non-blocking with timeout)"""
        if self.device is None:
            return None

        results = []
        for ep_addr, ep_size, intf in self._all_endpoints:
            try:
                data = self.device.read(ep_addr, ep_size, timeout=timeout)
                if data:
                    results.append((ep_addr, bytes(data)))
            except usb.core.USBError as e:
                if e.errno not in (110, 75) and 'timeout' not in str(e).lower():
                    pass  # ignore timeouts and overflows

        return results if results else None

    def set_key(self, button_id, keycode):
        """Program a button with a specific keycode"""
        if self.device is None:
            raise RuntimeError("Not connected")

        # Start sequence
        start_packet = bytes([0x03, 0xa1, 0x01] + [0x00] * 62)
        self._send_packet(start_packet)

        if keycode == 0x00:
            # Clear key
            clear_packet = bytes([0x03, button_id, 0x10] + [0x00] * 62)
            self._send_packet(clear_packet)
        else:
            # Set key - first packet
            set_packet1 = bytes([0x03, button_id, 0x11, 0x01] + [0x00] * 61)
            self._send_packet(set_packet1)

            # Set key - second packet with keycode
            set_packet2 = bytes([0x03, button_id, 0x11, 0x01, 0x01, 0x00, keycode] + [0x00] * 58)
            self._send_packet(set_packet2)

        # End/commit sequence
        end_packet = bytes([0x03, 0xaa, 0xaa] + [0x00] * 62)
        self._send_packet(end_packet)

    def program_all(self, config):
        """Program all buttons from a config dict"""
        for button_name, button_id in BUTTONS.items():
            keycode = config.get(button_name, 0x00)
            self.set_key(button_id, keycode)

    def _log_rgb(self, message):
        """Log RGB-related messages"""
        if self.rgb_log_callback:
            self.rgb_log_callback(message)

    def set_rgb_experimental(self, r, g, b, led_index=0, pattern_id=0):
        """Try experimental RGB control commands.

        pattern_id selects different command formats to try:
        0: Standard format - 0x03, 0xb0, led, r, g, b
        1: Mode format - 0x03, 0xb1, mode, r, g, b
        2: Feature report style - 0x07, led, r, g, b, brightness
        3: Alt format - 0x03, 0xc0, led, r, g, b
        4: Direct format - 0x09, r, g, b, led
        5: Brightness format - 0x03, 0xb2, brightness, r, g, b
        """
        if self.device is None:
            raise RuntimeError("Not connected")

        patterns = {
            0: bytes([0x03, 0xb0, led_index, r, g, b] + [0x00] * 59),
            1: bytes([0x03, 0xb1, 0x01, r, g, b] + [0x00] * 59),  # mode=1
            2: bytes([0x07, led_index, r, g, b, 0xff] + [0x00] * 59),  # with brightness
            3: bytes([0x03, 0xc0, led_index, r, g, b] + [0x00] * 59),
            4: bytes([0x09, r, g, b, led_index] + [0x00] * 60),
            5: bytes([0x03, 0xb2, 0xff, r, g, b] + [0x00] * 59),  # brightness=255
            6: bytes([0x03, 0xa0, r, g, b] + [0x00] * 60),  # a0 command
            7: bytes([0x03, 0xab, led_index, r, g, b] + [0x00] * 59),  # ab command
            8: bytes([0x03, 0xac, r, g, b, led_index] + [0x00] * 59),  # ac command
            9: bytes([0x03, 0xad, 0x01, r, g, b] + [0x00] * 59),  # ad with mode
            10: bytes([0x03, 0x10, led_index, r, g, b] + [0x00] * 59),  # 0x10 cmd
            11: bytes([0x03, 0x20, r, g, b, led_index] + [0x00] * 59),  # 0x20 cmd
            12: bytes([0x03, 0x30, 0x01, r, g, b] + [0x00] * 59),  # 0x30 with mode
        }

        packet = patterns.get(pattern_id, patterns[0])
        self._log_rgb(f"Trying pattern {pattern_id}: {packet[:10].hex()}...")

        try:
            self._send_packet(packet)
            return True
        except usb.core.USBError as e:
            self._log_rgb(f"Pattern {pattern_id} error: {e}")
            return False

    def set_rgb_all_patterns(self, r, g, b, led_index=0):
        """Try all RGB patterns sequentially"""
        results = []
        for pattern_id in range(13):
            try:
                success = self.set_rgb_experimental(r, g, b, led_index, pattern_id)
                results.append((pattern_id, success, None))
                time.sleep(0.1)  # Small delay between commands
            except Exception as e:
                results.append((pattern_id, False, str(e)))
        return results

    def set_rgb_control_transfer(self, r, g, b, led_index=0):
        """Try RGB control via control transfer (vendor-specific)"""
        if self.device is None:
            raise RuntimeError("Not connected")

        # bmRequestType: 0x21 = Host to Device, Class, Interface
        # bRequest: 0x09 = SET_REPORT (HID)
        # wValue: 0x0300 = Report Type (Feature=3) | Report ID (0)
        # wIndex: interface number

        data = bytes([led_index, r, g, b, 0xff, 0x00, 0x00, 0x00])

        control_configs = [
            # (bmRequestType, bRequest, wValue, wIndex)
            (0x21, 0x09, 0x0300, 0),  # Standard HID SET_REPORT Feature
            (0x21, 0x09, 0x0200, 0),  # HID SET_REPORT Output
            (0x40, 0x01, 0x0000, 0),  # Vendor specific
            (0x40, 0xb0, led_index, 0),  # Vendor with LED index
            (0x21, 0x09, 0x0307, 0),  # Feature report ID 7
            (0x21, 0x09, 0x0309, 0),  # Feature report ID 9
        ]

        results = []
        for bmRequestType, bRequest, wValue, wIndex in control_configs:
            try:
                self._log_rgb(f"Control transfer: type=0x{bmRequestType:02x} req=0x{bRequest:02x} "
                             f"val=0x{wValue:04x} idx={wIndex}")
                self.device.ctrl_transfer(bmRequestType, bRequest, wValue, wIndex, data, timeout=1000)
                results.append((bmRequestType, bRequest, True, None))
                self._log_rgb(f"  -> Success!")
            except usb.core.USBError as e:
                results.append((bmRequestType, bRequest, False, str(e)))
                self._log_rgb(f"  -> Error: {e}")

        return results

    def enumerate_rgb_commands(self, r, g, b):
        """Enumerate possible RGB command bytes systematically"""
        if self.device is None:
            raise RuntimeError("Not connected")

        # Try command bytes that might relate to LED control
        # Based on patterns seen in similar devices
        candidate_cmds = [
            0x10, 0x11, 0x12, 0x20, 0x21, 0x22,
            0x30, 0x31, 0x32, 0xa0, 0xa1, 0xa2,
            0xb0, 0xb1, 0xb2, 0xb3, 0xc0, 0xc1,
            0xd0, 0xd1, 0xe0, 0xe1, 0xf0, 0xf1
        ]

        for cmd in candidate_cmds:
            packet = bytes([0x03, cmd, 0x00, r, g, b] + [0x00] * 59)
            self._log_rgb(f"Trying cmd 0x{cmd:02x}: {packet[:8].hex()}")
            try:
                self._send_packet(packet)
                time.sleep(0.05)
            except usb.core.USBError as e:
                self._log_rgb(f"  -> Error: {e}")

        return True


class InputMonitor:
    """Monitor keyboard input in a background thread"""

    def __init__(self, device, callback):
        self.device = device
        self.callback = callback
        self.running = False
        self.thread = None
        self.last_keys = set()

    def start(self):
        """Start monitoring"""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()

    def stop(self):
        """Stop monitoring"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=0.5)
            self.thread = None

    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                results = self.device.read_input(timeout=50)
                if results:
                    for ep_addr, data in results:
                        self._process_input(data, ep_addr)
            except Exception as e:
                if self.running:
                    self.callback({'type': 'error', 'message': str(e)})
                    time.sleep(0.5)

    def _process_input(self, data, ep_addr=0):
        """Process HID input data"""
        if len(data) < 1:
            return

        # Always log raw data for debugging
        self.callback({
            'type': 'raw',
            'endpoint': ep_addr,
            'data': data.hex(),
            'bytes': list(data)
        })

        # Standard HID keyboard report:
        # Byte 0: Modifier keys
        # Byte 1: Reserved
        # Bytes 2-7: Key codes
        modifier = data[0]
        keys = set(data[2:]) - {0x00}  # Remove empty slots

        # Detect new key presses
        new_keys = keys - self.last_keys
        released_keys = self.last_keys - keys

        for keycode in new_keys:
            key_name = KEYCODE_TO_NAME.get(keycode, f"0x{keycode:02X}")
            mod_str = self._get_modifier_string(modifier)
            self.callback({
                'type': 'press',
                'keycode': keycode,
                'key_name': key_name,
                'modifier': mod_str,
                'raw': data.hex()
            })

        for keycode in released_keys:
            key_name = KEYCODE_TO_NAME.get(keycode, f"0x{keycode:02X}")
            self.callback({
                'type': 'release',
                'keycode': keycode,
                'key_name': key_name,
                'raw': data.hex()
            })

        self.last_keys = keys

    def _get_modifier_string(self, modifier):
        """Convert modifier byte to string"""
        if modifier == 0:
            return ""
        mods = []
        for bit, name in MODIFIER_NAMES.items():
            if modifier & bit:
                mods.append(name)
        return "+".join(mods)


class MiniKBApp:
    """Main GUI Application"""

    CONFIG_FILE = os.path.expanduser("~/.minikb_config.json")

    def __init__(self, root):
        self.root = root
        self.root.title("MiniKB Configurator - 6 Keys + Encoder")
        self.root.geometry("750x650")
        self.root.resizable(True, True)

        self.device = MiniKBDevice()
        self.connected = False
        self.config = {}
        self.key_combos = {}
        self.monitor = None
        self.monitoring = False

        # Button state indicators
        self.button_indicators = {}

        self._create_ui()
        self._load_config()

        # Set initial config to match detected device state
        self._set_detected_config()

    def _create_ui(self):
        """Create the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        self.status_label = ttk.Label(status_frame, text="Disconnected", foreground="red")
        self.status_label.pack(side="left")

        self.connect_btn = ttk.Button(status_frame, text="Connect", command=self._toggle_connection)
        self.connect_btn.pack(side="right")

        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=5)
        main_frame.rowconfigure(1, weight=1)
        main_frame.columnconfigure(0, weight=1)

        # Keys tab
        keys_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(keys_frame, text="Keys Configuration")
        self._create_keys_tab(keys_frame)

        # Encoder tab
        encoder_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(encoder_frame, text="Encoder Configuration")
        self._create_encoder_tab(encoder_frame)

        # Monitor tab
        monitor_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(monitor_frame, text="Live Monitor")
        self._create_monitor_tab(monitor_frame)

        # RGB tab
        rgb_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(rgb_frame, text="RGB Control")
        self._create_rgb_tab(rgb_frame)

        # Action buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)

        ttk.Button(btn_frame, text="Apply to Device", command=self._apply_config).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Save Config", command=self._save_config).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Load Config", command=self._load_config_file).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Reset to Default", command=self._reset_config).pack(side="right", padx=5)

    def _create_keys_tab(self, parent):
        """Create the keys configuration tab"""
        # Grid of 6 buttons (2 rows x 3 columns)
        key_names = ['Button 1', 'Button 2', 'Button 3', 'Button 4', 'Button 5', 'Button 6']
        sorted_keys = list(HID_KEYCODES.keys())

        for i, name in enumerate(key_names):
            row = i // 3
            col = i % 3

            frame = ttk.LabelFrame(parent, text=name, padding="10")
            frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            parent.columnconfigure(col, weight=1)
            parent.rowconfigure(row, weight=1)

            combo = ttk.Combobox(frame, values=sorted_keys, state="readonly", width=15)
            combo.set("None")
            combo.pack(fill="x")
            self.key_combos[name] = combo

    def _create_encoder_tab(self, parent):
        """Create the encoder configuration tab"""
        encoder_items = [
            ('Knob Left', 'Rotate CCW (Left)'),
            ('Knob Press', 'Press (Click)'),
            ('Knob Right', 'Rotate CW (Right)'),
        ]
        sorted_keys = list(HID_KEYCODES.keys())

        for i, (key_name, display_name) in enumerate(encoder_items):
            frame = ttk.LabelFrame(parent, text=display_name, padding="10")
            frame.grid(row=i, column=0, padx=10, pady=10, sticky="ew")
            parent.columnconfigure(0, weight=1)

            combo = ttk.Combobox(frame, values=sorted_keys, state="readonly", width=20)
            combo.set("None")
            combo.pack(fill="x")
            self.key_combos[key_name] = combo

    def _create_monitor_tab(self, parent):
        """Create the live monitor tab"""
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)

        # Control frame
        ctrl_frame = ttk.Frame(parent)
        ctrl_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        self.monitor_btn = ttk.Button(ctrl_frame, text="Start Monitoring", command=self._toggle_monitoring)
        self.monitor_btn.pack(side="left")

        ttk.Button(ctrl_frame, text="Clear Log", command=self._clear_log).pack(side="left", padx=10)

        self.monitor_status = ttk.Label(ctrl_frame, text="Stopped", foreground="gray")
        self.monitor_status.pack(side="right")

        # Visual button display
        visual_frame = ttk.LabelFrame(parent, text="Button States", padding="10")
        visual_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        # Create visual indicators for buttons
        btn_container = ttk.Frame(visual_frame)
        btn_container.pack(fill="x")

        button_labels = ['1', '2', '3', '4', '5', '6', '<', 'O', '>']
        button_names = ['Button 1', 'Button 2', 'Button 3', 'Button 4', 'Button 5', 'Button 6',
                        'Knob Left', 'Knob Press', 'Knob Right']

        for i, (label, name) in enumerate(zip(button_labels, button_names)):
            frame = ttk.Frame(btn_container)
            frame.pack(side="left", padx=5, pady=5)

            indicator = tk.Label(frame, text=label, width=4, height=2,
                                 relief="raised", bg="lightgray", font=("Arial", 12, "bold"))
            indicator.pack()
            ttk.Label(frame, text=name.replace('Button ', 'B').replace('Knob ', ''),
                      font=("Arial", 8)).pack()
            self.button_indicators[name] = indicator

        # Log display
        log_frame = ttk.LabelFrame(parent, text="Event Log", padding="5")
        log_frame.grid(row=2, column=0, sticky="nsew")
        parent.rowconfigure(2, weight=1)

        # Text widget with scrollbar
        self.log_text = tk.Text(log_frame, height=10, width=70, font=("Courier", 10))
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)

        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Configure tags for coloring
        self.log_text.tag_configure("press", foreground="green")
        self.log_text.tag_configure("release", foreground="red")
        self.log_text.tag_configure("error", foreground="orange")
        self.log_text.tag_configure("time", foreground="gray")
        self.log_text.tag_configure("raw", foreground="blue")

    def _create_rgb_tab(self, parent):
        """Create the RGB LED control tab"""
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(2, weight=1)

        # Info label
        info_frame = ttk.LabelFrame(parent, text="RGB LED Control (Experimental)", padding="10")
        info_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        ttk.Label(info_frame, text="This feature tries different USB commands to control LEDs.\n"
                                    "The exact protocol for your device is unknown - try different patterns!",
                  wraplength=600).pack()

        # Color controls
        color_frame = ttk.LabelFrame(parent, text="Color Settings", padding="10")
        color_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        # RGB sliders
        slider_frame = ttk.Frame(color_frame)
        slider_frame.pack(fill="x", pady=5)

        self.rgb_vars = {
            'r': tk.IntVar(value=255),
            'g': tk.IntVar(value=0),
            'b': tk.IntVar(value=0)
        }

        for i, (color, label) in enumerate([('r', 'Red'), ('g', 'Green'), ('b', 'Blue')]):
            row_frame = ttk.Frame(slider_frame)
            row_frame.pack(fill="x", pady=2)

            ttk.Label(row_frame, text=f"{label}:", width=8).pack(side="left")
            slider = ttk.Scale(row_frame, from_=0, to=255, variable=self.rgb_vars[color],
                               orient="horizontal", length=200, command=lambda v: self._update_color_preview())
            slider.pack(side="left", padx=5)
            ttk.Label(row_frame, textvariable=self.rgb_vars[color], width=4).pack(side="left")

        # Color preview
        preview_frame = ttk.Frame(color_frame)
        preview_frame.pack(fill="x", pady=10)

        ttk.Label(preview_frame, text="Preview:").pack(side="left")
        self.color_preview = tk.Label(preview_frame, text="   ", bg="#ff0000", width=10, height=2, relief="sunken")
        self.color_preview.pack(side="left", padx=10)

        # Preset colors
        presets_frame = ttk.Frame(color_frame)
        presets_frame.pack(fill="x", pady=5)

        ttk.Label(presets_frame, text="Presets:").pack(side="left")
        for name, (r, g, b) in list(RGB_PRESETS.items())[:8]:  # First 8 presets
            btn = ttk.Button(presets_frame, text=name, width=8,
                            command=lambda r=r, g=g, b=b: self._set_rgb_preset(r, g, b))
            btn.pack(side="left", padx=2)

        # Second row of presets
        presets_frame2 = ttk.Frame(color_frame)
        presets_frame2.pack(fill="x", pady=2)
        ttk.Label(presets_frame2, text="        ").pack(side="left")
        for name, (r, g, b) in list(RGB_PRESETS.items())[8:]:  # Remaining presets
            btn = ttk.Button(presets_frame2, text=name, width=8,
                            command=lambda r=r, g=g, b=b: self._set_rgb_preset(r, g, b))
            btn.pack(side="left", padx=2)

        # LED selection and pattern
        control_frame = ttk.Frame(color_frame)
        control_frame.pack(fill="x", pady=10)

        ttk.Label(control_frame, text="LED Index:").pack(side="left")
        self.led_index_var = tk.IntVar(value=0)
        led_spin = ttk.Spinbox(control_frame, from_=0, to=5, textvariable=self.led_index_var, width=5)
        led_spin.pack(side="left", padx=5)

        ttk.Label(control_frame, text="Pattern:").pack(side="left", padx=(20, 0))
        self.pattern_var = tk.IntVar(value=0)
        pattern_spin = ttk.Spinbox(control_frame, from_=0, to=12, textvariable=self.pattern_var, width=5)
        pattern_spin.pack(side="left", padx=5)

        # Action buttons
        action_frame = ttk.Frame(color_frame)
        action_frame.pack(fill="x", pady=10)

        ttk.Button(action_frame, text="Send Color", command=self._send_rgb_color).pack(side="left", padx=5)
        ttk.Button(action_frame, text="Try All Patterns", command=self._try_all_rgb_patterns).pack(side="left", padx=5)
        ttk.Button(action_frame, text="Try Control Transfers", command=self._try_rgb_control).pack(side="left", padx=5)
        ttk.Button(action_frame, text="Enumerate Commands", command=self._enumerate_rgb).pack(side="left", padx=5)

        # RGB log
        log_frame = ttk.LabelFrame(parent, text="RGB Command Log", padding="5")
        log_frame.grid(row=2, column=0, sticky="nsew")
        parent.rowconfigure(2, weight=1)

        self.rgb_log = tk.Text(log_frame, height=10, width=70, font=("Courier", 9))
        rgb_scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.rgb_log.yview)
        self.rgb_log.configure(yscrollcommand=rgb_scrollbar.set)

        self.rgb_log.pack(side="left", fill="both", expand=True)
        rgb_scrollbar.pack(side="right", fill="y")

        # Clear log button
        ttk.Button(log_frame, text="Clear", command=lambda: self.rgb_log.delete("1.0", "end")).pack(side="bottom")

        # Set up RGB log callback
        self.device.rgb_log_callback = self._rgb_log

    def _update_color_preview(self):
        """Update the color preview box"""
        r = self.rgb_vars['r'].get()
        g = self.rgb_vars['g'].get()
        b = self.rgb_vars['b'].get()
        color = f"#{r:02x}{g:02x}{b:02x}"
        self.color_preview.config(bg=color)

    def _set_rgb_preset(self, r, g, b):
        """Set RGB sliders to preset values"""
        self.rgb_vars['r'].set(r)
        self.rgb_vars['g'].set(g)
        self.rgb_vars['b'].set(b)
        self._update_color_preview()

    def _rgb_log(self, message):
        """Log RGB message"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.rgb_log.insert("end", f"[{timestamp}] {message}\n")
        self.rgb_log.see("end")

    def _send_rgb_color(self):
        """Send RGB color to device"""
        if not self.connected:
            messagebox.showwarning("Not Connected", "Please connect to the device first.")
            return

        r = self.rgb_vars['r'].get()
        g = self.rgb_vars['g'].get()
        b = self.rgb_vars['b'].get()
        led_index = self.led_index_var.get()
        pattern = self.pattern_var.get()

        self._rgb_log(f"Sending R={r} G={g} B={b} to LED {led_index} using pattern {pattern}")

        try:
            self.device.set_rgb_experimental(r, g, b, led_index, pattern)
            self._rgb_log("Command sent successfully")
        except Exception as e:
            self._rgb_log(f"Error: {e}")

    def _try_all_rgb_patterns(self):
        """Try all RGB patterns"""
        if not self.connected:
            messagebox.showwarning("Not Connected", "Please connect to the device first.")
            return

        r = self.rgb_vars['r'].get()
        g = self.rgb_vars['g'].get()
        b = self.rgb_vars['b'].get()
        led_index = self.led_index_var.get()

        self._rgb_log(f"Trying all patterns for R={r} G={g} B={b} LED={led_index}")
        self._rgb_log("Watch your device for any LED changes!")

        try:
            results = self.device.set_rgb_all_patterns(r, g, b, led_index)
            success_count = sum(1 for _, ok, _ in results if ok)
            self._rgb_log(f"Completed: {success_count}/{len(results)} commands sent")
        except Exception as e:
            self._rgb_log(f"Error: {e}")

    def _try_rgb_control(self):
        """Try RGB control transfers"""
        if not self.connected:
            messagebox.showwarning("Not Connected", "Please connect to the device first.")
            return

        r = self.rgb_vars['r'].get()
        g = self.rgb_vars['g'].get()
        b = self.rgb_vars['b'].get()
        led_index = self.led_index_var.get()

        self._rgb_log(f"Trying control transfers for R={r} G={g} B={b}")

        try:
            self.device.set_rgb_control_transfer(r, g, b, led_index)
            self._rgb_log("Control transfer tests completed")
        except Exception as e:
            self._rgb_log(f"Error: {e}")

    def _enumerate_rgb(self):
        """Enumerate RGB command bytes"""
        if not self.connected:
            messagebox.showwarning("Not Connected", "Please connect to the device first.")
            return

        r = self.rgb_vars['r'].get()
        g = self.rgb_vars['g'].get()
        b = self.rgb_vars['b'].get()

        self._rgb_log(f"Enumerating command bytes for R={r} G={g} B={b}")
        self._rgb_log("This will try many commands - watch for LED changes!")

        try:
            self.device.enumerate_rgb_commands(r, g, b)
            self._rgb_log("Enumeration completed")
        except Exception as e:
            self._rgb_log(f"Error: {e}")

    def _toggle_monitoring(self):
        """Toggle input monitoring"""
        if self.monitoring:
            self._stop_monitoring()
        else:
            self._start_monitoring()

    def _start_monitoring(self):
        """Start monitoring keyboard input"""
        if not self.connected:
            messagebox.showwarning("Not Connected", "Please connect to the device first.")
            return

        self.monitor = InputMonitor(self.device, self._on_input_event)
        self.monitor.start()
        self.monitoring = True
        self.monitor_btn.config(text="Stop Monitoring")
        self.monitor_status.config(text="Monitoring...", foreground="green")
        self._log_event("Monitoring started", "info")

    def _stop_monitoring(self):
        """Stop monitoring keyboard input"""
        if self.monitor:
            self.monitor.stop()
            self.monitor = None
        self.monitoring = False
        self.monitor_btn.config(text="Start Monitoring")
        self.monitor_status.config(text="Stopped", foreground="gray")
        self._log_event("Monitoring stopped", "info")

        # Reset all indicators
        for indicator in self.button_indicators.values():
            indicator.config(bg="lightgray")

    def _on_input_event(self, event):
        """Handle input event from monitor thread"""
        # Schedule UI update on main thread
        self.root.after(0, lambda: self._process_event(event))

    def _process_event(self, event):
        """Process input event on main thread"""
        event_type = event.get('type')

        if event_type == 'error':
            self._log_event(f"Error: {event.get('message')}", "error")
            return

        if event_type == 'raw':
            # Debug output - show all raw packets
            ep = event.get('endpoint', 0)
            data = event.get('data', '')
            bytes_list = event.get('bytes', [])
            self._log_event(f"RAW EP{ep:02x}: {data}  bytes: {bytes_list}", "raw")
            return

        key_name = event.get('key_name', '?')
        keycode = event.get('keycode', 0)
        modifier = event.get('modifier', '')
        raw = event.get('raw', '')

        # Build display string
        if modifier:
            display = f"{modifier}+{key_name}"
        else:
            display = key_name

        if event_type == 'press':
            self._log_event(f"PRESS:   {display:20} (0x{keycode:02X})  raw: {raw}", "press")
            self._highlight_button(keycode, True)
        elif event_type == 'release':
            self._log_event(f"RELEASE: {display:20} (0x{keycode:02X})", "release")
            self._highlight_button(keycode, False)

    def _highlight_button(self, keycode, pressed):
        """Highlight button indicator based on keycode and current config"""
        # Build dynamic mapping from current UI config
        key_to_buttons = {}
        for btn_name, combo in self.key_combos.items():
            key_name = combo.get()
            kc = HID_KEYCODES.get(key_name, 0)
            if kc != 0:
                if kc not in key_to_buttons:
                    key_to_buttons[kc] = []
                key_to_buttons[kc].append(btn_name)

        # Highlight all buttons that match this keycode
        button_names = key_to_buttons.get(keycode, [])
        for button_name in button_names:
            if button_name in self.button_indicators:
                indicator = self.button_indicators[button_name]
                if pressed:
                    indicator.config(bg="lime")
                else:
                    indicator.config(bg="lightgray")

    def _log_event(self, message, tag="info"):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.log_text.insert("end", f"[{timestamp}] ", "time")
        self.log_text.insert("end", f"{message}\n", tag)
        self.log_text.see("end")

        # Limit log size
        lines = int(self.log_text.index('end-1c').split('.')[0])
        if lines > 500:
            self.log_text.delete("1.0", "100.0")

    def _clear_log(self):
        """Clear the log"""
        self.log_text.delete("1.0", "end")

    def _toggle_connection(self):
        """Toggle device connection"""
        if self.connected:
            self._disconnect()
        else:
            self._connect()

    def _connect(self):
        """Connect to the device"""
        try:
            self.device.connect()
            self.connected = True
            self.status_label.config(text=f"Connected: {VENDOR_ID:04x}:{PRODUCT_ID:04x}", foreground="green")
            self.connect_btn.config(text="Disconnect")
            messagebox.showinfo("Success", "Connected to MiniKB device!")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect:\n{e}\n\nMake sure:\n1. Device is plugged in\n2. You have permissions (try running with sudo)")

    def _disconnect(self):
        """Disconnect from the device"""
        if self.monitoring:
            self._stop_monitoring()
        self.device.disconnect()
        self.connected = False
        self.status_label.config(text="Disconnected", foreground="red")
        self.connect_btn.config(text="Connect")

    def _get_current_config(self):
        """Get current configuration from UI"""
        config = {}
        for name, combo in self.key_combos.items():
            key_name = combo.get()
            config[name] = HID_KEYCODES.get(key_name, 0x00)
        return config

    def _apply_config(self):
        """Apply configuration to device"""
        if not self.connected:
            messagebox.showwarning("Not Connected", "Please connect to the device first.")
            return

        config = self._get_current_config()
        try:
            for button_name, keycode in config.items():
                button_id = BUTTONS.get(button_name)
                if button_id:
                    self.device.set_key(button_id, keycode)
            messagebox.showinfo("Success", "Configuration applied to device!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply configuration:\n{e}")

    def _save_config(self):
        """Save configuration to file"""
        config = {}
        for name, combo in self.key_combos.items():
            config[name] = combo.get()

        try:
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
            messagebox.showinfo("Saved", f"Configuration saved to:\n{self.CONFIG_FILE}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save:\n{e}")

    def _load_config(self):
        """Load configuration from default file"""
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                self._apply_config_to_ui(config)
            except Exception:
                pass

    def _load_config_file(self):
        """Load configuration from selected file"""
        filepath = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filepath:
            try:
                with open(filepath, 'r') as f:
                    config = json.load(f)
                self._apply_config_to_ui(config)
                messagebox.showinfo("Loaded", "Configuration loaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load:\n{e}")

    def _apply_config_to_ui(self, config):
        """Apply config dict to UI elements"""
        for name, combo in self.key_combos.items():
            key_name = config.get(name, "None")
            if key_name in HID_KEYCODES:
                combo.set(key_name)

    def _set_detected_config(self):
        """Set UI to match currently detected device configuration"""
        # Based on device testing - current actual state
        detected = {
            'Button 1': 'F13', 'Button 2': 'F14', 'Button 3': 'F15',
            'Button 4': 'C', 'Button 5': 'C', 'Button 6': 'C',  # Currently Ctrl+C
            'Knob Left': 'F16', 'Knob Press': 'F17', 'Knob Right': 'F18',
        }
        self._apply_config_to_ui(detected)

    def _reset_config(self):
        """Reset all settings to recommended F13-F21 mapping"""
        defaults = {
            'Button 1': 'F13', 'Button 2': 'F14', 'Button 3': 'F15',
            'Button 4': 'F16', 'Button 5': 'F17', 'Button 6': 'F18',
            'Knob Left': 'F19', 'Knob Press': 'F20', 'Knob Right': 'F21',
        }
        self._apply_config_to_ui(defaults)


def main():
    root = tk.Tk()

    # Set theme
    style = ttk.Style()
    try:
        style.theme_use('clam')
    except tk.TclError:
        pass

    app = MiniKBApp(root)

    # Handle window close
    def on_close():
        if app.monitoring:
            app._stop_monitoring()
        if app.connected:
            app._disconnect()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
