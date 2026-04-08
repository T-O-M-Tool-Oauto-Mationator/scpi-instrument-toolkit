"""Script execution and interactive debugger."""

import contextlib
from typing import Any

from lab_instruments.src.terminal import ColorPrinter


class _BreakSignal(Exception):
    """Raised by `break` to exit the innermost while/for loop."""


class _ContinueSignal(Exception):
    """Raised by `continue` to skip to the next loop iteration."""


class _AssertFailure(Exception):
    """Raised by `assert` when the condition is False — stops the script."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def _is_numeric(v: str) -> bool:
    try:
        float(v)
        return True
    except (TypeError, ValueError):
        return False


def _run_block(items: list, shell: Any, ctx: Any, debug: bool) -> None:
    """Execute an already-expanded item list.

    Raises _BreakSignal or _ContinueSignal if the block body emits them.
    """
    for item in items:
        _dispatch_item(item, shell, ctx, debug)


def _dispatch_item(item: tuple, shell: Any, ctx: Any, debug: bool) -> bool:
    """Dispatch a single expanded item.  Returns True if the script should exit."""
    if isinstance(item, tuple) and len(item) >= 1:
        tag = item[0]
        # break/continue are 2-tuples: (__BREAK__, src) / (__CONTINUE__, src)
        if tag == "__BREAK__":
            raise _BreakSignal()
        if tag == "__CONTINUE__":
            raise _ContinueSignal()
        # while/if are larger block-structure tuples (>= 3 elements)
        if len(item) >= 3:
            if tag == "__WHILE__":
                _, _src, condition, block_lines, var_snap = item
                _run_while(shell, ctx, condition, block_lines, var_snap, debug)
                return False
            if tag == "__IF__":
                _, _src, branches, else_block = item[:4]
                var_snap = item[4] if len(item) >= 5 else {}
                _run_if(shell, ctx, branches, else_block, debug, var_snap)
                return False

    # Regular 2-tuple: (cmd, source)
    cmd, _src = item if isinstance(item, tuple) and len(item) >= 2 else (item, item)
    cmd = str(cmd).strip()

    if not cmd or cmd.startswith("#") or cmd == "__NOP__":
        return False

    ctx.command_had_error = False
    try:
        if shell.onecmd(cmd):
            return True
    except _BreakSignal:
        raise
    except _ContinueSignal:
        raise
    except _AssertFailure:
        raise
    except KeyboardInterrupt:
        raise

    if ctx.exit_on_error and ctx.command_had_error:
        ColorPrinter.error("Script stopped (set -e)")
        return True
    return False


def _run_while(
    shell: Any,
    ctx: Any,
    condition: str,
    block_lines: list[str],
    var_snap: dict[str, str],
    debug: bool,
) -> None:
    """Execute a while loop at runtime."""
    import re as _re

    from .expander import expand_script_lines
    from ..syntax import safe_eval_bool

    _KEY_RE = _re.compile(r"^([A-Za-z_][A-Za-z0-9_.]*)\s*=")

    # Seed ctx.script_vars with compile-time snapshot for any variables
    # that were set before the while loop as compile-time NOPs
    for k, v in var_snap.items():
        if k not in ctx.script_vars:
            ctx.script_vars[k] = v

    MAX_ITER = 100_000
    for _iteration in range(MAX_ITER):
        # Evaluate condition: numeric vars as floats, string vars as strings
        num_vars: dict = {}
        for k, v in ctx.script_vars.items():
            try:
                num_vars[k] = float(v)
            except (TypeError, ValueError):
                num_vars[k] = v
        try:
            if not safe_eval_bool(condition, num_vars):
                break
        except Exception:
            break

        # Expand body with current ctx.script_vars so {var} substitution
        # and inc/compound ops use the latest values
        iter_vars = dict(ctx.script_vars)
        sub_expanded = expand_script_lines(block_lines, iter_vars, ctx)

        # Variables managed by runtime commands (x++, count+=1, etc.) update
        # ctx.script_vars themselves when the command executes.  Only NOP-only
        # variables (pure static assignments like y = x * 2 that emit no runtime
        # command) need to be pre-seeded so that {y} interpolation works inside
        # the body.  Pre-syncing runtime-cmd vars is harmful when continue/break
        # would skip the command — the pre-sync value would persist incorrectly.
        runtime_keys: set[str] = set()
        for _item in sub_expanded:
            if not isinstance(_item, tuple) or len(_item) < 1:
                continue
            _cmd = str(_item[0]).strip()
            if not _cmd or _cmd.startswith("#") or _cmd.startswith("__"):
                continue
            _m = _KEY_RE.match(_cmd)
            if _m:
                runtime_keys.add(_m.group(1))

        # Pre-sync only NOP variables
        for k, v in iter_vars.items():
            if k not in runtime_keys:
                ctx.script_vars[k] = v

        try:
            _run_block(sub_expanded, shell, ctx, debug)
        except _BreakSignal:
            break
        except _ContinueSignal:
            continue
        if ctx.exit_on_error and ctx.command_had_error:
            break


def _run_if(
    shell: Any,
    ctx: Any,
    branches: list[tuple[str, list[str]]],
    else_block: list[str],
    debug: bool,
    var_snap: dict[str, str] | None = None,
) -> None:
    """Execute an if/elif/else chain at runtime."""
    from .expander import expand_script_lines
    from ..syntax import safe_eval_bool

    # Seed ctx.script_vars from compile-time snapshot for NOP variables
    # (e.g. x = 5 before an if statement — x is a NOP and not in ctx.script_vars)
    if var_snap:
        for k, v in var_snap.items():
            if k not in ctx.script_vars:
                ctx.script_vars[k] = v

    # Build names: numeric vars as floats, string vars as strings (for x == "ok" comparisons)
    num_vars: dict = {}
    for k, v in ctx.script_vars.items():
        try:
            num_vars[k] = float(v)
        except (TypeError, ValueError):
            num_vars[k] = v

    for condition, block_lines in branches:
        try:
            result = safe_eval_bool(condition, num_vars)
        except Exception:
            result = False
        if result:
            iter_vars = dict(ctx.script_vars)
            sub_expanded = expand_script_lines(block_lines, iter_vars, ctx)
            for k, v in iter_vars.items():
                ctx.script_vars[k] = v
            _run_block(sub_expanded, shell, ctx, debug)
            return

    # else block
    if else_block:
        iter_vars = dict(ctx.script_vars)
        sub_expanded = expand_script_lines(else_block, iter_vars, ctx)
        for k, v in iter_vars.items():
            ctx.script_vars[k] = v
        _run_block(sub_expanded, shell, ctx, debug)


def run_expanded(expanded: list[tuple], shell: Any, ctx: Any, debug: bool = False) -> bool:
    """Execute a pre-expanded command list, optionally with an interactive debugger.

    Returns True if the script requests REPL exit.
    """
    # Separate flat commands from block-structure tuples for the debugger.
    # Block tuples (while/if) are kept inline but shown as single debug steps.
    lines = []
    source_lines = []
    breakpoints: set[int] = set()
    for item in expanded:
        tag = item[0] if isinstance(item, tuple) and len(item) >= 1 else None
        if tag == "__BREAKPOINT__":
            breakpoints.add(len(lines) + 1)
            continue
        if tag == "__NOP__":
            src = item[1] if len(item) >= 2 else ""
            lines.append(item)
            source_lines.append(str(src).strip())
            continue
        if isinstance(item, tuple) and len(item) >= 1:
            cmd = item[0]
            src = item[1] if len(item) >= 2 else cmd
            if not str(cmd).strip() or str(cmd).startswith("#"):
                continue
            lines.append(item)
            source_lines.append(str(src).strip())
        elif not isinstance(item, tuple):
            # Non-tuple raw string items — wrap for uniform dispatch
            cmd_str = str(item).strip()
            if not cmd_str or cmd_str.startswith("#"):
                continue
            if cmd_str == "__BREAKPOINT__":
                breakpoints.add(len(lines) + 1)
                continue
            lines.append((cmd_str, cmd_str))
            source_lines.append(cmd_str)

    if not lines:
        return False

    idx = 0
    debug_active = debug
    ctx.in_script = True
    ctx.in_debugger = debug
    ctx.interrupt_requested = False

    try:
        while idx < len(lines):
            item = lines[idx]
            tag = item[0] if isinstance(item, tuple) and len(item) >= 1 else None

            if (idx + 1) in breakpoints and not debug_active:
                ColorPrinter.info(f"Breakpoint at line {idx + 1}")
                debug_active = True
                ctx.in_debugger = True

            if debug_active:
                _debug_show_context(lines, source_lines, idx, breakpoints)
                while True:
                    try:
                        cmd_input = input("(dbg) ").strip()
                    except KeyboardInterrupt:
                        print()
                        continue
                    except EOFError:
                        ColorPrinter.warning("Debugger aborted")
                        return True

                    if cmd_input in ("", "n", "next", "s", "step"):
                        if tag == "__NOP__":
                            idx += 1
                            break
                        ctx.command_had_error = False
                        try:
                            result = _dispatch_item(item, shell, ctx, debug_active)
                            if result:
                                return True
                        except (_BreakSignal, _ContinueSignal, _AssertFailure) as exc:
                            if isinstance(exc, _AssertFailure):
                                ColorPrinter.error(f"Script aborted: {exc.message}")
                                ctx.command_had_error = True
                                return False
                            ColorPrinter.warning(f"{type(exc).__name__} outside loop — ignored in debugger")
                        except KeyboardInterrupt:
                            print()
                            ColorPrinter.warning(
                                "Command interrupted — staying at line (retry with Enter or skip with goto)"
                            )
                            break
                        if ctx.exit_on_error and ctx.command_had_error:
                            ColorPrinter.error("Script stopped (set -e)")
                            return True
                        idx += 1
                        break

                    elif cmd_input in ("c", "continue"):
                        if tag == "__NOP__":
                            debug_active = False
                            ctx.in_debugger = False
                            idx += 1
                            break
                        debug_active = False
                        ctx.in_debugger = False
                        ctx.command_had_error = False
                        try:
                            result = _dispatch_item(item, shell, ctx, False)
                            if result:
                                return True
                        except (_BreakSignal, _ContinueSignal, _AssertFailure) as exc:
                            if isinstance(exc, _AssertFailure):
                                ColorPrinter.error(f"Script aborted: {exc.message}")
                                ctx.command_had_error = True
                                return False
                            ColorPrinter.warning(f"{type(exc).__name__} outside loop — ignored in debugger")
                        except KeyboardInterrupt:
                            print()
                            ColorPrinter.warning("Command interrupted — re-entering debugger")
                            debug_active = True
                            ctx.in_debugger = True
                            break
                        if ctx.exit_on_error and ctx.command_had_error:
                            ColorPrinter.error("Script stopped (set -e)")
                            return True
                        idx += 1
                        break

                    elif cmd_input in ("back", "prev"):
                        if idx > 0:
                            idx -= 1
                            ColorPrinter.warning("Moved back — instrument state NOT reversed")
                            _debug_show_context(lines, source_lines, idx, breakpoints)
                        else:
                            ColorPrinter.warning("Already at first line")

                    elif cmd_input.startswith(("goto ", "jump ")):
                        parts = cmd_input.split()
                        try:
                            target = int(parts[1]) - 1
                            if 0 <= target < len(lines):
                                idx = target
                                ColorPrinter.warning(f"Jumped to line {idx + 1} — skipped lines NOT executed/reversed")
                                _debug_show_context(lines, source_lines, idx, breakpoints)
                            else:
                                ColorPrinter.error(f"Line out of range (1–{len(lines)})")
                        except (ValueError, IndexError):
                            ColorPrinter.error("Usage: goto <N>")

                    elif cmd_input.split()[:1] in (["b"], ["break"]):
                        parts = cmd_input.split()
                        try:
                            n = int(parts[1])
                            if 1 <= n <= len(lines):
                                breakpoints.add(n)
                                src_display = source_lines[n - 1] if source_lines else str(lines[n - 1])
                                ColorPrinter.info(f"Breakpoint set at line {n}: {src_display}")
                            else:
                                ColorPrinter.error(f"Line out of range (1–{len(lines)})")
                        except (ValueError, IndexError):
                            ColorPrinter.error("Usage: b <N>")

                    elif cmd_input.split()[:1] in (["d"], ["delete"], ["clear"]):
                        parts = cmd_input.split()
                        try:
                            n = int(parts[1])
                            if n in breakpoints:
                                breakpoints.discard(n)
                                ColorPrinter.info(f"Breakpoint {n} cleared")
                            else:
                                ColorPrinter.warning(f"No breakpoint at line {n}")
                        except (ValueError, IndexError):
                            ColorPrinter.error("Usage: d <N>")

                    elif cmd_input == "l" or cmd_input == "list" or cmd_input.startswith("l ") or cmd_input.startswith("list "):
                        parts = cmd_input.split(None, 1)
                        arg = parts[1] if len(parts) > 1 else ""
                        if arg.lower() == "all":
                            _debug_show_context(lines, source_lines, idx, breakpoints, show_all=True)
                        elif arg:
                            try:
                                _debug_show_context(lines, source_lines, idx, breakpoints, window=int(arg))
                            except ValueError:
                                ColorPrinter.error("Usage: l [N|all]")
                        else:
                            _debug_show_context(lines, source_lines, idx, breakpoints, window=8)

                    elif cmd_input in ("info", "i", "?"):
                        ColorPrinter.info(f"Position: line {idx + 1}/{len(lines)}")
                        if breakpoints:
                            ColorPrinter.info(f"Breakpoints: {sorted(breakpoints)}")
                        else:
                            ColorPrinter.info("No breakpoints set")

                    elif cmd_input in ("q", "quit", "abort"):
                        ColorPrinter.warning("Script aborted")
                        return True

                    elif cmd_input:
                        shell.onecmd(cmd_input)
            else:
                # Non-debug execution
                if tag == "__NOP__":
                    idx += 1
                    continue
                ctx.command_had_error = False
                try:
                    result = _dispatch_item(item, shell, ctx, False)
                    if result:
                        return True
                except _AssertFailure as exc:
                    ColorPrinter.error(f"Script aborted: {exc.message}")
                    ctx.command_had_error = True
                    return False
                except _BreakSignal:
                    ColorPrinter.warning("break outside loop — ignored")
                except _ContinueSignal:
                    ColorPrinter.warning("continue outside loop — ignored")
                except KeyboardInterrupt:
                    print()
                    ColorPrinter.warning("Command interrupted — re-entering debugger")
                    debug_active = True
                    ctx.in_debugger = True
                    continue
                if ctx.exit_on_error and ctx.command_had_error:
                    ColorPrinter.error("Script stopped (set -e)")
                    return True
                idx += 1

    except KeyboardInterrupt:
        ColorPrinter.warning("Script interrupted")
    finally:
        ctx.in_script = False
        ctx.in_debugger = False
        ctx.interrupt_requested = False

    return False


def _debug_show_context(
    lines: list,
    source_lines: list,
    idx: int,
    breakpoints: set[int],
    window: int = 3,
    show_all: bool = False,
) -> None:
    """Print lines around the current position for the script debugger."""
    total = len(lines)
    start = 0 if show_all else max(0, idx - window)
    end = total if show_all else min(total, idx + window + 1)
    print()
    print("  " + "─" * 60)
    for i in range(start, end):
        bp = "●" if (i + 1) in breakpoints else " "
        src = source_lines[i] if source_lines else str(lines[i])
        # For block tuples, show a representative string
        raw_item = lines[i]
        if isinstance(raw_item, tuple) and len(raw_item) >= 3:
            raw_str = src  # source display is enough
        else:
            raw_str = raw_item[0] if isinstance(raw_item, tuple) else str(raw_item)
        if i == idx:
            print(f"\033[96m  {bp} {i + 1:>4} → {src}\033[0m")
            if isinstance(raw_str, str) and raw_str != src:
                print(f"\033[90m         ↳ {raw_str}\033[0m")
        else:
            print(f"  {bp} {i + 1:>4}   {src}")
    print("  " + "─" * 60)
    print(f"  {idx + 1}/{total}  │  n=step  c=continue  back  goto N  b N=break  d N=del  l [N|all]=list  q=quit")
    print()
