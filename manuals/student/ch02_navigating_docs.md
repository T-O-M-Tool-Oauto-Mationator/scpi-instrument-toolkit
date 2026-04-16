# Chapter 2: Navigating the Official Docs

## The Docs Site

The official documentation lives at:

    https://t-o-m-tool-oauto-mationator.github.io/scpi-instrument-toolkit/

This site is always up to date with the latest version of the toolkit. Bookmark it -- you will reference it often during labs.

## Site Structure

The docs are organized into these sections:

**Home** -- Quick start guide, installation, and overview of all commands.

**Installation** -- Detailed install instructions for Windows, macOS, and Linux, including TAMU managed machines.

**Supported Instruments** -- List of all supported models with connection details.

**REPL section** -- One page per instrument type, plus scripting, examples, and logging:

- General Commands -- scan, list, use, idn, raw, state, all off, sleep, exit
- Power Supply (PSU) -- chan, set, meas, get, track, save/recall
- Function Generator (AWG) -- chan, wave, freq, amp, offset, duty, phase
- Multimeter (DMM) -- config, read, meas, check, beep, display
- Oscilloscope (Scope) -- autoset, run/stop, chan, trigger, meas, waveform capture
- Source Measure Unit (SMU) -- on/off, set, meas, sweep
- EV2300 (USB-to-I2C) -- read_word, write_word, scan, probe
- Scripting -- variables, loops, if/else, scripts, debugging
- Example Workflows -- 15 ready-to-run examples with explanations
- Log & Calc -- measurement log, calculations, CSV export
- Plotting -- static plots, live plots, interactive charts

**Python API** -- How to control instruments from Python scripts (for advanced users).

**Reference** -- Auto-generated command lists and expression function tables.

**Architecture** -- How the toolkit is structured internally (for developers).

**Troubleshooting** -- Fixes for common errors and TAMU-specific issues.

## How to Search

The docs site has a search bar at the top. Type any keyword to find relevant pages:

- Type "voltage" to find PSU voltage commands, DMM voltage measurement, etc.
- Type "frequency" to find AWG frequency settings, scope frequency measurement, etc.
- Type "csv" to find how to export data to CSV files

The search is fast and searches across all pages.

## How to Find Instrument Commands

Each instrument type has its own page with every command documented. To find a command:

1. Go to the REPL section in the left sidebar
2. Click the instrument type (PSU, DMM, Scope, etc.)
3. Scroll to the command you need
4. Each command shows: syntax, parameters table, and usage examples

For example, to learn how to set a PSU voltage:
- Go to "Power Supply (PSU)" page
- Find the "psu set" section
- You will see: `psu set <channel> <voltage> [current]`
- Below that are examples: `psu set 1 5.0`, `psu set 1 5.0 0.5`

## The REPL Command Reference

Under the Reference section, there is an auto-generated "REPL Command Reference" page. This page lists every single command available in the REPL, organized by instrument type. It is generated directly from the source code, so it is always accurate and complete.

Use this page when you need a quick lookup of all commands for a specific instrument without reading the full documentation page.

## Expression Functions Reference

Also under Reference, the "Expression Functions" page lists every function you can use in `calc` expressions and variable assignments:

- Math: sqrt, sin, cos, tan, log, log10, exp, ceil, floor, abs, round
- Type conversion: int, float, str, bool, hex, bin, oct
- Constants: pi, e, inf, nan, True, False
- Comparison: ==, !=, <, <=, >, >=
- Boolean: and, or, not

## Using Help Inside the REPL

You do not always need to open the docs site. The REPL has built-in help:

    help              # list all available commands
    help psu          # show help for PSU commands
    help dmm          # show help for DMM commands
    help scope        # show help for scope commands

The `docs` command opens the full documentation in your browser:

    docs              # opens the docs site in your default browser

## Finding and Running Examples

The `examples` command inside the REPL lists all 15 bundled examples:

    examples          # list all available examples with descriptions

To load and run one:

    examples load psu_dmm_test
    script run psu_dmm_test

See Chapter 4 for detailed instructions on running examples.

## Try It

1. Open the docs site in your browser
2. Use the search bar to find "psu set"
3. Read the PSU page to understand the command syntax
4. Launch `scpi-repl --mock` and try the commands you found
