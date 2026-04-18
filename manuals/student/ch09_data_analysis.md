# Chapter 9: Data Analysis

After collecting measurements, you need to analyze the data and produce figures for your lab report. This chapter shows how to work with exported CSV data in Python.

## Exporting Data

From the REPL, export your measurement log:

    log save lab_data.csv

This creates a CSV file with columns: Label, Value, Unit, Source.

## Loading CSV with pandas

    import pandas as pd

    df = pd.read_csv("lab_data.csv")
    print(df)

Output:

    Label           Value       Unit    Source
    v_1.0           0.999847    V       dmm1
    v_2.0           1.999623    V       dmm1
    v_3.3           3.299814    V       dmm1
    v_5.0           4.999952    V       dmm1

## Basic Statistics

    print(f"Mean: {df['Value'].mean():.4f}")
    print(f"Std:  {df['Value'].std():.4f}")
    print(f"Min:  {df['Value'].min():.4f}")
    print(f"Max:  {df['Value'].max():.4f}")

## Filtering Data

Select specific measurements by label pattern:

    # All voltage sweep points
    sweep = df[df["Label"].str.startswith("v_")]

    # Only measurements from dmm1
    dmm_data = df[df["Source"] == "dmm1"]

    # Only voltage measurements
    volts = df[df["Unit"] == "V"]

## Plotting with matplotlib

### Line Plot

    import matplotlib.pyplot as plt

    voltages_set = [1.0, 2.0, 3.3, 5.0]
    voltages_measured = sweep["Value"].values

    plt.figure(figsize=(8, 5))
    plt.plot(voltages_set, voltages_measured, "bo-", label="Measured")
    plt.plot(voltages_set, voltages_set, "r--", label="Ideal")
    plt.xlabel("Set Voltage (V)")
    plt.ylabel("Measured Voltage (V)")
    plt.title("PSU Voltage Accuracy")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("voltage_accuracy.png", dpi=150)

### Scatter Plot

    plt.figure(figsize=(8, 5))
    plt.scatter(voltages_set, voltages_measured, c="blue", s=50)
    plt.xlabel("Set Voltage (V)")
    plt.ylabel("Measured Voltage (V)")
    plt.title("Voltage Correlation")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("voltage_scatter.png", dpi=150)

### Bar Chart (Error Comparison)

    errors = [m - s for m, s in zip(voltages_measured, voltages_set)]
    error_pct = [(m - s) / s * 100 for m, s in zip(voltages_measured, voltages_set)]

    plt.figure(figsize=(8, 5))
    plt.bar([str(v) for v in voltages_set], error_pct, color="steelblue")
    plt.xlabel("Set Voltage (V)")
    plt.ylabel("Error (%)")
    plt.title("Percentage Error by Voltage")
    plt.axhline(y=0, color="black", linewidth=0.5)
    plt.grid(axis="y")
    plt.tight_layout()
    plt.savefig("error_bar.png", dpi=150)

### Frequency Response (Bode-like)

    freqs = [100, 500, 1000, 5000, 10000, 50000]
    gains_db = [0.1, 0.0, -0.2, -1.5, -3.1, -8.2]  # example data

    plt.figure(figsize=(8, 5))
    plt.semilogx(freqs, gains_db, "bo-")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Gain (dB)")
    plt.title("Frequency Response")
    plt.grid(True, which="both")
    plt.axhline(y=-3, color="red", linestyle="--", label="-3 dB")
    plt.legend()
    plt.tight_layout()
    plt.savefig("freq_response.png", dpi=150)

## Computing Error Metrics

    import numpy as np

    set_values = np.array(voltages_set)
    measured = np.array(voltages_measured)

    # Absolute error
    abs_error = np.abs(measured - set_values)
    print(f"Max absolute error: {abs_error.max():.6f} V")

    # Percentage error
    pct_error = np.abs((measured - set_values) / set_values) * 100
    print(f"Max percentage error: {pct_error.max():.4f}%")

    # RMS error
    rms_error = np.sqrt(np.mean((measured - set_values) ** 2))
    print(f"RMS error: {rms_error:.6f} V")

## Combining Multiple Test Runs

If you ran the same test multiple times:

    run1 = pd.read_csv("run1.csv")
    run2 = pd.read_csv("run2.csv")
    run3 = pd.read_csv("run3.csv")

    # Combine
    all_runs = pd.concat([run1, run2, run3], keys=["Run 1", "Run 2", "Run 3"])

    # Group by label and compute statistics
    grouped = all_runs.groupby("Label")["Value"]
    summary = grouped.agg(["mean", "std", "min", "max"])
    print(summary)

## Saving Figures for Reports

Always use these settings for professional-looking figures:

    plt.savefig("figure_name.png", dpi=150, bbox_inches="tight")

- Use `dpi=150` for print quality (300 for high-res)
- Use `bbox_inches="tight"` to remove excess whitespace
- Use descriptive filenames: `lab3_voltage_accuracy.png`

## Template: Complete Analysis Script

    import pandas as pd
    import matplotlib.pyplot as plt
    import numpy as np

    # Load data
    df = pd.read_csv("lab_data.csv")

    # Extract sweep data
    sweep = df[df["Label"].str.startswith("v_")]
    set_v = [float(label.split("_")[1]) for label in sweep["Label"]]
    meas_v = sweep["Value"].values

    # Compute errors
    abs_err = np.abs(meas_v - set_v)
    pct_err = np.abs((meas_v - set_v) / set_v) * 100

    # Print summary
    print("=== Voltage Accuracy Summary ===")
    for s, m, e in zip(set_v, meas_v, pct_err):
        print(f"  {s:5.1f} V -> {m:.6f} V  (error: {e:.4f}%)")
    print(f"  Max error: {pct_err.max():.4f}%")
    print(f"  RMS error: {np.sqrt(np.mean(abs_err**2)):.6f} V")

    # Plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    ax1.plot(set_v, meas_v, "bo-", label="Measured")
    ax1.plot(set_v, set_v, "r--", label="Ideal")
    ax1.set_xlabel("Set Voltage (V)")
    ax1.set_ylabel("Measured Voltage (V)")
    ax1.set_title("Voltage Accuracy")
    ax1.legend()
    ax1.grid(True)

    ax2.bar([str(v) for v in set_v], pct_err, color="steelblue")
    ax2.set_xlabel("Set Voltage (V)")
    ax2.set_ylabel("Error (%)")
    ax2.set_title("Percentage Error")
    ax2.grid(axis="y")

    plt.tight_layout()
    plt.savefig("lab_report_figure.png", dpi=150)
    plt.show()

## Try It

1. Run a voltage sweep in mock mode and export to CSV
2. Copy the template analysis script above
3. Run it against your CSV data
4. Generate figures for a report
