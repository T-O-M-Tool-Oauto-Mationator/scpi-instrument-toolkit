"""Canonical enumerations for instrument parameters.

All domain-specific string constants live here so that every layer of the
stack (drivers, REPL commands, GUI blocks) shares the same vocabulary.

Each enum uses the ``str, Enum`` mixin so that enum members compare equal to
their plain-string equivalents and can be passed directly to SCPI write calls
without extra conversion.
"""

from __future__ import annotations

from enum import Enum

# ---------------------------------------------------------------------------
# AWG / Function generator
# ---------------------------------------------------------------------------


class WaveformType(str, Enum):
    """Canonical SCPI waveform identifiers for AWG / function generators.

    Members compare equal to their string values so they can be passed
    directly to SCPI ``set_waveform`` calls::

        >>> WaveformType.SIN == "SIN"
        True
        >>> f"FUNC {WaveformType.SQU}"
        'FUNC SQU'

    Use :meth:`from_alias` to resolve user-supplied strings (e.g. ``"sine"``,
    ``"square"``) to the canonical member.
    """

    SIN = "SIN"
    SQU = "SQU"
    RAMP = "RAMP"
    PULS = "PULS"
    NOIS = "NOIS"
    DC = "DC"
    ARB = "ARB"
    PRBS = "PRBS"

    # ------------------------------------------------------------------
    # Alias resolution
    # ------------------------------------------------------------------

    _aliases: dict[str, WaveformType]  # populated below

    @classmethod
    def from_alias(cls, s: str) -> WaveformType:
        """Resolve a user-supplied waveform string to a :class:`WaveformType`.

        Accepts both canonical names (``"SIN"``) and friendly aliases
        (``"sine"``, ``"sin"``, ``"square"``, etc.).  Falls back to an
        upper-cased lookup so that any future canonical value still works.

        Args:
            s: User-supplied waveform string (case-insensitive).

        Returns:
            The matching :class:`WaveformType` member.

        Raises:
            ValueError: If *s* cannot be resolved to a known waveform.
        """
        key = s.strip().lower()
        resolved = _WAVE_ALIASES.get(key)
        if resolved is not None:
            return resolved
        try:
            return cls(s.strip().upper())
        except ValueError:
            known = ", ".join(sorted(_WAVE_ALIASES.keys()))
            raise ValueError(f"Unknown waveform '{s}'. Known aliases: {known}") from None


# Alias table: user-friendly name → WaveformType member
_WAVE_ALIASES: dict[str, WaveformType] = {
    "sine": WaveformType.SIN,
    "sin": WaveformType.SIN,
    "square": WaveformType.SQU,
    "squ": WaveformType.SQU,
    "ramp": WaveformType.RAMP,
    "triangle": WaveformType.RAMP,
    "tri": WaveformType.RAMP,
    "pulse": WaveformType.PULS,
    "puls": WaveformType.PULS,
    "noise": WaveformType.NOIS,
    "nois": WaveformType.NOIS,
    "dc": WaveformType.DC,
    "arb": WaveformType.ARB,
    "prbs": WaveformType.PRBS,
}


# ---------------------------------------------------------------------------
# DMM
# ---------------------------------------------------------------------------


class DMMMode(str, Enum):
    """Measurement mode identifiers for digital multimeters.

    Values match the method-name fragments used by DMM drivers::

        >>> getattr(dev, f"measure_{DMMMode.DC_VOLTAGE}")  # → dev.measure_dc_voltage
        >>> getattr(dev, f"configure_{DMMMode.FREQUENCY}")  # → dev.configure_frequency

    Use :meth:`from_alias` to resolve REPL shorthand (``"vdc"``, ``"vac"``,
    ``"res"``, …) to the canonical member.
    """

    DC_VOLTAGE = "dc_voltage"
    AC_VOLTAGE = "ac_voltage"
    DC_CURRENT = "dc_current"
    AC_CURRENT = "ac_current"
    RESISTANCE_2WIRE = "resistance_2wire"
    RESISTANCE_4WIRE = "resistance_4wire"
    FREQUENCY = "frequency"
    PERIOD = "period"
    CONTINUITY = "continuity"
    DIODE = "diode"
    CAPACITANCE = "capacitance"
    TEMPERATURE = "temperature"

    @classmethod
    def from_alias(cls, s: str) -> DMMMode:
        """Resolve a user-supplied mode string to a :class:`DMMMode`.

        Accepts both REPL shorthand (``"vdc"``, ``"res"``) and full internal
        names (``"dc_voltage"``, ``"resistance_2wire"``).

        Args:
            s: User-supplied mode string (case-insensitive).

        Returns:
            The matching :class:`DMMMode` member.

        Raises:
            ValueError: If *s* cannot be resolved to a known mode.
        """
        key = s.strip().lower()
        resolved = _DMM_ALIASES.get(key)
        if resolved is not None:
            return resolved
        try:
            return cls(key)
        except ValueError:
            known = ", ".join(sorted(_DMM_ALIASES.keys()))
            raise ValueError(f"Unknown DMM mode '{s}'. Known aliases: {known}") from None


# Alias table: REPL shorthand → DMMMode member
_DMM_ALIASES: dict[str, DMMMode] = {
    "vdc": DMMMode.DC_VOLTAGE,
    "dc_voltage": DMMMode.DC_VOLTAGE,
    "vac": DMMMode.AC_VOLTAGE,
    "ac_voltage": DMMMode.AC_VOLTAGE,
    "idc": DMMMode.DC_CURRENT,
    "dc_current": DMMMode.DC_CURRENT,
    "iac": DMMMode.AC_CURRENT,
    "ac_current": DMMMode.AC_CURRENT,
    "res": DMMMode.RESISTANCE_2WIRE,
    "resistance_2wire": DMMMode.RESISTANCE_2WIRE,
    "fres": DMMMode.RESISTANCE_4WIRE,
    "resistance_4wire": DMMMode.RESISTANCE_4WIRE,
    "freq": DMMMode.FREQUENCY,
    "frequency": DMMMode.FREQUENCY,
    "per": DMMMode.PERIOD,
    "period": DMMMode.PERIOD,
    "cont": DMMMode.CONTINUITY,
    "continuity": DMMMode.CONTINUITY,
    "diode": DMMMode.DIODE,
    "cap": DMMMode.CAPACITANCE,
    "capacitance": DMMMode.CAPACITANCE,
    "temp": DMMMode.TEMPERATURE,
    "temperature": DMMMode.TEMPERATURE,
}


# ---------------------------------------------------------------------------
# Oscilloscope
# ---------------------------------------------------------------------------


class CouplingMode(str, Enum):
    """Input coupling modes for oscilloscope channels.

    Example::

        dev.set_coupling(1, CouplingMode.DC)
    """

    DC = "DC"
    AC = "AC"
    GND = "GND"


class TriggerEdge(str, Enum):
    """Trigger slope (edge) selection for oscilloscopes.

    Example::

        dev.set_trigger_edge(TriggerEdge.RISE)
    """

    RISE = "RISE"
    FALL = "FALL"


class TriggerMode(str, Enum):
    """Trigger sweep mode for oscilloscopes.

    Example::

        dev.set_trigger_mode(TriggerMode.AUTO)
    """

    AUTO = "AUTO"
    NORMAL = "NORMAL"
    SINGLE = "SINGLE"


# ---------------------------------------------------------------------------
# SMU (Source Measure Unit)
# ---------------------------------------------------------------------------


class SMUSourceMode(str, Enum):
    """Output source mode for SMU instruments.

    Example::

        dev.set_source_mode(SMUSourceMode.VOLTAGE)
    """

    VOLTAGE = "VOLTAGE"
    CURRENT = "CURRENT"
