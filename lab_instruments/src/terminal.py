"""Terminal utility for colored output."""

import os
import sys


def _color_enabled() -> bool:
    """Return False when color output should be suppressed.

    Checks (in order):
    1. NO_COLOR env var (https://no-color.org/) -- any non-empty value disables color
    2. FORCE_COLOR env var -- overrides TTY detection
    3. stdout.isatty() -- disable color when piped or redirected
    """
    if os.environ.get("NO_COLOR", ""):
        return False
    if os.environ.get("FORCE_COLOR", ""):
        return True
    try:
        return sys.stdout.isatty()
    except Exception:
        return False


def disable_color() -> None:
    """Programmatically disable color output (e.g. from --no-color flag)."""
    os.environ["NO_COLOR"] = "1"
    ColorPrinter._refresh()


class ColorPrinter:
    """
    Utility for printing colored text to the terminal using ANSI escape codes.

    Respects the NO_COLOR env var (https://no-color.org/) and auto-detects
    non-TTY output. Use --no-color flag or set NO_COLOR=1 to disable.
    """

    # ANSI Color Codes (may be empty strings when color is disabled)
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    @classmethod
    def _refresh(cls) -> None:
        """Re-evaluate color support and update class constants."""
        if _color_enabled():
            cls.HEADER = "\033[95m"
            cls.BLUE = "\033[94m"
            cls.CYAN = "\033[96m"
            cls.GREEN = "\033[92m"
            cls.YELLOW = "\033[93m"
            cls.RED = "\033[91m"
            cls.RESET = "\033[0m"
            cls.BOLD = "\033[1m"
            cls.UNDERLINE = "\033[4m"
        else:
            cls.HEADER = ""
            cls.BLUE = ""
            cls.CYAN = ""
            cls.GREEN = ""
            cls.YELLOW = ""
            cls.RED = ""
            cls.RESET = ""
            cls.BOLD = ""
            cls.UNDERLINE = ""

    @staticmethod
    def info(message):
        """Print an informational message in blue."""
        print(f"{ColorPrinter.BLUE}[INFO] {message}{ColorPrinter.RESET}")

    @staticmethod
    def success(message):
        """Print a success message in green."""
        print(f"{ColorPrinter.GREEN}[SUCCESS] {message}{ColorPrinter.RESET}")

    @staticmethod
    def warning(message):
        """Print a warning message in yellow."""
        print(f"{ColorPrinter.YELLOW}[WARNING] {message}{ColorPrinter.RESET}")

    @staticmethod
    def error(message):
        """Print an error message in red."""
        print(f"{ColorPrinter.RED}[ERROR] {message}{ColorPrinter.RESET}")

    @staticmethod
    def header(message):
        """Print a bold header message in magenta."""
        print(f"\n{ColorPrinter.HEADER}{ColorPrinter.BOLD}{'=' * 60}")
        print(f"   {message.upper()}")
        print(f"{'=' * 60}{ColorPrinter.RESET}\n")

    @staticmethod
    def cyan(message):
        """Print a message in cyan."""
        print(f"{ColorPrinter.CYAN}{message}{ColorPrinter.RESET}")

    @staticmethod
    def print_info(message):
        """Alias for info."""
        ColorPrinter.info(message)

    @staticmethod
    def print_success(message):
        """Alias for success."""
        ColorPrinter.success(message)


# Auto-detect color support at import time
ColorPrinter._refresh()
