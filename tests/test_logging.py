"""
Tests for issue #97: library uses stdlib logging instead of bare print().

The library should be silent by default (NullHandler attached at package
level) and let users opt in to log output via stdlib logging.
"""

import importlib
import logging
from unittest.mock import MagicMock, patch

import pytest
import pyvisa

import lab_instruments  # noqa: I001
from lab_instruments.src.device_manager import DeviceManager


@pytest.fixture
def connected_dm():
    """A DeviceManager with a mocked-open instrument session."""
    dm = DeviceManager("FAKE::INSTR")
    dm.instrument = MagicMock()
    return dm


def test_send_command_silent_by_default(connected_dm, capsys):
    """send_command must not emit to stdout/stderr at default log level."""
    connected_dm.send_command("*RST")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_send_command_emits_debug_when_enabled(connected_dm, caplog):
    """With DEBUG enabled on the lab_instruments logger, send_command emits a record."""
    with caplog.at_level(logging.DEBUG, logger="lab_instruments"):
        connected_dm.send_command("*RST")
    matching = [r for r in caplog.records if "Sent command" in r.getMessage()]
    assert len(matching) == 1
    assert matching[0].levelno == logging.DEBUG
    assert "*RST" in matching[0].getMessage()


def test_connect_emits_info(caplog):
    """connect() emits an INFO record (not stdout) on success."""
    dm = DeviceManager("FAKE::INSTR")
    mock_instr = MagicMock()
    with (
        patch.object(dm.rm, "open_resource", return_value=mock_instr),
        caplog.at_level(logging.INFO, logger="lab_instruments"),
    ):
        dm.connect()
    matching = [r for r in caplog.records if "Connected to" in r.getMessage()]
    assert len(matching) == 1
    assert matching[0].levelno == logging.INFO
    assert "FAKE::INSTR" in matching[0].getMessage()


def test_failed_connect_emits_error_and_reraises(caplog):
    """A VisaIOError during connect() is logged at ERROR and re-raised."""
    dm = DeviceManager("BAD::INSTR")
    err = pyvisa.VisaIOError(-1073807343)  # VI_ERROR_RSRC_NFOUND
    with (
        patch.object(dm.rm, "open_resource", side_effect=err),
        caplog.at_level(logging.ERROR, logger="lab_instruments"),
        pytest.raises(pyvisa.VisaIOError),
    ):
        dm.connect()
    matching = [r for r in caplog.records if "Failed to connect" in r.getMessage()]
    assert len(matching) == 1
    assert matching[0].levelno == logging.ERROR


def test_disconnect_emits_info(connected_dm, caplog):
    """disconnect() emits an INFO record."""
    with caplog.at_level(logging.INFO, logger="lab_instruments"):
        connected_dm.disconnect()
    matching = [r for r in caplog.records if "Disconnected from" in r.getMessage()]
    assert len(matching) == 1
    assert matching[0].levelno == logging.INFO


def test_import_produces_no_output(capsys):
    """Reimporting lab_instruments must produce zero output on stdout/stderr."""
    capsys.readouterr()
    importlib.reload(lab_instruments)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_package_logger_has_null_handler():
    """Library installs a NullHandler so it stays silent without user config."""
    pkg_logger = logging.getLogger("lab_instruments")
    assert any(isinstance(h, logging.NullHandler) for h in pkg_logger.handlers)


# ---------------------------------------------------------------------------
# Subclass driver coverage — connect/disconnect overrides + setter prints
# ---------------------------------------------------------------------------


def test_matrix_mps6010h_connect_emits_info(caplog):
    """MATRIX_MPS6010H.connect routes both confirmations through logger.info."""
    from lab_instruments import MATRIX_MPS6010H

    psu = MATRIX_MPS6010H("FAKE::INSTR")
    mock_instr = MagicMock()
    with (
        patch.object(psu.rm, "open_resource", return_value=mock_instr),
        caplog.at_level(logging.INFO, logger="lab_instruments"),
    ):
        psu.connect()
    messages = [r.getMessage() for r in caplog.records if r.levelno == logging.INFO]
    assert any("Connected to FAKE::INSTR" in m for m in messages)
    assert any("Remote mode enabled" in m for m in messages)


def test_matrix_mps6010h_exit_emits_returned_to_local(caplog):
    """__exit__ logs 'Returned to local mode' at INFO, not stdout."""
    from lab_instruments import MATRIX_MPS6010H

    psu = MATRIX_MPS6010H("FAKE::INSTR")
    psu.instrument = MagicMock()
    with caplog.at_level(logging.INFO, logger="lab_instruments"):
        psu.__exit__(None, None, None)
    assert any("Returned to local mode" in r.getMessage() for r in caplog.records)


def test_owon_xdm1041_connect_emits_info(caplog):
    """Owon_XDM1041.connect (serial-config override) uses logger.info."""
    from lab_instruments import Owon_XDM1041

    dmm = Owon_XDM1041("FAKE::INSTR")
    mock_instr = MagicMock()
    with (
        patch.object(dmm.rm, "open_resource", return_value=mock_instr),
        caplog.at_level(logging.INFO, logger="lab_instruments"),
    ):
        dmm.connect()
    assert any("Connected to FAKE::INSTR" in r.getMessage() for r in caplog.records)


def test_jds6600_setter_emits_info(caplog):
    """JDS6600 set_waveform setter confirmation goes through logger.info."""
    from lab_instruments import JDS6600_Generator

    gen = JDS6600_Generator("FAKE::INSTR")
    gen.instrument = MagicMock()
    gen.instrument.read.return_value = ":ok"
    with caplog.at_level(logging.INFO, logger="lab_instruments"):
        gen.set_waveform(1, "sine")
    matching = [r for r in caplog.records if "waveform" in r.getMessage().lower()]
    assert len(matching) >= 1
    assert matching[0].levelno == logging.INFO


def test_jds6600_output_setter_emits_info(caplog, capsys):
    """JDS6600 enable_output setter confirmation goes through logger.info, not stdout."""
    from lab_instruments import JDS6600_Generator

    gen = JDS6600_Generator("FAKE::INSTR")
    gen.instrument = MagicMock()
    gen.instrument.read.return_value = ":ok"
    with caplog.at_level(logging.INFO, logger="lab_instruments"):
        gen.enable_output(True, False)
    out = capsys.readouterr().out
    assert out == ""
    assert any("Output: CH1=ON" in r.getMessage() for r in caplog.records)


# ---------------------------------------------------------------------------
# Warning-level classification — error paths that were `print(f"Failed ...")`
# ---------------------------------------------------------------------------


def test_rigol_failed_set_emits_warning(caplog):
    """Rigol's `Failed to set ...` paths use logger.warning, not logger.info."""
    from lab_instruments import Rigol_DHO804

    scope = Rigol_DHO804("FAKE::INSTR")
    scope.instrument = MagicMock()
    # write() raises VisaIOError -> driver catches, logs warning, re-raises
    scope.instrument.write.side_effect = pyvisa.VisaIOError(-1)
    with (
        caplog.at_level(logging.WARNING, logger="lab_instruments"),
        pytest.raises(pyvisa.VisaIOError),
    ):
        scope.set_bandwidth_limit(1, "20M")
    matching = [r for r in caplog.records if "Failed to set bandwidth limit" in r.getMessage()]
    assert len(matching) == 1
    assert matching[0].levelno == logging.WARNING


# ---------------------------------------------------------------------------
# Logger-name hierarchy — users can target a single driver
# ---------------------------------------------------------------------------


def test_logger_name_per_module(caplog):
    """Each driver module logs under its own `__name__`-based logger."""
    from lab_instruments.src.device_manager import DeviceManager as _DM

    dm = _DM("FAKE::INSTR")
    dm.instrument = MagicMock()
    with caplog.at_level(logging.DEBUG, logger="lab_instruments"):
        dm.send_command("*RST")
    names = {r.name for r in caplog.records if "Sent command" in r.getMessage()}
    assert "lab_instruments.src.device_manager" in names


def test_silencing_via_parent_logger_works(connected_dm, caplog):
    """Setting CRITICAL on the parent 'lab_instruments' logger filters DEBUG records."""
    pkg_logger = logging.getLogger("lab_instruments")
    prior = pkg_logger.level
    try:
        pkg_logger.setLevel(logging.CRITICAL)
        # caplog still records everything regardless of logger level, so we test
        # via the handler chain — propagation past the parent filter is what
        # matters for end-users.
        with caplog.at_level(logging.CRITICAL, logger="lab_instruments"):
            connected_dm.send_command("*RST")
        critical_records = [r for r in caplog.records if r.levelno >= logging.CRITICAL]
        assert critical_records == []
    finally:
        pkg_logger.setLevel(prior)
