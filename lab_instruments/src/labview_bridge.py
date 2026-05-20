"""
LabVIEW Bridge — flat wrapper functions for calling instrument drivers from LabVIEW Python Nodes.

LabVIEW's Python Node (2018+) can call Python functions but NOT class methods directly.
This module provides flat functions with simple types (str, int, float, bool) that wrap
the existing instrument driver classes via a module-level cache keyed by string IDs.

Usage from LabVIEW:
    1. Configure Python Node with module path to this file
    2. Call open_psu("USB0::...", "HP_E3631A") -> returns "psu_1"
    3. Call psu_set_voltage("psu_1", 1, 5.0) -> returns "OK"
    4. Call close_instrument("psu_1") -> returns "OK"

LabVIEW loads .py files by path as standalone scripts, so __package__ is None and
relative imports (from .xyz) would normally fail. The block below detects that case
and patches sys.path + __package__ before the relative imports are executed.
"""

# ruff: noqa: E402 -- bootstrap block must precede relative imports (LabVIEW standalone load)

import os as _os
import sys as _sys

if not __package__:
    # Standalone load: lab_instruments/src/labview_bridge.py -> parent = lab_instruments/src/
    # Two dirname() calls reach the directory that contains the lab_instruments package.
    _pkg_root = _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
    if _pkg_root not in _sys.path:
        _sys.path.insert(0, _pkg_root)
    # Pre-import the package hierarchy so Python's relative-import resolver can find them.
    import importlib as _il

    _il.import_module("lab_instruments")
    _il.import_module("lab_instruments.src")
    __package__ = "lab_instruments.src"
    del _il, _pkg_root

del _os, _sys

import contextlib
import json
import threading

from .bk_4063 import BK_4063
from .hp_34401a import HP_34401A
from .hp_e3631a import HP_E3631A
from .jds6600_generator import JDS6600_Generator
from .keysight_dsox1204g import Keysight_DSOX1204G
from .keysight_edu33212a import Keysight_EDU33212A
from .keysight_edu34450a import Keysight_EDU34450A
from .keysight_edu36311a import Keysight_EDU36311A
from .matrix_mps6010h import MATRIX_MPS6010H
from .owon_xdm1041 import Owon_XDM1041
from .rigol_dho804 import Rigol_DHO804
from .tektronix_mso2024 import Tektronix_MSO2024

try:
    from .ni_pxie_4139 import NI_PXIe_4139
except ImportError:
    NI_PXIe_4139 = None  # type: ignore[assignment,misc]

try:
    from .ev2300 import TI_EV2300
except (ImportError, OSError):
    TI_EV2300 = None  # type: ignore[assignment,misc]

# ---------------------------------------------------------------------------
# Module-level instrument cache
# ---------------------------------------------------------------------------

_instruments: dict[str, object] = {}
_id_counter: int = 0
_lock = threading.Lock()

# ---------------------------------------------------------------------------
# Driver map and category tuples
# ---------------------------------------------------------------------------

_DRIVER_MAP: dict[str, type] = {
    "HP_E3631A": HP_E3631A,
    "EDU36311A": Keysight_EDU36311A,
    "MPS6010H": MATRIX_MPS6010H,
    "HP_34401A": HP_34401A,
    "EDU34450A": Keysight_EDU34450A,
    "XDM1041": Owon_XDM1041,
    "EDU33212A": Keysight_EDU33212A,
    "BK_4063": BK_4063,
    "JDS6600": JDS6600_Generator,
    "MSO2024": Tektronix_MSO2024,
    "DHO804": Rigol_DHO804,
    "DSOX1204G": Keysight_DSOX1204G,
}

if NI_PXIe_4139 is not None:
    _DRIVER_MAP["PXIe_4139"] = NI_PXIe_4139

if TI_EV2300 is not None:
    _DRIVER_MAP["EV2300"] = TI_EV2300

_PSU_CLASSES = (HP_E3631A, Keysight_EDU36311A, MATRIX_MPS6010H)
if NI_PXIe_4139 is not None:
    _PSU_CLASSES = (*_PSU_CLASSES, NI_PXIe_4139)

_DMM_CLASSES = (HP_34401A, Keysight_EDU34450A, Owon_XDM1041)
_AWG_CLASSES = (Keysight_EDU33212A, BK_4063, JDS6600_Generator)
_SCOPE_CLASSES = (Tektronix_MSO2024, Rigol_DHO804, Keysight_DSOX1204G)
_SMU_CLASSES = (NI_PXIe_4139,) if NI_PXIe_4139 is not None else ()
_EV2300_CLASSES = (TI_EV2300,) if TI_EV2300 is not None else ()

# Category prefix for auto-generated IDs
_CATEGORY_PREFIX = {}
for _cls in (HP_E3631A, Keysight_EDU36311A, MATRIX_MPS6010H):
    _CATEGORY_PREFIX[_cls] = "psu"
for _cls in (HP_34401A, Keysight_EDU34450A, Owon_XDM1041):
    _CATEGORY_PREFIX[_cls] = "dmm"
for _cls in (Keysight_EDU33212A, BK_4063, JDS6600_Generator):
    _CATEGORY_PREFIX[_cls] = "awg"
for _cls in (Tektronix_MSO2024, Rigol_DHO804, Keysight_DSOX1204G):
    _CATEGORY_PREFIX[_cls] = "scope"
if NI_PXIe_4139 is not None:
    _CATEGORY_PREFIX[NI_PXIe_4139] = "smu"
if TI_EV2300 is not None:
    _CATEGORY_PREFIX[TI_EV2300] = "ev2300"

# HP_E3631A channel mapping: int -> Channel enum
_HP_CHANNEL_MAP = {
    1: HP_E3631A.Channel.POSITIVE_6V,
    2: HP_E3631A.Channel.POSITIVE_25V,
    3: HP_E3631A.Channel.NEGATIVE_25V,
}

# EDU36311A channel mapping: int -> string key
_EDU_CHANNEL_MAP = {
    1: "p6v_channel",
    2: "p30v_channel",
    3: "n30v_channel",
}

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _next_id(driver_class: type) -> str:
    """Generate the next instrument ID like 'psu_1', 'dmm_2', etc."""
    global _id_counter
    prefix = _CATEGORY_PREFIX.get(driver_class, "inst")
    _id_counter += 1
    return f"{prefix}_{_id_counter}"


def _get(instrument_id: str) -> object:
    """Retrieve a cached instrument or raise KeyError.

    Acquires _lock so a concurrent close_instrument cannot mutate the dict
    mid-read. The available-IDs snapshot used in the error message is
    captured under the same lock.
    """
    with _lock:
        dev = _instruments.get(instrument_id)
        if dev is not None:
            return dev
        available = list(_instruments.keys()) or ["(none - open an instrument first)"]
    raise KeyError(f"No instrument with ID '{instrument_id}'. Open instruments: {available}") from None


def _get_typed(instrument_id: str, valid_types: tuple) -> object:
    """Retrieve a cached instrument and validate its type."""
    dev = _get(instrument_id)
    if not isinstance(dev, valid_types):
        expected = [c.__name__ for c in valid_types]
        raise TypeError(f"Instrument '{instrument_id}' is {type(dev).__name__}, expected one of {expected}")
    return dev


# ---------------------------------------------------------------------------
# Parameter validation helpers
# ---------------------------------------------------------------------------
#
# LabVIEW's Python Node defaults unwired terminals to type-specific zero
# values: String -> "", I32 -> 0, DBL -> 0.0, Boolean -> False. None of those
# raise on the LabVIEW side, so cryptic Python errors (KeyError, AttributeError,
# silent disable) used to fall through to the user. These helpers translate
# the LabVIEW defaults into actionable error messages naming the parameter
# slot and what the user likely forgot to wire.


def _require_id(op: str, instrument_id) -> None:
    """Reject empty/non-string instrument_id.

    Unwired LabVIEW String terminal arrives as "" which matches no open
    instrument; raising here keeps the failure at the boundary instead of
    deep inside _get.
    """
    if not isinstance(instrument_id, str) or not instrument_id:
        raise ValueError(
            f"{op}: 'instrument_id' must be a non-empty string returned by "
            f"open_psu/open_dmm/open_awg/open_scope/open_smu/open_ev2300, got "
            f"{instrument_id!r} (type: {type(instrument_id).__name__}). "
            f"In LabVIEW: wire the output of the open_* Python Node into the "
            f"first (top) parameter slot of this Python Node. An unwired "
            f"String terminal arrives as the empty string."
        )


def _require_bool(op: str, param: str, value, *, lab_hint: str = "") -> None:
    """Reject non-bool. Unwired LabVIEW Boolean defaults to False which can
    silently disable an output - prefer a loud error."""
    if not isinstance(value, bool):
        hint = lab_hint or (
            f"In LabVIEW: place a True/False Constant from Programming > Boolean and wire it into the '{param}' slot."
        )
        raise TypeError(
            f"{op}: '{param}' must be a Boolean (True/False), got {value!r} (type: {type(value).__name__}). {hint}"
        )


def _require_number(op: str, param: str, value, *, lab_hint: str = "") -> None:
    """Reject non-numeric (also rejects bool because bool subclasses int and a
    True wired into a voltage slot is almost certainly a wiring mistake)."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        hint = lab_hint or (
            f"In LabVIEW: place a Numeric Constant (DBL, orange) from "
            f"Programming > Numeric and wire it into the '{param}' slot."
        )
        raise TypeError(
            f"{op}: '{param}' must be a number (int or float), got {value!r} (type: {type(value).__name__}). {hint}"
        )


def _require_channel(op: str, value, *, valid: tuple = (), max_ch: int = 0) -> None:
    """Reject non-int channel or out-of-range channel.

    Pass `valid=(1, 2, 3)` for explicit allowlist, or `max_ch=N` for 1..N.
    LabVIEW I32 unwired terminal arrives as 0 which is not a valid channel.
    """
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(
            f"{op}: 'channel' must be an integer, got {value!r} "
            f"(type: {type(value).__name__}). In LabVIEW: place a Numeric "
            f"Constant set to I32 representation and wire it into the "
            f"'channel' slot. An unwired terminal arrives as 0 which is "
            f"not a valid channel number."
        )
    if valid and value not in valid:
        raise ValueError(f"{op}: 'channel' must be one of {list(valid)}, got {value}.")
    if max_ch and not (1 <= value <= max_ch):
        raise ValueError(f"{op}: 'channel' must be 1..{max_ch}, got {value}.")


def _require_str(op: str, param: str, value, *, nonempty: bool = True) -> None:
    """Reject non-string (or empty-string when nonempty=True)."""
    if not isinstance(value, str):
        raise TypeError(f"{op}: '{param}' must be a string, got {value!r} (type: {type(value).__name__}).")
    if nonempty and not value:
        raise ValueError(
            f"{op}: '{param}' must be a non-empty string. In LabVIEW: an "
            f"unwired String terminal arrives as the empty string - make "
            f"sure a String Constant is connected to the '{param}' slot."
        )


def _require_byte(op: str, param: str, value) -> None:
    """Reject non-int or out-of-range [0, 255]."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{op}: '{param}' must be an integer 0..255, got {value!r} (type: {type(value).__name__}).")
    if not (0 <= value <= 0xFF):
        raise ValueError(f"{op}: '{param}' must be 0..255, got {value}.")


def _require_word(op: str, param: str, value) -> None:
    """Reject non-int or out-of-range [0, 65535]."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{op}: '{param}' must be an integer 0..65535, got {value!r} (type: {type(value).__name__}).")
    if not (0 <= value <= 0xFFFF):
        raise ValueError(f"{op}: '{param}' must be 0..65535, got {value}.")


def _require_i2c_addr(op: str, value) -> None:
    """Reject non-int or out-of-range 7-bit I2C address (0..127)."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(
            f"{op}: 'i2c_addr' must be an integer 7-bit I2C address (0..127), "
            f"got {value!r} (type: {type(value).__name__})."
        )
    if not (0 <= value <= 0x7F):
        raise ValueError(f"{op}: 'i2c_addr' must be a 7-bit I2C address (0..127), got 0x{value:X}.")


def _require_positive(op: str, param: str, value) -> None:
    """Reject value <= 0 (use after _require_number)."""
    if value <= 0:
        raise ValueError(
            f"{op}: '{param}' must be > 0, got {value}. In LabVIEW: an unwired Numeric terminal arrives as 0.0."
        )


# =========================================================================
# Discovery
# =========================================================================


def discover_instruments() -> str:
    """Scan for connected instruments and return results as JSON.

    Returns:
        str: JSON object like {"psu": "HP_E3631A", "dmm": "HP_34401A", ...}
    """
    from .discovery import find_all

    found = find_all(verbose=False)
    result = {name: type(drv).__name__ for name, drv in found.items()}
    return json.dumps(result)


def list_available_drivers() -> str:
    """Return a JSON list of driver name strings accepted by open_instrument().

    Returns:
        str: JSON list like ["HP_E3631A", "MPS6010H", "HP_34401A", ...]
    """
    return json.dumps(sorted(_DRIVER_MAP.keys()))


def list_open_instruments() -> str:
    """Return a JSON object of currently open instruments.

    Returns:
        str: JSON object like {"psu_1": "HP_E3631A", "dmm_2": "HP_34401A"}
    """
    with _lock:
        result = {k: type(v).__name__ for k, v in _instruments.items()}
    return json.dumps(result)


def list_visa_resources() -> str:
    """Return a JSON list of VISA resource strings visible on this system.

    Returns:
        str: JSON list like ["USB0::0x0957::0x0807::...", "ASRL3::INSTR", ...]
    """
    import pyvisa

    rm = pyvisa.ResourceManager()
    resources = list(rm.list_resources())
    return json.dumps(sorted(resources))


# =========================================================================
# Connection / lifecycle
# =========================================================================


def open_instrument(visa_address: str, driver_name: str) -> str:
    """Open an instrument connection and return its string ID.

    Args:
        visa_address: VISA resource string (e.g. "USB0::0x0957::...::INSTR")
        driver_name: Driver key from list_available_drivers() (e.g. "HP_E3631A")

    Returns:
        str: Instrument ID (e.g. "psu_1") to use in subsequent calls.
    """
    _require_str("open_instrument", "visa_address", visa_address)
    _require_str("open_instrument", "driver_name", driver_name)
    if driver_name not in _DRIVER_MAP:
        raise ValueError(f"Unknown driver '{driver_name}'. Available: {sorted(_DRIVER_MAP.keys())}")
    driver_class = _DRIVER_MAP[driver_name]
    dev = driver_class(visa_address)
    dev.connect()
    with _lock:
        inst_id = _next_id(driver_class)
        _instruments[inst_id] = dev
    return inst_id


def open_psu(visa_address: str, driver_name: str) -> str:
    """Open a power supply (validates driver is a PSU type)."""
    _require_str("open_psu", "visa_address", visa_address)
    _require_str("open_psu", "driver_name", driver_name)
    if driver_name not in _DRIVER_MAP:
        raise ValueError(f"Unknown driver '{driver_name}'. Available: {sorted(_DRIVER_MAP.keys())}")
    if not issubclass(_DRIVER_MAP[driver_name], _PSU_CLASSES):
        raise TypeError(f"'{driver_name}' is not a PSU driver.")
    return open_instrument(visa_address, driver_name)


def open_dmm(visa_address: str, driver_name: str) -> str:
    """Open a digital multimeter (validates driver is a DMM type)."""
    _require_str("open_dmm", "visa_address", visa_address)
    _require_str("open_dmm", "driver_name", driver_name)
    if driver_name not in _DRIVER_MAP:
        raise ValueError(f"Unknown driver '{driver_name}'. Available: {sorted(_DRIVER_MAP.keys())}")
    if not issubclass(_DRIVER_MAP[driver_name], _DMM_CLASSES):
        raise TypeError(f"'{driver_name}' is not a DMM driver.")
    return open_instrument(visa_address, driver_name)


def open_awg(visa_address: str, driver_name: str) -> str:
    """Open a function generator (validates driver is an AWG type)."""
    _require_str("open_awg", "visa_address", visa_address)
    _require_str("open_awg", "driver_name", driver_name)
    if driver_name not in _DRIVER_MAP:
        raise ValueError(f"Unknown driver '{driver_name}'. Available: {sorted(_DRIVER_MAP.keys())}")
    if not issubclass(_DRIVER_MAP[driver_name], _AWG_CLASSES):
        raise TypeError(f"'{driver_name}' is not an AWG driver.")
    return open_instrument(visa_address, driver_name)


def open_scope(visa_address: str, driver_name: str) -> str:
    """Open an oscilloscope (validates driver is a scope type)."""
    _require_str("open_scope", "visa_address", visa_address)
    _require_str("open_scope", "driver_name", driver_name)
    if driver_name not in _DRIVER_MAP:
        raise ValueError(f"Unknown driver '{driver_name}'. Available: {sorted(_DRIVER_MAP.keys())}")
    if not issubclass(_DRIVER_MAP[driver_name], _SCOPE_CLASSES):
        raise TypeError(f"'{driver_name}' is not a scope driver.")
    return open_instrument(visa_address, driver_name)


def open_smu(visa_address: str, driver_name: str) -> str:
    """Open a source measure unit (validates driver is an SMU type)."""
    if not _SMU_CLASSES:
        raise ImportError("SMU support not available (nidcpower not installed).")
    _require_str("open_smu", "visa_address", visa_address)
    _require_str("open_smu", "driver_name", driver_name)
    if driver_name not in _DRIVER_MAP:
        raise ValueError(f"Unknown driver '{driver_name}'. Available: {sorted(_DRIVER_MAP.keys())}")
    if not issubclass(_DRIVER_MAP[driver_name], _SMU_CLASSES):
        raise TypeError(f"'{driver_name}' is not an SMU driver.")
    return open_instrument(visa_address, driver_name)


def open_ev2300(resource_name: str = "") -> str:
    """Open a TI EV2300 USB-to-I2C adapter.

    Args:
        resource_name: HID device path, or empty string to auto-detect.

    Returns:
        str: Instrument ID (e.g. "ev2300_1").
    """
    if TI_EV2300 is None:
        raise ImportError("EV2300 driver not available. Install hidapi: pip install hidapi")
    # resource_name is intentionally allowed to be "" (auto-detect path),
    # but a non-str rejects loudly.
    if not isinstance(resource_name, str):
        raise TypeError(
            f"open_ev2300: 'resource_name' must be a string (empty for "
            f"auto-detect), got {resource_name!r} (type: {type(resource_name).__name__})."
        )
    if resource_name:
        dev = TI_EV2300(resource_name)
    else:
        devices = TI_EV2300.enumerate_devices()
        if not devices:
            raise RuntimeError("No EV2300 adapters found on USB.")
        dev = TI_EV2300(devices[0]["path"])
    dev.connect()
    with _lock:
        inst_id = _next_id(TI_EV2300)
        _instruments[inst_id] = dev
    return inst_id


def close_instrument(instrument_id: str) -> str:
    """Close an instrument and remove it from the cache.

    Returns:
        str: "OK"
    """
    _require_id("close_instrument", instrument_id)
    with _lock:
        dev = _instruments.pop(instrument_id, None)
    if dev is None:
        raise KeyError(f"No instrument with ID '{instrument_id}'.")
    dev.disconnect()
    return "OK"


def close_all() -> str:
    """Close all open instruments.

    Returns:
        str: "OK"
    """
    with _lock:
        items = list(_instruments.items())
        _instruments.clear()
    for _, dev in items:
        with contextlib.suppress(Exception):
            dev.disconnect()
    return "OK"


# =========================================================================
# PSU operations
# =========================================================================


def psu_set_voltage(instrument_id: str, channel: int, voltage: float) -> str:
    """Set the voltage on a PSU channel.

    Args:
        instrument_id: ID returned by open_psu/open_instrument.
        channel: Channel number (1, 2, or 3). Single-channel PSUs ignore this.
        voltage: Desired voltage in volts.

    Returns:
        str: "OK"
    """
    _require_id("psu_set_voltage", instrument_id)
    _require_channel("psu_set_voltage", channel)
    _require_number("psu_set_voltage", "voltage", voltage)
    dev = _get_typed(instrument_id, _PSU_CLASSES)
    if isinstance(dev, HP_E3631A):
        ch = _HP_CHANNEL_MAP.get(channel)
        if ch is None:
            raise ValueError(f"HP_E3631A channel must be 1, 2, or 3. Got {channel!r} (type: {type(channel).__name__}).")
        dev.set_voltage(ch, voltage)
    elif isinstance(dev, Keysight_EDU36311A):
        ch_key = _EDU_CHANNEL_MAP.get(channel)
        if ch_key is None:
            raise ValueError(f"EDU36311A channel must be 1, 2, or 3. Got {channel!r} (type: {type(channel).__name__}).")
        dev.set_voltage(ch_key, voltage)
    elif isinstance(dev, MATRIX_MPS6010H) or (NI_PXIe_4139 is not None and isinstance(dev, NI_PXIe_4139)):
        dev.set_voltage(voltage)
    else:
        raise TypeError(f"Unsupported PSU type: {type(dev).__name__}")
    return "OK"


def psu_set_current_limit(instrument_id: str, channel: int, current: float) -> str:
    """Set the current limit on a PSU channel.

    Returns:
        str: "OK"
    """
    _require_id("psu_set_current_limit", instrument_id)
    _require_channel("psu_set_current_limit", channel)
    _require_number("psu_set_current_limit", "current", current)
    dev = _get_typed(instrument_id, _PSU_CLASSES)
    if isinstance(dev, HP_E3631A):
        ch = _HP_CHANNEL_MAP.get(channel)
        if ch is None:
            raise ValueError(f"HP_E3631A channel must be 1, 2, or 3. Got {channel!r} (type: {type(channel).__name__}).")
        dev.set_current_limit(ch, current)
    elif isinstance(dev, Keysight_EDU36311A):
        ch_key = _EDU_CHANNEL_MAP.get(channel)
        if ch_key is None:
            raise ValueError(f"EDU36311A channel must be 1, 2, or 3. Got {channel!r} (type: {type(channel).__name__}).")
        dev.set_current_limit(ch_key, current)
    elif isinstance(dev, MATRIX_MPS6010H) or (NI_PXIe_4139 is not None and isinstance(dev, NI_PXIe_4139)):
        dev.set_current_limit(current)
    else:
        raise TypeError(f"Unsupported PSU type: {type(dev).__name__}")
    return "OK"


def psu_set_output_channel(instrument_id: str, channel: int, voltage: float, current_limit: float) -> str:
    """Set voltage and current limit for a PSU channel in one call.

    Returns:
        str: "OK"
    """
    _require_id("psu_set_output_channel", instrument_id)
    _require_channel("psu_set_output_channel", channel)
    _require_number("psu_set_output_channel", "voltage", voltage)
    _require_number("psu_set_output_channel", "current_limit", current_limit)
    dev = _get_typed(instrument_id, _PSU_CLASSES)
    if isinstance(dev, HP_E3631A):
        ch = _HP_CHANNEL_MAP.get(channel)
        if ch is None:
            raise ValueError(f"HP_E3631A channel must be 1, 2, or 3. Got {channel!r} (type: {type(channel).__name__}).")
        dev.set_output_channel(ch, voltage, current_limit)
    elif isinstance(dev, Keysight_EDU36311A):
        ch_key = _EDU_CHANNEL_MAP.get(channel)
        if ch_key is None:
            raise ValueError(f"EDU36311A channel must be 1, 2, or 3. Got {channel!r} (type: {type(channel).__name__}).")
        dev.set_output_channel(ch_key, voltage, current_limit)
    elif isinstance(dev, MATRIX_MPS6010H) or (NI_PXIe_4139 is not None and isinstance(dev, NI_PXIe_4139)):
        dev.set_output_channel(channel, voltage, current_limit)
    else:
        raise TypeError(f"Unsupported PSU type: {type(dev).__name__}")
    return "OK"


def psu_enable_output(instrument_id: str, enabled: bool) -> str:
    """Enable or disable the PSU output.

    Returns:
        str: "OK"
    """
    _require_id("psu_enable_output", instrument_id)
    _require_bool(
        "psu_enable_output",
        "enabled",
        enabled,
        lab_hint=(
            "In LabVIEW: place a True/False Constant from Programming > "
            "Boolean and wire it into the second parameter slot of the "
            "Python Node. An unwired Boolean terminal silently defaults to "
            "False, which disables the PSU output."
        ),
    )
    dev = _get_typed(instrument_id, _PSU_CLASSES)
    dev.enable_output(enabled)
    return "OK"


def psu_measure_voltage(instrument_id: str, channel: int) -> float:
    """Measure voltage on a PSU channel.

    Returns:
        float: Measured voltage in volts.
    """
    _require_id("psu_measure_voltage", instrument_id)
    _require_channel("psu_measure_voltage", channel)
    dev = _get_typed(instrument_id, _PSU_CLASSES)
    if isinstance(dev, HP_E3631A):
        ch = _HP_CHANNEL_MAP.get(channel)
        if ch is None:
            raise ValueError(f"HP_E3631A channel must be 1, 2, or 3. Got {channel!r} (type: {type(channel).__name__}).")
        return dev.measure_voltage(ch)
    elif isinstance(dev, Keysight_EDU36311A):
        ch_key = _EDU_CHANNEL_MAP.get(channel)
        if ch_key is None:
            raise ValueError(f"EDU36311A channel must be 1, 2, or 3. Got {channel!r} (type: {type(channel).__name__}).")
        return dev.measure_voltage(ch_key)
    elif isinstance(dev, MATRIX_MPS6010H) or (NI_PXIe_4139 is not None and isinstance(dev, NI_PXIe_4139)):
        return dev.measure_voltage()
    raise TypeError(f"Unsupported PSU type: {type(dev).__name__}")


def psu_measure_current(instrument_id: str, channel: int) -> float:
    """Measure current on a PSU channel.

    Returns:
        float: Measured current in amps.
    """
    _require_id("psu_measure_current", instrument_id)
    _require_channel("psu_measure_current", channel)
    dev = _get_typed(instrument_id, _PSU_CLASSES)
    if isinstance(dev, HP_E3631A):
        ch = _HP_CHANNEL_MAP.get(channel)
        if ch is None:
            raise ValueError(f"HP_E3631A channel must be 1, 2, or 3. Got {channel!r} (type: {type(channel).__name__}).")
        return dev.measure_current(ch)
    elif isinstance(dev, Keysight_EDU36311A):
        ch_key = _EDU_CHANNEL_MAP.get(channel)
        if ch_key is None:
            raise ValueError(f"EDU36311A channel must be 1, 2, or 3. Got {channel!r} (type: {type(channel).__name__}).")
        return dev.measure_current(ch_key)
    elif isinstance(dev, MATRIX_MPS6010H) or (NI_PXIe_4139 is not None and isinstance(dev, NI_PXIe_4139)):
        return dev.measure_current()
    raise TypeError(f"Unsupported PSU type: {type(dev).__name__}")


def psu_disable_all(instrument_id: str) -> str:
    """Disable all PSU channels and set to safe state.

    Returns:
        str: "OK"
    """
    _require_id("psu_disable_all", instrument_id)
    dev = _get_typed(instrument_id, _PSU_CLASSES)
    dev.disable_all_channels()
    return "OK"


def psu_get_voltage_setpoint(instrument_id: str, channel: int) -> float:
    """Read back the configured voltage setpoint without enabling output.

    Useful before psu_enable_output to verify what will be applied.

    Returns:
        float: Voltage setpoint in volts.
    """
    _require_id("psu_get_voltage_setpoint", instrument_id)
    _require_channel("psu_get_voltage_setpoint", channel)
    dev = _get_typed(instrument_id, _PSU_CLASSES)
    if isinstance(dev, HP_E3631A):
        ch = _HP_CHANNEL_MAP.get(channel)
        if ch is None:
            raise ValueError(f"HP_E3631A channel must be 1, 2, or 3. Got {channel!r} (type: {type(channel).__name__}).")
        return float(dev.get_voltage_setpoint(ch))
    if isinstance(dev, Keysight_EDU36311A):
        ch_key = _EDU_CHANNEL_MAP.get(channel)
        if ch_key is None:
            raise ValueError(f"EDU36311A channel must be 1, 2, or 3. Got {channel!r} (type: {type(channel).__name__}).")
        return float(dev.get_voltage_setpoint(ch_key))
    if isinstance(dev, MATRIX_MPS6010H) or (NI_PXIe_4139 is not None and isinstance(dev, NI_PXIe_4139)):
        return float(dev.get_voltage_setpoint())
    raise TypeError(f"Unsupported PSU type: {type(dev).__name__}")


def psu_get_current_limit(instrument_id: str, channel: int) -> float:
    """Read back the configured current limit. Returns amps."""
    _require_id("psu_get_current_limit", instrument_id)
    _require_channel("psu_get_current_limit", channel)
    dev = _get_typed(instrument_id, _PSU_CLASSES)
    if isinstance(dev, HP_E3631A):
        ch = _HP_CHANNEL_MAP.get(channel)
        if ch is None:
            raise ValueError(f"HP_E3631A channel must be 1, 2, or 3. Got {channel!r} (type: {type(channel).__name__}).")
        return float(dev.get_current_limit(ch))
    if isinstance(dev, Keysight_EDU36311A):
        ch_key = _EDU_CHANNEL_MAP.get(channel)
        if ch_key is None:
            raise ValueError(f"EDU36311A channel must be 1, 2, or 3. Got {channel!r} (type: {type(channel).__name__}).")
        return float(dev.get_current_limit(ch_key))
    if isinstance(dev, MATRIX_MPS6010H) or (NI_PXIe_4139 is not None and isinstance(dev, NI_PXIe_4139)):
        return float(dev.get_current_limit())
    raise TypeError(f"Unsupported PSU type: {type(dev).__name__}")


def psu_get_output_state(instrument_id: str) -> bool:
    """Read back whether the PSU output is enabled. True == enabled.

    For multi-channel PSUs this is the master output state (shared by all
    channels on HP_E3631A and EDU36311A).
    """
    _require_id("psu_get_output_state", instrument_id)
    dev = _get_typed(instrument_id, _PSU_CLASSES)
    return bool(dev.get_output_state())


def psu_get_error(instrument_id: str) -> str:
    """Read and clear the PSU SCPI error queue. Returns a vendor-specific
    string (e.g. '+0,"No error"' on HP/Keysight)."""
    _require_id("psu_get_error", instrument_id)
    dev = _get_typed(instrument_id, _PSU_CLASSES)
    return str(dev.get_error())


# =========================================================================
# DMM operations
# =========================================================================


def dmm_measure_dc_voltage(instrument_id: str) -> float:
    """Measure DC voltage."""
    _require_id("dmm_measure_dc_voltage", instrument_id)
    dev = _get_typed(instrument_id, _DMM_CLASSES)
    return dev.measure_dc_voltage()


def dmm_measure_ac_voltage(instrument_id: str) -> float:
    """Measure AC voltage."""
    _require_id("dmm_measure_ac_voltage", instrument_id)
    dev = _get_typed(instrument_id, _DMM_CLASSES)
    return dev.measure_ac_voltage()


def dmm_measure_dc_current(instrument_id: str) -> float:
    """Measure DC current."""
    _require_id("dmm_measure_dc_current", instrument_id)
    dev = _get_typed(instrument_id, _DMM_CLASSES)
    return dev.measure_dc_current()


def dmm_measure_resistance_2w(instrument_id: str) -> float:
    """Measure 2-wire resistance."""
    _require_id("dmm_measure_resistance_2w", instrument_id)
    dev = _get_typed(instrument_id, _DMM_CLASSES)
    return dev.measure_resistance_2wire()


def dmm_measure_resistance_4w(instrument_id: str) -> float:
    """Measure 4-wire resistance."""
    _require_id("dmm_measure_resistance_4w", instrument_id)
    dev = _get_typed(instrument_id, _DMM_CLASSES)
    return dev.measure_resistance_4wire()


def dmm_measure_frequency(instrument_id: str) -> float:
    """Measure frequency."""
    _require_id("dmm_measure_frequency", instrument_id)
    dev = _get_typed(instrument_id, _DMM_CLASSES)
    return dev.measure_frequency()


def dmm_measure_diode(instrument_id: str) -> float:
    """Measure diode forward voltage."""
    _require_id("dmm_measure_diode", instrument_id)
    dev = _get_typed(instrument_id, _DMM_CLASSES)
    return dev.measure_diode()


# DMM configure_* family
#
# The drivers have heterogeneous signatures:
#   HP_34401A         -> configure_*(range_val="DEF", resolution="DEF", nplc=None)
#   Keysight_EDU34450A-> configure_*(range_val="DEF", resolution="DEF)
#   Owon_XDM1041      -> configure_*(range_val=None)
#
# LabVIEW Numeric terminals can't easily pass the "DEF" string sentinel, so
# the bridge wrappers accept floats with a `-1.0` sentinel meaning
# "instrument default". Pass an actual numeric range (e.g. 0.1 for the 100mV
# range) or -1.0 for autorange.


def _dmm_def(value: float):
    """Translate the -1.0 sentinel into the 'DEF' string SCPI keyword.

    LabVIEW unwired DBL terminal -> 0.0 - which means "explicit 0 range",
    not "instrument default". The bridge requires -1.0 as the explicit
    "use instrument default" sentinel. Anything strictly less than zero
    becomes "DEF"; anything >= 0 is passed through as a float.
    """
    return value if value >= 0 else "DEF"


def _dmm_nplc(value: float):
    """Translate -1.0 sentinel into None (skip NPLC configuration)."""
    return value if value > 0 else None


def _dmm_owon_range(value: float):
    """Owon driver expects float | None - translate -1 / 0 sentinel."""
    return value if value > 0 else None


def dmm_configure_dc_voltage(
    instrument_id: str,
    range_val: float = -1.0,
    resolution: float = -1.0,
    nplc: float = -1.0,
) -> str:
    """Configure DMM for DC voltage measurement.

    Args:
        instrument_id: ID returned by open_dmm.
        range_val: Voltage range in volts (e.g. 0.1 for 100 mV, 10.0 for 10 V).
            Pass -1.0 for instrument default (typically autorange).
        resolution: Resolution in volts (e.g. 0.0001 for 100 uV). Pass -1.0
            for instrument default. Ignored on Owon XDM1041.
        nplc: Integration time in Power Line Cycles (0.02, 0.2, 1, 10, 100).
            Higher = more noise rejection, slower. Pass -1.0 to skip NPLC
            configuration. Only takes effect on HP_34401A; ignored on
            Keysight_EDU34450A and Owon_XDM1041 which don't expose NPLC.

    Returns:
        str: "OK"
    """
    _require_id("dmm_configure_dc_voltage", instrument_id)
    _require_number("dmm_configure_dc_voltage", "range_val", range_val)
    _require_number("dmm_configure_dc_voltage", "resolution", resolution)
    _require_number("dmm_configure_dc_voltage", "nplc", nplc)
    dev = _get_typed(instrument_id, _DMM_CLASSES)
    if isinstance(dev, HP_34401A):
        dev.configure_dc_voltage(range_val=_dmm_def(range_val), resolution=_dmm_def(resolution), nplc=_dmm_nplc(nplc))
    elif isinstance(dev, Keysight_EDU34450A):
        dev.configure_dc_voltage(range_val=_dmm_def(range_val), resolution=_dmm_def(resolution))
    elif isinstance(dev, Owon_XDM1041):
        dev.configure_dc_voltage(range_val=_dmm_owon_range(range_val))
    else:
        raise TypeError(f"Unsupported DMM type: {type(dev).__name__}")
    return "OK"


def dmm_configure_ac_voltage(instrument_id: str, range_val: float = -1.0, resolution: float = -1.0) -> str:
    """Configure DMM for AC voltage measurement. See dmm_configure_dc_voltage
    for argument semantics. AC paths do not accept NPLC on any of the
    supported DMMs."""
    _require_id("dmm_configure_ac_voltage", instrument_id)
    _require_number("dmm_configure_ac_voltage", "range_val", range_val)
    _require_number("dmm_configure_ac_voltage", "resolution", resolution)
    dev = _get_typed(instrument_id, _DMM_CLASSES)
    if isinstance(dev, (HP_34401A, Keysight_EDU34450A)):
        dev.configure_ac_voltage(range_val=_dmm_def(range_val), resolution=_dmm_def(resolution))
    elif isinstance(dev, Owon_XDM1041):
        dev.configure_ac_voltage(range_val=_dmm_owon_range(range_val))
    else:
        raise TypeError(f"Unsupported DMM type: {type(dev).__name__}")
    return "OK"


def dmm_configure_dc_current(
    instrument_id: str,
    range_val: float = -1.0,
    resolution: float = -1.0,
    nplc: float = -1.0,
) -> str:
    """Configure DMM for DC current measurement. See dmm_configure_dc_voltage
    for argument semantics."""
    _require_id("dmm_configure_dc_current", instrument_id)
    _require_number("dmm_configure_dc_current", "range_val", range_val)
    _require_number("dmm_configure_dc_current", "resolution", resolution)
    _require_number("dmm_configure_dc_current", "nplc", nplc)
    dev = _get_typed(instrument_id, _DMM_CLASSES)
    if isinstance(dev, HP_34401A):
        dev.configure_dc_current(range_val=_dmm_def(range_val), resolution=_dmm_def(resolution), nplc=_dmm_nplc(nplc))
    elif isinstance(dev, Keysight_EDU34450A):
        dev.configure_dc_current(range_val=_dmm_def(range_val), resolution=_dmm_def(resolution))
    elif isinstance(dev, Owon_XDM1041):
        dev.configure_dc_current(range_val=_dmm_owon_range(range_val))
    else:
        raise TypeError(f"Unsupported DMM type: {type(dev).__name__}")
    return "OK"


def dmm_configure_ac_current(instrument_id: str, range_val: float = -1.0, resolution: float = -1.0) -> str:
    """Configure DMM for AC current measurement."""
    _require_id("dmm_configure_ac_current", instrument_id)
    _require_number("dmm_configure_ac_current", "range_val", range_val)
    _require_number("dmm_configure_ac_current", "resolution", resolution)
    dev = _get_typed(instrument_id, _DMM_CLASSES)
    if isinstance(dev, (HP_34401A, Keysight_EDU34450A)):
        dev.configure_ac_current(range_val=_dmm_def(range_val), resolution=_dmm_def(resolution))
    elif isinstance(dev, Owon_XDM1041):
        dev.configure_ac_current(range_val=_dmm_owon_range(range_val))
    else:
        raise TypeError(f"Unsupported DMM type: {type(dev).__name__}")
    return "OK"


def dmm_configure_resistance_2w(
    instrument_id: str,
    range_val: float = -1.0,
    resolution: float = -1.0,
    nplc: float = -1.0,
) -> str:
    """Configure DMM for 2-wire resistance measurement."""
    _require_id("dmm_configure_resistance_2w", instrument_id)
    _require_number("dmm_configure_resistance_2w", "range_val", range_val)
    _require_number("dmm_configure_resistance_2w", "resolution", resolution)
    _require_number("dmm_configure_resistance_2w", "nplc", nplc)
    dev = _get_typed(instrument_id, _DMM_CLASSES)
    if isinstance(dev, HP_34401A):
        dev.configure_resistance_2wire(
            range_val=_dmm_def(range_val), resolution=_dmm_def(resolution), nplc=_dmm_nplc(nplc)
        )
    elif isinstance(dev, Keysight_EDU34450A):
        dev.configure_resistance_2wire(range_val=_dmm_def(range_val), resolution=_dmm_def(resolution))
    elif isinstance(dev, Owon_XDM1041):
        dev.configure_resistance_2wire(range_val=_dmm_owon_range(range_val))
    else:
        raise TypeError(f"Unsupported DMM type: {type(dev).__name__}")
    return "OK"


def dmm_configure_resistance_4w(
    instrument_id: str,
    range_val: float = -1.0,
    resolution: float = -1.0,
    nplc: float = -1.0,
) -> str:
    """Configure DMM for 4-wire (Kelvin) resistance measurement."""
    _require_id("dmm_configure_resistance_4w", instrument_id)
    _require_number("dmm_configure_resistance_4w", "range_val", range_val)
    _require_number("dmm_configure_resistance_4w", "resolution", resolution)
    _require_number("dmm_configure_resistance_4w", "nplc", nplc)
    dev = _get_typed(instrument_id, _DMM_CLASSES)
    if isinstance(dev, HP_34401A):
        dev.configure_resistance_4wire(
            range_val=_dmm_def(range_val), resolution=_dmm_def(resolution), nplc=_dmm_nplc(nplc)
        )
    elif isinstance(dev, Keysight_EDU34450A):
        dev.configure_resistance_4wire(range_val=_dmm_def(range_val), resolution=_dmm_def(resolution))
    elif isinstance(dev, Owon_XDM1041):
        dev.configure_resistance_4wire(range_val=_dmm_owon_range(range_val))
    else:
        raise TypeError(f"Unsupported DMM type: {type(dev).__name__}")
    return "OK"


def dmm_read(instrument_id: str) -> float:
    """Trigger a measurement using the currently-configured DMM mode and
    return the result. Use after dmm_configure_*."""
    _require_id("dmm_read", instrument_id)
    dev = _get_typed(instrument_id, _DMM_CLASSES)
    if hasattr(dev, "read"):
        return float(dev.read())
    if hasattr(dev, "measure"):
        return float(dev.measure())
    raise AttributeError(f"DMM {type(dev).__name__} exposes neither read() nor measure().")


def dmm_fetch(instrument_id: str) -> float:
    """Return the last measurement without triggering a new one. Only
    supported on HP_34401A and Keysight_EDU34450A; raises on Owon."""
    _require_id("dmm_fetch", instrument_id)
    dev = _get_typed(instrument_id, _DMM_CLASSES)
    if not hasattr(dev, "fetch"):
        raise AttributeError(f"DMM {type(dev).__name__} does not support fetch(). Use dmm_read instead.")
    return float(dev.fetch())


def dmm_get_error(instrument_id: str) -> str:
    """Read and clear the DMM's SCPI error queue. Returns a vendor-specific
    string. Useful from LabVIEW for first-failure debugging."""
    _require_id("dmm_get_error", instrument_id)
    dev = _get_typed(instrument_id, _DMM_CLASSES)
    return str(dev.get_error())


# =========================================================================
# AWG operations
# =========================================================================


def awg_set_waveform(
    instrument_id: str,
    channel: int,
    wave_type: str,
    frequency: float,
    amplitude: float,
    offset: float,
) -> str:
    """Set waveform type and parameters on an AWG channel.

    Args:
        wave_type: Waveform type string (e.g. "SIN", "SQU", "RAMP", "DC", "sine", "square").
            Keysight/BK use SCPI names (SIN, SQU, RAMP, PULS, DC).
            JDS6600 uses lowercase names (sine, square, triangle, pulse, dc).

    Returns:
        str: "OK"
    """
    _require_id("awg_set_waveform", instrument_id)
    _require_channel("awg_set_waveform", channel, valid=(1, 2))
    _require_str("awg_set_waveform", "wave_type", wave_type)
    _require_number("awg_set_waveform", "frequency", frequency)
    _require_number("awg_set_waveform", "amplitude", amplitude)
    _require_number("awg_set_waveform", "offset", offset)
    dev = _get_typed(instrument_id, _AWG_CLASSES)
    if isinstance(dev, JDS6600_Generator):
        dev.set_waveform(channel, wave_type)
        dev.set_frequency(channel, frequency)
        dev.set_amplitude(channel, amplitude)
        dev.set_offset(channel, offset)
    else:
        dev.set_waveform(channel, wave_type, frequency=frequency, amplitude=amplitude, offset=offset)
    return "OK"


def awg_set_frequency(instrument_id: str, channel: int, frequency: float) -> str:
    """Set frequency on an AWG channel.

    Returns:
        str: "OK"
    """
    _require_id("awg_set_frequency", instrument_id)
    _require_channel("awg_set_frequency", channel, valid=(1, 2))
    _require_number("awg_set_frequency", "frequency", frequency)
    dev = _get_typed(instrument_id, _AWG_CLASSES)
    dev.set_frequency(channel, frequency)
    return "OK"


def awg_set_amplitude(instrument_id: str, channel: int, amplitude: float) -> str:
    """Set amplitude (Vpp) on an AWG channel.

    Returns:
        str: "OK"
    """
    _require_id("awg_set_amplitude", instrument_id)
    _require_channel("awg_set_amplitude", channel, valid=(1, 2))
    _require_number("awg_set_amplitude", "amplitude", amplitude)
    dev = _get_typed(instrument_id, _AWG_CLASSES)
    dev.set_amplitude(channel, amplitude)
    return "OK"


def awg_set_dc_output(instrument_id: str, channel: int, voltage: float) -> str:
    """Set DC output on an AWG channel.

    Returns:
        str: "OK"
    """
    _require_id("awg_set_dc_output", instrument_id)
    _require_channel("awg_set_dc_output", channel, valid=(1, 2))
    _require_number("awg_set_dc_output", "voltage", voltage)
    dev = _get_typed(instrument_id, _AWG_CLASSES)
    if isinstance(dev, JDS6600_Generator):
        dev.set_waveform(channel, "dc")
        dev.set_offset(channel, voltage)
    else:
        dev.set_dc_output(channel, voltage)
    return "OK"


def awg_enable_output(instrument_id: str, channel: int, enabled: bool) -> str:
    """Enable or disable output on an AWG channel.

    Returns:
        str: "OK"
    """
    _require_id("awg_enable_output", instrument_id)
    _require_channel("awg_enable_output", channel, valid=(1, 2))
    _require_bool("awg_enable_output", "enabled", enabled)
    dev = _get_typed(instrument_id, _AWG_CLASSES)
    if isinstance(dev, JDS6600_Generator):
        if channel == 1:
            dev.enable_output(ch1=enabled)
        else:
            dev.enable_output(ch2=enabled)
    else:
        dev.enable_output(channel, enabled)
    return "OK"


def awg_disable_all(instrument_id: str) -> str:
    """Disable all AWG outputs and set to safe state.

    Returns:
        str: "OK"
    """
    _require_id("awg_disable_all", instrument_id)
    dev = _get_typed(instrument_id, _AWG_CLASSES)
    if isinstance(dev, JDS6600_Generator):
        dev.disable_output()
    else:
        dev.disable_all_channels()
    return "OK"


def awg_set_offset(instrument_id: str, channel: int, offset: float) -> str:
    """Set DC offset (volts) on an AWG channel independently of the
    current waveform settings."""
    _require_id("awg_set_offset", instrument_id)
    _require_channel("awg_set_offset", channel, valid=(1, 2))
    _require_number("awg_set_offset", "offset", offset)
    dev = _get_typed(instrument_id, _AWG_CLASSES)
    dev.set_offset(channel, offset)
    return "OK"


def awg_get_amplitude(instrument_id: str, channel: int) -> float:
    """Read back the amplitude (Vpp) on an AWG channel."""
    _require_id("awg_get_amplitude", instrument_id)
    _require_channel("awg_get_amplitude", channel, valid=(1, 2))
    dev = _get_typed(instrument_id, _AWG_CLASSES)
    return float(dev.get_amplitude(channel))


def awg_get_offset(instrument_id: str, channel: int) -> float:
    """Read back the DC offset on an AWG channel."""
    _require_id("awg_get_offset", instrument_id)
    _require_channel("awg_get_offset", channel, valid=(1, 2))
    dev = _get_typed(instrument_id, _AWG_CLASSES)
    return float(dev.get_offset(channel))


def awg_get_frequency(instrument_id: str, channel: int) -> float:
    """Read back the frequency on an AWG channel."""
    _require_id("awg_get_frequency", instrument_id)
    _require_channel("awg_get_frequency", channel, valid=(1, 2))
    dev = _get_typed(instrument_id, _AWG_CLASSES)
    return float(dev.get_frequency(channel))


def awg_get_output_state(instrument_id: str, channel: int) -> bool:
    """Read back whether the AWG output for a channel is enabled."""
    _require_id("awg_get_output_state", instrument_id)
    _require_channel("awg_get_output_state", channel, valid=(1, 2))
    dev = _get_typed(instrument_id, _AWG_CLASSES)
    return bool(dev.get_output_state(channel))


def awg_get_error(instrument_id: str) -> str:
    """Read and clear the AWG SCPI error queue. Returns a vendor-specific
    string. JDS6600 has no error queue so this returns a 'not supported'
    string for that device."""
    _require_id("awg_get_error", instrument_id)
    dev = _get_typed(instrument_id, _AWG_CLASSES)
    if not hasattr(dev, "get_error"):
        return f"not supported on {type(dev).__name__}"
    return str(dev.get_error())


# =========================================================================
# Scope operations
# =========================================================================


def scope_run(instrument_id: str) -> str:
    """Start oscilloscope acquisition.

    Returns:
        str: "OK"
    """
    _require_id("scope_run", instrument_id)
    dev = _get_typed(instrument_id, _SCOPE_CLASSES)
    dev.run()
    return "OK"


def scope_stop(instrument_id: str) -> str:
    """Stop oscilloscope acquisition.

    Returns:
        str: "OK"
    """
    _require_id("scope_stop", instrument_id)
    dev = _get_typed(instrument_id, _SCOPE_CLASSES)
    dev.stop()
    return "OK"


def scope_single(instrument_id: str) -> str:
    """Arm single-shot acquisition.

    Returns:
        str: "OK"
    """
    _require_id("scope_single", instrument_id)
    dev = _get_typed(instrument_id, _SCOPE_CLASSES)
    dev.single()
    return "OK"


def scope_set_vertical_scale(instrument_id: str, channel: int, volts_per_div: float) -> str:
    """Set vertical scale for a scope channel.

    Returns:
        str: "OK"
    """
    _require_id("scope_set_vertical_scale", instrument_id)
    _require_channel("scope_set_vertical_scale", channel, max_ch=4)
    _require_number("scope_set_vertical_scale", "volts_per_div", volts_per_div)
    _require_positive("scope_set_vertical_scale", "volts_per_div", volts_per_div)
    dev = _get_typed(instrument_id, _SCOPE_CLASSES)
    dev.set_vertical_scale(channel, volts_per_div)
    return "OK"


def scope_set_timebase(instrument_id: str, time_per_div: float) -> str:
    """Set horizontal timebase (seconds per division).

    Returns:
        str: "OK"
    """
    _require_id("scope_set_timebase", instrument_id)
    _require_number("scope_set_timebase", "time_per_div", time_per_div)
    _require_positive("scope_set_timebase", "time_per_div", time_per_div)
    dev = _get_typed(instrument_id, _SCOPE_CLASSES)
    dev.set_horizontal_scale(time_per_div)
    return "OK"


def scope_measure_vpp(instrument_id: str, channel: int) -> float:
    """Measure peak-to-peak voltage on a scope channel."""
    _require_id("scope_measure_vpp", instrument_id)
    _require_channel("scope_measure_vpp", channel, max_ch=4)
    dev = _get_typed(instrument_id, _SCOPE_CLASSES)
    if isinstance(dev, Tektronix_MSO2024):
        return dev.measure_peak_to_peak(channel)
    else:
        return dev.measure_vpp(channel)


def scope_measure_frequency(instrument_id: str, channel: int) -> float:
    """Measure frequency on a scope channel."""
    _require_id("scope_measure_frequency", instrument_id)
    _require_channel("scope_measure_frequency", channel, max_ch=4)
    dev = _get_typed(instrument_id, _SCOPE_CLASSES)
    return dev.measure_frequency(channel)


def scope_measure_vrms(instrument_id: str, channel: int) -> float:
    """Measure RMS voltage on a scope channel."""
    _require_id("scope_measure_vrms", instrument_id)
    _require_channel("scope_measure_vrms", channel, max_ch=4)
    dev = _get_typed(instrument_id, _SCOPE_CLASSES)
    if isinstance(dev, Tektronix_MSO2024):
        return dev.measure_rms(channel)
    else:
        return dev.measure_vrms(channel)


# =========================================================================
# EV2300 operations
# =========================================================================


def ev2300_wait_for_bq(instrument_id: str, timeout_s: float = 30.0) -> str:
    """Poll the BQ76920 over I2C until it acknowledges, or timeout.

    Blocks the calling thread until a read of CC_CFG (reg 0x0B) succeeds
    at either possible BQ address (0x08 or 0x18), or ``timeout_s`` seconds
    elapse. Use this after ``open_ev2300`` if the EVM may have been
    BOOT-pressed during the open call -- the function returns as soon as
    the chip wakes up.

    Args:
        instrument_id: ID returned by open_ev2300.
        timeout_s: Maximum seconds to wait (default 30).

    Returns:
        str: "OK" once the BQ ACKs.

    Raises:
        TimeoutError: If the BQ does not respond within timeout_s.
    """
    _require_id("ev2300_wait_for_bq", instrument_id)
    _require_number("ev2300_wait_for_bq", "timeout_s", timeout_s)
    _require_positive("ev2300_wait_for_bq", "timeout_s", timeout_s)
    dev = _get_typed(instrument_id, _EV2300_CLASSES)
    dev.wait_for_bq(timeout_s=timeout_s)
    return "OK"


def ev2300_read_byte(instrument_id: str, i2c_addr: int, register: int) -> int:
    """Read a single byte from an I2C register via EV2300.

    Returns:
        int: The byte value (0-255).
    """
    _require_id("ev2300_read_byte", instrument_id)
    _require_i2c_addr("ev2300_read_byte", i2c_addr)
    _require_byte("ev2300_read_byte", "register", register)
    dev = _get_typed(instrument_id, _EV2300_CLASSES)
    result = dev.read_byte(i2c_addr, register)
    if not result.get("ok"):
        raise RuntimeError(result.get("status_text", "EV2300 read_byte failed"))
    return result["value"]


def ev2300_write_byte(instrument_id: str, i2c_addr: int, register: int, value: int) -> str:
    """Write a single byte to an I2C register via EV2300.

    Returns:
        str: "OK"
    """
    _require_id("ev2300_write_byte", instrument_id)
    _require_i2c_addr("ev2300_write_byte", i2c_addr)
    _require_byte("ev2300_write_byte", "register", register)
    _require_byte("ev2300_write_byte", "value", value)
    dev = _get_typed(instrument_id, _EV2300_CLASSES)
    result = dev.write_byte(i2c_addr, register, value)
    if not result.get("ok"):
        raise RuntimeError(result.get("status_text", "EV2300 write_byte failed"))
    return "OK"


def ev2300_read_word(instrument_id: str, i2c_addr: int, register: int) -> int:
    """Read a 16-bit word from an I2C register via EV2300.

    Returns:
        int: The 16-bit value (0-65535).
    """
    _require_id("ev2300_read_word", instrument_id)
    _require_i2c_addr("ev2300_read_word", i2c_addr)
    _require_byte("ev2300_read_word", "register", register)
    dev = _get_typed(instrument_id, _EV2300_CLASSES)
    result = dev.read_word(i2c_addr, register)
    if not result.get("ok"):
        raise RuntimeError(result.get("status_text", "EV2300 read_word failed"))
    return result["value"]


def ev2300_write_word(instrument_id: str, i2c_addr: int, register: int, value: int) -> str:
    """Write a 16-bit word to an I2C register via EV2300.

    Returns:
        str: "OK"
    """
    _require_id("ev2300_write_word", instrument_id)
    _require_i2c_addr("ev2300_write_word", i2c_addr)
    _require_byte("ev2300_write_word", "register", register)
    _require_word("ev2300_write_word", "value", value)
    dev = _get_typed(instrument_id, _EV2300_CLASSES)
    result = dev.write_word(i2c_addr, register, value)
    if not result.get("ok"):
        raise RuntimeError(result.get("status_text", "EV2300 write_word failed"))
    return "OK"


def ev2300_read_block(instrument_id: str, i2c_addr: int, register: int) -> str:
    """Read a block of bytes from an I2C register via EV2300.

    Returns:
        str: JSON list of integers (e.g. "[16, 32, 48]").
    """
    _require_id("ev2300_read_block", instrument_id)
    _require_i2c_addr("ev2300_read_block", i2c_addr)
    _require_byte("ev2300_read_block", "register", register)
    dev = _get_typed(instrument_id, _EV2300_CLASSES)
    result = dev.read_block(i2c_addr, register)
    if not result.get("ok"):
        raise RuntimeError(result.get("status_text", "EV2300 read_block failed"))
    return json.dumps(list(result["data"]))


def ev2300_write_block(instrument_id: str, i2c_addr: int, register: int, data_json: str) -> str:
    """Write a block of bytes to an I2C register via EV2300.

    Args:
        data_json: JSON list of integers (e.g. "[16, 32, 48]").

    Returns:
        str: "OK"
    """
    _require_id("ev2300_write_block", instrument_id)
    _require_i2c_addr("ev2300_write_block", i2c_addr)
    _require_byte("ev2300_write_block", "register", register)
    _require_str("ev2300_write_block", "data_json", data_json)
    try:
        decoded = json.loads(data_json)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"ev2300_write_block: 'data_json' must be a JSON list of byte "
            f"integers (0..255), e.g. '[16, 32, 48]'. Got {data_json!r}; "
            f"JSON parse error: {exc}."
        ) from None
    if not isinstance(decoded, list):
        raise ValueError(
            f"ev2300_write_block: 'data_json' must decode to a list of byte integers, got {type(decoded).__name__}."
        )
    for i, b in enumerate(decoded):
        if isinstance(b, bool) or not isinstance(b, int) or not (0 <= b <= 0xFF):
            raise ValueError(
                f"ev2300_write_block: data_json[{i}] must be an integer 0..255, got {b!r} (type: {type(b).__name__})."
            )
    data = bytes(decoded)
    dev = _get_typed(instrument_id, _EV2300_CLASSES)
    result = dev.write_block(i2c_addr, register, data)
    if not result.get("ok"):
        raise RuntimeError(result.get("status_text", "EV2300 write_block failed"))
    return "OK"


def ev2300_get_device_info(instrument_id: str) -> str:
    """Get EV2300 device info.

    Returns:
        str: JSON object with device info.
    """
    _require_id("ev2300_get_device_info", instrument_id)
    dev = _get_typed(instrument_id, _EV2300_CLASSES)
    info = dev.get_device_info()
    return json.dumps(info)


# BQ76920 SYS_STAT bit definitions (register 0x00, write-1-to-clear per
# datasheet SLUSBK2I section 7.5). Mirrored from the firmware header
# BQ76920_Bridge/Core/Inc/bq76920.h to ensure host and firmware agree.
_BQ_SYS_STAT_BITS = {
    7: "CC_READY",
    5: "DEVICE_XREADY",
    4: "OVRD_ALERT",
    3: "UV",
    2: "OV",
    1: "SCD",
    0: "OCD",
}
# Bits that are latched faults (vs. CC_READY which auto-asserts on next CC
# sample, vs. OVRD_ALERT which mirrors the ALERT pin state).
_BQ_SYS_STAT_FAULT_BITS = {5, 3, 2, 1, 0}


def ev2300_read_sys_stat(instrument_id: str, i2c_addr: int = 0x08) -> str:
    """Read and decode the BQ76920 SYS_STAT register (0x00).

    Returns a JSON object describing every bit, e.g.::

        {
          "raw": 132,                    # 0x84
          "raw_hex": "0x84",
          "bits": {"CC_READY": true, "DEVICE_XREADY": false,
                   "OVRD_ALERT": false, "UV": false, "OV": true,
                   "SCD": false, "OCD": false},
          "active_bits": ["CC_READY", "OV"],
          "active_faults": ["OV"]
        }

    Bit positions per BQ76920 datasheet SLUSBK2I section 7.5. Use this from
    LabVIEW to surface specific fault conditions instead of an opaque
    integer.

    Args:
        instrument_id: ID returned by open_ev2300.
        i2c_addr: BQ76920 I2C address (default 0x08; some variants 0x18).

    Returns:
        str: JSON object as documented above.
    """
    _require_id("ev2300_read_sys_stat", instrument_id)
    _require_i2c_addr("ev2300_read_sys_stat", i2c_addr)
    dev = _get_typed(instrument_id, _EV2300_CLASSES)
    result = dev.read_byte(i2c_addr, 0x00)
    if not result.get("ok"):
        raise RuntimeError(result.get("status_text", "EV2300 read SYS_STAT failed"))
    val = int(result["value"])
    bits = {name: bool(val & (1 << bit)) for bit, name in _BQ_SYS_STAT_BITS.items()}
    active_bits = [name for bit, name in sorted(_BQ_SYS_STAT_BITS.items(), reverse=True) if val & (1 << bit)]
    active_faults = [
        name
        for bit, name in sorted(_BQ_SYS_STAT_BITS.items(), reverse=True)
        if val & (1 << bit) and bit in _BQ_SYS_STAT_FAULT_BITS
    ]
    return json.dumps(
        {
            "raw": val,
            "raw_hex": f"0x{val:02X}",
            "bits": bits,
            "active_bits": active_bits,
            "active_faults": active_faults,
        }
    )


def ev2300_clear_bq_faults(instrument_id: str, i2c_addr: int = 0x08, mask: int = 0xFF) -> str:
    """Clear latched faults in BQ76920 SYS_STAT via write-1-to-clear.

    SYS_STAT (register 0x00) is W1C per datasheet SLUSBK2I section 7.5:
    a write byte does NOT replace the register contents, it clears each
    bit that is set to 1 in the written value. ``mask=0xFF`` clears every
    latched fault (and also CC_READY which simply re-asserts on the next
    CC sample so is harmless). To clear only OV without disturbing other
    bits, pass ``mask=0x04``.

    Note that a fault bit will re-latch immediately if the underlying
    condition is still true (e.g. OV will stay set while the cell voltage
    is above OV_TRIP, register 0x09). Read SYS_STAT after this call -- if
    a fault is still set, the chip is telling you the protection condition
    has not been resolved yet.

    Args:
        instrument_id: ID returned by open_ev2300.
        i2c_addr: BQ76920 I2C address (default 0x08).
        mask: Bit mask of which flags to clear (default 0xFF, clear all).

    Returns:
        str: "OK"
    """
    _require_id("ev2300_clear_bq_faults", instrument_id)
    _require_i2c_addr("ev2300_clear_bq_faults", i2c_addr)
    _require_byte("ev2300_clear_bq_faults", "mask", mask)
    dev = _get_typed(instrument_id, _EV2300_CLASSES)
    result = dev.write_byte(i2c_addr, 0x00, mask)
    if not result.get("ok"):
        raise RuntimeError(result.get("status_text", "EV2300 clear_bq_faults failed"))
    return "OK"


# =========================================================================
# SMU operations (NI PXIe-4139)
# =========================================================================


def smu_set_voltage_mode(instrument_id: str, voltage: float, current_limit: float) -> str:
    """Switch SMU to voltage mode and set voltage/current limit.

    Returns:
        str: "OK"
    """
    _require_id("smu_set_voltage_mode", instrument_id)
    _require_number("smu_set_voltage_mode", "voltage", voltage)
    _require_number("smu_set_voltage_mode", "current_limit", current_limit)
    dev = _get_typed(instrument_id, _SMU_CLASSES)
    dev.set_voltage_mode(voltage, current_limit)
    return "OK"


def smu_set_current_mode(instrument_id: str, current: float, voltage_limit: float) -> str:
    """Switch SMU to current mode and set current/voltage limit.

    Returns:
        str: "OK"
    """
    _require_id("smu_set_current_mode", instrument_id)
    _require_number("smu_set_current_mode", "current", current)
    _require_number("smu_set_current_mode", "voltage_limit", voltage_limit)
    dev = _get_typed(instrument_id, _SMU_CLASSES)
    dev.set_current_mode(current, voltage_limit)
    return "OK"


def smu_enable_output(instrument_id: str, enabled: bool) -> str:
    """Enable or disable SMU output.

    Returns:
        str: "OK"
    """
    _require_id("smu_enable_output", instrument_id)
    _require_bool("smu_enable_output", "enabled", enabled)
    dev = _get_typed(instrument_id, _SMU_CLASSES)
    dev.enable_output(enabled)
    return "OK"


def smu_measure_voltage(instrument_id: str) -> float:
    """Measure voltage on the SMU."""
    _require_id("smu_measure_voltage", instrument_id)
    dev = _get_typed(instrument_id, _SMU_CLASSES)
    return dev.measure_voltage()


def smu_measure_current(instrument_id: str) -> float:
    """Measure current on the SMU."""
    _require_id("smu_measure_current", instrument_id)
    dev = _get_typed(instrument_id, _SMU_CLASSES)
    return dev.measure_current()


# =========================================================================
# Generic / raw SCPI
# =========================================================================


def send_scpi(instrument_id: str, command: str) -> str:
    """Send a raw SCPI command (write only, no response).

    Note: Not supported on NI_PXIe_4139 (no-op).

    Returns:
        str: "OK"
    """
    _require_id("send_scpi", instrument_id)
    _require_str("send_scpi", "command", command)
    dev = _get(instrument_id)
    dev.send_command(command)
    return "OK"


def query_scpi(instrument_id: str, command: str) -> str:
    """Send a raw SCPI query and return the response string.

    Note: NI_PXIe_4139 returns an IDN-like string for any query.
    """
    _require_id("query_scpi", instrument_id)
    _require_str("query_scpi", "command", command)
    dev = _get(instrument_id)
    return dev.query(command)


def reset_instrument(instrument_id: str) -> str:
    """Send *RST to reset the instrument.

    Returns:
        str: "OK"
    """
    _require_id("reset_instrument", instrument_id)
    dev = _get(instrument_id)
    dev.reset()
    return "OK"


def get_instrument_type(instrument_id: str) -> str:
    """Return the category of the instrument.

    Returns:
        str: "psu", "dmm", "awg", "scope", "smu", "ev2300", or "unknown"
    """
    _require_id("get_instrument_type", instrument_id)
    dev = _get(instrument_id)
    return _CATEGORY_PREFIX.get(type(dev), "unknown")


def get_version() -> str:
    """Return the scpi-instrument-toolkit package version.

    Reads from importlib.metadata so the returned value always matches what
    pip installed - the package's ``__init__.py`` ``__version__`` was
    historically allowed to drift from ``pyproject.toml``, which meant
    LabVIEW students could see a stale version after upgrading. Falls back
    to ``__version__`` when running from source without an installed dist
    (e.g. inside a fresh clone with no ``pip install``).

    Returns:
        str: Version string (e.g. "1.0.65").
    """
    try:
        from importlib.metadata import PackageNotFoundError, version

        try:
            return version("scpi-instrument-toolkit")
        except PackageNotFoundError:
            pass
    except ImportError:
        pass
    from .. import __version__

    return __version__
