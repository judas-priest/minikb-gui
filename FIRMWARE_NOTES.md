# MiniKB Firmware Development Notes

## Device Info
- **USB ID:** 1189:8890
- **Chip:** CH552G (16-pin SOP)
- **Layout:** 6 keys + rotary encoder (with button)
- **LEDs:** RGB per key

## Known Issue
Firmware always sends L-Ctrl (0x01) modifier with every keypress.
Cannot be fixed via USB configuration - requires reflashing.

## Pinout (from Hackaday 6-key version)
```
Button 1: P1.5     Button 4: P3.0
Button 2: P3.4     Button 5: P1.6
Button 3: P1.1     Button 6: P1.7

Encoder A: P3.2    Encoder B: P1.4
Encoder Button: P3.3

LED: P3.4 (WS2812/NeoPixel)
```
**Note:** Pinout may differ - verify with multimeter!

## CH552G Pinout Reference
```
        +--------+
    P32 |1    16| P14
    P15 |2    15| P15/RST
    P16 |3    14| P34
    P17 |4    13| P33
    GND |5    12| P32
    VCC |6    11| P31
    P30 |7    10| P11
    P36 |8     9| P10
        +--------+
```

## Bootloader Mode
1. Short R12 on PCB and connect USB
2. OR hold all buttons + encoder while connecting
3. Check: `lsusb | grep 4348` -> should show `4348:55e0`

## Flash Tools
```bash
pip install ch55xtool
ch55xtool -f firmware.bin
```

## Firmware Sources

### RECOMMENDED: wagiminator CH552-MacroPad-plus ⭐
**Perfect match for 6-key + encoder version!**
- https://github.com/wagiminator/CH552-MacroPad-plus
- ✅ 6 keys + rotary encoder (with button)
- ✅ RGB LED support (WS2812)
- ✅ Ready-to-flash .bin file included
- ✅ Python flashing tool (chprog.py)
- 📦 Downloaded to: `firmware/macropad_plus.bin`

**Quick flash:**
```bash
cd firmware
python3 chprog.py macropad_plus.bin
```

**Enter bootloader:**
- Hold rotary encoder button while connecting USB
- OR short P1.5 to GND (first time only)
- All LEDs will glow white for ~10 seconds

### Other Ready-made (may need pin adaptation)
- https://hackaday.io/project/189914-rgb-macropad-custom-firmware (3-key)
- https://github.com/MrGeorgeK55/Macropad-8-keys (8-key, no encoder)
- https://github.com/eccherda/ch552g_mini_keyboard (3-key version)

### Configuration Tools (don't fix Ctrl bug)
- https://github.com/kriomant/ch57x-keyboard-tool
- https://github.com/devkev/hid-minikb-libusb

## Build Environment (Arduino)
1. Install Arduino IDE
2. Add board manager URL:
   ```
   https://raw.githubusercontent.com/DeqingSun/ch55xduino/ch55xduino/package_ch55xduino_mcs51_index.json
   ```
3. Select: CH55xDuino board
4. Bootloader: P3.6 (D+) Pull up
5. Clock: 16MHz (internal) 3.5V or 5V
6. Upload method: USB
7. USB Setting: USER CODE w/148B USB RAM

## Firmware Code Template
```c
// Pin definitions - VERIFY WITH YOUR BOARD!
#define PIN_BTN1  P15
#define PIN_BTN2  P34
#define PIN_BTN3  P11
#define PIN_BTN4  P30
#define PIN_BTN5  P16
#define PIN_BTN6  P17

#define PIN_ENC_A P32
#define PIN_ENC_B P14
#define PIN_ENC_BTN P33

#define PIN_LED   P34

// USB HID keyboard implementation
// See ch55xduino examples for USB HID
```

## Alternative: Software Filter
If reflashing is not possible, use `minikb_filter.py`:
```bash
sudo pip install evdev
sudo python3 minikb_filter.py
```
Intercepts keyboard events and removes Ctrl modifier.

## PCB Photo
Saved: /tmp/minikb_pcb.jpg

## TODO
- [ ] Verify pinout with multimeter
- [ ] Adapt firmware to correct pins
- [ ] Test bootloader mode
- [ ] Flash and test
