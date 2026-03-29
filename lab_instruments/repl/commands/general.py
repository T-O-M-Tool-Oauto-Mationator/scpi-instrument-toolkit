"""General REPL commands: scan, list, use, status, idn, raw, state, etc."""

import contextlib
import os
import sys
from typing import Any

from lab_instruments.src.terminal import ColorPrinter

from .base import BaseCommand
from .safety import SafetySystem


class GeneralCommands(BaseCommand):
    """Handles general REPL commands."""

    def __init__(self, ctx, safety: SafetySystem) -> None:
        super().__init__(ctx)
        self.safety = safety
        self._docs_port = None
        self._docs_server = None

    def do_docs(self, arg: str) -> None:
        import http.server
        import pathlib
        import subprocess
        import threading
        import webbrowser

        args = self.parse_args(arg)
        if self.is_help(args):
            self.print_colored_usage(
                [
                    "# DOCS",
                    "",
                    "docs",
                    "  - open the full command reference in your web browser",
                    "  - serves the bundled MkDocs site if available",
                    "  - auto-builds from mkdocs.yml if the site has not been built yet",
                    "  - requires: pip install mkdocs-material  (for auto-build)",
                ]
            )
            return

        # Locate paths relative to the package
        # __file__ = lab_instruments/repl/commands/general.py
        # lab_instruments/ is 3 parents up; repo root is 4 parents up
        lab_pkg = pathlib.Path(__file__).resolve().parent.parent.parent
        pkg_root = lab_pkg.parent  # repo root — mkdocs.yml lives here
        site_dir = lab_pkg / "site"  # matches site_dir in mkdocs.yml
        mkdocs_yml = pkg_root / "mkdocs.yml"

        # Auto-build if needed
        if not (site_dir / "index.html").exists() and mkdocs_yml.exists():
            ColorPrinter.info("Building docs (first run — takes a few seconds)...")
            try:
                subprocess.run(
                    [sys.executable, "-m", "mkdocs", "build"],
                    cwd=str(pkg_root),
                    check=True,
                    capture_output=True,
                    text=True,
                )
                ColorPrinter.success("Docs built.")
            except FileNotFoundError:
                ColorPrinter.warning("mkdocs not found. Install with: pip install mkdocs-material")
                ColorPrinter.info(f"Docs source: {pkg_root / 'docs'}")
                return
            except subprocess.CalledProcessError as exc:
                stderr = (exc.stderr or "")[:200]
                ColorPrinter.error(f"mkdocs build failed: {stderr}")
                return

        if not (site_dir / "index.html").exists():
            ColorPrinter.warning("No built docs site found.")
            ColorPrinter.info(f"To build: cd {pkg_root} && mkdocs build")
            ColorPrinter.info("Requires: pip install mkdocs-material")
            return

        # Spawn HTTP server on first call; reuse port on subsequent calls
        if self._docs_server is None:
            _site = str(site_dir)

            class _QuietHandler(http.server.SimpleHTTPRequestHandler):
                def __init__(self_h, *a, **kw):
                    super().__init__(*a, directory=_site, **kw)

                def log_message(self_h, fmt, *a):
                    pass

            self._docs_server = http.server.HTTPServer(("127.0.0.1", 0), _QuietHandler)
            self._docs_port = self._docs_server.server_address[1]
            threading.Thread(target=self._docs_server.serve_forever, daemon=True).start()

        url = f"http://127.0.0.1:{self._docs_port}/index.html"
        ColorPrinter.info(f"Opening docs: {url}")
        webbrowser.open(url)

    def do_scan(self, arg: str, discovery: Any, scan_done: Any) -> None:
        args = self.parse_args(arg)
        if self.is_help(args):
            self.print_colored_usage(
                [
                    "# SCAN",
                    "",
                    "scan",
                    "  - discover and connect to all VISA instruments",
                    "  - instruments are assigned names: psu1, awg1, dmm1, scope1, …",
                    "  - re-run at any time to pick up newly connected devices",
                ]
            )
            return
        if not scan_done.is_set():
            ColorPrinter.info("Waiting for background scan to finish...")
            scan_done.wait()
        else:
            self.registry.devices = discovery.scan(verbose=True)
            if self.registry.selected not in self.registry.devices:
                self.registry.selected = None
            if self.registry.devices:
                ColorPrinter.success(f"Found {len(self.registry.devices)} device(s).")
            else:
                ColorPrinter.warning("No instruments found.")

    def do_list(self, arg: str) -> None:
        args = self.parse_args(arg)
        if self.is_help(args):
            self.print_colored_usage(
                [
                    "# LIST",
                    "",
                    "list",
                    "  - show all connected instruments and their assigned names",
                    "  - the active instrument (set via 'use') is highlighted",
                ]
            )
            return
        self.print_devices()

    def do_use(self, arg: str) -> None:
        args = self.parse_args(arg)
        if self.is_help(args) or not args:
            self.print_colored_usage(
                [
                    "# USE — select active instrument",
                    "",
                    "use <name>",
                    "  - With one PSU connected, bare 'psu' commands work automatically.",
                    "  - With two PSUs (psu1, psu2), you must be explicit:",
                    "    - Either prefix every command:  psu1 set 5.0  /  psu2 set 12.0",
                    "    - Or pick one with 'use':  use psu1  then  psu set 5.0  (acts on psu1)",
                    "  - 'use' only affects bare commands — psu1/psu2 prefixes always work.",
                    "",
                    "  - example: use psu1   then: psu set 5.0   psu meas v",
                    "  - example: use dmm1   then: dmm meas vdc",
                ]
            )
            self.print_devices()
            return
        name = args[0]
        if name not in self.registry.devices:
            ColorPrinter.warning(f"Unknown instrument '{name}'. Connected: {list(self.registry.devices.keys())}")
            return
        self.registry.selected = name
        ColorPrinter.success(f"Active: {name}  (bare commands now target this instrument)")

    def do_status(self, arg: str) -> None:
        self.print_devices()

    def do_idn(self, arg: str) -> None:
        args = self.parse_args(arg)
        if self.is_help(args):
            self.print_colored_usage(
                [
                    "# IDN",
                    "",
                    "idn",
                    "  - query *IDN? on the active instrument",
                    "idn <name>",
                    "  - query *IDN? on a specific named instrument",
                    "  - example: idn dmm",
                    "  - example: idn psu2",
                ]
            )
            return
        name = args[0] if args else None
        dev = self.registry.get_device(name)
        if not dev:
            self.ctx.command_had_error = True
            return
        try:
            ColorPrinter.cyan(dev.query("*IDN?"))
        except Exception as exc:
            self.error(str(exc))

    def do_raw(self, arg: str) -> None:
        args = self.parse_args(arg)
        args, help_flag = self.strip_help(args)
        if not args or help_flag:
            self.print_colored_usage(
                [
                    "# RAW",
                    "",
                    "raw <scpi>",
                    "  - send a raw SCPI command to the active instrument",
                    "  - commands ending with ? are queries — response is printed",
                    "raw <name> <scpi>",
                    "  - send to a specific named instrument",
                    "  - example: raw *IDN?",
                    "  - example: raw *RST",
                    "  - example: raw scope MEASUrement:IMMed:VALue?",
                    "  - example: raw psu2 MEAS:VOLT?",
                ]
            )
            return
        name = None
        if args[0] in self.registry.devices:
            name = args[0]
            args = args[1:]
        dev = self.registry.get_device(name)
        if not dev or not args:
            if not dev:
                self.ctx.command_had_error = True
            return
        cmd_str = " ".join(args)
        try:
            if cmd_str.strip().endswith("?"):
                ColorPrinter.cyan(dev.query(cmd_str))
            else:
                dev.send_command(cmd_str)
                ColorPrinter.success(f"Sent: {cmd_str}")
        except Exception as exc:
            self.error(str(exc))

    def do_state(self, arg: str) -> None:
        args = self.parse_args(arg)
        if self.is_help(args):
            self._state_help()
            return
        if not args or args[0] == "list":
            self._state_help()
            return
        if args[0] in ("safe", "reset", "off", "on"):
            if args[0] == "safe":
                self.safe_all()
            elif args[0] == "off":
                self.off_all()
            elif args[0] == "on":
                self.on_all()
            else:
                self.reset_all()
            return
        if len(args) < 2:
            ColorPrinter.warning("Usage: state <device> <safe|reset|on|off>")
            return
        name = args[0]
        state = args[1].lower()
        dev = self.registry.get_device(name)
        if not dev:
            self.ctx.command_had_error = True
            return
        try:
            if name.startswith("psu"):
                self._state_psu(name, dev, state)
            elif name.startswith("ev2300"):
                self._state_ev2300(name, dev, state)
            elif name.startswith("smu"):
                self._state_smu(name, dev, state)
            elif name.startswith("awg"):
                self._state_awg(name, dev, state)
            elif name.startswith("scope"):
                self._state_scope(name, dev, state)
            elif name.startswith("dmm"):
                self._state_dmm(name, dev, state)
        except Exception as exc:
            ColorPrinter.error(str(exc))

    def _state_help(self) -> None:
        self.print_colored_usage(
            [
                "# STATE",
                "",
                "state on",
                "  - enable outputs on all instruments",
                "state off",
                "  - disable outputs on all instruments",
                "state safe",
                "  - apply safe state to all instruments (voltage/current to minimum)",
                "state reset",
                "  - send *RST to all instruments",
                "state <device> on|off|safe|reset",
                "  - apply a state to one specific instrument",
                "  - example: state psu1 off",
                "  - example: state awg safe",
                "state list",
                "  - show current output state of all instruments",
            ]
        )

    def _state_psu(self, name, dev, state):
        if state in ("safe", "off"):
            if hasattr(dev, "disable_all_channels"):
                dev.disable_all_channels()
            elif hasattr(dev, "disable_output"):
                dev.disable_output()
            elif hasattr(dev, "enable_output"):
                dev.enable_output(False)
            ColorPrinter.success(f"{name}: output disabled")
        elif state == "on":
            if not self.safety.check_psu_output_allowed(name):
                return
            if hasattr(dev, "enable_output"):
                dev.enable_output(True)
            ColorPrinter.success(f"{name}: output enabled")
        elif state == "reset":
            dev.reset()
            ColorPrinter.success(f"{name}: reset")
        else:
            ColorPrinter.warning("PSU states: on, off, safe, reset")

    def _state_awg(self, name, dev, state):
        if state in ("safe", "off"):
            if hasattr(dev, "disable_all_channels"):
                dev.disable_all_channels()
            elif hasattr(dev, "disable_output"):
                dev.disable_output()
            elif hasattr(dev, "enable_output"):
                try:
                    dev.enable_output(ch1=False, ch2=False)
                except TypeError:
                    dev.enable_output(False)
            ColorPrinter.success(f"{name}: outputs disabled")
        elif state == "on":
            for ch in (1, 2):
                if not self.safety.check_awg_output_allowed(name, ch):
                    return
            if hasattr(dev, "enable_all_channels"):
                dev.enable_all_channels()
            elif hasattr(dev, "enable_output"):
                try:
                    dev.enable_output(ch1=True, ch2=True)
                except TypeError:
                    dev.enable_output(True)
            ColorPrinter.success(f"{name}: outputs enabled")
        elif state == "reset":
            dev.reset()
            ColorPrinter.success(f"{name}: reset")
        else:
            ColorPrinter.warning("AWG states: on, off, safe, reset")

    def _state_scope(self, name, dev, state):
        if state in ("safe", "off"):
            if hasattr(dev, "disable_all_channels"):
                dev.disable_all_channels()
            ColorPrinter.success(f"{name}: channels disabled")
        elif state == "on":
            if hasattr(dev, "enable_all_channels"):
                dev.enable_all_channels()
            ColorPrinter.success(f"{name}: channels enabled")
        elif state == "reset":
            dev.reset()
            ColorPrinter.success(f"{name}: reset")

    def _state_smu(self, name, dev, state):
        if state in ("safe", "off"):
            if hasattr(dev, "disable_all_channels"):
                dev.disable_all_channels()
            elif hasattr(dev, "enable_output"):
                dev.enable_output(False)
            ColorPrinter.success(f"{name}: output disabled")
        elif state == "on":
            if not self.safety.check_psu_output_allowed(name):
                return
            if hasattr(dev, "enable_output"):
                dev.enable_output(True)
            ColorPrinter.success(f"{name}: output enabled")
        elif state == "reset":
            dev.reset()
            ColorPrinter.success(f"{name}: reset")
        else:
            ColorPrinter.warning("SMU states: on, off, safe, reset")

    def _state_ev2300(self, name, dev, state):
        if state in ("safe", "off", "reset"):
            if hasattr(dev, "reset"):
                dev.reset()
            ColorPrinter.success(f"{name}: reset")
        elif state == "on":
            ColorPrinter.info(f"{name}: adapter is always on when connected")
        else:
            ColorPrinter.warning("EV2300 states: on, off, safe, reset")

    def _state_dmm(self, name, dev, state):
        if state in ("safe", "reset"):
            dev.reset()
            ColorPrinter.success(f"{name}: reset")

    def do_close(self, arg: str) -> None:
        args = self.parse_args(arg)
        if self.is_help(args):
            self.print_colored_usage(
                [
                    "# CLOSE",
                    "",
                    "close",
                    "  - disconnect all instruments and release VISA resources",
                    "  - use 'scan' to reconnect",
                ]
            )
            return
        for name, dev in list(self.registry.devices.items()):
            try:
                dev.disconnect()
                ColorPrinter.success(f"{name}: disconnected")
            except Exception as exc:
                ColorPrinter.error(f"{name}: {exc}")
        self.registry.devices.clear()
        self.registry.selected = None
        ColorPrinter.success("All instruments disconnected.")

    def do_version(self, arg: str, version: str) -> None:
        ColorPrinter.info(f"scpi-instrument-toolkit v{version}")

    def do_clear(self, arg: str) -> None:
        os.system("cls" if os.name == "nt" else "clear")

    def do_reload(self, arg: str) -> None:
        ColorPrinter.info("Disconnecting all instruments...")
        for dev in list(self.registry.devices.values()):
            with contextlib.suppress(Exception):
                dev.disconnect()
        ColorPrinter.success("Restarting process...")
        argv0 = sys.argv[0]
        if os.path.isfile(argv0) and argv0.endswith(".py"):
            os.execv(sys.executable, [sys.executable] + sys.argv)
        else:
            os.execv(sys.executable, [sys.executable, "-m", "lab_instruments.repl"] + sys.argv[1:])

    def do_all(self, arg: str) -> None:
        args = self.parse_args(arg)
        args, help_flag = self.strip_help(args)
        if not args or help_flag:
            self.print_colored_usage(
                [
                    "# ALL",
                    "",
                    "all on",
                    "  - enable outputs on every connected instrument",
                    "all off",
                    "  - disable outputs on every connected instrument",
                    "all safe",
                    "  - apply safe state to every instrument (voltages/currents to minimum)",
                    "all reset",
                    "  - send *RST to every connected instrument",
                ]
            )
            return
        state = args[0].lower()
        {"on": self.on_all, "off": self.off_all, "safe": self.safe_all, "reset": self.reset_all}.get(
            state, lambda: ColorPrinter.warning("Use: all on|off|safe|reset")
        )()

    # ------------------------------------------------------------------
    # Bulk state operations
    # ------------------------------------------------------------------
    def safe_all(self) -> None:
        for name, dev in self.registry.devices.items():
            try:
                if name.startswith("psu"):
                    if hasattr(dev, "disable_all_channels"):
                        dev.disable_all_channels()
                    elif hasattr(dev, "disable_output"):
                        dev.disable_output()
                    elif hasattr(dev, "enable_output"):
                        dev.enable_output(False)
                elif name.startswith("awg"):
                    if hasattr(dev, "disable_all_channels"):
                        dev.disable_all_channels()
                    elif hasattr(dev, "disable_output"):
                        dev.disable_output()
                    elif hasattr(dev, "enable_output"):
                        dev.enable_output(ch1=False, ch2=False)
                elif name.startswith("scope"):
                    if hasattr(dev, "stop"):
                        dev.stop()
                    if hasattr(dev, "disable_all_channels"):
                        dev.disable_all_channels()
                    elif hasattr(dev, "disable_channel"):
                        for ch in range(1, 5):
                            with contextlib.suppress(Exception):
                                dev.disable_channel(ch)
                    if hasattr(dev, "awg_set_output_enable"):
                        try:
                            dev.awg_set_output_enable(False)
                            if hasattr(dev, "awg_set_function"):
                                dev.awg_set_function("DC")
                            if hasattr(dev, "awg_set_offset"):
                                dev.awg_set_offset(0.0)
                        except Exception:
                            pass
                elif name.startswith("smu"):
                    if hasattr(dev, "disable_all_channels"):
                        dev.disable_all_channels()
                elif name.startswith("ev2300"):
                    pass  # Bus adapter — no dangerous output state
                elif name.startswith("dmm") and hasattr(dev, "reset"):
                    dev.reset()
                ColorPrinter.success(f"{name}: safe state applied")
            except Exception as exc:
                ColorPrinter.error(f"{name}: {exc}")

    def reset_all(self) -> None:
        for name, dev in self.registry.devices.items():
            try:
                dev.reset()
                ColorPrinter.success(f"{name}: reset")
            except Exception as exc:
                ColorPrinter.error(f"{name}: {exc}")

    def off_all(self) -> None:
        for name, dev in self.registry.devices.items():
            try:
                if name.startswith("psu"):
                    if hasattr(dev, "disable_all_channels"):
                        dev.disable_all_channels()
                    elif hasattr(dev, "disable_output"):
                        dev.disable_output()
                    elif hasattr(dev, "enable_output"):
                        dev.enable_output(False)
                    ColorPrinter.success(f"{name}: output disabled")
                elif name.startswith("awg"):
                    if hasattr(dev, "disable_all_channels"):
                        dev.disable_all_channels()
                    elif hasattr(dev, "disable_output"):
                        dev.disable_output()
                    elif hasattr(dev, "enable_output"):
                        dev.enable_output(ch1=False, ch2=False)
                    ColorPrinter.success(f"{name}: outputs disabled")
                elif name.startswith("scope"):
                    if hasattr(dev, "stop"):
                        dev.stop()
                        ColorPrinter.success(f"{name}: acquisition stopped")
                    if hasattr(dev, "disable_all_channels"):
                        dev.disable_all_channels()
                        ColorPrinter.success(f"{name}: channels disabled")
                    elif hasattr(dev, "disable_channel"):
                        for ch in range(1, 5):
                            with contextlib.suppress(Exception):
                                dev.disable_channel(ch)
                        ColorPrinter.success(f"{name}: all channels disabled")
                elif name.startswith("smu"):
                    if hasattr(dev, "disable_all_channels"):
                        dev.disable_all_channels()
                    elif hasattr(dev, "enable_output"):
                        dev.enable_output(False)
                    ColorPrinter.success(f"{name}: output disabled")
                elif name.startswith("ev2300"):
                    pass  # Bus adapter — no output to disable
                elif name.startswith("dmm") and hasattr(dev, "reset"):
                    dev.reset()
                    ColorPrinter.success(f"{name}: reset")
            except Exception as exc:
                ColorPrinter.error(f"{name}: {exc}")

    def on_all(self) -> None:
        for name, dev in self.registry.devices.items():
            try:
                if name.startswith("psu"):
                    if hasattr(dev, "enable_output"):
                        if not self.safety.check_psu_output_allowed(name):
                            continue
                        dev.enable_output(True)
                        ColorPrinter.success(f"{name}: output enabled")
                elif name.startswith("awg"):
                    if hasattr(dev, "enable_output"):
                        blocked = False
                        for ch in (1, 2):
                            if not self.safety.check_awg_output_allowed(name, ch):
                                blocked = True
                                break
                        if blocked:
                            continue
                        try:
                            dev.enable_output(ch1=True, ch2=True)
                        except TypeError:
                            dev.enable_output(1, True)
                            dev.enable_output(2, True)
                        ColorPrinter.success(f"{name}: outputs enabled")
                elif name.startswith("smu"):
                    if hasattr(dev, "enable_output"):
                        if not self.safety.check_psu_output_allowed(name):
                            continue
                        dev.enable_output(True)
                        ColorPrinter.success(f"{name}: output enabled")
                elif name.startswith("ev2300"):
                    pass  # Bus adapter — always on when connected
                elif name.startswith("scope") and hasattr(dev, "enable_all_channels"):
                    dev.enable_all_channels()
                    ColorPrinter.success(f"{name}: channels enabled")
            except Exception as exc:
                ColorPrinter.error(f"{name}: {exc}")

    def print_devices(self) -> None:
        if not self.registry.devices:
            ColorPrinter.warning("No instruments connected.")
            return
        C = ColorPrinter.CYAN
        G = ColorPrinter.GREEN
        Y = ColorPrinter.YELLOW
        B = ColorPrinter.BOLD
        R = ColorPrinter.RESET
        for name, dev in self.registry.devices.items():
            if name == self.registry.selected:
                marker = f"{G}*{R}"
                name_str = f"{G}{B}{name}{R}"
            else:
                marker = " "
                name_str = f"{C}{name}{R}"
            print(f" {marker} {name_str}: {Y}{dev.__class__.__name__}{R}")
