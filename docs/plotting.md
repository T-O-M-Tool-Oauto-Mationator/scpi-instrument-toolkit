# Plotting

The toolkit provides two plotting systems: **static plots** (matplotlib, rendered as PNG) and **live plots** (pyqtgraph, real-time in the GUI). Both work with measurement data collected via the assignment syntax (`label = instrument meas ...`).

---

## Static plots — `plot`

Render the measurement log (or a filtered subset) as a PNG image.

```text
plot                                    # plot all measurements
plot linereg_*                          # only labels matching a glob pattern
plot linereg_* loadreg_*                # multiple patterns
plot --title "Line Regulation"          # custom title
plot load_* --save ../plots/load.png    # save to a specific path
```

The chart opens as an image tab in the GUI. If the matched measurements have different units (e.g. V and A), they are split into separate subplots automatically.

### Options

| Flag | Description |
|------|-------------|
| `--title "text"` | Set the plot title. |
| `--save <path.png>` | Save the plot to a PNG file. Relative paths are resolved from the script directory. |

---

## Live plots — `liveplot`

Open a live-updating chart that refreshes as new measurements are recorded. This is the main way to visualize data during a sweep or ramp — you see each point appear in real time.

```text
liveplot dmm_*                                          # one series
liveplot psu_v_* psu_i_*                                # two series on ONE chart
liveplot dmm_* --title "Sweep" --xlabel "Time (s)" --ylabel "Voltage (V)"
```

### How it works

1. Run the `liveplot` command **before** collecting data (typically at the top of your script).
2. A new tab opens in the GUI immediately.
3. As measurements are recorded, matching points appear on the chart automatically.
4. The x-axis is time (seconds since the REPL session started).

### Multiple series vs. multiple plots

- **Multiple patterns, one command** = multiple series overlaid on one chart:
  ```text
  liveplot psu_v_* psu_i_*    # voltage and current on the same chart
  ```

- **Multiple `liveplot` commands** = separate tabs:
  ```text
  liveplot psu_v_* --title "Voltage"    # tab 1
  liveplot psu_i_* --title "Current"    # tab 2
  ```

### Options

| Flag | Description |
|------|-------------|
| `--title "text"` | Chart title (shown at the top). |
| `--xlabel "text"` | X-axis label. Defaults to "Time (s)". |
| `--ylabel "text"` | Y-axis label. Auto-detected from measurement units if not set. |

---

## Interacting with live plots

The live plot widget is fully interactive:

### Navigation

| Action | What it does |
|--------|-------------|
| **Scroll wheel** | Zoom in/out |
| **Click + drag** | Pan around |
| **Double-click** | Auto-fit view to all data |

### Crosshair and inspection

| Action | What it does |
|--------|-------------|
| **Hover** | Crosshair follows mouse, coordinate readout updates (bottom-right) |
| **Click near a point** | Tooltip shows: label, value, unit, time, and series name |

### Toolbar buttons

| Button | Description |
|--------|-------------|
| **Pause / Resume** | Freeze the chart to examine data without it scrolling |
| **Clear** | Wipe all displayed data. Only data recorded *after* the clear will appear |
| **Fit** | Reset zoom to fit all data |
| **Export** | Save the current view as a PNG image |
| **Select** | Enter rectangle selection mode (see below) |
| **Cross** | Toggle crosshair on/off |
| **Grid** | Toggle grid lines on/off |
| **Series buttons** | Click to show/hide individual series (only appears with multiple patterns) |
| **Refresh** | Spinner controlling how often the chart updates (1–30 times per second) |

---

## Rectangle selection and Detail View

You can select a region of the live plot and open it in a standalone window for closer analysis.

### Selecting data

1. Click the **Select** button in the toolbar.
2. Click the **first corner** of the region you want.
3. Move the mouse — a white dashed rectangle previews the selection.
4. Click the **second corner** — the rectangle locks in.
5. A blue **Open Selection** button appears. Click it.

A new **Detail Plot Window** opens with only the data points inside your rectangle.

### Detail Plot Window

The detail window is a standalone, editable plot for analysis and export:

| Feature | Description |
|---------|-------------|
| **Title / X / Y fields** | Type to change labels — the chart updates live |
| **Grid** | Toggle grid lines |
| **Cross** | Toggle crosshair |
| **Fit** | Auto-range to all data |
| **Export PNG** | Save as a 1920px-wide PNG image |
| **Save CSV** | Export the selected data as a CSV file with columns: `series, label, time, value` |
| **Click-to-inspect** | Same tooltip behavior as the live plot |
| **Zoom / Pan** | Same scroll and drag behavior |

---

## SCPI examples with live plots

These bundled examples demonstrate live plotting. All work with `--mock` for testing without hardware.

### live_voltage_sweep

Sweeps PSU through 51 voltage steps (0.5 V to 12 V via `linspace`) while a live plot tracks DMM readings.

```text
examples load live_voltage_sweep
script run live_voltage_sweep
```

### live_multi_plot

Opens **two** live-plot tabs (voltage and current) and ramps the PSU through 51 steps.

```text
examples load live_multi_plot
script run live_multi_plot
```

### live_combined_plot

Plots voltage **and** current as two series overlaid on a **single** chart. The key difference from `live_multi_plot`: one `liveplot` command with two patterns instead of two separate commands.

```text
examples load live_combined_plot
script run live_combined_plot
```

### live_freq_sweep

Sweeps AWG through 16 frequencies while a live plot tracks scope frequency measurements.

```text
examples load live_freq_sweep
script run live_freq_sweep
```

---

## Python API examples

Every example above also has a Python version. Import from the GUI menu under **Examples > Python Scripts**, or use the REPL:

```text
python examples/python/live_voltage_sweep.py
python examples/python/live_multi_plot.py
python examples/python/live_combined_plot.py
python examples/python/live_freq_sweep.py
```

In Python scripts, start a live plot with:

```python
repl.onecmd('liveplot dmm_* --title "My Plot" --xlabel "Time (s)" --ylabel "Voltage (V)"')
```

Record measurements with:

```python
measured = dmm.measure_dc_voltage()
repl.ctx.measurements.record("dmm_5.0V", measured, "V", "dmm1")
```

Use `linspace`-style loops for many data points:

```python
step = (V_END - V_START) / STEPS
voltages = [V_START + step * i for i in range(STEPS + 1)]

for target_v in voltages:
    psu.set_output_channel(ch, target_v, CURRENT_LIMIT)
    time.sleep(0.15)
    measured = dmm.measure_dc_voltage()
    repl.ctx.measurements.record(f"dmm_{target_v:.2f}V", measured, "V", "dmm1")
```

---

## Stopping a running script

When any script or command is running, a red **Running** banner appears at the bottom of the console with a **STOP** button.

Clicking STOP:

1. **Kills the running thread immediately** — does not wait for the current command to finish.
2. **Sets all instrument outputs to safe state** (E-STOP) — voltages go to 0, outputs disable.
3. Logs `[STOPPED] Execution killed. All outputs set to safe state.` to the console.

This is a kill switch. Use it when something goes wrong.

---

## Tips

- Run `liveplot` **before** the loop that collects data, so the tab is open and ready.
- Use `linspace` (SCPI) or a Python list comprehension for many evenly-spaced points — 50+ points makes the live update clearly visible.
- The **Clear** button only affects the display. The measurement store still has the data. Running a new script opens a new plot tab that starts fresh.
- Use **Select** + **Detail View** to isolate an interesting region, then **Save CSV** for further analysis in Excel or Python.
- Multiple live-plot tabs can be open simultaneously — each tracks its own patterns independently.
