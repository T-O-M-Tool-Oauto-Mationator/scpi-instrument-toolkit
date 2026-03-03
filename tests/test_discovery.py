"""
Test Instrument Discovery
=========================
Verifies that the lab_instruments.discovery module can find and initialize
connected devices.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from lab_instruments import ColorPrinter, find_all
except ImportError as e:
    print(f"Import Error: {e}")
    print("Ensure you are running this from the project root or have installed the package.")
    sys.exit(1)


def main():
    ColorPrinter.header("Testing Instrument Discovery")

    # Run the scanner
    instruments = find_all(verbose=True)

    try:
        print("\nSummary of Connected Devices:")
        for name, driver in instruments.items():
            print(f" - {name.ljust(10)} : {driver.resource_name}")

        # Optional: Verify connection by asking for IDN again from the driver wrapper
        if instruments:
            print("\nVerifying Driver Communications:")
            for name, driver in instruments.items():
                try:
                    # Assuming drivers have a query method or similar, or we can use the raw instrument
                    # Our DeviceManager has a query method
                    idn = driver.query("*IDN?")
                    print(f" [{name}] -> {idn}")
                except Exception as e:
                    ColorPrinter.error(f" [{name}] -> Communication Failed: {e}")

    finally:
        # Cleanup
        print("\nDisconnecting...")
        for driver in instruments.values():
            driver.disconnect()


if __name__ == "__main__":
    main()
