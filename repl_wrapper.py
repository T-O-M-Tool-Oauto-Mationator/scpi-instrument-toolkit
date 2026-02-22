# Copy this file to your personal lab repo root and rename it to repl.py
#
# Prerequisites:
#   1. Add scpi-instrument-toolkit as a submodule in your personal repo:
#        git submodule add https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git
#   2. Run: git submodule update --init
#
# Then just run from your personal repo root:
#   python repl.py
#
# .repl_scripts.json will be saved in your personal repo root automatically.

import sys
import os

# Add the submodule to sys.path so both `repl` and `lab_instruments` are importable
_toolkit = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scpi-instrument-toolkit")
if _toolkit not in sys.path:
    sys.path.insert(0, _toolkit)

from repl import main

if __name__ == "__main__":
    main()
