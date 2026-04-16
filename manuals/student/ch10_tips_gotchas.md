# Chapter 10: Instrument Tips and Gotchas

Each instrument has quirks. This chapter covers the things that trip students up most often.

## Power Supplies

### HP E3631A (psu1)

- **Triple output with shared ground.** Channels 1 (0-6V), 2 (0-25V), and 3 (0 to -25V) share a common ground. You cannot float them independently.
- **Tracking mode** links channels 2 and 3 for +/- supply configurations. Use `psu track on`.
- **No current readback below ~1mA.** Very low currents read as 0. Use an external DMM for milliamp-level measurements.
- **Output enable is per-channel.** You must run `psu chan 1 on` before `psu set 1 5.0` produces any output.

### Keysight EDU36311A (psu3)

- **OVP/OCP protection.** Over-voltage and over-current protection can trip and latch off the output. Check the front panel if the output unexpectedly drops to 0.
- **5 save/recall slots.** Use `psu save 1` and `psu recall 1` to store and restore setups.
- **USB enumeration delay.** After connecting, wait 5-10 seconds before running `scan`. The USB interface takes time to initialize.

### Matrix MPS-6010H (psu2)

- **Serial interface with slow command response.** Allow 100-200ms between commands. The toolkit handles this automatically, but manual `raw` commands may need `sleep 0.2` between them.
- **Remote mode must be enabled.** The toolkit does this automatically on first command.

## Multimeters

### HP 34401A (dmm1)

- **NPLC setting matters.** Integration time (power line cycles) directly affects accuracy and speed:
  - `nplc=0.02` -- fast but noisy (50 readings/second)
  - `nplc=1` -- good balance (default)
  - `nplc=10` -- high accuracy, slow (about 0.5 seconds per reading)
  - `nplc=100` -- maximum accuracy, very slow (about 2 seconds per reading)
- **Display blanking.** `dmm display off` speeds up measurements by ~10% on GPIB.
- **Auto-range settling.** When auto-ranging, the first reading after a range change may be inaccurate. Take a throwaway reading first.
- **GPIB address.** Default is usually address 22. Check the front panel under Utility > Remote Interface.

### Keysight EDU34450A (dmm3)

- **No NPLC support.** Uses SLOW/MEDIUM/FAST speed settings instead.
- **Capacitance and temperature modes.** Supported but not on all HP models -- check before using.
- **Dual display.** Can show two measurements simultaneously on the front panel, but the REPL reads only the primary display.

### OWON XDM1041 (dmm2)

- **4.5 digits.** Lower resolution than the HP 34401A (6.5 digits). Expect more noise in readings.
- **Limited modes.** Does not support NPLC, display text, or fetch.

## Oscilloscopes

### Rigol DHO804 (scope1)

- **Autoset works well** but may choose unexpected time/voltage scales for complex signals. Always verify the display after autoset.
- **Measurement force.** After `scope single` + `scope wait_stop`, run `scope meas_force` before reading measurements. This forces the DSP to finalize values.
- **9.9e+37 sentinel.** If a measurement returns `9.9e+37`, the scope has not triggered yet. Use `scope wait_stop` to wait for the trigger.
- **Built-in AWG.** The DHO804 has a built-in function generator accessible through `scope1 awg_*` commands.
- **Counter and DVM.** Built-in frequency counter and digital voltmeter -- useful for quick checks without switching instruments.

### Tektronix MSO2024 (scope2)

- **Basic command set only.** Does not support counter, DVM, cursors, recording, or built-in AWG features.
- **Slower autoset.** Allow 2-3 seconds for autoset to complete.
- **save_waveform_csv accepts lists.** You can pass `[1, 2]` to save multiple channels in one CSV.

### Keysight DSOX1204G (scope3)

- **Most feature-rich scope.** Supports counter, DVM, cursors, mask test, built-in AWG (WGEN), screenshot, display, acquire, math, labels, segmented acquisition, and measurement statistics.
- **No recording support.** Cannot use the record/playback feature.
- **Segmented memory.** Supports capturing multiple trigger events in separate memory segments.

## Function Generators

### Keysight EDU33212A (awg1)

- **Dual channel.** Both channels can output independently. Use `awg chan 1 on` and `awg chan 2 on`.
- **PRBS mode.** Supports pseudo-random binary sequence for BER testing. Other AWGs do not have this.
- **High impedance vs 50 ohm.** The AWG assumes a 50 ohm load. If your circuit is high-impedance, the actual output voltage will be double the set amplitude.

### JDS6600 (awg2)

- **Serial interface.** Slower than USB instruments. Allow 200ms between commands.
- **17 waveform types.** Supports more waveform shapes than other AWGs.
- **Frequency accuracy.** DDS-based, so frequency accuracy is excellent.

### BK Precision 4063 (awg3)

- **Single channel only.** No channel 2.

## Source Measure Unit

### NI PXIe-4139 (smu)

- **PXIe boot order matters.** The PXIe chassis must be powered on before the host PC boots. If the PC boots first, the PXIe card will not be detected. Power cycle the chassis and reboot.
- **4-quadrant operation.** Can source and sink both voltage and current. Be careful with polarity.
- **Compliance limits.** Always set current compliance when sourcing voltage, and voltage compliance when sourcing current. The toolkit enforces this.
- **nidcpower required.** The NI-DCPower Python driver must be installed. See the NI PXIe-4139 setup page in the docs.

## EV2300 (USB-to-I2C Adapter)

### TI EV2300

- **HID interface.** Communicates over USB HID, not VISA. No NI-VISA required.
- **I2C address format.** Addresses are 7-bit. Use hex: `ev2300 read_word 0x08 0x09`.
- **Bus recovery.** If I2C communication hangs, use `ev2300 fix` to attempt bus recovery.
- **Slow for bulk transfers.** HID has limited bandwidth. Block reads of large registers take time.

## General Tips

- **Always `sleep` after setting a voltage.** PSU outputs need 100-500ms to settle. Without this delay, your DMM will read an intermediate value.
- **Configure the DMM mode before measuring.** The most common mistake is measuring without setting the correct mode (vdc, idc, res, etc.).
- **Use `all off` before disconnecting.** This safely disables all outputs before you unplug anything.
- **Save early, save often.** Run `log save` frequently. If the REPL crashes or you accidentally run `log clear`, your data is gone.
- **Use descriptive labels.** `ch1_vout_5v0` is much better than `v1` when you look at the CSV later.
