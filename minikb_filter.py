#!/usr/bin/env python3
"""
MiniKB Filter - Removes hardcoded Ctrl modifier from mini keyboard
Runs as a daemon, intercepts events and re-emits them without Ctrl

Usage:
    sudo python3 minikb_filter.py

Requires: pip install evdev
"""

import sys
import asyncio

try:
    import evdev
    from evdev import ecodes, UInput, InputDevice
except ImportError:
    print("Error: evdev not installed. Run: pip install evdev")
    sys.exit(1)

# USB ID of the mini keyboard
VENDOR_ID = 0x1189
PRODUCT_ID = 0x8890

# Keys to filter out (Left Ctrl)
FILTERED_KEYS = {ecodes.KEY_LEFTCTRL}


def find_minikb_devices():
    """Find all input devices matching our keyboard"""
    devices = []
    for path in evdev.list_devices():
        dev = InputDevice(path)
        if dev.info.vendor == VENDOR_ID and dev.info.product == PRODUCT_ID:
            # Check if it has keyboard capabilities
            caps = dev.capabilities()
            if ecodes.EV_KEY in caps:
                devices.append(dev)
    return devices


async def filter_device(device, uinput):
    """Filter events from one device"""
    print(f"Filtering: {device.path} - {device.name}")

    # Grab the device so original events don't pass through
    device.grab()

    try:
        async for event in device.async_read_loop():
            if event.type == ecodes.EV_KEY:
                if event.code in FILTERED_KEYS:
                    # Skip Ctrl key events
                    continue
                # Pass through other key events
                uinput.write_event(event)
                uinput.syn()
            elif event.type == ecodes.EV_SYN:
                # Sync events
                pass
            else:
                # Pass through other events (REL for encoder, etc)
                uinput.write_event(event)
                uinput.syn()
    except OSError:
        print(f"Device disconnected: {device.path}")
    finally:
        try:
            device.ungrab()
        except:
            pass


def create_virtual_keyboard():
    """Create virtual keyboard device for filtered output"""
    # Define capabilities - standard keyboard + relative events for encoder
    cap = {
        ecodes.EV_KEY: list(range(1, 256)),  # All standard keys
        ecodes.EV_REL: [ecodes.REL_WHEEL, ecodes.REL_HWHEEL],  # Scroll
    }

    ui = UInput(cap, name="MiniKB Filtered", vendor=0x1234, product=0x5678)
    print(f"Created virtual device: {ui.device.path}")
    return ui


async def main():
    print("MiniKB Filter - Removes Ctrl modifier from keyboard events")
    print(f"Looking for device {VENDOR_ID:04x}:{PRODUCT_ID:04x}...")

    devices = find_minikb_devices()

    if not devices:
        print("No MiniKB devices found!")
        print("\nMake sure:")
        print("  1. Keyboard is connected")
        print("  2. Running as root (sudo)")
        sys.exit(1)

    print(f"Found {len(devices)} input device(s)")

    # Create virtual keyboard for output
    uinput = create_virtual_keyboard()

    print("\nFiltering started. Press Ctrl+C to stop.")
    print("Filtered keys: Left Ctrl")

    # Create tasks for all devices
    tasks = [filter_device(dev, uinput) for dev in devices]

    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        uinput.close()
        for dev in devices:
            try:
                dev.ungrab()
            except:
                pass


if __name__ == "__main__":
    if sys.platform != "linux":
        print("This script only works on Linux")
        sys.exit(1)

    asyncio.run(main())
