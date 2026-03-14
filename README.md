# Cyberpower UPS Status via USB

A python script to output the current status of a **Cyberpower CP1500PFCLCDa UPS** connected via **USB**.

## Prepare

```
# Install BREW if not present
if ! command which brew ; then 
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Install hidapi libraries on MacOS
if uname -s | grep -i darwin ; then
  brew install hidapi
fi

# create a python VENV
python3 -m venv python

# Install python libraries
./python/bin/pip install -r requirements.txt
```

## Run
```
source ./python/bin/activate
python ups_info.py
```

## Result (example script output)

```
CyberPower CP1500PFCLCDA USB HID Status Reader
Target: VID=0x0764  PID=0x0601

============================================================
HID DEVICE ENUMERATION
============================================================
  Path              : b'DevSrvsID:4294973505'
  Vendor  ID        : 0x0764
  Product ID        : 0x0601
  Serial            : XXXXX0000000
  Manufacturer      : CPS
  Product           : CP1500PFCLCDa TW
  Usage Page        : 0x0084  (UPS)
  Usage             : 0x0004
  Interface Number  : 0
  Release Number    : 0x0200

  Path              : b'DevSrvsID:4294973505'
  Vendor  ID        : 0x0764
  Product ID        : 0x0601
  Serial            : XXXXX0000000
  Manufacturer      : CPS
  Product           : CP1500PFCLCDa TW
  Usage Page        : 0x0084  (UPS)
  Usage             : 0x0024
  Interface Number  : 0
  Release Number    : 0x0200

  Path              : b'DevSrvsID:4294973505'
  Vendor  ID        : 0x0764
  Product ID        : 0x0601
  Serial            : XXXXX0000000
  Manufacturer      : CPS
  Product           : CP1500PFCLCDa TW
  Usage Page        : 0x0084  (UPS)
  Usage             : 0x001a
  Interface Number  : 0
  Release Number    : 0x0200

  Path              : b'DevSrvsID:4294973505'
  Vendor  ID        : 0x0764
  Product ID        : 0x0601
  Serial            : XXXXX0000000
  Manufacturer      : CPS
  Product           : CP1500PFCLCDa TW
  Usage Page        : 0x0084  (UPS)
  Usage             : 0x001c
  Interface Number  : 0
  Release Number    : 0x0200

  Path              : b'DevSrvsID:4294973505'
  Vendor  ID        : 0x0764
  Product ID        : 0x0601
  Serial            : XXXXX0000000
  Manufacturer      : CPS
  Product           : CP1500PFCLCDa TW
  Usage Page        : 0xff01  (other)
  Usage             : 0x001d
  Interface Number  : 0
  Release Number    : 0x0200

============================================================
HID DEVICE INFO (hidapi)
============================================================
  Manufacturer      : CPS
  Product           : CP1500PFCLCDa TW
  Serial Number     : XXXXX0000000

============================================================
HID FEATURE REPORTS (raw probe, report IDs 0x01–0x1F)
============================================================
  Report ID    Hex bytes                                            Notes
  ---------    --------------------------------------------------   -----
  0x01         01 01                                                u16=1 u32=1
  0x02         02 02                                                u16=2 u32=2
  0x03         03 04                                                u16=4 u32=4
  0x04         04 03                                                u16=3 u32=3
  0x05         05 01                                                u16=1 u32=1
  0x06         06 02                                                u16=2 u32=2
  0x07         07 64 05 0a 14 0a 64                                 u16=1380 u32=336201060
  0x08         08 64 1e 14 2c 01                                    u16=7780 u32=739516004
  0x09         09 f0 00                                             u16=240 u32=240
  0x0a         0a 13 01                                             u16=275 u32=275
  0x0b         0b 11                                                u16=17 u32=17
  0x0c         0c 02                                                u16=2 u32=2
  0x0d         0d 03                                                u16=3 u32=3
  0x0e         0e 78                                                u16=120 u32=120
  0x0f         0f 75 00                                             u16=117 u32=117
  0x10         10 5e 00 8c 00                                       u16=94 u32=9175134
  0x12         12 75 00                                             u16=117 u32=117
  0x13         13 07                                                u16=7 u32=7
  0x14         14 06                                                u16=6 u32=6
  0x15         15 ff ff                                             u16=65535 u32=65535
  0x16         16 ff ff                                             u16=65535 u32=65535
  0x18         18 e8 03 dc 05                                       u16=1000 u32=98305000
  0x19         19 4c 00                                             u16=76 u32=76
  0x1a         1a 01                                                u16=1 u32=1
  0x1b         1b 05                                                u16=5 u32=5
  0x1d         1d 54 00                                             u16=84 u32=84

============================================================
DECODED UPS STATUS & CONFIGURATION
============================================================
  battery.charge (%)                  = 100 %                   (report 0x08, raw=100, bytes=[08 64])
  battery.charge.low (%)              = 10 %                    (report 0x07, raw=10, bytes=[07 64 05 0a 14 0a])
  battery.charge.warning (%)          = 20 %                    (report 0x07, raw=20, bytes=[07 64 05 0a 14])
  battery.runtime (s)                 = 5150 s                  (report 0x08, raw=5150, bytes=[08 64 1e 14])
  battery.runtime.low (s)             = 300 s                   (report 0x08, raw=300, bytes=[08 64 1e 14 2c 01])
  battery.voltage (V)                 = 27.4 V                  (report 0x0a, raw=274, bytes=[0a 12 01])
  battery.voltage.nominal (V)         = 12 V                    (report 0x1a, raw=1, bytes=[1a 01])
  input.voltage (V)                   = 117 V                   (report 0x0f, raw=117, bytes=[0f 75 00])
  input.voltage.nominal (V)           = 110 V                   (report 0x0c, raw=2, bytes=[0c 02])
  input.frequency.nominal (Hz)        = 60 Hz                   (report 0x0d, raw=3, bytes=[0d 03])
  input.frequency (Hz)                = 60.0 Hz                 (report 0x0e, raw=120, bytes=[0e 78])
  input.transfer.low (V)              = 94 V                    (report 0x10, raw=94, bytes=[10 5e 00])
  output.voltage (V)                  = 117 V                   (report 0x12, raw=117, bytes=[12 75 00])
  output.voltage.nominal (V)          = 230 V                   (report 0x13, raw=7, bytes=[13 07])
  output.frequency (Hz)               = 60 Hz                   (report 0x14, raw=6, bytes=[14 06])
  ups.realpower (W)                   = 76 W                    (report 0x19, raw=76, bytes=[19 4c 00])
  ups.apparent_power (VA)             = 84 VA                   (report 0x1d, raw=84, bytes=[1d 54 00])
  ups.realpower.nominal (W)           = 1000 W                  (report 0x18, raw=1000, bytes=[18 e8 03])
  ups.load (%) [derived]              = 7.6 %                   (report 0x19, raw=76, bytes=[19 4c 00])
  ups.beeper.status                   = enabled                 (report 0x1b, raw=5, bytes=[1b 05])
  ups.status (present)                = 0x11  [AC_Present, FullyCharged]  (report 0x0b, raw=17, bytes=[0b 11])
  ups.delay.shutdown (s)              = not set                 (report 0x16, raw=65535, bytes=[16 ff ff])

```

## Acknowledgements

* The [Network UPS Tools (NUT) Project](https://github.com/networkupstools/nut/) as a reference, without which debugging this script would have taken so much longer.



