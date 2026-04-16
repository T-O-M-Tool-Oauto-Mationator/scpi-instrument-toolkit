"""
tests/conftest.py — Shared pytest fixtures for scpi-instrument-toolkit unit tests.

Two-layer pyvisa mocking strategy:
  Layer 1 (session scope): inject fake pyvisa module if not installed in CI.
  Layer 2 (function scope): patch pyvisa.ResourceManager per test.
"""

import sys
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# SAFETY CAP: bound the pytest process at 4 GB virtual memory.
#
# If a memory leak re-appears (historically the test suite grew to 26+ GB
# via atexit pinning of InstrumentRepl instances), this cap causes pytest to
# die with a clean MemoryError instead of OOM'ing the developer's machine.
# Steady-state usage for the full suite is well under 1 GB; 4 GB gives ~4x
# headroom while still killing runaway leaks fast. Best-effort: silently
# skipped on Windows or when the hard limit is already below our cap.
# ---------------------------------------------------------------------------
try:
    import resource as _resource

    _SAFETY_CAP_BYTES = 4 * 1024 * 1024 * 1024  # 4 GB
    _soft, _hard = _resource.getrlimit(_resource.RLIMIT_AS)
    _new_hard = _SAFETY_CAP_BYTES if _hard == _resource.RLIM_INFINITY else min(_hard, _SAFETY_CAP_BYTES)
    _new_soft = _SAFETY_CAP_BYTES if _soft == _resource.RLIM_INFINITY else min(_soft, _new_hard)
    _resource.setrlimit(_resource.RLIMIT_AS, (_new_soft, _new_hard))
except (ImportError, OSError, ValueError):
    pass

# ---------------------------------------------------------------------------
# Layer 0 — force all InstrumentRepl instances created during a test to skip
# process-level lifecycle registration (atexit, signal, readline, termios)
# and be closed at test teardown. This catches REPLs created through any
# path, including the 18 test files with file-local make_repl helpers that
# don't pass register_lifecycle=False directly. Without this safety net, a
# single InstrumentRepl() left in atexit pins its full object graph for the
# pytest process lifetime and causes the suite to OOM at ~2000 tests.
#
# Weakrefs avoid pinning the REPLs ourselves — a test that explicitly closes
# and drops its REPL can still be GC'd, so the regression tests in
# test_repl_lifecycle.py continue to work.
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _cap_repl_lifecycle(monkeypatch):
    import contextlib as _cl
    import weakref as _weakref

    from lab_instruments.repl.shell import InstrumentRepl

    tracked: list = []
    orig_init = InstrumentRepl.__init__

    def _traced_init(self, *args, **kwargs):
        kwargs.setdefault("register_lifecycle", False)
        orig_init(self, *args, **kwargs)
        tracked.append(_weakref.ref(self))

    monkeypatch.setattr(InstrumentRepl, "__init__", _traced_init)
    yield
    for wref in tracked:
        repl = wref()
        if repl is not None:
            with _cl.suppress(Exception):
                repl.close()


# ---------------------------------------------------------------------------
# Layer 1 — ensure pyvisa is importable even when not installed
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True, scope="session")
def ensure_pyvisa_mocked():
    """Inject a minimal fake pyvisa module if pyvisa is not installed."""
    if "pyvisa" not in sys.modules:
        fake = MagicMock()
        fake.VisaIOError = OSError
        fake.constants = MagicMock()
        fake.errors = MagicMock()
        fake.errors.VisaIOError = OSError
        sys.modules["pyvisa"] = fake
        sys.modules["pyvisa.constants"] = fake.constants
        sys.modules["pyvisa.errors"] = fake.errors
    yield


@pytest.fixture(autouse=True, scope="session")
def ensure_nidcpower_mocked():
    """Inject a minimal fake nidcpower module if nidcpower is not installed."""
    if "nidcpower" not in sys.modules:
        fake = MagicMock()
        fake.OutputFunction = MagicMock()
        fake.OutputFunction.DC_VOLTAGE = "DC_VOLTAGE"
        fake.OutputFunction.DC_CURRENT = "DC_CURRENT"
        fake.Session = MagicMock
        sys.modules["nidcpower"] = fake
    yield


# ---------------------------------------------------------------------------
# Layer 2 — per-test ResourceManager patch
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_visa_rm(ensure_pyvisa_mocked):
    """Patch pyvisa.ResourceManager; yield (mock_rm, mock_instrument)."""
    mock_instrument = MagicMock()
    mock_rm = MagicMock()
    mock_rm.open_resource.return_value = mock_instrument
    with patch("pyvisa.ResourceManager", return_value=mock_rm):
        yield mock_rm, mock_instrument


# ---------------------------------------------------------------------------
# Driver fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def hp_e3631a(mock_visa_rm):
    mock_rm, mock_instrument = mock_visa_rm
    from lab_instruments.src.hp_e3631a import HP_E3631A

    psu = HP_E3631A("GPIB::5::INSTR")
    psu.instrument = mock_instrument
    mock_instrument.reset_mock()
    return psu, mock_instrument


@pytest.fixture
def matrix_mps6010h(mock_visa_rm):
    mock_rm, mock_instrument = mock_visa_rm
    from lab_instruments.src.matrix_mps6010h import MATRIX_MPS6010H

    psu = MATRIX_MPS6010H("ASRL3::INSTR")
    psu.instrument = mock_instrument
    mock_instrument.reset_mock()
    return psu, mock_instrument


@pytest.fixture
def hp_34401a(mock_visa_rm):
    mock_rm, mock_instrument = mock_visa_rm
    from lab_instruments.src.hp_34401a import HP_34401A

    dmm = HP_34401A("GPIB::22::INSTR")
    dmm.instrument = mock_instrument
    mock_instrument.reset_mock()
    return dmm, mock_instrument


@pytest.fixture
def owon_xdm1041(mock_visa_rm):
    mock_rm, mock_instrument = mock_visa_rm
    from lab_instruments.src.owon_xdm1041 import Owon_XDM1041

    dmm = Owon_XDM1041("ASRL5::INSTR")
    dmm.instrument = mock_instrument
    mock_instrument.reset_mock()
    return dmm, mock_instrument


@pytest.fixture
def keysight_edu33212a(mock_visa_rm):
    mock_rm, mock_instrument = mock_visa_rm
    from lab_instruments.src.keysight_edu33212a import Keysight_EDU33212A

    awg = Keysight_EDU33212A("USB::0x2A8D::0x0000::INSTR")
    awg.instrument = mock_instrument
    mock_instrument.reset_mock()
    return awg, mock_instrument


@pytest.fixture
def keysight_edu36311a(mock_visa_rm):
    mock_rm, mock_instrument = mock_visa_rm
    from lab_instruments.src.keysight_edu36311a import Keysight_EDU36311A

    psu = Keysight_EDU36311A("USB::0x2A8D::0x9201::INSTR")
    psu.instrument = mock_instrument
    mock_instrument.reset_mock()
    return psu, mock_instrument


@pytest.fixture
def keysight_edu34450a(mock_visa_rm):
    mock_rm, mock_instrument = mock_visa_rm
    from lab_instruments.src.keysight_edu34450a import Keysight_EDU34450A

    dmm = Keysight_EDU34450A("USB::0x2A8D::0x8E01::INSTR")
    dmm.instrument = mock_instrument
    mock_instrument.reset_mock()
    return dmm, mock_instrument


@pytest.fixture
def bk_4063(mock_visa_rm):
    mock_rm, mock_instrument = mock_visa_rm
    from lab_instruments.src.bk_4063 import BK_4063

    awg = BK_4063("USB::0x1AB1::0x0000::INSTR")
    awg.instrument = mock_instrument
    mock_instrument.reset_mock()
    return awg, mock_instrument


@pytest.fixture
def jds6600_generator(mock_visa_rm, monkeypatch):
    mock_rm, mock_instrument = mock_visa_rm
    import lab_instruments.src.jds6600_generator as _mod

    # Suppress the 0.1 s sleep that _send_command inserts after every write
    monkeypatch.setattr(_mod.time, "sleep", lambda _: None)
    from lab_instruments.src.jds6600_generator import JDS6600_Generator

    gen = JDS6600_Generator("ASRL4::INSTR")
    gen.instrument = mock_instrument
    mock_instrument.reset_mock()
    return gen, mock_instrument


@pytest.fixture
def keysight_dsox1204g(mock_visa_rm):
    mock_rm, mock_instrument = mock_visa_rm
    from lab_instruments.src.keysight_dsox1204g import Keysight_DSOX1204G

    scope = Keysight_DSOX1204G("USB::0x2A8D::0x0396::CN63347188::INSTR")
    scope.instrument = mock_instrument
    mock_instrument.reset_mock()
    return scope, mock_instrument


@pytest.fixture
def rigol_dho804(mock_visa_rm):
    mock_rm, mock_instrument = mock_visa_rm
    from lab_instruments.src.rigol_dho804 import Rigol_DHO804

    scope = Rigol_DHO804("USB::0x1AB1::0x0000::INSTR")
    scope.instrument = mock_instrument
    mock_instrument.reset_mock()
    return scope, mock_instrument


@pytest.fixture
def tektronix_mso2024(mock_visa_rm):
    mock_rm, mock_instrument = mock_visa_rm
    from lab_instruments.src.tektronix_mso2024 import Tektronix_MSO2024

    scope = Tektronix_MSO2024("GPIB::7::INSTR")
    scope.instrument = mock_instrument
    mock_instrument.reset_mock()
    return scope, mock_instrument


@pytest.fixture
def ni_pxie_4139(ensure_nidcpower_mocked):
    mock_session = MagicMock()
    mock_session.voltage_level = 0.0
    mock_session.current_limit = 0.01
    mock_session.output_enabled = False
    mock_session.instrument_model = "PXIe-4139"
    import datetime

    mock_session.measure_multiple.return_value = [MagicMock(voltage=0.0, current=0.0, in_compliance=False)]
    mock_session.source_delay = datetime.timedelta(seconds=0.0)
    mock_session.samples_to_average = 1
    mock_session.query_in_compliance.return_value = False
    mock_session.read_current_temperature.return_value = 25.0

    with patch("nidcpower.Session", return_value=mock_session):
        from lab_instruments.src.ni_pxie_4139 import NI_PXIe_4139

        smu = NI_PXIe_4139("PXI1Slot2")
        smu.connect()
        mock_session.reset_mock()
        yield smu, mock_session


# ---------------------------------------------------------------------------
# REPL factory fixture
# ---------------------------------------------------------------------------


@pytest.fixture
def make_repl(monkeypatch):
    """Return a factory that builds an InstrumentRepl wired to a given devices dict.

    Every REPL created through this factory is tracked and closed during fixture
    teardown. `register_lifecycle=False` skips atexit/signal/readline/termios
    registration so REPLs do not accumulate in process-level registries across
    tests. Together these two measures prevent the pytest OOM caused by
    atexit pinning of REPL instances.
    """
    import contextlib as _contextlib

    created = []

    def _make(devices):
        from lab_instruments.src import discovery as _disc

        monkeypatch.setattr(_disc.InstrumentDiscovery, "__init__", lambda self: None)
        monkeypatch.setattr(_disc.InstrumentDiscovery, "scan", lambda self, verbose=True: devices)
        from lab_instruments.repl import InstrumentRepl

        repl = InstrumentRepl(register_lifecycle=False)
        # Wait for the background scan (including its safe_all() call) to finish
        # before the test manipulates device state — prevents a race where
        # safe_all() resets state set by a test command.
        repl._scan_thread.join(timeout=5.0)
        if repl._scan_thread.is_alive():
            # Thread didn't finish in time; ensure the event is set so any
            # subsequent _scan_done.wait() calls don't block indefinitely.
            repl._scan_done.wait(timeout=5.0)
        repl.devices = devices
        created.append(repl)
        return repl

    yield _make

    for repl in created:
        with _contextlib.suppress(Exception):
            repl.close()


@pytest.fixture
def ev2300():
    """Create a TI_EV2300 driver with mocked HID backend."""
    from lab_instruments.src.ev2300 import TI_EV2300, _EV2300Core, crc8

    mock_backend = MagicMock()

    # Enumerate returns one EV2300
    mock_backend.find.return_value = "/dev/hidraw_mock"
    mock_backend.open.return_value = 42
    mock_backend.get_caps.return_value = None
    mock_backend.get_info.return_value = {
        "ok": True,
        "vid": "0x0451",
        "pid": "0x0036",
        "serial": "TEST001",
        "product": "EV2300A",
        "manufacturer": "Texas Inst",
        "version": "0x0200",
    }

    def _make_read_word_response():
        """Build a realistic read_word success response."""
        buf = bytearray(64)
        buf[0] = 12  # length
        buf[1] = 0xAA  # marker
        buf[2] = 0x41  # CMD_READ_WORD | RESP_FLAG
        buf[3] = 0x00
        buf[4] = 0x00
        buf[5] = 0x00
        buf[6] = 2  # payload len
        buf[7] = 0x10  # i2c_addr byte
        buf[8] = 0x12  # high byte of value (big-endian, value = 0x1234)
        buf[9] = 0x34  # low byte of value
        # parse_response checks: raw[length-1] == crc8(raw[2:length-1])
        buf[11] = crc8(buf[2:11])
        buf[10] = 0x55  # not used in this position for this length
        # Correct: length=12, so CRC at buf[11], FRAME_END... actually parse uses length
        # Let me recalculate properly:
        # parse_response checks: raw[length-1] == crc8(raw[2:length-1])
        # length=12, so CRC at raw[11], computed over raw[2:11]
        buf[11] = crc8(buf[2:11])
        return bytes(buf)

    mock_backend.write.return_value = True
    mock_backend.read.return_value = _make_read_word_response()

    dev = TI_EV2300("/dev/hidraw_mock")
    # Manually create core with our mock backend
    core = _EV2300Core(backend=mock_backend)
    core.open("/dev/hidraw_mock")
    dev._core = core
    yield dev, mock_backend
