"""
Instrument Discovery and Initialization Module
"""

import pyvisa
import time
import threading
import concurrent.futures
from typing import Dict, Optional, Any, Tuple, List

from .terminal import ColorPrinter
from .bk_4063 import BK_4063
from .hp_34401a import HP_34401A
from .hp_e3631a import HP_E3631A
from .tektronix_mso2024 import Tektronix_MSO2024
from .rigol_dho804 import Rigol_DHO804
from .matrix_mps6010h import MATRIX_MPS6010H
from .owon_xdm1041 import Owon_XDM1041
from .jds6600_generator import JDS6600_Generator
from .keysight_edu33212a import Keysight_EDU33212A


class InstrumentDiscovery:
    """
    Scans for and initializes lab instruments automatically.
    """

    # Mapping of model substrings to Driver Classes
    MODEL_MAP = {
        "4063": BK_4063,
        "MSO2024": Tektronix_MSO2024,
        "DHO804": Rigol_DHO804,
        "E3631A": HP_E3631A,
        "34401A": HP_34401A,
        "MPS-6010H-1C": MATRIX_MPS6010H,
        "XDM1041": Owon_XDM1041,
        "JDS6600": JDS6600_Generator,
        "EDU33212A": Keysight_EDU33212A,
    }

    # Friendly names for the instruments (use generic names)
    NAME_MAP = {
        "4063": "awg",
        "MSO2024": "scope",
        "DHO804": "scope",
        "E3631A": "psu",
        "34401A": "dmm",
        "MPS-6010H-1C": "psu",      # Generic name
        "XDM1041": "dmm",           # Generic name
        "JDS6600": "awg",
        "EDU33212A": "awg",
    }


    def __init__(self):
        self.rm = pyvisa.ResourceManager()
        self.found_devices: Dict[str, Any] = {}
        self._print_lock = threading.Lock()

    def _safe_print(self, msg, end="\n", flush=False):
        """Thread-safe printing."""
        with self._print_lock:
            print(msg, end=end, flush=flush)

    def _try_serial_idn(self, inst) -> Optional[str]:
        """
        Try common serial configurations to query *IDN?.

        Returns:
            str: IDN response if successful, None otherwise
        """
        # Common serial configurations for lab instruments
        configs = [
            # (baud_rate, read_term, write_term)
            (9600, '\n', '\r\n'),    # MATRIX MPS-6010H-1C
            (9600, '\n', '\n'),
            (19200, '\n', '\r\n'),
            (115200, '\n', '\n'),
            (115200, '\r\n', '\r\n'),  # JDS6600
        ]

        for baud, read_term, write_term in configs:
            try:
                # Set serial parameters with error handling
                try:
                    inst.baud_rate = baud
                except (ValueError, TypeError):
                    continue  # Skip if baud rate can't be set

                try:
                    inst.data_bits = 8
                    inst.parity = pyvisa.constants.Parity.none
                    inst.stop_bits = pyvisa.constants.StopBits.one
                except (ValueError, TypeError, AttributeError):
                    pass  # Continue even if these fail

                inst.read_termination = read_term
                inst.write_termination = write_term
                inst.timeout = 1000  # 1 second timeout for serial

                idn = inst.query("*IDN?", delay=0.1).strip()
                if idn:  # Got a response
                    return idn
            except Exception:
                continue

        return None

    def _try_matrix_idn(self, inst) -> Optional[str]:
        """
        Try MATRIX MPS-6010H-1C identification.
        This device requires REM:ON before *IDN? will work.
        The IDN response contains non-ASCII garbage bytes before "MPS-6010H-1C",
        so we read raw bytes and search for the key rather than decoding as a string.

        Returns:
            str: "MPS-6010H-1C" if identified, None otherwise
        """
        try:
            inst.baud_rate = 9600
            inst.data_bits = 8
            inst.parity = pyvisa.constants.Parity.none
            inst.stop_bits = pyvisa.constants.StopBits.one
            inst.read_termination = "\n"
            inst.write_termination = "\n"  # LF only, not CR+LF
            inst.timeout = 2000

            # Flush stale bytes left by previous probes at wrong baud rates
            try:
                inst.clear()
            except Exception:
                pass
            time.sleep(0.1)

            # Enable remote mode first (required for *IDN? to work)
            try:
                inst.write("REM:ON")
            except Exception:
                return None
            time.sleep(0.3)

            # Read raw bytes so non-ASCII garbage in the response doesn't cause
            # a decode exception. The IDN response looks like:
            #   <garbage bytes> MPS-6010H-1C \n
            try:
                inst.write("*IDN?")
                time.sleep(0.3)
                raw = inst.read_raw()  # returns bytes, no decoding
                if b"MPS-6010H-1C" in raw:
                    return "MPS-6010H-1C"
            except Exception:
                pass

        except Exception:
            pass

        return None

    def _try_jds6600_idn(self, inst) -> Optional[str]:
        """
        Try JDS6600/Seesii DDS generator identification.
        JDS6600 doesn't respond to *IDN?, uses its own protocol.

        Returns:
            str: "JDS6600" if identified, None otherwise
        """
        try:
            inst.baud_rate = 115200
            inst.data_bits = 8
            inst.parity = pyvisa.constants.Parity.none
            inst.stop_bits = pyvisa.constants.StopBits.one
            inst.read_termination = "\r\n"
            inst.write_termination = "\r\n"
            inst.timeout = 1000

            # Try reading output status (command :r20=)
            inst.write(":r20=")
            response = inst.read().strip()

            # JDS6600 responds with format like ":r20=1,1."
            if response.startswith(":r20=") and (',' in response):
                # Try to get model info
                try:
                    inst.write(":r00=")
                    model_resp = inst.read().strip()
                    # Response like ":r00=15." indicates model
                    return f"JDS6600"
                except:
                    return "JDS6600"

        except Exception:
            pass

        return None

    def _probe_resource(self, resource: str, verbose: bool) -> Optional[Tuple[str, Any, str, str]]:
        """
        Probe a single resource and return (generic_name, driver_instance, model_key, idn) if successful.
        """
        # Skip Bluetooth and other virtual serial ports that often hang
        if any(skip in resource for skip in ["Bluetooth", "BTHENUM", "BT"]):
            if verbose:
                self._safe_print(f"Skipping {resource} (virtual port)")
            return None

        try:
            # Open resource with a short timeout for identification
            inst = self.rm.open_resource(resource, timeout=2000)

            # Clear buffer if possible
            try:
                inst.clear()
            except:
                pass

            # Query IDN
            idn = None
            try:
                # Check if this is a serial device
                if resource.startswith("ASRL"):
                    # Try common serial configurations
                    idn = self._try_serial_idn(inst)

                    # If no *IDN? response, try JDS6600 protocol
                    if not idn:
                        idn = self._try_jds6600_idn(inst)

                    # If still no response, try MATRIX MPS-6010H-1C protocol
                    if not idn:
                        idn = self._try_matrix_idn(inst)
                else:
                    # Standard query for USB/GPIB/Ethernet devices
                    idn = inst.query("*IDN?").strip()

                if not idn:
                    raise pyvisa.VisaIOError("No response")

            except pyvisa.VisaIOError:
                if verbose:
                    self._safe_print(f"Checking {resource}... {ColorPrinter.RED}No response{ColorPrinter.RESET}")
                inst.close()
                return None

            # Match against known models
            for model_key, driver_class in self.MODEL_MAP.items():
                if model_key in idn:
                    generic = self.NAME_MAP[model_key]

                    # We found a match! Initialize the specific driver.
                    # Note: We close the raw instance first, let the driver handle connection.
                    inst.close()

                    try:
                        # Instantiate the driver
                        driver = driver_class(resource)
                        driver.connect()
                        if verbose:
                            self._safe_print(f"Checking {resource}... {ColorPrinter.GREEN}Found: {idn}{ColorPrinter.RESET}")
                            self._safe_print(f"  -> Identified as {generic.upper()} ({model_key})")
                        return (generic, driver, model_key, idn)
                    except Exception as e:
                        if verbose:
                            self._safe_print(f"Checking {resource}... {ColorPrinter.GREEN}Found: {idn}{ColorPrinter.RESET}")
                            self._safe_print(f"{ColorPrinter.RED}  -> Failed to initialize driver: {e}{ColorPrinter.RESET}")
                        return None

            # No match found
            inst.close()
            if verbose:
                self._safe_print(f"Checking {resource}... {ColorPrinter.GREEN}Found: {idn}{ColorPrinter.RESET}")
                self._safe_print(f"{ColorPrinter.YELLOW}  -> Unknown or unsupported device.{ColorPrinter.RESET}")
            return None

        except Exception as e:
            if verbose:
                # Only show meaningful errors, not format/type errors
                error_str = str(e)
                if "format" not in error_str.lower():
                    self._safe_print(f"Checking {resource}... {ColorPrinter.RED}Error: {e}{ColorPrinter.RESET}")
                else:
                    self._safe_print(f"Checking {resource}... {ColorPrinter.RED}No response{ColorPrinter.RESET}")
            return None

    def scan(self, verbose=True) -> Dict[str, Any]:
        """Scans all available VISA resources and attempts to identify supported instruments.

        Returns:
            Dict[str, Any]: A dictionary of initialized instrument drivers, keyed by their friendly name
                            (e.g., 'scope', 'psu', 'awg', 'dmm').
        """
        if verbose:
            ColorPrinter.header("Scanning for Instruments")

        try:
            if verbose:
                print("Enumerating VISA resources...", flush=True)
            resources = self.rm.list_resources()
            if verbose:
                print(f"Found {len(resources)} VISA resource(s)", flush=True)
        except pyvisa.VisaIOError as e:
            if verbose:
                ColorPrinter.error(f"Failed to list resources: {e}")
            return {}
        except Exception as e:
            if verbose:
                ColorPrinter.error(f"Unexpected error listing resources: {e}")
            return {}

        # Use temp keys during scan so we know the full count before naming.
        # Temp key format: "__awg_0", "__awg_1", etc. (double-underscore prefix).
        # After the loop we rename based on total count per type:
        #   1 device  → "awg"
        #   2+ devices → "awg1", "awg2", "awg3", ...
        found_drivers: Dict[str, Any] = {}
        type_counts: Dict[str, int] = {}

        for resource in resources:
            # Skip Bluetooth and other virtual serial ports that often hang
            if any(skip in resource for skip in ["Bluetooth", "BTHENUM", "BT"]):
                if verbose:
                    print(f"Skipping {resource} (virtual port)")
                continue

            if verbose:
                print(f"Checking {resource}...", end=" ", flush=True)

            try:
                # Open resource with a short timeout for identification
                inst = self.rm.open_resource(resource, timeout=2000)

                # Clear buffer if possible
                try:
                    inst.clear()
                except:
                    pass

                # Query IDN
                idn = None
                try:
                    # Check if this is a serial device
                    if resource.startswith("ASRL"):
                        # Try common serial configurations
                        idn = self._try_serial_idn(inst)

                        # If no *IDN? response, try JDS6600 protocol
                        if not idn:
                            idn = self._try_jds6600_idn(inst)

                        # If still no response, try MATRIX MPS-6010H-1C protocol
                        if not idn:
                            idn = self._try_matrix_idn(inst)
                    else:
                        # Standard query for USB/GPIB/Ethernet devices
                        idn = inst.query("*IDN?").strip()

                    if not idn:
                        raise pyvisa.VisaIOError("No response")

                except pyvisa.VisaIOError:
                    if verbose:
                        print(f"{ColorPrinter.RED}No response{ColorPrinter.RESET}")
                    inst.close()
                    continue

                if verbose:
                    print(f"{ColorPrinter.GREEN}Found: {idn}{ColorPrinter.RESET}")

                # Match against known models
                matched = False
                for model_key, driver_class in self.MODEL_MAP.items():
                    if model_key in idn:
                        generic = self.NAME_MAP[model_key]
                        idx = type_counts.get(generic, 0)
                        temp_key = f"__{generic}_{idx}"
                        type_counts[generic] = idx + 1

                        # We found a match! Initialize the specific driver.
                        # Note: We close the raw instance first, let the driver handle connection.
                        inst.close()

                        if verbose:
                            ColorPrinter.success(
                                f"  -> Identified as {generic.upper()} #{idx + 1} ({model_key})"
                            )

                        try:
                            # Instantiate the driver (store under temp key for now)
                            driver = driver_class(resource)
                            driver.connect()
                            found_drivers[temp_key] = driver
                            matched = True
                        except Exception as e:
                            if verbose:
                                ColorPrinter.error(
                                    f"  -> Failed to initialize driver: {e}"
                                )
                        break

                if not matched:
                    inst.close()
                    if verbose:
                        ColorPrinter.warning("  -> Unknown or unsupported device.")

            except Exception as e:
                if verbose:
                    # Only show meaningful errors, not format/type errors
                    error_str = str(e)
                    if "format" not in error_str.lower():
                        print(f"{ColorPrinter.RED}Error: {e}{ColorPrinter.RESET}")
                    else:
                        print(f"{ColorPrinter.RED}No response{ColorPrinter.RESET}")
                continue

        # Post-process: rename from temp keys to final friendly names.
        # 1 device of a type  → "awg"
        # 2+ devices of a type → "awg1", "awg2", "awg3", ...
        final_drivers: Dict[str, Any] = {}
        for generic, total in type_counts.items():
            for idx in range(total):
                temp_key = f"__{generic}_{idx}"
                if temp_key not in found_drivers:
                    continue  # driver failed to initialize
                if total == 1:
                    final_name = generic
                else:
                    final_name = f"{generic}{idx + 1}"
                final_drivers[final_name] = found_drivers[temp_key]

        if verbose:
            for final_name, driver in final_drivers.items():
                ColorPrinter.info(f"  Assigned name: '{final_name}'")

        self.found_devices = final_drivers

        if verbose:
            print("\n")
            if final_drivers:
                ColorPrinter.success(
                    f"Discovery Complete. Found {len(final_drivers)} instruments."
                )
            else:
                ColorPrinter.warning(
                    "Discovery Complete. No supported instruments found."
                )
            print("-" * 60)

        return final_drivers

    def get(self, name: str) -> Optional[Any]:
        """Get an initialized driver by its assigned name.

        Valid names are whatever was assigned during scan() — e.g. 'awg', 'awg1',
        'awg2', 'scope', 'scope1', 'psu', 'dmm', or any custom name set via rename().
        Call list_devices() to see all available names after a scan.
        """
        if name not in self.found_devices:
            available = list(self.found_devices.keys()) or ["(none found — run scan() first)"]
            raise ValueError(
                f"No instrument named '{name}'. Available: {available}"
            )
        return self.found_devices[name]

    def list_devices(self) -> Dict[str, Any]:
        """Return all discovered instruments as a dict of name → driver instance."""
        return dict(self.found_devices)

    def rename(self, old_name: str, new_name: str) -> None:
        """Rename a discovered instrument to a custom name.

        Args:
            old_name (str): Current name (e.g. 'awg1').
            new_name (str): Desired name (e.g. 'awg_xyz').

        Raises:
            ValueError: If old_name does not exist or new_name is already in use.
        """
        if old_name not in self.found_devices:
            available = list(self.found_devices.keys()) or ["(none — run scan() first)"]
            raise ValueError(
                f"No instrument named '{old_name}'. Available: {available}"
            )
        if new_name in self.found_devices:
            raise ValueError(
                f"Name '{new_name}' is already in use by another instrument."
            )
        self.found_devices[new_name] = self.found_devices.pop(old_name)


def find_all(verbose=True) -> Dict[str, Any]:
    """Shortcut function to scan and return all instruments."""
    scanner = InstrumentDiscovery()
    return scanner.scan(verbose)
