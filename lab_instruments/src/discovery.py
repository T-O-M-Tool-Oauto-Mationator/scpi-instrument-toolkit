"""
Instrument Discovery and Initialization Module
"""

import concurrent.futures
import contextlib
import threading
import time
from typing import Any

import pyvisa

from .bk_4063 import BK_4063
from .hp_34401a import HP_34401A
from .hp_e3631a import HP_E3631A
from .jds6600_generator import JDS6600_Generator
from .keysight_dsox1204g import Keysight_DSOX1204G
from .keysight_edu33212a import Keysight_EDU33212A
from .keysight_edu34450a import Keysight_EDU34450A
from .keysight_edu36311a import Keysight_EDU36311A
from .matrix_mps6010h import MATRIX_MPS6010H

try:
    from .ni_pxie_4139 import NI_PXIe_4139

    _NI_PXIE_AVAILABLE = True
except ImportError:
    NI_PXIe_4139 = None  # type: ignore[assignment,misc]
    _NI_PXIE_AVAILABLE = False
try:
    from .ev2300 import TI_EV2300

    _EV2300_AVAILABLE = True
except (ImportError, OSError):
    TI_EV2300 = None  # type: ignore[assignment,misc]
    _EV2300_AVAILABLE = False
from .owon_xdm1041 import Owon_XDM1041
from .rigol_dho804 import Rigol_DHO804
from .tektronix_mso2024 import Tektronix_MSO2024
from .terminal import ColorPrinter


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
        "EDU36311A": Keysight_EDU36311A,
        "EDU34450A": Keysight_EDU34450A,
        "DSOX1204G": Keysight_DSOX1204G,
        **({"PXIe-4139": NI_PXIe_4139} if _NI_PXIE_AVAILABLE else {}),
        **({"EV2300": TI_EV2300} if _EV2300_AVAILABLE else {}),
    }

    # Friendly names for the instruments (use generic names)
    NAME_MAP = {
        "4063": "awg",
        "MSO2024": "scope",
        "DHO804": "scope",
        "E3631A": "psu",
        "34401A": "dmm",
        "MPS-6010H-1C": "psu",  # Generic name
        "XDM1041": "dmm",  # Generic name
        "JDS6600": "awg",
        "EDU33212A": "awg",
        "EDU36311A": "psu",
        "EDU34450A": "dmm",
        "DSOX1204G": "scope",
        "PXIe-4139": "smu",
        "EV2300": "ev2300",
    }

    # Models recognized during scan but not yet supported (driver under development)
    WIP_MODELS = {}

    # PXI slot range to scan for NI-DCPower devices
    PXI_SLOT_RANGE = range(2, 19)

    def __init__(self):
        self.rm = pyvisa.ResourceManager()
        self.found_devices: dict[str, Any] = {}
        self._print_lock = threading.Lock()

    def _safe_print(self, msg, end="\n", flush=False):
        """Thread-safe printing."""
        with self._print_lock:
            print(msg, end=end, flush=flush)

    def _try_serial_idn(self, inst) -> str | None:
        """
        Try common serial configurations to query *IDN?.

        Returns:
            str: IDN response if successful, None otherwise
        """
        # Common serial configurations for lab instruments
        configs = [
            # (baud_rate, read_term, write_term)
            (9600, "\n", "\r\n"),  # MATRIX MPS-6010H-1C
            (9600, "\n", "\n"),
            (19200, "\n", "\r\n"),
            (115200, "\n", "\n"),
            (115200, "\r\n", "\r\n"),  # JDS6600
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

    def _try_matrix_idn(self, inst) -> str | None:
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
            with contextlib.suppress(Exception):
                inst.clear()
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

    def _try_jds6600_idn(self, inst) -> str | None:
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
            if response.startswith(":r20=") and ("," in response):
                # Try to get model info
                try:
                    inst.write(":r00=")
                    inst.read()
                    # Response like ":r00=15." indicates model
                    return "JDS6600"
                except Exception:
                    return "JDS6600"

        except Exception:
            pass

        return None

    def _probe_nidcpower(self, verbose: bool, skip_resources: dict | None = None) -> list:
        """Probe PXI slots for NI-DCPower devices (e.g. PXIe-4139 SMUs).

        Args:
            skip_resources: resource names to skip (already connected).

        Returns a list of (generic_name, driver_instance, model_key, idn) tuples.
        """
        skip_resources = skip_resources or {}
        try:
            import nidcpower
        except ImportError:
            if verbose:
                self._safe_print("Skipping NI-DCPower scan (nidcpower not installed)")
            return []

        if verbose:
            self._safe_print("Scanning PXI slots for NI-DCPower devices...", flush=True)

        results = []
        for slot in self.PXI_SLOT_RANGE:
            resource_name = f"PXI1Slot{slot}"
            if resource_name in skip_resources:
                if verbose:
                    name, _ = skip_resources[resource_name]
                    self._safe_print(f"Keeping {resource_name}... already connected as '{name}'")
                continue
            try:
                session = nidcpower.Session(resource_name=resource_name, channels="0")
                try:
                    model = session.instrument_model
                finally:
                    session.close()

                # Match against known NI-DCPower models
                model_key = None
                for key in self.MODEL_MAP:
                    if key in model:
                        model_key = key
                        break

                if model_key is None:
                    if verbose:
                        self._safe_print(
                            f"Checking {resource_name}... {ColorPrinter.GREEN}Found: {model}{ColorPrinter.RESET}"
                        )
                        self._safe_print(f"{ColorPrinter.YELLOW}  -> Unknown NI-DCPower device.{ColorPrinter.RESET}")
                    continue

                generic = self.NAME_MAP[model_key]
                driver = NI_PXIe_4139(resource_name)
                driver.connect()
                idn = f"National Instruments,{model},{resource_name},nidcpower"

                if verbose:
                    self._safe_print(
                        f"Checking {resource_name}... {ColorPrinter.GREEN}Found: {idn}{ColorPrinter.RESET}"
                    )
                    self._safe_print(f"  -> Identified as {generic.upper()} ({model_key})")

                results.append((generic, driver, model_key, idn))

            except Exception:
                # Slot empty or not an NI-DCPower device — skip silently
                continue

        return results

    def _probe_ev2300(self, verbose: bool, skip_resources: dict | None = None) -> list:
        """Probe USB HID for TI EV2300 adapters.

        Args:
            skip_resources: resource names to skip (already connected).

        Returns a list of (generic_name, driver_instance, model_key, idn) tuples.
        """
        skip_resources = skip_resources or {}
        if not _EV2300_AVAILABLE:
            if verbose:
                self._safe_print("Scanning USB HID for EV2300 adapters...")
                self._safe_print("  [SKIP] EV2300 driver not available (import failed)")
            return []

        if verbose:
            self._safe_print("Scanning USB HID for EV2300 adapters...", flush=True)

        results = []
        try:
            devices = TI_EV2300.enumerate_devices(diagnostics=verbose)
            if not devices and verbose:
                # Check if any are stuck in bootloader mode
                bl_count = TI_EV2300.count_bootloader_devices()
                if bl_count:
                    self._safe_print(
                        f"  {ColorPrinter.YELLOW}[WARN] Found {bl_count} EV2300 in "
                        f"bootloader mode (firmware not loaded). "
                        f"Flash firmware via TI bqStudio.{ColorPrinter.RESET}"
                    )
                else:
                    self._safe_print("  No EV2300 adapters found")

            for dev_info in devices:
                try:
                    path = dev_info["path"]
                    if str(path) in skip_resources:
                        if verbose:
                            name, _ = skip_resources[str(path)]
                            self._safe_print(f"Keeping EV2300... already connected as '{name}'")
                        continue
                    driver = TI_EV2300(path)
                    driver.connect()
                    info = driver.get_device_info()
                    serial = info.get("serial", "unknown") if info.get("ok") else "unknown"
                    idn = f"Texas Instruments,EV2300A,{serial},pure-python-hid"

                    if verbose:
                        self._safe_print(f"Checking USB HID... {ColorPrinter.GREEN}Found: {idn}{ColorPrinter.RESET}")
                        self._safe_print("  -> Identified as EV2300 (USB-to-I2C adapter)")

                    results.append(("ev2300", driver, "EV2300", idn))
                except Exception as exc:
                    if verbose:
                        path_str = dev_info.get("path_str", dev_info.get("path", "?"))
                        self._safe_print(
                            f"  {ColorPrinter.YELLOW}[WARN] EV2300 at {path_str}: "
                            f"connect failed: {exc}{ColorPrinter.RESET}"
                        )
                    continue
        except Exception as exc:
            if verbose:
                self._safe_print(f"  {ColorPrinter.YELLOW}[WARN] EV2300 HID scan failed: {exc}{ColorPrinter.RESET}")

        return results

    def _probe_resource(self, resource: str, verbose: bool) -> tuple[str, Any, str, str] | None:
        """
        Probe a single resource and return (generic_name, driver_instance, model_key, idn) if successful.
        """
        # Skip Bluetooth and other virtual serial ports that often hang
        if any(skip in resource for skip in ["Bluetooth", "BTHENUM"]):
            if verbose:
                self._safe_print(f"Skipping {resource} (virtual port)")
            return None

        # PXI resources are register-based (no query()) and are handled by _probe_nidcpower()
        if resource.upper().startswith("PXI"):
            return None

        try:
            # Open resource with a short timeout for identification
            inst = self.rm.open_resource(resource, timeout=2000)

            # Clear buffer if possible
            with contextlib.suppress(BaseException):
                inst.clear()

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
                            self._safe_print(
                                f"Checking {resource}... {ColorPrinter.GREEN}Found: {idn}{ColorPrinter.RESET}"
                            )
                            self._safe_print(f"  -> Identified as {generic.upper()} ({model_key})")
                        return (generic, driver, model_key, idn)
                    except Exception as e:
                        if verbose:
                            self._safe_print(
                                f"Checking {resource}... {ColorPrinter.GREEN}Found: {idn}{ColorPrinter.RESET}"
                            )
                            self._safe_print(
                                f"{ColorPrinter.RED}  -> Failed to initialize driver: {e}{ColorPrinter.RESET}"
                            )
                        return None

            # Check for WIP models (recognized but driver not yet implemented)
            for wip_key, wip_desc in self.WIP_MODELS.items():
                if wip_key in idn:
                    inst.close()
                    if verbose:
                        self._safe_print(f"Checking {resource}... {ColorPrinter.GREEN}Found: {idn}{ColorPrinter.RESET}")
                        self._safe_print(
                            f"{ColorPrinter.YELLOW}  -> {wip_desc} — not yet supported.{ColorPrinter.RESET}"
                        )
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

    def scan(self, verbose=True, force=False) -> dict[str, Any]:
        """Scans all available VISA resources and attempts to identify supported instruments.

        This scan is performed in parallel for improved performance.
        Already-connected instruments are kept as-is so that a re-scan does
        not disrupt running outputs (e.g. a PSU that is actively sourcing).

        Args:
            verbose: Print progress messages.
            force: If True, re-probe all resources from scratch (first-scan
                behaviour). Existing drivers are disconnected and all
                instruments are re-initialised to safe defaults.

        Returns:
            Dict[str, Any]: A dictionary of initialized instrument drivers, keyed by their friendly name
                            (e.g., 'scope', 'psu', 'awg', 'dmm').
        """
        if verbose:
            ColorPrinter.header("Scanning for Instruments")

        if force:
            # Disconnect existing drivers so they get freshly initialised
            for _name, drv in list(self.found_devices.items()):
                with contextlib.suppress(Exception):
                    drv.disconnect()
            self.found_devices.clear()

        # Build a lookup of resource_name -> (friendly_name, driver) for
        # instruments that are already connected so we can skip re-probing them.
        existing_by_resource: dict[str, tuple[str, Any]] = {}
        for name, drv in self.found_devices.items():
            res_name = getattr(drv, "resource_name", None)
            if res_name:
                existing_by_resource[res_name] = (name, drv)

        try:
            if verbose:
                print("Enumerating VISA resources...", flush=True)
            resources = sorted(self.rm.list_resources())
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

        if not resources:
            return {}

        # Separate resources into already-known and new
        new_resources = []
        kept_results = []  # (generic, driver, model_key, idn) for existing drivers
        for res in resources:
            if res in existing_by_resource:
                name, drv = existing_by_resource[res]
                # Derive the generic type from the name (e.g. "psu1" -> "psu")
                generic = name.rstrip("0123456789")
                # Find the model_key for this driver class
                model_key = ""
                for key, cls in self.MODEL_MAP.items():
                    if isinstance(drv, cls):
                        model_key = key
                        break
                if verbose:
                    self._safe_print(f"Keeping {res}... already connected as '{name}'")
                kept_results.append((generic, drv, model_key, ""))
            else:
                new_resources.append(res)

        # Run probes in parallel — only for new resources
        results = list(kept_results)
        if new_resources:
            with concurrent.futures.ThreadPoolExecutor(max_workers=len(new_resources)) as executor:
                future_to_resource = {executor.submit(self._probe_resource, res, verbose): res for res in new_resources}
                for future in concurrent.futures.as_completed(future_to_resource):
                    try:
                        res = future.result()
                        if res:
                            results.append(res)
                    except Exception as e:
                        if verbose:
                            self._safe_print(f"{ColorPrinter.RED}Thread error during scan: {e}{ColorPrinter.RESET}")

        # Probe PXI slots for NI-DCPower devices (SMUs) — skip already-connected slots
        nidcpower_results = self._probe_nidcpower(verbose, skip_resources=existing_by_resource)
        results.extend(nidcpower_results)

        # Probe USB HID for EV2300 adapters — skip already-connected ones
        ev2300_results = self._probe_ev2300(verbose, skip_resources=existing_by_resource)
        results.extend(ev2300_results)

        # Post-process: handle naming and type counts
        # Sort results by resource name to ensure deterministic naming (e.g. ASRL1 is psu1, ASRL4 is psu2)
        # Result format: (generic, driver, model_key, idn)
        results.sort(key=lambda x: str(x[1].resource_name))

        final_drivers: dict[str, Any] = {}
        type_counts: dict[str, int] = {}

        # Calculate totals for naming
        type_totals: dict[str, int] = {}
        for generic, _, _, _ in results:
            type_totals[generic] = type_totals.get(generic, 0) + 1

        for generic, driver, _model_key, _idn in results:
            idx = type_counts.get(generic, 0)
            total = type_totals[generic]

            final_name = generic if total == 1 else f"{generic}{idx + 1}"

            type_counts[generic] = idx + 1
            final_drivers[final_name] = driver

        if verbose:
            for final_name in sorted(final_drivers.keys()):
                ColorPrinter.info(f"  Assigned name: '{final_name}'")

        self.found_devices = final_drivers

        if verbose:
            print("\n")
            if final_drivers:
                ColorPrinter.success(f"Discovery Complete. Found {len(final_drivers)} instruments.")
            else:
                ColorPrinter.warning("Discovery Complete. No supported instruments found.")
            print("-" * 60)

        return final_drivers

    def get(self, name: str) -> Any | None:
        """Get an initialized driver by its assigned name.

        Valid names are whatever was assigned during scan() — e.g. 'awg', 'awg1',
        'awg2', 'scope', 'scope1', 'psu', 'dmm', or any custom name set via rename().
        Call list_devices() to see all available names after a scan.
        """
        if name not in self.found_devices:
            available = list(self.found_devices.keys()) or ["(none found — run scan() first)"]
            raise ValueError(f"No instrument named '{name}'. Available: {available}")
        return self.found_devices[name]

    def list_devices(self) -> dict[str, Any]:
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
            raise ValueError(f"No instrument named '{old_name}'. Available: {available}")
        if new_name in self.found_devices:
            raise ValueError(f"Name '{new_name}' is already in use by another instrument.")
        self.found_devices[new_name] = self.found_devices.pop(old_name)


def find_all(verbose=True) -> dict[str, Any]:
    """Shortcut function to scan and return all instruments."""
    scanner = InstrumentDiscovery()
    return scanner.scan(verbose)
