#!/usr/bin/env python3
"""
YAML Configuration Parser for MiniKB
Compatible with ch57x-keyboard-tool format
"""

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    print("Warning: pyyaml not installed. Run: pip install pyyaml")


# Key name to HID keycode mapping (compatible with ch57x-keyboard-tool)
KEY_MAP = {
    # Letters
    'a': 0x04, 'b': 0x05, 'c': 0x06, 'd': 0x07, 'e': 0x08,
    'f': 0x09, 'g': 0x0a, 'h': 0x0b, 'i': 0x0c, 'j': 0x0d,
    'k': 0x0e, 'l': 0x0f, 'm': 0x10, 'n': 0x11, 'o': 0x12,
    'p': 0x13, 'q': 0x14, 'r': 0x15, 's': 0x16, 't': 0x17,
    'u': 0x18, 'v': 0x19, 'w': 0x1a, 'x': 0x1b, 'y': 0x1c, 'z': 0x1d,

    # Numbers
    '1': 0x1e, '2': 0x1f, '3': 0x20, '4': 0x21, '5': 0x22,
    '6': 0x23, '7': 0x24, '8': 0x25, '9': 0x26, '0': 0x27,

    # Function keys
    'f1': 0x3a, 'f2': 0x3b, 'f3': 0x3c, 'f4': 0x3d, 'f5': 0x3e, 'f6': 0x3f,
    'f7': 0x40, 'f8': 0x41, 'f9': 0x42, 'f10': 0x43, 'f11': 0x44, 'f12': 0x45,
    'f13': 0x68, 'f14': 0x69, 'f15': 0x6a, 'f16': 0x6b,
    'f17': 0x6c, 'f18': 0x6d, 'f19': 0x6e, 'f20': 0x6f,
    'f21': 0x70, 'f22': 0x71, 'f23': 0x72, 'f24': 0x73,

    # Special keys
    'enter': 0x28, 'escape': 0x29, 'backspace': 0x2a, 'tab': 0x2b,
    'space': 0x2c, 'minus': 0x2d, 'equal': 0x2e,
    'leftbracket': 0x2f, 'rightbracket': 0x30, 'backslash': 0x31,
    'semicolon': 0x33, 'quote': 0x34, 'grave': 0x35,
    'comma': 0x36, 'dot': 0x37, 'slash': 0x38,
    'capslock': 0x39,

    # Navigation
    'insert': 0x49, 'home': 0x4a, 'pageup': 0x4b,
    'delete': 0x4c, 'end': 0x4d, 'pagedown': 0x4e,
    'right': 0x4f, 'left': 0x50, 'down': 0x51, 'up': 0x52,

    # Media keys
    'mute': 0xef, 'volumeup': 0xed, 'volumedown': 0xee,
    'next': 0xeb, 'previous': 0xea, 'prev': 0xea,
    'play': 0xe8, 'stop': 0xe9,
}

# Modifier name to bitmask
MODIFIER_MAP = {
    'ctrl': 0x01,
    'shift': 0x02,
    'alt': 0x04,
    'opt': 0x04,  # Mac option = alt
    'win': 0x08,
    'cmd': 0x08,  # Mac command = win
    'rctrl': 0x10,
    'rshift': 0x20,
    'ralt': 0x40,
    'ropt': 0x40,
    'rwin': 0x80,
    'rcmd': 0x80,
}


def parse_key_action(action_str):
    """Parse key action string like 'ctrl-shift-c' into (keycode, modifier)

    Args:
        action_str: String like 'a', 'ctrl-c', 'ctrl-shift-delete', etc.

    Returns:
        tuple: (keycode, modifier) or None if invalid
    """
    if not action_str or not isinstance(action_str, str):
        return None

    parts = action_str.lower().split('-')

    # Last part is the key
    key = parts[-1]
    modifiers = parts[:-1]

    # Get keycode
    keycode = KEY_MAP.get(key)
    if keycode is None:
        print(f"Warning: Unknown key '{key}' in action '{action_str}'")
        return None

    # Calculate modifier bitmask
    modifier = 0x00
    for mod in modifiers:
        mod_bit = MODIFIER_MAP.get(mod)
        if mod_bit is None:
            print(f"Warning: Unknown modifier '{mod}' in action '{action_str}'")
            return None
        modifier |= mod_bit

    return (keycode, modifier)


def parse_yaml_config(yaml_path):
    """Load and parse YAML config file in ch57x-keyboard-tool format

    Args:
        yaml_path: Path to mapping.yaml file

    Returns:
        dict: Parsed config with button mappings
        Format: {
            'orientation': 'normal',
            'rows': 2,
            'columns': 3,
            'knobs': 1,
            'buttons': [(keycode, modifier), ...],  # 6 buttons
            'knob_ccw': (keycode, modifier),
            'knob_press': (keycode, modifier),
            'knob_cw': (keycode, modifier),
        }
    """
    if not YAML_AVAILABLE:
        raise RuntimeError("pyyaml not installed. Run: pip install pyyaml")

    with open(yaml_path, 'r') as f:
        config = yaml.safe_load(f)

    if not config or 'layers' not in config:
        raise ValueError("Invalid YAML config: missing 'layers'")

    # Use first layer (layer 0)
    layer = config['layers'][0]

    # Parse buttons (2D array -> flat list)
    button_grid = layer.get('buttons', [])
    buttons = []
    for row in button_grid:
        for action in row:
            parsed = parse_key_action(action)
            buttons.append(parsed if parsed else (0x00, 0x00))

    # Parse knob
    knob_config = layer.get('knobs', [{}])[0] if layer.get('knobs') else {}
    knob_ccw = parse_key_action(knob_config.get('ccw', ''))
    knob_press = parse_key_action(knob_config.get('press', ''))
    knob_cw = parse_key_action(knob_config.get('cw', ''))

    return {
        'orientation': config.get('orientation', 'normal'),
        'rows': config.get('rows', 2),
        'columns': config.get('columns', 3),
        'knobs': config.get('knobs', 1),
        'buttons': buttons,
        'knob_ccw': knob_ccw if knob_ccw else (0x00, 0x00),
        'knob_press': knob_press if knob_press else (0x00, 0x00),
        'knob_cw': knob_cw if knob_cw else (0x00, 0x00),
    }


def apply_yaml_to_device(device, yaml_path):
    """Load YAML config and apply to device

    Args:
        device: MiniKBDevice instance
        yaml_path: Path to mapping.yaml

    Returns:
        bool: True if successful
    """
    config = parse_yaml_config(yaml_path)

    # Button IDs: 1-6 for buttons, 0x0d, 0x0e, 0x0f for knob
    button_ids = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06]

    # Apply button mappings
    for i, (keycode, modifier) in enumerate(config['buttons']):
        if i < len(button_ids):
            device.set_key(button_ids[i], keycode, modifier, layer=0)

    # Apply knob mappings
    knob_ccw_keycode, knob_ccw_mod = config['knob_ccw']
    knob_press_keycode, knob_press_mod = config['knob_press']
    knob_cw_keycode, knob_cw_mod = config['knob_cw']

    device.set_key(0x0d, knob_ccw_keycode, knob_ccw_mod, layer=0)      # Knob CCW
    device.set_key(0x0e, knob_press_keycode, knob_press_mod, layer=0)  # Knob Press
    device.set_key(0x0f, knob_cw_keycode, knob_cw_mod, layer=0)        # Knob CW

    print(f"Applied YAML config: {len(config['buttons'])} buttons + knob")
    return True


if __name__ == "__main__":
    # Test parsing
    import sys
    if len(sys.argv) > 1:
        config = parse_yaml_config(sys.argv[1])
        print(f"Parsed config:")
        print(f"  Orientation: {config['orientation']}")
        print(f"  Grid: {config['rows']}x{config['columns']}")
        print(f"  Buttons: {config['buttons']}")
        print(f"  Knob CCW: {config['knob_ccw']}")
        print(f"  Knob Press: {config['knob_press']}")
        print(f"  Knob CW: {config['knob_cw']}")
