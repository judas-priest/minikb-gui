#!/usr/bin/env python3
"""
MiniKB GUI - Configuration tool for 6-key + encoder mini keyboard
USB ID: 1189:8890 (Acer Communications & Multimedia)
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import struct

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

# Button identifiers for the device
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


class MiniKBDevice:
    """USB communication with the mini keyboard"""

    def __init__(self):
        self.device = None
        self.was_kernel_driver_active = False

    def connect(self):
        """Find and connect to the device"""
        if not USB_AVAILABLE:
            raise RuntimeError("pyusb not installed")

        self.device = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
        if self.device is None:
            raise RuntimeError(f"Device {VENDOR_ID:04x}:{PRODUCT_ID:04x} not found")

        # Detach kernel driver if needed
        try:
            if self.device.is_kernel_driver_active(0):
                self.device.detach_kernel_driver(0)
                self.was_kernel_driver_active = True
        except (usb.core.USBError, NotImplementedError):
            pass

        # Set configuration
        try:
            self.device.set_configuration()
        except usb.core.USBError:
            pass

        # Send init packet
        self._send_packet(bytes([0x03] + [0x00] * 64))
        return True

    def disconnect(self):
        """Disconnect from the device"""
        if self.device and self.was_kernel_driver_active:
            try:
                usb.util.dispose_resources(self.device)
                self.device.attach_kernel_driver(0)
            except (usb.core.USBError, NotImplementedError):
                pass
        self.device = None

    def _send_packet(self, data):
        """Send a 65-byte packet to the device"""
        if len(data) < 65:
            data = data + bytes(65 - len(data))
        self.device.write(ENDPOINT_OUT, data, timeout=1000)

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


class MiniKBApp:
    """Main GUI Application"""

    CONFIG_FILE = os.path.expanduser("~/.minikb_config.json")

    def __init__(self, root):
        self.root = root
        self.root.title("MiniKB Configurator - 6 Keys + Encoder")
        self.root.geometry("600x500")
        self.root.resizable(True, True)

        self.device = MiniKBDevice()
        self.connected = False
        self.config = {}
        self.key_combos = {}

        self._create_ui()
        self._load_config()

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
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=5)
        main_frame.rowconfigure(1, weight=1)
        main_frame.columnconfigure(0, weight=1)

        # Keys tab
        keys_frame = ttk.Frame(notebook, padding="10")
        notebook.add(keys_frame, text="Keys Configuration")
        self._create_keys_tab(keys_frame)

        # Encoder tab
        encoder_frame = ttk.Frame(notebook, padding="10")
        notebook.add(encoder_frame, text="Encoder Configuration")
        self._create_encoder_tab(encoder_frame)

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
            ('Knob Left', 'Rotate Left'),
            ('Knob Right', 'Rotate Right'),
            ('Knob Press', 'Press/Click'),
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

    def _reset_config(self):
        """Reset all settings to default (F13-F21)"""
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
        if app.connected:
            app._disconnect()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
