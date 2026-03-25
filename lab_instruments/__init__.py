__version__ = "0.1.116"
__author__ = "Brighton Sikarskie, Cesar Magana"

from .src.bk_4063 import BK_4063
from .src.device_manager import DeviceManager
from .src.discovery import InstrumentDiscovery, find_all
from .src.hp_34401a import HP_34401A
from .src.hp_e3631a import HP_E3631A
from .src.jds6600_generator import JDS6600_Generator
from .src.keysight_edu33212a import Keysight_EDU33212A
from .src.matrix_mps6010h import MATRIX_MPS6010H
try:
    from .src.ni_pxie_4139 import NI_PXIe_4139
except ImportError:
    NI_PXIe_4139 = None  # type: ignore[assignment,misc]
from .src.owon_xdm1041 import Owon_XDM1041
from .src.rigol_dho804 import Rigol_DHO804
from .src.tektronix_mso2024 import Tektronix_MSO2024
from .src.terminal import ColorPrinter

__all__ = [
    "DeviceManager",
    "HP_E3631A",
    "HP_34401A",
    "BK_4063",
    "Tektronix_MSO2024",
    "Rigol_DHO804",
    "MATRIX_MPS6010H",
    "NI_PXIe_4139",
    "Owon_XDM1041",
    "JDS6600_Generator",
    "Keysight_EDU33212A",
    "ColorPrinter",
    "InstrumentDiscovery",
    "find_all",
]
