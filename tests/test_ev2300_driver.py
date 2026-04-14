"""Driver-level unit tests for the TI EV2300."""

from unittest.mock import MagicMock, patch

import pytest

from lab_instruments.src.ev2300 import (
    BUF_SIZE,
    CMD_ERROR,
    CMD_READ_BLOCK,
    CMD_READ_BYTE,
    CMD_READ_WORD,
    CMD_SUBMIT,
    CMD_WRITE_BYTE,
    CMD_WRITE_WORD,
    FRAME_END,
    FRAME_MARKER,
    RESP_FLAG,
    TI_EV2300,
    _EV2300Core,
    crc8,
)

# =========================================================================
# CRC-8 tests
# =========================================================================


class TestCRC8:
    def test_empty(self):
        assert crc8(b"") == 0x00

    def test_single_zero(self):
        assert crc8(b"\x00") == 0x00

    def test_single_one(self):
        assert crc8(b"\x01") == 0x07

    def test_known_vector(self):
        # CRC-8 poly=0x07 of "123456789"
        data = bytes([0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39])
        assert crc8(data) == 0xF4

    def test_bytearray(self):
        assert crc8(bytearray(b"\x01")) == crc8(b"\x01")


# =========================================================================
# Packet builder tests
# =========================================================================


class TestBuildPacket:
    def test_submit_packet(self):
        pkt = _EV2300Core.build_packet(CMD_SUBMIT)
        assert pkt[0] == 8  # length
        assert pkt[1] == FRAME_MARKER
        assert pkt[2] == CMD_SUBMIT
        assert pkt[8] == FRAME_END

    def test_read_word_packet(self):
        pkt = _EV2300Core.build_packet(CMD_READ_WORD, i2c_addr=0x08, reg=0x00)
        assert pkt[1] == FRAME_MARKER
        assert pkt[2] == CMD_READ_WORD
        assert pkt[7] == 0x08 << 1  # i2c addr left-shifted
        assert pkt[8] == 0x00  # register
        # CRC and FRAME_END should be in the right place
        plen = pkt[6]
        assert plen == 2  # i2c_addr + reg
        crc_end = 7 + plen
        assert pkt[crc_end] == crc8(pkt[2:crc_end])
        assert pkt[crc_end + 1] == FRAME_END

    def test_write_word_packet(self):
        import struct

        data = struct.pack("<H", 0x1234)
        pkt = _EV2300Core.build_packet(CMD_WRITE_WORD, i2c_addr=0x08, reg=0x05, data=data)
        assert pkt[2] == CMD_WRITE_WORD
        assert pkt[7] == 0x08 << 1
        assert pkt[8] == 0x05
        assert pkt[9] == 0x34  # low byte
        assert pkt[10] == 0x12  # high byte

    def test_read_block_packet(self):
        pkt = _EV2300Core.build_packet(CMD_READ_BLOCK, i2c_addr=0x08, reg=0x0B)
        assert pkt[2] == CMD_READ_BLOCK

    def test_write_byte_packet(self):
        pkt = _EV2300Core.build_packet(CMD_WRITE_BYTE, i2c_addr=0x08, reg=0x04, data=bytes([0xFF]))
        assert pkt[2] == CMD_WRITE_BYTE
        assert pkt[9] == 0xFF

    def test_packet_is_64_bytes(self):
        pkt = _EV2300Core.build_packet(CMD_READ_WORD, 0x08, 0x00)
        assert len(pkt) == BUF_SIZE

    def test_crc_round_trip(self):
        pkt = _EV2300Core.build_packet(CMD_READ_WORD, 0x08, 0x00)
        plen = pkt[6]
        crc_end = 7 + plen
        assert pkt[crc_end] == crc8(pkt[2:crc_end])


# =========================================================================
# Response parser tests
# =========================================================================


class TestParseResponse:
    def _make_response(self, cmd: int, payload: bytes = b"", ok: bool = True) -> bytearray:
        """Build a response packet matching the EV2300 protocol.

        parse_response expects: raw[length-1] == crc8(raw[2:length-1])
        So CRC is at position (length-1), computed over raw[2:length-1].
        """
        buf = bytearray(BUF_SIZE)
        plen = len(payload)
        buf[1] = FRAME_MARKER
        buf[2] = cmd
        buf[6] = plen
        buf[7 : 7 + plen] = payload
        # length field: frame_end is at crc_pos+1, crc at crc_pos
        # crc_pos = 7 + plen, frame_end = 7 + plen + 1
        # parse_response uses: crc at raw[length-1], checked against crc8(raw[2:length-1])
        # So length = 7 + plen + 1 (to include CRC at length-1)
        crc_pos = 7 + plen
        length = crc_pos + 1
        buf[0] = length
        buf[crc_pos] = crc8(buf[2:crc_pos]) if ok else 0xFF
        return buf

    def test_valid_response(self):
        buf = self._make_response(CMD_READ_WORD | RESP_FLAG, b"\x10\x00")
        resp = _EV2300Core.parse_response(buf)
        assert resp["ok"] is True
        assert resp["cmd"] == CMD_READ_WORD | RESP_FLAG
        assert resp["error"] is False

    def test_short_response(self):
        resp = _EV2300Core.parse_response(b"\x00\x01\x02")
        assert resp["ok"] is False
        assert resp["error"] is True

    def test_none_response(self):
        resp = _EV2300Core.parse_response(None)
        assert resp["ok"] is False

    def test_bad_marker(self):
        buf = bytearray(BUF_SIZE)
        buf[0] = 10
        buf[1] = 0x00  # bad marker
        buf[2] = 0x41
        resp = _EV2300Core.parse_response(buf)
        assert resp["ok"] is False
        assert "Bad marker" in resp.get("status_text", "")

    def test_error_response(self):
        buf = bytearray(BUF_SIZE)
        buf[0] = 10
        buf[1] = FRAME_MARKER
        buf[2] = CMD_ERROR
        resp = _EV2300Core.parse_response(buf)
        assert resp["ok"] is False
        assert resp["error"] is True

    def test_success_flag_determines_ok(self):
        # Command with RESP_FLAG set = success
        buf = self._make_response(CMD_READ_WORD | RESP_FLAG, b"\x10\x00")
        resp = _EV2300Core.parse_response(buf)
        assert resp["ok"] is True
        # Command without RESP_FLAG = not ok
        buf2 = self._make_response(CMD_READ_WORD, b"\x10\x00")
        resp2 = _EV2300Core.parse_response(buf2)
        assert resp2["ok"] is False


# =========================================================================
# Connection tests
# =========================================================================


class TestConnect:
    def test_connect_success(self, ev2300):
        dev, mock_be = ev2300
        assert dev.is_open

    def test_resource_name(self, ev2300):
        dev, _ = ev2300
        assert dev.resource_name == "/dev/hidraw_mock"

    def test_connect_not_found(self):
        mock_be = MagicMock()
        mock_be.find.return_value = None

        with patch("lab_instruments.src.ev2300._get_or_create_backend", return_value=mock_be):
            dev = TI_EV2300("auto")
            with pytest.raises(ConnectionError, match="not found"):
                dev.connect()

    def test_connect_bootloader(self):
        mock_be = MagicMock()
        mock_be.find.side_effect = lambda vid, pid: "bootloader_path" if pid == 0x2136 else None

        with patch("lab_instruments.src.ev2300._get_or_create_backend", return_value=mock_be):
            dev = TI_EV2300("auto")
            with pytest.raises(ConnectionError, match="bootloader"):
                dev.connect()


class TestDisconnect:
    def test_disconnect(self, ev2300):
        dev, mock_be = ev2300
        dev.disconnect()
        assert not dev.is_open
        mock_be.close.assert_called_once()

    def test_disconnect_when_not_open(self):
        dev = TI_EV2300()
        dev.disconnect()  # Should not raise


class TestContextManager:
    def test_context_manager(self):
        mock_be = MagicMock()
        mock_be.find.return_value = "/dev/mock"
        mock_be.open.return_value = 42
        mock_be.get_caps.return_value = None

        with patch("lab_instruments.src.ev2300._get_or_create_backend", return_value=mock_be):
            with TI_EV2300("auto") as dev:
                assert dev.is_open
            assert not dev.is_open


# =========================================================================
# SMBus operation tests
# =========================================================================


class TestReadWord:
    def test_read_word_success(self, ev2300):
        dev, _ = ev2300
        result = dev.read_word(0x08, 0x00)
        assert result["ok"] is True
        assert result["value"] == 0x1234

    def test_read_word_calls_write_and_read(self, ev2300):
        dev, mock_be = ev2300
        dev.read_word(0x08, 0x00)
        assert mock_be.write.called
        assert mock_be.read.called


class TestWriteWord:
    def test_write_word_success(self, ev2300):
        dev, mock_be = ev2300
        # Write operations send two packets (command + submit)
        mock_be.write.return_value = True
        # Build a success response
        buf = bytearray(64)
        buf[0] = 10
        buf[1] = FRAME_MARKER
        buf[2] = CMD_WRITE_WORD | RESP_FLAG
        buf[6] = 0
        buf[9] = crc8(buf[2:9])
        buf[10] = FRAME_END
        mock_be.read.return_value = bytes(buf)
        dev.write_word(0x08, 0x00, 0x5678)
        # write is called twice: command + submit
        assert mock_be.write.call_count >= 2

    def test_write_word_not_connected(self):
        dev = TI_EV2300()
        with pytest.raises(ConnectionError):
            dev.write_word(0x08, 0x00, 0x1234)


class TestReadByte:
    def test_read_byte_success(self, ev2300):
        dev, mock_be = ev2300
        # Build a read_byte response
        buf = bytearray(64)
        buf[0] = 11
        buf[1] = FRAME_MARKER
        buf[2] = CMD_READ_BYTE | RESP_FLAG
        buf[6] = 2
        buf[7] = 0x10
        buf[8] = 0xAB  # value
        buf[10] = crc8(buf[2:10])
        buf[11] = FRAME_END
        mock_be.read.return_value = bytes(buf)
        result = dev.read_byte(0x08, 0x00)
        assert result["ok"] is True
        assert result["value"] == 0xAB


class TestWriteByte:
    def test_write_byte_not_connected(self):
        dev = TI_EV2300()
        with pytest.raises(ConnectionError):
            dev.write_byte(0x08, 0x00, 0xFF)


class TestReadBlock:
    def test_read_block_success(self, ev2300):
        dev, mock_be = ev2300
        # Build a read_block response with 3 bytes of data
        buf = bytearray(64)
        buf[1] = FRAME_MARKER
        buf[2] = CMD_READ_BLOCK | RESP_FLAG
        buf[6] = 5  # payload len
        buf[7] = 0x10  # i2c addr
        buf[8] = 3  # block length
        buf[9] = 0xAA
        buf[10] = 0xBB
        buf[11] = 0xCC
        length = 2 + 1 + 3 + 1 + 5 + 1 + 1
        buf[0] = length
        crc_end = 7 + 5
        buf[crc_end] = crc8(buf[2:crc_end])
        mock_be.read.return_value = bytes(buf)
        result = dev.read_block(0x08, 0x0B)
        assert result["ok"] is True
        assert result["block"] == b"\xaa\xbb\xcc"


class TestWriteBlock:
    def test_write_block_too_large(self, ev2300):
        dev, _ = ev2300
        result = dev.write_block(0x08, 0x00, b"\x00" * 53)
        assert result["ok"] is False
        assert "too large" in result.get("status_text", "").lower()


class TestSendByte:
    def test_send_byte_not_connected(self):
        dev = TI_EV2300()
        with pytest.raises(ConnectionError):
            dev.send_byte(0x08, 0x00)


# =========================================================================
# Device info tests
# =========================================================================


class TestDeviceInfo:
    def test_get_device_info(self, ev2300):
        dev, _ = ev2300
        info = dev.get_device_info()
        assert info["ok"] is True
        assert info["vid"] == "0x0451"
        assert info["pid"] == "0x0036"
        assert info["product"] == "EV2300A"

    def test_get_device_info_not_connected(self):
        dev = TI_EV2300()
        with pytest.raises(ConnectionError):
            dev.get_device_info()


# =========================================================================
# SCPI compatibility stubs
# =========================================================================


class TestStubs:
    def test_query_returns_idn(self, ev2300):
        dev, _ = ev2300
        idn = dev.query("*IDN?")
        assert "Texas Instruments" in idn
        assert "EV2300A" in idn

    def test_send_command_noop(self, ev2300):
        dev, _ = ev2300
        dev.send_command("*RST")  # Should not raise

    def test_clear_status_noop(self, ev2300):
        dev, _ = ev2300
        dev.clear_status()  # Should not raise


# =========================================================================
# SMBusTransport protocol tests
# =========================================================================


class TestSMBusTransport:
    def test_open_device(self):
        mock_be = MagicMock()
        mock_be.find.return_value = "/dev/mock"
        mock_be.open.return_value = 42
        mock_be.get_caps.return_value = None

        with patch("lab_instruments.src.ev2300._get_or_create_backend", return_value=mock_be):
            dev = TI_EV2300()
            result = dev.open_device()
            assert result["ok"] is True
            dev.disconnect()

    def test_close_device(self, ev2300):
        dev, _ = ev2300
        ret = dev.close_device()
        assert ret == 0
        assert not dev.is_open

    def test_i2c_power(self, ev2300):
        dev, _ = ev2300
        result = dev.i2c_power(1)
        assert result["ok"] is True

    def test_read_smbus_word(self, ev2300):
        dev, _ = ev2300
        result = dev.read_smbus_word(0x08, 0x00)
        assert result["ok"] is True
        assert result["value"] == 0x1234


# =========================================================================
# Static helpers
# =========================================================================


class TestStaticHelpers:
    def test_enumerate_devices(self):
        mock_be = MagicMock()
        mock_be.enumerate.return_value = [
            {"path": "/dev/hidraw0", "path_str": "/dev/hidraw0", "vid": 0x0451, "pid": 0x0036, "version": 0},
            {"path": "/dev/hidraw1", "path_str": "/dev/hidraw1", "vid": 0x1234, "pid": 0x5678, "version": 0},
        ]
        with patch("lab_instruments.src.ev2300._get_or_create_backend", return_value=mock_be):
            devices = TI_EV2300.enumerate_devices()
            assert len(devices) == 1
            assert devices[0]["vid"] == 0x0451

    def test_is_available_true(self):
        mock_be = MagicMock()
        mock_be.enumerate.return_value = [
            {"path": "/dev/hidraw0", "path_str": "/dev/hidraw0", "vid": 0x0451, "pid": 0x0036, "version": 0},
        ]
        with patch("lab_instruments.src.ev2300._get_or_create_backend", return_value=mock_be):
            assert TI_EV2300.is_available() is True

    def test_is_available_false(self):
        mock_be = MagicMock()
        mock_be.enumerate.return_value = []
        with patch("lab_instruments.src.ev2300._get_or_create_backend", return_value=mock_be):
            assert TI_EV2300.is_available() is False

    def test_build_packet_accessible(self):
        pkt = TI_EV2300.build_packet(CMD_READ_WORD, 0x08, 0x00)
        assert len(pkt) == BUF_SIZE

    def test_parse_response_accessible(self):
        resp = TI_EV2300.parse_response(None)
        assert resp["ok"] is False


# =========================================================================
# wait_for_bq tests
# =========================================================================


class TestWaitForBq:
    def test_returns_immediately_on_first_success(self, ev2300, monkeypatch):
        """Returns without sleeping when read_byte succeeds on the first try."""
        dev, _ = ev2300
        dev.read_byte = MagicMock(return_value={"ok": True, "value": 0x19})
        sleep_calls = []
        monkeypatch.setattr("time.sleep", lambda s: sleep_calls.append(s))
        dev.wait_for_bq(timeout_s=30.0)
        dev.read_byte.assert_called_once_with(0x08, 0x0B)
        assert sleep_calls == []

    def test_retries_then_succeeds(self, ev2300, monkeypatch):
        """Retries when read_byte fails, returns when it succeeds on a later attempt."""
        dev, _ = ev2300
        # First two calls fail (both addresses on first poll), third succeeds
        dev.read_byte = MagicMock(
            side_effect=[
                {"ok": False},  # 0x08, poll 1
                {"ok": False},  # 0x18, poll 1
                {"ok": True, "value": 0x19},  # 0x08, poll 2
            ]
        )
        monkeypatch.setattr("time.sleep", lambda _: None)
        # Always return 0 so deadline = 30 and every subsequent check is well inside
        # the window -- independent of how many times monotonic() is called.
        monkeypatch.setattr("time.monotonic", lambda: 0.0)
        dev.wait_for_bq(timeout_s=30.0)
        assert dev.read_byte.call_count == 3

    def test_raises_timeout_when_never_succeeds(self, ev2300, monkeypatch):
        """Raises TimeoutError when read_byte never returns ok within the timeout."""
        dev, _ = ev2300
        dev.read_byte = MagicMock(return_value={"ok": False})
        monkeypatch.setattr("time.sleep", lambda _: None)
        # First call sets deadline (returns 0), second call is past deadline (returns 31)
        _seq = iter([0, 31])
        monkeypatch.setattr("time.monotonic", lambda: next(_seq))
        with pytest.raises(TimeoutError, match="BQ76920 did not respond"):
            dev.wait_for_bq(timeout_s=30.0)
