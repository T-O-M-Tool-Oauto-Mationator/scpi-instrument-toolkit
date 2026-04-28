"""
Live, hardware-in-the-loop validation of all connected Keysight drivers.

Pass A (this script): passive checks — IDN, error queue, setpoint round-trips,
input validation, mode/coupling/trigger/acquisition config, queries.
Does NOT enable any PSU/AWG/WGEN output. Safe to run with whatever DUT (or
nothing) is wired to the instruments.
"""

from __future__ import annotations

import math
import sys
import time
import traceback

from lab_instruments.src.discovery import InstrumentDiscovery


class Recorder:
    def __init__(self, label: str):
        self.label = label
        self.passed = 0
        self.failed = 0
        self.errors: list[tuple[str, str]] = []

    def check(self, name: str, fn):
        try:
            fn()
            self.passed += 1
            print(f"  [PASS] {name}")
        except AssertionError as e:
            self.failed += 1
            self.errors.append((name, f"AssertionError: {e}"))
            print(f"  [FAIL] {name}: {e}")
        except Exception as e:
            self.failed += 1
            tb = traceback.format_exc(limit=2)
            self.errors.append((name, f"{type(e).__name__}: {e}\n{tb}"))
            print(f"  [ERR ] {name}: {type(e).__name__}: {e}")

    def summary(self) -> str:
        return f"{self.label}: {self.passed} passed, {self.failed} failed/errored"


def approx(a: float, b: float, rel: float = 1e-3, abs_: float = 1e-6) -> bool:
    return math.isclose(a, b, rel_tol=rel, abs_tol=abs_)


def expect_value_error(fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except ValueError:
        return
    except Exception as e:
        raise AssertionError(f"expected ValueError, got {type(e).__name__}: {e}") from e
    raise AssertionError("expected ValueError, got no exception")


def drain_errors(label: str, getter) -> list[str]:
    """Drain the SCPI error queue, return list of non-empty error strings."""
    errs: list[str] = []
    for _ in range(20):
        try:
            err = getter().strip()
        except Exception as e:
            errs.append(f"<query failed: {e}>")
            break
        if not err:
            break
        if "+0" in err and "No error" in err:
            break
        if err.startswith('0,"No error"') or err == '0,"No error"':
            break
        errs.append(err)
    if errs:
        print(f"  >> {label} error queue: {errs}")
    return errs


# ----------------------------------------------------------------------
# PSU: Keysight EDU36311A
# ----------------------------------------------------------------------
def test_psu(psu) -> Recorder:
    r = Recorder("PSU EDU36311A")
    print(f"\n=== {r.label} @ {psu.resource_name} ===")

    # Baseline: outputs already disabled by connect(); confirm.
    psu.clear_status()

    r.check(
        "output state is OFF after connect",
        lambda: (
            (s := psu.get_output_state()),
            (_ := (False if isinstance(s, bool) else None)),
            (_ := True if s is False else (_ for _ in ()).throw(AssertionError(f"expected False, got {s}"))),
        ),
    )

    # Setpoint round-trip on each channel — voltages low, current limits also low.
    test_points = {
        "p6v_channel": (1.234, 0.250),
        "p30v_channel": (5.500, 0.150),
        "n30v_channel": (3.300, 0.100),
    }

    for ch, (v, i) in test_points.items():
        r.check(f"set_output_channel {ch} v={v} i={i}", lambda ch=ch, v=v, i=i: psu.set_output_channel(ch, v, i))
        r.check(
            f"voltage setpoint round-trip {ch}",
            lambda ch=ch, v=v: (
                (got := psu.get_voltage_setpoint(ch)),
                None
                if approx(got, v, rel=2e-3, abs_=5e-3)
                else (_ for _ in ()).throw(AssertionError(f"set {v} got {got}")),
            ),
        )
        r.check(
            f"current limit round-trip {ch}",
            lambda ch=ch, i=i: (
                (got := psu.get_current_limit(ch)),
                None
                if approx(got, i, rel=2e-3, abs_=5e-3)
                else (_ for _ in ()).throw(AssertionError(f"set {i} got {got}")),
            ),
        )

    # set_voltage / set_current_limit (no APPLy) round-trip
    r.check("set_voltage on p6v_channel", lambda: psu.set_voltage("p6v_channel", 2.5))
    r.check(
        "set_voltage round-trip",
        lambda: (
            (got := psu.get_voltage_setpoint("p6v_channel")),
            None if approx(got, 2.5, abs_=5e-3) else (_ for _ in ()).throw(AssertionError(f"got {got}")),
        ),
    )
    r.check("set_current_limit on p6v_channel", lambda: psu.set_current_limit("p6v_channel", 0.5))
    r.check(
        "set_current_limit round-trip",
        lambda: (
            (got := psu.get_current_limit("p6v_channel")),
            None if approx(got, 0.5, abs_=5e-3) else (_ for _ in ()).throw(AssertionError(f"got {got}")),
        ),
    )

    # Tracking on/off (just verify SCPI accepted)
    r.check("set_tracking ON", lambda: psu.set_tracking(True))
    r.check("set_tracking OFF", lambda: psu.set_tracking(False))

    # Save / recall round-trip in slot 1 (preserving previous slot? *SAV overwrites)
    r.check("save_state slot 1", lambda: psu.save_state(1))
    r.check("recall_state slot 1", lambda: psu.recall_state(1))

    # Input validation
    r.check(
        "select_channel rejects bad name",
        lambda: expect_value_error(psu.select_channel, "bogus"),
    )
    r.check(
        "set_output_channel rejects bad name",
        lambda: expect_value_error(psu.set_output_channel, "bogus", 1.0, 0.1),
    )
    r.check(
        "measure_voltage rejects bad name",
        lambda: expect_value_error(psu.measure_voltage, "bogus"),
    )
    r.check(
        "save_state rejects out-of-range slot",
        lambda: expect_value_error(psu.save_state, 99),
    )
    r.check(
        "recall_state rejects out-of-range slot",
        lambda: expect_value_error(psu.recall_state, 0),
    )

    # Output is still OFF (connect() turned it off, set_output_channel is APPLy
    # which doesn't change output state by itself).
    r.check(
        "output still OFF after setpoint changes",
        lambda: (
            None if psu.get_output_state() is False else (_ for _ in ()).throw(AssertionError("output unexpectedly ON"))
        ),
    )

    # Measurements are valid even with output off — they read the rails.
    for ch in test_points:
        r.check(
            f"measure_voltage {ch} (output OFF, expect ~0)",
            lambda ch=ch: (
                (v := psu.measure_voltage(ch)),
                None if abs(v) < 0.5 else (_ for _ in ()).throw(AssertionError(f"output OFF but read {v}V")),
            ),
        )
        r.check(
            f"measure_current {ch} (output OFF, expect ~0)",
            lambda ch=ch: (
                (i := psu.measure_current(ch)),
                None if abs(i) < 0.05 else (_ for _ in ()).throw(AssertionError(f"output OFF but read {i}A")),
            ),
        )

    # Drain error queue
    drain_errors("PSU", psu.get_error)

    # Final safety: re-disable everything.
    r.check("disable_all_channels (final)", psu.disable_all_channels)
    return r


# ----------------------------------------------------------------------
# DMM: Keysight EDU34450A
# ----------------------------------------------------------------------
def test_dmm(dmm) -> Recorder:
    r = Recorder("DMM EDU34450A")
    print(f"\n=== {r.label} @ {dmm.resource_name} ===")

    dmm.clear_status()

    # Configure + read each function; we just verify the read returns a float
    # (open leads typically return ~0V or overload ~9.9e37).
    # AC and capacitance modes settle slower than DC, so bump the VISA timeout
    # for those reads — the EDU34450A's first AC reading after a mode change
    # can take several seconds on AUTO range.
    SLOW_MODES = {"vac", "iac", "cap", "freq", "per"}

    def read_after(configure, name):
        configure()
        saved = dmm.instrument.timeout
        if name in SLOW_MODES:
            dmm.instrument.timeout = 15000
        try:
            v = dmm.read()
        finally:
            dmm.instrument.timeout = saved
        if not isinstance(v, float):
            raise AssertionError(f"{name} read returned {type(v).__name__}, not float")
        if math.isnan(v):
            raise AssertionError(f"{name} read NaN")
        print(f"     value: {v:g}")

    r.check("DC voltage configure+read", lambda: read_after(lambda: dmm.configure_dc_voltage("AUTO", "DEF"), "vdc"))
    r.check("AC voltage configure+read", lambda: read_after(lambda: dmm.configure_ac_voltage("AUTO", "DEF"), "vac"))
    r.check("DC current configure+read", lambda: read_after(lambda: dmm.configure_dc_current("AUTO", "DEF"), "idc"))
    r.check("AC current configure+read", lambda: read_after(lambda: dmm.configure_ac_current("AUTO", "DEF"), "iac"))
    r.check(
        "Resistance 2W configure+read", lambda: read_after(lambda: dmm.configure_resistance_2wire("AUTO", "DEF"), "res")
    )
    r.check(
        "Resistance 4W configure+read",
        lambda: read_after(lambda: dmm.configure_resistance_4wire("AUTO", "DEF"), "fres"),
    )
    r.check("Frequency configure+read", lambda: read_after(lambda: dmm.configure_frequency("AUTO", "DEF"), "freq"))
    r.check("Period configure+read", lambda: read_after(lambda: dmm.configure_period("AUTO", "DEF"), "per"))
    r.check("Continuity configure+read", lambda: read_after(dmm.configure_continuity, "cont"))
    r.check("Diode configure+read", lambda: read_after(dmm.configure_diode, "diode"))
    r.check("Capacitance configure+read", lambda: read_after(lambda: dmm.configure_capacitance("AUTO"), "cap"))
    r.check("Temperature configure+read", lambda: read_after(dmm.configure_temperature, "temp"))

    # Dedicated MEASure helpers
    r.check("measure_dc_voltage()", lambda: dmm.measure_dc_voltage())
    r.check("measure_dc_current()", lambda: dmm.measure_dc_current())
    r.check("measure_resistance_2wire()", lambda: dmm.measure_resistance_2wire())
    r.check("measure_continuity()", lambda: dmm.measure_continuity())
    r.check("measure_diode()", lambda: dmm.measure_diode())
    r.check("measure_capacitance()", lambda: dmm.measure_capacitance())

    # set_mode dispatch (friendly names)
    for friendly in ["vdc", "vac", "idc", "iac", "res", "fres", "freq", "per", "cont", "diode", "cap", "temp"]:
        r.check(f"set_mode('{friendly}')", lambda f=friendly: dmm.set_mode(f))

    # Trigger configuration & multi-sample fetch
    dmm.set_mode("vdc")
    r.check("set_trigger_source IMM", lambda: dmm.set_trigger_source("IMM"))
    r.check("set_trigger_delay 0", lambda: dmm.set_trigger_delay(0))
    r.check("set_sample_count 5", lambda: dmm.set_sample_count(5))
    # Per EDU34450A Programmer's Reference: after explicit INITiate the
    # correct readout is FETCh? (READ? = INITiate+FETCh and re-INITiating
    # while INIT'd raises -410 "Query INTERRUPTED"). Drivers map READ→read()
    # and FETCh→fetch() — this test must use fetch().
    # 5 samples on AUTO range need a longer timeout than the 5s default.
    def _init_fetch_5():
        saved = dmm.instrument.timeout
        dmm.instrument.timeout = 30000
        try:
            dmm.init()
            v = dmm.fetch()
        finally:
            dmm.instrument.timeout = saved
        if not isinstance(v, float):
            raise AssertionError("not float")

    r.check("init + fetch averaged 5-sample", _init_fetch_5)
    r.check("set_sample_count back to 1", lambda: dmm.set_sample_count(1))

    # Display / beeper
    r.check("display_text 'HELLO'", lambda: dmm.display_text("HELLO"))
    r.check("clear_display_text", dmm.clear_display_text)
    r.check("set_beeper OFF", lambda: dmm.set_beeper(False))
    r.check("set_beeper ON", lambda: dmm.set_beeper(True))
    r.check("set_display ON", lambda: dmm.set_display(True))

    # Input validation
    r.check("set_mode invalid", lambda: expect_value_error(dmm.set_mode, "bogus"))
    r.check("set_trigger_source invalid", lambda: expect_value_error(dmm.set_trigger_source, "bogus"))

    # Drain error queue
    drain_errors("DMM", dmm.get_error)

    return r


# ----------------------------------------------------------------------
# Scope: Keysight DSOX1204G
# ----------------------------------------------------------------------
def test_scope(scope) -> Recorder:
    r = Recorder("Scope DSOX1204G")
    print(f"\n=== {r.label} @ {scope.resource_name} ===")

    scope.clear_status()

    # On firmware <= 02.12 long write bursts can wedge the USB-TMC parser; a
    # USBTMC clear() at section boundaries mirrors how a real user paces work
    # and prevents state from accumulating across 130+ rapid SCPI commands.
    import contextlib

    def _settle(label):
        with contextlib.suppress(Exception):
            scope.instrument.clear()
        time.sleep(0.05)
        scope.instrument.write("*CLS")
        time.sleep(0.02)
        print(f"     -- settle before {label}")

    # Make sure WGEN is OFF before we touch anything.
    r.check("WGEN output OFF (pre)", lambda: scope.awg_set_output_enable(False))

    # ---- Channel configuration ----
    for ch in (1, 2, 3, 4):
        r.check(f"enable CH{ch}", lambda c=ch: scope.enable_channel(c))
        r.check(f"set_vertical_scale CH{ch} 1V/div", lambda c=ch: scope.set_vertical_scale(c, 1.0, 0.0))
        r.check(f"set_vertical_position CH{ch} 0.5V", lambda c=ch: scope.set_vertical_position(c, 0.5))
        r.check(
            f"get_vertical_position CH{ch} round-trip",
            lambda c=ch: (
                (got := scope.get_vertical_position(c)),
                None if approx(got, 0.5, abs_=0.05) else (_ for _ in ()).throw(AssertionError(f"got {got}")),
            ),
        )
        r.check(f"move_vertical CH{ch} +0.1", lambda c=ch: scope.move_vertical(c, 0.1))
        r.check(f"set_coupling CH{ch} DC", lambda c=ch: scope.set_coupling(c, "DC"))
        r.check(f"set_coupling CH{ch} AC", lambda c=ch: scope.set_coupling(c, "AC"))
        r.check(f"set_probe_attenuation CH{ch} 10x", lambda c=ch: scope.set_probe_attenuation(c, 10))
        r.check(f"set_probe_attenuation CH{ch} 1x", lambda c=ch: scope.set_probe_attenuation(c, 1))
        r.check(f"set_bandwidth_limit CH{ch} 20M", lambda c=ch: scope.set_bandwidth_limit(c, "20M"))
        r.check(f"set_bandwidth_limit CH{ch} OFF", lambda c=ch: scope.set_bandwidth_limit(c, "OFF"))
        r.check(f"invert CH{ch} ON", lambda c=ch: scope.invert_channel(c, True))
        r.check(f"invert CH{ch} OFF", lambda c=ch: scope.invert_channel(c, False))
        r.check(f"set_channel_label CH{ch}", lambda c=ch: scope.set_channel_label(c, f"L{c}"))
        r.check(f"set_channel_units CH{ch} VOLT", lambda c=ch: scope.set_channel_units(c, "VOLT"))
        r.check(
            f"get_channel_units CH{ch}",
            lambda c=ch: (
                (got := scope.get_channel_units(c)),
                None if "VOLT" in got.upper() else (_ for _ in ()).throw(AssertionError(f"got {got}")),
            ),
        )

    # Coupling/bandwidth validation
    r.check("set_coupling rejects GND", lambda: expect_value_error(scope.set_coupling, 1, "GND"))
    r.check("set_coupling rejects bogus", lambda: expect_value_error(scope.set_coupling, 1, "BOGUS"))
    r.check("set_bandwidth_limit rejects bogus", lambda: expect_value_error(scope.set_bandwidth_limit, 1, "BOGUS"))
    r.check("set_vertical_scale rejects bad ch", lambda: expect_value_error(scope.set_vertical_scale, 5, 1.0))

    # ---- Horizontal ----
    r.check("set_horizontal_scale 1ms/div", lambda: scope.set_horizontal_scale(1e-3))
    r.check("set_horizontal_offset 0", lambda: scope.set_horizontal_offset(0.0))
    r.check(
        "get_horizontal_offset round-trip",
        lambda: (
            (got := scope.get_horizontal_offset()),
            None if approx(got, 0.0, abs_=1e-6) else (_ for _ in ()).throw(AssertionError(f"got {got}")),
        ),
    )
    r.check("move_horizontal +1ms", lambda: scope.move_horizontal(1e-3))
    r.check("set_timebase_mode MAIN", lambda: scope.set_timebase_mode("MAIN"))
    r.check(
        "get_timebase_mode round-trip MAIN",
        lambda: (
            (got := scope.get_timebase_mode()),
            None if "MAIN" in got.upper() else (_ for _ in ()).throw(AssertionError(f"got {got}")),
        ),
    )
    r.check("set_timebase_reference CENTER", lambda: scope.set_timebase_reference("CENTER"))
    r.check("set_timebase_mode rejects bogus", lambda: expect_value_error(scope.set_timebase_mode, "BOGUS"))

    # ---- Trigger ----
    r.check("configure_trigger CH1 0V RISE AUTO", lambda: scope.configure_trigger(1, 0.0, "RISE", "AUTO"))
    r.check("set_trigger_sweep AUTO", lambda: scope.set_trigger_sweep("AUTO"))
    r.check("set_trigger_sweep NORMAL", lambda: scope.set_trigger_sweep("NORMAL"))
    r.check("set_trigger_holdoff 1us", lambda: scope.set_trigger_holdoff(1e-6))
    r.check(
        "get_trigger_holdoff round-trip",
        lambda: (
            (got := scope.get_trigger_holdoff()),
            None if approx(got, 1e-6, rel=0.5, abs_=1e-7) else (_ for _ in ()).throw(AssertionError(f"got {got}")),
        ),
    )
    r.check("set_trigger_holdoff rejects <60ns", lambda: expect_value_error(scope.set_trigger_holdoff, 1e-9))
    r.check("set_trigger_noise_reject ON", lambda: scope.set_trigger_noise_reject(True))
    r.check("set_trigger_noise_reject OFF", lambda: scope.set_trigger_noise_reject(False))
    r.check("set_trigger_hf_reject ON", lambda: scope.set_trigger_hf_reject(True))
    r.check("set_trigger_hf_reject OFF", lambda: scope.set_trigger_hf_reject(False))
    r.check("set_trigger_coupling DC", lambda: scope.set_trigger_coupling("DC"))
    r.check("set_trigger_coupling AC", lambda: scope.set_trigger_coupling("AC"))
    r.check("set_trigger_coupling LFREJECT", lambda: scope.set_trigger_coupling("LFREJECT"))
    r.check("set_trigger_coupling rejects bogus", lambda: expect_value_error(scope.set_trigger_coupling, "BOGUS"))
    r.check(
        "get_trigger_status",
        lambda: (
            s := scope.get_trigger_status(),
            None if s in ("RUN", "TD") else (_ for _ in ()).throw(AssertionError(f"got {s}")),
        ),
    )

    # ---- Acquisition ----
    r.check("set_acquisition_type NORMAL", lambda: scope.set_acquisition_type("NORMAL"))
    r.check("set_acquisition_type AVERAGE", lambda: scope.set_acquisition_type("AVERAGE"))
    r.check("set_average_count 4", lambda: scope.set_average_count(4))
    r.check("set_acquisition_type HRESOLUTION", lambda: scope.set_acquisition_type("HRESOLUTION"))
    r.check("set_acquisition_type PEAK", lambda: scope.set_acquisition_type("PEAK"))
    r.check("set_acquisition_type back to NORMAL", lambda: scope.set_acquisition_type("NORMAL"))
    r.check("set_acquisition_type rejects bogus", lambda: expect_value_error(scope.set_acquisition_type, "BOGUS"))
    r.check(
        "get_sample_rate > 0",
        lambda: (
            (sr := scope.get_sample_rate()),
            None if sr > 0 else (_ for _ in ()).throw(AssertionError(f"sr={sr}")),
        ),
    )
    r.check("set_acquisition_mode RTIM", lambda: scope.set_acquisition_mode("RTIM"))
    r.check("set_acquisition_mode rejects bogus", lambda: expect_value_error(scope.set_acquisition_mode, "BOGUS"))

    # ---- Run/Stop/Single ----
    r.check("run", scope.run)
    r.check("stop", scope.stop)
    r.check("single", scope.single)
    r.check("force_trigger", scope.force_trigger)
    r.check("run again", scope.run)

    # ---- Math ----
    r.check("enable_math_channel", lambda: scope.enable_math_channel(1, True))
    r.check("configure_math_operation ADD CH1+CH2", lambda: scope.configure_math_operation(1, "ADD", "CHAN1", "CHAN2"))
    r.check(
        "configure_math_operation MULTIPLY", lambda: scope.configure_math_operation(1, "MULTIPLY", "CHAN1", "CHAN2")
    )
    r.check("configure_fft on CH1", lambda: scope.configure_fft(1, "CHAN1", "HANN"))
    r.check("set_math_scale 1V/div", lambda: scope.set_math_scale(1, 1.0, 0.0))
    r.check("disable_math_channel", lambda: scope.enable_math_channel(1, False))

    # ---- Mask ----
    r.check("set_mask_source CH1", lambda: scope.set_mask_source(1))
    r.check(
        "get_mask_source",
        lambda: (
            (s := scope.get_mask_source()),
            None if "CHAN" in s.upper() else (_ for _ in ()).throw(AssertionError(f"got {s}")),
        ),
    )
    r.check("set_mask_tolerance_x 0.1", lambda: scope.set_mask_tolerance_x(0.1))
    r.check("set_mask_tolerance_y 0.1", lambda: scope.set_mask_tolerance_y(0.1))
    r.check(
        "get_mask_enable returns bool",
        lambda: (
            (e := scope.get_mask_enable()),
            None if isinstance(e, bool) else (_ for _ in ()).throw(AssertionError(f"got {type(e).__name__}")),
        ),
    )

    # ---- Cursors ----
    _settle("Cursors")
    r.check("set_cursor_mode MANual", lambda: scope.set_cursor_mode("MANual"))
    r.check("set_cursor_source CH1", lambda: scope.set_cursor_source(1))
    r.check(
        "set_manual_cursor_positions full",
        lambda: scope.set_manual_cursor_positions(x1=-1e-3, x2=1e-3, y1=-0.5, y2=0.5),
    )
    r.check(
        "get_manual_cursor_values",
        lambda: (
            (d := scope.get_manual_cursor_values()),
            None
            if set(d.keys()) >= {"x1", "x2", "y1", "y2", "dx", "dy"}
            else (_ for _ in ()).throw(AssertionError(f"keys={list(d.keys())}")),
        ),
    )
    r.check("set_cursor_mode rejects bogus", lambda: expect_value_error(scope.set_cursor_mode, "BOGUS"))
    r.check("set_cursor_mode OFF", lambda: scope.set_cursor_mode("OFF"))

    # ---- Measurements (whatever's on inputs) ----
    _settle("Measurements")
    for mt in [
        "vpp",
        "vrms",
        "vmax",
        "vmin",
        "frequency",
        "period",
        "rise",
        "fall",
        "pwidth",
        "nwidth",
        "duty",
        "overshoot",
        "preshoot",
        "mean",
        "amplitude",
    ]:
        r.check(
            f"measure CH1 {mt}",
            lambda m=mt: (
                (v := scope.measure(1, m)),
                None if isinstance(v, float) else (_ for _ in ()).throw(AssertionError(f"not float: {v}")),
            ),
        )

    r.check("clear_measurements", scope.clear_measurements)
    r.check("set_measurement_statistics ON", lambda: scope.set_measurement_statistics(True))
    r.check("get_measurement_results", lambda: scope.get_measurement_results())
    r.check("reset_measurement_statistics", scope.reset_measurement_statistics)
    r.check("set_measurement_statistics OFF", lambda: scope.set_measurement_statistics(False))

    # ---- Display ----
    _settle("Display")
    r.check("set_waveform_brightness 50", lambda: scope.set_waveform_brightness(50))
    r.check("set_waveform_brightness rejects 0", lambda: expect_value_error(scope.set_waveform_brightness, 0))
    r.check("set_waveform_brightness rejects 200", lambda: expect_value_error(scope.set_waveform_brightness, 200))
    r.check("set_persistence MIN", lambda: scope.set_persistence("MIN"))
    r.check("set_display_vectors ON", lambda: scope.set_display_vectors(True))
    r.check("set_display_annotation 'TEST'", lambda: scope.set_display_annotation("TEST"))
    r.check("clear_display_annotation", scope.clear_display_annotation)
    r.check("set_system_message 'hi'", lambda: scope.set_system_message("hi"))
    r.check("set_system_message ''", lambda: scope.set_system_message(""))

    # ---- Screenshot (small but real binary transfer) ----
    _settle("Screenshot")
    r.check(
        "get_screenshot returns bytes",
        lambda: (
            (b := scope.get_screenshot()),
            None
            if isinstance(b, bytes) and len(b) > 100
            else (_ for _ in ()).throw(AssertionError(f"len={len(b) if hasattr(b, '__len__') else '?'}")),
        ),
    )

    # ---- Waveform acquisition ----
    _settle("Waveform")
    # Earlier trigger section left sweep in NORMAL — :DIGitize would wait
    # forever for a trigger that never fires on an open input. Force AUTO so
    # :DIGitize completes promptly regardless of input signal.
    scope.set_trigger_sweep("AUTO")
    r.check(
        "acquire_waveform CH1",
        lambda: (
            (w := scope.acquire_waveform(1, "NORMAL")),
            None if len(w) > 0 else (_ for _ in ()).throw(AssertionError("empty")),
        ),
    )

    # ---- AWG (configure but DO NOT enable output) ----
    _settle("WGEN")
    r.check("awg_set_output_enable OFF (pre-config)", lambda: scope.awg_set_output_enable(False))
    r.check("awg_set_function SINusoid", lambda: scope.awg_set_function("SINusoid"))
    r.check("awg_set_frequency 1kHz", lambda: scope.awg_set_frequency(1000.0))
    r.check("awg_set_amplitude 1Vpp", lambda: scope.awg_set_amplitude(1.0))
    r.check("awg_set_offset 0V", lambda: scope.awg_set_offset(0.0))
    r.check("awg_set_function rejects bogus", lambda: expect_value_error(scope.awg_set_function, "BOGUS"))
    r.check("awg_set_function SQUare", lambda: scope.awg_set_function("SQUare"))
    r.check("awg_set_square_duty 25", lambda: scope.awg_set_square_duty(25))
    r.check("awg_set_function RAMP", lambda: scope.awg_set_function("RAMP"))
    r.check("awg_set_ramp_symmetry 50", lambda: scope.awg_set_ramp_symmetry(50))
    r.check("awg_set_function PULSe", lambda: scope.awg_set_function("PULSe"))
    r.check("awg_set_pulse_width 100us", lambda: scope.awg_set_pulse_width(100e-6))
    r.check("awg_set_pulse_width rejects 0", lambda: expect_value_error(scope.awg_set_pulse_width, 0))
    r.check("awg_set_modulation_type AM", lambda: scope.awg_set_modulation_type("AM"))
    r.check("awg_set_modulation_type rejects bogus", lambda: expect_value_error(scope.awg_set_modulation_type, "BOGUS"))
    r.check("awg_set_modulation_enable OFF", lambda: scope.awg_set_modulation_enable(False))

    # Confirm WGEN output is still OFF
    r.check(
        "WGEN output still OFF",
        lambda: (
            (s := scope.instrument.query(":WGEN:OUTPut?").strip()),
            None if s == "0" else (_ for _ in ()).throw(AssertionError(f":WGEN:OUTPut?={s}")),
        ),
    )

    # ---- DVM ----
    _settle("DVM")
    r.check("set_dvm_source CH1", lambda: scope.set_dvm_source(1))
    r.check("set_dvm_mode DC", lambda: scope.set_dvm_mode("DC"))
    r.check("set_dvm_enable ON", lambda: scope.set_dvm_enable(True))
    r.check(
        "get_dvm_current returns float",
        lambda: (
            (v := scope.get_dvm_current()),
            None if isinstance(v, float) else (_ for _ in ()).throw(AssertionError(f"not float: {v}")),
        ),
    )
    r.check("set_dvm_enable OFF", lambda: scope.set_dvm_enable(False))

    # ---- Self-test (long; runs at the end so a failure won't tank the rest) ----
    _settle("self-test")
    r.check(
        "self_test returns int (0 == pass)",
        lambda: (
            (rc := scope.self_test()),
            None if isinstance(rc, int) else (_ for _ in ()).throw(AssertionError(f"got {type(rc).__name__}")),
        ),
    )

    drain_errors("Scope", scope.get_error)

    return r


# ----------------------------------------------------------------------
# AWG: Keysight EDU33212A
# ----------------------------------------------------------------------
def test_awg(awg) -> Recorder:
    r = Recorder("AWG EDU33212A")
    print(f"\n=== {r.label} @ {awg.resource_name} ===")

    awg.clear_status()

    # SAFETY: verify both outputs are OFF before doing anything else.
    out1 = awg.get_output_state(1)
    out2 = awg.get_output_state(2)
    if out1 or out2:
        print(
            f"  !! ABORT: AWG outputs are ON (CH1={out1}, CH2={out2}). "
            "Disable manually or unplug DUT before re-running."
        )
        r.failed += 1
        r.errors.append(("safety check", f"outputs already ON ch1={out1} ch2={out2}"))
        return r
    r.passed += 1
    print("  [PASS] both AWG channels confirmed OFF")

    # Now safe to put into known state.
    r.check("disable_all_channels (force known state)", awg.disable_all_channels)

    # Per-channel: function, frequency, amplitude, offset round-trip; outputs stay OFF.
    for ch in (1, 2):
        for func in ("SIN", "SQU", "RAMP", "PULS", "NOIS", "DC"):
            r.check(f"CH{ch} set_function {func}", lambda c=ch, f=func: awg.set_function(c, f))

        # Pick SIN for parameter round-trips (frequency only meaningful for non-DC/NOIS)
        r.check(f"CH{ch} set_function SIN", lambda c=ch: awg.set_function(c, "SIN"))
        r.check(f"CH{ch} set_frequency 1234.5 Hz", lambda c=ch: awg.set_frequency(c, 1234.5))
        r.check(
            f"CH{ch} get_frequency round-trip",
            lambda c=ch: (
                (got := awg.get_frequency(c)),
                None if approx(got, 1234.5, rel=1e-4) else (_ for _ in ()).throw(AssertionError(f"got {got}")),
            ),
        )
        r.check(f"CH{ch} set_amplitude 0.5 Vpp", lambda c=ch: awg.set_amplitude(c, 0.5))
        r.check(
            f"CH{ch} get_amplitude round-trip",
            lambda c=ch: (
                (got := awg.get_amplitude(c)),
                None if approx(got, 0.5, abs_=1e-3) else (_ for _ in ()).throw(AssertionError(f"got {got}")),
            ),
        )
        r.check(f"CH{ch} set_offset 0.1 V", lambda c=ch: awg.set_offset(c, 0.1))
        r.check(
            f"CH{ch} get_offset round-trip",
            lambda c=ch: (
                (got := awg.get_offset(c)),
                None if approx(got, 0.1, abs_=1e-3) else (_ for _ in ()).throw(AssertionError(f"got {got}")),
            ),
        )

        # set_high_low + set_voltage_unit
        r.check(f"CH{ch} set_high_low(1.0, -1.0)", lambda c=ch: awg.set_high_low(c, 1.0, -1.0))
        r.check(f"CH{ch} set_voltage_unit VPP", lambda c=ch: awg.set_voltage_unit(c, "VPP"))
        r.check(f"CH{ch} set_voltage_unit VRMS", lambda c=ch: awg.set_voltage_unit(c, "VRMS"))
        r.check(f"CH{ch} set_voltage_unit DBM", lambda c=ch: awg.set_voltage_unit(c, "DBM"))
        r.check(f"CH{ch} set_voltage_unit invalid", lambda c=ch: expect_value_error(awg.set_voltage_unit, c, "BOGUS"))
        r.check(f"CH{ch} restore VPP", lambda c=ch: awg.set_voltage_unit(c, "VPP"))

        # Output load
        r.check(f"CH{ch} set_output_load 50", lambda c=ch: awg.set_output_load(c, 50))
        r.check(f"CH{ch} set_output_load INF", lambda c=ch: awg.set_output_load(c, "INF"))
        r.check(f"CH{ch} set_output_load back to 50", lambda c=ch: awg.set_output_load(c, 50))
        r.check(f"CH{ch} set_output_polarity NORMal", lambda c=ch: awg.set_output_polarity(c, True))
        r.check(f"CH{ch} set_output_polarity INVerted", lambda c=ch: awg.set_output_polarity(c, False))
        r.check(f"CH{ch} restore polarity NORMal", lambda c=ch: awg.set_output_polarity(c, True))

        # Square / ramp / pulse params
        r.check(f"CH{ch} set_function SQU", lambda c=ch: awg.set_function(c, "SQU"))
        r.check(f"CH{ch} set_square_duty 25", lambda c=ch: awg.set_square_duty(c, 25))
        r.check(f"CH{ch} set_function RAMP", lambda c=ch: awg.set_function(c, "RAMP"))
        r.check(f"CH{ch} set_ramp_symmetry 50", lambda c=ch: awg.set_ramp_symmetry(c, 50))
        r.check(f"CH{ch} set_function PULS", lambda c=ch: awg.set_function(c, "PULS"))
        r.check(f"CH{ch} set_pulse_period 1ms", lambda c=ch: awg.set_pulse_period(c, 1e-3))
        r.check(f"CH{ch} set_pulse_width 100us", lambda c=ch: awg.set_pulse_width(c, 100e-6))
        r.check(f"CH{ch} set_pulse_duty 30", lambda c=ch: awg.set_pulse_duty(c, 30))
        r.check(f"CH{ch} set_pulse_edge 10ns/10ns", lambda c=ch: awg.set_pulse_edge(c, leading=10e-9, trailing=10e-9))

        # Convenience method
        r.check(
            f"CH{ch} set_waveform SIN 1kHz 1Vpp",
            lambda c=ch: awg.set_waveform(c, "SIN", frequency=1000, amplitude=1.0, offset=0.0),
        )

        # Modulation (configure but state OFF, so output is unaffected)
        r.check(f"CH{ch} set_am(state=False)", lambda c=ch: awg.set_am(c, False))
        r.check(f"CH{ch} set_am(state=True, INTernal)", lambda c=ch: awg.set_am(c, True, depth=50, mod_freq=100))
        r.check(f"CH{ch} disable AM", lambda c=ch: awg.set_am(c, False))
        r.check(f"CH{ch} set_fm(state=True)", lambda c=ch: awg.set_fm(c, True, deviation=50, mod_freq=100))
        r.check(f"CH{ch} disable FM", lambda c=ch: awg.set_fm(c, False))
        r.check(f"CH{ch} set_pm(state=True)", lambda c=ch: awg.set_pm(c, True, deviation=90, mod_freq=100))
        r.check(f"CH{ch} disable PM", lambda c=ch: awg.set_pm(c, False))
        r.check(f"CH{ch} set_fsk(state=True)", lambda c=ch: awg.set_fsk(c, True, hop_freq=200, rate=10))
        r.check(f"CH{ch} disable FSK", lambda c=ch: awg.set_fsk(c, False))
        # PWM requires PULS carrier
        r.check(f"CH{ch} set_function PULS (for PWM)", lambda c=ch: awg.set_function(c, "PULS"))
        r.check(f"CH{ch} set_pwm(state=True)", lambda c=ch: awg.set_pwm(c, True, mod_freq=100))
        r.check(f"CH{ch} disable PWM", lambda c=ch: awg.set_pwm(c, False))

        # Sweep / burst (configure but enabling sweep does NOT enable output channel)
        r.check(f"CH{ch} set_sweep(True)", lambda c=ch: awg.set_sweep(c, True, start=100, stop=1000, time=0.1))
        r.check(f"CH{ch} set_sweep(False)", lambda c=ch: awg.set_sweep(c, False))
        r.check(f"CH{ch} set_burst(True)", lambda c=ch: awg.set_burst(c, True, n_cycles=3, period=0.01))
        r.check(f"CH{ch} set_burst(False)", lambda c=ch: awg.set_burst(c, False))

        # Trigger
        r.check(f"CH{ch} set_trigger_source IMM", lambda c=ch: awg.set_trigger_source(c, "IMMediate"))
        r.check(f"CH{ch} set_trigger_source BUS", lambda c=ch: awg.set_trigger_source(c, "BUS"))
        r.check(f"CH{ch} set_trigger_source IMM (restore)", lambda c=ch: awg.set_trigger_source(c, "IMMediate"))

    # send_trigger (no harm; bus trigger has no addressed channel here)
    r.check("send_trigger", awg.send_trigger)

    # Sync output
    r.check("set_sync_output ON", lambda: awg.set_sync_output(True))
    r.check("set_sync_output OFF", lambda: awg.set_sync_output(False))

    # State save / recall (slot 1)
    r.check("save_state slot 1", lambda: awg.save_state(1))
    r.check("recall_state slot 1", lambda: awg.recall_state(1))
    r.check("save_state rejects 5", lambda: expect_value_error(awg.save_state, 5))
    r.check("recall_state rejects 5", lambda: expect_value_error(awg.recall_state, 5))

    # Validation errors
    r.check("set_function rejects bogus", lambda: expect_value_error(awg.set_function, 1, "BOGUS"))
    r.check("set_function rejects bad ch", lambda: expect_value_error(awg.set_function, 5, "SIN"))
    r.check("set_frequency rejects bad ch", lambda: expect_value_error(awg.set_frequency, 0, 1000))
    r.check("set_waveform rejects bogus type", lambda: expect_value_error(awg.set_waveform, 1, "BOGUS"))
    r.check("enable_output rejects bad ch", lambda: expect_value_error(awg.enable_output, 9, False))

    # Final: verify both outputs still OFF and quiesce.
    r.check(
        "CH1 output still OFF",
        lambda: (None if awg.get_output_state(1) is False else (_ for _ in ()).throw(AssertionError("CH1 became ON")),),
    )
    r.check(
        "CH2 output still OFF",
        lambda: (None if awg.get_output_state(2) is False else (_ for _ in ()).throw(AssertionError("CH2 became ON")),),
    )
    r.check("disable_all_channels (final)", awg.disable_all_channels)

    drain_errors("AWG", awg.get_error)
    return r


# ----------------------------------------------------------------------
# Driver
# ----------------------------------------------------------------------
def main() -> int:
    print("Scanning for instruments...")
    devs = InstrumentDiscovery().scan(verbose=False)
    print(f"Found: {sorted(devs.keys())}")

    recorders: list[Recorder] = []

    if "psu" in devs:
        recorders.append(test_psu(devs["psu"]))
    if "dmm" in devs:
        recorders.append(test_dmm(devs["dmm"]))
    if "scope" in devs:
        recorders.append(test_scope(devs["scope"]))
    if "awg" in devs:
        recorders.append(test_awg(devs["awg"]))

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    total_pass, total_fail = 0, 0
    for r in recorders:
        print(f"  {r.summary()}")
        total_pass += r.passed
        total_fail += r.failed

    print(f"\nTotal: {total_pass} passed, {total_fail} failed/errored")

    if total_fail:
        print("\nFAILURES / ERRORS:")
        for r in recorders:
            for name, msg in r.errors:
                print(f"  [{r.label}] {name}: {msg.splitlines()[0]}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
