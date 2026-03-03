import sys
from pathlib import Path

import pytest

# Hardware integration test — run manually with real instruments, not in CI
pytestmark = pytest.mark.skip(reason="hardware integration test — requires physical oscilloscope/AWG")

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from lab_instruments import (
        BK_4063,
        ColorPrinter,
        InstrumentDiscovery,
        Tektronix_MSO2024,
    )
except ImportError as e:
    print(f"Import Error: {e}")
    print("Ensure you are running this from the project root or have installed the package.")
    sys.exit(1)


def test_channel_control(oscope):
    """Test channel enable/disable functionality."""
    ColorPrinter.header("Channel Control Test")

    ColorPrinter.info("This test verifies that channels can be enabled and disabled.")
    results = {}

    # Test enabling individual channels
    for channel in [1, 2, 3, 4]:
        ColorPrinter.info(f"\n--- Testing Channel {channel} ---")
        ColorPrinter.info(f"Enabling Channel {channel}...")
        oscope.enable_channel(channel)

        input(f"Check if Channel {channel} is displayed on the scope, then press Enter...")
        user_input = input(f"Is Channel {channel} visible? (yes/no): ").strip().lower()
        results[f"Enable_CH{channel}"] = user_input == "yes"

        ColorPrinter.info(f"Disabling Channel {channel}...")
        oscope.disable_channel(channel)

        input(f"Check if Channel {channel} is now hidden, then press Enter...")
        user_input = input(f"Is Channel {channel} hidden? (yes/no): ").strip().lower()
        results[f"Disable_CH{channel}"] = user_input == "yes"

    return results


def test_basic_measurements_with_awg(oscope, awg):
    """Test basic measurements using an AWG as signal source."""
    ColorPrinter.header("Basic Measurements Test (with AWG)")

    ColorPrinter.info("Setup Instructions:")
    ColorPrinter.info("1. Connect AWG Output to Oscilloscope Channel 1")
    ColorPrinter.info("2. Make sure probe is set to 1X or 10X (note which one)")
    input("\nPress Enter when connections are ready...")

    # Configure the probe attenuation
    probe_atten = input("What is your probe attenuation? (1 or 10): ").strip()
    probe_atten = float(probe_atten)
    oscope.set_probe_attenuation(1, probe_atten)

    results = {}

    # Enable Channel 1
    oscope.enable_channel(1)

    # Test different waveforms and frequencies
    test_configs = [
        {"waveform": "SIN", "frequency": 1000, "amplitude": 1.0, "offset": 0},
        {"waveform": "SQU", "frequency": 500, "amplitude": 2.0, "offset": 0},
        {"waveform": "TRI", "frequency": 2000, "amplitude": 0.5, "offset": 0},
    ]

    awg.enable_output(True)

    for i, config in enumerate(test_configs):
        ColorPrinter.info(f"\n--- Test {i + 1}: {config['waveform']} wave ---")
        ColorPrinter.info(f"Setting AWG: {config['frequency']}Hz, {config['amplitude']}Vpp")

        awg.set_waveform(
            waveform=config["waveform"],
            frequency=config["frequency"],
            amplitude=config["amplitude"],
            offset=config["offset"],
        )

        input("Press Enter to perform autoset and measure...")

        # Perform autoset
        oscope.autoset()

        # Measure frequency
        measured_freq = oscope.measure_frequency(1)
        ColorPrinter.info(f"Expected Frequency: {config['frequency']}Hz")
        ColorPrinter.info(f"Measured Frequency: {measured_freq:.2f}Hz")

        # Measure peak-to-peak
        measured_pk2pk = oscope.measure_peak_to_peak(1)
        ColorPrinter.info(f"Expected Amplitude: {config['amplitude']}Vpp")
        ColorPrinter.info(f"Measured Peak-to-Peak: {measured_pk2pk:.3f}Vpp")

        user_input = input("Do the measurements look correct? (yes/no): ").strip().lower()
        results[f"{config['waveform']}_{config['frequency']}Hz"] = user_input == "yes"

    awg.enable_output(False)
    return results


def test_measurement_types(oscope, awg):
    """Test various measurement types."""
    ColorPrinter.header("Measurement Types Test")

    ColorPrinter.info("Setup Instructions:")
    ColorPrinter.info("1. AWG should be connected to Channel 1")
    input("\nPress Enter when ready...")

    results = {}

    # Set AWG to generate a sine wave
    ColorPrinter.info("Setting AWG to 1kHz sine wave, 2Vpp...")
    awg.set_waveform(waveform="SIN", frequency=1000, amplitude=2.0, offset=0)
    awg.enable_output(True)

    oscope.enable_channel(1)
    oscope.autoset()

    input("Press Enter to measure various parameters...")

    # Test different measurement types
    measurements = {
        "Frequency": oscope.measure_frequency(1),
        "Period": oscope.measure_period(1),
        "Peak-to-Peak": oscope.measure_peak_to_peak(1),
        "RMS": oscope.measure_rms(1),
        "Mean": oscope.measure_mean(1),
        "Maximum": oscope.measure_max(1),
        "Minimum": oscope.measure_min(1),
    }

    ColorPrinter.info("\n--- Measurement Results ---")
    for name, value in measurements.items():
        ColorPrinter.info(f"{name}: {value:.6f}")

    user_input = input("\nDo all measurements appear reasonable? (yes/no): ").strip().lower()
    results["All_Measurement_Types"] = user_input == "yes"

    awg.enable_output(False)
    return results


def test_vertical_scale(oscope, awg):
    """Test vertical scale adjustment."""
    ColorPrinter.header("Vertical Scale Test")

    ColorPrinter.info("Setup Instructions:")
    ColorPrinter.info("1. AWG should be connected to Channel 1")
    input("\nPress Enter when ready...")

    results = {}

    # Set AWG to known signal
    awg.set_waveform(waveform="SIN", frequency=1000, amplitude=2.0, offset=0)
    awg.enable_output(True)

    oscope.enable_channel(1)

    # Test different vertical scales
    scales = [0.5, 1.0, 2.0]  # Volts per division

    for scale in scales:
        ColorPrinter.info(f"\n--- Testing {scale}V/div ---")
        oscope.set_vertical_scale(1, scale)

        input(f"Check that vertical scale is {scale}V/div, then press Enter...")
        user_input = input("Is the scale correct? (yes/no): ").strip().lower()
        results[f"Vertical_Scale_{scale}V_div"] = user_input == "yes"

    awg.enable_output(False)
    return results


def test_horizontal_scale(oscope, awg):
    """Test horizontal (time) scale adjustment."""
    ColorPrinter.header("Horizontal Scale Test")

    ColorPrinter.info("Setup Instructions:")
    ColorPrinter.info("1. AWG should be connected to Channel 1")
    input("\nPress Enter when ready...")

    results = {}

    # Set AWG to known signal
    awg.set_waveform(waveform="SIN", frequency=1000, amplitude=2.0, offset=0)
    awg.enable_output(True)

    oscope.enable_channel(1)
    oscope.autoset()

    # Test different horizontal scales
    scales = [0.0001, 0.001, 0.01]  # Seconds per division

    for scale in scales:
        ColorPrinter.info(f"\n--- Testing {scale * 1000}ms/div ---")
        oscope.set_horizontal_scale(scale)

        input(f"Check that horizontal scale is {scale * 1000}ms/div, then press Enter...")
        user_input = input("Is the scale correct? (yes/no): ").strip().lower()
        results[f"Horizontal_Scale_{scale * 1000}ms_div"] = user_input == "yes"

    awg.enable_output(False)
    return results


def test_trigger_configuration(oscope, awg):
    """Test trigger configuration."""
    ColorPrinter.header("Trigger Configuration Test")

    ColorPrinter.info("Setup Instructions:")
    ColorPrinter.info("1. AWG should be connected to Channel 1")
    input("\nPress Enter when ready...")

    results = {}

    # Set AWG to square wave for clear triggering
    awg.set_waveform(waveform="SQU", frequency=1000, amplitude=2.0, offset=0)
    awg.enable_output(True)

    oscope.enable_channel(1)
    oscope.autoset()

    # Test rising edge trigger
    ColorPrinter.info("\n--- Testing Rising Edge Trigger ---")
    oscope.configure_trigger(1, level=0.5, slope="RISE", mode="NORMAL")

    input("Check that trigger is on rising edge at 0.5V, then press Enter...")
    user_input = input("Is the trigger working correctly? (yes/no): ").strip().lower()
    results["Trigger_Rising_Edge"] = user_input == "yes"

    # Test falling edge trigger
    ColorPrinter.info("\n--- Testing Falling Edge Trigger ---")
    oscope.configure_trigger(1, level=0.5, slope="FALL", mode="NORMAL")

    input("Check that trigger is on falling edge at 0.5V, then press Enter...")
    user_input = input("Is the trigger working correctly? (yes/no): ").strip().lower()
    results["Trigger_Falling_Edge"] = user_input == "yes"

    awg.enable_output(False)
    return results


def test_math_functions(oscope, awg):
    """Test math functions."""
    ColorPrinter.header("Math Functions Test")

    ColorPrinter.info("Setup Instructions:")
    ColorPrinter.info("1. AWG should be connected to Channel 1 and Channel 2")
    ColorPrinter.info("2. For this test, we'll use the same signal on both channels")
    input("\nPress Enter when ready...")

    results = {}
    test_it = input("Do you have AWG connected to both CH1 and CH2? (yes/no): ").strip().lower()

    if test_it == "yes":
        # Set AWG to known signal
        awg.set_waveform(waveform="SIN", frequency=1000, amplitude=2.0, offset=0)
        awg.enable_output(True)

        oscope.enable_channel(1)
        oscope.enable_channel(2)
        oscope.autoset()

        # Configure math to show CH1 - CH2 (should be ~0 if same signal)
        ColorPrinter.info("\n--- Testing Math: CH1 - CH2 ---")
        oscope.configure_math("CH1-CH2")

        input("Check the Math waveform display, then press Enter...")
        user_input = input("Is Math waveform displayed? (yes/no): ").strip().lower()
        results["Math_Display"] = user_input == "yes"

        # Measure math waveform
        mean_diff = oscope.measure_math_bnf("MEAN")
        ColorPrinter.info(f"Mean of (CH1 - CH2): {mean_diff:.6f}V")
        ColorPrinter.info("(Should be close to 0 if same signal)")

        user_input = input("Is the math measurement reasonable? (yes/no): ").strip().lower()
        results["Math_Measurement"] = user_input == "yes"

        awg.enable_output(False)
    else:
        ColorPrinter.warning("Skipping math functions test")
        results["Math_Display"] = None
        results["Math_Measurement"] = None

    return results


def test_waveform_capture(oscope, awg):
    """Test waveform data capture."""
    ColorPrinter.header("Waveform Data Capture Test")

    ColorPrinter.info("Setup Instructions:")
    ColorPrinter.info("1. AWG should be connected to Channel 1")
    input("\nPress Enter when ready...")

    results = {}

    # Set AWG to known signal
    awg.set_waveform(waveform="SIN", frequency=1000, amplitude=2.0, offset=0)
    awg.enable_output(True)

    oscope.enable_channel(1)
    oscope.autoset()

    input("Press Enter to capture waveform data...")

    # Get raw data
    ColorPrinter.info("Capturing raw waveform data...")
    raw_data = oscope.get_waveform_data(1)
    ColorPrinter.info(f"Captured {len(raw_data)} data points")

    user_input = input("Was data captured successfully? (yes/no): ").strip().lower()
    results["Waveform_Raw_Data"] = user_input == "yes"

    # Get scaled data
    ColorPrinter.info("\nCapturing scaled waveform data...")
    time_vals, volt_vals = oscope.get_waveform_scaled(1)
    ColorPrinter.info(f"Captured {len(time_vals)} time points and {len(volt_vals)} voltage points")

    if len(time_vals) > 0 and len(volt_vals) > 0:
        ColorPrinter.info(f"Time range: {time_vals[0]:.6f}s to {time_vals[-1]:.6f}s")
        ColorPrinter.info(f"Voltage range: {min(volt_vals):.3f}V to {max(volt_vals):.3f}V")

    user_input = input("Does the scaled data look correct? (yes/no): ").strip().lower()
    results["Waveform_Scaled_Data"] = user_input == "yes"

    # Optional: Save to CSV
    save_csv = input("\nDo you want to save waveform to CSV? (yes/no): ").strip().lower()
    if save_csv == "yes":
        filename = input("Enter filename (e.g., waveform.csv): ").strip()
        if not filename.endswith(".csv"):
            filename += ".csv"
        oscope.save_waveform_csv(1, filename)
        ColorPrinter.success(f"Waveform saved to {filename}")

    awg.enable_output(False)
    return results


def test_acquisition_modes(oscope, awg):
    """Test different acquisition modes."""
    ColorPrinter.header("Acquisition Modes Test")

    ColorPrinter.info("Setup Instructions:")
    ColorPrinter.info("1. AWG should be connected to Channel 1")
    input("\nPress Enter when ready...")

    results = {}

    # Set AWG to known signal
    awg.set_waveform(waveform="SIN", frequency=1000, amplitude=2.0, offset=0)
    awg.enable_output(True)

    oscope.enable_channel(1)
    oscope.autoset()

    # Test different acquisition modes
    modes = ["SAMPLE", "AVERAGE", "PEAKDETECT"]

    for mode in modes:
        ColorPrinter.info(f"\n--- Testing {mode} Mode ---")
        if mode == "AVERAGE":
            oscope.set_acquisition_mode(mode, num_averages=16)
            ColorPrinter.info("Set to AVERAGE mode with 16 averages")
        else:
            oscope.set_acquisition_mode(mode)

        input("Check the acquisition mode on the scope, then press Enter...")
        user_input = input(f"Is {mode} mode active? (yes/no): ").strip().lower()
        results[f"Acquisition_Mode_{mode}"] = user_input == "yes"

    awg.enable_output(False)
    return results


def print_test_summary(all_results):
    """Print summary of all test results."""
    ColorPrinter.header("Test Summary")

    passed = 0
    failed = 0
    skipped = 0

    for test_name, result in all_results.items():
        if result is None:
            ColorPrinter.warning(f"{test_name}: SKIPPED")
            skipped += 1
        elif result:
            ColorPrinter.success(f"{test_name}: PASS")
            passed += 1
        else:
            ColorPrinter.error(f"{test_name}: FAIL")
            failed += 1

    ColorPrinter.info(f"\nTotal: {len(all_results)} tests")
    ColorPrinter.success(f"Passed: {passed}")
    ColorPrinter.error(f"Failed: {failed}")
    ColorPrinter.warning(f"Skipped: {skipped}")


def main():
    ColorPrinter.header("Testing Tektronix MSO2024 Oscilloscope Driver")

    # Discover connected instruments
    discovery = InstrumentDiscovery()
    discovery.scan(verbose=True)
    oscope = discovery.get("scope")
    awg = discovery.get("awg")

    if not oscope or not isinstance(oscope, Tektronix_MSO2024):
        ColorPrinter.error("Tektronix MSO2024 Oscilloscope not found among connected instruments.")
        return

    if not awg or not isinstance(awg, BK_4063):
        ColorPrinter.warning("BK_4063 AWG not found. Some tests will be skipped.")

    # Menu for test selection
    all_results = {}

    try:
        while True:
            ColorPrinter.header("Oscilloscope Test Menu")
            print("1. Channel Control Test")
            print("2. Basic Measurements Test (requires AWG)")
            print("3. Measurement Types Test (requires AWG)")
            print("4. Vertical Scale Test (requires AWG)")
            print("5. Horizontal Scale Test (requires AWG)")
            print("6. Trigger Configuration Test (requires AWG)")
            print("7. Math Functions Test (requires AWG)")
            print("8. Waveform Capture Test (requires AWG)")
            print("9. Acquisition Modes Test (requires AWG)")
            print("10. Run All Tests")
            print("11. Show Summary & Exit")
            print("0. Exit")

            choice = input("\nSelect test (0-11): ").strip()

            if choice == "1":
                all_results.update(test_channel_control(oscope))
            elif choice == "2":
                if awg:
                    all_results.update(test_basic_measurements_with_awg(oscope, awg))
                else:
                    ColorPrinter.error("AWG required for this test")
            elif choice == "3":
                if awg:
                    all_results.update(test_measurement_types(oscope, awg))
                else:
                    ColorPrinter.error("AWG required for this test")
            elif choice == "4":
                if awg:
                    all_results.update(test_vertical_scale(oscope, awg))
                else:
                    ColorPrinter.error("AWG required for this test")
            elif choice == "5":
                if awg:
                    all_results.update(test_horizontal_scale(oscope, awg))
                else:
                    ColorPrinter.error("AWG required for this test")
            elif choice == "6":
                if awg:
                    all_results.update(test_trigger_configuration(oscope, awg))
                else:
                    ColorPrinter.error("AWG required for this test")
            elif choice == "7":
                if awg:
                    all_results.update(test_math_functions(oscope, awg))
                else:
                    ColorPrinter.error("AWG required for this test")
            elif choice == "8":
                if awg:
                    all_results.update(test_waveform_capture(oscope, awg))
                else:
                    ColorPrinter.error("AWG required for this test")
            elif choice == "9":
                if awg:
                    all_results.update(test_acquisition_modes(oscope, awg))
                else:
                    ColorPrinter.error("AWG required for this test")
            elif choice == "10":
                # Run all tests
                all_results.update(test_channel_control(oscope))
                if awg:
                    all_results.update(test_basic_measurements_with_awg(oscope, awg))
                    all_results.update(test_measurement_types(oscope, awg))
                    all_results.update(test_vertical_scale(oscope, awg))
                    all_results.update(test_horizontal_scale(oscope, awg))
                    all_results.update(test_trigger_configuration(oscope, awg))
                    all_results.update(test_math_functions(oscope, awg))
                    all_results.update(test_waveform_capture(oscope, awg))
                    all_results.update(test_acquisition_modes(oscope, awg))
            elif choice == "11":
                if all_results:
                    print_test_summary(all_results)
                else:
                    ColorPrinter.warning("No tests have been run yet")
                break
            elif choice == "0":
                ColorPrinter.info("Exiting without summary")
                break
            else:
                ColorPrinter.error("Invalid choice. Please try again.")

            print("\n")

    except KeyboardInterrupt:
        ColorPrinter.warning("\nTest interrupted by user")
    finally:
        ColorPrinter.info("Disconnecting instruments...")
        oscope.disable_all_channels()
        oscope.disconnect()
        if awg:
            awg.enable_output(False)
            awg.disconnect()

        if all_results:
            print_test_summary(all_results)


if __name__ == "__main__":
    main()
