"""Script line expansion: for, repeat, array, call, import, export, limits."""

import contextlib
import re
import shlex
from typing import Any

from lab_instruments.src.terminal import ColorPrinter

from ..syntax import safe_eval, substitute_expand

# Matches Python-style assignment: identifier = expression
# The (?!=) prevents matching lines like "print ============"
_ASSIGN_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_.]*)\s*=(?!=)\s*(.+)$")

# Matches instrument read RHS: <instrument> read [unit=X]
# Also matches ev2300 read_word/read_byte/read_block commands
_INSTR_READ_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s+(?:read|meas|read_word|read_byte|read_block)(?:\s+(.*))?$")


def expand_script_lines(
    lines: list[str],
    variables: dict[str, str],
    ctx: Any,
    depth: int = 0,
    parent_vars: dict[str, str] | None = None,
    exports: dict[str, str] | None = None,
    _loop_ctx: str = "",
) -> list[tuple[str, str]]:
    """Expand script lines into (command, source_display) tuples.

    Handles: import, export, breakpoint, set, call, repeat, array, for,
    lower_limit, upper_limit. Returns list of (cmd, source) where cmd may
    be '__NOP__' (metadata) or '__BREAKPOINT__'.
    """
    if depth > 10:
        ColorPrinter.error("Maximum script call depth (10) exceeded.")
        return []
    if depth == 0:
        ctx.safety_limits = {}
        ctx.awg_channel_state = {}
    expanded: list[tuple[str, str]] = []
    idx = 0
    while idx < len(lines):
        raw_line = lines[idx].strip()
        idx += 1
        if not raw_line or raw_line.startswith("#"):
            expanded.append(("__NOP__", _loop_ctx + raw_line))
            continue
        try:
            tokens = shlex.split(raw_line)
        except ValueError:
            tokens = raw_line.split()
        if not tokens:
            continue
        head = tokens[0].lower()

        if head == "import" and len(tokens) >= 2:
            for varname in tokens[1:]:
                if parent_vars is not None and varname in parent_vars:
                    variables[varname] = parent_vars[varname]
                else:
                    ctx.error(f"import: '{varname}' not found in parent scope")
            expanded.append(("__NOP__", _loop_ctx + raw_line))
            continue

        if head == "export" and len(tokens) >= 2:
            for varname in tokens[1:]:
                if varname in variables:
                    if exports is not None:
                        exports[varname] = variables[varname]
                else:
                    ctx.error(f"export: '{varname}' not set in this scope")
            expanded.append(("__NOP__", _loop_ctx + raw_line))
            continue

        if head == "breakpoint":
            expanded.append(("__BREAKPOINT__", "breakpoint"))
            continue

        if head == "set" and len(tokens) >= 2:
            if len(tokens) == 2 and tokens[1] in ("-e", "+e"):
                if tokens[1] == "-e":
                    ctx.exit_on_error = True
                    ColorPrinter.info("Exit on error enabled")
                else:
                    ctx.exit_on_error = False
                    ColorPrinter.info("Exit on error disabled")
                expanded.append(("__NOP__", _loop_ctx + raw_line))
                continue
            if len(tokens) >= 3:
                key = tokens[1]
                raw_val = substitute_expand(" ".join(tokens[2:]), variables)
                try:
                    num_vars = {}
                    for k, v in variables.items():
                        with contextlib.suppress(TypeError, ValueError):
                            num_vars[k] = float(v)
                    result = safe_eval(raw_val, num_vars)
                    variables[key] = str(result)
                except Exception:
                    variables[key] = raw_val
                expanded.append(("__NOP__", f"{_loop_ctx}{raw_line}  →  {key} = {variables[key]}"))
                continue

        if head == "call" and len(tokens) >= 2:
            script_name = tokens[1]
            if script_name not in ctx.scripts:
                ColorPrinter.error(f"call: script '{script_name}' not found.")
                continue
            call_params = {}
            for token in tokens[2:]:
                if "=" in token:
                    k, v = token.split("=", 1)
                    call_params[k] = substitute_expand(v, variables)
            call_exports: dict[str, str] = {}
            expanded.extend(
                expand_script_lines(
                    ctx.scripts[script_name],
                    call_params,
                    ctx,
                    depth + 1,
                    parent_vars=variables,
                    exports=call_exports,
                    _loop_ctx=f"[call {script_name}] " + _loop_ctx,
                )
            )
            variables.update(call_exports)
            continue

        if head == "repeat" and len(tokens) >= 2:
            try:
                count = int(tokens[1])
            except ValueError:
                ColorPrinter.error(f"repeat: expected integer count, got '{tokens[1]}'")
                continue
            block, idx = _collect_block(lines, idx)
            for i in range(count):
                iter_ctx = f"[repeat {i + 1}/{count}] "
                expanded.append(("__NOP__", f"{_loop_ctx}{raw_line}  →  iteration {i + 1}/{count}"))
                expanded.extend(expand_script_lines(block, dict(variables), ctx, depth, _loop_ctx=_loop_ctx + iter_ctx))
            continue

        if head == "array" and len(tokens) >= 2:
            varname = tokens[1]
            elements: list[str] = []
            while idx < len(lines):
                line = lines[idx].strip()
                idx += 1
                if not line or line.startswith("#"):
                    continue
                inner_tokens = shlex.split(line)
                if not inner_tokens:
                    continue
                if inner_tokens[0].lower() == "end":
                    break
                elements.extend(shlex.split(substitute_expand(line, variables)))
            variables[varname] = " ".join(elements)
            expanded.append(("__NOP__", f"{_loop_ctx}{raw_line}  →  {varname} = [{variables[varname]}]"))
            continue

        if head == "for" and len(tokens) >= 3:
            key = tokens[1]
            values: list[str] = []
            for _rv in tokens[2:]:
                _subst = substitute_expand(_rv, variables)
                try:
                    values.extend(shlex.split(_subst))
                except ValueError:
                    values.append(_subst)
            block, idx = _collect_block(lines, idx)
            if "," in key:
                keys = [name for name in key.split(",") if name]
                for value in values:
                    parts = value.split(",")
                    if len(parts) != len(keys):
                        ColorPrinter.error("for: var list and value list length mismatch.")
                        break
                    local_vars = dict(variables)
                    for name, val in zip(keys, parts, strict=True):
                        local_vars[name] = substitute_expand(val, variables)
                    iter_ctx = " ".join(f"{k}={v}" for k, v in zip(keys, parts, strict=True))
                    expanded.append(("__NOP__", f"{_loop_ctx}{raw_line}  →  {iter_ctx}"))
                    expanded.extend(
                        expand_script_lines(block, local_vars, ctx, depth, _loop_ctx=_loop_ctx + f"[{iter_ctx}] ")
                    )
            else:
                for value in values:
                    local_vars = dict(variables)
                    local_vars[key] = substitute_expand(value, variables)
                    expanded.append(("__NOP__", f"{_loop_ctx}{raw_line}  →  {key}={value}"))
                    expanded.extend(
                        expand_script_lines(block, local_vars, ctx, depth, _loop_ctx=_loop_ctx + f"[{key}={value}] ")
                    )
            continue

        if head == "end":
            expanded.append(("__NOP__", _loop_ctx + raw_line))
            continue

        # Runtime-evaluated blocks: while, if/elif/else, assert, break, continue
        # These must pass through the expander untouched so the shell can
        # evaluate conditions with live variable values at runtime.
        if head in ("while", "if"):
            block, idx = _collect_block(lines, idx)
            # Emit variable sync commands so runtime has access to
            # variables that were set during expansion (before this block).
            for vk, vv in variables.items():
                expanded.append((f"{vk} = {vv}", f"{_loop_ctx}[sync] {vk} = {vv}"))
            # Emit header, body, and closing 'end' as raw commands
            expanded.append((raw_line, _loop_ctx + raw_line))
            for bline in block:
                expanded.append((bline, _loop_ctx + bline))
            expanded.append(("end", _loop_ctx + "end"))
            continue

        if head in ("elif", "else"):
            # These are only reached inside an if-block being passed through
            expanded.append((raw_line, _loop_ctx + raw_line))
            continue

        if head in ("assert", "break", "continue"):
            # Emit variable sync so assert can access expander-time variables
            for vk, vv in variables.items():
                expanded.append((f"{vk} = {vv}", f"{_loop_ctx}[sync] {vk} = {vv}"))
            expanded.append((raw_line, _loop_ctx + raw_line))
            continue

        if head in ("lower_limit", "upper_limit") and len(tokens) >= 3:
            _parse_limit(head, tokens, ctx, expanded, _loop_ctx, raw_line)
            continue

        # Python-style assignment: identifier = expression
        _assign_match = _ASSIGN_RE.match(raw_line)
        if _assign_match:
            key = _assign_match.group(1)
            raw_val = substitute_expand(_assign_match.group(2).strip(), variables)
            # Instrument read assignment: value = dmm read [unit=X]
            # Emit the full line as a command so the shell handles it at runtime
            instr_read_match = _INSTR_READ_RE.match(raw_val)
            if instr_read_match:
                expanded.append((raw_line, _loop_ctx + raw_line))
                continue
            # input assignment: VAR = input [prompt]
            # Must run at runtime (user interaction), so emit as command
            inp_parts = raw_val.split(None, 1)
            if inp_parts and inp_parts[0] == "input":
                expanded.append((raw_line, _loop_ctx + raw_line))
                continue
            # linspace assignment: VAR = linspace start stop [count]
            ls_parts = raw_val.split()
            if ls_parts and ls_parts[0] == "linspace" and len(ls_parts) >= 3:
                try:
                    ls_start = float(ls_parts[1])
                    ls_stop = float(ls_parts[2])
                    ls_count = int(ls_parts[3]) if len(ls_parts) >= 4 else 11
                    if ls_count < 2:
                        raise ValueError("count must be >= 2")
                    ls_step = (ls_stop - ls_start) / (ls_count - 1)
                    ls_vals = [ls_start + i * ls_step for i in range(ls_count)]
                    variables[key] = " ".join(f"{v:g}" for v in ls_vals)
                    expanded.append(("__NOP__", f"{_loop_ctx}{raw_line}  →  {key} = [{variables[key]}]"))
                except (ValueError, ZeroDivisionError) as exc:
                    ColorPrinter.error(f"linspace: {exc}")
                continue
            try:
                num_vars = {}
                for k, v in variables.items():
                    with contextlib.suppress(TypeError, ValueError):
                        num_vars[k] = float(v)
                result = safe_eval(raw_val, num_vars)
                variables[key] = str(result)
            except Exception:
                variables[key] = raw_val
            expanded.append(("__NOP__", f"{_loop_ctx}{raw_line}  →  {key} = {variables[key]}"))
            continue

        expanded.append((substitute_expand(raw_line, variables), _loop_ctx + raw_line))
    return expanded


def _collect_block(lines: list[str], idx: int) -> tuple[list[str], int]:
    """Collect lines until a matching 'end', tracking nested depth."""
    block: list[str] = []
    depth_inner = 1
    while idx < len(lines):
        line = lines[idx].strip()
        idx += 1
        if not line or line.startswith("#"):
            continue
        try:
            line_tokens = shlex.split(line)
        except ValueError:
            line_tokens = line.split()
        if not line_tokens:
            continue
        if line_tokens[0].lower() in ("repeat", "for", "array", "while", "if"):
            depth_inner += 1
        elif line_tokens[0].lower() == "end":
            depth_inner -= 1
            if depth_inner == 0:
                break
        block.append(line)
    return block, idx


def _parse_limit(
    head: str,
    tokens: list[str],
    ctx: Any,
    expanded: list[tuple[str, str]],
    _loop_ctx: str,
    raw_line: str,
) -> None:
    """Parse and store a lower_limit/upper_limit directive."""
    direction = "lower" if head == "lower_limit" else "upper"
    device_str = tokens[1].lower()
    base_type = re.sub(r"\d+$", "", device_str)
    VALID_PARAMS = {
        "awg": {"vpeak", "vtrough", "vpp", "freq", "voltage"},
        "psu": {"voltage", "current"},
        "smu": {"voltage", "current"},
    }
    if base_type not in VALID_PARAMS:
        ctx.error(f"{head}: unknown device type '{device_str}'")
        expanded.append(("__NOP__", _loop_ctx + raw_line))
        return
    channel_or_none = None
    rest = tokens[2:]
    if rest and rest[0].lower() == "chan":
        if len(rest) < 4:
            ctx.error(f"{head}: 'chan' requires a channel number, param, and value")
            expanded.append(("__NOP__", _loop_ctx + raw_line))
            return
        try:
            channel_or_none = int(rest[1])
        except ValueError:
            ctx.error(f"{head}: invalid channel number '{rest[1]}'")
            expanded.append(("__NOP__", _loop_ctx + raw_line))
            return
        rest = rest[2:]
    if len(rest) == 1:
        try:
            float(rest[0])
            rest = ["voltage", rest[0]]
        except ValueError:
            pass
    if len(rest) < 2:
        ctx.error(f"{head}: requires <param> <value>  (e.g. {head} {device_str} voltage 5.0)")
        expanded.append(("__NOP__", _loop_ctx + raw_line))
        return
    param = rest[0].lower()
    try:
        value = float(rest[1])
    except ValueError:
        ctx.error(f"{head}: '{rest[1]}' is not a number")
        expanded.append(("__NOP__", _loop_ctx + raw_line))
        return
    if param not in VALID_PARAMS[base_type]:
        ctx.error(f"{head}: unknown param '{param}' for '{base_type}'")
        expanded.append(("__NOP__", _loop_ctx + raw_line))
        return
    if base_type == "awg" and param == "voltage":
        param = "vpeak" if direction == "upper" else "vtrough"
    key = (device_str, channel_or_none)
    ctx.safety_limits.setdefault(key, {})[f"{param}_{direction}"] = value
    expanded.append(("__NOP__", f"{_loop_ctx}{raw_line}  →  limit set"))
