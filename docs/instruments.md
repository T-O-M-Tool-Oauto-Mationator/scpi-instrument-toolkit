# Supported Instruments

## Supported models

!!! tip "Auto-generated version"
    An auto-generated instruments table (built from source code, always up-to-date) is available at [Instruments & Capabilities](generated/instruments.md).

| Model | Type | Interface | Key Features |
|-------|------|-----------|--------------|
| Rigol DHO804 | Oscilloscope | USB | Screenshot, display, acquire, cursor, math, record, mask, label, invert, bwlimit, built-in AWG/counter/DVM |
| Tektronix MSO2024 | Oscilloscope | USB / GPIB | Basic scope commands |
| HP E3631A | Power Supply | GPIB | Triple-output, tracking |
| Keysight EDU36311A | Power Supply | USB / LAN | Triple-output (6V/5A, 30V/1A, 30V/1A), tracking, OVP/OCP |
| Matrix MPS-6010H-1C | Power Supply | Serial | Remote mode |
| HP 34401A | Multimeter | GPIB | Display text, NPLC control |
| Keysight EDU34450A | Multimeter | USB / LAN | 5½-digit, capacitance, temperature, dual display |
| OWON XDM1041 | Multimeter | USB / Serial | Basic DMM commands |
| BK Precision 4063 | Function Generator | USB | Basic AWG commands |
| Keysight EDU33212A | Function Generator | USB | Dual-channel |
| JDS6600 (Seesii DDS) | Function Generator | Serial | DDS waveform codes |
| NI PXIe-4139 | SMU | PXIe (nidcpower) | ±60 V / 3 A four-quadrant (20 W source, 12 W sink), voltage/current source and measure |
| Keysight DSOX1204G | Oscilloscope | USB / LAN | Screenshot, display, acquire, math, mask, label, invert, bwlimit, built-in AWG (WGEN), DVM |
| TI EV2300A | USB-to-I2C Adapter | USB HID | SMBus/I2C read/write word/byte/block, register scan, raw probe |

---

## Connection setup

### USB and GPIB instruments

1. Install [NI-VISA](https://www.ni.com/en/support/downloads/drivers/download.ni-visa.html)
2. Connect the instrument
3. Launch `scpi-repl` — it will auto-detect the instrument

### NI PXIe instruments (NI PXIe-4139 SMU)

The NI PXIe-4139 uses the NI-DCPower driver, **not** VISA/SCPI. It is auto-detected by the REPL when the `nidcpower` Python package and NI-DCPower runtime are installed:

```bash
pip install nidcpower
```

The instrument appears as `smu1` in the REPL. See [Source Measure Unit (SMU)](smu.md) for commands.

**Prerequisites and limitations:**

- Requires a PXIe chassis with a compatible controller slot connected to the host PC via MXI-Express or Thunderbolt.
- NI-DCPower runtime and `nidcpower` Python package must be installed (Windows only; Linux support is limited).
- The REPL auto-detects the first available device as `smu1`. Multiple cards are not currently supported.
- Not compatible with VISA/SCPI — VISA-based commands (`*IDN?`, etc.) do not apply.
- Remote PXI controllers are not supported.

### TI EV2300A (USB-to-I2C)

The EV2300A is detected automatically via USB HID — no VISA or extra TI drivers needed. It appears as `ev2300` in the REPL. See [USB-to-I2C Adapter (EV2300)](ev2300.md) for commands.

**Prerequisites:**

- EV2300A must have firmware loaded (not in bootloader mode). If the REPL reports "bootloader mode", flash firmware via TI bqStudio.
- On Linux, a udev rule is needed for `/dev/hidraw` access. On macOS, install `hidapi`.

### Serial instruments (Matrix MPS, JDS6600)

Serial instruments are probed automatically at multiple baud rates. No manual configuration is needed. Connect via USB-to-serial adapter, then launch `scpi-repl`.

---

## Auto-detection

On startup (or when you type `scan`), the REPL:

1. Lists all VISA resources (USB, GPIB, Serial)
2. Queries `*IDN?` on each one
3. Scans PXI slots for NI-DCPower devices
4. Scans USB HID for EV2300 adapters
5. Matches responses against the known model list
6. Assigns a name (`psu1`, `dmm1`, `scope1`, `awg1`, `smu1`, `ev2300`, etc.)

If multiple instruments of the same type are found, they are numbered: `psu1`, `psu2`, etc.

---

## Testing without hardware

Use `--mock` to run the REPL with simulated instruments:

```bash
scpi-repl --mock
```

Mock mode injects: `psu1`, `psu2`, `psu3`, `awg1`, `awg2`, `dmm1`, `dmm2`, `dmm3`, `smu`, `scope1`, `scope2`, `scope3`. Measurements return realistic random values. Useful for testing scripts before connecting real hardware.
