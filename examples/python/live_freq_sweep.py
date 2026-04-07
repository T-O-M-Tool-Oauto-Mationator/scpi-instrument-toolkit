"""Live frequency sweep -- Python API version.

Sweeps AWG through frequencies while a live plot tracks scope measurements.
Works with --mock.
"""
import time

# --- Configuration ---
FREQUENCIES = [100, 200, 500, 750, 1000, 2000, 3000, 5000, 7500,
               10000, 15000, 20000, 30000, 50000, 75000, 100000]
AMPLITUDE = 2.0
CHANNEL = 1

# --- Get instruments ---
awg = devices.get("awg") or devices.get("awg1")
scope = devices.get("scope") or devices.get("scope1")

if not awg:
    ColorPrinter.error("No AWG found. Run 'scan' first.")
    raise SystemExit
if not scope:
    ColorPrinter.error("No scope found. Run 'scan' first.")
    raise SystemExit

# --- Start live plot ---
repl.onecmd('liveplot freq_* --title "Frequency Response" --xlabel "Time (s)" --ylabel "Frequency (Hz)"')

# --- Configure AWG ---
ColorPrinter.header("Live Frequency Sweep")
awg.set_waveform(CHANNEL, "SIN", amplitude=AMPLITUDE, offset=0)
awg.enable_output(CHANNEL, True)
time.sleep(0.3)

# --- Sweep ---
for freq in FREQUENCIES:
    awg.set_frequency(CHANNEL, freq)
    time.sleep(0.25)
    measured = scope.measure_bnf(CHANNEL, "FREQUENCY")
    repl.ctx.measurements.record(f"freq_{freq}", measured, "Hz", "scope1")
    ColorPrinter.info(f"  {freq:>8,} Hz  ->  Scope: {measured:.3f} Hz")

awg.enable_output(CHANNEL, False)
ColorPrinter.success("Sweep complete")
