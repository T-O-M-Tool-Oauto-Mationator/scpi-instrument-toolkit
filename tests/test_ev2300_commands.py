"""Tests for EV2300 REPL commands using MockEV2300."""

import pytest

from lab_instruments.mock_instruments import MockEV2300


@pytest.fixture
def ev2300_repl(make_repl):
    return make_repl({"ev2300": MockEV2300()})


class TestEv2300Info:
    def test_info(self, ev2300_repl, capsys):
        ev2300_repl.onecmd("ev2300 info")
        out = capsys.readouterr().out
        assert "0x0451" in out or "vid" in out.lower()


class TestEv2300ReadWord:
    def test_read_word_hex(self, ev2300_repl, capsys):
        ev2300_repl.onecmd("ev2300 read_word 0x08 0x00")
        out = capsys.readouterr().out
        assert "0x" in out or "(" in out

    def test_read_word_decimal(self, ev2300_repl, capsys):
        ev2300_repl.onecmd("ev2300 read_word 8 0")
        out = capsys.readouterr().out
        assert "0x" in out or "(" in out

    def test_read_word_missing_args(self, ev2300_repl, capsys):
        ev2300_repl.onecmd("ev2300 read_word")
        out = capsys.readouterr().out
        assert "Usage" in out or "usage" in out.lower()


class TestEv2300WriteWord:
    def test_write_word(self, ev2300_repl, capsys):
        ev2300_repl.onecmd("ev2300 write_word 0x08 0x00 0x1234")
        out = capsys.readouterr().out
        assert "Wrote" in out or "wrote" in out.lower()

    def test_write_word_missing_args(self, ev2300_repl, capsys):
        ev2300_repl.onecmd("ev2300 write_word 0x08 0x00")
        out = capsys.readouterr().out
        assert "Usage" in out or "usage" in out.lower()


class TestEv2300ReadByte:
    def test_read_byte(self, ev2300_repl, capsys):
        ev2300_repl.onecmd("ev2300 read_byte 0x08 0x04")
        out = capsys.readouterr().out
        assert "0x" in out


class TestEv2300WriteByte:
    def test_write_byte(self, ev2300_repl, capsys):
        ev2300_repl.onecmd("ev2300 write_byte 0x08 0x04 0xFF")
        out = capsys.readouterr().out
        assert "Wrote" in out or "wrote" in out.lower()


class TestEv2300ReadBlock:
    def test_read_block(self, ev2300_repl, capsys):
        ev2300_repl.onecmd("ev2300 read_block 0x08 0x00")
        out = capsys.readouterr().out
        assert "bytes" in out.lower()


class TestEv2300SendByte:
    def test_send_byte(self, ev2300_repl, capsys):
        ev2300_repl.onecmd("ev2300 send_byte 0x08 0x01")
        out = capsys.readouterr().out
        assert "Sent" in out or "sent" in out.lower()


class TestEv2300Help:
    def test_bare_command_shows_help(self, ev2300_repl, capsys):
        ev2300_repl.onecmd("ev2300")
        out = capsys.readouterr().out
        assert "read_word" in out

    def test_unknown_subcommand(self, ev2300_repl, capsys):
        ev2300_repl.onecmd("ev2300 bogus")
        out = capsys.readouterr().out
        assert "Unknown" in out or "unknown" in out.lower()


class TestEv2300Mock:
    def test_mock_read_word(self):
        mock = MockEV2300()
        result = mock.read_word(0x08, 0x00)
        assert result["ok"] is True
        assert 0 <= result["value"] <= 0xFFFF

    def test_mock_write_word(self):
        mock = MockEV2300()
        result = mock.write_word(0x08, 0x00, 0x1234)
        assert result["ok"] is True

    def test_mock_read_byte(self):
        mock = MockEV2300()
        result = mock.read_byte(0x08, 0x04)
        assert result["ok"] is True
        assert 0 <= result["value"] <= 0xFF

    def test_mock_write_byte(self):
        mock = MockEV2300()
        result = mock.write_byte(0x08, 0x04, 0xFF)
        assert result["ok"] is True

    def test_mock_read_block(self):
        mock = MockEV2300()
        result = mock.read_block(0x08, 0x0B)
        assert result["ok"] is True
        assert isinstance(result["block"], bytes)

    def test_mock_write_block(self):
        mock = MockEV2300()
        result = mock.write_block(0x08, 0x0B, b"\x19")
        assert result["ok"] is True

    def test_mock_send_byte(self):
        mock = MockEV2300()
        result = mock.send_byte(0x08, 0x01)
        assert result["ok"] is True

    def test_mock_get_device_info(self):
        mock = MockEV2300()
        info = mock.get_device_info()
        assert info["ok"] is True
        assert info["vid"] == "0x0451"

    def test_mock_connect_disconnect(self):
        mock = MockEV2300()
        assert not mock.is_open
        mock.connect()
        assert mock.is_open
        mock.disconnect()
        assert not mock.is_open

    def test_mock_query(self):
        mock = MockEV2300()
        idn = mock.query("*IDN?")
        assert "EV2300A" in idn

    def test_mock_smbus_transport(self):
        mock = MockEV2300()
        result = mock.open_device()
        assert result["ok"] is True
        result = mock.read_smbus_word(0x08, 0x00)
        assert result["ok"] is True
        result = mock.write_smbus_byte(0x08, 0x04, 0xFF)
        assert result["ok"] is True
        ret = mock.close_device()
        assert ret == 0

    def test_mock_probe_command(self):
        mock = MockEV2300()
        result = mock.probe_command(0x01)
        assert result["ok"] is True
        assert result["cmd"] == 0x41
