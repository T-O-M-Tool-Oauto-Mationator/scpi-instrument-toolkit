"""Capability flags for instrument drivers."""

from enum import Flag, auto


class Capability(Flag):
    """Flags describing what an instrument supports."""

    NONE = 0

    # PSU capabilities
    PSU_MULTI_CHANNEL = auto()
    PSU_READBACK = auto()
    PSU_TRACKING = auto()
    PSU_SAVE_RECALL = auto()

    # AWG capabilities
    AWG_SYNC = auto()
    AWG_JDS6600_PROTOCOL = auto()
    AWG_INDEPENDENT_PARAMS = auto()

    # DMM capabilities
    DMM_NPLC = auto()
    DMM_DISPLAY_CONTROL = auto()
    DMM_DISPLAY_TEXT = auto()
    DMM_FETCH = auto()
    DMM_BEEP = auto()
    DMM_RANGES = auto()

    # Scope capabilities
    SCOPE_SCREENSHOT = auto()
    SCOPE_BUILTIN_AWG = auto()
    SCOPE_COUNTER = auto()
    SCOPE_DVM = auto()
    SCOPE_DISPLAY_CONTROL = auto()
    SCOPE_ACQUIRE_CONTROL = auto()
    SCOPE_CURSOR = auto()
    SCOPE_MATH = auto()
    SCOPE_RECORD = auto()
    SCOPE_MASK = auto()
    SCOPE_LABEL = auto()
    SCOPE_INVERT = auto()
    SCOPE_BWLIMIT = auto()
    SCOPE_FORCE_TRIGGER = auto()
    SCOPE_WAIT_STOP = auto()
    SCOPE_MEAS_FORCE = auto()
    SCOPE_MEAS_CLEAR = auto()


# Per-driver capability declarations
# Maps class name to its capabilities
DRIVER_CAPABILITIES = {
    # PSUs
    "HP_E3631A": (
        Capability.PSU_MULTI_CHANNEL | Capability.PSU_READBACK | Capability.PSU_TRACKING | Capability.PSU_SAVE_RECALL
    ),
    "MockHP_E3631A": (
        Capability.PSU_MULTI_CHANNEL | Capability.PSU_READBACK | Capability.PSU_TRACKING | Capability.PSU_SAVE_RECALL
    ),
    "MATRIX_MPS6010H": Capability.NONE,  # single channel, no readback
    "MockMPS6010H": Capability.NONE,
    "NI_PXIe_4139": Capability.PSU_READBACK,
    "MockNI_PXIe_4139": Capability.PSU_READBACK,
    "Keysight_EDU36311A": (
        Capability.PSU_MULTI_CHANNEL | Capability.PSU_READBACK | Capability.PSU_TRACKING | Capability.PSU_SAVE_RECALL
    ),
    "MockEDU36311A": (
        Capability.PSU_MULTI_CHANNEL | Capability.PSU_READBACK | Capability.PSU_TRACKING | Capability.PSU_SAVE_RECALL
    ),
    # AWGs
    "Keysight_EDU33212A": (Capability.AWG_SYNC | Capability.AWG_INDEPENDENT_PARAMS),
    "MockEDU33212A": (Capability.AWG_SYNC | Capability.AWG_INDEPENDENT_PARAMS),
    "BK_4063": Capability.AWG_INDEPENDENT_PARAMS,
    "JDS6600_Generator": Capability.AWG_JDS6600_PROTOCOL,
    "MockJDS6600": Capability.AWG_JDS6600_PROTOCOL,
    # DMMs
    "HP_34401A": (
        Capability.DMM_NPLC
        | Capability.DMM_DISPLAY_CONTROL
        | Capability.DMM_DISPLAY_TEXT
        | Capability.DMM_FETCH
        | Capability.DMM_BEEP
        | Capability.DMM_RANGES
    ),
    "MockHP_34401A": (
        Capability.DMM_NPLC
        | Capability.DMM_DISPLAY_CONTROL
        | Capability.DMM_DISPLAY_TEXT
        | Capability.DMM_FETCH
        | Capability.DMM_BEEP
        | Capability.DMM_RANGES
    ),
    "Keysight_EDU34450A": (
        Capability.DMM_DISPLAY_CONTROL
        | Capability.DMM_DISPLAY_TEXT
        | Capability.DMM_FETCH
        | Capability.DMM_BEEP
        | Capability.DMM_RANGES
    ),
    "MockEDU34450A": (
        Capability.DMM_DISPLAY_CONTROL
        | Capability.DMM_DISPLAY_TEXT
        | Capability.DMM_FETCH
        | Capability.DMM_BEEP
        | Capability.DMM_RANGES
    ),
    "Owon_XDM1041": Capability.NONE,
    "MockXDM1041": Capability.NONE,
    # Scopes
    "Rigol_DHO804": (
        Capability.SCOPE_SCREENSHOT
        | Capability.SCOPE_BUILTIN_AWG
        | Capability.SCOPE_COUNTER
        | Capability.SCOPE_DVM
        | Capability.SCOPE_DISPLAY_CONTROL
        | Capability.SCOPE_ACQUIRE_CONTROL
        | Capability.SCOPE_CURSOR
        | Capability.SCOPE_MATH
        | Capability.SCOPE_RECORD
        | Capability.SCOPE_MASK
        | Capability.SCOPE_LABEL
        | Capability.SCOPE_INVERT
        | Capability.SCOPE_BWLIMIT
        | Capability.SCOPE_FORCE_TRIGGER
        | Capability.SCOPE_WAIT_STOP
        | Capability.SCOPE_MEAS_FORCE
        | Capability.SCOPE_MEAS_CLEAR
    ),
    "MockDHO804": (
        Capability.SCOPE_SCREENSHOT
        | Capability.SCOPE_BUILTIN_AWG
        | Capability.SCOPE_COUNTER
        | Capability.SCOPE_DVM
        | Capability.SCOPE_DISPLAY_CONTROL
        | Capability.SCOPE_ACQUIRE_CONTROL
        | Capability.SCOPE_CURSOR
        | Capability.SCOPE_MATH
        | Capability.SCOPE_RECORD
        | Capability.SCOPE_MASK
        | Capability.SCOPE_LABEL
        | Capability.SCOPE_INVERT
        | Capability.SCOPE_BWLIMIT
        | Capability.SCOPE_FORCE_TRIGGER
        | Capability.SCOPE_WAIT_STOP
        | Capability.SCOPE_MEAS_FORCE
        | Capability.SCOPE_MEAS_CLEAR
    ),
    "Keysight_DSOX1204G": (
        Capability.SCOPE_SCREENSHOT
        | Capability.SCOPE_BUILTIN_AWG
        | Capability.SCOPE_DVM
        | Capability.SCOPE_DISPLAY_CONTROL
        | Capability.SCOPE_ACQUIRE_CONTROL
        | Capability.SCOPE_MATH
        | Capability.SCOPE_MASK
        | Capability.SCOPE_LABEL
        | Capability.SCOPE_INVERT
        | Capability.SCOPE_BWLIMIT
        | Capability.SCOPE_FORCE_TRIGGER
        | Capability.SCOPE_WAIT_STOP
        | Capability.SCOPE_MEAS_CLEAR
    ),
    "MockDSOX1204G": (
        Capability.SCOPE_SCREENSHOT
        | Capability.SCOPE_BUILTIN_AWG
        | Capability.SCOPE_DVM
        | Capability.SCOPE_DISPLAY_CONTROL
        | Capability.SCOPE_ACQUIRE_CONTROL
        | Capability.SCOPE_MATH
        | Capability.SCOPE_MASK
        | Capability.SCOPE_LABEL
        | Capability.SCOPE_INVERT
        | Capability.SCOPE_BWLIMIT
        | Capability.SCOPE_FORCE_TRIGGER
        | Capability.SCOPE_WAIT_STOP
        | Capability.SCOPE_MEAS_CLEAR
    ),
    "Tektronix_MSO2024": Capability.SCOPE_WAIT_STOP,
    "MockMSO2024": Capability.SCOPE_WAIT_STOP,
}

# Display names for known instrument classes
DISPLAY_NAMES = {
    "HP_E3631A": "HP E3631A",
    "MockHP_E3631A": "HP E3631A (Mock)",
    "MATRIX_MPS6010H": "MATRIX MPS-6010H",
    "MockMPS6010H": "MATRIX MPS-6010H (Mock)",
    "NI_PXIe_4139": "NI PXIe-4139 SMU",
    "MockNI_PXIe_4139": "NI PXIe-4139 SMU (Mock)",
    "Keysight_EDU33212A": "Keysight EDU33212A",
    "MockEDU33212A": "Keysight EDU33212A (Mock)",
    "BK_4063": "BK Precision 4063",
    "JDS6600_Generator": "JDS6600",
    "MockJDS6600": "JDS6600 (Mock)",
    "HP_34401A": "HP 34401A",
    "MockHP_34401A": "HP 34401A (Mock)",
    "Owon_XDM1041": "Owon XDM1041",
    "MockXDM1041": "Owon XDM1041 (Mock)",
    "Rigol_DHO804": "Rigol DHO804",
    "MockDHO804": "Rigol DHO804 (Mock)",
    "Keysight_EDU36311A": "Keysight EDU36311A",
    "MockEDU36311A": "Keysight EDU36311A (Mock)",
    "Keysight_DSOX1204G": "Keysight DSOX1204G",
    "MockDSOX1204G": "Keysight DSOX1204G (Mock)",
    "Keysight_EDU34450A": "Keysight EDU34450A",
    "MockEDU34450A": "Keysight EDU34450A (Mock)",
    "Tektronix_MSO2024": "Tektronix MSO2024",
    "MockMSO2024": "Tektronix MSO2024 (Mock)",
}
