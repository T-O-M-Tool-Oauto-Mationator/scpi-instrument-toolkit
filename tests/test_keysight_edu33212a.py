import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from lab_instruments import ColorPrinter, InstrumentDiscovery, Keysight_EDU33212A
except ImportError as e:
    print(f"Import Error: {e}")
    print("Ensure you are running this from the project root or have installed the package.")
    sys.exit(1)


def _ask(prompt):
    return input(prompt).strip().lower()


def _test_step(label, fn, results):
    ColorPrinter.info(label)
    try:
        fn()
        ok = _ask("Press Enter if correct, type 'no' if wrong: ") != "no"
    except Exception as exc:
        ColorPrinter.error(f"  Exception: {exc}")
        ok = False
    results[label] = ok
    if ok:
        ColorPrinter.success("  PASS")
    else:
        ColorPrinter.error("  FAIL")


def main():
    ColorPrinter.header("Testing Keysight EDU33212A AWG Driver")

    discovery = InstrumentDiscovery()
    discovery.scan(verbose=True)

    # Find any EDU33212A among discovered instruments (awg, awg1, awg2, ...)
    awg = None
    for name, driver in discovery.found_devices.items():
        if isinstance(driver, Keysight_EDU33212A):
            awg = driver
            ColorPrinter.info(f"Using EDU33212A at name '{name}'")
            break

    if not awg:
        ColorPrinter.error("Keysight EDU33212A not found. Check USB connection and that *IDN? returns 'EDU33212A'.")
        return

    ColorPrinter.success(f"Found EDU33212A at: {awg.resource_name}")

    results = {}

    try:
        # ---- CH1 Basic Waveforms ----
        ColorPrinter.header("CH1 Basic Waveforms")

        _test_step(
            "CH1 SIN 1kHz 1Vpp",
            lambda: (
                awg.set_waveform(1, "SIN", frequency=1000, amplitude=1.0, offset=0),
                awg.enable_output(1, True),
            ),
            results,
        )

        _test_step(
            "CH1 SQU 1kHz 1Vpp 50% duty",
            lambda: (
                awg.set_waveform(1, "SQU", frequency=1000, amplitude=1.0, duty=50),
                awg.enable_output(1, True),
            ),
            results,
        )

        _test_step(
            "CH1 RAMP 1kHz 1Vpp 50% symmetry",
            lambda: (
                awg.set_waveform(1, "RAMP", frequency=1000, amplitude=1.0, symmetry=50),
                awg.enable_output(1, True),
            ),
            results,
        )

        _test_step(
            "CH1 PULS 1kHz 1Vpp 10% duty",
            lambda: (
                awg.set_waveform(1, "PULS", frequency=1000, amplitude=1.0, duty=10),
                awg.enable_output(1, True),
            ),
            results,
        )

        _test_step(
            "CH1 NOIS 1Vpp",
            lambda: (
                awg.set_waveform(1, "NOIS", amplitude=1.0),
                awg.enable_output(1, True),
            ),
            results,
        )

        _test_step(
            "CH1 DC +1V",
            lambda: (
                awg.set_dc_output(1, 1.0),
                awg.enable_output(1, True),
            ),
            results,
        )

        awg.enable_output(1, False)

        # ---- CH2 Basic Waveforms ----
        ColorPrinter.header("CH2 Basic Waveforms")

        _test_step(
            "CH2 SIN 2kHz 0.5Vpp",
            lambda: (
                awg.set_waveform(2, "SIN", frequency=2000, amplitude=0.5, offset=0),
                awg.enable_output(2, True),
            ),
            results,
        )

        _test_step(
            "CH2 SQU 2kHz 0.5Vpp 25% duty",
            lambda: (
                awg.set_waveform(2, "SQU", frequency=2000, amplitude=0.5, duty=25),
                awg.enable_output(2, True),
            ),
            results,
        )

        _test_step(
            "CH2 RAMP 500Hz 1Vpp 100% symmetry (sawtooth up)",
            lambda: (
                awg.set_waveform(2, "RAMP", frequency=500, amplitude=1.0, symmetry=100),
                awg.enable_output(2, True),
            ),
            results,
        )

        awg.enable_output(2, False)

        # ---- Output Load ----
        ColorPrinter.header("Output Load (termination)")

        _test_step(
            "CH1 SIN 1kHz, load = High-Z",
            lambda: (
                awg.set_waveform(1, "SIN", frequency=1000, amplitude=1.0),
                awg.set_output_load(1, "INF"),
                awg.enable_output(1, True),
            ),
            results,
        )
        awg.set_output_load(1, 50)  # restore default
        awg.enable_output(1, False)

        # ---- Modulation ----
        ColorPrinter.header("Modulation")

        _test_step(
            "CH1 AM: 1kHz sine carrier, 100% depth, 10Hz internal SIN",
            lambda: (
                awg.set_waveform(1, "SIN", frequency=1000, amplitude=1.0),
                awg.set_am(1, True, depth=100, mod_freq=10, mod_func="SIN"),
                awg.enable_output(1, True),
            ),
            results,
        )
        awg.set_am(1, False)
        awg.enable_output(1, False)

        _test_step(
            "CH1 FM: 1kHz sine carrier, 100Hz deviation, 10Hz internal SIN",
            lambda: (
                awg.set_waveform(1, "SIN", frequency=1000, amplitude=1.0),
                awg.set_fm(1, True, deviation=100, mod_freq=10, mod_func="SIN"),
                awg.enable_output(1, True),
            ),
            results,
        )
        awg.set_fm(1, False)
        awg.enable_output(1, False)

        _test_step(
            "CH1 FSK: 1kHz carrier, 500Hz hop, 5Hz rate",
            lambda: (
                awg.set_waveform(1, "SIN", frequency=1000, amplitude=1.0),
                awg.set_fsk(1, True, hop_freq=500, rate=5),
                awg.enable_output(1, True),
            ),
            results,
        )
        awg.set_fsk(1, False)
        awg.enable_output(1, False)

        # ---- Sweep ----
        ColorPrinter.header("Sweep")

        _test_step(
            "CH1 Sweep: 100Hz to 10kHz, 2s, linear",
            lambda: (
                awg.set_waveform(1, "SIN", amplitude=1.0),
                awg.set_sweep(1, True, start=100, stop=10000, time=2.0),
                awg.enable_output(1, True),
            ),
            results,
        )
        awg.set_sweep(1, False)
        awg.enable_output(1, False)

        # ---- Burst ----
        ColorPrinter.header("Burst")

        _test_step(
            "CH1 Burst: 1kHz SIN, 5 cycles, 10ms period",
            lambda: (
                awg.set_waveform(1, "SIN", frequency=1000, amplitude=1.0),
                awg.set_burst(1, True, mode="TRIGgered", n_cycles=5, period=0.01),
                awg.set_trigger_source(1, "IMMediate"),
                awg.enable_output(1, True),
            ),
            results,
        )
        awg.set_burst(1, False)
        awg.enable_output(1, False)

        # ---- Dual Channel ----
        ColorPrinter.header("Dual Channel (CH1 + CH2 simultaneous)")

        _test_step(
            "CH1 SIN 1kHz + CH2 SQU 2kHz, both enabled",
            lambda: (
                awg.set_waveform(1, "SIN", frequency=1000, amplitude=1.0),
                awg.set_waveform(2, "SQU", frequency=2000, amplitude=1.0, duty=50),
                awg.enable_output(1, True),
                awg.enable_output(2, True),
            ),
            results,
        )
        awg.disable_all_channels()

    finally:
        ColorPrinter.info("Disabling all outputs and disconnecting.")
        awg.disable_all_channels()
        awg.disconnect()

    # Summary
    ColorPrinter.header("Test Summary")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    for label, ok in results.items():
        if ok:
            ColorPrinter.success(f"  PASS  {label}")
        else:
            ColorPrinter.error(f"  FAIL  {label}")
    print()
    ColorPrinter.success(f"{passed}/{total} tests passed.") if passed == total else ColorPrinter.warning(
        f"{passed}/{total} tests passed."
    )


if __name__ == "__main__":
    main()
