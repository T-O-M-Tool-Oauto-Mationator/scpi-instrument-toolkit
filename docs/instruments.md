# Supported Instruments

## Supported models

| Model | Type | Interface | Key Features |
|-------|------|-----------|--------------|
| Rigol DHO804 | Oscilloscope | USB | Screenshot, display, acquire, cursor, math, record, mask, label, invert, bwlimit, built-in AWG/counter/DVM |
| Tektronix MSO2024 | Oscilloscope | USB / GPIB | Basic scope commands |
| HP E3631A | Power Supply | GPIB | Triple-output, tracking |
| Matrix MPS-6010H-1C | Power Supply | Serial | Remote mode |
| HP 34401A | Multimeter | GPIB | Display text, NPLC control |
| OWON XDM1041 | Multimeter | USB / Serial | Basic DMM commands |
| BK Precision 4063 | Function Generator | USB | Basic AWG commands |
| Keysight EDU33212A | Function Generator | USB | Dual-channel |
| JDS6600 (Seesii DDS) | Function Generator | Serial | DDS waveform codes |
| NI PXIe-4139 | SMU | PXIe (nidcpower) | ±60 V / 1 A four-quadrant, voltage/current source and measure |

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

### Serial instruments (Matrix MPS, JDS6600)

Serial instruments are probed automatically at multiple baud rates. No manual configuration is needed. Connect via USB-to-serial adapter, then launch `scpi-repl`.

---

## Auto-detection

On startup (or when you type `scan`), the REPL:

1. Lists all VISA resources (USB, GPIB, Serial)
2. Queries `*IDN?` on each one
3. Matches the response against the known model list
4. Assigns a name (`psu1`, `dmm1`, `scope1`, `awg1`, etc.)

If multiple instruments of the same type are found, they are numbered: `psu1`, `psu2`, etc.

---

## Testing without hardware

Use `--mock` to run the REPL with simulated instruments:

```bash
scpi-repl --mock
```

Mock mode injects: `psu1`, `psu2`, `awg1`, `awg2`, `dmm1`, `dmm2`, `scope1`, `scope2` — two of each type. Measurements return realistic random values. Useful for testing scripts before connecting real hardware.
