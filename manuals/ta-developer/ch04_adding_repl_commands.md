# Chapter 4: Adding REPL Commands

## The BaseCommand Interface

All command handlers inherit from `BaseCommand` (`lab_instruments/repl/commands/base.py`):

    class BaseCommand:
        def __init__(self, ctx: ReplContext):
            self.ctx = ctx

Key methods provided:

- `parse_args(arg)` -- splits a command string into tokens using shlex (handles quotes)
- `parse_channels(ch_str, max_ch=4)` -- resolves "all", "ch1", "1" to channel lists
- `is_help(args)` / `strip_help(args)` -- detect and strip trailing "help" or "?"
- `error(msg)` -- print error with ColorPrinter and set error flag
- `print_colored_usage(lines)` -- print syntax-highlighted help

## The Command Handler Pattern

Each instrument type has a command handler class. Here is the PsuCommand pattern from `lab_instruments/repl/commands/psu.py`:

    class PsuCommand(BaseCommand):
        def execute(self, arg, dev, dev_name):
            args = self.parse_args(arg)
            if not args or self.is_help(args):
                self._show_help()
                return

            cmd = args[0].lower()
            rest = args[1:]

            if cmd == "chan":
                self._handle_chan(rest, dev, dev_name)
            elif cmd == "set":
                self._handle_set(rest, dev, dev_name)
            elif cmd == "meas":
                self._handle_meas(rest, dev, dev_name)
            elif cmd in ("on", "off"):
                self._handle_on_off(cmd, dev, dev_name)
            elif cmd == "state":
                self._handle_state(rest, dev, dev_name)
            else:
                self.error(f"Unknown psu command: {cmd}")

Each sub-handler parses its specific arguments, validates inputs, calls the driver method, and prints feedback:

    def _handle_set(self, args, dev, dev_name):
        if len(args) < 2:
            self.error("Usage: psu set <channel> <voltage> [current]")
            return
        channel = self._resolve_channel(dev, args[0])
        voltage = float(args[1])
        dev.set_voltage(channel, voltage)
        ColorPrinter.success(f"Set {args[0]}: {voltage}V")

## Registering a New Command in shell.py

### 1. Import the handler

    from .commands.mytype import MyTypeCommand

### 2. Create the handler instance in __init__

    self._mytype_cmd = MyTypeCommand(self.ctx)

### 3. Wire the state callback (if needed)

    self._mytype_cmd.set_state_callback(
        lambda name, st: self.do_state(f"{name} {st}")
    )

### 4. Add the do_* method

    def do_mytype(self, arg):
        """Control mytype instruments."""
        parts = arg.split(None, 1)
        cmd_token = parts[0] if parts else ""
        rest = parts[1] if len(parts) > 1 else ""

        dev_name = self.ctx.registry.resolve_type("mytype")
        if not dev_name:
            ColorPrinter.warning("No mytype found. Run 'scan' first.")
            return
        dev = self.ctx.registry.get_device(dev_name)
        self._mytype_cmd.execute(arg, dev, dev_name)

### 5. Add to help system

In the `do_help` method or the help text dictionary, add your new command with a description.

## Capabilities Flags

Some commands only work on certain models. The capabilities system (`lab_instruments/repl/capabilities.py`) defines feature flags:

    DRIVER_CAPABILITIES = {
        "Rigol_DHO804": {"counter", "dvm", "cursors", "recording", "mask_test", "awg"},
        "Keysight_DSOX1204G": {"counter", "dvm", "cursors", "mask_test", "awg", "screenshot"},
        "Tektronix_MSO2024": set(),   # basic scope only
    }

In command handlers, check capabilities before executing:

    caps = get_capabilities(dev)
    if "counter" not in caps:
        self.error("Counter not supported on this scope model.")
        return

## Adding Help Text

Each handler should include a help method that shows usage when the user types `help mytype`:

    def _show_help(self):
        self.print_colored_usage([
            ("mytype set <channel> <value>", "Set output value"),
            ("mytype meas <channel>", "Measure current value"),
            ("mytype on / off", "Enable or disable output"),
        ])

## Testing Commands

Test commands using the `make_repl` fixture from conftest.py:

    def test_psu_set_prints_success(self, make_repl, capsys):
        devices = {"psu1": MockHP_E3631A()}
        repl = make_repl(devices)
        repl.onecmd("scan")
        repl.onecmd("psu1 set 1 5.0")
        out = capsys.readouterr().out
        assert "5.0" in out
