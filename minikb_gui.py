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


# LED colors supported by ch57x protocol (from ch57x-keyboard-tool)
LED_COLORS = {
    'Off': 0,
    'White': 0,
    'Red': 1,
    'Orange': 2,
    'Yellow': 3,
    'Green': 4,
    'Cyan': 5,
    'Blue': 6,
    'Purple': 7,
}

# LED modes
LED_MODES = {
    'Off': 0,
    'Steady': 1,
    'Breathe': 2,
    'Blink': 3,
    'Rainbow': 4,
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
        print(f"DEBUG RGB: {message}")
        if self.rgb_log_callback:
            self.rgb_log_callback(message)

    def _send_led_packet(self, data):
        """Send LED control packet (9 bytes for ch57x protocol)"""
        # Pad to 65 bytes for USB HID
        if len(data) < 65:
            data = data + bytes(65 - len(data))
        self.device.write(ENDPOINT_OUT, data, timeout=1000)

    def set_led_mode(self, mode):
        """Set LED mode using ch57x protocol for 8890 keyboard.

        Protocol from ch57x-keyboard-tool:
        1. Init:   [0x03, 0xa1, 0x01, 0, 0, 0, 0, 0, 0]
        2. Mode:   [0x03, 0xb0, 0x18, <mode>, 0, 0, 0, 0, 0]
        3. Finish: [0x03, 0xaa, 0xa1, 0, 0, 0, 0, 0, 0]
        """
        if self.device is None:
            raise RuntimeError("Not connected")

        self._log_rgb(f"Setting LED mode: {mode}")

        # Init packet
        init_packet = bytes([0x03, 0xa1, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        self._log_rgb(f"  Init: {init_packet.hex()}")
        self._send_led_packet(init_packet)

        # Mode packet
        mode_packet = bytes([0x03, 0xb0, 0x18, mode, 0x00, 0x00, 0x00, 0x00, 0x00])
        self._log_rgb(f"  Mode: {mode_packet.hex()}")
        self._send_led_packet(mode_packet)

        # Finish packet
        finish_packet = bytes([0x03, 0xaa, 0xa1, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        self._log_rgb(f"  Finish: {finish_packet.hex()}")
        self._send_led_packet(finish_packet)

        self._log_rgb(f"LED mode {mode} set successfully")
        return True

    def set_led_color_mode(self, color_code, mode_code=1):
        """Set LED with color and mode.

        Color codes: 0=White, 1=Red, 2=Orange, 3=Yellow, 4=Green, 5=Cyan, 6=Blue, 7=Purple
        Mode codes: 0=Off, 1=Steady, 2=Breathe, 3=Blink, etc.

        Combined mode byte might be: (color << 4) | mode
        """
        if self.device is None:
            raise RuntimeError("Not connected")

        # Try different encodings
        combined = (color_code << 4) | mode_code
        self._log_rgb(f"Setting LED: color={color_code}, mode={mode_code}, combined=0x{combined:02x}")

        return self.set_led_mode(combined)

    def try_all_led_modes(self):
        """Try all LED modes 0-255 to find working ones"""
        if self.device is None:
            raise RuntimeError("Not connected")

        self._log_rgb("Trying LED modes 0-20...")
        for mode in range(21):
            try:
                self._log_rgb(f"--- Mode {mode} ---")
                self.set_led_mode(mode)
                time.sleep(0.3)
            except Exception as e:
                self._log_rgb(f"Mode {mode} error: {e}")

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
        info_frame = ttk.LabelFrame(parent, text="LED Control (ch57x protocol)", padding="10")
        info_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        ttk.Label(info_frame, text="Control LED backlight using ch57x-keyboard-tool protocol.\n"
                                    "Select color and mode, then click Apply.",
                  wraplength=600).pack()

        # Color and mode controls
        color_frame = ttk.LabelFrame(parent, text="LED Settings", padding="10")
        color_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        # Color selection
        color_row = ttk.Frame(color_frame)
        color_row.pack(fill="x", pady=5)

        ttk.Label(color_row, text="Color:", width=10).pack(side="left")
        self.led_color_var = tk.StringVar(value="Red")
        color_combo = ttk.Combobox(color_row, textvariable=self.led_color_var,
                                   values=list(LED_COLORS.keys()), state="readonly", width=15)
        color_combo.pack(side="left", padx=5)

        # Color preview buttons
        for color_name in ['Red', 'Green', 'Blue', 'Cyan', 'Purple', 'White']:
            btn = ttk.Button(color_row, text=color_name, width=7,
                            command=lambda c=color_name: self.led_color_var.set(c))
            btn.pack(side="left", padx=2)

        # Mode selection
        mode_row = ttk.Frame(color_frame)
        mode_row.pack(fill="x", pady=5)

        ttk.Label(mode_row, text="Mode:", width=10).pack(side="left")
        self.led_mode_var = tk.StringVar(value="Steady")
        mode_combo = ttk.Combobox(mode_row, textvariable=self.led_mode_var,
                                  values=list(LED_MODES.keys()), state="readonly", width=15)
        mode_combo.pack(side="left", padx=5)

        # Mode buttons
        for mode_name in LED_MODES.keys():
            btn = ttk.Button(mode_row, text=mode_name, width=8,
                            command=lambda m=mode_name: self.led_mode_var.set(m))
            btn.pack(side="left", padx=2)

        # Raw mode value
        raw_row = ttk.Frame(color_frame)
        raw_row.pack(fill="x", pady=5)

        ttk.Label(raw_row, text="Raw Mode:", width=10).pack(side="left")
        self.led_raw_var = tk.IntVar(value=1)
        raw_spin = ttk.Spinbox(raw_row, from_=0, to=255, textvariable=self.led_raw_var, width=8)
        raw_spin.pack(side="left", padx=5)
        ttk.Label(raw_row, text="(0-255, use for direct mode control)").pack(side="left")

        # Action buttons
        action_frame = ttk.Frame(color_frame)
        action_frame.pack(fill="x", pady=15)

        ttk.Button(action_frame, text="Apply Color+Mode", command=self._apply_led_color).pack(side="left", padx=5)
        ttk.Button(action_frame, text="Apply Raw Mode", command=self._apply_led_raw).pack(side="left", padx=5)
        ttk.Button(action_frame, text="LED Off", command=self._led_off).pack(side="left", padx=5)
        ttk.Button(action_frame, text="Try All Modes (0-20)", command=self._try_all_led_modes).pack(side="left", padx=5)

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

    def _rgb_log(self, message):
        """Log RGB message"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.rgb_log.insert("end", f"[{timestamp}] {message}\n")
        self.rgb_log.see("end")

    def _apply_led_color(self):
        """Apply LED color and mode"""
        if not self.connected:
            messagebox.showwarning("Not Connected", "Please connect to the device first.")
            return

        color_name = self.led_color_var.get()
        mode_name = self.led_mode_var.get()

        color_code = LED_COLORS.get(color_name, 1)
        mode_code = LED_MODES.get(mode_name, 1)

        self._rgb_log(f"Applying: {color_name} (code={color_code}), {mode_name} (code={mode_code})")

        try:
            self.device.set_led_color_mode(color_code, mode_code)
            self._rgb_log("LED color+mode applied!")
        except Exception as e:
            self._rgb_log(f"Error: {e}")

    def _apply_led_raw(self):
        """Apply raw LED mode value"""
        if not self.connected:
            messagebox.showwarning("Not Connected", "Please connect to the device first.")
            return

        raw_mode = self.led_raw_var.get()
        self._rgb_log(f"Applying raw mode: {raw_mode} (0x{raw_mode:02x})")

        try:
            self.device.set_led_mode(raw_mode)
            self._rgb_log(f"Raw mode {raw_mode} applied!")
        except Exception as e:
            self._rgb_log(f"Error: {e}")

    def _led_off(self):
        """Turn LED off"""
        if not self.connected:
            messagebox.showwarning("Not Connected", "Please connect to the device first.")
            return

        self._rgb_log("Turning LED off...")

        try:
            self.device.set_led_mode(0)
            self._rgb_log("LED turned off!")
        except Exception as e:
            self._rgb_log(f"Error: {e}")

    def _try_all_led_modes(self):
        """Try all LED modes"""
        if not self.connected:
            messagebox.showwarning("Not Connected", "Please connect to the device first.")
            return

        self._rgb_log("Trying all LED modes 0-20... Watch the keyboard!")

        try:
            self.device.try_all_led_modes()
            self._rgb_log("Finished trying all modes")
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
