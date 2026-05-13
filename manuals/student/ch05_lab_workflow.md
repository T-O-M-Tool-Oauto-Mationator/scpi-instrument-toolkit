# Chapter 5: Lab Report Workflow

This chapter walks through the complete workflow from connecting instruments to producing figures for your lab report.

## The Workflow

1. Connect instruments and launch the REPL
2. Configure measurement modes
3. Take measurements and log them
4. Export data to CSV
5. Load CSV in Python with pandas
6. Plot with matplotlib
7. Include figures in your DOCX report

## Step 1: Connect and Launch

Plug in your instruments via USB. Open a terminal and run:

    scpi-repl

The REPL scans and finds your instruments automatically. Run `list` to confirm.

## Step 2: Configure Instruments

Set up each instrument for your test:

    use psu1
    psu chan 1 on
    psu set 1 5.0 0.5

    dmm1 config vdc

## Step 3: Take Measurements

Use the assignment syntax to record every reading with a label and unit:

    v_set = psu1 meas v unit=V
    i_set = psu1 meas i unit=A
    v_dmm = dmm1 meas unit=V

For a sweep, use a for loop:

    for v 1.0 2.0 3.3 5.0
      psu set 1 {v}
      sleep 0.5
      v_{v} = dmm1 meas unit=V
    end

## Step 4: Calculate Derived Values

Use calc to compute quantities from your measurements:

<!-- doc-test: skip reason="depends on v_dmm and i_set recorded by preceding measurement steps" -->

    calc power = v_dmm * i_set unit=W
    calc error = v_dmm - 5.0 unit=V
    calc error_pct = (v_dmm - 5.0) / 5.0 * 100 unit=%

## Step 5: Review and Export

View all measurements:

    log print

Export to CSV:

    log save lab3_data.csv

The CSV file contains columns: Label, Value, Unit, Source. You can open it in Excel or Python.

## Step 6: Plot in Python

Create a Python script (e.g., `plot_lab3.py`) to generate figures:

    import pandas as pd
    import matplotlib.pyplot as plt

    # Load the CSV
    df = pd.read_csv("lab3_data.csv")

    # Filter voltage sweep data
    sweep = df[df["Label"].str.startswith("v_")]
    voltages = [float(label.split("_")[1]) for label in sweep["Label"]]
    measured = sweep["Value"].values

    # Plot
    plt.figure(figsize=(8, 5))
    plt.plot(voltages, measured, "bo-", label="Measured")
    plt.plot(voltages, voltages, "r--", label="Ideal")
    plt.xlabel("Set Voltage (V)")
    plt.ylabel("Measured Voltage (V)")
    plt.title("PSU Voltage Accuracy")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("voltage_accuracy.png", dpi=150)
    plt.show()

Run the script:

    python plot_lab3.py

This generates `voltage_accuracy.png` -- a publication-ready figure for your report.

## Step 7: Include in Your Report

Insert the PNG figure into your DOCX lab report. Add a caption referencing the test conditions:

<!-- doc-test: skip reason="prose caption example, not REPL input" -->

    "Figure 1: PSU voltage accuracy measured with HP 34401A DMM.
     Set voltage vs. measured voltage across 1.0-5.0 V range."

## Complete Example Script

Here is a full REPL script you can save and reuse:

    # lab3_voltage_test.scpi
    log clear
    psu1 chan 1 on
    dmm1 config vdc

    for v 1.0 2.0 3.3 5.0
      psu1 set 1 {v}
      sleep 0.5
      v_{v} = dmm1 meas unit=V
    end

    psu1 chan 1 off
    log print
    log save lab3_data.csv
    print "Data saved to lab3_data.csv"

## Tips for Good Lab Data

- Always wait for the PSU output to settle before measuring. Use `sleep 0.5` (500ms) minimum.
- Record both the PSU's own measurement and the DMM's measurement. The difference tells you about measurement accuracy.
- Use descriptive labels: `v_3v3_rail` is better than `v1`.
- Run `log clear` at the start of each test to avoid mixing data from different runs.
- Save CSV files with descriptive names including the date: `lab3_voltage_sweep_20260416.csv`.

## Try It

1. Run the complete example script above in mock mode
2. Export to CSV with `log save`
3. Write a Python script to plot the results
4. Generate a PNG figure
