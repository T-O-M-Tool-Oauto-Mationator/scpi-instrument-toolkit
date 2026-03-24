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
    mock_session.measure_multiple.return_value = [
        MagicMock(voltage=0.0, current=0.0)
    ]

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
    """Return a factory that builds an InstrumentRepl wired to a given devices dict."""

    def _make(devices):
        from lab_instruments.src import discovery as _disc

        monkeypatch.setattr(_disc.InstrumentDiscovery, "__init__", lambda self: None)
        monkeypatch.setattr(_disc.InstrumentDiscovery, "scan", lambda self, verbose=True: devices)
        from lab_instruments.repl import InstrumentRepl

        repl = InstrumentRepl()
        # Wait for the background scan (including its safe_all() call) to finish
        # before the test manipulates device state — prevents a race where
        # safe_all() resets state set by a test command.
        repl._scan_thread.join(timeout=5.0)
        if repl._scan_thread.is_alive():
            # Thread didn't finish in time; ensure the event is set so any
            # subsequent _scan_done.wait() calls don't block indefinitely.
            repl._scan_done.wait(timeout=5.0)
        repl.devices = devices
        return repl

    return _make
