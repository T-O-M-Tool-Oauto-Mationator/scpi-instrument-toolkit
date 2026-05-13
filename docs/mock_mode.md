# Mock Mode: Practice Without Hardware

Mock mode simulates the lab bench so you can practice and test scripts without any instrument plugged in. No NI-VISA driver, no USB cables, no hardware required.

Launch the REPL with the `--mock` flag:

```bash
scpi-repl --mock
```

You will see the usual `eset>` prompt. Everything works exactly as it does with real hardware: `scan`, `psu set`, `dmm meas`, `scope autoset`, `log save`, scripts, the debugger, etc.

## When to use mock mode

- Practicing commands before going to the lab
- Writing and testing scripts at home
- Learning the toolkit without hardware access
- Running the full bundled examples (`script run psu_dmm_test`, etc.)
- Demoing a workflow without booking bench time

## What gets simulated

The 14 simulated devices are:

| Name    | Type                | Simulates              |
|---------|---------------------|------------------------|
| psu1    | Power Supply        | HP E3631A              |
| psu2    | Power Supply        | Matrix MPS-6010H       |
| psu3    | Power Supply        | Keysight EDU36311A     |
| smu     | Source Measure Unit | NI PXIe-4139           |
| awg1    | Function Generator  | Keysight EDU33212A     |
| awg2    | Function Generator  | JDS6600                |
| awg3    | Function Generator  | BK Precision 4063      |
| dmm1    | Multimeter          | HP 34401A              |
| dmm2    | Multimeter          | OWON XDM1041           |
| dmm3    | Multimeter          | Keysight EDU34450A     |
| scope1  | Oscilloscope        | Rigol DHO804           |
| scope2  | Oscilloscope        | Tektronix MSO2024      |
| scope3  | Oscilloscope        | Keysight DSOX1204G     |
| ev2300  | USB-to-I2C Adapter  | TI EV2300              |

Mock instruments return realistic random values (not constants), so your measurements look like real data with small variations from call to call.

## Quick sanity check

After launching with `--mock`, run:

<!-- doc-test: skip reason="illustrative quick-start sequence; `scan` is not re-runnable in the doc-test harness" -->
```text
scan
psu chan 1 on
psu set 1 5.0
sleep 0.2
v = psu meas 1 v unit=V
log print
```

You should see a row in the measurement log with a voltage near 5.0 V.

## Limitations

- Mock mode does not catch real hardware quirks (settling time, autorange artifacts, GPIB timing). Scripts that pass in mock mode can still fail on the bench -- always run a dry run on real instruments before turning in lab data.
- Some advanced features (scope screenshots, segmented memory, EV2300 register reads) return stub data rather than full waveforms.

## Next steps

- Walk through bundled examples: see [Examples](examples.md)
- Learn the REPL syntax: see [REPL Reference](repl.md)
- Write your own scripts: see [Scripting](scripting.md)
