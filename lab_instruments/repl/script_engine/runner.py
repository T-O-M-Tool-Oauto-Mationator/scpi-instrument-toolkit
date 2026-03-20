"""Script execution and interactive debugger."""

from typing import Any, List, Set, Tuple

from lab_instruments.src.terminal import ColorPrinter


def run_expanded(expanded: List[Tuple[str, str]], shell: Any, ctx: Any, debug: bool = False) -> bool:
    """Execute a pre-expanded command list, optionally with an interactive debugger.

    Returns True if the script requests REPL exit.
    """
    lines = []
    source_lines = []
    breakpoints: Set[int] = set()
    for item in expanded:
        cmd, src = item if isinstance(item, tuple) else (item, item)
        cmd = cmd.strip()
        if not cmd or cmd.startswith("#"):
            continue
        if cmd == "__BREAKPOINT__":
            breakpoints.add(len(lines) + 1)
            continue
        lines.append(cmd)
        source_lines.append(src.strip())

    if not lines:
        return False

    idx = 0
    debug_active = debug
    ctx.in_script = True
    ctx.in_debugger = debug
    ctx.interrupt_requested = False

    try:
        while idx < len(lines):
            line = lines[idx]

            if (idx + 1) in breakpoints and not debug_active:
                ColorPrinter.info(f"Breakpoint at line {idx + 1}")
                debug_active = True
                ctx.in_debugger = True

            if debug_active:
                _debug_show_context(lines, source_lines, idx, breakpoints)
                while True:
                    try:
                        cmd = input("(dbg) ").strip()
                    except KeyboardInterrupt:
                        print()
                        continue
                    except EOFError:
                        ColorPrinter.warning("Debugger aborted")
                        return True

                    if cmd in ("", "n", "next", "s", "step"):
                        if line == "__NOP__":
                            idx += 1
                            break
                        ctx.command_had_error = False
                        try:
                            if shell.onecmd(line):
                                return True
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

                    elif cmd in ("c", "continue"):
                        if line == "__NOP__":
                            debug_active = False
                            ctx.in_debugger = False
                            idx += 1
                            break
                        debug_active = False
                        ctx.in_debugger = False
                        ctx.command_had_error = False
                        try:
                            if shell.onecmd(line):
                                return True
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

                    elif cmd in ("back", "prev"):
                        if idx > 0:
                            idx -= 1
                            ColorPrinter.warning("Moved back — instrument state NOT reversed")
                            _debug_show_context(lines, source_lines, idx, breakpoints)
                        else:
                            ColorPrinter.warning("Already at first line")

                    elif cmd.startswith(("goto ", "jump ")):
                        parts = cmd.split()
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

                    elif cmd.split()[:1] in (["b"], ["break"]):
                        parts = cmd.split()
                        try:
                            n = int(parts[1])
                            if 1 <= n <= len(lines):
                                breakpoints.add(n)
                                ColorPrinter.info(f"Breakpoint set at line {n}: {lines[n - 1]}")
                            else:
                                ColorPrinter.error(f"Line out of range (1–{len(lines)})")
                        except (ValueError, IndexError):
                            ColorPrinter.error("Usage: b <N>")

                    elif cmd.split()[:1] in (["d"], ["delete"], ["clear"]):
                        parts = cmd.split()
                        try:
                            n = int(parts[1])
                            if n in breakpoints:
                                breakpoints.discard(n)
                                ColorPrinter.info(f"Breakpoint {n} cleared")
                            else:
                                ColorPrinter.warning(f"No breakpoint at line {n}")
                        except (ValueError, IndexError):
                            ColorPrinter.error("Usage: d <N>")

                    elif cmd == "l" or cmd == "list" or cmd.startswith("l ") or cmd.startswith("list "):
                        parts = cmd.split(None, 1)
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

                    elif cmd in ("info", "i", "?"):
                        ColorPrinter.info(f"Position: line {idx + 1}/{len(lines)}")
                        if breakpoints:
                            ColorPrinter.info(f"Breakpoints: {sorted(breakpoints)}")
                        else:
                            ColorPrinter.info("No breakpoints set")

                    elif cmd in ("q", "quit", "abort"):
                        ColorPrinter.warning("Script aborted")
                        return True

                    elif cmd:
                        shell.onecmd(cmd)
            else:
                if line == "__NOP__":
                    idx += 1
                    continue
                ctx.command_had_error = False
                try:
                    if shell.onecmd(line):
                        return True
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
    breakpoints: Set[int],
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
        src = source_lines[i] if source_lines else lines[i]
        if i == idx:
            print(f"\033[96m  {bp} {i + 1:>4} → {src}\033[0m")
            if lines[i] != src:
                print(f"\033[90m         ↳ {lines[i]}\033[0m")
        else:
            print(f"  {bp} {i + 1:>4}   {src}")
    print("  " + "─" * 60)
    print(f"  {idx + 1}/{total}  │  n=step  c=continue  back  goto N  b N=break  d N=del  l [N|all]=list  q=quit")
    print()
