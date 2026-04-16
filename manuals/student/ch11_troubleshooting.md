# Chapter 11: Troubleshooting

## "scpi-repl" is not recognized

**Windows (personal machine):** Run `python -m lab_instruments` once. The toolkit automatically adds the Scripts folder to your PATH. Open a new terminal window and try again.

**TAMU managed machines (VOAL):** Registry edits are blocked. Use the module form as your permanent launch method:

    python -m lab_instruments
    python -m lab_instruments --mock

Or set PATH for the current session only:

    $env:PATH = "$env:LOCALAPPDATA\Programs\Python\Python312\Scripts;" + $env:PATH

Then `scpi-repl` will work in that terminal window.

## "No module named 'lab_instruments'"

The toolkit is not installed. Run:

    pip install git+https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git

If you get permission errors, add `--user`:

    pip install --user git+https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git

## "Scan complete: no instruments found"

- Check that instruments are powered on and connected via USB/GPIB.
- Make sure NI-VISA is installed (required for VISA instruments).
- Check that no other program (BQStudio, vendor GUI, another REPL session) is using the instrument. Only one program can connect at a time.
- Try `force_scan` -- this does a slower, more thorough scan.
- On Linux, make sure your user is in the `dialout` group for serial instruments.

## "Resource busy" or "Cannot open resource"

Another program is already connected to the instrument. Close it first:

- Another terminal running `scpi-repl`
- A Python script using the same instrument
- Vendor software (BQStudio, Keysight Connection Expert, NI MAX, etc.)
- A previous REPL session that crashed without disconnecting

If a previous session crashed:

    # On macOS/Linux -- find and kill stuck processes
    ps aux | grep scpi
    kill <pid>

    # On Windows
    tasklist | findstr python
    taskkill /PID <pid> /F

## Measurements return "9.9e+37"

This is the SCPI sentinel value for "measurement not available." Common causes:

- The scope has not triggered yet. Use `scope wait_stop` before reading measurements.
- The DMM is not configured. Run `dmm config vdc` (or appropriate mode) first.
- The instrument is in an error state. Run `idn` to verify communication, then `state reset`.

## PSU output stays at 0 V

- Did you enable the output? Run `psu chan 1 on` first.
- Is OVP/OCP tripped? Check the front panel for protection indicators.
- Did you set the correct channel? `psu set 1 5.0` sets channel 1. `psu set 2 5.0` sets channel 2.

## DMM reads the wrong value

- Check the measurement mode. Run `dmm config vdc` for DC voltage, `dmm config idc` for DC current, etc.
- Wrong range? Auto-range may pick an unexpected range. Specify manually: `dmm config vdc 10`.
- Probe connected to wrong terminals? Voltage uses V/COM terminals. Current uses A/COM or mA/COM.

## "NI-VISA not found"

Install the NI-VISA runtime:

    https://www.ni.com/en/support/downloads/drivers/download.ni-visa.html

On Linux, install from the .deb or .rpm package. On macOS, install from the .dmg.

After installing, restart your terminal.

## NI PXIe-4139 not detected

1. Power cycle the PXIe chassis FIRST
2. Then reboot the host PC
3. The chassis must be on before the PC boots -- boot order matters
4. Verify with NI MAX that the device appears

## Serial port permission denied (Linux)

Add your user to the dialout group:

    sudo usermod -a -G dialout $USER

Log out and back in for the change to take effect.

## EV2300 communication errors

The I2C bus may be stuck. Try:

    ev2300 fix

This sends clock pulses to recover the bus. If that does not work, disconnect and reconnect the EV2300 USB cable.

## "git" is not recognized (Windows)

Install Git for Windows from https://git-scm.com/download/win or use the toolkit's setup script which does not require git.

## REPL crashes or freezes

- Check if an instrument disconnected during a measurement. Reconnect and run `scan`.
- If the REPL is frozen, press Ctrl+C to interrupt, then Ctrl+D to exit.
- If Ctrl+C does not work, close the terminal window.

## Update errors

If `pip install --upgrade` fails:

    pip install --force-reinstall git+https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git

## Getting Help

- Official docs: https://t-o-m-tool-oauto-mationator.github.io/scpi-instrument-toolkit/
- In the REPL: type `help` for command list, `help psu` for specific help
- Report bugs: https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit/issues
