"""TI EV2300A USB-to-I2C/SMBus adapter driver.

Pure-Python cross-platform driver using HID protocol via ctypes.
Does NOT inherit from DeviceManager (no PyVISA, no SCPI).

Platforms:
  Windows: ctypes -> hid.dll + setupapi.dll + kernel32.dll
  Linux:   open/read/write on /dev/hidrawN + ioctl for device info
  macOS:   hidapi package (pip install hidapi) or IOKit ctypes fallback

Protocol reference: romixlab/ev2300 (MIT License, 2018)
Tested against real EV2300A hardware (Windows + Linux).
"""

from __future__ import annotations

import logging
import os
import struct
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# USB identifiers
# ---------------------------------------------------------------------------
VID = 0x0451  # Texas Instruments
PID_FLASHED = 0x0036  # Normal operational mode
PID_BOOTLOADER = 0x2136  # Firmware not yet loaded

# ---------------------------------------------------------------------------
# HID protocol constants
# ---------------------------------------------------------------------------
CMD_READ_WORD = 0x01
CMD_READ_BLOCK = 0x02
CMD_READ_BYTE = 0x03
CMD_WRITE_WORD = 0x04
CMD_WRITE_BLOCK = 0x05
CMD_COMMAND = 0x06  # SMBus "Send Byte"
CMD_WRITE_BYTE = 0x07
CMD_SUBMIT = 0x80  # Write handshake
CMD_ERROR = 0x46  # Device error response

RESP_FLAG = 0x40  # Success responses have bit 6 set
FRAME_MARKER = 0xAA
FRAME_END = 0x55
BUF_SIZE = 64

# ---------------------------------------------------------------------------
# CRC-8 (polynomial 0x07, init 0x00)
# ---------------------------------------------------------------------------
_CRC8_TABLE: list[int] = []
for _i in range(256):
    _c = _i
    for _ in range(8):
        _c = ((_c << 1) ^ 0x07) & 0xFF if _c & 0x80 else (_c << 1) & 0xFF
    _CRC8_TABLE.append(_c)


def crc8(data: bytes | bytearray) -> int:
    """Compute CRC-8 (poly=0x07, init=0x00) over *data*."""
    crc = 0x00
    for b in data:
        crc = _CRC8_TABLE[crc ^ b]
    return crc


# ===========================================================================
# Platform backends
# ===========================================================================


class _HIDBackend:
    """Abstract HID backend interface."""

    def enumerate(self) -> list[dict]:
        raise NotImplementedError

    def find(self, vid: int, pid: int) -> object | None:
        for dev in self.enumerate():
            if dev["vid"] == vid and dev["pid"] == pid:
                return dev["path"]
        return None

    def open(self, path: object) -> object:
        raise NotImplementedError

    def close(self, handle: object) -> None:
        raise NotImplementedError

    def write(self, handle: object, data: bytes) -> bool:
        raise NotImplementedError

    def read(self, handle: object) -> bytes | None:
        raise NotImplementedError

    def flush(self, handle: object) -> None:
        pass

    def get_info(self, handle: object, path: object) -> dict:
        raise NotImplementedError

    def get_caps(self, path: object) -> dict | None:
        return None


# ---------------------------------------------------------------------------
# Windows backend
# ---------------------------------------------------------------------------


class _WindowsBackend(_HIDBackend):
    def __init__(self) -> None:
        import ctypes
        import ctypes.wintypes as wt

        self._ct = ctypes
        self._wt = wt
        self._setup_api()

    def _setup_api(self) -> None:
        ct = self._ct
        wt = self._wt

        class GUID(ct.Structure):
            _fields_ = [
                ("Data1", ct.c_ulong),
                ("Data2", ct.c_ushort),
                ("Data3", ct.c_ushort),
                ("Data4", ct.c_ubyte * 8),
            ]

        self.GUID = GUID

        class SP_DEVIF(ct.Structure):
            _fields_ = [
                ("cbSize", wt.DWORD),
                ("InterfaceClassGuid", GUID),
                ("Flags", wt.DWORD),
                ("Reserved", ct.POINTER(ct.c_ulong)),
            ]

        self._SP_DEVIF = SP_DEVIF

        class DETAIL(ct.Structure):
            _fields_ = [("cbSize", wt.DWORD), ("DevicePath", ct.c_char * 512)]

        self._DETAIL = DETAIL

        class ATTRS(ct.Structure):
            _fields_ = [
                ("Size", wt.ULONG),
                ("VendorID", ct.c_ushort),
                ("ProductID", ct.c_ushort),
                ("VersionNumber", ct.c_ushort),
            ]

        self._ATTRS = ATTRS

        class CAPS(ct.Structure):
            _fields_ = [
                ("Usage", ct.c_ushort),
                ("UsagePage", ct.c_ushort),
                ("InputReportByteLength", ct.c_ushort),
                ("OutputReportByteLength", ct.c_ushort),
                ("FeatureReportByteLength", ct.c_ushort),
                ("Reserved", ct.c_ushort * 17),
                ("NumberLinkCollectionNodes", ct.c_ushort),
                ("NumberInputButtonCaps", ct.c_ushort),
                ("NumberInputValueCaps", ct.c_ushort),
                ("NumberInputDataIndices", ct.c_ushort),
                ("NumberOutputButtonCaps", ct.c_ushort),
                ("NumberOutputValueCaps", ct.c_ushort),
                ("NumberOutputDataIndices", ct.c_ushort),
                ("NumberFeatureButtonCaps", ct.c_ushort),
                ("NumberFeatureValueCaps", ct.c_ushort),
                ("NumberFeatureDataIndices", ct.c_ushort),
            ]

        self._CAPS = CAPS

        self._hid = ct.windll.hid
        self._sa = ct.windll.setupapi
        self._k32 = ct.windll.kernel32

        self._INVALID = ct.c_void_p(-1).value
        self._SHARE_RW = 0x03
        self._OPEN_EXISTING = 3
        self._detail_cbsize = 8 if ct.sizeof(ct.c_void_p) == 8 else 5

        self._sa.SetupDiGetClassDevsA.restype = ct.c_void_p
        self._sa.SetupDiGetClassDevsA.argtypes = [ct.POINTER(GUID), ct.c_char_p, ct.c_void_p, wt.DWORD]
        self._sa.SetupDiEnumDeviceInterfaces.restype = wt.BOOL
        self._sa.SetupDiEnumDeviceInterfaces.argtypes = [
            ct.c_void_p,
            ct.c_void_p,
            ct.POINTER(GUID),
            wt.DWORD,
            ct.POINTER(SP_DEVIF),
        ]
        self._sa.SetupDiGetDeviceInterfaceDetailA.restype = wt.BOOL
        self._sa.SetupDiGetDeviceInterfaceDetailA.argtypes = [
            ct.c_void_p,
            ct.POINTER(SP_DEVIF),
            ct.c_void_p,
            wt.DWORD,
            ct.POINTER(wt.DWORD),
            ct.c_void_p,
        ]
        self._sa.SetupDiDestroyDeviceInfoList.argtypes = [ct.c_void_p]

        self._k32.CreateFileA.restype = ct.c_void_p
        self._k32.CreateFileA.argtypes = [
            ct.c_char_p,
            wt.DWORD,
            wt.DWORD,
            ct.c_void_p,
            wt.DWORD,
            wt.DWORD,
            ct.c_void_p,
        ]
        self._k32.CloseHandle.argtypes = [ct.c_void_p]
        self._k32.CloseHandle.restype = wt.BOOL
        self._k32.WriteFile.restype = wt.BOOL
        self._k32.WriteFile.argtypes = [ct.c_void_p, ct.c_void_p, wt.DWORD, ct.POINTER(wt.DWORD), ct.c_void_p]
        self._k32.ReadFile.restype = wt.BOOL
        self._k32.ReadFile.argtypes = [ct.c_void_p, ct.c_void_p, wt.DWORD, ct.POINTER(wt.DWORD), ct.c_void_p]

        self._hid.HidD_GetHidGuid.argtypes = [ct.POINTER(GUID)]
        self._hid.HidD_GetAttributes.restype = wt.BOOL
        self._hid.HidD_GetAttributes.argtypes = [ct.c_void_p, ct.c_void_p]
        self._hid.HidD_GetPreparsedData.restype = wt.BOOL
        self._hid.HidD_GetPreparsedData.argtypes = [ct.c_void_p, ct.POINTER(ct.c_void_p)]
        self._hid.HidP_GetCaps.restype = ct.c_long
        self._hid.HidP_GetCaps.argtypes = [ct.c_void_p, ct.POINTER(CAPS)]
        self._hid.HidD_FreePreparsedData.argtypes = [ct.c_void_p]
        self._hid.HidD_SetNumInputBuffers.restype = wt.BOOL
        self._hid.HidD_SetNumInputBuffers.argtypes = [ct.c_void_p, wt.ULONG]
        for fn in ("HidD_GetSerialNumberString", "HidD_GetProductString", "HidD_GetManufacturerString"):
            f = getattr(self._hid, fn)
            f.restype = wt.BOOL
            f.argtypes = [ct.c_void_p, ct.c_void_p, wt.ULONG]

    def enumerate(self) -> list[dict]:
        ct = self._ct
        guid = self.GUID()
        self._hid.HidD_GetHidGuid(ct.byref(guid))
        h_info = self._sa.SetupDiGetClassDevsA(ct.byref(guid), None, None, 0x12)
        if h_info == self._INVALID:
            return []
        devices: list[dict] = []
        try:
            idx = 0
            while True:
                iface = self._SP_DEVIF()
                iface.cbSize = ct.sizeof(self._SP_DEVIF)
                if not self._sa.SetupDiEnumDeviceInterfaces(h_info, None, ct.byref(guid), idx, ct.byref(iface)):
                    break
                detail = self._DETAIL()
                detail.cbSize = self._detail_cbsize
                req = self._wt.DWORD()
                self._sa.SetupDiGetDeviceInterfaceDetailA(
                    h_info, ct.byref(iface), ct.byref(detail), ct.sizeof(detail), ct.byref(req), None
                )
                path_bytes = detail.DevicePath
                path_str = path_bytes.decode("ascii", errors="replace")
                h_dev = self._k32.CreateFileA(path_bytes, 0, self._SHARE_RW, None, self._OPEN_EXISTING, 0, None)
                if h_dev != self._INVALID:
                    attrs = self._ATTRS()
                    attrs.Size = ct.sizeof(self._ATTRS)
                    if self._hid.HidD_GetAttributes(h_dev, ct.byref(attrs)):
                        devices.append(
                            {
                                "path": path_bytes,
                                "path_str": path_str,
                                "vid": attrs.VendorID,
                                "pid": attrs.ProductID,
                                "version": attrs.VersionNumber,
                            }
                        )
                    self._k32.CloseHandle(h_dev)
                idx += 1
        finally:
            self._sa.SetupDiDestroyDeviceInfoList(h_info)
        return devices

    def open(self, path: object) -> object:
        h = self._k32.CreateFileA(path, 0x80000000 | 0x40000000, self._SHARE_RW, None, self._OPEN_EXISTING, 0, None)
        if h == self._INVALID:
            raise OSError(f"CreateFile failed ({self._ct.GetLastError()})")
        self._hid.HidD_SetNumInputBuffers(h, 64)
        return h

    def close(self, handle: object) -> None:
        self._k32.CloseHandle(handle)

    def write(self, handle: object, data: bytes) -> bool:
        report = b"\x00" + bytes(data[:BUF_SIZE])
        report += b"\x00" * (65 - len(report))
        written = self._wt.DWORD()
        ok = self._k32.WriteFile(handle, report, len(report), self._ct.byref(written), None)
        return bool(ok)

    def read(self, handle: object) -> bytes | None:
        buf = self._ct.create_string_buffer(65)
        read_n = self._wt.DWORD()
        ok = self._k32.ReadFile(handle, buf, 65, self._ct.byref(read_n), None)
        if not ok:
            return None
        raw = buf.raw[: read_n.value]
        return raw[1:] if len(raw) > 1 else None

    def flush(self, handle: object) -> None:
        import contextlib

        with contextlib.suppress(Exception):
            self._hid.HidD_FlushQueue(handle)

    def get_info(self, handle: object, path: object) -> dict:
        ct = self._ct
        attrs = self._ATTRS()
        attrs.Size = ct.sizeof(self._ATTRS)
        self._hid.HidD_GetAttributes(handle, ct.byref(attrs))

        def _str(func):
            buf = ct.create_unicode_buffer(256)
            ok = func(handle, buf, ct.sizeof(buf))
            return buf.value if ok else None

        return {
            "ok": True,
            "vid": f"0x{attrs.VendorID:04x}",
            "pid": f"0x{attrs.ProductID:04x}",
            "version": f"0x{attrs.VersionNumber:04x}",
            "serial": _str(self._hid.HidD_GetSerialNumberString),
            "product": _str(self._hid.HidD_GetProductString),
            "manufacturer": _str(self._hid.HidD_GetManufacturerString),
        }

    def get_caps(self, path: object) -> dict | None:
        ct = self._ct
        h = self._k32.CreateFileA(path, 0, self._SHARE_RW, None, self._OPEN_EXISTING, 0, None)
        if h == self._INVALID:
            return None
        try:
            ppd = ct.c_void_p()
            if not self._hid.HidD_GetPreparsedData(h, ct.byref(ppd)):
                return None
            caps = self._CAPS()
            self._hid.HidP_GetCaps(ppd, ct.byref(caps))
            self._hid.HidD_FreePreparsedData(ppd)
            return {
                "usage": caps.Usage,
                "usage_page": caps.UsagePage,
                "input_report_length": caps.InputReportByteLength,
                "output_report_length": caps.OutputReportByteLength,
                "feature_report_length": caps.FeatureReportByteLength,
            }
        finally:
            self._k32.CloseHandle(h)


# ---------------------------------------------------------------------------
# Linux backend
# ---------------------------------------------------------------------------


class _LinuxBackend(_HIDBackend):
    _HIDIOCGRAWINFO = 0x80084803
    _HIDIOCGRAWNAME_BASE = 0x80004804

    @staticmethod
    def _hidiocgrawname(length: int) -> int:
        return 0x80004804 | ((length & 0x3FFF) << 16)

    def enumerate(self) -> list[dict]:
        devices: list[dict] = []
        hidraw_dir = Path("/sys/class/hidraw")
        if not hidraw_dir.is_dir():
            return devices

        for entry in sorted(hidraw_dir.iterdir()):
            dev_path = f"/dev/{entry.name}"
            if not Path(dev_path).exists():
                continue

            vid, pid = self._read_vid_pid_sysfs(entry)
            if vid is None:
                vid, pid = self._read_vid_pid_ioctl(dev_path)
            if vid is None:
                continue

            devices.append(
                {
                    "path": dev_path,
                    "path_str": dev_path,
                    "vid": vid,
                    "pid": pid,
                    "version": 0,
                }
            )

        return devices

    @staticmethod
    def _read_vid_pid_sysfs(hidraw_entry: Path) -> tuple:
        uevent = hidraw_entry / "device" / "uevent"
        if not uevent.is_file():
            return None, None

        try:
            text = uevent.read_text()
        except OSError:
            return None, None

        for line in text.splitlines():
            if line.startswith("HID_ID="):
                parts = line.split("=", 1)[1].split(":")
                if len(parts) >= 3:
                    try:
                        vid = int(parts[1], 16) & 0xFFFF
                        pid = int(parts[2], 16) & 0xFFFF
                        return vid, pid
                    except ValueError:
                        pass

        device_dir = hidraw_entry / "device"
        for parent in [device_dir, device_dir / "..", device_dir / ".." / ".."]:
            try:
                parent = parent.resolve()
                vid_file = parent / "idVendor"
                pid_file = parent / "idProduct"
                if vid_file.is_file() and pid_file.is_file():
                    vid = int(vid_file.read_text().strip(), 16)
                    pid = int(pid_file.read_text().strip(), 16)
                    return vid, pid
            except (OSError, ValueError):
                continue

        return None, None

    def _read_vid_pid_ioctl(self, dev_path: str) -> tuple:
        import fcntl

        try:
            fd = os.open(dev_path, os.O_RDONLY)
            try:
                buf = bytearray(8)
                fcntl.ioctl(fd, self._HIDIOCGRAWINFO, buf)
                _, vid, pid = struct.unpack("<Ihh", buf)
                return vid & 0xFFFF, pid & 0xFFFF
            finally:
                os.close(fd)
        except OSError:
            return None, None

    def open(self, path: object) -> int:
        return os.open(str(path), os.O_RDWR)

    def close(self, handle: object) -> None:
        os.close(handle)

    def write(self, handle: object, data: bytes) -> bool:
        report = bytes(data[:BUF_SIZE])
        report += b"\x00" * (BUF_SIZE - len(report))
        try:
            written = os.write(handle, report)
            return written == BUF_SIZE
        except OSError as e:
            logger.warning("write failed: %s", e)
            return False

    def read(self, handle: object) -> bytes | None:
        try:
            data = os.read(handle, BUF_SIZE)
            return data if data else None
        except OSError as e:
            logger.warning("read failed: %s", e)
            return None

    def flush(self, handle: object) -> None:
        import fcntl

        try:
            flags = fcntl.fcntl(handle, fcntl.F_GETFL)
            fcntl.fcntl(handle, fcntl.F_SETFL, flags | os.O_NONBLOCK)
            try:
                while True:
                    data = os.read(handle, BUF_SIZE)
                    if not data:
                        break
            except BlockingIOError:
                pass
            finally:
                fcntl.fcntl(handle, fcntl.F_SETFL, flags)
        except OSError:
            pass

    def get_info(self, handle: object, path: object) -> dict:
        import fcntl

        info: dict = {"ok": True}
        path_str = str(path)

        try:
            buf = bytearray(8)
            fcntl.ioctl(handle, self._HIDIOCGRAWINFO, buf)
            _, vid, pid = struct.unpack("<Ihh", buf)
            info["vid"] = f"0x{vid & 0xFFFF:04x}"
            info["pid"] = f"0x{pid & 0xFFFF:04x}"
        except OSError:
            info["vid"] = "unknown"
            info["pid"] = "unknown"

        try:
            name_buf = bytearray(256)
            fcntl.ioctl(handle, self._hidiocgrawname(256), name_buf)
            name = name_buf.split(b"\x00", 1)[0].decode("utf-8", errors="replace")
            info["product"] = name
        except OSError:
            info["product"] = None

        info["serial"] = self._read_serial_sysfs(path_str)
        info["manufacturer"] = self._read_sysfs_attr(path_str, "manufacturer")
        info["version"] = "0x0000"

        return info

    @staticmethod
    def _read_serial_sysfs(dev_path: str) -> str | None:
        name = Path(dev_path).name
        device_dir = Path(f"/sys/class/hidraw/{name}/device")
        for parent in [device_dir, device_dir / "..", device_dir / ".." / ".."]:
            try:
                serial_file = parent.resolve() / "serial"
                if serial_file.is_file():
                    return serial_file.read_text().strip()
            except OSError:
                continue
        return None

    @staticmethod
    def _read_sysfs_attr(dev_path: str, attr: str) -> str | None:
        name = Path(dev_path).name
        device_dir = Path(f"/sys/class/hidraw/{name}/device")
        for parent in [device_dir, device_dir / "..", device_dir / ".." / ".."]:
            try:
                f = parent.resolve() / attr
                if f.is_file():
                    return f.read_text().strip()
            except OSError:
                continue
        return None

    def get_caps(self, path: object) -> dict | None:
        return None


# ---------------------------------------------------------------------------
# macOS backend
# ---------------------------------------------------------------------------


class _DarwinBackend(_HIDBackend):
    """macOS HID backend using the ``hidapi`` package.

    Install with::

        pip install hidapi
    """

    def __init__(self) -> None:
        try:
            import hid  # type: ignore[import-untyped]

            self._hid = hid
        except ImportError as exc:
            raise ImportError(
                "macOS EV2300 support requires the 'hidapi' package. Install it with: pip install hidapi"
            ) from exc

    def enumerate(self) -> list[dict]:
        devices: list[dict] = []
        for dev in self._hid.enumerate():
            devices.append(
                {
                    "path": dev["path"],
                    "path_str": dev["path"].decode("utf-8", errors="replace")
                    if isinstance(dev["path"], bytes)
                    else str(dev["path"]),
                    "vid": dev["vendor_id"],
                    "pid": dev["product_id"],
                    "version": dev.get("release_number", 0),
                }
            )
        return devices

    def open(self, path: object) -> object:
        device = self._hid.device()
        device.open_path(path)
        return device

    def close(self, handle: object) -> None:
        handle.close()

    def write(self, handle: object, data: bytes) -> bool:
        report = b"\x00" + bytes(data[:BUF_SIZE])
        report += b"\x00" * (65 - len(report))
        try:
            handle.write(report)
            return True
        except OSError:
            return False

    def read(self, handle: object) -> bytes | None:
        data = handle.read(BUF_SIZE, timeout_ms=200)
        return bytes(data) if data else None

    def flush(self, handle: object) -> None:
        try:
            while handle.read(BUF_SIZE, timeout_ms=0):
                pass
        except Exception:
            pass

    def get_info(self, handle: object, path: object) -> dict:
        return {
            "ok": True,
            "vid": f"0x{VID:04x}",
            "pid": f"0x{PID_FLASHED:04x}",
            "version": "0x0000",
            "serial": handle.get_serial_number_string() or None,
            "product": handle.get_product_string() or None,
            "manufacturer": handle.get_manufacturer_string() or None,
        }


# ---------------------------------------------------------------------------
# Backend auto-selection
# ---------------------------------------------------------------------------


def _get_backend() -> _HIDBackend:
    if sys.platform == "win32":
        return _WindowsBackend()
    elif sys.platform.startswith("linux"):
        return _LinuxBackend()
    elif sys.platform == "darwin":
        return _DarwinBackend()
    else:
        raise OSError(f"Unsupported platform: {sys.platform}. Supported: Windows, Linux, macOS")


_backend: _HIDBackend | None = None


def _get_or_create_backend() -> _HIDBackend:
    global _backend
    if _backend is None:
        _backend = _get_backend()
    return _backend


# ===========================================================================
# _EV2300Core -- internal driver implementation
# ===========================================================================


class _EV2300Core:
    """Internal HID driver for the EV2300.  Wrapped by :class:`TI_EV2300`."""

    def __init__(self, backend: _HIDBackend | None = None) -> None:
        self._be = backend or _get_or_create_backend()
        self._handle: object | None = None
        self._path: object | None = None
        self._caps: dict | None = None

    def open(self, path: object | None = None) -> dict:
        if path is None:
            path = self._be.find(VID, PID_FLASHED)
            if path is None:
                bl = self._be.find(VID, PID_BOOTLOADER)
                if bl:
                    return {"ok": False, "status": -2, "status_text": "EV2300 in bootloader mode (PID=0x2136)"}
                return {"ok": False, "status": -1, "status_text": "EV2300 not found (VID=0x0451 PID=0x0036)"}

        self._path = path
        try:
            self._handle = self._be.open(path)
        except OSError as e:
            self._handle = None
            return {"ok": False, "status": -3, "status_text": str(e)}

        self._caps = self._be.get_caps(path)
        return {"ok": True, "status": 0, "caps": self._caps, "status_text": "EV2300 opened"}

    def close(self) -> int:
        if self._handle is not None:
            self._be.close(self._handle)
            self._handle = None
        return 0

    @property
    def is_open(self) -> bool:
        return self._handle is not None

    def write_report(self, data: bytes | bytearray) -> bool:
        if self._handle is None:
            raise RuntimeError("Device not open")
        return self._be.write(self._handle, data)

    def read_report(self) -> bytes | None:
        if self._handle is None:
            raise RuntimeError("Device not open")
        return self._be.read(self._handle)

    def flush_input(self) -> None:
        if self._handle is not None:
            self._be.flush(self._handle)

    # ------------------------------------------------------------------
    # Packet building and parsing
    # ------------------------------------------------------------------

    @staticmethod
    def build_packet(cmd: int, i2c_addr: int = 0, reg: int = 0, data: bytes | bytearray = b"") -> bytearray:
        buf = bytearray(BUF_SIZE)

        if cmd == CMD_SUBMIT:
            buf[0] = 8
            buf[1] = FRAME_MARKER
            buf[2] = CMD_SUBMIT
            buf[6] = 0
            buf[7] = crc8(buf[2:7])
            buf[8] = FRAME_END
            return buf

        payload = bytearray()
        payload.append(i2c_addr << 1)
        payload.append(reg)
        payload.extend(data)

        plen = len(payload)
        buf[0] = 2 + 1 + 3 + 1 + plen + 1 + 1
        buf[1] = FRAME_MARKER
        buf[2] = cmd
        buf[6] = plen
        buf[7 : 7 + plen] = payload

        crc_end = 7 + plen
        buf[crc_end] = crc8(buf[2:crc_end])
        buf[crc_end + 1] = FRAME_END

        return buf

    @staticmethod
    def parse_response(raw: bytes | bytearray | None) -> dict:
        if raw is None or len(raw) < 8:
            return {"ok": False, "error": True, "raw": raw, "status_text": "Response too short"}

        length = raw[0]
        marker = raw[1]
        cmd = raw[2]

        if marker != FRAME_MARKER:
            return {
                "ok": False,
                "error": True,
                "cmd": cmd,
                "raw": bytes(raw),
                "status_text": f"Bad marker 0x{marker:02x}",
            }

        if cmd == CMD_ERROR:
            return {
                "ok": False,
                "error": True,
                "cmd": cmd,
                "length": length,
                "raw": bytes(raw),
                "status_text": "Device error (0x46)",
            }

        crc_ok = False
        if 3 <= length <= BUF_SIZE:
            crc_ok = raw[length - 1] == crc8(raw[2 : length - 1])

        plen = raw[6] if length > 6 else 0
        payload = bytes(raw[7 : 7 + plen]) if plen > 0 else b""

        return {
            "ok": crc_ok,
            "cmd": cmd,
            "length": length,
            "payload_len": plen,
            "payload": payload,
            "crc_ok": crc_ok,
            "error": False,
            "raw": bytes(raw),
        }

    # ------------------------------------------------------------------
    # Core request/response
    # ------------------------------------------------------------------

    def _request(self, packet: bytearray, write_submit: bool = False) -> dict:
        if not self.write_report(packet):
            return {"ok": False, "status_text": "Write failed"}

        if write_submit:
            submit = self.build_packet(CMD_SUBMIT)
            if not self.write_report(submit):
                return {"ok": False, "status_text": "Submit write failed"}

        raw = self.read_report()
        if raw is None:
            return {"ok": False, "status_text": "Read timeout"}

        return self.parse_response(raw)

    # ------------------------------------------------------------------
    # SMBus operations
    # ------------------------------------------------------------------

    def read_word(self, i2c_addr: int, register: int) -> dict:
        pkt = self.build_packet(CMD_READ_WORD, i2c_addr, register)
        resp = self._request(pkt)
        if resp["ok"] and len(resp.get("raw", b"")) >= 10:
            resp["value"] = struct.unpack("<H", resp["raw"][8:10])[0]
        else:
            resp["value"] = None
        return resp

    def write_word(self, i2c_addr: int, register: int, value: int) -> dict:
        data = struct.pack("<H", value & 0xFFFF)
        pkt = self.build_packet(CMD_WRITE_WORD, i2c_addr, register, data)
        return self._request(pkt, write_submit=True)

    def read_byte(self, i2c_addr: int, register: int) -> dict:
        pkt = self.build_packet(CMD_READ_BYTE, i2c_addr, register)
        resp = self._request(pkt)
        resp["value"] = resp["raw"][8] if resp["ok"] and len(resp.get("raw", b"")) > 8 else None
        return resp

    def write_byte(self, i2c_addr: int, register: int, value: int) -> dict:
        pkt = self.build_packet(CMD_WRITE_BYTE, i2c_addr, register, bytes([value & 0xFF]))
        return self._request(pkt, write_submit=True)

    def read_block(self, i2c_addr: int, register: int) -> dict:
        pkt = self.build_packet(CMD_READ_BLOCK, i2c_addr, register)
        resp = self._request(pkt)
        if resp["ok"] and len(resp.get("raw", b"")) > 9:
            blen = resp["raw"][8]
            resp["block"] = bytes(resp["raw"][9 : 9 + blen])
        else:
            resp["block"] = None
        return resp

    def write_block(self, i2c_addr: int, register: int, data: bytes | bytearray) -> dict:
        if len(data) > 52:
            return {"ok": False, "status_text": "Block too large (max 52)"}
        pkt = self.build_packet(CMD_WRITE_BLOCK, i2c_addr, register, bytes([len(data)]) + bytes(data))
        return self._request(pkt, write_submit=True)

    def send_byte(self, i2c_addr: int, command: int) -> dict:
        pkt = self.build_packet(CMD_COMMAND, i2c_addr, command)
        return self._request(pkt, write_submit=True)

    def get_device_info(self) -> dict:
        if self._handle is None:
            return {"ok": False, "status_text": "Not open"}
        info = self._be.get_info(self._handle, self._path)
        info["caps"] = self._caps
        return info

    def probe_command(
        self, cmd: int, i2c_addr: int = 0x08, register: int = 0x00, data: bytes = b"", write_submit: bool = False
    ) -> dict:
        pkt = self.build_packet(cmd, i2c_addr, register, data)
        resp = self._request(pkt, write_submit=write_submit)
        resp["probe_cmd"] = cmd
        return resp


# ===========================================================================
# TI_EV2300 -- public driver class (toolkit interface)
# ===========================================================================


class TI_EV2300:
    """TI EV2300A USB-to-I2C/SMBus adapter driver.

    Does NOT inherit from DeviceManager — communicates via USB HID,
    not PyVISA/SCPI.  Follows the same non-standard pattern as
    :class:`NI_PXIe_4139`.

    Usage::

        ev = TI_EV2300()
        ev.connect()
        result = ev.read_word(0x08, 0x00)
        print(result["value"])
        ev.disconnect()

    Linux permissions -- create ``/etc/udev/rules.d/99-ev2300.rules``::

        SUBSYSTEM=="hidraw", ATTRS{idVendor}=="0451", ATTRS{idProduct}=="0036", MODE="0666"

    Then: ``sudo udevadm control --reload-rules && sudo udevadm trigger``
    """

    VID = VID
    PID_FLASHED = PID_FLASHED
    PID_BOOTLOADER = PID_BOOTLOADER

    def __init__(self, resource_name: str = "auto") -> None:
        self.resource_name = resource_name
        self._core: _EV2300Core | None = None
        self._device_info: dict = {}

    # ------------------------------------------------------------------
    # Lifecycle (toolkit convention)
    # ------------------------------------------------------------------

    def connect(self) -> None:
        """Open the EV2300 device."""
        self._core = _EV2300Core()
        path = None if self.resource_name == "auto" else self.resource_name
        result = self._core.open(path)
        if not result["ok"]:
            self._core = None
            raise ConnectionError(f"EV2300: {result['status_text']}")

    def disconnect(self) -> None:
        """Close the EV2300 device."""
        if self._core is not None:
            self._core.close()
            self._core = None

    def __enter__(self) -> TI_EV2300:
        self.connect()
        return self

    def __exit__(self, *args: object) -> bool:
        self.disconnect()
        return False

    @property
    def is_open(self) -> bool:
        return self._core is not None and self._core.is_open

    # ------------------------------------------------------------------
    # SMBus operations
    # ------------------------------------------------------------------

    def read_word(self, i2c_addr: int, register: int) -> dict:
        """Read a 16-bit LE word from *register* on *i2c_addr*."""
        self._require_open()
        return self._core.read_word(i2c_addr, register)

    def write_word(self, i2c_addr: int, register: int, value: int) -> dict:
        """Write a 16-bit LE word to *register* on *i2c_addr*."""
        self._require_open()
        return self._core.write_word(i2c_addr, register, value)

    def read_byte(self, i2c_addr: int, register: int) -> dict:
        """Read a single byte from *register* on *i2c_addr*."""
        self._require_open()
        return self._core.read_byte(i2c_addr, register)

    def write_byte(self, i2c_addr: int, register: int, value: int) -> dict:
        """Write a single byte to *register* on *i2c_addr*."""
        self._require_open()
        return self._core.write_byte(i2c_addr, register, value)

    def read_block(self, i2c_addr: int, register: int) -> dict:
        """Read a variable-length block from *register* on *i2c_addr*."""
        self._require_open()
        return self._core.read_block(i2c_addr, register)

    def write_block(self, i2c_addr: int, register: int, data: bytes | bytearray) -> dict:
        """Write a block (max 52 bytes) to *register* on *i2c_addr*."""
        self._require_open()
        return self._core.write_block(i2c_addr, register, data)

    def send_byte(self, i2c_addr: int, command: int) -> dict:
        """SMBus Send Byte (no register address)."""
        self._require_open()
        return self._core.send_byte(i2c_addr, command)

    def get_device_info(self) -> dict:
        """Return VID, PID, serial, product, manufacturer."""
        self._require_open()
        return self._core.get_device_info()

    def probe_command(
        self, cmd: int, i2c_addr: int = 0x08, register: int = 0x00, data: bytes = b"", write_submit: bool = False
    ) -> dict:
        """Send an arbitrary command and return raw response."""
        self._require_open()
        return self._core.probe_command(cmd, i2c_addr, register, data, write_submit)

    # ------------------------------------------------------------------
    # SCPI compatibility stubs
    # ------------------------------------------------------------------

    def query(self, cmd: str, **kwargs: object) -> str:
        """Return an IDN-like string for compatibility with the toolkit."""
        return f"Texas Instruments,EV2300A,{self.resource_name},pure-python-hid"

    def send_command(self, cmd: str) -> None:
        """No-op SCPI compatibility stub."""

    def reset(self) -> None:
        """Disconnect and reconnect."""
        if self.is_open:
            self.disconnect()
            self.connect()

    def clear_status(self) -> None:
        """No-op SCPI compatibility stub."""

    # ------------------------------------------------------------------
    # SMBusTransport protocol compatibility
    # ------------------------------------------------------------------

    def open_device(self, adapter: str = "auto") -> dict:
        """SMBusTransport compat: open the device."""
        try:
            self.connect()
            return {"ok": True, "status": 0}
        except ConnectionError as e:
            return {"ok": False, "status": -1, "status_text": str(e)}

    def close_device(self) -> int:
        """SMBusTransport compat: close the device."""
        self.disconnect()
        return 0

    def i2c_power(self, enabled: int = 1) -> dict:
        """SMBusTransport compat: no-op (I2C always powered when open)."""
        return {"ok": True, "status": 0, "enabled": int(enabled)}

    def read_smbus_word(self, i2c_addr: int, register_addr: int, pec: int = 0) -> dict:
        """SMBusTransport compat: read 16-bit word."""
        r = self.read_word(i2c_addr, register_addr)
        return {
            "ok": r["ok"],
            "status": 0 if r["ok"] else -1,
            "value": r.get("value"),
            "status_text": r.get("status_text", ""),
        }

    def write_smbus_byte(self, i2c_addr: int, register_addr: int, value: int, pec: int = 0) -> dict:
        """SMBusTransport compat: write single byte."""
        r = self.write_byte(i2c_addr, register_addr, value)
        return {
            "ok": r["ok"],
            "status": 0 if r["ok"] else -1,
            "register": register_addr,
            "value": value & 0xFF,
            "status_text": r.get("status_text", ""),
        }

    # ------------------------------------------------------------------
    # Static discovery helpers
    # ------------------------------------------------------------------

    @staticmethod
    def enumerate_devices() -> list[dict]:
        """Return list of all EV2300 devices found on the system."""
        try:
            be = _get_or_create_backend()
            return [d for d in be.enumerate() if d["vid"] == VID and d["pid"] == PID_FLASHED]
        except (OSError, ImportError):
            return []

    @staticmethod
    def is_available() -> bool:
        """Return True if at least one EV2300 is connected."""
        return len(TI_EV2300.enumerate_devices()) > 0

    # Expose static helpers for testing
    build_packet = staticmethod(_EV2300Core.build_packet)
    parse_response = staticmethod(_EV2300Core.parse_response)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _require_open(self) -> None:
        if self._core is None or not self._core.is_open:
            raise ConnectionError("EV2300 not connected. Call connect() first.")
