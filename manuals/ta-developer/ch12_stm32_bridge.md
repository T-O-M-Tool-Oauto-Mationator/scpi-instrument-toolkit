# Chapter 12: The STM32 Bridge (EV2300 Replacement)

## Why we built it

The TI EV2300A USB-to-SMBus bridge is the original "TAMU bench standard" adapter students use to talk to the BQ76920 battery-monitor IC on its EVM board. It is discontinued, and replacement units on the secondary market are expensive and inconsistent. To keep ESET 453 lab kits running past the current supply, we built a drop-in replacement out of an Adafruit Feather STM32F405 + a FeatherWing protoboard.

Key properties of the replacement:

- Open hardware, ~$25 in parts per unit, solderable in ~30 minutes.
- Enumerates over USB HID with the same semantics the EV2300 driver already speaks.
- `lab_instruments/src/ev2300.py` autodetects both bridges; no REPL or script changes are required.
- Firmware is re-flashable via the STM32 DFU bootloader, so any TA can service a unit without vendor tools.

## Bill of Materials (per unit)

| Part | Qty | Notes |
|------|-----|-------|
| Adafruit Feather STM32F405 Express | 1 | USB-C, SPI/I2C pins broken out on the Feather edge |
| Adafruit FeatherWing Proto PCB | 1 | Socketed pin grid that mates to the Feather |
| JST-PH 4-pin right-angle connector | 1 | Mates the ribbon cable that ships with the BQ EVM I2C header |
| Male pin header strips, 0.1 in | 2 | Cut to length for the Feather edges |
| 22 AWG solid hookup wire (yellow, blue, black) | ~6 in each | SDA, SCL, GND |
| Heat-shrink, 3 mm | ~2 in | Strain relief where the JST pigtail meets the board |
| USB-C cable | 1 | Reuse from bench kit |

Cost is ~$25 per kit at current Adafruit pricing.

## Soldering the adapter

The build goes in five stages. Take continuity measurements between stages 3 and 5; catching a short before you stack the Feather saves a lot of time.

### Step 1 - Bare protoboard and connector

![Bare protoboard with JST connector and hookup wires staged next to it](../../docs/img/stm32/IMG_0255_protoboard_bare.jpg)

- Position the JST connector on the short edge of the protoboard, keyway facing out so the cable can seat without fighting the Feather body above it.
- Pre-cut two lengths of 22 AWG hookup wire for SDA (yellow) and SCL (blue). GND and 3V3 use the two outer JST shell pins and short traces on the protoboard.

### Step 2 - Mount in the helping-hand

![Protoboard held in a helping-hand clamp, ready to be soldered](../../docs/img/stm32/IMG_0256_protoboard_clamp.jpg)

- Clamp the protoboard close to the JST connector but not on it; the connector body warps if squeezed.
- Tack one JST pin first, check that the connector sits flush, then solder the remaining three.

### Step 3 - Back-side wiring to the JST

![Yellow and blue hookup wires soldered across the back of the protoboard to the JST pins](../../docs/img/stm32/IMG_0263_wires_soldered.jpg)

- SDA pad on the Feather footprint routes to JST pin 2 (yellow).
- SCL pad routes to JST pin 3 (blue).
- GND pad routes to JST pin 4.
- The red wire on the BQ EVM ribbon is a no-connect. Do not route it to 3V3 - the EVM provides its own logic rail and back-powering the bridge through that pin will fight the Feather regulator.
- Before stacking, buzz each pad-to-pin trace with a DMM in continuity mode. Any two adjacent pins should read OL.

### Step 4 - Headers on the Feather

![Adafruit Feather STM32F405 with male pin headers installed along both long edges](../../docs/img/stm32/IMG_0264_feather_headers.jpg)

- Push male headers through the Feather from the top side, long end down.
- Use the protoboard itself as a jig: drop the Feather onto it so the headers land straight, then solder the four corner pins before doing the rest. This keeps the two boards coplanar.

### Step 5 - Stack and finish

![Finished adapter: STM32F405 Feather stacked on the wired protoboard with the JST pigtail exiting the short edge](../../docs/img/stm32/IMG_0265_assembled.jpg)

- Separate the boards, tin the Feather headers, then re-seat and solder each header pin through to the protoboard pads.
- Add a 3 mm heat-shrink collar where the JST cable exits the board for strain relief.
- Plug the JST cable into the BQ EVM I2C header and a USB-C cable into the Feather.

## Firmware

Flash the Feather with the STM32 bridge firmware before handing the unit out.

- Firmware source: internal repo (ask the course coordinator for the current link; this chapter intentionally does not hardcode it because the repo is still private).
- Flash path: USB DFU. Press RESET while holding BOOT to enter DFU mode, then use `dfu-util` or the Adafruit WebDFU page.
- The driver matches on both USB descriptors:
    - Real EV2300A: VID `0x0451`, PID `0x0036`
    - STM32 bridge: reuses the same VID/PID after firmware enumeration, so `lab_instruments/src/ev2300.py` sees it as a normal `EV2300A`.

If the bridge comes up in DFU mode (no I2C traffic, `scan` shows a "bootloader" descriptor), reflash. There is no recovery path from the REPL.

## Bench verification checklist

After assembly, run this top-to-bottom before labeling the unit as good:

1. Power the BQ76920 EVM from an 18 V bench supply on the external power input.
2. Plug the STM32 bridge USB into the host computer.
3. Press the BOOT button on the BQ EVM. This clears any stuck I2C state from the last session.
4. Launch the REPL: `scpi-repl --no-color`.
5. Run `scan`. Expect `ev2300` in the device list within two seconds.
6. Run `ev2300 read_word 0x08 0x09`. For a nominal 3.3 V cell stack you should see `0x0CE4 (3300)` or similar; the exact value depends on the battery state but it must not be `0x0000` or `0xFFFF`.
7. Run `ev2300 scan 0x08` and confirm you get more than 20 readable registers.
8. Run the regression subset: `python -m pytest tests/test_ev2300_driver.py -x`.

If any step fails, move to the troubleshooting section below before handing out the kit.

## Troubleshooting the bridge

### Bridge enumerates but `read_word` returns 0xFFFF

The STM32 firmware retries BQ76920 init every 2 s after a failed startup detection. Usually caused by the EVM being unpowered when the USB was plugged in. Fix: leave USB connected, power the EVM, then call `ev2300 read_word ...` again. The `wait_for_bq` helper in `lab_instruments/src/ev2300.py` polls `CC_CFG` (reg `0x0B`) on both possible I2C addresses until the IC responds, and is the programmatic version of this procedure.

### Intermittent `0x46` errors on long sessions

Usually USB noise coupling onto the I2C lines. Fixes, in order of cost:

1. Clip a ferrite onto the JST pigtail close to the adapter.
2. Shorten the JST cable run.
3. Replace the USB cable with a shielded one.

### `connect failed` on `scan`

Another process holds the HID handle. Close BQ Studio, then retry.

### Board is dead after flashing

The DFU flow leaves the Feather in app mode only after a clean reset. Unplug USB, hold BOOT, plug USB back in, release BOOT, and reflash. If the board still does not enumerate, the STM32F405 may have been bricked by a bad firmware image - fall back to the STM32CubeProgrammer and reflash the default Adafruit bootloader first.

## Making another one

This chapter is the build log. BOM, soldering photos, firmware path, and verification checklist are all here - a TA with a soldering iron and a copy of the firmware binary should be able to assemble a replacement unit without any other documentation.
