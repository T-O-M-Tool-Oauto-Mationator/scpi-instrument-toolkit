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

    def test_help_lists_i2c_power(self, ev2300_repl, capsys):
        """Regression: i2c_power was implemented in the driver but not surfaced
        in the REPL help, so users had no interactive way to enable the bus
        rail when reads NACKed after a fresh power-up."""
        ev2300_repl.onecmd("ev2300")
        out = capsys.readouterr().out
        assert "i2c_power" in out

    def test_fix_text_leads_with_boot(self, ev2300_repl, capsys):
        """Regression: the previous 'fix' text mentioned BOOT only as step 2.
        After characterising a real BQ76920 EVM cold-start we confirmed BOOT
        is mandatory after every power-up, so it has to be the first remedy."""
        ev2300_repl.onecmd("ev2300 fix")
        out = capsys.readouterr().out
        # The "BOOT" instruction should come before any 'disconnect ev2300' step
        assert "BOOT" in out
        boot_pos = out.find("BOOT")
        disconnect_pos = out.find("disconnect ev2300")
        assert boot_pos < disconnect_pos, "BOOT recovery step must precede disconnect/rescan"


class TestEv2300Cycle:
    """`ev2300 cycle` bundles disconnect + BOOT-press prompt + reconnect."""

    def test_cycle_runs_through_disconnect_reconnect(self, ev2300_repl, capsys, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda *a, **kw: "")
        ev2300_repl.onecmd("ev2300 cycle")
        out = capsys.readouterr().out
        assert "Disconnecting" in out
        assert "BOOT" in out
        assert "Reconnecting" in out
        assert "reconnected" in out.lower()

    def test_cycle_reminds_about_psu(self, ev2300_repl, capsys, monkeypatch):
        """The whole point of `cycle` (vs. unplugging USB) is that the PSU
        stays on so the BQ EVM remains powered. The reminder has to be in
        the output."""
        monkeypatch.setattr("builtins.input", lambda *a, **kw: "")
        ev2300_repl.onecmd("ev2300 cycle")
        out = capsys.readouterr().out
        assert "PSU" in out

    def test_cycle_cancel_via_keyboard_interrupt(self, ev2300_repl, capsys, monkeypatch):
        def raise_kbd(*a, **kw):
            raise KeyboardInterrupt

        monkeypatch.setattr("builtins.input", raise_kbd)
        ev2300_repl.onecmd("ev2300 cycle")
        out = capsys.readouterr().out
        assert "cancelled" in out.lower()

    def test_cycle_listed_in_help(self, ev2300_repl, capsys):
        ev2300_repl.onecmd("ev2300")
        out = capsys.readouterr().out
        assert "cycle" in out

    def test_fix_text_mentions_cycle(self, ev2300_repl, capsys):
        """The fix recovery text should point students at `ev2300 cycle` as
        the recommended bundle for steps 5-6."""
        ev2300_repl.onecmd("ev2300 fix")
        out = capsys.readouterr().out
        assert "ev2300 cycle" in out


class TestEv2300SysStat:
    """`ev2300 sys_stat [i2c_addr]` reads BQ76920 SYS_STAT (reg 0x00) and
    decodes each bit. Verified against TI datasheet SLUSBK2I Table 8-3.

    Bit map:
      bit 7: CC_READY    bit 5: DEVICE_XREADY   bit 4: OVRD_ALERT
      bit 3: UV          bit 2: OV              bit 1: SCD    bit 0: OCD
    """

    def test_decodes_0x84_as_cc_ready_plus_ov(self, ev2300_repl, capsys, monkeypatch):
        """Issue #128 reproduction: user saw 0x84 after overvoltage event."""
        mock = ev2300_repl.ctx.registry.devices["ev2300"]
        monkeypatch.setattr(mock, "read_byte", lambda *a, **kw: {"ok": True, "value": 0x84})
        ev2300_repl.onecmd("ev2300 sys_stat")
        out = capsys.readouterr().out
        assert "0x84" in out
        assert "CC_READY" in out
        assert "OV" in out
        # UV must not appear (bit 3 is not set)
        assert "UV" not in out or "UV=" in out  # may show in bit-list but not as fault

    def test_reports_latched_faults(self, ev2300_repl, capsys, monkeypatch):
        mock = ev2300_repl.ctx.registry.devices["ev2300"]
        monkeypatch.setattr(mock, "read_byte", lambda *a, **kw: {"ok": True, "value": 0x84})
        ev2300_repl.onecmd("ev2300 sys_stat")
        out = capsys.readouterr().out
        assert "latched fault" in out.lower()
        assert "clear_faults" in out

    def test_baseline_0x80_no_faults(self, ev2300_repl, capsys, monkeypatch):
        mock = ev2300_repl.ctx.registry.devices["ev2300"]
        monkeypatch.setattr(mock, "read_byte", lambda *a, **kw: {"ok": True, "value": 0x80})
        ev2300_repl.onecmd("ev2300 sys_stat")
        out = capsys.readouterr().out
        assert "0x80" in out
        assert "CC_READY" in out
        # Make sure we're not flagging this as a latched fault
        assert "latched faults: (none)" in out

    def test_explicit_i2c_addr(self, ev2300_repl, capsys, monkeypatch):
        mock = ev2300_repl.ctx.registry.devices["ev2300"]
        calls = []

        def fake_read(addr, reg):
            calls.append((addr, reg))
            return {"ok": True, "value": 0x80}

        monkeypatch.setattr(mock, "read_byte", fake_read)
        ev2300_repl.onecmd("ev2300 sys_stat 0x18")
        assert calls == [(0x18, 0x00)]

    def test_listed_in_help(self, ev2300_repl, capsys):
        ev2300_repl.onecmd("ev2300")
        out = capsys.readouterr().out
        assert "sys_stat" in out

    def test_help_explains_write_1_to_clear(self, ev2300_repl, capsys):
        """The help text must explain the W1C semantics so students don't
        repeat issue #128 by writing 0x80 to the register."""
        ev2300_repl.onecmd("ev2300")
        out = capsys.readouterr().out
        assert "write-1-to-clear" in out.lower() or "w1c" in out.lower()


class TestEv2300ClearFaults:
    """`ev2300 clear_faults [i2c_addr] [mask]` writes mask (default 0xFF) to
    SYS_STAT then re-reads to show what was cleared vs. what re-asserted."""

    def test_default_writes_0xff(self, ev2300_repl, capsys, monkeypatch):
        mock = ev2300_repl.ctx.registry.devices["ev2300"]
        # Before: 0x84 (OV latched). Mock the write so we can capture the value.
        writes = []
        reads = iter(
            [
                {"ok": True, "value": 0x84},  # before-clear read
                {"ok": True, "value": 0x80},  # after-clear read (OV gone)
            ]
        )

        def fake_read(addr, reg):
            return next(reads)

        def fake_write(addr, reg, val):
            writes.append((addr, reg, val))
            return {"ok": True}

        monkeypatch.setattr(mock, "read_byte", fake_read)
        monkeypatch.setattr(mock, "write_byte", fake_write)
        ev2300_repl.onecmd("ev2300 clear_faults")
        out = capsys.readouterr().out
        assert writes == [(0x08, 0x00, 0xFF)]
        assert "0x84" in out and "0x80" in out
        assert "cleared" in out.lower()
        assert "OV" in out

    def test_custom_mask(self, ev2300_repl, capsys, monkeypatch):
        """mask=0x04 clears only OV bit; UV/SCD/OCD are left alone."""
        mock = ev2300_repl.ctx.registry.devices["ev2300"]
        writes = []
        reads = iter(
            [
                {"ok": True, "value": 0x84},
                {"ok": True, "value": 0x80},
            ]
        )
        monkeypatch.setattr(mock, "read_byte", lambda a, r: next(reads))
        monkeypatch.setattr(mock, "write_byte", lambda a, r, v: writes.append((a, r, v)) or {"ok": True})
        ev2300_repl.onecmd("ev2300 clear_faults 0x08 0x04")
        assert writes == [(0x08, 0x00, 0x04)]

    def test_explains_when_fault_persists(self, ev2300_repl, capsys, monkeypatch):
        """If OV re-asserts because cell voltage is still above OV_TRIP,
        the command must point at the underlying condition (NOT lie about
        successful clear)."""
        mock = ev2300_repl.ctx.registry.devices["ev2300"]
        reads = iter(
            [
                {"ok": True, "value": 0x84},  # OV before
                {"ok": True, "value": 0x84},  # OV still latched after - voltage too high
            ]
        )
        monkeypatch.setattr(mock, "read_byte", lambda a, r: next(reads))
        monkeypatch.setattr(mock, "write_byte", lambda a, r, v: {"ok": True})
        ev2300_repl.onecmd("ev2300 clear_faults")
        out = capsys.readouterr().out
        assert "STILL active" in out
        assert "OV" in out
        # The hint about underlying condition is mandatory - this is the
        # whole point of the after-clear re-read
        assert "OV_TRIP" in out or "cell voltage" in out.lower()

    def test_write_failure_propagates(self, ev2300_repl, capsys, monkeypatch):
        mock = ev2300_repl.ctx.registry.devices["ev2300"]
        monkeypatch.setattr(mock, "read_byte", lambda a, r: {"ok": True, "value": 0x84})
        monkeypatch.setattr(mock, "write_byte", lambda a, r, v: {"ok": False, "status_text": "Device error (0x46)"})
        ev2300_repl.onecmd("ev2300 clear_faults")
        out = capsys.readouterr().out
        assert "failed" in out.lower()

    def test_rejects_out_of_range_mask(self, ev2300_repl, capsys, monkeypatch):
        mock = ev2300_repl.ctx.registry.devices["ev2300"]
        monkeypatch.setattr(mock, "read_byte", lambda a, r: {"ok": True, "value": 0x80})
        ev2300_repl.onecmd("ev2300 clear_faults 0x08 0x100")
        out = capsys.readouterr().out
        assert "out of range" in out.lower()

    def test_listed_in_help(self, ev2300_repl, capsys):
        ev2300_repl.onecmd("ev2300")
        out = capsys.readouterr().out
        assert "clear_faults" in out


class TestEv2300I2CPower:
    """Regression: i2c_power was previously only callable via the Python API.
    Bench debugging of the BQ76920 EVM motivated exposing it interactively."""

    def test_on_emits_enabled_1(self, ev2300_repl, capsys):
        ev2300_repl.onecmd("ev2300 i2c_power on")
        out = capsys.readouterr().out
        assert "ON" in out
        assert "I2C power" in out or "i2c power" in out.lower()

    def test_off_emits_enabled_0(self, ev2300_repl, capsys):
        ev2300_repl.onecmd("ev2300 i2c_power off")
        out = capsys.readouterr().out
        assert "OFF" in out

    def test_alias_1_means_on(self, ev2300_repl, capsys):
        ev2300_repl.onecmd("ev2300 i2c_power 1")
        out = capsys.readouterr().out
        assert "ON" in out

    def test_alias_0_means_off(self, ev2300_repl, capsys):
        ev2300_repl.onecmd("ev2300 i2c_power 0")
        out = capsys.readouterr().out
        assert "OFF" in out

    def test_missing_arg_shows_usage(self, ev2300_repl, capsys):
        ev2300_repl.onecmd("ev2300 i2c_power")
        out = capsys.readouterr().out
        assert "Usage" in out or "usage" in out.lower()

    def test_invalid_arg_warns(self, ev2300_repl, capsys):
        ev2300_repl.onecmd("ev2300 i2c_power maybe")
        out = capsys.readouterr().out
        assert "maybe" in out or "Invalid" in out or "invalid" in out.lower()

    def test_transport_exception_routed_through_fail(self, ev2300_repl, capsys, monkeypatch):
        """Regression: a USB transport exception must surface via _fail with
        a recovery hint, not bubble out of the REPL command loop. The driver
        normally returns ok=True for cmd 0x18 (silent on the wire), so this
        exercises the unreachable-by-default exception branch."""
        dev = ev2300_repl.ctx.registry.devices["ev2300"]

        def boom(**_kwargs):
            raise OSError("simulated USB stall")

        monkeypatch.setattr(dev, "i2c_power", boom)
        ev2300_repl.onecmd("ev2300 i2c_power on")
        out = capsys.readouterr().out
        assert "i2c_power" in out
        assert "OSError" in out or "simulated USB stall" in out


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
