#!/usr/bin/env python3
"""
CyberPower CP1500PFCLCDa USB HID status reader for macOS.
Vendor: 0x0764 (Cyber Power Systems), Product: 0x0601
Uses HID Power Device class (Usage Pages 0x84 = UPS, 0x85 = Battery System)
NUT driver: usbhid-ups with cps subdriver (cps-hid.c); 0x0601 has no battery
voltage scaling (unlike 0x0501 which applies cps_battery_scale).
"""

import sys
import time
import hid
import usb.core
import usb.util

VENDOR_ID  = 0x0764
PRODUCT_ID = 0x0601

# HID Power Device usage page IDs
USAGE_PAGE_POWER_DEVICE  = 0x84
USAGE_PAGE_BATTERY_SYSTEM = 0x85

# Feature report IDs known for CPS 0x0601 devices
# These correspond to HID report IDs used by the UPS firmware.
REPORT_IDS = list(range(1, 32))  # probe 1..31


def print_usb_device_info():
    """Print low-level USB device descriptor info via PyUSB."""
    print("=" * 60)
    print("USB DEVICE DESCRIPTOR (PyUSB)")
    print("=" * 60)
    dev = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
    if dev is None:
        print("  [!] Device not found via PyUSB")
        return

    print(f"  Bus / Address     : {dev.bus} / {dev.address}")
    print(f"  Vendor  ID        : 0x{dev.idVendor:04x}")
    print(f"  Product ID        : 0x{dev.idProduct:04x}")
    print(f"  USB Version       : {dev.bcdUSB >> 8}.{(dev.bcdUSB >> 4) & 0xF}{dev.bcdUSB & 0xF}")
    print(f"  Device Class      : 0x{dev.bDeviceClass:02x}")
    print(f"  Device Subclass   : 0x{dev.bDeviceSubClass:02x}")
    print(f"  Device Protocol   : 0x{dev.bDeviceProtocol:02x}")
    print(f"  Max Packet Size 0 : {dev.bMaxPacketSize0}")
    print(f"  Num Configurations: {dev.bNumConfigurations}")
    try:
        print(f"  Manufacturer      : {usb.util.get_string(dev, dev.iManufacturer)}")
        print(f"  Product           : {usb.util.get_string(dev, dev.iProduct)}")
        print(f"  Serial Number     : {usb.util.get_string(dev, dev.iSerialNumber)}")
    except Exception as e:
        print(f"  [string descriptors unavailable: {e}]")

    print()
    for cfg in dev:
        print(f"  Configuration {cfg.bConfigurationValue}:")
        print(f"    bNumInterfaces    : {cfg.bNumInterfaces}")
        print(f"    bmAttributes      : 0x{cfg.bmAttributes:02x}")
        print(f"    bMaxPower         : {cfg.bMaxPower * 2} mA")
        for intf in cfg:
            print(f"    Interface {intf.bInterfaceNumber} Alt {intf.bAlternateSetting}:")
            print(f"      bInterfaceClass   : 0x{intf.bInterfaceClass:02x}  "
                  f"({'HID' if intf.bInterfaceClass == 3 else 'other'})")
            print(f"      bInterfaceSubClass: 0x{intf.bInterfaceSubClass:02x}")
            print(f"      bInterfaceProtocol: 0x{intf.bInterfaceProtocol:02x}")
            for ep in intf:
                direction = "IN" if ep.bEndpointAddress & 0x80 else "OUT"
                ep_type = {0: "Control", 1: "Isochronous",
                           2: "Bulk", 3: "Interrupt"}.get(ep.bmAttributes & 0x3, "?")
                print(f"      Endpoint 0x{ep.bEndpointAddress:02x}: {direction} {ep_type} "
                      f"MaxPacket={ep.wMaxPacketSize} Interval={ep.bInterval}ms")
    print()


def print_hid_device_info(h):
    """Print HID-level device info."""
    print("=" * 60)
    print("HID DEVICE INFO (hidapi)")
    print("=" * 60)
    print(f"  Manufacturer      : {h.manufacturer}")
    print(f"  Product           : {h.product}")
    print(f"  Serial Number     : {h.serial}")
    print()


def enumerate_hid_devices():
    """List all HID devices matching vendor/product."""
    print("=" * 60)
    print("HID DEVICE ENUMERATION")
    print("=" * 60)
    devices = hid.enumerate(VENDOR_ID, PRODUCT_ID)
    if not devices:
        print("  [!] No matching HID devices found")
        return
    for d in devices:
        print(f"  Path              : {d['path']}")
        print(f"  Vendor  ID        : 0x{d['vendor_id']:04x}")
        print(f"  Product ID        : 0x{d['product_id']:04x}")
        print(f"  Serial            : {d['serial_number']}")
        print(f"  Manufacturer      : {d['manufacturer_string']}")
        print(f"  Product           : {d['product_string']}")
        print(f"  Usage Page        : 0x{d['usage_page']:04x}  "
              f"({'UPS' if d['usage_page'] == USAGE_PAGE_POWER_DEVICE else 'Battery' if d['usage_page'] == USAGE_PAGE_BATTERY_SYSTEM else 'other'})")
        print(f"  Usage             : 0x{d['usage']:04x}")
        print(f"  Interface Number  : {d['interface_number']}")
        print(f"  Release Number    : 0x{d['release_number']:04x}")
        print()


def probe_feature_reports(h):
    """
    Probe all feature report IDs and print raw bytes + decoded values.
    CPS 0x0601 uses HID Power Device class; feature reports carry UPS data.
    """
    print("=" * 60)
    print("HID FEATURE REPORTS (raw probe, report IDs 0x01–0x1F)")
    print("=" * 60)
    print(f"  {'Report ID':<12} {'Hex bytes':<52} Notes")
    print(f"  {'-'*9:<12} {'-'*50:<52} -----")

    for rid in REPORT_IDS:
        try:
            # get_feature_report: first byte is the report ID
            buf = h.get_feature_report(rid, 64)
            if buf and len(buf) > 1 and any(b != 0 for b in buf[1:]):
                hex_str = " ".join(f"{b:02x}" for b in buf)
                # Attempt simple integer decode (little-endian) of payload
                payload = bytes(buf[1:])
                try:
                    val_u16 = int.from_bytes(payload[:2], "little")
                    val_u32 = int.from_bytes(payload[:4], "little")
                    note = f"u16={val_u16} u32={val_u32}"
                except Exception:
                    note = ""
                print(f"  0x{rid:02x}         {hex_str:<52} {note}")
        except Exception:
            pass  # report ID not supported by device
    print()


# Known HID Power Device usage mappings for CPS UPS (from NUT cps-hid.c + HID spec).
# Scaling notes (NUT cps-hid.c / USB HID Power Device spec / descriptor analysis):
#   - battery.voltage (0x0a): POW_VOLTAGE, 16-bit LE * 0.1 V (UExp=+6 is firmware quirk).
#   - report 0x07: 6 packed 8-bit capacity % fields (NOT voltage); see KNOWN_FIELDS_07.
#   - Voltages (0x0f, 0x12): UExp=+7 firmware bug; raw value is already in whole volts.
#   - battery.runtime (0x05, 0x06): raw = minutes (not seconds).
#   - ups.load: derived from POW_ACTIVE_POWER (0x19) / POW_CONFIG_ACTIVE_POWER (0x18) * 100.
#     Device has no PercentLoad (0x00840035) report.
#   - input.voltage.nominal (0x0c): index lookup (1=100V, 2=110V, 3=120V).
#   - battery.voltage.nominal (0x1a): index lookup (1=12V, 2=24V).
#   - output.frequency (0x14): index (LogMax=6); 6=60Hz.
#   - input.frequency (0x0e): POW_CONFIG_VOLTAGE byte, raw * 0.5 = Hz.
# Format: (label, report_id, byte_offset, byte_len, scale, unit)
KNOWN_FIELDS = [
    # label,                        rid,  off, ln, scale, unit
    ("battery.charge (%)",           0x08,  1,  1,  1.0,  "%"),   # BAT_REMAINING_CAPACITY
    ("battery.charge.low (%)",       0x07,  5,  1,  1.0,  "%"),   # BAT_REMAINING_CAPACITY_LIMIT
    ("battery.charge.warning (%)",   0x07,  4,  1,  1.0,  "%"),   # BAT_WARNING_CAPACITY_LIMIT
    ("battery.runtime (s)",          0x08,  2,  2,  1.0,  "s"),   # BAT_RUN_TIME_TO_EMPTY (unit=seconds)
    ("battery.runtime.low (s)",      0x08,  4,  2,  1.0,  "s"),   # BAT_REMAINING_TIME_LIMIT
    ("battery.voltage (V)",          0x0a,  1,  2,  0.1,  "V"),   # POW_VOLTAGE, 16-bit LE * 0.1
    ("battery.voltage.nominal (V)",  0x1a,  1,  1,  1.0,  "V"),   # lookup below
    ("input.voltage (V)",            0x0f,  1,  2,  1.0,  "V"),
    ("input.voltage.nominal (V)",    0x0c,  1,  1,  1.0,  "V"),   # lookup below
    ("input.frequency.nominal (Hz)", 0x0d,  1,  1,  1.0,  "Hz"),  # lookup below
    ("input.frequency (Hz)",         0x0e,  1,  1,  0.5,  "Hz"),  # raw * 0.5 = Hz
    ("input.transfer.low (V)",       0x10,  1,  2,  1.0,  "V"),
    # ("input.transfer.high (V)",    0x11, ...) — always errors on macOS (IOHIDDeviceGetReport 0xE0005000)
    ("output.voltage (V)",           0x12,  1,  2,  1.0,  "V"),
    ("output.voltage.nominal (V)",   0x13,  1,  1,  1.0,  "V"),   # lookup below
    ("output.frequency (Hz)",        0x14,  1,  1,  1.0,  "Hz"),  # lookup below (index)
    ("ups.realpower (W)",             0x19,  1,  2,  1.0,  "W"),   # POW_ACTIVE_POWER, actual
    ("ups.apparent_power (VA)",       0x1d,  1,  2,  1.0,  "VA"),  # POW_APPARENT_POWER, actual
    ("ups.realpower.nominal (W)",     0x18,  1,  2,  1.0,  "W"),   # POW_CONFIG_ACTIVE_POWER
    ("ups.load (%) [derived]",        0x19,  1,  2,  1.0,  "%"),   # derived: realpower/nominal*100
    ("ups.beeper.status",            0x1b,  1,  1,  1.0,  ""),
    ("ups.status (present)",         0x0b,  1,  1,  1.0,  ""),
    ("ups.delay.shutdown (s)",       0x16,  1,  2,  1.0,  "s"),   # 0xFFFF = not set
]

BEEPER_MAP = {1: "disabled", 2: "enabled", 3: "muted", 4: "enabled+muted", 5: "enabled"}
# Report 0x0b PresentStatus: 6 x 1-bit fields (verified from descriptor path analysis)
# bit 0: 0x008500d0 AC_PRESENT       → mains power OK
# bit 1: 0x00850044 Charging         → battery charging
# bit 2: 0x00850045 Discharging      → on battery
# bit 3: 0x00850042 BelowRemainingCapacityLimit → low battery
# bit 4: 0x00850046 FullyCharged     → battery full
# bit 5: 0x00850043 RemainingTimeLimitExpired → runtime expired
STATUS_BITS = {
    0: "AC_Present",
    1: "Charging",
    2: "Discharging",
    3: "BelowRemainingCapacityLimit (LowBatt)",
    4: "FullyCharged",
    5: "RemainingTimeLimitExpired",
}
# Index lookups (USB HID Power Device spec + NUT hid-subdrivers.txt)
VOLTAGE_NOMINAL_MAP = {1: "100 V", 2: "110 V", 3: "120 V", 4: "200 V",
                       5: "208 V", 6: "220 V", 7: "230 V", 8: "240 V"}
BATT_VOLTAGE_NOMINAL = {1: "12 V", 2: "24 V", 3: "36 V", 4: "48 V",
                        5: "72 V", 6: "96 V", 7: "108 V", 8: "120 V", 9: "144 V"}
# output.frequency: CPS firmware uses index (LogMax=6); 6=60Hz
FREQ_INDEX_MAP = {1: "50 Hz", 2: "60 Hz", 3: "60 Hz", 4: "50 Hz", 5: "50 Hz", 6: "60 Hz"}
# input.frequency.nominal config index (0x0d): CPS TW firmware: 3=60Hz
FREQ_NOM_INDEX_MAP = {1: "50 Hz", 2: "60 Hz", 3: "60 Hz", 4: "50 Hz"}


def decode_known_fields(h):
    """Read and decode known HID feature report fields for the CPS UPS."""
    print("=" * 60)
    print("DECODED UPS STATUS & CONFIGURATION")
    print("=" * 60)

    for label, rid, off, ln, scale, unit in KNOWN_FIELDS:
        try:
            buf = h.get_feature_report(rid, 64)
            if not buf or len(buf) < off + ln:
                print(f"  {label:<35} = [short report]")
                continue

            raw = int.from_bytes(bytes(buf[off:off+ln]), "little")
            val = raw * scale
            raw_hex = " ".join(f"{b:02x}" for b in buf[:off+ln])

            if label.startswith("ups.beeper"):
                display = BEEPER_MAP.get(raw, f"raw={raw}")
            elif label.startswith("ups.status"):
                bits = [STATUS_BITS[i] for i in range(6) if raw & (1 << i)]
                display = f"0x{raw:02x}  [{', '.join(bits) if bits else 'none'}]"
            elif label.startswith("ups.load"):
                # Derived: realpower / nominal * 100
                try:
                    nom_buf = h.get_feature_report(0x18, 64)
                    nominal_w = int.from_bytes(bytes(nom_buf[1:3]), "little")
                    display = f"{raw / nominal_w * 100:.1f} %" if nominal_w else f"{raw} W (nominal unknown)"
                except Exception:
                    display = f"{raw} W"
            elif label.startswith("ups.delay"):
                display = "not set" if raw == 0xFFFF else f"{raw} s"
            elif "voltage.nominal" in label and "battery" not in label:
                val_str = VOLTAGE_NOMINAL_MAP.get(raw, f"idx={raw}")
                # CPS TW firmware quirk: output.voltage.nominal reports idx=7 (230V)
                # even on 110V models; treat as informational only.
                display = val_str
            elif label.startswith("battery.voltage.nominal"):
                display = BATT_VOLTAGE_NOMINAL.get(raw, f"idx={raw}")
            elif "frequency.nominal" in label:
                display = FREQ_NOM_INDEX_MAP.get(raw, f"idx={raw}")
            elif "frequency" in label:
                if scale != 1.0:
                    display = f"{val:.1f} {unit}"
                else:
                    display = FREQ_INDEX_MAP.get(raw, f"idx={raw}")
            elif scale != 1.0:
                display = f"{val:.1f} {unit}"
            else:
                display = f"{int(val)} {unit}".strip()

            print(f"  {label:<35} = {display:<22}  (report 0x{rid:02x}, raw={raw}, bytes=[{raw_hex}])")
        except Exception as e:
            print(f"  {label:<35} = [error: {e}]")
    print()


def main():
    print()
    print("CyberPower CP1500PFCLCDA USB HID Status Reader")
    print(f"Target: VID=0x{VENDOR_ID:04x}  PID=0x{PRODUCT_ID:04x}")
    print()

    # # 1. USB descriptor info (PyUSB)
    # try:
    #     print_usb_device_info()
    # except Exception as e:
    #     print(f"[PyUSB error: {e}]\n")

    # 2. HID enumeration
    enumerate_hid_devices()

    # 3. Open HID device and read data
    while True:
        try:
            h = hid.Device(VENDOR_ID, PRODUCT_ID)
            break
        except Exception:
            print("Waiting for device...", end="\r")
            time.sleep(2)

    try:
        print_hid_device_info(h)
        probe_feature_reports(h)
        decode_known_fields(h)
    finally:
        h.close()


if __name__ == "__main__":
    main()
