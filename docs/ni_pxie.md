# NI PXIe-4139 Setup

The NI PXIe-4139 is a ±60 V / 1 A four-quadrant Source Measure Unit (SMU). It uses the **NI-DCPower** driver — not VISA/SCPI — so it requires its own driver stack.

---

## Prerequisites

### 1 — NI-DAQmx runtime

Download and install from:
[NI-DAQmx Downloads](https://www.ni.com/en/support/downloads/drivers/download.ni-daqmx.html)

This installs the NI instrument driver runtime that the `nidcpower` Python package calls into.

!!! note "Windows only"
    The `nidcpower` package and NI-DAQmx runtime are only supported on Windows at this time. The REPL loads the NI PXIe-4139 driver conditionally — on Linux/macOS the instrument is silently skipped.

### 2 — nidcpower Python package

```bash
pip install nidcpower
```

### 3 — Verify the DLL is found

After installing NI-DAQmx, the required DLL (`nidcpower_64.dll` or `nidcpower.dll`) should be in one of:

- `C:\Program Files\IVI Foundation\IVI\Bin\`
- `C:\Program Files (x86)\IVI Foundation\IVI\Bin\`

If Python can't find the DLL, add the IVI Bin directory to your system PATH.

---

## Hardware setup

1. Seat the PXIe-4139 card in the PXIe chassis.
2. Connect the chassis to the host PC via MXI-Express or Thunderbolt.
3. Open **NI MAX** (Measurement & Automation Explorer) and verify the card appears under `My System > Devices and Interfaces`.
4. Note the **resource name** shown in NI MAX (e.g., `PXI1Slot2`). This name is needed for manual Python scripts (see the example below). The REPL typically auto-discovers the card without requiring manual resource specification; the resource name is only needed as a fallback if auto-detection fails or you need to force a specific device.

---

## REPL auto-detection

When `nidcpower` is installed and the card is present, the REPL assigns the SMU as `smu1` automatically on startup (or on `scan`).

```
eset> scan
[scpi] Found: smu1  (NI PXIe-4139)
```

If the card is not found, run `scan` after the chassis is powered and the MXI link is established.

---

## Minimal working example

```python
# Verify nidcpower works outside the REPL
import nidcpower

with nidcpower.Session("PXI1Slot2") as session:
    session.output_function = nidcpower.OutputFunction.DC_VOLTAGE
    session.voltage_level = 5.0
    session.current_limit = 0.01
    session.output_enabled = True
    session.initiate()
    v = session.measure(nidcpower.MeasurementTypes.VOLTAGE)
    i = session.measure(nidcpower.MeasurementTypes.CURRENT)
    print(f"V = {v:.6f} V   I = {i:.6f} A")
    session.output_enabled = False
```

---

## REPL usage

Once detected as `smu1`, use the standard SMU commands:

```bash
upper_limit smu voltage 6.0
upper_limit smu current 0.05

smu set 5.0 0.02
smu on
sleep 0.5
smu meas v
smu meas i
smu off
```

See [Source Measure Unit (SMU)](smu.md) for the full command reference.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `ImportError: No module named 'nidcpower'` | Package not installed | `pip install nidcpower` |
| `nidcpower` imports but `smu1` not found | Card not visible to driver | Check NI MAX; re-seat card; power-cycle chassis |
| `DLL load failed` | NI-DAQmx not installed or DLL not on PATH | Install NI-DAQmx runtime; add IVI Bin dir to PATH |
| `Resource not found` | Wrong resource name | Open NI MAX and confirm the resource name shown there |
