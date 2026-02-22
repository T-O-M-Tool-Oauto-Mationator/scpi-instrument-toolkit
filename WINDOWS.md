# Windows Installation Guide

On Windows, the `scpi-repl` command may be blocked by Application Control policies. This guide explains the issue and how to fix it.

## The Problem

When you install the toolkit with `pip install`, it creates a `scpi-repl.exe` file. Windows may block this exe with an "Application Control policy has blocked this file" error.

This is a security feature but prevents you from using the CLI as documented.

## Solution

Run the post-install fix script after installing:

```bash
python fix_windows.py
```

This will:

1. Remove the blocked exe file
2. Create a batch file wrapper that calls Python directly
3. Make `scpi-repl` command work immediately

## After the Fix

You can now use the toolkit exactly as documented:

```bash
scpi-repl                    # Start the interactive REPL
scpi-repl --mock             # Demo mode with mock instruments
scpi-repl lab3               # Run a script from the REPL
scpi-repl script.scpi        # Run a SCPI script file
```

## Alternative (Without Fix)

If you prefer not to run the fix script, you can always use:

```bash
python -m lab_instruments.repl
```

This works identically to `scpi-repl` without any Windows issues.

## Re-installing

If you reinstall the toolkit with pip, you may need to run `python fix_windows.py` again to reapply the fix.
