"""
Bundled example scripts for the SCPI Instrument REPL.

Each entry in EXAMPLES has:
  "description" : one-line summary shown by `examples` command
  "lines"       : list of script lines (same format as .repl_scripts.json)

Load any example into your session with:  examples load <name>
Load all at once with:                    examples load all
Then run with:                            script run <name> [params]
"""

from typing import Dict, List

EXAMPLES: Dict[str, Dict] = {

    # ------------------------------------------------------------------
    "psu_dmm_test": {
        "description": "Set PSU to a voltage, measure with DMM, log result",
        "lines": [
            "# psu_dmm_test",
            "# Params: voltage (default 5.0), label (default 'vtest')",
            "#",
            "# Usage: script run psu_dmm_test voltage=5.0 label=vtest",
            "#        uses psu1 and dmm1 — rename with 'examples load' then edit if needed",
            "",
            "set voltage 5.0",
            "set label vtest",
            "",
            "print \"=== PSU/DMM Voltage Test ===\"",
            "print \"Target: ${voltage}V\"",
            "",
            "# Turn on PSU and set voltage",
            "psu1 chan 1 on",
            "psu1 set ${voltage}",
            "sleep 0.5",
            "",
            "# Read PSU output",
            "psu1 meas_store v psu_v unit=V",
            "",
            "# Read DMM",
            "dmm1 meas vdc",
            "dmm1 meas_store vdc ${label} unit=V",
            "",
            "print \"=== Test complete ===\"",
            "log print",
        ],
    },

    # ------------------------------------------------------------------
    "voltage_sweep": {
        "description": "Sweep PSU through a list of voltages, log DMM reading at each step",
        "lines": [
            "# voltage_sweep",
            "# Sweeps PSU through preset voltages and logs DMM measurements",
            "# Edit the 'for' line to change the voltage list",
            "",
            "print \"=== Voltage Sweep ===\"",
            "psu1 chan 1 on",
            "sleep 0.3",
            "",
            "for v 1.0 2.0 3.3 5.0 9.0 12.0",
            "  print \"Setting ${v}V...\"",
            "  psu1 set ${v}",
            "  sleep 0.5",
            "  dmm1 meas_store vdc v_${v} unit=V",
            "end",
            "",
            "psu1 chan 1 off",
            "print \"=== Sweep complete ===\"",
            "log print",
            "log save voltage_sweep.csv",
        ],
    },

    # ------------------------------------------------------------------
    "awg_scope_check": {
        "description": "Output sine wave on AWG ch1, measure frequency and PK2PK on scope",
        "lines": [
            "# awg_scope_check",
            "# Params: freq (default 1000), amp (default 2.0)",
            "#",
            "# Usage: script run awg_scope_check freq=1000 amp=2.0",
            "",
            "set freq 1000",
            "set amp 2.0",
            "",
            "print \"=== AWG + Scope Signal Check ===\"",
            "print \"Frequency: ${freq} Hz   Amplitude: ${amp} Vpp\"",
            "",
            "# Configure AWG",
            "awg1 chan 1 on",
            "awg1 wave 1 sine freq=${freq} amp=${amp} offset=0",
            "sleep 0.5",
            "",
            "# Autoset scope and measure",
            "scope1 autoset",
            "sleep 1.0",
            "",
            "scope1 meas_store 1 FREQUENCY meas_freq unit=Hz",
            "scope1 meas_store 1 PK2PK     meas_pk2pk unit=V",
            "scope1 meas_store 1 RMS       meas_rms unit=V",
            "",
            "print \"=== Results ===\"",
            "log print",
        ],
    },

    # ------------------------------------------------------------------
    "freq_sweep": {
        "description": "Sweep AWG through a list of frequencies, scope measures each",
        "lines": [
            "# freq_sweep",
            "# Sweeps AWG ch1 through frequencies, measures scope CH1 at each",
            "# Edit the 'for' line to change the frequency list",
            "",
            "print \"=== Frequency Sweep ===\"",
            "awg1 chan 1 on",
            "awg1 wave 1 sine amp=2.0 offset=0",
            "sleep 0.3",
            "",
            "for f 100 500 1000 5000 10000 50000 100000",
            "  print \"Testing ${f} Hz...\"",
            "  awg1 freq 1 ${f}",
            "  sleep 0.4",
            "  scope1 meas_store 1 FREQUENCY freq_${f} unit=Hz",
            "  scope1 meas_store 1 PK2PK     pk2pk_${f} unit=V",
            "end",
            "",
            "awg1 chan 1 off",
            "print \"=== Sweep complete ===\"",
            "log print",
            "log save freq_sweep.csv",
        ],
    },

    # ------------------------------------------------------------------
    "psu_ramp": {
        "description": "Ramp PSU voltage from start to end in N equal steps",
        "lines": [
            "# psu_ramp",
            "# Params: v_start, v_end, steps, delay",
            "#",
            "# Usage: script run psu_ramp v_start=0 v_end=12.0 steps=7 delay=0.5",
            "",
            "set v_start 0",
            "set v_end 12.0",
            "set steps 7",
            "set delay 0.5",
            "",
            "print \"=== PSU Voltage Ramp ===\"",
            "print \"${v_start}V → ${v_end}V in ${steps} steps\"",
            "",
            "psu1 chan 1 on",
            "",
            "# Build step list: pre-calculated values",
            "# (edit this for loop to match v_start, v_end, steps)",
            "for v ${v_start} 2.0 4.0 6.0 8.0 10.0 ${v_end}",
            "  print \"Ramping to ${v}V\"",
            "  psu1 set ${v}",
            "  sleep ${delay}",
            "  psu1 meas_store v ramp_${v} unit=V",
            "end",
            "",
            "print \"=== Ramp complete ===\"",
            "log print",
        ],
    },
}
