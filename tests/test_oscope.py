import contextlib
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

    results = {}
    for channel in [1, 2, 3, 4]:
        ColorPrinter.info(f"Testing Channel {channel} enable/disable")
        oscope.enable_channel(channel)
        user_input = input(f"Is CH{channel} visible? (Enter=yes, 'no'=no): ").strip().lower()
        results[f"Enable_CH{channel}"] = user_input != "no"

        oscope.disable_channel(channel)
        user_input = input(f"Is CH{channel} hidden? (Enter=yes, 'no'=no): ").strip().lower()
        results[f"Disable_CH{channel}"] = user_input != "no"

    return results


def test_basic_measurements(oscope, awg):
    """Test basic measurements using an AWG as signal source."""
    ColorPrinter.header("Basic Measurements Test")

    ColorPrinter.info("Connect AWG Output to Oscilloscope Channel 1")
    probe_atten = input("Probe attenuation (1 or 10): ").strip()
    oscope.set_probe_attenuation(1, float(probe_atten))

    results = {}
    oscope.enable_channel(1)

    test_configs = [
        {"wave_type": "SINE", "frequency": 1000, "amplitude": 1.0, "offset": 0},
        {"wave_type": "SQUARE", "frequency": 500, "amplitude": 2.0, "offset": 0},
        {"wave_type": "RAMP", "frequency": 2000, "amplitude": 0.5, "offset": 0},
    ]

    for config in test_configs:
        ColorPrinter.info(f"Testing {config['wave_type']} at {config['frequency']}Hz, {config['amplitude']}Vpp")

        awg.set_waveform(1, **config)
        awg.enable_output(1, True)
        oscope.autoset()

        measured_freq = oscope.measure_frequency(1)
        measured_pk2pk = oscope.measure_peak_to_peak(1)

        ColorPrinter.info(f"Expected: {config['frequency']}Hz, {config['amplitude']}Vpp")
        ColorPrinter.info(f"Measured: {measured_freq:.2f}Hz, {measured_pk2pk:.3f}Vpp")

        user_input = input("Measurements correct? (Enter=yes, 'no'=no): ").strip().lower()
        results[f"{config['wave_type']}_{config['frequency']}Hz"] = user_input != "no"

        awg.enable_output(1, False)

    return results


def test_measurement_types(oscope, awg):
    """Test various measurement types."""
    ColorPrinter.header("Measurement Types Test")

    results = {}

    ColorPrinter.info("Setting AWG to 1kHz sine wave, 2Vpp")
    awg.set_waveform(1, "SINE", frequency=1000, amplitude=2.0, offset=0)
    awg.enable_output(1, True)

    oscope.enable_channel(1)
    oscope.autoset()

    measurements = {
        "Frequency": oscope.measure_frequency(1),
        "Period": oscope.measure_period(1),
        "Peak-to-Peak": oscope.measure_peak_to_peak(1),
        "RMS": oscope.measure_rms(1),
        "Mean": oscope.measure_mean(1),
        "Maximum": oscope.measure_max(1),
        "Minimum": oscope.measure_min(1),
    }

    for name, value in measurements.items():
        ColorPrinter.info(f"{name}: {value:.6f}")

    user_input = input("All measurements reasonable? (Enter=yes, 'no'=no): ").strip().lower()
    results["All_Measurement_Types"] = user_input != "no"

    awg.enable_output(1, False)
    return results


def test_scales(oscope, awg):
    """Test vertical and horizontal scale adjustments."""
    ColorPrinter.header("Scale Test")

    results = {}

    awg.set_waveform(1, "SINE", frequency=1000, amplitude=2.0, offset=0)
    awg.enable_output(1, True)
    oscope.enable_channel(1)
    oscope.autoset()

    # Vertical scales
    for scale in [0.5, 1.0, 2.0]:
        ColorPrinter.info(f"Testing {scale}V/div")
        oscope.set_vertical_scale(1, scale)
        user_input = input("Scale correct? (Enter=yes, 'no'=no): ").strip().lower()
        results[f"Vertical_{scale}V"] = user_input != "no"

    # Horizontal scales
    for scale in [0.0001, 0.001, 0.01]:
        ColorPrinter.info(f"Testing {scale * 1000}ms/div")
        oscope.set_horizontal_scale(scale)
        user_input = input("Scale correct? (Enter=yes, 'no'=no): ").strip().lower()
        results[f"Horizontal_{scale * 1000}ms"] = user_input != "no"

    awg.enable_output(1, False)
    return results


def test_trigger(oscope, awg):
    """Test trigger configuration."""
    ColorPrinter.header("Trigger Test")

    results = {}

    awg.set_waveform(1, "SQUARE", frequency=1000, amplitude=2.0, offset=0)
    awg.enable_output(1, True)
    oscope.enable_channel(1)
    oscope.autoset()

    ColorPrinter.info("Testing Rising Edge Trigger at 0.5V")
    oscope.configure_trigger(1, level=0.5, slope="RISE", mode="NORMAL")
    user_input = input("Trigger working? (Enter=yes, 'no'=no): ").strip().lower()
    results["Trigger_Rising"] = user_input != "no"

    ColorPrinter.info("Testing Falling Edge Trigger at 0.5V")
    oscope.configure_trigger(1, level=0.5, slope="FALL", mode="NORMAL")
    user_input = input("Trigger working? (Enter=yes, 'no'=no): ").strip().lower()
    results["Trigger_Falling"] = user_input != "no"

    awg.enable_output(1, False)
    return results


def test_waveform_capture(oscope, awg):
    """Test waveform data capture."""
    ColorPrinter.header("Waveform Capture Test")

    results = {}

    awg.set_waveform(1, "SINE", frequency=1000, amplitude=2.0, offset=0)
    awg.enable_output(1, True)
    oscope.enable_channel(1)
    oscope.autoset()

    ColorPrinter.info("Capturing waveform data")
    raw_data = oscope.get_waveform_data(1)
    ColorPrinter.info(f"Captured {len(raw_data)} raw points")

    time_vals, volt_vals = oscope.get_waveform_scaled(1)
    ColorPrinter.info(f"Captured {len(time_vals)} scaled points")

    if len(volt_vals) > 0:
        ColorPrinter.info(f"Voltage range: {min(volt_vals):.3f}V to {max(volt_vals):.3f}V")

    user_input = input("Data captured correctly? (Enter=yes, 'no'=no): ").strip().lower()
    results["Waveform_Capture"] = user_input != "no"

    awg.enable_output(1, False)
    return results


def test_delay_measurement(oscope, awg):
    """Test delay measurement between two channels."""
    ColorPrinter.header("Delay Measurement Test")

    results = {}

    ColorPrinter.info("Setting AWG CH1 to 1kHz sine")
    awg.set_waveform(1, "SINE", frequency=1000, amplitude=2.0, offset=0)

    # Note: BK_4063 driver might need update to support phase/delay if we want to automate the source delay.
    # For now, we will ask user to setup a delay or just use two channels if available.
    # Assuming the user connects CH1 to Scope CH1 and Scope CH2.

    ColorPrinter.info("Connect AWG CH1 to Scope CH1 AND Scope CH2 (or use two AWG channels with phase shift)")
    ColorPrinter.info("This test assumes a signal is present on both CH1 and CH2")

    awg.enable_output(1, True)
    # If possible, enable AWG CH2 as well if connected
    try:
        awg.set_waveform(
            2, "SINE", frequency=1000, amplitude=2.0, offset=0, phase=90
        )  # 90 deg phase shift = 0.25ms delay
        awg.enable_output(2, True)
        ColorPrinter.info("Attempted to set AWG CH2 with 90 degree phase shift")
    except Exception as e:
        ColorPrinter.warning(f"Could not set AWG CH2: {e}. Ensure signal is split to CH1 & CH2 or manually configure.")

    oscope.enable_channel(1)
    oscope.enable_channel(2)
    oscope.autoset()

    # Measure Delay
    delay = oscope.measure_delay(1, 2)
    ColorPrinter.info(f"Measured Delay (CH1 -> CH2): {delay:.6e} s")

    user_input = input("Delay measurement reasonable? (Enter=yes, 'no'=no): ").strip().lower()
    results["Delay_Measurement"] = user_input != "no"

    awg.enable_output(1, False)
    with contextlib.suppress(BaseException):
        awg.enable_output(2, False)

    return results


def print_summary(results):
    """Print test summary."""
    ColorPrinter.header("Test Summary")

    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    skipped = sum(1 for r in results.values() if r is None)

    for name, result in results.items():
        if result is None:
            ColorPrinter.warning(f"{name}: SKIPPED")
        elif result:
            ColorPrinter.success(f"{name}: PASS")
        else:
            ColorPrinter.error(f"{name}: FAIL")

    ColorPrinter.info(f"\nTotal: {len(results)}")
    ColorPrinter.success(f"Passed: {passed}")
    ColorPrinter.error(f"Failed: {failed}")
    ColorPrinter.warning(f"Skipped: {skipped}")


def main():
    ColorPrinter.header("Testing Tektronix MSO2024 Oscilloscope Driver")

    # Discover instruments
    discovery = InstrumentDiscovery()
    discovery.scan(verbose=True)
    oscope = discovery.get("scope")
    awg = discovery.get("awg")

    if not oscope or not isinstance(oscope, Tektronix_MSO2024):
        ColorPrinter.error("Tektronix MSO2024 not found")
        return

    if not awg or not isinstance(awg, BK_4063):
        ColorPrinter.warning("BK_4063 AWG not found. Some tests will be skipped.")

    all_results = {}

    try:
        while True:
            ColorPrinter.header("Oscilloscope Test Menu")
            print("1. Channel Control Test")
            print("2. Basic Measurements Test (requires AWG)")
            print("3. Measurement Types Test (requires AWG)")
            print("4. Scale Test (requires AWG)")
            print("5. Trigger Test (requires AWG)")
            print("6. Waveform Capture Test (requires AWG)")
            print("7. Delay Measurement Test (requires AWG)")
            print("8. Run All Tests")
            print("9. Show Summary & Exit")
            print("0. Exit")

            choice = input("\nSelect test (0-9): ").strip()

            if choice == "1":
                all_results.update(test_channel_control(oscope))
            elif choice == "2":
                if awg:
                    all_results.update(test_basic_measurements(oscope, awg))
                else:
                    ColorPrinter.error("AWG required")
            elif choice == "3":
                if awg:
                    all_results.update(test_measurement_types(oscope, awg))
                else:
                    ColorPrinter.error("AWG required")
            elif choice == "4":
                if awg:
                    all_results.update(test_scales(oscope, awg))
                else:
                    ColorPrinter.error("AWG required")
            elif choice == "5":
                if awg:
                    all_results.update(test_trigger(oscope, awg))
                else:
                    ColorPrinter.error("AWG required")
            elif choice == "6":
                if awg:
                    all_results.update(test_waveform_capture(oscope, awg))
                else:
                    ColorPrinter.error("AWG required")
            elif choice == "7":
                if awg:
                    all_results.update(test_delay_measurement(oscope, awg))
                else:
                    ColorPrinter.error("AWG required")
            elif choice == "8":
                all_results.update(test_channel_control(oscope))
                if awg:
                    all_results.update(test_basic_measurements(oscope, awg))
                    all_results.update(test_measurement_types(oscope, awg))
                    all_results.update(test_scales(oscope, awg))
                    all_results.update(test_trigger(oscope, awg))
                    all_results.update(test_waveform_capture(oscope, awg))
                    all_results.update(test_delay_measurement(oscope, awg))
            elif choice == "9":
                if all_results:
                    print_summary(all_results)
                else:
                    ColorPrinter.warning("No tests run yet")
                break
            elif choice == "0":
                break
            else:
                ColorPrinter.error("Invalid choice")

            print()

    except KeyboardInterrupt:
        ColorPrinter.warning("\nInterrupted by user")
    finally:
        ColorPrinter.info("Disconnecting instruments")
        oscope.disable_all_channels()
        oscope.disconnect()
        if awg:
            awg.disable_all_channels()
            awg.disconnect()

        if all_results:
            print_summary(all_results)


if __name__ == "__main__":
    main()
