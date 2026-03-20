"""Script management commands: script, record, examples, python, limits."""

import contextlib
import json
import os
import pathlib
import subprocess
import tempfile
import time
import traceback

from lab_instruments.src.terminal import ColorPrinter

from ..script_engine.expander import expand_script_lines
from ..script_engine.runner import run_expanded
from .base import BaseCommand
from .safety import SafetySystem


class ScriptingCommands(BaseCommand):
    """Handles script, record, examples, python, upper_limit, lower_limit."""

    def __init__(self, ctx, safety: SafetySystem, shell=None) -> None:
        super().__init__(ctx)
        self.safety = safety
        self.shell = shell  # set later by the shell

    def do_script(self, arg: str) -> None:
        args = self.parse_args(arg)
        args, help_flag = self.strip_help(args)
        if not args or help_flag:
            self.print_colored_usage([
                "# SCRIPT — manage and run named scripts", "",
                "script new <name>            # create a new script (opens in editor)",
                "script run <name>            # execute a script",
                "script debug <name>          # execute with step debugger",
                "script edit <name>           # open in editor",
                "script list                  # show all saved scripts",
                "script rm <name>             # delete a script",
                "script show <name>           # display script contents",
                "script import <name> <path>  # import a .scpi file",
                "script load                  # reload scripts from disk",
                "script save                  # save all scripts to disk",
                "script dir [path|reset]      # get or set scripts directory",
            ])
            return
        sub = args[0].lower()
        if sub == "new" and len(args) >= 2:
            name = args[1]
            lines = self._edit_script(name, [])
            if lines is not None:
                self.ctx.scripts[name] = lines
                self._save_script(name)
                ColorPrinter.success(f"Script '{name}' created.")
        elif sub == "run" and len(args) >= 2:
            name = args[1]
            if name not in self.ctx.scripts:
                ColorPrinter.error(f"Script '{name}' not found.")
                return
            expanded = expand_script_lines(self.ctx.scripts[name], {}, self.ctx)
            run_expanded(expanded, self.shell, self.ctx, debug=False)
        elif sub == "debug" and len(args) >= 2:
            name = args[1]
            if name not in self.ctx.scripts:
                ColorPrinter.error(f"Script '{name}' not found.")
                return
            expanded = expand_script_lines(self.ctx.scripts[name], {}, self.ctx)
            run_expanded(expanded, self.shell, self.ctx, debug=True)
        elif sub == "edit" and len(args) >= 2:
            name = args[1]
            current = self.ctx.scripts.get(name, [])
            lines = self._edit_script(name, current)
            if lines is not None:
                self.ctx.scripts[name] = lines
                self._save_script(name)
                ColorPrinter.success(f"Script '{name}' updated.")
        elif sub == "list":
            if not self.ctx.scripts:
                ColorPrinter.warning("No scripts saved.")
                return
            for name, lines in sorted(self.ctx.scripts.items()):
                ColorPrinter.cyan(f"  {name}  ({len(lines)} lines)")
        elif sub == "rm" and len(args) >= 2:
            name = args[1]
            if name not in self.ctx.scripts:
                ColorPrinter.warning(f"Script '{name}' not found.")
                return
            del self.ctx.scripts[name]
            path = self.ctx.script_file(name)
            with contextlib.suppress(OSError):
                os.remove(path)
            ColorPrinter.success(f"Script '{name}' deleted.")
        elif sub == "show" and len(args) >= 2:
            name = args[1]
            if name not in self.ctx.scripts:
                ColorPrinter.warning(f"Script '{name}' not found.")
                return
            for i, line in enumerate(self.ctx.scripts[name], 1):
                print(f"  {i:>3}  {line}")
        elif sub == "import" and len(args) >= 3:
            name = args[1]
            path = args[2]
            try:
                with open(path, encoding="utf-8") as f:
                    lines = [line.rstrip("\n") for line in f.readlines()]
                while lines and not lines[-1].strip():
                    lines.pop()
                self.ctx.scripts[name] = lines
                self._save_script(name)
                ColorPrinter.success(f"Imported '{path}' as script '{name}' ({len(lines)} lines).")
            except Exception as exc:
                ColorPrinter.error(f"Failed to import: {exc}")
        elif sub == "load":
            self.ctx.scripts = self.ctx.load_scripts()
            ColorPrinter.success(f"Loaded {len(self.ctx.scripts)} script(s).")
        elif sub == "save":
            for name in self.ctx.scripts:
                self._save_script(name)
            ColorPrinter.success(f"Saved {len(self.ctx.scripts)} script(s).")
        elif sub == "dir":
            rest = args[1:]
            if not rest:
                ColorPrinter.cyan(f"Scripts dir: {self.ctx.get_scripts_dir()}")
                return
            path_arg = rest[0]
            if path_arg.lower() == "reset":
                self.ctx._scripts_dir_override = None
                ColorPrinter.success(f"Scripts dir reset to default: {self.ctx.get_scripts_dir()}")
            else:
                resolved = os.path.abspath(path_arg)
                try:
                    os.makedirs(resolved, exist_ok=True)
                    self.ctx._scripts_dir_override = resolved
                    self.ctx.scripts = self.ctx.load_scripts()
                    ColorPrinter.success(f"Scripts dir set to: {resolved}")
                except Exception as exc:
                    ColorPrinter.error(f"Cannot use '{resolved}': {exc}")
        else:
            ColorPrinter.warning(f"Unknown script sub-command: {sub}")

    def do_record(self, arg: str) -> None:
        args = self.parse_args(arg)
        if not args:
            if self.ctx.record_script:
                ColorPrinter.info(f"Recording to: {self.ctx.record_script}")
            else:
                ColorPrinter.warning("Not recording.")
            self.print_colored_usage([
                "# RECORD", "",
                "record start <name>  # start recording commands to a script",
                "record stop          # stop recording",
                "record status        # show recording status",
            ])
            return
        sub = args[0].lower()
        if sub == "start" and len(args) >= 2:
            name = args[1]
            self.ctx.record_script = name
            if name not in self.ctx.scripts:
                self.ctx.scripts[name] = []
            ColorPrinter.success(f"Recording to '{name}'. Type 'record stop' when done.")
        elif sub == "stop":
            if self.ctx.record_script:
                name = self.ctx.record_script
                self._save_script(name)
                ColorPrinter.success(f"Stopped recording. Script '{name}' saved ({len(self.ctx.scripts.get(name, []))} lines).")
                self.ctx.record_script = None
            else:
                ColorPrinter.warning("Not recording.")
        elif sub == "status":
            if self.ctx.record_script:
                lines = self.ctx.scripts.get(self.ctx.record_script, [])
                ColorPrinter.info(f"Recording to: {self.ctx.record_script} ({len(lines)} lines)")
            else:
                ColorPrinter.info("Not recording.")

    def do_examples(self, arg: str) -> None:
        args = self.parse_args(arg)
        try:
            from lab_instruments.examples import EXAMPLES
        except ImportError:
            ColorPrinter.warning("No examples available.")
            return
        if not args:
            ColorPrinter.info("Available example scripts:")
            for name, info in EXAMPLES.items():
                desc = info.get("description", "")
                ColorPrinter.cyan(f"  {name}: {desc}")
            print("\n  Use: examples load <name>  or  examples load all")
            return
        if args[0].lower() == "load":
            name = args[1] if len(args) >= 2 else None
            if name == "all":
                for ename, info in EXAMPLES.items():
                    self.ctx.scripts[ename] = info.get("lines", [])
                ColorPrinter.success(f"Loaded {len(EXAMPLES)} example scripts.")
            elif name and name in EXAMPLES:
                self.ctx.scripts[name] = EXAMPLES[name].get("lines", [])
                ColorPrinter.success(f"Loaded example '{name}'.")
            else:
                ColorPrinter.warning(f"Example '{name}' not found.")

    def do_python(self, arg: str) -> None:
        args = self.parse_args(arg)
        args, help_flag = self.strip_help(args)
        if help_flag or not args:
            self.print_colored_usage([
                "# PYTHON SCRIPT EXECUTION", "",
                "python <file.py> - execute external Python script",
                "  - The script has access to REPL context:",
                "  - repl: the REPL instance",
                "  - devices: dictionary of connected instruments",
                "  - measurements: list of recorded measurements",
                "  - ColorPrinter: for colored output",
            ])
            return
        filename = args[0]
        if not os.path.exists(filename):
            ColorPrinter.error(f"File not found: {filename}")
            return
        try:
            with open(filename) as f:
                script_code = f.read()
        except Exception as exc:
            ColorPrinter.error(f"Failed to read file: {exc}")
            return
        exec_globals = {
            "__name__": "__main__",
            "__file__": filename,
            "repl": self.shell,
            "devices": self.registry.devices,
            "measurements": self.measurements.entries,
            "ColorPrinter": ColorPrinter,
            "os": os,
            "json": json,
            "time": time,
        }
        try:
            ColorPrinter.info(f"Executing {filename}...")
            exec(script_code, exec_globals)
            ColorPrinter.success(f"Script {filename} executed successfully")
        except Exception as exc:
            ColorPrinter.error(f"Script execution failed: {exc}")
            traceback.print_exc()

    def do_upper_limit(self, arg: str) -> None:
        if not arg:
            self.print_colored_usage([
                "# UPPER LIMIT", "",
                "upper_limit <device> [chan <N>] <param> <value>",
                "", "# PSU PARAMS", "",
                "upper_limit psu voltage <V>", "upper_limit psu current <A>",
                "upper_limit psu chan <N> voltage <V>",
                "", "# AWG PARAMS", "",
                "upper_limit awg voltage <V>", "upper_limit awg vpp <V>",
                "upper_limit awg freq <Hz>", "upper_limit awg chan <N> voltage <V>",
            ])
            return
        before = self.ctx.command_had_error
        self.ctx.command_had_error = False
        expand_script_lines([f"upper_limit {arg}"], {}, self.ctx, depth=1)
        if not self.ctx.command_had_error:
            ColorPrinter.success(f"Limit set: upper_limit {arg}")
            self.safety.retroactive_limit_check_all()
        self.ctx.command_had_error = before

    def do_lower_limit(self, arg: str) -> None:
        if not arg:
            self.print_colored_usage([
                "# LOWER LIMIT", "",
                "lower_limit <device> [chan <N>] <param> <value>",
                "", "# PSU PARAMS", "",
                "lower_limit psu voltage <V>", "lower_limit psu current <A>",
                "", "# AWG PARAMS", "",
                "lower_limit awg voltage <V>", "lower_limit awg vpp <V>",
                "lower_limit awg freq <Hz>",
            ])
            return
        before = self.ctx.command_had_error
        self.ctx.command_had_error = False
        expand_script_lines([f"lower_limit {arg}"], {}, self.ctx, depth=1)
        if not self.ctx.command_had_error:
            ColorPrinter.success(f"Limit set: lower_limit {arg}")
            self.safety.retroactive_limit_check_all()
        self.ctx.command_had_error = before

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _save_script(self, name: str) -> None:
        try:
            script_path = self.ctx.script_file(name)
            lines = self.ctx.scripts[name]
            with open(script_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
                if lines:
                    f.write("\n")
        except Exception as exc:
            ColorPrinter.error(f"Failed to save script '{name}': {exc}")

    def _edit_script(self, name: str, current_lines: list):
        if os.name == "nt":
            path = pathlib.Path(self.ctx.script_file(name))
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
            except Exception as exc:
                ColorPrinter.error(f"Cannot create scripts directory '{path.parent}': {exc}")
                return None
            self.ctx.scripts[name] = list(current_lines)
            self._save_script(name)
            try:
                path.touch(exist_ok=True)
            except Exception as exc:
                ColorPrinter.error(f"Cannot create script file '{path}': {exc}")
                return None
            self._open_file_nonblocking(str(path))
            ColorPrinter.info(f"Opened '{path}' — edit and save it, then run: script load")
            return None
        editor = os.environ.get("EDITOR", "nano")
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".repl", encoding="utf-8", newline="\n") as handle:
                tmp_path = handle.name
                handle.write(f"# Script: {name}\n")
                handle.write("# Syntax: set <var> <val>  |  $var  |  repeat <n> ... end  |  for <var> v1 v2 ... end  |  call <name>\n")
                handle.write("#\n")
                for line in current_lines:
                    handle.write(f"{line}\n")
            try:
                subprocess.run([editor, tmp_path])
            except FileNotFoundError:
                ColorPrinter.error(f"Editor '{editor}' not found. Set $EDITOR.")
                return list(current_lines)
            with open(tmp_path, encoding="utf-8") as handle:
                lines = [line.rstrip("\n") for line in handle.readlines()]
            result = []
            for line in lines:
                stripped = line.strip()
                if stripped.startswith("# Script:") or stripped.startswith("# Syntax:") or stripped == "#":
                    continue
                result.append(line)
            return result
        finally:
            if tmp_path and os.path.exists(tmp_path):
                with contextlib.suppress(OSError):
                    os.remove(tmp_path)

    @staticmethod
    def _open_file_nonblocking(path: str) -> None:
        if os.name == "nt":
            os.startfile(path)
            return
        editor = os.environ.get("EDITOR")
        if editor:
            subprocess.Popen([editor, path])
        else:
            subprocess.Popen(["xdg-open", path])
