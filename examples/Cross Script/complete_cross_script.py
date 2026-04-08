# v1.0.2
"""Complete cross-script demo — Python analysis phase.

Reads all measurements and variables left by complete_cross_script.scpi,
then performs comprehensive data analysis, statistical computation, and
matplotlib visualization.

Run the SCPI phase first:
    examples load complete_cross_script
    script run complete_cross_script

Then run this Python analysis:
    python examples/Cross\ Script/complete_cross_script.py

Works with --mock mode.

Demonstrates:
  - Reading SCPI variables via repl.ctx.script_vars
  - Reading measurements via repl.ctx.measurements.entries
  - Statistical analysis (mean, std dev, min, max, error, SNR)
  - Linear regression (manual computation)
  - Matplotlib plotting (line, scatter, bar, histogram, subplots)
  - Calling REPL commands from Python via repl.onecmd()
  - CSV export of analysis results
  - Writing results back to REPL variables
  - ColorPrinter formatted output
  - SCPI <-> Python interop patterns 11-20
  - Glob pattern demos via repl.onecmd for plot/liveplot
"""

# ============================================================================
# SECTION 1: SETUP & DATA RETRIEVAL
# ============================================================================

ColorPrinter.header("Complete Cross-Script Analysis (Python Phase)")
ColorPrinter.info("Reading data from SCPI phase...")

# Access REPL variables set by the SCPI script
script_vars = repl.ctx.script_vars
all_entries = repl.ctx.measurements.entries

if not all_entries:
    ColorPrinter.error("No measurements found! Run the SCPI phase first:")
    ColorPrinter.info("  examples load complete_cross_script")
    ColorPrinter.info("  script run complete_cross_script")
    raise SystemExit

# Read key variables from the SCPI run
target = float(script_vars.get("target", "5.0"))
tolerance = float(script_vars.get("tolerance", "0.05"))

ColorPrinter.info(f"Total measurements recorded: {len(all_entries)}")
ColorPrinter.info(f"Total REPL variables: {len(script_vars)}")
ColorPrinter.info(f"Target voltage: {target} V, Tolerance: +/- {tolerance} V")

# ============================================================================
# SECTION 2: DATA EXTRACTION & FILTERING
# ============================================================================

ColorPrinter.header("Data Extraction")


def extract_measurements(entries, prefix, unit_filter=None):
    """Extract measurement values matching a label prefix and optional unit."""
    results = []
    for entry in entries:
        if entry["label"].startswith(prefix):
            if unit_filter is None or entry.get("unit", "") == unit_filter:
                results.append({
                    "label": entry["label"],
                    "value": entry["value"],
                    "unit": entry.get("unit", ""),
                    "source": entry.get("source", ""),
                })
    return results


# Group measurements by instrument/category
psu_sweep = extract_measurements(all_entries, "psu_sweep_", "V")
loop_basic = extract_measurements(all_entries, "loop_basic_", "V")
tuple_data = extract_measurements(all_entries, "tuple_v_", "V")
while_data = extract_measurements(all_entries, "while_v_", "V")
repeat_data = extract_measurements(all_entries, "repeat_r", "V")
nested_data = extract_measurements(all_entries, "nested_", "V")
array_data = extract_measurements(all_entries, "array_v_", "V")
iv_voltages = extract_measurements(all_entries, "iv_v_", "V")
iv_currents = extract_measurements(all_entries, "iv_i_", "A")
freq_sweep = extract_measurements(all_entries, "fsweep_", "Hz")
cross_data = extract_measurements(all_entries, "cross_")
scope_data = extract_measurements(all_entries, "scope_")
dmm_data = [e for e in all_entries if e["label"].startswith("dmm_")]
smu_data = [e for e in all_entries if e["label"].startswith("smu_")]

categories = {
    "PSU Sweep": psu_sweep,
    "Basic Loop": loop_basic,
    "Tuple Loop": tuple_data,
    "While Loop": while_data,
    "Repeat Loop": repeat_data,
    "Nested Loop": nested_data,
    "Array Loop": array_data,
    "IV Voltage": iv_voltages,
    "IV Current": iv_currents,
    "Freq Sweep": freq_sweep,
    "Cross-Instrument": cross_data,
    "Scope": scope_data,
    "DMM": dmm_data,
    "SMU": smu_data,
}

for name, data in categories.items():
    ColorPrinter.info(f"  {name}: {len(data)} measurements")

# ============================================================================
# SECTION 3: STATISTICAL ANALYSIS
# ============================================================================

ColorPrinter.header("Statistical Analysis")


def compute_stats(values):
    """Compute basic statistics for a list of numeric values."""
    if not values:
        return None
    n = len(values)
    mean = sum(values) / n
    min_v = min(values)
    max_v = max(values)
    spread = max_v - min_v
    variance = sum((x - mean) ** 2 for x in values) / n
    std_dev = variance ** 0.5
    return {
        "n": n,
        "mean": mean,
        "min": min_v,
        "max": max_v,
        "spread": spread,
        "std_dev": std_dev,
        "variance": variance,
    }


# Analyze PSU sweep data
if psu_sweep:
    psu_values = [m["value"] for m in psu_sweep]
    psu_stats = compute_stats(psu_values)
    ColorPrinter.info("PSU Sweep Statistics:")
    ColorPrinter.info(f"  Samples:    {psu_stats['n']}")
    ColorPrinter.info(f"  Mean:       {psu_stats['mean']:.6f} V")
    ColorPrinter.info(f"  Min:        {psu_stats['min']:.6f} V")
    ColorPrinter.info(f"  Max:        {psu_stats['max']:.6f} V")
    ColorPrinter.info(f"  Spread:     {psu_stats['spread']:.6f} V")
    ColorPrinter.info(f"  Std Dev:    {psu_stats['std_dev']:.6f} V")

# Analyze all voltage measurements
all_voltage_entries = [e for e in all_entries if e.get("unit") == "V"]
if all_voltage_entries:
    all_v_values = [e["value"] for e in all_voltage_entries]
    v_stats = compute_stats(all_v_values)
    ColorPrinter.info(f"\nAll Voltage Measurements ({v_stats['n']} total):")
    ColorPrinter.info(f"  Mean:       {v_stats['mean']:.6f} V")
    ColorPrinter.info(f"  Range:      [{v_stats['min']:.6f}, {v_stats['max']:.6f}] V")
    ColorPrinter.info(f"  Std Dev:    {v_stats['std_dev']:.6f} V")

# Analyze repeat measurements (stability check)
if repeat_data:
    repeat_values = [m["value"] for m in repeat_data]
    r_stats = compute_stats(repeat_values)
    error = r_stats["mean"] - target
    error_pct = (error / target * 100) if target != 0 else 0
    ColorPrinter.info(f"\nRepeat Stability Analysis ({r_stats['n']} samples):")
    ColorPrinter.info(f"  Mean:       {r_stats['mean']:.6f} V")
    ColorPrinter.info(f"  Std Dev:    {r_stats['std_dev']:.6f} V  (lower = more stable)")
    ColorPrinter.info(f"  Error:      {error:+.6f} V ({error_pct:+.4f}%)")

    # Signal-to-noise ratio (SNR) calculation
    if r_stats["std_dev"] > 0:
        snr = r_stats["mean"] / r_stats["std_dev"]
        ColorPrinter.info(f"  SNR:        {snr:.2f}")
    else:
        ColorPrinter.info("  SNR:        inf (perfect stability)")

# ============================================================================
# SECTION 4: LINEAR REGRESSION (PSU Sweep)
# ============================================================================

ColorPrinter.header("Linear Regression")

if psu_sweep and len(psu_sweep) >= 2:
    # Extract setpoints from label names (psu_sweep_1.0, psu_sweep_2.0, etc.)
    setpoints = []
    measured = []
    for m in psu_sweep:
        label = m["label"]
        # Parse the voltage setpoint from the label: psu_sweep_X.X
        parts = label.replace("psu_sweep_", "")
        try:
            sp = float(parts)
            setpoints.append(sp)
            measured.append(m["value"])
        except ValueError:
            pass

    if len(setpoints) >= 2:
        # Manual linear regression: y = mx + b
        n = len(setpoints)
        sum_x = sum(setpoints)
        sum_y = sum(measured)
        sum_xy = sum(x * y for x, y in zip(setpoints, measured))
        sum_x2 = sum(x ** 2 for x in setpoints)

        denom = n * sum_x2 - sum_x ** 2
        if abs(denom) > 1e-12:
            slope = (n * sum_xy - sum_x * sum_y) / denom
            intercept = (sum_y - slope * sum_x) / n

            # R-squared (coefficient of determination)
            y_mean = sum_y / n
            ss_tot = sum((y - y_mean) ** 2 for y in measured)
            ss_res = sum((y - (slope * x + intercept)) ** 2
                         for x, y in zip(setpoints, measured))
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 1.0

            # Residuals
            residuals = [y - (slope * x + intercept)
                         for x, y in zip(setpoints, measured)]
            max_residual = max(abs(r) for r in residuals)

            ColorPrinter.info(f"PSU Sweep Linear Fit: y = {slope:.6f}x + {intercept:.6f}")
            ColorPrinter.info(f"  R-squared:      {r_squared:.8f}")
            ColorPrinter.info(f"  Slope:          {slope:.6f}  (ideal = 1.000000)")
            ColorPrinter.info(f"  Intercept:      {intercept:.6f} V  (ideal = 0.000000)")
            ColorPrinter.info(f"  Max residual:   {max_residual:.6f} V")

            # Store regression results in REPL
            repl.ctx.script_vars["regression_slope"] = str(round(slope, 6))
            repl.ctx.script_vars["regression_intercept"] = str(round(intercept, 6))
            repl.ctx.script_vars["regression_r2"] = str(round(r_squared, 8))
        else:
            ColorPrinter.warning("Cannot compute regression: degenerate data")
            setpoints = []
else:
    ColorPrinter.warning("Not enough PSU sweep data for regression")
    setpoints = []
    measured = []

# ============================================================================
# SECTION 5: MATPLOTLIB PLOTTING
# ============================================================================

ColorPrinter.header("Generating Plots")

try:
    import matplotlib
    matplotlib.use("Agg")  # Non-interactive backend for file output
    import matplotlib.pyplot as plt

    # Create a multi-panel dashboard figure
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle("Complete Cross-Script Analysis Dashboard", fontsize=16, fontweight="bold")

    # --- Plot 1: PSU Voltage Sweep (Line Plot) ---
    ax1 = axes[0, 0]
    if psu_sweep:
        labels = [m["label"].replace("psu_sweep_", "") for m in psu_sweep]
        values = [m["value"] for m in psu_sweep]
        try:
            x_vals = [float(l) for l in labels]
        except ValueError:
            x_vals = list(range(len(values)))
        ax1.plot(x_vals, values, "b-o", linewidth=2, markersize=6, label="Measured")
        ax1.plot(x_vals, x_vals, "r--", linewidth=1, alpha=0.7, label="Ideal (1:1)")
        ax1.set_xlabel("Setpoint (V)")
        ax1.set_ylabel("Measured (V)")
        ax1.set_title("PSU Voltage Sweep")
        ax1.legend()
        ax1.grid(True, alpha=0.3)
    else:
        ax1.text(0.5, 0.5, "No PSU sweep data", ha="center", va="center")
        ax1.set_title("PSU Voltage Sweep")

    # --- Plot 2: Target vs Actual Scatter with Error ---
    ax2 = axes[0, 1]
    if setpoints and measured:
        errors = [m - s for s, m in zip(setpoints, measured)]
        scatter = ax2.scatter(setpoints, measured, c=errors, cmap="RdYlGn_r",
                              s=80, edgecolors="black", linewidth=0.5, zorder=5)
        ax2.plot([min(setpoints), max(setpoints)],
                 [min(setpoints), max(setpoints)], "k--", alpha=0.5, label="Ideal")
        plt.colorbar(scatter, ax=ax2, label="Error (V)")
        ax2.set_xlabel("Setpoint (V)")
        ax2.set_ylabel("Measured (V)")
        ax2.set_title("Accuracy: Target vs Actual")
        ax2.legend()
        ax2.grid(True, alpha=0.3)
    else:
        ax2.text(0.5, 0.5, "No data", ha="center", va="center")
        ax2.set_title("Accuracy: Target vs Actual")

    # --- Plot 3: Measurement Count by Category (Bar Chart) ---
    ax3 = axes[0, 2]
    cat_names = [name for name, data in categories.items() if data]
    cat_counts = [len(data) for name, data in categories.items() if data]
    if cat_names:
        colors = plt.cm.tab20(range(len(cat_names)))
        bars = ax3.barh(cat_names, cat_counts, color=colors, edgecolor="black", linewidth=0.5)
        ax3.set_xlabel("Count")
        ax3.set_title("Measurements by Category")
        for bar, count in zip(bars, cat_counts):
            ax3.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                     str(count), va="center", fontsize=8)
    else:
        ax3.text(0.5, 0.5, "No data", ha="center", va="center")
        ax3.set_title("Measurements by Category")

    # --- Plot 4: Repeat Stability Histogram ---
    ax4 = axes[1, 0]
    if repeat_data and len(repeat_data) > 1:
        repeat_values = [m["value"] for m in repeat_data]
        ax4.hist(repeat_values, bins=max(5, len(repeat_values) // 2),
                 color="steelblue", edgecolor="black", alpha=0.8)
        r_mean = sum(repeat_values) / len(repeat_values)
        ax4.axvline(r_mean, color="red", linestyle="--", linewidth=2, label=f"Mean: {r_mean:.4f}")
        ax4.axvline(target, color="green", linestyle=":", linewidth=2, label=f"Target: {target}")
        ax4.set_xlabel("Voltage (V)")
        ax4.set_ylabel("Frequency")
        ax4.set_title("Repeat Measurement Distribution")
        ax4.legend(fontsize=8)
    else:
        ax4.text(0.5, 0.5, "Not enough repeat data", ha="center", va="center")
        ax4.set_title("Repeat Measurement Distribution")

    # --- Plot 5: IV Curve ---
    ax5 = axes[1, 1]
    if iv_voltages and iv_currents and len(iv_voltages) == len(iv_currents):
        iv_v = [m["value"] for m in iv_voltages]
        iv_i = [m["value"] for m in iv_currents]
        ax5.plot(iv_v, iv_i, "g-o", linewidth=2, markersize=6, color="darkgreen")
        ax5.set_xlabel("Voltage (V)")
        ax5.set_ylabel("Current (A)")
        ax5.set_title("SMU IV Curve")
        ax5.grid(True, alpha=0.3)
        ax5.fill_between(iv_v, iv_i, alpha=0.15, color="green")
    else:
        ax5.text(0.5, 0.5, "No IV data", ha="center", va="center")
        ax5.set_title("SMU IV Curve")

    # --- Plot 6: Frequency Sweep ---
    ax6 = axes[1, 2]
    if freq_sweep:
        # Extract target frequencies from labels
        target_freqs = []
        meas_freqs = []
        for m in freq_sweep:
            try:
                tf = float(m["label"].replace("fsweep_", ""))
                target_freqs.append(tf)
                meas_freqs.append(m["value"])
            except ValueError:
                pass
        if target_freqs:
            ax6.loglog(target_freqs, meas_freqs, "m-s", linewidth=2,
                       markersize=6, label="Measured")
            ax6.loglog(target_freqs, target_freqs, "k--", alpha=0.5, label="Ideal")
            ax6.set_xlabel("Target Frequency (Hz)")
            ax6.set_ylabel("Measured Frequency (Hz)")
            ax6.set_title("Frequency Sweep (log-log)")
            ax6.legend()
            ax6.grid(True, alpha=0.3, which="both")
    else:
        ax6.text(0.5, 0.5, "No freq sweep data", ha="center", va="center")
        ax6.set_title("Frequency Sweep")

    plt.tight_layout()

    # Save the dashboard
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".png", prefix="cross_script_dashboard_",
                                     delete=False) as tmp:
        dashboard_path = tmp.name
    fig.savefig(dashboard_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    # Emit marker for GUI to detect and display as tab
    print(f"__PLOT__:{dashboard_path}")
    ColorPrinter.success(f"Dashboard saved to: {dashboard_path}")

except ImportError:
    ColorPrinter.warning("matplotlib not installed — skipping plots.")
    ColorPrinter.info("Install with: pip install matplotlib")

# ============================================================================
# SECTION 6: CALLING REPL COMMANDS FROM PYTHON (basic)
# ============================================================================

ColorPrinter.header("REPL Integration from Python")

# Execute REPL commands directly from Python
ColorPrinter.info("Calling 'log print' via repl.onecmd():")
repl.onecmd("log print")

# Start a liveplot from Python using glob patterns
repl.onecmd('liveplot iv_v_* --title "IV Voltage (from Python)" --xlabel "Step" --ylabel "V"')

# You can even set REPL variables from Python
repl.ctx.script_vars["python_was_here"] = "true"
repl.ctx.script_vars["analysis_timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")

ColorPrinter.info(f"Set python_was_here = true")
ColorPrinter.info(f"Set analysis_timestamp = {repl.ctx.script_vars['analysis_timestamp']}")

# Record a derived measurement into the REPL measurement store
if psu_sweep:
    psu_values = [m["value"] for m in psu_sweep]
    psu_mean = sum(psu_values) / len(psu_values)
    repl.ctx.measurements.record("python_psu_mean", psu_mean, "V", "python_analysis")
    ColorPrinter.info(f"Recorded python_psu_mean = {psu_mean:.6f} V")

# ============================================================================
# SECTION 7: SCPI <-> PYTHON INTEROP (Patterns 11-20)
# ============================================================================
#
# This section demonstrates all 10 Python-context interop patterns.
# The Python script calls SCPI (inline via repl.onecmd, or via a file),
# passes variables both ways, and reads results back.
#
# Helper file: examples/Cross Script/_interop_helper.scpi
# ============================================================================

ColorPrinter.header("SCPI <-> Python Interop (Patterns 11-20)")

# Import the SCPI helper script so we can call it via "script run"
helper_dir = os.path.dirname(os.path.abspath(__file__))
helper_scpi_path = os.path.join(helper_dir, "_interop_helper.scpi")
repl.onecmd(f'script import interop_helper "{helper_scpi_path}"')

# ── PATTERN 11: calling SCPI inline (repl.onecmd) ───────────────────
ColorPrinter.info("")
ColorPrinter.info("--- PATTERN 11: calling SCPI inline ---")
repl.onecmd("psu1 chan 1 on")
repl.onecmd("psu1 set 1 5.0")
repl.onecmd("sleep 100ms")
p11_before = repl.ctx.script_vars.get("p11_v", "NOT_SET")
repl.onecmd("p11_v = psu1 meas v unit=V")
p11_after = repl.ctx.script_vars.get("p11_v", "NOT_SET")
repl.onecmd("psu1 chan 1 off")
ColorPrinter.info(f"PATTERN 11: measured PSU voltage inline: p11_v = {p11_after}")

# ── PATTERN 12: calling SCPI file in a loop ──────────────────────────
ColorPrinter.info("")
ColorPrinter.info("--- PATTERN 12: calling SCPI file in a loop ---")
# Set required variables for the helper before each call
repl.ctx.script_vars["py_to_scpi_file"] = "999"
repl.ctx.script_vars["py_modify_scpi_file"] = "200"
for loop_i in range(1, 4):
    repl.ctx.script_vars["helper_loop_counter"] = str(loop_i)
    ColorPrinter.info(f"  Calling interop_helper.scpi (iteration {loop_i})...")
    repl.onecmd("script run interop_helper")
ColorPrinter.info(f"PATTERN 12: called SCPI helper 3 times in a loop")
ColorPrinter.info(f"  py_modify_scpi_file now = {repl.ctx.script_vars.get('py_modify_scpi_file')}")

# ── PATTERN 13: calling SCPI inline in a loop ────────────────────────
ColorPrinter.info("")
ColorPrinter.info("--- PATTERN 13: calling SCPI inline in a loop ---")
repl.onecmd("psu1 chan 1 on")
for step_v in [1.0, 2.0, 3.0]:
    repl.onecmd(f"psu1 set 1 {step_v}")
    repl.onecmd("sleep 50ms")
    repl.onecmd(f"p13_v_{step_v} = psu1 meas v unit=V")
    val = repl.ctx.script_vars.get(f"p13_v_{step_v}", "?")
    ColorPrinter.info(f"  SCPI inline loop: set {step_v}V -> measured {val}V")
repl.onecmd("psu1 chan 1 off")
ColorPrinter.info("PATTERN 13: called SCPI inline 3 times in a Python loop")

# ── PATTERN 14: calling SCPI file (script run) ───────────────────────
ColorPrinter.info("")
ColorPrinter.info("--- PATTERN 14: calling SCPI file ---")
repl.ctx.script_vars["py_to_scpi_file"] = "999"
repl.ctx.script_vars["py_modify_scpi_file"] = "200"
repl.ctx.script_vars["helper_loop_counter"] = "0"
repl.onecmd("script run interop_helper")
ColorPrinter.info("PATTERN 14: called _interop_helper.scpi via script run")

# ── PATTERN 15: Python var → f-string in repl.onecmd ─────────────────
ColorPrinter.info("")
ColorPrinter.info("--- PATTERN 15: Python var used in SCPI inline ---")
py_voltage = 7.5
repl.onecmd("psu1 chan 1 on")
repl.onecmd(f"psu1 set 1 {py_voltage}")
repl.onecmd("sleep 100ms")
repl.onecmd("p15_v = psu1 meas v unit=V")
val = repl.ctx.script_vars.get("p15_v", "?")
repl.onecmd("psu1 chan 1 off")
ColorPrinter.info(f"PATTERN 15: Python var py_voltage={py_voltage} used in SCPI inline, measured={val}")

# ── PATTERN 16: Python var → script_vars → SCPI file reads {var} ─────
ColorPrinter.info("")
ColorPrinter.info("--- PATTERN 16: Python var used in SCPI file ---")
repl.ctx.script_vars["py_to_scpi_file"] = "999"
repl.ctx.script_vars["py_modify_scpi_file"] = "200"
repl.ctx.script_vars["helper_loop_counter"] = "0"
repl.onecmd("script run interop_helper")
# The helper script prints: read Python var py_to_scpi_file = 999
ColorPrinter.info("PATTERN 16: SCPI file read py_to_scpi_file=999 (see helper output above)")

# ── PATTERN 17: Python var modified by SCPI inline, Python reads back ─
ColorPrinter.info("")
ColorPrinter.info("--- PATTERN 17: Python var modified by SCPI inline ---")
repl.ctx.script_vars["py_counter"] = "50"
ColorPrinter.info(f"  Before SCPI: py_counter = {repl.ctx.script_vars['py_counter']}")
# Use simple assignment with expression (more robust than +=)
repl.onecmd("py_counter = 50 + 25")
after = repl.ctx.script_vars.get("py_counter", "?")
ColorPrinter.info(f"  After SCPI inline: py_counter = {after}")
ColorPrinter.info(f"PATTERN 17: Python stored 50, SCPI inline set to 50+25, Python read back {after}")

# ── PATTERN 18: Python var modified by SCPI file, Python reads back ───
ColorPrinter.info("")
ColorPrinter.info("--- PATTERN 18: Python var modified by SCPI file ---")
repl.ctx.script_vars["py_modify_scpi_file"] = "200"
repl.ctx.script_vars["py_to_scpi_file"] = "999"
repl.ctx.script_vars["helper_loop_counter"] = "0"
ColorPrinter.info(f"  Before script run: py_modify_scpi_file = {repl.ctx.script_vars['py_modify_scpi_file']}")
repl.onecmd("script run interop_helper")
after = repl.ctx.script_vars.get("py_modify_scpi_file", "?")
ColorPrinter.info(f"  After script run: py_modify_scpi_file = {after}")
ColorPrinter.info(f"PATTERN 18: Python stored 200, SCPI file incremented, Python read back {after}")

# ── PATTERN 19: SCPI inline creates value, Python reads it ───────────
ColorPrinter.info("")
ColorPrinter.info("--- PATTERN 19: value created in SCPI inline, read in Python ---")
repl.onecmd("scpi_inline_created = from_scpi_inline")
val = repl.ctx.script_vars.get("scpi_inline_created", "NOT_FOUND")
ColorPrinter.info(f"PATTERN 19: SCPI inline created scpi_inline_created = {val}")

# ── PATTERN 20: SCPI file creates value, Python reads it ─────────────
ColorPrinter.info("")
ColorPrinter.info("--- PATTERN 20: value created in SCPI file, read in Python ---")
repl.ctx.script_vars["py_to_scpi_file"] = "999"
repl.ctx.script_vars["py_modify_scpi_file"] = "200"
repl.ctx.script_vars["helper_loop_counter"] = "0"
repl.onecmd("script run interop_helper")
val = repl.ctx.script_vars.get("scpi_file_created", "NOT_FOUND")
ColorPrinter.info(f"PATTERN 20: SCPI file created scpi_file_created = {val}")

ColorPrinter.success("All 10 Python-context interop patterns (11-20) demonstrated!")

# ============================================================================
# SECTION 8: GLOB PATTERN DEMOS FROM PYTHON
# ============================================================================

ColorPrinter.header("Glob Pattern Demos from Python")

# Use repl.onecmd to issue plot/liveplot with glob patterns
# These demonstrate how Python can trigger glob-based plots

# Single glob pattern
repl.onecmd('plot psu_sweep_* --title "PSU Sweep (glob from Python)"')

# Multiple glob patterns on one chart
repl.onecmd('liveplot psu_v_reading psu_i_reading --title "PSU V & I (from Python)"')

# Glob for DMM readings from loop
repl.onecmd('plot dmm_reading_* --title "DMM Readings (glob from Python)"')

# Glob for frequency sweep
repl.onecmd('plot fsweep_* --title "Freq Sweep (glob from Python)"')

# Glob for IV curve data — two families on one chart
repl.onecmd('liveplot iv_v_* iv_i_* --title "IV Curve V+I (from Python)"')

ColorPrinter.info("Glob demos complete — plots issued for multiple measurement families")

# ============================================================================
# SECTION 9: CSV EXPORT
# ============================================================================

ColorPrinter.header("CSV Export")

csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "complete_analysis_results.csv")

try:
    with open(csv_path, "w", newline="") as f:
        # Header
        f.write("category,label,value,unit,source\n")

        # Write all measurements grouped by category
        for cat_name, cat_data in categories.items():
            for m in cat_data:
                label = m.get("label", m["label"]) if isinstance(m, dict) else m["label"]
                value = m.get("value", "")
                unit = m.get("unit", "")
                source = m.get("source", "")
                f.write(f"{cat_name},{label},{value},{unit},{source}\n")

        # Write summary statistics
        f.write("\n# Summary Statistics\n")
        f.write("stat,value\n")
        f.write(f"total_measurements,{len(all_entries)}\n")
        f.write(f"total_variables,{len(script_vars)}\n")
        f.write(f"target_voltage,{target}\n")

        if psu_sweep:
            psu_values = [m["value"] for m in psu_sweep]
            s = compute_stats(psu_values)
            f.write(f"psu_sweep_mean,{s['mean']:.6f}\n")
            f.write(f"psu_sweep_std,{s['std_dev']:.6f}\n")
            f.write(f"psu_sweep_min,{s['min']:.6f}\n")
            f.write(f"psu_sweep_max,{s['max']:.6f}\n")

    ColorPrinter.success(f"Analysis CSV saved to: {csv_path}")

except Exception as exc:
    ColorPrinter.error(f"Failed to save CSV: {exc}")

# ============================================================================
# SECTION 10: MEASUREMENT UNCERTAINTY ANALYSIS
# ============================================================================

ColorPrinter.header("Measurement Uncertainty Analysis")

# Analyze each voltage measurement category for uncertainty
uncertainty_results = {}
for cat_name, cat_data in categories.items():
    values = [m["value"] for m in cat_data if isinstance(m.get("value"), (int, float))]
    if len(values) >= 2:
        stats = compute_stats(values)
        # Type A uncertainty: standard deviation of the mean
        u_a = stats["std_dev"] / (stats["n"] ** 0.5)
        uncertainty_results[cat_name] = {
            "mean": stats["mean"],
            "std_dev": stats["std_dev"],
            "u_a": u_a,
            "n": stats["n"],
        }

if uncertainty_results:
    ColorPrinter.info(f"{'Category':<20} {'Mean':>10} {'Std Dev':>10} {'U(A)':>10} {'N':>5}")
    ColorPrinter.info("-" * 60)
    for cat, u in uncertainty_results.items():
        ColorPrinter.info(
            f"{cat:<20} {u['mean']:>10.4f} {u['std_dev']:>10.6f} "
            f"{u['u_a']:>10.6f} {u['n']:>5d}"
        )
else:
    ColorPrinter.info("Not enough data for uncertainty analysis.")

# ============================================================================
# SECTION 11: PASS/FAIL SUMMARY
# ============================================================================

ColorPrinter.header("Pass/Fail Summary")

pass_count = 0
fail_count = 0
results_detail = []

# Check PSU sweep accuracy
if psu_sweep and setpoints:
    for sp, meas_val in zip(setpoints, measured):
        error = abs(meas_val - sp)
        passed = error < 1.0  # 1V tolerance for mock data
        if passed:
            pass_count += 1
        else:
            fail_count += 1
        results_detail.append({
            "test": f"PSU {sp:.1f}V accuracy",
            "expected": sp,
            "actual": meas_val,
            "error": error,
            "passed": passed,
        })

# Check repeat measurement stability
if repeat_data:
    repeat_values = [m["value"] for m in repeat_data]
    r_stats = compute_stats(repeat_values)
    stable = r_stats["spread"] < 2.0  # 2V spread tolerance for mock data
    if stable:
        pass_count += 1
    else:
        fail_count += 1
    results_detail.append({
        "test": "Repeat stability",
        "expected": "spread < 2.0V",
        "actual": r_stats["spread"],
        "error": r_stats["spread"],
        "passed": stable,
    })

# Check frequency sweep accuracy
if freq_sweep:
    for m in freq_sweep:
        try:
            target_f = float(m["label"].replace("fsweep_", ""))
            error_f = abs(m["value"] - target_f)
            # Allow 50% error tolerance for mock data
            passed_f = error_f < target_f * 0.5
            if passed_f:
                pass_count += 1
            else:
                fail_count += 1
            results_detail.append({
                "test": f"Freq {target_f:.0f}Hz",
                "expected": target_f,
                "actual": m["value"],
                "error": error_f,
                "passed": passed_f,
            })
        except ValueError:
            pass

total_tests = pass_count + fail_count
ColorPrinter.info(f"Total tests: {total_tests}")
ColorPrinter.info(f"Passed:      {pass_count}")
ColorPrinter.info(f"Failed:      {fail_count}")

if total_tests > 0:
    pass_rate = pass_count / total_tests * 100
    ColorPrinter.info(f"Pass rate:   {pass_rate:.1f}%")

    if fail_count == 0:
        ColorPrinter.success(f"OVERALL VERDICT: PASS ({pass_count}/{total_tests})")
    else:
        ColorPrinter.error(f"OVERALL VERDICT: FAIL ({pass_count}/{total_tests} passed)")

    # Show failed tests
    failed = [r for r in results_detail if not r["passed"]]
    if failed:
        ColorPrinter.warning("\nFailed tests:")
        for f in failed:
            ColorPrinter.warning(f"  {f['test']}: expected={f['expected']}, "
                                 f"actual={f['actual']:.4f}, error={f['error']:.4f}")
else:
    ColorPrinter.warning("No tests were executed.")

# Store verdict in REPL
repl.ctx.script_vars["pass_count"] = str(pass_count)
repl.ctx.script_vars["fail_count"] = str(fail_count)
repl.ctx.script_vars["pass_rate"] = str(round(pass_rate, 1)) if total_tests > 0 else "N/A"
repl.ctx.script_vars["verdict"] = "PASS" if fail_count == 0 else "FAIL"

# ============================================================================
# SECTION 12: FINAL SUMMARY
# ============================================================================

ColorPrinter.header("Analysis Complete")

ColorPrinter.info(f"Measurements analyzed:  {len(all_entries)}")
ColorPrinter.info(f"Categories found:       {len([c for c in categories.values() if c])}")
ColorPrinter.info(f"Tests run:              {total_tests}")
ColorPrinter.info(f"Verdict:                {repl.ctx.script_vars['verdict']}")
ColorPrinter.info(f"Analysis timestamp:     {repl.ctx.script_vars['analysis_timestamp']}")

if setpoints and measured:
    ColorPrinter.info(f"Regression slope:       {repl.ctx.script_vars.get('regression_slope', 'N/A')}")
    ColorPrinter.info(f"Regression R-squared:   {repl.ctx.script_vars.get('regression_r2', 'N/A')}")

ColorPrinter.info("")
ColorPrinter.info("Variables stored back in REPL:")
for key in ["python_was_here", "analysis_timestamp", "verdict",
            "pass_count", "fail_count", "pass_rate",
            "regression_slope", "regression_intercept", "regression_r2"]:
    val = repl.ctx.script_vars.get(key)
    if val is not None:
        ColorPrinter.info(f"  {key} = {val}")

ColorPrinter.info("")
ColorPrinter.info("Interop patterns demonstrated:")
ColorPrinter.info("  Patterns 1-10:  SCPI-side (in complete_cross_script.scpi)")
ColorPrinter.info("  Patterns 11-20: Python-side (in this file)")

ColorPrinter.success("Complete cross-script analysis finished successfully.")
