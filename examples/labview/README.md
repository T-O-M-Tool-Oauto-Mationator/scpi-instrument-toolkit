# LabVIEW Examples

Reference VIs verified end-to-end on the ESET-453 lab bench.

## ev2300_hybrid.vi

Coordinated PSU + EV2300 chain that powers the BQ76920 EVM, prompts the
human to press the BOOT button, then reads the SYS_STAT register over I2C.
Flat Sequence Structure forces PSU-on → BOOT prompt → I2C read ordering.

**Bench setup:**

- HP E3631A PSU, +25V channel wired to BQ EVM BATT+/-
- TI EV2300 USB-to-I2C adapter on the host PC
- BQ76920 EVM with BOOT button accessible

**VI structure:**

| Frame | Purpose | Nodes |
|-------|---------|-------|
| 1 | Power up the BQ | `open_psu(GPIB0::4::INSTR, HP_E3631A)` -> `psu_set_output_channel(id, 2, 18.0, 0.5)` -> `psu_enable_output(id, True)` |
| 2 | Pause for BOOT press | One Button Dialog: "Press Boot on BQ EVM" |
| 3 | Read SYS_STAT | `open_ev2300("")` -> `ev2300_read_byte(id, 0x08, 0x00)` -> Indicator |

**Why `psu_set_output_channel` instead of `psu_set_voltage`:**
`psu_set_voltage` only programs the voltage setpoint; if the channel's
current limit was previously zeroed (an old bridge bug, fixed in v1.0.63
but worth the safety habit), the PSU enables into CC mode at 0 A and
delivers no power. `psu_set_output_channel(id, ch, V, A)` sends `APPLY`
which sets both setpoints atomically — same call the REPL's `psu set`
makes.

**Expected output:** front panel "return value" indicator displays the
SYS_STAT byte. A healthy idle BQ76920 typically reads `0x80` (CC_READY
flag set, no faults) — `128` in decimal.

**Module path constant:** point Python Nodes at the repo's top-level shim:

```text
<repo>/labview_bridge.py
```

For the editable-install setup that lets LabVIEW pick up bridge edits
without re-copying files, see `CLAUDE.md` -> "LabVIEW bridge install
layout".

**Screenshots:**

- Block diagram: [`docs/assets/labview-ev2300-hybrid-block-diagram.png`](../../docs/assets/labview-ev2300-hybrid-block-diagram.png)
- Front panel: [`docs/assets/labview-ev2300-hybrid-front-panel.png`](../../docs/assets/labview-ev2300-hybrid-front-panel.png)
