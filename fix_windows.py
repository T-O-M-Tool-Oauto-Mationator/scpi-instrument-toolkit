#!/usr/bin/env python3
"""
Post-install script to fix Windows security issues with console_scripts.

On Windows, pip generates .exe wrappers for console_scripts entries, which can be
blocked by Windows Application Control policies. This script replaces the .exe
with a batch file wrapper that calls the Python module directly.

Run this after installing scpi-instrument-toolkit on Windows.
"""

import os
import sys
import shutil
from pathlib import Path


def fix_windows_scpi_repl():
    """Replace scpi-repl.exe with scpi-repl.bat on Windows."""
    
    if not sys.platform.startswith('win'):
        print("This script is for Windows only.")
        return False
    
    # Find the Scripts directory
    if hasattr(sys, 'base_prefix'):
        scripts_dir = Path(sys.base_prefix) / 'Scripts'
    else:
        scripts_dir = Path(sys.prefix) / 'Scripts'
    
    exe_file = scripts_dir / 'scpi-repl.exe'
    bat_file = scripts_dir / 'scpi-repl.bat'
    
    if not exe_file.exists():
        print(f"scpi-repl.exe not found at {exe_file}")
        return False
    
    # Create batch file content
    bat_content = """@echo off
REM scpi-repl batch file wrapper for Windows
REM Bypasses exe blocking by directly calling the Python module
python -m lab_instruments.repl %*
"""
    
    try:
        # Remove the exe
        exe_file.unlink()
        print(f"✓ Removed {exe_file}")
        
        # Create the batch file
        bat_file.write_text(bat_content)
        print(f"✓ Created {bat_file}")
        print("\n✓ scpi-repl command is now ready to use!")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


if __name__ == '__main__':
    success = fix_windows_scpi_repl()
    sys.exit(0 if success else 1)
