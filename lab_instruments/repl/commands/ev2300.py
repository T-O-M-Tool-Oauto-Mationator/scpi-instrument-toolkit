"""EV2300 USB-to-I2C adapter command handler for the REPL."""

from typing import Any

from lab_instruments.src.terminal import ColorPrinter

from ..context import ReplContext
from .base import BaseCommand


class Ev2300Command(BaseCommand):
    """Handler for EV2300 commands."""

    def __init__(self, ctx: ReplContext) -> None:
        super().__init__(ctx)

    def set_state_callback(self, callback) -> None:
        """Register the shell's ``do_state`` so we can delegate ``ev2300 state`` commands."""
        self._state_callback = callback

    def _state_callback(self, dev_name: str, state_arg: str) -> None:
        """Default no-op; overridden by set_state_callback."""
        ColorPrinter.warning("state command not wired up")

    def execute(self, arg: str, dev: Any, dev_name: str) -> None:
        """Execute an EV2300 command."""
        args = self.parse_args(arg)
        args, _help_flag = self.strip_help(args)

        if not args:
            self._show_help()
            return

        cmd_name = args[0].lower()

        try:
            if cmd_name == "info":
                self._handle_info(dev)
            elif cmd_name == "read_word":
                self._handle_read_word(args, dev)
            elif cmd_name == "write_word":
                self._handle_write_word(args, dev)
            elif cmd_name == "read_byte":
                self._handle_read_byte(args, dev)
            elif cmd_name == "write_byte":
                self._handle_write_byte(args, dev)
            elif cmd_name == "read_block":
                self._handle_read_block(args, dev)
            elif cmd_name == "write_block":
                self._handle_write_block(args, dev)
            elif cmd_name == "send_byte":
                self._handle_send_byte(args, dev)
            elif cmd_name == "scan":
                self._handle_scan(args, dev)
            elif cmd_name == "probe":
                self._handle_probe(args, dev)
            elif cmd_name == "state":
                if len(args) < 2:
                    self._show_help()
                    return
                self._state_callback(dev_name, args[1])
            else:
                ColorPrinter.warning(f"Unknown EV2300 command: ev2300 {arg}")
        except Exception as exc:
            ColorPrinter.error(f"{type(exc).__name__}: {exc}")

    # ------------------------------------------------------------------
    # Help
    # ------------------------------------------------------------------

    def _show_help(self) -> None:
        self.print_colored_usage(
            [
                "# EV2300 USB-to-I2C Adapter",
                "",
                "ev2300 info",
                "  - show device VID, PID, serial, product, manufacturer",
                "ev2300 read_word <i2c_addr> <register>",
                "  - read 16-bit LE word; addr/reg in hex (0x08) or decimal",
                "ev2300 write_word <i2c_addr> <register> <value>",
                "  - write 16-bit LE word",
                "ev2300 read_byte <i2c_addr> <register>",
                "ev2300 write_byte <i2c_addr> <register> <value>",
                "ev2300 read_block <i2c_addr> <register>",
                "ev2300 write_block <i2c_addr> <register> <hex_bytes>",
                "  - example: ev2300 write_block 0x08 0x04 AABB",
                "ev2300 send_byte <i2c_addr> <command>",
                "  - SMBus Send Byte (no register address)",
                "ev2300 scan <i2c_addr>",
                "  - probe registers 0x00-0xFF on a given I2C address",
                "ev2300 probe <cmd_code> [i2c_addr] [register]",
                "  - send arbitrary command code for reverse engineering",
                "ev2300 state on|off|safe|reset",
            ]
        )

    # ------------------------------------------------------------------
    # Argument parsing helper
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_int(s: str, label: str = "value") -> int:
        """Parse an integer from hex (0x...) or decimal string."""
        try:
            return int(s, 0)
        except ValueError:
            raise ValueError(f"Invalid {label} {s!r} -- expected hex (0x..) or decimal integer") from None

    # ------------------------------------------------------------------
    # Command handlers
    # ------------------------------------------------------------------

    def _handle_info(self, dev: Any) -> None:
        info = dev.get_device_info()
        if not info.get("ok"):
            ColorPrinter.error(info.get("status_text", "Failed to get device info"))
            return
        for key in ("vid", "pid", "serial", "product", "manufacturer", "version"):
            val = info.get(key)
            if val is not None:
                ColorPrinter.info(f"  {key:14s}: {val}")

    def _handle_read_word(self, args: list, dev: Any) -> None:
        if len(args) < 3:
            ColorPrinter.warning("Usage: ev2300 read_word <i2c_addr> <register>")
            return
        addr = self._parse_int(args[1], "i2c_addr")
        reg = self._parse_int(args[2], "register")
        result = dev.read_word(addr, reg)
        if result.get("ok") and result.get("value") is not None:
            val = result["value"]
            ColorPrinter.cyan(f"0x{val:04X} ({val})")
        else:
            ColorPrinter.error(
                f"read_word addr=0x{addr:02X} reg=0x{reg:02X} failed: {result.get('status_text', 'unknown error')}"
            )

    def _handle_write_word(self, args: list, dev: Any) -> None:
        if len(args) < 4:
            ColorPrinter.warning("Usage: ev2300 write_word <i2c_addr> <register> <value>")
            return
        addr = self._parse_int(args[1], "i2c_addr")
        reg = self._parse_int(args[2], "register")
        val = self._parse_int(args[3], "value")
        result = dev.write_word(addr, reg, val)
        if result.get("ok"):
            ColorPrinter.success(f"Wrote 0x{val:04X} to addr=0x{addr:02X} reg=0x{reg:02X}")
        else:
            ColorPrinter.error(
                f"write_word addr=0x{addr:02X} reg=0x{reg:02X} val=0x{val:04X} failed: "
                f"{result.get('status_text', 'unknown error')}"
            )

    def _handle_read_byte(self, args: list, dev: Any) -> None:
        if len(args) < 3:
            ColorPrinter.warning("Usage: ev2300 read_byte <i2c_addr> <register>")
            return
        addr = self._parse_int(args[1], "i2c_addr")
        reg = self._parse_int(args[2], "register")
        result = dev.read_byte(addr, reg)
        if result.get("ok") and result.get("value") is not None:
            val = result["value"]
            ColorPrinter.cyan(f"0x{val:02X} ({val})")
        else:
            ColorPrinter.error(
                f"read_byte addr=0x{addr:02X} reg=0x{reg:02X} failed: {result.get('status_text', 'unknown error')}"
            )

    def _handle_write_byte(self, args: list, dev: Any) -> None:
        if len(args) < 4:
            ColorPrinter.warning("Usage: ev2300 write_byte <i2c_addr> <register> <value>")
            return
        addr = self._parse_int(args[1], "i2c_addr")
        reg = self._parse_int(args[2], "register")
        val = self._parse_int(args[3], "value")
        result = dev.write_byte(addr, reg, val)
        if result.get("ok"):
            ColorPrinter.success(f"Wrote 0x{val:02X} to addr=0x{addr:02X} reg=0x{reg:02X}")
        else:
            ColorPrinter.error(
                f"write_byte addr=0x{addr:02X} reg=0x{reg:02X} val=0x{val:02X} failed: "
                f"{result.get('status_text', 'unknown error')}"
            )

    def _handle_read_block(self, args: list, dev: Any) -> None:
        if len(args) < 3:
            ColorPrinter.warning("Usage: ev2300 read_block <i2c_addr> <register>")
            return
        addr = self._parse_int(args[1], "i2c_addr")
        reg = self._parse_int(args[2], "register")
        result = dev.read_block(addr, reg)
        if result.get("ok") and result.get("block") is not None:
            block = result["block"]
            hex_str = " ".join(f"{b:02X}" for b in block)
            ColorPrinter.cyan(f"[{len(block)} bytes] {hex_str}")
        else:
            ColorPrinter.error(
                f"read_block addr=0x{addr:02X} reg=0x{reg:02X} failed: {result.get('status_text', 'unknown error')}"
            )

    def _handle_write_block(self, args: list, dev: Any) -> None:
        if len(args) < 4:
            ColorPrinter.warning("Usage: ev2300 write_block <i2c_addr> <register> <hex_bytes>")
            return
        addr = self._parse_int(args[1], "i2c_addr")
        reg = self._parse_int(args[2], "register")
        hex_str = args[3].replace(" ", "")
        if len(hex_str) % 2 != 0:
            ColorPrinter.error(f"Invalid hex string {args[3]!r} -- odd number of nibbles")
            return
        try:
            data = bytes.fromhex(hex_str)
        except ValueError as exc:
            ColorPrinter.error(f"Invalid hex string {args[3]!r}: {exc}")
            return
        result = dev.write_block(addr, reg, data)
        if result.get("ok"):
            ColorPrinter.success(f"Wrote {len(data)} bytes to addr=0x{addr:02X} reg=0x{reg:02X}")
        else:
            ColorPrinter.error(
                f"write_block addr=0x{addr:02X} reg=0x{reg:02X} ({len(data)} bytes) failed: "
                f"{result.get('status_text', 'unknown error')}"
            )

    def _handle_send_byte(self, args: list, dev: Any) -> None:
        if len(args) < 3:
            ColorPrinter.warning("Usage: ev2300 send_byte <i2c_addr> <command>")
            return
        addr = self._parse_int(args[1], "i2c_addr")
        cmd = self._parse_int(args[2], "command")
        result = dev.send_byte(addr, cmd)
        if result.get("ok"):
            ColorPrinter.success(f"Sent byte 0x{cmd:02X} to addr=0x{addr:02X}")
        else:
            ColorPrinter.error(
                f"send_byte addr=0x{addr:02X} cmd=0x{cmd:02X} failed: {result.get('status_text', 'unknown error')}"
            )

    def _handle_scan(self, args: list, dev: Any) -> None:
        if len(args) < 2:
            ColorPrinter.warning("Usage: ev2300 scan <i2c_addr>")
            return
        addr = self._parse_int(args[1], "i2c_addr")
        ColorPrinter.info(f"Scanning registers 0x00-0xFF on I2C addr 0x{addr:02X}...")
        found = []
        errors: dict[int, str] = {}
        for reg in range(0x100):
            result = dev.read_word(addr, reg)
            if result.get("ok") and result.get("value") is not None:
                found.append((reg, result["value"]))
            elif not result.get("ok"):
                errors[reg] = result.get("status_text", "unknown error")
        if found:
            ColorPrinter.success(f"Found {len(found)} readable registers:")
            for reg, val in found:
                print(f"  0x{reg:02X}: 0x{val:04X} ({val})")
        else:
            ColorPrinter.warning(f"No readable registers found on addr=0x{addr:02X}")
        if errors:
            unique = set(errors.values())
            ColorPrinter.warning(f"  {len(errors)} registers returned errors (e.g. {next(iter(unique))})")

    def _handle_probe(self, args: list, dev: Any) -> None:
        if len(args) < 2:
            ColorPrinter.warning("Usage: ev2300 probe <cmd_code> [i2c_addr] [register]")
            return
        cmd_code = self._parse_int(args[1], "cmd_code")
        i2c_addr = self._parse_int(args[2], "i2c_addr") if len(args) > 2 else 0x08
        register = self._parse_int(args[3], "register") if len(args) > 3 else 0x00
        result = dev.probe_command(cmd_code, i2c_addr, register)
        resp_cmd = result.get("cmd", -1)
        raw = result.get("raw", b"")
        hex_str = " ".join(f"{b:02X}" for b in raw[:16]) if raw else ""
        status = result.get("status_text", "")
        if result.get("error"):
            detail = f" -- {status}" if status else ""
            ColorPrinter.error(
                f"probe cmd=0x{cmd_code:02X} addr=0x{i2c_addr:02X} reg=0x{register:02X}: ERROR{detail}  [{hex_str}]"
            )
        else:
            ColorPrinter.cyan(
                f"probe cmd=0x{cmd_code:02X} addr=0x{i2c_addr:02X} reg=0x{register:02X}: "
                f"resp=0x{resp_cmd:02X}  [{hex_str}]"
            )
