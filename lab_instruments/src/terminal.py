"""Terminal utility for colored output."""


class ColorPrinter:
    """
    Utility for printing colored text to the terminal using ANSI escape codes.
    """

    # ANSI Color Codes
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

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
