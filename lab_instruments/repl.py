#!/usr/bin/env python3
"""
Interactive REPL for ESET-452 lab instruments.

Use to discover instruments, send commands, and place devices into known states.
"""

# Use NI-VISA backend for USB device support (pyvisa-py doesn't support USB-TMC)
# The discovery code has been updated with timeouts to prevent hanging
import os
import re
import sys
# os.environ['PYVISA_LIBRARY'] = '@py'  # Disabled - need NI-VISA for USB

import cmd
import json
import shlex
import subprocess
import tempfile
import time
import ast
import inspect
import traceback
import signal
import atexit
from typing import Dict, Any, Optional

from lab_instruments import InstrumentDiscovery, ColorPrinter


DEVICE_NAMES = ("scope", "psu", "awg", "dmm", "dds")

PSU_CHANNEL_ALIASES = {
    # Unified channel numbers
    "1": "positive_6_volts_channel",
    "2": "positive_25_volts_channel",
    "3": "negative_25_volts_channel",
    # Internal names
    "positive_6_volts_channel": "positive_6_volts_channel",
    "positive_25_volts_channel": "positive_25_volts_channel",
    "negative_25_volts_channel": "negative_25_volts_channel",
}

AWG_WAVE_KEYS = {
    "freq": "frequency",
    "frequency": "frequency",
    "amp": "amplitude",
    "amplitude": "amplitude",
    "offset": "offset",
    "phase": "phase",
    "duty": "duty",
    "sym": "symmetry",
    "symmetry": "symmetry",
}

# Maps user-friendly waveform names → canonical SCPI abbreviations used by SCPI AWGs
AWG_WAVE_ALIASES = {
    "sine":     "SIN",
    "sin":      "SIN",
    "square":   "SQU",
    "squ":      "SQU",
    "ramp":     "RAMP",
    "triangle": "RAMP",
    "tri":      "RAMP",
    "pulse":    "PULS",
    "puls":     "PULS",
    "noise":    "NOIS",
    "nois":     "NOIS",
    "dc":       "DC",
    "arb":      "ARB",
    "prbs":     "PRBS",
}

DMM_MODE_ALIASES = {
    "vdc": "dc_voltage",
    "vac": "ac_voltage",
    "idc": "dc_current",
    "iac": "ac_current",
    "res": "resistance_2wire",
    "fres": "resistance_4wire",
    "freq": "frequency",
    "per": "period",
    "cont": "continuity",
    "diode": "diode",
}


class InstrumentRepl(cmd.Cmd):
    intro = "ESET-452 Instrument REPL. Type 'help' for commands."
    prompt = "eset> "

    def __init__(self):
        super().__init__()
        self.discovery = InstrumentDiscovery()
        self.devices: Dict[str, Any] = {}
        self.selected: Optional[str] = None
        self._scripts_path = ".repl_scripts.json"
        self.scripts: Dict[str, Any] = self._load_scripts()
        self.measurements = []
        self._dmm_text_loop_active = False
        self._dmm_text_frames = []
        self._dmm_text_index = 0
        self._dmm_text_delay = 0.2
        self._dmm_text_last = 0.0
        self._device_override: Optional[str] = None  # set by default() for awg1, scope2, etc.
        self._cleanup_done = False

        ColorPrinter.info("Scanning for instruments... (Ctrl+C to cancel)")
        self.scan()
        if self.devices:
            ColorPrinter.success(f"Found {len(self.devices)} device(s)")
        else:
            ColorPrinter.warning(f"Found {len(self.devices)} device(s)")

        # Register cleanup handlers AFTER scan completes (so Ctrl+C works during scan)
        if self.devices:
            atexit.register(self._cleanup_on_exit)
            signal.signal(signal.SIGINT, self._cleanup_on_interrupt)
            if hasattr(signal, 'SIGTERM'):
                signal.signal(signal.SIGTERM, self._cleanup_on_interrupt)

            # Ensure all instruments start in safe/off state
            try:
                ColorPrinter.info("\n=== Setting all instruments to safe state ===")
                self._safe_all()
                print()  # Add blank line after startup
            except Exception as exc:
                ColorPrinter.error(f"Error during startup safety check: {exc}")
                traceback.print_exc()

    def _cleanup_on_exit(self):
        """Called automatically on normal program exit (via atexit)."""
        if not self._cleanup_done and self.devices:
            self._cleanup_done = True
            ColorPrinter.warning("\n=== Shutting down instruments safely ===")
            try:
                self._safe_all()
            except Exception as exc:
                ColorPrinter.error(f"Error during cleanup: {exc}")

    def _cleanup_on_interrupt(self, signum, frame):
        """Called when Ctrl+C or termination signal is received."""
        if not self._cleanup_done and self.devices:
            self._cleanup_done = True
            ColorPrinter.warning("\n\n=== Interrupted! Shutting down instruments safely ===")
            try:
                self._safe_all()
            except Exception as exc:
                ColorPrinter.error(f"Error during cleanup: {exc}")
        # Exit gracefully
        print("\nGoodbye!")
        os._exit(0)

    # --------------------------
    # Core helpers
    # --------------------------
    def scan(self):
        self.devices = self.discovery.scan(verbose=True)
        if self.devices and self.selected not in self.devices:
            self.selected = next(iter(self.devices))

    def _get_device(self, name: Optional[str]) -> Optional[Any]:
        if not self.devices:
            ColorPrinter.warning("No instruments connected. Run 'scan' first.")
            return None

        if name is None:
            if self.selected is None:
                ColorPrinter.warning("No active instrument. Use 'use <name>'.")
                return None
            return self.devices.get(self.selected)

        if name not in self.devices:
            ColorPrinter.warning(
                f"Unknown instrument '{name}'. Available: {list(self.devices.keys())}"
            )
            return None
        return self.devices.get(name)

    def _resolve_device_type(self, device_type: str) -> Optional[str]:
        """
        Resolve a generic device type to a specific device instance.

        Discovers candidates dynamically by matching device names against the
        pattern ^<type>\\d*$ so awg, awg1, awg2, scope, scope1, psu, dmm, etc.
        all work.  If a specific device was pre-selected via default() routing
        (e.g. the user typed 'awg1 wave ...'), _device_override is used directly.

        Returns the assigned device name string, or None if not found.
        """
        # If a specific device was pre-selected by default() routing, use it directly
        if self._device_override and self._device_override in self.devices:
            return self._device_override

        # Build candidate list dynamically: names matching ^<type>\d*$
        pattern = re.compile(rf'^{re.escape(device_type)}\d*$')
        candidates = [name for name in self.devices if pattern.match(name)]

        # Legacy: 'awg' command also matches old 'dds' key (JDS6600)
        if device_type == 'awg' and 'dds' in self.devices and 'dds' not in candidates:
            candidates.append('dds')

        if not candidates:
            ColorPrinter.warning(f"No {device_type.upper()} found. Run 'scan' first.")
            return None

        if len(candidates) == 1:
            return candidates[0]

        # Multiple devices — require explicit naming
        ColorPrinter.warning(
            f"Multiple {device_type.upper()}s found: {candidates}. "
            f"Use explicit name, e.g. '{candidates[0]}'."
        )
        return None

    def _parse_args(self, arg):
        try:
            return shlex.split(arg)
        except ValueError as exc:
            ColorPrinter.error(f"Parse error: {exc}")
            return []

    def _channels_for_device(self, dev, base_type: str):
        """Return the list of channel numbers for a device, or None if not applicable."""
        if hasattr(dev, 'CHANNEL_MAP'):
            return sorted(dev.CHANNEL_MAP.keys())
        if base_type == 'scope':
            return list(range(1, getattr(dev, 'num_channels', 4) + 1))
        if base_type == 'psu':
            if 'E3631A' in type(dev).__name__:
                return [1, 2, 3]
            return [1]
        if 'JDS6600' in type(dev).__name__:
            return [1, 2]
        return None

    def _load_scripts(self, path: Optional[str] = None):
        target = path or self._scripts_path
        try:
            with open(target, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            if isinstance(data, dict):
                return data
        except FileNotFoundError:
            return {}
        except Exception as exc:
            ColorPrinter.error(f"Failed to load scripts: {exc}")
        return {}

    def _save_scripts(self, path: Optional[str] = None):
        target = path or self._scripts_path
        try:
            with open(target, "w", encoding="utf-8") as handle:
                json.dump(self.scripts, handle, indent=2, sort_keys=True)
        except Exception as exc:
            ColorPrinter.error(f"Failed to save scripts: {exc}")
    
    def _edit_script_in_editor(self, name, current_lines):
        editor = os.environ.get("EDITOR")
        if not editor:
            editor = "notepad" if os.name == "nt" else "nano"
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", delete=False, suffix=".repl", encoding="utf-8", newline="\n"
            ) as handle:
                tmp_path = handle.name
                handle.write(f"# Script: {name}\n")
                handle.write("# Syntax: set <var> <val>  |  ${var}  |  repeat <n> ... end  |  for <var> v1 v2 ... end  |  call <name>\n")
                handle.write("#\n")
                for line in current_lines:
                    handle.write(f"{line}\n")
            try:
                subprocess.run([editor, tmp_path])
            except FileNotFoundError:
                ColorPrinter.error(f"Editor '{editor}' not found. Set $EDITOR to a valid editor.")
                return list(current_lines)
            with open(tmp_path, "r", encoding="utf-8") as handle:
                lines = [line.rstrip("\n") for line in handle.readlines()]
            # Strip comment header lines added by this editor
            result = []
            for line in lines:
                stripped = line.strip()
                if stripped.startswith("# Script:") or stripped.startswith("# Syntax:") or stripped == "#":
                    continue
                result.append(line)
            return result
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass

    def _open_file_nonblocking(self, path):
        if os.name == "nt":
            os.startfile(path)
            return
        editor = os.environ.get("EDITOR")
        if editor:
            subprocess.Popen([editor, path])
        else:
            subprocess.Popen(["xdg-open", path])

    def _is_help(self, args):
        if not args:
            return False
        return args[-1].lower() in ("help", "-h", "--help")

    def _strip_help(self, args):
        if self._is_help(args):
            return args[:-1], True
        return args, False

    def _print_usage(self, lines):
        for line in lines:
            print(line)

    def _print_colored_usage(self, lines):
        """Print colorful usage help for a command."""
        for line in lines:
            # Apply color coding based on content patterns
            if line.strip().startswith("#"):
                # Section headers
                ColorPrinter.header(line.strip("# ").strip())
            elif line.strip().startswith("-"):
                # Examples and sub-items in yellow
                print(f"{ColorPrinter.YELLOW}{line}{ColorPrinter.RESET}")
            elif "<" in line and ">" in line:
                # Commands with parameters - highlight command in cyan
                parts = line.split(" ", 1)
                if len(parts) == 2:
                    cmd = parts[0]
                    rest = parts[1]
                    print(f"{ColorPrinter.CYAN}{cmd}{ColorPrinter.RESET} {rest}")
                else:
                    print(f"{ColorPrinter.CYAN}{line}{ColorPrinter.RESET}")
            elif line.strip() and not line.startswith(" "):
                # Top-level commands in cyan
                print(f"{ColorPrinter.CYAN}{line}{ColorPrinter.RESET}")
            else:
                # Regular text
                print(line)

    def _stop_dmm_text_loop(self):
        self._dmm_text_loop_active = False
        self._dmm_text_frames = []
        self._dmm_text_index = 0
        self._dmm_text_last = 0.0

    def _start_dmm_text_loop(self, message, width=12, delay=0.2, pad=4):
        text = str(message)
        width = max(1, int(width))
        pad = max(1, int(pad))
        spacer = " " * pad
        window_text = text + spacer
        cycle_text = window_text + window_text
        frames = []
        for start in range(len(window_text)):
            frames.append(cycle_text[start : start + width])
        if not frames:
            frames = [text[:width]]
        self._dmm_text_frames = frames
        self._dmm_text_index = 0
        self._dmm_text_delay = float(delay)
        self._dmm_text_last = 0.0
        self._dmm_text_loop_active = True

    def _tick_dmm_text_loop(self, force=False):
        if not self._dmm_text_loop_active or not self._dmm_text_frames:
            return
        now = time.time()
        if not force and (now - self._dmm_text_last) < self._dmm_text_delay:
            return
        dev = self._get_device("dmm")
        if not dev:
            return
        frame = self._dmm_text_frames[self._dmm_text_index]
        self._dmm_text_index = (self._dmm_text_index + 1) % len(self._dmm_text_frames)
        self._dmm_text_last = now
        try:
            dev.display_text(frame)
        except Exception:
            self._stop_dmm_text_loop()

    def _record_measurement(self, label, value, unit="", source=""):
        self.measurements.append(
            {
                "label": label,
                "value": value,
                "unit": unit,
                "source": source,
            }
        )

    def _safe_eval(self, expr, names):
        allowed_funcs = {"abs": abs, "min": min, "max": max, "round": round}

        def _eval(node):
            if isinstance(node, ast.Expression):
                return _eval(node.body)
            if isinstance(node, ast.Constant):
                if isinstance(node.value, (int, float)):
                    return node.value
                raise ValueError("Only numeric constants are allowed.")
            if isinstance(node, ast.Name):
                if node.id in names:
                    return names[node.id]
                if node.id in allowed_funcs:
                    return allowed_funcs[node.id]
                raise ValueError(f"Unknown name '{node.id}'.")
            if isinstance(node, ast.BinOp):
                left = _eval(node.left)
                right = _eval(node.right)
                if isinstance(node.op, ast.Add):
                    return left + right
                if isinstance(node.op, ast.Sub):
                    return left - right
                if isinstance(node.op, ast.Mult):
                    return left * right
                if isinstance(node.op, ast.Div):
                    return left / right
                if isinstance(node.op, ast.Pow):
                    return left ** right
                if isinstance(node.op, ast.Mod):
                    return left % right
                raise ValueError("Operator not allowed.")
            if isinstance(node, ast.UnaryOp):
                operand = _eval(node.operand)
                if isinstance(node.op, ast.UAdd):
                    return +operand
                if isinstance(node.op, ast.USub):
                    return -operand
                raise ValueError("Unary operator not allowed.")
            if isinstance(node, ast.Subscript):
                value = _eval(node.value)
                if not isinstance(value, dict):
                    raise ValueError("Subscript base must be a dict.")
                if isinstance(node.slice, ast.Constant):
                    key = node.slice.value
                elif isinstance(node.slice, ast.Name):
                    key = node.slice.id
                else:
                    key = _eval(node.slice)
                return value[key]
            if isinstance(node, ast.Call):
                func = _eval(node.func)
                args = [_eval(arg) for arg in node.args]
                if func in allowed_funcs.values():
                    return func(*args)
                raise ValueError("Function not allowed.")
            raise ValueError("Expression not allowed.")

        parsed = ast.parse(expr, mode="eval")
        return _eval(parsed)

    def _substitute_vars(self, text, variables):
        result = text
        for name, value in variables.items():
            result = result.replace(f"${{{name}}}", str(value))
        return result

    def _expand_script_lines(self, lines, variables, depth=0):
        if depth > 10:
            ColorPrinter.error("Maximum script call depth (10) exceeded.")
            return []
        expanded = []
        idx = 0
        while idx < len(lines):
            raw_line = lines[idx].strip()
            idx += 1
            if not raw_line or raw_line.startswith("#"):
                continue
            tokens = shlex.split(raw_line)
            if not tokens:
                continue
            head = tokens[0].lower()
            if head == "set" and len(tokens) >= 3:
                key = tokens[1]
                raw_val = self._substitute_vars(" ".join(tokens[2:]), variables)
                try:
                    num_vars = {}
                    for k, v in variables.items():
                        try:
                            num_vars[k] = float(v)
                        except (TypeError, ValueError):
                            pass
                    result = self._safe_eval(raw_val, num_vars)
                    variables[key] = str(result)
                except Exception:
                    variables[key] = raw_val
                continue
            if head == "call" and len(tokens) >= 2:
                script_name = tokens[1]
                if script_name not in self.scripts:
                    ColorPrinter.error(f"call: script '{script_name}' not found.")
                    continue
                call_params = dict(variables)
                for token in tokens[2:]:
                    if "=" in token:
                        k, v = token.split("=", 1)
                        call_params[k] = v
                expanded.extend(self._expand_script_lines(self.scripts[script_name], call_params, depth + 1))
                continue
            if head == "repeat" and len(tokens) >= 2:
                try:
                    count = int(tokens[1])
                except ValueError:
                    ColorPrinter.error(f"repeat: expected integer count, got '{tokens[1]}'")
                    continue
                block = []
                depth_inner = 1
                while idx < len(lines):
                    line = lines[idx].strip()
                    idx += 1
                    if not line or line.startswith("#"):
                        continue
                    line_tokens = shlex.split(line)
                    if not line_tokens:
                        continue
                    if line_tokens[0].lower() in ("repeat", "for"):
                        depth_inner += 1
                    elif line_tokens[0].lower() == "end":
                        depth_inner -= 1
                        if depth_inner == 0:
                            break
                    block.append(line)
                for _ in range(count):
                    expanded.extend(self._expand_script_lines(block, dict(variables), depth))
                continue
            if head == "for" and len(tokens) >= 3:
                key = tokens[1]
                values = tokens[2:]
                block = []
                depth_inner = 1
                while idx < len(lines):
                    line = lines[idx].strip()
                    idx += 1
                    if not line or line.startswith("#"):
                        continue
                    line_tokens = shlex.split(line)
                    if not line_tokens:
                        continue
                    if line_tokens[0].lower() in ("repeat", "for"):
                        depth_inner += 1
                    elif line_tokens[0].lower() == "end":
                        depth_inner -= 1
                        if depth_inner == 0:
                            break
                    block.append(line)
                if "," in key:
                    keys = [name for name in key.split(",") if name]
                    for value in values:
                        parts = value.split(",")
                        if len(parts) != len(keys):
                            ColorPrinter.error("for: var list and value list length mismatch.")
                            break
                        local_vars = dict(variables)
                        for name, val in zip(keys, parts):
                            local_vars[name] = self._substitute_vars(val, variables)
                        expanded.extend(self._expand_script_lines(block, local_vars, depth))
                else:
                    for value in values:
                        local_vars = dict(variables)
                        local_vars[key] = self._substitute_vars(value, variables)
                        expanded.extend(self._expand_script_lines(block, local_vars, depth))
                continue
            if head == "end":
                continue
            expanded.append(self._substitute_vars(raw_line, variables))
        return expanded

    def _run_script_lines(self, lines):
        expanded = self._expand_script_lines(lines, {})
        for raw_line in expanded:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            self._tick_dmm_text_loop()
            if self.onecmd(line):
                return True
        return False

    def _onecmd_single(self, line):
        tokens = self._parse_args(line)
        if len(tokens) >= 3 and tokens[0].lower() == "repeat":
            try:
                count = int(tokens[1])
            except ValueError:
                return super().onecmd(line)
            cmd_line = " ".join(tokens[2:])
            for _ in range(count):
                if super().onecmd(cmd_line):
                    return True
            return False

        # Expand 'all' channel token into one call per channel
        # e.g. "awg wave all sine freq=1000" → "awg wave 1 sine ..." + "awg wave 2 sine ..."
        all_indices = [i for i, t in enumerate(tokens) if t.lower() == 'all']
        if all_indices:
            cmd_token = tokens[0].lower() if tokens else ''
            base_type = re.sub(r'\d+$', '', cmd_token)
            if base_type in ('awg', 'scope', 'psu', 'dds'):
                dev = None
                if self._device_override and self._device_override in self.devices:
                    dev = self.devices[self._device_override]
                elif cmd_token in self.devices:
                    dev = self.devices[cmd_token]
                else:
                    pattern = re.compile(rf'^{re.escape(base_type)}\d*$')
                    for dname, d in self.devices.items():
                        if pattern.match(dname):
                            dev = d
                            break
                    if dev is None and base_type == 'awg' and 'dds' in self.devices:
                        dev = self.devices['dds']
                if dev is not None:
                    channels = self._channels_for_device(dev, base_type)
                    if channels:
                        all_idx = all_indices[0]
                        for ch in channels:
                            new_tokens = list(tokens)
                            new_tokens[all_idx] = str(ch)
                            if super().onecmd(' '.join(new_tokens)):
                                return True
                        return False

        return super().onecmd(line)

    def onecmd(self, line):
        scan_line = line.replace(";", " ; ")
        tokens = self._parse_args(scan_line)
        if "repeat" in tokens or "repeatall" in tokens:
            try:
                if "repeatall" in tokens:
                    idx = tokens.index("repeatall")
                    repeat_all = True
                else:
                    idx = tokens.index("repeat")
                    repeat_all = False
                if idx + 2 < len(tokens) and "end" in tokens[idx + 2 :]:
                    end_idx = tokens.index("end", idx + 2)
                    count = int(tokens[idx + 1])
                    body_tokens = tokens[idx + 2 : end_idx]
                    body = " ".join(body_tokens).strip()
                    for _ in range(count):
                        if self.onecmd(body):
                            return True
                    remainder = tokens[end_idx + 1 :]
                    while remainder and remainder[0] == ";":
                        remainder = remainder[1:]
                    if remainder:
                        return self.onecmd(" ".join(remainder))
                    return False
                if repeat_all:
                    count = int(tokens[idx + 1])
                    cmd_line = " ".join(tokens[idx + 2 :])
                    for _ in range(count):
                        if self.onecmd(cmd_line):
                            return True
                    return False
            except (ValueError, IndexError):
                pass
        if len(tokens) >= 3 and tokens[0].lower() == "repeatall":
            try:
                count = int(tokens[1])
            except ValueError:
                return super().onecmd(line)
            cmd_line = " ".join(tokens[2:])
            for _ in range(count):
                if super().onecmd(cmd_line):
                    return True
            return False
        if ";" in line:
            should_exit = False
            for chunk in line.split(";"):
                cmd_line = chunk.strip()
                if not cmd_line:
                    continue
                if self._onecmd_single(cmd_line):
                    should_exit = True
                    break
            return should_exit
        return self._onecmd_single(line)

    def _print_devices(self):
        if not self.devices:
            ColorPrinter.warning("No instruments connected.")
            return
        for name, dev in self.devices.items():
            marker = "*" if name == self.selected else " "
            print(f"{marker} {name}: {dev.__class__.__name__}")

    def _safe_all(self):
        for name, dev in self.devices.items():
            try:
                # PSU devices (psu, psu1, psu2, ...)
                if name.startswith("psu"):
                    if hasattr(dev, 'disable_all_channels'):
                        dev.disable_all_channels()
                    elif hasattr(dev, 'enable_output'):
                        dev.enable_output(False)
                # AWG/DDS devices (awg, awg1, awg2, dds)
                elif name.startswith("awg") or name == "dds":
                    if hasattr(dev, 'disable_all_channels'):
                        dev.disable_all_channels()
                    elif hasattr(dev, 'enable_output'):
                        dev.enable_output(ch1=False, ch2=False)
                # Oscilloscope (scope, scope1, scope2, ...)
                elif name.startswith("scope"):
                    if hasattr(dev, 'stop'):
                        dev.stop()
                    if hasattr(dev, 'disable_all_channels'):
                        dev.disable_all_channels()
                    elif hasattr(dev, 'disable_channel'):
                        for ch in range(1, 5):
                            try:
                                dev.disable_channel(ch)
                            except Exception:
                                pass
                # DMM devices (dmm, dmm1, dmm2, ...)
                elif name.startswith("dmm"):
                    if hasattr(dev, 'reset'):
                        dev.reset()
                ColorPrinter.success(f"{name}: safe state applied")
            except Exception as exc:
                ColorPrinter.error(f"{name}: {exc}")

    def _reset_all(self):
        for name, dev in self.devices.items():
            try:
                dev.reset()
                ColorPrinter.success(f"{name}: reset")
            except Exception as exc:
                ColorPrinter.error(f"{name}: {exc}")

    def _off_all(self):
        for name, dev in self.devices.items():
            try:
                # PSU devices (psu, psu1, psu2, ...)
                if name.startswith("psu"):
                    if hasattr(dev, 'enable_output'):
                        dev.enable_output(False)
                        ColorPrinter.success(f"{name}: output disabled")
                # AWG/DDS devices (awg, awg1, awg2, dds)
                elif name.startswith("awg") or name == "dds":
                    if hasattr(dev, 'disable_all_channels'):
                        dev.disable_all_channels()
                        ColorPrinter.success(f"{name}: channels disabled")
                    elif hasattr(dev, 'enable_output'):
                        dev.enable_output(ch1=False, ch2=False)
                        ColorPrinter.success(f"{name}: outputs disabled")
                # Oscilloscope (scope, scope1, scope2, ...)
                elif name.startswith("scope"):
                    if hasattr(dev, 'stop'):
                        dev.stop()
                        ColorPrinter.success(f"{name}: acquisition stopped")
                    if hasattr(dev, 'disable_all_channels'):
                        dev.disable_all_channels()
                        ColorPrinter.success(f"{name}: channels disabled")
                    elif hasattr(dev, 'disable_channel'):
                        for ch in range(1, 5):
                            try:
                                dev.disable_channel(ch)
                            except Exception:
                                pass
                        ColorPrinter.success(f"{name}: all channels (1-4) disabled")
                # DMM devices (dmm, dmm1, dmm2, ...)
                elif name.startswith("dmm"):
                    if hasattr(dev, 'reset'):
                        dev.reset()
                        ColorPrinter.success(f"{name}: reset")
            except Exception as exc:
                ColorPrinter.error(f"{name}: {exc}")

    def _on_all(self):
        for name, dev in self.devices.items():
            try:
                # PSU devices (psu, psu1, psu2, ...)
                if name.startswith("psu"):
                    if hasattr(dev, 'enable_output'):
                        dev.enable_output(True)
                        ColorPrinter.success(f"{name}: output enabled")
                # AWG/DDS devices (awg, awg1, awg2, dds)
                elif name.startswith("awg") or name == "dds":
                    if hasattr(dev, 'enable_output'):
                        try:
                            dev.enable_output(ch1=True, ch2=True)
                        except TypeError:
                            dev.enable_output(1, True)
                            dev.enable_output(2, True)
                        ColorPrinter.success(f"{name}: outputs enabled")
                # Oscilloscope (scope, scope1, scope2, ...)
                elif name.startswith("scope"):
                    if hasattr(dev, 'enable_all_channels'):
                        dev.enable_all_channels()
                        ColorPrinter.success(f"{name}: channels enabled")
                # DMM devices - no "on" state, nothing to do
            except Exception as exc:
                ColorPrinter.error(f"{name}: {exc}")

    # --------------------------
    # General commands
    # --------------------------
    def do_scan(self, arg):
        "scan: discover and connect to instruments"
        args = self._parse_args(arg)
        if self._is_help(args):
            self._print_usage(["scan  # rescan and connect to instruments"])
            return
        self.scan()

    def do_reload(self, arg):
        "reload: restart the REPL process to pick up changes to repl.py and lab_instruments"
        ColorPrinter.info("Disconnecting all instruments...")
        for dev in list(self.devices.values()):
            try:
                dev.disconnect()
            except Exception:
                pass

        ColorPrinter.success("Restarting process...")
        os.execv(sys.executable, [sys.executable] + sys.argv)

    def do_list(self, arg):
        "list: show connected instruments"
        args = self._parse_args(arg)
        if self._is_help(args):
            self._print_usage(["list  # show connected instruments"])
            return
        self._print_devices()

    def do_use(self, arg):
        "use <name>: set active instrument (scope, psu, awg, dmm)"
        args = self._parse_args(arg)
        if self._is_help(args) or not args:
            self._print_usage(
                [
                    "use <name>",
                    "  - name: scope|psu|awg|dmm",
                    "  - example: use dmm",
                    "  - after use dmm, you can run: idn  (same as: idn dmm)",
                ]
            )
            self._print_devices()
            return
        name = args[0]
        if name not in self.devices:
            ColorPrinter.warning(f"Unknown instrument '{name}'.")
            return
        self.selected = name
        ColorPrinter.success(f"Selected: {name}")

    def default(self, line):
        """Handle numbered device names like 'awg1', 'scope2', 'psu1', 'dmm3'."""
        parts = line.split(None, 1)
        cmd_token = parts[0]
        rest = parts[1] if len(parts) > 1 else ""

        if cmd_token in self.devices:
            # Strip trailing digits to get the base type ("awg1" → "awg")
            base_type = re.sub(r'\d+$', '', cmd_token)
            handler = getattr(self, f"do_{base_type}", None)
            if handler:
                self._device_override = cmd_token
                try:
                    handler(rest)
                finally:
                    self._device_override = None
                return

        ColorPrinter.error(f"Unknown syntax: {line}")

    def do_idn(self, arg):
        "idn [name]: query *IDN? for selected or named instrument"
        args = self._parse_args(arg)
        if self._is_help(args):
            self._print_usage(
                [
                    "idn [name]",
                    "  - example: idn",
                    "  - example: idn dmm",
                ]
            )
            return
        name = args[0] if args else None
        dev = self._get_device(name)
        if not dev:
            return
        try:
            ColorPrinter.cyan(dev.query("*IDN?"))
        except Exception as exc:
            ColorPrinter.error(str(exc))

    def do_raw(self, arg):
        "raw [name] <scpi>: send raw SCPI; if ends with ?, query and print"
        args = self._parse_args(arg)
        args, help_flag = self._strip_help(args)
        if not args or help_flag:
            self._print_usage(
                [
                    "raw [name] <scpi>",
                    "  - example: raw *IDN?",
                    "  - example: raw scope MEASUrement:IMMed:VALue?",
                ]
            )
            return
        name = None
        if args[0] in self.devices:
            name = args[0]
            args = args[1:]
        dev = self._get_device(name)
        if not dev or not args:
            return
        cmd_str = " ".join(args)
        try:
            if cmd_str.strip().endswith("?"):
                ColorPrinter.cyan(dev.query(cmd_str))
            else:
                dev.send_command(cmd_str)
        except Exception as exc:
            ColorPrinter.error(str(exc))

    def do_state(self, arg):
        "state [safe|reset|list] or state <device> <safe|reset|on|off>"
        args = self._parse_args(arg)
        if self._is_help(args):
            self._print_usage(
                [
                    "state off                # outputs off for all devices",
                    "state on                 # outputs on for all devices",
                    "state safe               # safe state for all devices",
                    "state reset              # *RST for all devices",
                    "state <dev> on|off|safe|reset",
                    "state list",
                ]
            )
            return
        if not args or args[0] == "list":
            self._print_usage(
                [
                    "state off                # outputs off for all devices",
                    "state on                 # outputs on for all devices",
                    "state safe               # safe state for all devices",
                    "state reset              # *RST for all devices",
                    "state <dev> on|off|safe|reset",
                    "state list",
                ]
            )
            return

        if args[0] in ("safe", "reset", "off", "on"):
            if args[0] == "safe":
                self._safe_all()
            elif args[0] == "off":
                self._off_all()
            elif args[0] == "on":
                self._on_all()
            else:
                self._reset_all()
            return

        if len(args) < 2:
            ColorPrinter.warning("Usage: state <device> <safe|reset|on|off>")
            return

        name = args[0]
        state = args[1].lower()
        dev = self._get_device(name)
        if not dev:
            return

        try:
            if name.startswith("psu"):
                if state in ("safe", "off"):
                    dev.disable_all_channels()
                elif state == "on":
                    dev.enable_output(True)
                elif state == "reset":
                    dev.reset()
                else:
                    ColorPrinter.warning("PSU states: on, off, safe, reset")
            elif name.startswith("awg") or name == "dds":
                if state in ("safe", "off"):
                    dev.disable_all_channels()
                elif state == "on":
                    dev.enable_output(1, True)
                    dev.enable_output(2, True)
                elif state == "reset":
                    dev.reset()
                else:
                    ColorPrinter.warning("AWG states: on, off, safe, reset")
            elif name.startswith("scope"):
                if state in ("safe", "off"):
                    dev.disable_all_channels()
                elif state == "on":
                    dev.enable_all_channels()
                elif state == "reset":
                    dev.reset()
                else:
                    ColorPrinter.warning("Scope states: on, off, safe, reset")
            elif name.startswith("dmm"):
                if state in ("safe", "reset"):
                    dev.reset()
                else:
                    ColorPrinter.warning("DMM states: safe, reset")
        except Exception as exc:
            ColorPrinter.error(str(exc))

    def do_close(self, arg):
        "close: disconnect all instruments"
        args = self._parse_args(arg)
        if self._is_help(args):
            self._print_usage(["close  # disconnect all instruments"])
            return
        for name, dev in self.devices.items():
            try:
                dev.disconnect()
            except Exception as exc:
                ColorPrinter.error(f"{name}: {exc}")
        self.devices = {}
        self.selected = None

    def do_status(self, arg):
        "status: show current selection"
        args = self._parse_args(arg)
        if self._is_help(args):
            self._print_usage(["status  # show current selection"])
            return
        if not self.devices:
            ColorPrinter.warning("No instruments connected.")
            return
        ColorPrinter.info(f"Selected: {self.selected}")
        self._print_devices()

    def do_sleep(self, arg):
        "sleep <seconds>: pause between actions"
        args = self._parse_args(arg)
        args, help_flag = self._strip_help(args)
        if not args or help_flag:
            self._print_usage(
                [
                    "sleep <seconds>",
                    "  - example: sleep 0.5",
                ]
            )
            return
        try:
            delay = float(args[0])
        except ValueError:
            ColorPrinter.warning("sleep expects a number of seconds.")
            return
        if delay < 0:
            ColorPrinter.warning("sleep expects a non-negative number.")
            return
        end_time = time.time() + delay
        while True:
            remaining = end_time - time.time()
            if remaining <= 0:
                break
            self._tick_dmm_text_loop()
            time.sleep(min(0.05, remaining))

    def do_wait(self, arg):
        "wait <seconds>: alias for sleep"
        return self.do_sleep(arg)

    def do_script(self, arg):
        "script <new|run|edit|list|rm|show|import|load|save> [args]: manage and run scripts"
        args = self._parse_args(arg)
        args, help_flag = self._strip_help(args)

        usage = [
            "script new  <name>                   # create new script in editor",
            "script run  <name> [key=val ...]      # execute with optional params",
            "script edit <name>                    # edit existing script in editor",
            "script list                           # show all scripts",
            "script rm   <name>                    # delete",
            "script show <name>                    # print script lines",
            "script import <name> <path>           # import from .txt file",
            "script load [path]                    # load JSON file",
            "script save [path]                    # save JSON file",
        ]

        if not args or help_flag:
            self._print_usage(usage)
            return

        subcmd = args[0].lower()

        if subcmd == "new":
            if len(args) < 2:
                ColorPrinter.warning("Usage: script new <name>")
                return
            name = args[1]
            if name in self.scripts:
                ColorPrinter.warning(f"Script '{name}' already exists — opening for edit. Use 'script rm {name}' first to start fresh.")
            lines = self._edit_script_in_editor(name, self.scripts.get(name, []))
            self.scripts[name] = lines
            self._save_scripts()
            ColorPrinter.success(f"Saved script '{name}' ({len(lines)} lines).")

        elif subcmd == "run":
            if len(args) < 2:
                ColorPrinter.warning("Usage: script run <name> [key=val ...]")
                return
            name = args[1]
            lines = self.scripts.get(name)
            if lines is None:
                ColorPrinter.warning(f"Script '{name}' not found.")
                return
            params = {}
            for token in args[2:]:
                if "=" in token:
                    key, value = token.split("=", 1)
                    params[key] = value
            expanded = self._expand_script_lines(lines, params)
            for raw_line in expanded:
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                self._tick_dmm_text_loop()
                if self.onecmd(line):
                    return True
            return False

        elif subcmd == "edit":
            if len(args) < 2:
                ColorPrinter.warning("Usage: script edit <name>")
                return
            name = args[1]
            if name not in self.scripts:
                ColorPrinter.warning(f"Script '{name}' not found.")
                return
            lines = self._edit_script_in_editor(name, self.scripts[name])
            self.scripts[name] = lines
            self._save_scripts()
            ColorPrinter.success(f"Updated script '{name}' ({len(lines)} lines).")

        elif subcmd == "list":
            if not self.scripts:
                ColorPrinter.warning("No scripts saved.")
                return
            for name in sorted(self.scripts.keys()):
                lines = self.scripts[name]
                count = f"{len(lines)} lines" if lines else "empty"
                print(f"  {name}  ({count})")

        elif subcmd == "rm":
            if len(args) < 2:
                ColorPrinter.warning("Usage: script rm <name>")
                return
            name = args[1]
            if name not in self.scripts:
                ColorPrinter.warning(f"Script '{name}' not found.")
                return
            del self.scripts[name]
            self._save_scripts()
            ColorPrinter.success(f"Deleted script '{name}'.")

        elif subcmd == "show":
            if len(args) < 2:
                ColorPrinter.warning("Usage: script show <name>")
                return
            name = args[1]
            if name not in self.scripts:
                ColorPrinter.warning(f"Script '{name}' not found.")
                return
            ColorPrinter.info(f"Script '{name}':")
            for line in self.scripts[name]:
                print(f"  {line}")

        elif subcmd == "import":
            if len(args) < 3:
                ColorPrinter.warning("Usage: script import <name> <path>")
                return
            name = args[1]
            path = args[2]
            try:
                with open(path, "r", encoding="utf-8") as handle:
                    lines = [line.rstrip("\n") for line in handle.readlines()]
                self.scripts[name] = lines
                self._save_scripts()
                ColorPrinter.success(f"Imported script '{name}' ({len(lines)} lines).")
            except Exception as exc:
                ColorPrinter.error(f"Failed to import script: {exc}")

        elif subcmd == "load":
            path = args[1] if len(args) >= 2 else None
            data = self._load_scripts(path)
            if not data:
                ColorPrinter.warning("No scripts loaded.")
                return
            self.scripts = data
            ColorPrinter.success(f"Loaded {len(self.scripts)} scripts.")

        elif subcmd == "save":
            path = args[1] if len(args) >= 2 else None
            self._save_scripts(path)
            ColorPrinter.success("Scripts saved.")

        else:
            ColorPrinter.warning(f"Unknown subcommand '{subcmd}'.")
            self._print_usage(usage)

    def do_all(self, arg):
        "all <on|off|safe|reset>: apply a state to all instruments"
        args = self._parse_args(arg)
        args, help_flag = self._strip_help(args)
        if not args or help_flag:
            self._print_usage(
                [
                    "all on",
                    "all off",
                    "all safe",
                    "all reset",
                ]
            )
            return
        state = args[0].lower()
        if state == "on":
            self._on_all()
        elif state == "off":
            self._off_all()
        elif state == "safe":
            self._safe_all()
        elif state == "reset":
            self._reset_all()
        else:
            ColorPrinter.warning("Use: all on|off|safe|reset")

    def do_exit(self, arg):
        "exit: quit the REPL"
        return True

    def do_quit(self, arg):
        "quit: quit the REPL"
        return True

    def do_EOF(self, arg):
        print()
        return True

    def do_help(self, arg):
        "help [command]: show help for a command, or list all commands"
        if arg:
            # Per-command help: show docstring, colorized
            try:
                func = getattr(self, f"help_{arg}")
                func()
                return
            except AttributeError:
                pass
            try:
                doc = getattr(self, f"do_{arg}").__doc__
            except AttributeError:
                doc = None
            if doc:
                # First token of docstring is the usage signature — print it in cyan
                lines = doc.strip().splitlines()
                first = lines[0]
                rest = lines[1:]
                print(f"{ColorPrinter.CYAN}{first}{ColorPrinter.RESET}")
                for line in rest:
                    print(line)
            else:
                ColorPrinter.warning(f"No help for '{arg}'.")
            return

        # Full listing — grouped by category
        C = ColorPrinter.CYAN
        Y = ColorPrinter.YELLOW
        B = ColorPrinter.BOLD
        R = ColorPrinter.RESET

        def section(title):
            print(f"\n{Y}{B}{title}{R}")

        def cmd_line(name, desc):
            print(f"  {C}{name:<12}{R} {desc}")

        print(f"{B}ESET-452 Instrument REPL{R}  —  type {C}help <command>{R} for details\n")

        section("GENERAL")
        cmd_line("scan",    "discover and connect to instruments")
        cmd_line("reload",  "restart the REPL process")
        cmd_line("list",    "show connected instruments")
        cmd_line("use",     "set active instrument  (use <name>)")
        cmd_line("status",  "show current selection")
        cmd_line("state",   "set instrument state  (safe/reset/on/off)")
        cmd_line("all",     "apply state to all instruments")
        cmd_line("idn",     "query *IDN?")
        cmd_line("raw",     "send raw SCPI command or query")
        cmd_line("sleep",   "pause between actions  (sleep <seconds>)")
        cmd_line("wait",    "alias for sleep")
        cmd_line("close",   "disconnect all instruments")
        cmd_line("exit",    "quit the REPL")
        cmd_line("quit",    "quit the REPL")

        section("INSTRUMENTS")
        cmd_line("psu",     "power supply  (output, set, meas, track, save, recall)")
        cmd_line("awg",     "function generator  (wave, freq, amp, offset, duty, phase)")
        cmd_line("dmm",     "multimeter  (config, read, fetch, meas, beep, display)")
        cmd_line("scope",   "oscilloscope  (chan, measure, save, trigger, awg, dvm, counter)")

        section("SCRIPTING")
        cmd_line("script",  "manage and run named scripts  (new, run, edit, list, rm, show, import, load, save)")
        cmd_line("python",  "execute an external Python script with REPL context")

        section("LOGGING & MATH")
        cmd_line("log",     "show or save recorded measurements  (print, save, clear)")
        cmd_line("calc",    "compute a value from logged measurements")

        print()

    # --------------------------
    # PSU commands
    # --------------------------
    def do_psu(self, arg):
        "psu <cmd>: control the power supply (output, set, meas, track, save, recall)"
        # Resolve which PSU to use (auto-select if only one)
        psu_name = self._resolve_device_type("psu")
        if not psu_name:
            return

        dev = self._get_device(psu_name)
        if not dev:
            return

        # Detect single-channel by checking if measure_voltage() takes a channel arg
        try:
            sig = inspect.signature(dev.measure_voltage)
            is_single_channel = "channel" not in sig.parameters
        except (ValueError, TypeError):
            is_single_channel = False
        return self._handle_psu_unified(arg, dev, psu_name, is_single_channel)

    def _handle_psu_unified(self, arg, dev, psu_name, is_single_channel):
        """Unified PSU command handler for all PSU types"""
        args = self._parse_args(arg)
        args, help_flag = self._strip_help(args)

        if not args:
            if is_single_channel:
                self._print_usage(
                    [
                        "# UNIFIED PSU COMMANDS (single-channel PSU)",
                        "",
                        "psu output on|off",
                        "psu set <voltage> [current]",
                        "  - voltage: 0-60V, current: 0-10A",
                        "  - example: psu set 5.0 1.0",
                        "psu meas v|i",
                        "psu meas_store v|i <label> [unit=]",
                        "psu get  (show setpoints)",
                        "psu state on|off|safe|reset",
                    ]
                )
            else:
                self._print_usage(
                    [
                        "# UNIFIED PSU COMMANDS (multi-channel PSU)",
                        "",
                        "psu output on|off",
                        "psu set <channel> <voltage> [current]",
                        "  - channels: 1 (6V), 2 (25V+), 3 (25V-)",
                        "  - example: psu set 1 5.0 0.2",
                        "  - example: psu set 2 12.0 0.5",
                        "psu meas v|i <channel>",
                        "  - example: psu meas v 1",
                        "psu meas_store v|i <channel> <label> [unit=]",
                        "psu track on|off",
                        "psu save <1-3>",
                        "psu recall <1-3>",
                        "psu state on|off|safe|reset",
                    ]
                )
            return

        cmd_name = args[0].lower()

        try:
            # OUTPUT COMMAND
            if cmd_name == "output" and len(args) >= 2:
                dev.enable_output(args[1].lower() == "on")
                ColorPrinter.success(f"Output {'enabled' if args[1].lower() == 'on' else 'disabled'}")

            # SET COMMAND - unified for both single and multi-channel
            elif cmd_name == "set":
                if is_single_channel:
                    # Single-channel: psu set <voltage> [current]
                    if len(args) < 2:
                        ColorPrinter.warning("Usage: psu set <voltage> [current]")
                        return
                    voltage = float(args[1])
                    current = float(args[2]) if len(args) >= 3 else None
                    dev.set_voltage(voltage)
                    if current is not None:
                        dev.set_current_limit(current)
                    ColorPrinter.success(
                        f"Set: {voltage}V @ {current if current else dev.get_current_limit()}A"
                    )
                else:
                    # Multi-channel: psu set <channel> <voltage> [current]
                    if len(args) < 3:
                        ColorPrinter.warning("Usage: psu set <channel> <voltage> [current]")
                        ColorPrinter.warning("Channels: 1 (6V), 2 (25V+), 3 (25V-)")
                        return
                    channel = PSU_CHANNEL_ALIASES.get(args[1].lower())
                    if not channel:
                        ColorPrinter.warning("Invalid channel. Use 1, 2, or 3")
                        return
                    voltage = float(args[2])
                    current = float(args[3]) if len(args) >= 4 else None
                    dev.set_output_channel(channel, voltage, current)
                    ColorPrinter.success(f"Set {args[1].upper()}: {voltage}V" + (f" @ {current}A" if current else ""))

            # MEAS COMMAND - unified for both single and multi-channel
            elif cmd_name == "meas":
                if is_single_channel:
                    # Single-channel: psu meas v|i
                    if len(args) < 2:
                        ColorPrinter.warning("Usage: psu meas v|i")
                        return
                    mode = args[1].lower()
                    if mode in ("v", "volt", "voltage"):
                        value = dev.measure_voltage()
                        ColorPrinter.cyan(f"{value:.6f}V")
                    elif mode in ("i", "curr", "current"):
                        value = dev.measure_current()
                        ColorPrinter.cyan(f"{value:.6f}A")
                    else:
                        ColorPrinter.warning("psu meas v|i")
                else:
                    # Multi-channel: psu meas v|i <channel>
                    if len(args) < 3:
                        ColorPrinter.warning("Usage: psu meas v|i <channel>")
                        return
                    mode = args[1].lower()
                    channel = PSU_CHANNEL_ALIASES.get(args[2].lower())
                    if not channel:
                        ColorPrinter.warning("Invalid channel. Use 1, 2, or 3")
                        return
                    if mode in ("v", "volt", "voltage"):
                        ColorPrinter.cyan(str(dev.measure_voltage(channel)))
                    elif mode in ("i", "curr", "current"):
                        ColorPrinter.cyan(str(dev.measure_current(channel)))
                    else:
                        ColorPrinter.warning("psu meas v|i <channel>")

            # MEAS_STORE COMMAND - unified for both single and multi-channel
            elif cmd_name == "meas_store":
                unit = ""
                if is_single_channel:
                    # Single-channel: psu meas_store v|i <label> [unit=]
                    if len(args) < 3:
                        ColorPrinter.warning("Usage: psu meas_store v|i <label> [unit=]")
                        return
                    mode = args[1].lower()
                    label = args[2]
                    for token in args[3:]:
                        if token.lower().startswith("unit="):
                            unit = token.split("=", 1)[1]
                    if mode in ("v", "volt", "voltage"):
                        value = dev.measure_voltage()
                        unit = unit or "V"
                    elif mode in ("i", "curr", "current"):
                        value = dev.measure_current()
                        unit = unit or "A"
                    else:
                        ColorPrinter.warning("psu meas_store v|i <label>")
                        return
                    self._record_measurement(label, value, unit, "psu.meas")
                    ColorPrinter.cyan(str(value))
                else:
                    # Multi-channel: psu meas_store v|i <channel> <label> [unit=]
                    if len(args) < 4:
                        ColorPrinter.warning("Usage: psu meas_store v|i <channel> <label> [unit=]")
                        return
                    mode = args[1].lower()
                    channel = PSU_CHANNEL_ALIASES.get(args[2].lower())
                    label = args[3]
                    for token in args[4:]:
                        token_lower = token.lower()
                        if token_lower.startswith("unit="):
                            unit = token.split("=", 1)[1]
                    if not channel:
                        ColorPrinter.warning("Invalid channel. Use 1, 2, or 3")
                        return
                    if mode in ("v", "volt", "voltage"):
                        value = dev.measure_voltage(channel)
                    elif mode in ("i", "curr", "current"):
                        value = dev.measure_current(channel)
                    else:
                        ColorPrinter.warning("psu meas_store v|i <channel> <label>")
                        return
                    self._record_measurement(label, value, unit, "psu.meas")
                    ColorPrinter.cyan(str(value))

            # GET COMMAND (single-channel only)
            elif cmd_name == "get":
                if is_single_channel:
                    v = dev.get_voltage_setpoint()
                    i = dev.get_current_limit()
                    out = "ON" if dev.get_output_state() else "OFF"
                    ColorPrinter.info(f"Setpoint: {v}V @ {i}A, Output: {out}")
                else:
                    ColorPrinter.warning("'get' command not available for multi-channel PSU")

            # TRACK COMMAND (multi-channel only)
            elif cmd_name == "track" and len(args) >= 2:
                if not is_single_channel:
                    dev.set_tracking(args[1].lower() == "on")
                else:
                    ColorPrinter.warning("'track' command not available for single-channel PSU")

            # SAVE/RECALL COMMANDS (multi-channel only)
            elif cmd_name == "save" and len(args) >= 2:
                if not is_single_channel:
                    dev.save_state(int(args[1]))
                else:
                    ColorPrinter.warning("'save' command not available for single-channel PSU")
            elif cmd_name == "recall" and len(args) >= 2:
                if not is_single_channel:
                    dev.recall_state(int(args[1]))
                else:
                    ColorPrinter.warning("'recall' command not available for single-channel PSU")

            # STATE COMMAND
            elif cmd_name == "state" and len(args) >= 2:
                self.do_state(f"{psu_name} {args[1]}")

            else:
                ColorPrinter.warning("Unknown PSU command. Type 'psu' for help.")

        except Exception as exc:
            ColorPrinter.error(str(exc))

    # --------------------------
    # AWG commands
    # --------------------------
    def do_awg(self, arg):
        "awg <cmd>: control the function generator (output, wave, freq, amp, etc.)"
        # Resolve which AWG/DDS to use (auto-select if only one)
        awg_name = self._resolve_device_type("awg")
        if not awg_name:
            return

        dev = self._get_device(awg_name)
        if not dev:
            return

        # Detect device type to route commands appropriately
        is_jds6600 = awg_name == 'dds' or 'JDS6600' in str(type(dev).__name__)

        args = self._parse_args(arg)
        args, help_flag = self._strip_help(args)

        if not args or help_flag:
            self._print_colored_usage(
                [
                    "# AWG COMMANDS (works with all AWG/DDS models)",
                    "",
                    "awg chan <1|2|all> on|off",
                    "awg wave <1|2|all> <type> [freq=] [amp=] [offset=] [duty=] [phase=]",
                    "  - type: sine|square|ramp|triangle|pulse|noise|dc|arb",
                    "  - example: awg wave 1 sine freq=1000 amp=5.0 offset=2.5",
                    "  - example: awg wave all sine freq=1000",
                    "",
                    "awg freq <1|2|all> <Hz>",
                    "awg amp <1|2|all> <Vpp>",
                    "awg offset <1|2|all> <V>",
                    "awg duty <1|2|all> <%>",
                    "awg phase <1|2|all> <deg>",
                    "",
                    "awg sync on|off",
                    "awg state on|off|safe|reset",
                ]
            )
            return

        cmd_name = args[0].lower()

        try:
            # CHAN COMMAND — enable/disable a channel output
            if cmd_name == "chan" and len(args) >= 3:
                channel_str = args[1].lower()
                state = args[2].lower() == "on"

                if channel_str in ("ch1", "1"):
                    channel = 1
                elif channel_str in ("ch2", "2"):
                    channel = 2
                else:
                    ColorPrinter.error("Channel must be '1', '2', 'ch1', or 'ch2'")
                    return

                if is_jds6600:
                    dev.enable_output(
                        ch1=state if channel == 1 else None,
                        ch2=state if channel == 2 else None,
                    )
                else:
                    dev.enable_output(channel, state)
                ColorPrinter.success(f"CH{channel}: {'on' if state else 'off'}")

            # WAVE COMMAND
            elif cmd_name == "wave" and len(args) >= 3:
                channel = int(args[1])
                waveform = args[2].lower()

                params = {}
                for token in args[3:]:
                    if "=" in token:
                        key, value = token.split("=", 1)
                        params[key.lower()] = float(value)

                if is_jds6600:
                    dev.set_waveform(channel, waveform)
                    if "freq" in params or "frequency" in params:
                        dev.set_frequency(channel, params.get("freq", params.get("frequency")))
                    if "amp" in params or "amplitude" in params:
                        dev.set_amplitude(channel, params.get("amp", params.get("amplitude")))
                    if "offset" in params:
                        dev.set_offset(channel, params["offset"])
                    if "duty" in params:
                        dev.set_duty_cycle(channel, params["duty"])
                    if "phase" in params:
                        dev.set_phase(channel, params["phase"])
                else:
                    # Normalize to SCPI abbreviations: "sine" → "SIN", "square" → "SQU", etc.
                    scpi_wave = AWG_WAVE_ALIASES.get(waveform, waveform.upper())
                    kwargs = {}
                    for key, value in params.items():
                        mapped_key = AWG_WAVE_KEYS.get(key)
                        if mapped_key:
                            kwargs[mapped_key] = value
                    dev.set_waveform(channel, scpi_wave, **kwargs)

                param_str = "  " + "  ".join(f"{k}={v}" for k, v in params.items()) if params else ""
                ColorPrinter.success(f"CH{channel}: {AWG_WAVE_ALIASES.get(waveform, waveform.upper())}{param_str}")

            # FREQ COMMAND
            elif cmd_name == "freq" and len(args) >= 3:
                channel = int(args[1])
                frequency = float(args[2])
                if is_jds6600:
                    dev.set_frequency(channel, frequency)
                elif hasattr(dev, 'set_frequency'):
                    dev.set_frequency(channel, frequency)
                else:
                    ColorPrinter.warning("Frequency not supported independently. Use 'awg wave' with freq=")
                    return
                ColorPrinter.success(f"CH{channel}: {frequency} Hz")

            # AMP COMMAND
            elif cmd_name == "amp" and len(args) >= 3:
                channel = int(args[1])
                amplitude = float(args[2])
                if is_jds6600:
                    dev.set_amplitude(channel, amplitude)
                elif hasattr(dev, 'set_amplitude'):
                    dev.set_amplitude(channel, amplitude)
                else:
                    ColorPrinter.warning("Amplitude not supported independently. Use 'awg wave' with amp=")
                    return
                ColorPrinter.success(f"CH{channel}: {amplitude} Vpp")

            # OFFSET COMMAND
            elif cmd_name == "offset" and len(args) >= 3:
                channel = int(args[1])
                offset = float(args[2])
                if is_jds6600:
                    dev.set_offset(channel, offset)
                elif hasattr(dev, 'set_offset'):
                    dev.set_offset(channel, offset)
                else:
                    ColorPrinter.warning("Offset not supported independently. Use 'awg wave' with offset=")
                    return
                ColorPrinter.success(f"CH{channel}: offset {offset} V")

            # DUTY COMMAND
            elif cmd_name == "duty" and len(args) >= 3:
                channel = int(args[1])
                duty = float(args[2])
                if is_jds6600:
                    dev.set_duty_cycle(channel, duty)
                elif hasattr(dev, 'set_duty_cycle'):
                    dev.set_duty_cycle(channel, duty)
                else:
                    ColorPrinter.warning("Duty cycle not supported independently. Use 'awg wave' with duty=")
                    return
                ColorPrinter.success(f"CH{channel}: duty {duty}%")

            # PHASE COMMAND
            elif cmd_name == "phase" and len(args) >= 3:
                channel = int(args[1])
                phase = float(args[2])
                if is_jds6600:
                    dev.set_phase(channel, phase)
                elif hasattr(dev, 'set_phase'):
                    dev.set_phase(channel, phase)
                else:
                    ColorPrinter.warning("Phase not supported independently. Use 'awg wave' with phase=")
                    return
                ColorPrinter.success(f"CH{channel}: phase {phase} deg")

            # SYNC COMMAND
            elif cmd_name == "sync" and len(args) >= 2:
                state = args[1].lower() == "on"
                if hasattr(dev, 'set_sync_output'):
                    dev.set_sync_output(state)
                    ColorPrinter.success(f"Sync: {'on' if state else 'off'}")
                else:
                    ColorPrinter.warning("Sync output not available on this device.")

            # STATE COMMAND
            elif cmd_name == "state" and len(args) >= 2:
                self.do_state(f"{awg_name} {args[1]}")

            else:
                ColorPrinter.warning("Unknown AWG command. Type 'awg' for help.")

        except ValueError as e:
            ColorPrinter.error(f"Invalid value: {e}")
        except Exception as exc:
            ColorPrinter.error(str(exc))

    # --------------------------
    # DMM commands
    # --------------------------
    def do_dmm(self, arg):
        "dmm <cmd>: control the multimeter (config, read, fetch, meas, beep, display)"
        # Resolve which DMM to use (auto-select if only one)
        dmm_name = self._resolve_device_type("dmm")
        if not dmm_name:
            return

        dev = self._get_device(dmm_name)
        if not dev:
            return

        # Use unified handler for all DMM types
        is_owon = dmm_name == "dmm_owon"
        return self._handle_dmm_unified(arg, dev, dmm_name, is_owon)

    def _handle_dmm_unified(self, arg, dev, dmm_name, is_owon):
        """Unified DMM command handler for all DMM types"""
        args = self._parse_args(arg)
        args, help_flag = self._strip_help(args)

        if not args:
            self._print_usage(
                [
                    "# UNIFIED DMM COMMANDS (works with all multimeter models)",
                    "",
                    "dmm config <vdc|vac|idc|iac|res|fres|freq|per|cont|diode|cap|temp> [range] [res] [nplc=]",
                    "  - range/res/nplc are optional (auto-configured if not specified)",
                    "  - nplc=0.02|0.2|1|10|100 (DC only, if supported)",
                    "  - example: dmm config vdc",
                    "  - example: dmm config vdc 10 0.001 nplc=10",
                    "",
                    "dmm read",
                    "dmm read_store <label> [scale=] [unit=]",
                    "dmm fetch",
                    "dmm meas <mode> [range] [res]",
                    "dmm beep",
                    "dmm display on|off",
                    "",
                    "# Advanced (HP DMM only):",
                    "dmm text <message> [scroll=auto|on|off] [delay=] [loops=] [pad=] [width=]",
                    "dmm ranges  # show valid ranges/res/nplc",
                    "dmm state safe|reset",
                ]
            )
            return

        cmd_name = args[0].lower()

        # Show ranges (HP DMM only)
        if cmd_name in ("ranges", "limits"):
            if not is_owon:
                self._print_usage(
                    [
                        "Valid DMM ranges/res/nplc (HP 34401A):",
                        "vdc: range 0.1|1|10|100|1000 or MIN/MAX/DEF/AUTO, res numeric, nplc 0.02|0.2|1|10|100",
                        "vac: range 0.1|1|10|100|750 or MIN/MAX/DEF/AUTO, res numeric",
                        "idc: range 0.01|0.1|1|3 or MIN/MAX/DEF/AUTO, res numeric, nplc 0.02|0.2|1|10|100",
                        "iac: range 0.01|0.1|1|3 or MIN/MAX/DEF/AUTO, res numeric",
                        "res/fres: range 100|1e3|10e3|100e3|1e6|10e6|100e6 or MIN/MAX/DEF/AUTO, res numeric",
                        "freq/per: range 0.1|1|10|100|750 or MIN/MAX/DEF/AUTO, res numeric",
                        "cont/diode: fixed range (no range/res args)",
                    ]
                )
            else:
                ColorPrinter.info("Owon DMM auto-configures ranges. No manual range specification needed.")
            return

        try:
            # CONFIG COMMAND - unified for both HP and Owon
            if cmd_name in ("config", "mode") and len(args) >= 2:
                mode_arg = args[1].lower()
                mode = DMM_MODE_ALIASES.get(mode_arg, mode_arg)

                if is_owon:
                    # Owon: Simple mode setting only
                    dev.set_mode(mode_arg)
                    ColorPrinter.success(f"Mode set to: {mode_arg}")
                else:
                    # HP: Support range/resolution/nplc parameters (optional)
                    if not mode or mode not in DMM_MODE_ALIASES.values():
                        # Try without alias
                        mode = mode_arg

                    func = getattr(dev, f"configure_{mode}", None)
                    if not func:
                        ColorPrinter.warning(f"Invalid mode '{mode_arg}'. Type 'dmm' for options.")
                        return

                    # Handle modes that don't take parameters
                    if mode in ("continuity", "diode"):
                        func()
                        ColorPrinter.success(f"Configured for {mode}")
                        return

                    # Parse optional parameters
                    range_val = "DEF"
                    resolution = "DEF"
                    nplc = None
                    positional = []

                    for token in args[2:]:
                        token_lower = token.lower()
                        if token_lower.startswith("nplc="):
                            nplc = float(token.split("=", 1)[1])
                        elif token_lower.startswith("range="):
                            range_val = token.split("=", 1)[1]
                        elif token_lower.startswith(("res=", "resolution=")):
                            resolution = token.split("=", 1)[1]
                        else:
                            positional.append(token)

                    if positional:
                        range_val = positional[0]
                    if len(positional) >= 2:
                        resolution = positional[1]

                    # Call configure function with appropriate parameters
                    if nplc is not None:
                        func(range_val, resolution, nplc)
                    else:
                        func(range_val, resolution)
                    ColorPrinter.success(f"Configured for {mode}")

            # READ COMMAND
            elif cmd_name == "read":
                ColorPrinter.cyan(str(dev.read()))

            # READ_STORE COMMAND
            elif cmd_name == "read_store" and len(args) >= 2:
                label = args[1]
                scale = 1.0
                unit = ""
                for token in args[2:]:
                    token_lower = token.lower()
                    if token_lower.startswith("scale="):
                        scale = float(token.split("=", 1)[1])
                    elif token_lower.startswith("unit="):
                        unit = token.split("=", 1)[1]
                value = dev.read()
                scaled = value * scale
                self._record_measurement(label, scaled, unit, "dmm.read")
                ColorPrinter.cyan(str(scaled))

            # FETCH COMMAND (HP only)
            elif cmd_name == "fetch":
                if hasattr(dev, 'fetch'):
                    ColorPrinter.cyan(str(dev.fetch()))
                else:
                    ColorPrinter.warning("'fetch' command not available on this DMM")

            # MEAS COMMAND
            elif cmd_name == "meas" and len(args) >= 2:
                mode_arg = args[1].lower()
                mode = DMM_MODE_ALIASES.get(mode_arg, mode_arg)

                if is_owon:
                    # Owon: Set mode then read
                    dev.set_mode(mode_arg)
                    ColorPrinter.cyan(str(dev.read()))
                else:
                    # HP: Use measure function
                    if not mode or mode not in DMM_MODE_ALIASES.values():
                        mode = mode_arg

                    func = getattr(dev, f"measure_{mode}", None)
                    if not func:
                        ColorPrinter.warning(f"Invalid mode '{mode_arg}'. Type 'dmm' for options.")
                        return

                    # Parse optional range/resolution parameters
                    range_val = args[2] if len(args) >= 3 else "DEF"
                    resolution = args[3] if len(args) >= 4 else "DEF"

                    if "continuity" in mode or "diode" in mode:
                        ColorPrinter.cyan(str(func()))
                    else:
                        ColorPrinter.cyan(str(func(range_val, resolution)))

            # BEEP COMMAND
            elif cmd_name == "beep":
                if hasattr(dev, 'beep'):
                    dev.beep()
                else:
                    ColorPrinter.warning("'beep' command not available on this DMM")

            # DISPLAY COMMAND
            elif cmd_name == "display" and len(args) >= 2:
                if hasattr(dev, 'set_display'):
                    dev.set_display(args[1].lower() == "on")
                else:
                    ColorPrinter.warning("'display' command not available on this DMM")

            # TEXT COMMAND (HP only)
            elif cmd_name == "text":
                if not is_owon and hasattr(dev, 'display_text'):
                    if len(args) < 2:
                        ColorPrinter.warning("Usage: dmm text <message> [scroll=] [delay=] [loops=] [pad=] [width=]")
                        return
                    msg_parts = []
                    options = {}
                    for token in args[1:]:
                        if "=" in token:
                            key, value = token.split("=", 1)
                            options[key.lower()] = value
                        else:
                            msg_parts.append(token)
                    message = " ".join(msg_parts)
                    scroll_mode = options.get("scroll", "auto").lower()
                    width = int(options.get("width", 12))
                    delay = float(options.get("delay", 0.2))
                    pad = int(options.get("pad", 4))
                    loops = int(options.get("loops", 1))
                    if scroll_mode == "off":
                        dev.display_text(message)
                    elif scroll_mode == "on":
                        dev.display_text_scroll(message, delay, pad, width, loops)
                    else:
                        if len(message) > width:
                            dev.display_text_scroll(message, delay, pad, width, loops)
                        else:
                            dev.display_text(message)
                else:
                    ColorPrinter.warning("'text' command not available on this DMM")

            # TEXT_LOOP COMMAND (HP only)
            elif cmd_name == "text_loop":
                if not is_owon:
                    if len(args) >= 2 and args[1].lower() == "off":
                        self._dmm_text_loop_active = False
                        if hasattr(dev, 'clear_display'):
                            dev.clear_display()
                        ColorPrinter.info("Text loop stopped")
                    elif len(args) >= 2:
                        msg_parts = []
                        options = {}
                        for token in args[1:]:
                            if "=" in token:
                                key, value = token.split("=", 1)
                                options[key.lower()] = value
                            else:
                                msg_parts.append(token)
                        message = " ".join(msg_parts)
                        delay = float(options.get("delay", 0.2))
                        pad = int(options.get("pad", 4))
                        width = int(options.get("width", 12))
                        # Generate scroll frames
                        padded = (" " * pad) + message + (" " * pad)
                        frames = [padded[i:i+width] for i in range(len(padded) - width + 1)]
                        self._dmm_text_frames = frames
                        self._dmm_text_index = 0
                        self._dmm_text_delay = delay
                        self._dmm_text_last = time.time()
                        self._dmm_text_loop_active = True
                        ColorPrinter.info(f"Text loop started: '{message}'")
                    else:
                        ColorPrinter.warning("Usage: dmm text_loop <message> [delay=] [pad=] [width=]")
                else:
                    ColorPrinter.warning("'text_loop' command not available on this DMM")

            # CLEARTEXT COMMAND (HP only)
            elif cmd_name == "cleartext":
                if not is_owon and hasattr(dev, 'clear_display'):
                    dev.clear_display()
                else:
                    ColorPrinter.warning("'cleartext' command not available on this DMM")

            # STATE COMMAND
            elif cmd_name == "state" and len(args) >= 2:
                self.do_state(f"{dmm_name} {args[1]}")

            else:
                ColorPrinter.warning("Unknown DMM command. Type 'dmm' for help.")

        except Exception as exc:
            ColorPrinter.error(str(exc))

    # --------------------------
    # Scope commands
    # --------------------------
    def do_scope(self, arg):
        "scope <cmd>: control the oscilloscope (autoset, run, stop, single, chan, coupling, probe, hscale, vscale, vpos, vmove, hpos, hmove, measure, save, trigger, awg)"
        # Resolve which scope to use (auto-select if only one)
        scope_name = self._resolve_device_type("scope")
        if not scope_name:
            return

        dev = self._get_device(scope_name)
        if not dev:
            return

        args = self._parse_args(arg)
        args, help_flag = self._strip_help(args)
        if not args:
            self._print_colored_usage(
                [
                    "# OSCILLOSCOPE COMMANDS",
                    "",
                    "scope autoset",
                    "scope run - start/resume continuous acquisition",
                    "scope stop - pause acquisition (freeze current display)",
                    "scope single - arm single-shot trigger (capture one event and stop)",
                    "",
                    "scope chan <1-4|all> on|off",
                    "scope coupling <1-4|all> <DC|AC|GND>",
                    "  - example: scope coupling 1 AC",
                    "  - example: scope coupling all DC",
                    "scope probe <1-4|all> <attenuation> - set probe attenuation (1, 10, 100, etc.)",
                    "  - example: scope probe 1 10",
                    "",
                    "scope hscale <seconds_per_div>",
                    "  - example: scope hscale 1e-3",
                    "scope hpos <percentage> - set horizontal position (0-100%)",
                    "scope hmove <delta> - move horizontal position by delta",
                    "",
                    "scope vscale <1-4|all> <volts_per_div> [pos]",
                    "  - example: scope vscale 1 0.5 0",
                    "  - example: scope vscale all 1.0",
                    "scope vpos <1-4|all> <divisions> - set vertical position",
                    "scope vmove <1-4|all> <delta> - move vertical position by delta",
                    "",
                    "scope trigger <chan> <level> [slope=RISE] [mode=AUTO]",
                    "",
                    "scope measure <1-4|all> <type> - measure waveform parameter",
                    "  - types: FREQUENCY, PK2PK, RMS, MEAN, PERIOD, MINIMUM, MAXIMUM",
                    "  - types: RISE, FALL, AMPLITUDE, HIGH, LOW, PWIDTH, NWIDTH, CRMS",
                    "  - example: scope measure 1 FREQUENCY",
                    "  - example: scope measure all PK2PK",
                    "scope measure_store <1-4|all> <type> <label> [unit=]",
                    "scope measure_delay <ch1> <ch2> [edge1=RISE] [edge2=RISE] [direction=FORWARDS]",
                    "scope measure_delay_store <ch1> <ch2> <label> [edge1=RISE] [edge2=RISE] [direction=FORWARDS] [unit=]",
                    "",
                    "scope save <channels> <filename> [record=<secs>] [time=<secs>] [points=<n>]",
                    "  - channels: single channel (1-4) or comma-separated list (1,3)",
                    "  - record=<secs>: WAIT and record for X seconds before saving",
                    "  - time=<secs>: filter to last X seconds of buffer (no waiting)",
                    "  - points=<n>: limit to specific number of points",
                    "  - example: scope save 1 ch1_data.csv",
                    "  - example: scope save 1,3 data.csv record=15  (wait 15s then save)",
                    "  - example: scope save 2 output.csv time=5 (filter to last 5s)",
                    "  - example: scope save 2 output.csv points=1000",
                    "",
                    "scope awg <subcmd> - built-in AWG control (type 'scope awg' for help)",
                    "scope counter <subcmd> - frequency counter (type 'scope counter' for help)",
                    "scope dvm <subcmd> - digital voltmeter (type 'scope dvm' for help)",
                    "scope state on|off|safe|reset",
                ]
            )
            return

        cmd_name = args[0].lower()
        if help_flag:
            self._print_usage(["scope ... (see main help)"])
            return
        try:
            if cmd_name == "autoset":
                dev.autoset()
                ColorPrinter.success("Autoset complete")
            elif cmd_name == "run":
                dev.run()
                ColorPrinter.success("Acquisition running")
            elif cmd_name == "stop":
                dev.stop()
                ColorPrinter.success("Acquisition stopped")
            elif cmd_name == "single":
                dev.single()
                ColorPrinter.success("Single shot armed")
            elif cmd_name == "chan" and len(args) >= 3:
                channel = int(args[1])
                enable = args[2].lower() == "on"
                if enable:
                    dev.enable_channel(channel)
                    ColorPrinter.success(f"CH{channel}: on")
                else:
                    dev.disable_channel(channel)
                    ColorPrinter.info(f"CH{channel}: off")
            elif cmd_name == "coupling" and len(args) >= 3:
                channel = int(args[1])
                coupling_type = args[2].upper()
                dev.set_coupling(channel, coupling_type)
                ColorPrinter.success(f"CH{channel}: coupling {coupling_type}")
            elif cmd_name == "probe" and len(args) >= 3:
                channel = int(args[1])
                attenuation = float(args[2])
                dev.set_probe_attenuation(channel, attenuation)
                ColorPrinter.success(f"CH{channel} probe attenuation set to {attenuation}x")
            elif cmd_name == "hscale" and len(args) >= 2:
                scale = float(args[1])
                dev.set_horizontal_scale(scale)
                ColorPrinter.success(f"Horizontal scale set to {scale} s/div")
            elif cmd_name == "hpos" and len(args) >= 2:
                position = float(args[1])
                dev.set_horizontal_position(position)
                ColorPrinter.success(f"Horizontal position set to {position}%")
            elif cmd_name == "hmove" and len(args) >= 2:
                delta = float(args[1])
                dev.move_horizontal(delta)
                ColorPrinter.success(f"Horizontal position moved by {delta}")
            elif cmd_name == "vscale" and len(args) >= 3:
                channel = int(args[1])
                scale = float(args[2])
                position = float(args[3]) if len(args) >= 4 else 0.0
                dev.set_vertical_scale(channel, scale, position)
                ColorPrinter.success(f"CH{channel} vertical scale set to {scale} V/div")
            elif cmd_name == "vpos" and len(args) >= 3:
                channel = int(args[1])
                position = float(args[2])
                dev.set_vertical_position(channel, position)
                ColorPrinter.success(f"CH{channel} vertical position set to {position} div")
            elif cmd_name == "vmove" and len(args) >= 3:
                channel = int(args[1])
                delta = float(args[2])
                dev.move_vertical(channel, delta)
                ColorPrinter.success(f"CH{channel}: moved {delta} div")
            elif cmd_name == "trigger" and len(args) >= 3:
                channel = int(args[1])
                level = float(args[2])
                slope = args[3].upper() if len(args) >= 4 else "RISE"
                mode = args[4].upper() if len(args) >= 5 else "AUTO"
                dev.configure_trigger(channel, level, slope, mode)
                ColorPrinter.success(f"Trigger configured: CH{channel} @ {level}V, {slope}, {mode}")
            elif cmd_name == "measure":
                if len(args) < 3:
                    # Show available measurement types
                    ColorPrinter.warning("Missing arguments. Usage: scope measure <1-4> <type>")
                    self._print_colored_usage([
                        "",
                        "# AVAILABLE MEASUREMENT TYPES",
                        "",
                        "  - FREQUENCY   - signal frequency (Hz)",
                        "  - PK2PK       - peak-to-peak voltage",
                        "  - RMS         - RMS voltage",
                        "  - CRMS        - cyclic RMS voltage",
                        "  - MEAN        - average voltage",
                        "  - PERIOD      - signal period",
                        "  - AMPLITUDE   - signal amplitude",
                        "  - MINIMUM     - minimum voltage",
                        "  - MAXIMUM     - maximum voltage",
                        "  - HIGH        - high state level",
                        "  - LOW         - low state level",
                        "  - RISE        - rise time",
                        "  - FALL        - fall time",
                        "  - PWIDTH      - positive pulse width",
                        "  - NWIDTH      - negative pulse width",
                        "",
                        "  - example: scope measure 1 FREQUENCY",
                        "  - example: scope measure 2 PK2PK",
                    ])
                else:
                    channel = int(args[1])
                    measure_type = args[2]
                    result = dev.measure_bnf(channel, measure_type)
                    ColorPrinter.cyan(f"CH{channel} {measure_type}: {result}")
            elif cmd_name == "measure_store" and len(args) >= 4:
                channel = int(args[1])
                measure_type = args[2]
                label = args[3]
                unit = ""
                for token in args[4:]:
                    if token.lower().startswith("unit="):
                        unit = token.split("=", 1)[1]
                val = dev.measure_bnf(channel, measure_type)
                self._record_measurement(label, val, unit, f"scope.meas.{measure_type}")
                ColorPrinter.success(f"CH{channel} {measure_type}: {val} → stored as '{label}'")
            elif cmd_name == "measure_delay" and len(args) >= 3:
                ch1 = int(args[1])
                ch2 = int(args[2])
                edge1 = args[3].upper() if len(args) >= 4 else "RISE"
                edge2 = args[4].upper() if len(args) >= 5 else "RISE"
                direction = args[5].upper() if len(args) >= 6 else "FORWARDS"
                ColorPrinter.cyan(str(dev.measure_delay(ch1, ch2, edge1, edge2, direction)))
            elif cmd_name == "measure_delay_store" and len(args) >= 4:
                ch1 = int(args[1])
                ch2 = int(args[2])
                label = args[3]
                edge1 = "RISE"
                edge2 = "RISE"
                direction = "FORWARDS"
                unit = "s"
                # Parse optional args
                # Expected order after label: [edge1] [edge2] [dir] [unit=]
                # But unit= can be anywhere
                optional_args = [a for a in args[4:] if not a.lower().startswith("unit=")]
                unit_args = [a for a in args[4:] if a.lower().startswith("unit=")]
                if unit_args:
                    unit = unit_args[0].split("=", 1)[1]

                if len(optional_args) >= 1: edge1 = optional_args[0].upper()
                if len(optional_args) >= 2: edge2 = optional_args[1].upper()
                if len(optional_args) >= 3: direction = optional_args[2].upper()

                val = dev.measure_delay(ch1, ch2, edge1, edge2, direction)
                self._record_measurement(label, val, unit, "scope.meas.delay")
                ColorPrinter.cyan(str(val))
            elif cmd_name == "save" and len(args) >= 3:
                channels_str = args[1]
                filename = args[2]

                # Parse optional parameters (time=X, points=N, record=X)
                max_points = None
                time_window = None
                record_duration = None
                for token in args[3:]:
                    if token.lower().startswith("time="):
                        time_window = float(token.split("=", 1)[1])
                    elif token.lower().startswith("points="):
                        max_points = int(token.split("=", 1)[1])
                    elif token.lower().startswith("record="):
                        record_duration = float(token.split("=", 1)[1])

                # If record= is specified, run scope and wait before saving
                if record_duration:
                    ColorPrinter.info(f"Recording for {record_duration} seconds...")
                    dev.run()  # Ensure scope is running
                    time.sleep(record_duration)  # Wait for the specified duration
                    ColorPrinter.success(f"Recording complete")

                # Parse channel list (supports single channel or comma-separated)
                if "," in channels_str:
                    # Multiple channels
                    channels = [int(ch.strip()) for ch in channels_str.split(",")]
                    dev.save_waveforms_csv(channels, filename, max_points=max_points, time_window=time_window)
                    channels_list = ",".join(str(ch) for ch in sorted(channels))
                    ColorPrinter.success(f"Waveforms from CH{channels_list} saved to {filename}")
                else:
                    # Single channel
                    channel = int(channels_str)
                    dev.save_waveform_csv(channel, filename, max_points=max_points, time_window=time_window)
                    ColorPrinter.success(f"Waveform from CH{channel} saved to {filename}")
            elif cmd_name == "awg":
                self._handle_scope_awg(dev, args[1:])
            elif cmd_name == "counter":
                self._handle_scope_counter(dev, args[1:])
            elif cmd_name == "dvm":
                self._handle_scope_dvm(dev, args[1:])
            elif cmd_name == "state" and len(args) >= 2:
                self.do_state(f"{scope_name} {args[1]}")
            else:
                ColorPrinter.warning("Unknown scope command. Type 'scope' for help.")
        except Exception as exc:
            ColorPrinter.error(str(exc))

    def _handle_scope_awg(self, dev, args):
        """Handle built-in oscilloscope AWG commands (DHO914S/DHO924S)"""
        if not args:
            self._print_colored_usage(
                [
                    "# BUILT-IN AWG CONTROL (DHO914S/DHO924S)",
                    "",
                    "scope awg output on|off - enable/disable AWG output",
                    "scope awg set <func> <freq> <amp> [offset=0] - quick config",
                    "  - func: SINusoid|SQUare|RAMP|DC|NOISe",
                    "  - freq: frequency in Hz",
                    "  - amp: amplitude in Vpp",
                    "  - example: scope awg set SINusoid 1000 2.0",
                    "",
                    "scope awg func <type> - set waveform function",
                    "scope awg freq <Hz> - set frequency",
                    "scope awg amp <Vpp> - set amplitude",
                    "scope awg offset <V> - set DC offset",
                    "scope awg phase <deg> - set phase (0-360)",
                    "scope awg duty <percent> - set square duty cycle",
                    "scope awg sym <percent> - set ramp symmetry",
                    "",
                    "scope awg mod on|off - enable/disable modulation",
                    "scope awg mod_type AM|FM|PM - set modulation type",
                ]
            )
            return

        try:
            cmd = args[0].lower()

            if cmd == "output" and len(args) >= 2:
                dev.awg_set_output_enable(args[1].lower() == "on")
                ColorPrinter.success(f"AWG output {'enabled' if args[1].lower() == 'on' else 'disabled'}")

            elif cmd == "set" and len(args) >= 4:
                # Quick configuration: scope awg set SINusoid 1000 2.0 [offset=0]
                function = args[1]
                frequency = float(args[2])
                amplitude = float(args[3])
                offset = 0.0
                for token in args[4:]:
                    if token.lower().startswith("offset="):
                        offset = float(token.split("=", 1)[1])
                dev.awg_configure_simple(function, frequency, amplitude, offset, enable=True)
                ColorPrinter.success(f"AWG configured: {function} {frequency}Hz {amplitude}Vpp offset={offset}V")

            elif cmd == "func" and len(args) >= 2:
                dev.awg_set_function(args[1])
                ColorPrinter.success(f"AWG function: {args[1]}")

            elif cmd == "freq" and len(args) >= 2:
                freq = float(args[1])
                dev.awg_set_frequency(freq)
                ColorPrinter.success(f"AWG frequency: {freq} Hz")

            elif cmd == "amp" and len(args) >= 2:
                amp = float(args[1])
                dev.awg_set_amplitude(amp)
                ColorPrinter.success(f"AWG amplitude: {amp} Vpp")

            elif cmd == "offset" and len(args) >= 2:
                offset = float(args[1])
                dev.awg_set_offset(offset)
                ColorPrinter.success(f"AWG offset: {offset} V")

            elif cmd == "phase" and len(args) >= 2:
                phase = float(args[1])
                dev.awg_set_phase(phase)
                ColorPrinter.success(f"AWG phase: {phase}°")

            elif cmd == "duty" and len(args) >= 2:
                duty = float(args[1])
                dev.awg_set_square_duty(duty)
                ColorPrinter.success(f"AWG square duty: {duty}%")

            elif cmd == "sym" and len(args) >= 2:
                sym = float(args[1])
                dev.awg_set_ramp_symmetry(sym)
                ColorPrinter.success(f"AWG ramp symmetry: {sym}%")

            elif cmd == "mod" and len(args) >= 2:
                dev.awg_set_modulation_enable(args[1].lower() == "on")
                ColorPrinter.success(f"AWG modulation {'enabled' if args[1].lower() == 'on' else 'disabled'}")

            elif cmd == "mod_type" and len(args) >= 2:
                mod_type = args[1].upper()
                dev.awg_set_modulation_type(mod_type)
                ColorPrinter.success(f"AWG modulation type: {mod_type}")

            else:
                ColorPrinter.warning("Unknown AWG command. Type 'scope awg' for help.")

        except AttributeError:
            ColorPrinter.warning("AWG not supported on this oscilloscope model (requires DHO914S/DHO924S)")
        except Exception as exc:
            ColorPrinter.error(str(exc))

    def _handle_scope_counter(self, dev, args):
        """Handle oscilloscope frequency counter commands"""
        if not args:
            self._print_colored_usage(
                [
                    "# FREQUENCY COUNTER",
                    "",
                    "scope counter on|off - enable/disable counter",
                    "scope counter read - read current frequency",
                    "scope counter source <1-4> - set source channel",
                    "scope counter mode <freq|period|totalize> - set mode",
                ]
            )
            return

        try:
            cmd = args[0].lower()

            if cmd in ("on", "off"):
                dev.set_counter_enable(cmd == "on")
                ColorPrinter.success(f"Counter {'enabled' if cmd == 'on' else 'disabled'}")

            elif cmd == "read":
                value = dev.get_counter_current()
                ColorPrinter.cyan(f"Counter: {value}")

            elif cmd == "source" and len(args) >= 2:
                channel = int(args[1])
                dev.set_counter_source(channel)
                ColorPrinter.success(f"Counter source: CH{channel}")

            elif cmd == "mode" and len(args) >= 2:
                mode = args[1].upper()
                dev.set_counter_mode(mode)
                ColorPrinter.success(f"Counter mode: {mode}")

            else:
                ColorPrinter.warning("Unknown counter command. Type 'scope counter' for help.")

        except AttributeError:
            ColorPrinter.warning("Counter not supported on this oscilloscope")
        except Exception as exc:
            ColorPrinter.error(str(exc))

    def _handle_scope_dvm(self, dev, args):
        """Handle oscilloscope digital voltmeter commands"""
        if not args:
            self._print_colored_usage(
                [
                    "# DIGITAL VOLTMETER",
                    "",
                    "scope dvm on|off - enable/disable DVM",
                    "scope dvm read - read current voltage",
                    "scope dvm source <1-4> - set source channel",
                ]
            )
            return

        try:
            cmd = args[0].lower()

            if cmd in ("on", "off"):
                dev.set_dvm_enable(cmd == "on")
                ColorPrinter.success(f"DVM {'enabled' if cmd == 'on' else 'disabled'}")

            elif cmd == "read":
                value = dev.get_dvm_current()
                ColorPrinter.cyan(f"DVM: {value} V")

            elif cmd == "source" and len(args) >= 2:
                channel = int(args[1])
                dev.set_dvm_source(channel)
                ColorPrinter.success(f"DVM source: CH{channel}")

            else:
                ColorPrinter.warning("Unknown DVM command. Type 'scope dvm' for help.")

        except AttributeError:
            ColorPrinter.warning("DVM not supported on this oscilloscope")
        except Exception as exc:
            ColorPrinter.error(str(exc))

    # --------------------------
    # Logging commands
    # --------------------------
    def do_log(self, arg):
        "log <print|save|clear>: show or save measurements"
        args = self._parse_args(arg)
        args, help_flag = self._strip_help(args)
        if help_flag or not args:
            self._print_usage(
                [
                    "log print",
                    "log save <path> [csv|txt]",
                    "log clear",
                ]
            )
            return
        cmd_name = args[0].lower()
        if cmd_name == "clear":
            self.measurements = []
            ColorPrinter.success("Cleared measurements.")
            return
        if cmd_name == "print":
            if not self.measurements:
                ColorPrinter.warning("No measurements recorded.")
                return
            header = f"{'Label':<24} {'Value':>14} {'Unit':<8} {'Source':<12}"
            print(header)
            print("-" * len(header))
            for entry in self.measurements:
                label = entry.get("label", "")
                value = entry.get("value", "")
                unit = entry.get("unit", "")
                source = entry.get("source", "")
                print(f"{label:<24} {value:>14} {unit:<8} {source:<12}")
            return
        if cmd_name == "save" and len(args) >= 2:
            path = args[1]
            fmt = args[2].lower() if len(args) >= 3 else ""
            if not fmt:
                _, ext = os.path.splitext(path)
                fmt = ext.lstrip(".").lower()
            if fmt not in ("csv", "txt"):
                ColorPrinter.warning("log save expects format csv or txt (or use .csv/.txt).")
                return
            if not self.measurements:
                ColorPrinter.warning("No measurements recorded.")
                return
            try:
                with open(path, "w", encoding="utf-8", newline="") as handle:
                    if fmt == "csv":
                        handle.write("label,value,unit,source\n")
                        for entry in self.measurements:
                            handle.write(
                                f"{entry.get('label','')},{entry.get('value','')},{entry.get('unit','')},{entry.get('source','')}\n"
                            )
                    else:
                        header = f"{'Label':<24} {'Value':>14} {'Unit':<8} {'Source':<12}"
                        handle.write(header + "\n")
                        handle.write("-" * len(header) + "\n")
                        for entry in self.measurements:
                            label = entry.get("label", "")
                            value = entry.get("value", "")
                            unit = entry.get("unit", "")
                            source = entry.get("source", "")
                            handle.write(f"{label:<24} {value:>14} {unit:<8} {source:<12}\n")
                ColorPrinter.success(f"Saved measurements to {path}.")
            except Exception as exc:
                ColorPrinter.error(f"Failed to save measurements: {exc}")
            return
        ColorPrinter.warning("Unknown log command. Use: log print|save|clear")

    def do_calc(self, arg):
        "calc <label> <expr> [unit=]: compute a value from logged measurements"
        args = self._parse_args(arg)
        args, help_flag = self._strip_help(args)
        if help_flag or len(args) < 2:
            self._print_usage(
                [
                    "calc <label> <expr> [unit=]",
                    "  - expr can use m[\"label\"], last, and variables like pi",
                    "  - functions: abs, min, max, round",
                    "  - example: calc ron_ohm m[\"vout_5_mV\"]/1000/m[\"psu_i_5_A\"] unit=ohm",
                ]
            )
            return
        label = args[0]
        unit = ""
        expr_parts = []
        for token in args[1:]:
            token_lower = token.lower()
            if token_lower.startswith("unit="):
                unit = token.split("=", 1)[1]
            else:
                expr_parts.append(token)
        expr = " ".join(expr_parts)
        if not expr:
            ColorPrinter.warning("calc expects an expression.")
            return
        if not self.measurements:
            ColorPrinter.warning("No measurements recorded. Use meas_store/read_store/measure_store first.")
            return
        m = {entry["label"]: entry["value"] for entry in self.measurements}
        last = self.measurements[-1]["value"]
        names = {"m": m, "last": last}
        try:
            value = self._safe_eval(expr, names)
            self._record_measurement(label, value, unit, "calc")
            ColorPrinter.cyan(str(value))
        except Exception as exc:
            ColorPrinter.error(f"calc failed: {exc}")

    # --------------------------
    def do_python(self, arg):
        "python <file.py>: execute external Python script with REPL context"
        args = self._parse_args(arg)
        args, help_flag = self._strip_help(args)

        if help_flag or not args:
            self._print_colored_usage(
                [
                    "# PYTHON SCRIPT EXECUTION",
                    "",
                    "python <file.py> - execute external Python script",
                    "  - The script has access to REPL context:",
                    "  - repl: the REPL instance",
                    "  - devices: dictionary of connected instruments",
                    "  - measurements: list of recorded measurements",
                    "  - ColorPrinter: for colored output",
                    "",
                    "  - example: python process_data.py",
                    "  - example: python analysis.py",
                ]
            )
            return

        filename = args[0]

        # Check if file exists
        if not os.path.exists(filename):
            ColorPrinter.error(f"File not found: {filename}")
            return

        # Read the file
        try:
            with open(filename, 'r') as f:
                script_code = f.read()
        except Exception as exc:
            ColorPrinter.error(f"Failed to read file: {exc}")
            return

        # Prepare execution context
        # Provide access to REPL, devices, measurements, and utilities
        exec_globals = {
            '__name__': '__main__',
            '__file__': filename,
            'repl': self,
            'devices': self.devices,
            'measurements': self.measurements,
            'ColorPrinter': ColorPrinter,
            # Common libraries that might be useful
            'os': os,
            'json': json,
            'time': time,
        }

        # Execute the script
        try:
            ColorPrinter.info(f"Executing {filename}...")
            exec(script_code, exec_globals)
            ColorPrinter.success(f"Script {filename} executed successfully")
        except Exception as exc:
            ColorPrinter.error(f"Script execution failed: {exc}")
            traceback.print_exc()


def main():
    args = sys.argv[1:]

    if "--mock" in args:
        args = [a for a in args if a != "--mock"]
        from lab_instruments import mock_instruments
        from lab_instruments.src import discovery as _disc
        _disc.InstrumentDiscovery.scan = lambda self, verbose=True: mock_instruments.get_mock_devices(verbose)

    repl = InstrumentRepl()

    if args:
        script_name = args[0]
        if script_name not in repl.scripts:
            ColorPrinter.error(f"Script '{script_name}' not found.")
            sys.exit(1)
        repl._run_script_lines(repl.scripts[script_name])
        return

    repl.cmdloop()


if __name__ == "__main__":
    main()
