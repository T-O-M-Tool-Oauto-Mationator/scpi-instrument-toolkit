"""Base class for REPL command handlers."""

import os
import shlex
from typing import List

from lab_instruments.src.terminal import ColorPrinter

from ..context import ReplContext


class BaseCommand:
    """Base class for REPL command handlers."""

    def __init__(self, ctx: ReplContext) -> None:
        self.ctx = ctx

    @property
    def registry(self):
        return self.ctx.registry

    @property
    def measurements(self):
        return self.ctx.measurements

    def error(self, msg: str) -> None:
        self.ctx.error(msg)

    def parse_args(self, arg: str) -> List[str]:
        try:
            if os.name == "nt":
                # On Windows, use posix=False to preserve backslashes in paths,
                # then strip surrounding quotes that posix=False retains.
                tokens = shlex.split(arg, posix=False)
                return [
                    t[1:-1] if len(t) >= 2 and t[0] in ('"', "'") and t[-1] == t[0] else t
                    for t in tokens
                ]
            return shlex.split(arg)
        except ValueError as exc:
            ColorPrinter.error(f"Parse error: {exc}")
            return []

    def is_help(self, args: List[str]) -> bool:
        if not args:
            return False
        return args[-1].lower() in ("help", "-h", "--help")

    def strip_help(self, args: List[str]):
        if self.is_help(args):
            return args[:-1], True
        return args, False

    def parse_channels(self, ch_str: str, max_ch: int = 4) -> List[int]:
        s = str(ch_str).lower().strip()
        if s == "all":
            return list(range(1, max_ch + 1))
        if s.startswith("ch"):
            s = s[2:]
        return [int(s)]

    @staticmethod
    def print_usage(lines: list) -> None:
        for line in lines:
            print(line)

    @staticmethod
    def print_colored_usage(lines: list) -> None:
        for line in lines:
            if line.strip().startswith("#"):
                ColorPrinter.header(line.strip("# ").strip())
            elif line.strip().startswith("-"):
                print(f"{ColorPrinter.YELLOW}{line}{ColorPrinter.RESET}")
            elif line.strip() and not line.startswith(" "):
                parts = line.split(" ", 1)
                if len(parts) == 2:
                    print(f"{ColorPrinter.CYAN}{parts[0]}{ColorPrinter.RESET} {parts[1]}")
                else:
                    print(f"{ColorPrinter.CYAN}{line}{ColorPrinter.RESET}")
            else:
                print(line)

    def raw_path_arg(self, raw: str, strip_word: str = None) -> str:
        s = raw.strip()
        if strip_word:
            prefix = strip_word.lower()
            if s.lower().startswith(prefix) and (len(s) == len(prefix) or s[len(prefix)].isspace()):
                s = s[len(prefix) :].lstrip()
        if not s:
            return None
        if len(s) >= 2 and s[0] in ('"', "'") and s[-1] == s[0]:
            s = s[1:-1]
        return s or None
