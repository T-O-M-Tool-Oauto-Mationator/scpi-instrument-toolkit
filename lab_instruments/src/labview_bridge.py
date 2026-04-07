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
"""

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
    """Retrieve a cached instrument or raise KeyError."""
    try:
        return _instruments[instrument_id]
    except KeyError:
        available = list(_instruments.keys()) or ["(none — open an instrument first)"]
        raise KeyError(f"No instrument with ID '{instrument_id}'. Open instruments: {available}") from None


def _get_typed(instrument_id: str, valid_types: tuple) -> object:
    """Retrieve a cached instrument and validate its type."""
    dev = _get(instrument_id)
    if not isinstance(dev, valid_types):
        expected = [c.__name__ for c in valid_types]
        raise TypeError(f"Instrument '{instrument_id}' is {type(dev).__name__}, expected one of {expected}")
    return dev


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
    if driver_name not in _DRIVER_MAP:
        raise ValueError(f"Unknown driver '{driver_name}'.")
    if not issubclass(_DRIVER_MAP[driver_name], _PSU_CLASSES):
        raise TypeError(f"'{driver_name}' is not a PSU driver.")
    return open_instrument(visa_address, driver_name)


def open_dmm(visa_address: str, driver_name: str) -> str:
    """Open a digital multimeter (validates driver is a DMM type)."""
    if driver_name not in _DRIVER_MAP:
        raise ValueError(f"Unknown driver '{driver_name}'.")
    if not issubclass(_DRIVER_MAP[driver_name], _DMM_CLASSES):
        raise TypeError(f"'{driver_name}' is not a DMM driver.")
    return open_instrument(visa_address, driver_name)


def open_awg(visa_address: str, driver_name: str) -> str:
    """Open a function generator (validates driver is an AWG type)."""
    if driver_name not in _DRIVER_MAP:
        raise ValueError(f"Unknown driver '{driver_name}'.")
    if not issubclass(_DRIVER_MAP[driver_name], _AWG_CLASSES):
        raise TypeError(f"'{driver_name}' is not an AWG driver.")
    return open_instrument(visa_address, driver_name)


def open_scope(visa_address: str, driver_name: str) -> str:
    """Open an oscilloscope (validates driver is a scope type)."""
    if driver_name not in _DRIVER_MAP:
        raise ValueError(f"Unknown driver '{driver_name}'.")
    if not issubclass(_DRIVER_MAP[driver_name], _SCOPE_CLASSES):
        raise TypeError(f"'{driver_name}' is not a scope driver.")
    return open_instrument(visa_address, driver_name)


def open_smu(visa_address: str, driver_name: str) -> str:
    """Open a source measure unit (validates driver is an SMU type)."""
    if not _SMU_CLASSES:
        raise ImportError("SMU support not available (nidcpower not installed).")
    if driver_name not in _DRIVER_MAP:
        raise ValueError(f"Unknown driver '{driver_name}'.")
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
    dev = _get_typed(instrument_id, _PSU_CLASSES)
    if isinstance(dev, HP_E3631A):
        ch = _HP_CHANNEL_MAP.get(channel)
        if ch is None:
            raise ValueError(f"HP_E3631A channel must be 1, 2, or 3. Got {channel}.")
        dev.set_voltage(ch, voltage)
    elif isinstance(dev, Keysight_EDU36311A):
        ch_key = _EDU_CHANNEL_MAP.get(channel)
        if ch_key is None:
            raise ValueError(f"EDU36311A channel must be 1, 2, or 3. Got {channel}.")
        dev.set_voltage(ch_key, voltage)
    elif isinstance(dev, MATRIX_MPS6010H) or NI_PXIe_4139 is not None and isinstance(dev, NI_PXIe_4139):
        dev.set_voltage(voltage)
    return "OK"


def psu_set_current_limit(instrument_id: str, channel: int, current: float) -> str:
    """Set the current limit on a PSU channel.

    Returns:
        str: "OK"
    """
    dev = _get_typed(instrument_id, _PSU_CLASSES)
    if isinstance(dev, HP_E3631A):
        ch = _HP_CHANNEL_MAP.get(channel)
        if ch is None:
            raise ValueError(f"HP_E3631A channel must be 1, 2, or 3. Got {channel}.")
        dev.set_current_limit(ch, current)
    elif isinstance(dev, Keysight_EDU36311A):
        ch_key = _EDU_CHANNEL_MAP.get(channel)
        if ch_key is None:
            raise ValueError(f"EDU36311A channel must be 1, 2, or 3. Got {channel}.")
        dev.set_current_limit(ch_key, current)
    elif isinstance(dev, MATRIX_MPS6010H) or NI_PXIe_4139 is not None and isinstance(dev, NI_PXIe_4139):
        dev.set_current_limit(current)
    return "OK"


def psu_set_output_channel(instrument_id: str, channel: int, voltage: float, current_limit: float) -> str:
    """Set voltage and current limit for a PSU channel in one call.

    Returns:
        str: "OK"
    """
    dev = _get_typed(instrument_id, _PSU_CLASSES)
    if isinstance(dev, HP_E3631A):
        ch = _HP_CHANNEL_MAP.get(channel)
        if ch is None:
            raise ValueError(f"HP_E3631A channel must be 1, 2, or 3. Got {channel}.")
        dev.set_output_channel(ch, voltage, current_limit)
    elif isinstance(dev, Keysight_EDU36311A):
        ch_key = _EDU_CHANNEL_MAP.get(channel)
        if ch_key is None:
            raise ValueError(f"EDU36311A channel must be 1, 2, or 3. Got {channel}.")
        dev.set_output_channel(ch_key, voltage, current_limit)
    elif isinstance(dev, MATRIX_MPS6010H) or NI_PXIe_4139 is not None and isinstance(dev, NI_PXIe_4139):
        dev.set_output_channel(channel, voltage, current_limit)
    return "OK"


def psu_enable_output(instrument_id: str, enabled: bool) -> str:
    """Enable or disable the PSU output.

    Returns:
        str: "OK"
    """
    dev = _get_typed(instrument_id, _PSU_CLASSES)
    dev.enable_output(enabled)
    return "OK"


def psu_measure_voltage(instrument_id: str, channel: int) -> float:
    """Measure voltage on a PSU channel.

    Returns:
        float: Measured voltage in volts.
    """
    dev = _get_typed(instrument_id, _PSU_CLASSES)
    if isinstance(dev, HP_E3631A):
        ch = _HP_CHANNEL_MAP.get(channel)
        if ch is None:
            raise ValueError(f"HP_E3631A channel must be 1, 2, or 3. Got {channel}.")
        return dev.measure_voltage(ch)
    elif isinstance(dev, Keysight_EDU36311A):
        ch_key = _EDU_CHANNEL_MAP.get(channel)
        if ch_key is None:
            raise ValueError(f"EDU36311A channel must be 1, 2, or 3. Got {channel}.")
        return dev.measure_voltage(ch_key)
    elif isinstance(dev, MATRIX_MPS6010H) or NI_PXIe_4139 is not None and isinstance(dev, NI_PXIe_4139):
        return dev.measure_voltage()
    raise TypeError(f"Unsupported PSU type: {type(dev).__name__}")


def psu_measure_current(instrument_id: str, channel: int) -> float:
    """Measure current on a PSU channel.

    Returns:
        float: Measured current in amps.
    """
    dev = _get_typed(instrument_id, _PSU_CLASSES)
    if isinstance(dev, HP_E3631A):
        ch = _HP_CHANNEL_MAP.get(channel)
        if ch is None:
            raise ValueError(f"HP_E3631A channel must be 1, 2, or 3. Got {channel}.")
        return dev.measure_current(ch)
    elif isinstance(dev, Keysight_EDU36311A):
        ch_key = _EDU_CHANNEL_MAP.get(channel)
        if ch_key is None:
            raise ValueError(f"EDU36311A channel must be 1, 2, or 3. Got {channel}.")
        return dev.measure_current(ch_key)
    elif isinstance(dev, MATRIX_MPS6010H) or NI_PXIe_4139 is not None and isinstance(dev, NI_PXIe_4139):
        return dev.measure_current()
    raise TypeError(f"Unsupported PSU type: {type(dev).__name__}")


def psu_disable_all(instrument_id: str) -> str:
    """Disable all PSU channels and set to safe state.

    Returns:
        str: "OK"
    """
    dev = _get_typed(instrument_id, _PSU_CLASSES)
    dev.disable_all_channels()
    return "OK"


# =========================================================================
# DMM operations
# =========================================================================


def dmm_measure_dc_voltage(instrument_id: str) -> float:
    """Measure DC voltage."""
    dev = _get_typed(instrument_id, _DMM_CLASSES)
    return dev.measure_dc_voltage()


def dmm_measure_ac_voltage(instrument_id: str) -> float:
    """Measure AC voltage."""
    dev = _get_typed(instrument_id, _DMM_CLASSES)
    return dev.measure_ac_voltage()


def dmm_measure_dc_current(instrument_id: str) -> float:
    """Measure DC current."""
    dev = _get_typed(instrument_id, _DMM_CLASSES)
    return dev.measure_dc_current()


def dmm_measure_resistance_2w(instrument_id: str) -> float:
    """Measure 2-wire resistance."""
    dev = _get_typed(instrument_id, _DMM_CLASSES)
    return dev.measure_resistance_2wire()


def dmm_measure_resistance_4w(instrument_id: str) -> float:
    """Measure 4-wire resistance."""
    dev = _get_typed(instrument_id, _DMM_CLASSES)
    return dev.measure_resistance_4wire()


def dmm_measure_frequency(instrument_id: str) -> float:
    """Measure frequency."""
    dev = _get_typed(instrument_id, _DMM_CLASSES)
    return dev.measure_frequency()


def dmm_measure_diode(instrument_id: str) -> float:
    """Measure diode forward voltage."""
    dev = _get_typed(instrument_id, _DMM_CLASSES)
    return dev.measure_diode()


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
    dev = _get_typed(instrument_id, _AWG_CLASSES)
    dev.set_frequency(channel, frequency)
    return "OK"


def awg_set_amplitude(instrument_id: str, channel: int, amplitude: float) -> str:
    """Set amplitude (Vpp) on an AWG channel.

    Returns:
        str: "OK"
    """
    dev = _get_typed(instrument_id, _AWG_CLASSES)
    dev.set_amplitude(channel, amplitude)
    return "OK"


def awg_set_dc_output(instrument_id: str, channel: int, voltage: float) -> str:
    """Set DC output on an AWG channel.

    Returns:
        str: "OK"
    """
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
    dev = _get_typed(instrument_id, _AWG_CLASSES)
    if isinstance(dev, JDS6600_Generator):
        dev.disable_output()
    else:
        dev.disable_all_channels()
    return "OK"


# =========================================================================
# Scope operations
# =========================================================================


def scope_run(instrument_id: str) -> str:
    """Start oscilloscope acquisition.

    Returns:
        str: "OK"
    """
    dev = _get_typed(instrument_id, _SCOPE_CLASSES)
    dev.run()
    return "OK"


def scope_stop(instrument_id: str) -> str:
    """Stop oscilloscope acquisition.

    Returns:
        str: "OK"
    """
    dev = _get_typed(instrument_id, _SCOPE_CLASSES)
    dev.stop()
    return "OK"


def scope_single(instrument_id: str) -> str:
    """Arm single-shot acquisition.

    Returns:
        str: "OK"
    """
    dev = _get_typed(instrument_id, _SCOPE_CLASSES)
    dev.single()
    return "OK"


def scope_set_vertical_scale(instrument_id: str, channel: int, volts_per_div: float) -> str:
    """Set vertical scale for a scope channel.

    Returns:
        str: "OK"
    """
    dev = _get_typed(instrument_id, _SCOPE_CLASSES)
    dev.set_vertical_scale(channel, volts_per_div)
    return "OK"


def scope_set_timebase(instrument_id: str, time_per_div: float) -> str:
    """Set horizontal timebase (seconds per division).

    Returns:
        str: "OK"
    """
    dev = _get_typed(instrument_id, _SCOPE_CLASSES)
    dev.set_horizontal_scale(time_per_div)
    return "OK"


def scope_measure_vpp(instrument_id: str, channel: int) -> float:
    """Measure peak-to-peak voltage on a scope channel."""
    dev = _get_typed(instrument_id, _SCOPE_CLASSES)
    if isinstance(dev, Tektronix_MSO2024):
        return dev.measure_peak_to_peak(channel)
    else:
        return dev.measure_vpp(channel)


def scope_measure_frequency(instrument_id: str, channel: int) -> float:
    """Measure frequency on a scope channel."""
    dev = _get_typed(instrument_id, _SCOPE_CLASSES)
    return dev.measure_frequency(channel)


def scope_measure_vrms(instrument_id: str, channel: int) -> float:
    """Measure RMS voltage on a scope channel."""
    dev = _get_typed(instrument_id, _SCOPE_CLASSES)
    if isinstance(dev, Tektronix_MSO2024):
        return dev.measure_rms(channel)
    else:
        return dev.measure_vrms(channel)


# =========================================================================
# EV2300 operations
# =========================================================================


def ev2300_read_byte(instrument_id: str, i2c_addr: int, register: int) -> int:
    """Read a single byte from an I2C register via EV2300.

    Returns:
        int: The byte value (0-255).
    """
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
    dev = _get_typed(instrument_id, _EV2300_CLASSES)
    data = bytes(json.loads(data_json))
    result = dev.write_block(i2c_addr, register, data)
    if not result.get("ok"):
        raise RuntimeError(result.get("status_text", "EV2300 write_block failed"))
    return "OK"


def ev2300_get_device_info(instrument_id: str) -> str:
    """Get EV2300 device info.

    Returns:
        str: JSON object with device info.
    """
    dev = _get_typed(instrument_id, _EV2300_CLASSES)
    info = dev.get_device_info()
    return json.dumps(info)


# =========================================================================
# SMU operations (NI PXIe-4139)
# =========================================================================


def smu_set_voltage_mode(instrument_id: str, voltage: float, current_limit: float) -> str:
    """Switch SMU to voltage mode and set voltage/current limit.

    Returns:
        str: "OK"
    """
    dev = _get_typed(instrument_id, _SMU_CLASSES)
    dev.set_voltage_mode(voltage, current_limit)
    return "OK"


def smu_set_current_mode(instrument_id: str, current: float, voltage_limit: float) -> str:
    """Switch SMU to current mode and set current/voltage limit.

    Returns:
        str: "OK"
    """
    dev = _get_typed(instrument_id, _SMU_CLASSES)
    dev.set_current_mode(current, voltage_limit)
    return "OK"


def smu_enable_output(instrument_id: str, enabled: bool) -> str:
    """Enable or disable SMU output.

    Returns:
        str: "OK"
    """
    dev = _get_typed(instrument_id, _SMU_CLASSES)
    dev.enable_output(enabled)
    return "OK"


def smu_measure_voltage(instrument_id: str) -> float:
    """Measure voltage on the SMU."""
    dev = _get_typed(instrument_id, _SMU_CLASSES)
    return dev.measure_voltage()


def smu_measure_current(instrument_id: str) -> float:
    """Measure current on the SMU."""
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
    dev = _get(instrument_id)
    dev.send_command(command)
    return "OK"


def query_scpi(instrument_id: str, command: str) -> str:
    """Send a raw SCPI query and return the response string.

    Note: NI_PXIe_4139 returns an IDN-like string for any query.
    """
    dev = _get(instrument_id)
    return dev.query(command)


def reset_instrument(instrument_id: str) -> str:
    """Send *RST to reset the instrument.

    Returns:
        str: "OK"
    """
    dev = _get(instrument_id)
    dev.reset()
    return "OK"


def get_instrument_type(instrument_id: str) -> str:
    """Return the category of the instrument.

    Returns:
        str: "psu", "dmm", "awg", "scope", "smu", "ev2300", or "unknown"
    """
    dev = _get(instrument_id)
    return _CATEGORY_PREFIX.get(type(dev), "unknown")


def get_version() -> str:
    """Return the scpi-instrument-toolkit package version.

    Returns:
        str: Version string (e.g. "0.1.153").
    """
    from .. import __version__

    return __version__
