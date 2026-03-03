import sys
import pytest
from pathlib import Path

# Hardware integration test — run manually with real instruments, not in CI
pytestmark = pytest.mark.skip(reason="hardware integration test — requires physical DMM/PSU")

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from lab_instruments import HP_34401A, HP_E3631A, ColorPrinter, InstrumentDiscovery
except ImportError as e:
    print(f"Import Error: {e}")
    print(
        "Ensure you are running this from the project root or have installed the package."
    )
    sys.exit(1)


def test_dc_voltage_with_psu(dmm, psu):
    """Test DC Voltage measurements using the PSU as a reference."""
    ColorPrinter.header("DC Voltage Measurement Test")

    test_voltages = [1.0, 3.3, 5.0, 10.0, 15.0]
    results = {}

    ColorPrinter.info("Setup Instructions:")
    ColorPrinter.info("1. Connect PSU positive_6_volts_channel (+) to DMM HI (Red)")
    ColorPrinter.info("2. Connect PSU COM (-) to DMM LO (Black)")
    input("\nPress Enter when connections are ready...")

    psu.enable_output(True)

    for voltage in test_voltages:
        ColorPrinter.info(f"\nSetting PSU to {voltage}V...")
        psu.set_output_channel("positive_6_volts_channel", voltage, current_limit=0.1)

        input(f"Press Enter to measure {voltage}V...")
        measured = dmm.measure_dc_voltage()

        ColorPrinter.info(f"PSU Set: {voltage}V | DMM Measured: {measured:.6f}V")
        ColorPrinter.info(f"Difference: {abs(voltage - measured):.6f}V")

        user_input = input("Does the reading look correct? (yes/no): ").strip().lower()
        results[f"DC_Voltage_{voltage}V"] = user_input == "yes"

    psu.enable_output(False)
    return results


def test_dc_current_with_resistor(dmm, psu):
    """Test DC Current measurements with known resistor."""
    ColorPrinter.header("DC Current Measurement Test")

    ColorPrinter.info("Setup Instructions:")
    ColorPrinter.info("1. Get a 100Ω resistor (or note the actual value)")
    resistor_value = float(input("Enter the resistor value in Ohms (e.g., 100): "))

    ColorPrinter.info("\n2. Connect circuit as follows:")
    ColorPrinter.info("   PSU positive_6_volts_channel (+) → Resistor → DMM HI (Red)")
    ColorPrinter.info("   DMM LO (Black) → PSU COM (-)")
    ColorPrinter.info("   (DMM is in series to measure current)")
    input("\nPress Enter when connections are ready...")

    test_voltages = [1.0, 3.0, 5.0]
    results = {}

    psu.enable_output(True)

    for voltage in test_voltages:
        ColorPrinter.info(f"\nSetting PSU to {voltage}V...")
        psu.set_output_channel("positive_6_volts_channel", voltage, current_limit=1.0)

        expected_current = voltage / resistor_value
        input(f"Press Enter to measure current...")
        measured = dmm.measure_dc_current()

        ColorPrinter.info(
            f"Expected Current: {expected_current:.6f}A ({expected_current*1000:.3f}mA)"
        )
        ColorPrinter.info(f"DMM Measured: {measured:.6f}A ({measured*1000:.3f}mA)")
        ColorPrinter.info(f"Difference: {abs(expected_current - measured)*1000:.3f}mA")

        user_input = input("Does the reading look correct? (yes/no): ").strip().lower()
        results[f"DC_Current_{voltage}V"] = user_input == "yes"

    psu.enable_output(False)
    return results


def test_resistance_2wire(dmm):
    """Test 2-Wire Resistance measurements."""
    ColorPrinter.header("2-Wire Resistance Measurement Test")

    ColorPrinter.info("Setup Instructions:")
    ColorPrinter.info("1. Get several resistors with known values")
    ColorPrinter.info("2. Connect resistor between DMM HI (Red) and LO (Black)")
    ColorPrinter.info("3. We'll test multiple resistors")

    results = {}
    test_count = int(input("\nHow many resistors do you want to test? "))

    for i in range(test_count):
        ColorPrinter.info(f"\n--- Resistor #{i+1} ---")
        expected_value = float(input("Enter the expected resistance in Ohms: "))
        input("Connect resistor and press Enter to measure...")

        measured = dmm.measure_resistance_2wire()

        ColorPrinter.info(f"Expected: {expected_value}Ω")
        ColorPrinter.info(f"Measured: {measured:.2f}Ω")

        if expected_value > 0:
            percent_diff = abs((measured - expected_value) / expected_value) * 100
            ColorPrinter.info(f"Percent Difference: {percent_diff:.2f}%")

        user_input = input("Does the reading look correct? (yes/no): ").strip().lower()
        results[f"2Wire_Resistance_{i+1}"] = user_input == "yes"

    return results


def test_resistance_4wire(dmm):
    """Test 4-Wire Resistance measurements (Kelvin Sensing)."""
    ColorPrinter.header("4-Wire Resistance Measurement Test (Kelvin Sensing)")

    ColorPrinter.info("Setup Instructions:")
    ColorPrinter.info("1. Get a low-value resistor (e.g., 1Ω - 100Ω)")
    ColorPrinter.info("2. Connect using 4-wire configuration:")
    ColorPrinter.info("   - Force HI: Current source positive")
    ColorPrinter.info("   - Sense HI: Voltage sense positive")
    ColorPrinter.info("   - Sense LO: Voltage sense negative")
    ColorPrinter.info("   - Force LO: Current source negative")
    ColorPrinter.info("3. 4-wire eliminates lead resistance errors")

    results = {}
    test_it = input("\nDo you have 4-wire setup ready? (yes/no): ").strip().lower()

    if test_it == "yes":
        expected_value = float(input("Enter the expected resistance in Ohms: "))
        input("Press Enter to measure...")

        measured_4wire = dmm.measure_resistance_4wire()
        ColorPrinter.info(f"4-Wire Measured: {measured_4wire:.6f}Ω")

        input("\nNow test with 2-wire for comparison. Press Enter...")
        measured_2wire = dmm.measure_resistance_2wire()
        ColorPrinter.info(f"2-Wire Measured: {measured_2wire:.6f}Ω")

        ColorPrinter.info(f"\nDifference: {abs(measured_4wire - measured_2wire):.6f}Ω")
        ColorPrinter.info("(4-wire should be more accurate for low resistance)")

        user_input = input("Does 4-wire work correctly? (yes/no): ").strip().lower()
        results["4Wire_Resistance"] = user_input == "yes"
    else:
        ColorPrinter.warning("Skipping 4-wire test")
        results["4Wire_Resistance"] = None

    return results


def test_continuity(dmm):
    """Test Continuity function."""
    ColorPrinter.header("Continuity Test")

    ColorPrinter.info("Setup Instructions:")
    ColorPrinter.info("1. This tests for low resistance (< 1kΩ)")
    ColorPrinter.info("2. Use a wire or low-value resistor for 'closed' test")
    ColorPrinter.info("3. Use nothing (open) for 'open' test")

    results = {}

    # Test closed circuit
    ColorPrinter.info("\n--- Test 1: Closed Circuit ---")
    input("Connect a wire between DMM HI and LO, then press Enter...")
    closed_reading = dmm.measure_continuity()
    ColorPrinter.info(f"Continuity Reading (Closed): {closed_reading:.2f}Ω")
    ColorPrinter.info("Should be very low (< 10Ω for wire)")
    user_input = input("Is continuity detected? (yes/no): ").strip().lower()
    results["Continuity_Closed"] = user_input == "yes"

    # Test open circuit
    ColorPrinter.info("\n--- Test 2: Open Circuit ---")
    input("Remove wire (open circuit), then press Enter...")
    open_reading = dmm.measure_continuity()
    ColorPrinter.info(f"Continuity Reading (Open): {open_reading}")
    ColorPrinter.info("Should be very high or overflow")
    user_input = input("Is open circuit detected? (yes/no): ").strip().lower()
    results["Continuity_Open"] = user_input == "yes"

    return results


def test_diode(dmm):
    """Test Diode function."""
    ColorPrinter.header("Diode Test")

    ColorPrinter.info("Setup Instructions:")
    ColorPrinter.info("1. Get a standard diode (e.g., 1N4148, 1N4001)")
    ColorPrinter.info("2. Diode test applies ~1mA and measures forward voltage")
    ColorPrinter.info("3. Forward voltage should be ~0.5-0.7V for silicon diodes")

    results = {}
    test_it = input("\nDo you have a diode ready? (yes/no): ").strip().lower()

    if test_it == "yes":
        # Forward bias
        ColorPrinter.info("\n--- Test 1: Forward Bias ---")
        ColorPrinter.info("Connect: DMM HI (Red) → Diode Anode")
        ColorPrinter.info("         DMM LO (Black) → Diode Cathode")
        input("Press Enter to measure forward voltage...")
        forward_voltage = dmm.measure_diode()
        ColorPrinter.info(f"Forward Voltage: {forward_voltage:.3f}V")
        ColorPrinter.info("Typical: 0.5-0.7V for silicon, 0.2-0.3V for Schottky")
        user_input = input("Is forward voltage reasonable? (yes/no): ").strip().lower()
        results["Diode_Forward"] = user_input == "yes"

        # Reverse bias
        ColorPrinter.info("\n--- Test 2: Reverse Bias ---")
        ColorPrinter.info("Reverse the diode connections")
        input("Press Enter to measure reverse voltage...")
        reverse_voltage = dmm.measure_diode()
        ColorPrinter.info(f"Reverse Voltage: {reverse_voltage}")
        ColorPrinter.info("Should show overflow/open (very high resistance)")
        user_input = (
            input("Is reverse bias working (open/OL)? (yes/no): ").strip().lower()
        )
        results["Diode_Reverse"] = user_input == "yes"
    else:
        ColorPrinter.warning("Skipping diode test")
        results["Diode_Forward"] = None
        results["Diode_Reverse"] = None

    return results


def test_ac_voltage(dmm):
    """Test AC Voltage measurements."""
    ColorPrinter.header("AC Voltage Measurement Test")

    ColorPrinter.info("Setup Instructions:")
    ColorPrinter.info("1. You'll need an AC source (function generator or wall outlet)")
    ColorPrinter.info("2. For safety, use a function generator with 1-10V AC")
    ColorPrinter.info("3. Connect AC source to DMM HI and LO")
    ColorPrinter.warning("DANGER: Be careful with mains voltage (120V/240V)!")

    results = {}
    test_it = input("\nDo you have a safe AC source ready? (yes/no): ").strip().lower()

    if test_it == "yes":
        expected_voltage = float(input("What AC voltage do you expect? (RMS): "))
        input("Connect AC source and press Enter to measure...")

        measured = dmm.measure_ac_voltage()
        ColorPrinter.info(f"Expected AC Voltage: {expected_voltage}V (RMS)")
        ColorPrinter.info(f"Measured AC Voltage: {measured:.3f}V (RMS)")

        user_input = input("Does the reading look correct? (yes/no): ").strip().lower()
        results["AC_Voltage"] = user_input == "yes"
    else:
        ColorPrinter.warning("Skipping AC voltage test")
        results["AC_Voltage"] = None

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
    ColorPrinter.header("Testing HP 34401A DMM Driver")

    # Discover connected instruments
    discovery = InstrumentDiscovery()
    discovery.scan(verbose=True)
    dmm = discovery.get("dmm")
    psu = discovery.get("psu")

    if not dmm or not isinstance(dmm, HP_34401A):
        ColorPrinter.error("HP 34401A DMM not found among connected instruments.")
        return

    if not psu or not isinstance(psu, HP_E3631A):
        ColorPrinter.warning("HP E3631A PSU not found. Some tests will be skipped.")

    # Menu for test selection
    all_results = {}

    try:
        while True:
            ColorPrinter.header("DMM Test Menu")
            print("1. DC Voltage Test (requires PSU)")
            print("2. DC Current Test (requires PSU + resistor)")
            print("3. 2-Wire Resistance Test (requires resistors)")
            print("4. 4-Wire Resistance Test (requires 4-wire setup)")
            print("5. Continuity Test (requires wire)")
            print("6. Diode Test (requires diode)")
            print("7. AC Voltage Test (requires AC source)")
            print("8. Run All Tests")
            print("9. Show Summary & Exit")
            print("0. Exit")

            choice = input("\nSelect test (0-9): ").strip()

            if choice == "1":
                if psu:
                    all_results.update(test_dc_voltage_with_psu(dmm, psu))
                else:
                    ColorPrinter.error("PSU required for this test")
            elif choice == "2":
                if psu:
                    all_results.update(test_dc_current_with_resistor(dmm, psu))
                else:
                    ColorPrinter.error("PSU required for this test")
            elif choice == "3":
                all_results.update(test_resistance_2wire(dmm))
            elif choice == "4":
                all_results.update(test_resistance_4wire(dmm))
            elif choice == "5":
                all_results.update(test_continuity(dmm))
            elif choice == "6":
                all_results.update(test_diode(dmm))
            elif choice == "7":
                all_results.update(test_ac_voltage(dmm))
            elif choice == "8":
                # Run all tests
                if psu:
                    all_results.update(test_dc_voltage_with_psu(dmm, psu))
                    all_results.update(test_dc_current_with_resistor(dmm, psu))
                all_results.update(test_resistance_2wire(dmm))
                all_results.update(test_resistance_4wire(dmm))
                all_results.update(test_continuity(dmm))
                all_results.update(test_diode(dmm))
                all_results.update(test_ac_voltage(dmm))
            elif choice == "9":
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
        dmm.disconnect()
        if psu:
            psu.disable_all_channels()
            psu.disconnect()

        if all_results:
            print_test_summary(all_results)


if __name__ == "__main__":
    main()
