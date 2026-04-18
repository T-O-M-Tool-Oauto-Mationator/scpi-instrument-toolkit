# Chapter 6: The SCPI Driver Contract

Every driver in the toolkit must follow these 8 rules. They exist because real bugs were caused when they were violated.

## Rule 1: Never Return Hardcoded Values from Getters

**Wrong:**

    def get_voltage_setpoint(self):
        return 5.0          # hardcoded!

**Right:**

    def get_voltage_setpoint(self):
        return self._voltage  # return cached state

**Why:** If a getter returns a constant, tests pass but the value never reflects what the instrument is actually doing. A student sets 3.3V and the getter still says 5.0V.

## Rule 2: Never Use "from time import sleep"

**Wrong:**

    from time import sleep
    sleep(0.5)

**Right:**

    import time
    time.sleep(0.5)

**Why:** Tests use `monkeypatch.setattr(module.time, "sleep", lambda _: None)` to skip delays. If you import `sleep` directly, the monkeypatch cannot intercept it and tests run slowly.

## Rule 3: Always Implement get_error()

**Wrong:** Omitting `get_error()` entirely.

**Right (if the instrument supports it):**

    def get_error(self):
        return self.query("SYST:ERR?")

**Right (if the instrument does not support it):**

    def get_error(self):
        return "0,not supported on MyNewInstrument"

**Why:** The REPL calls `get_error()` after failures to provide diagnostic information. If the method is missing, the REPL crashes with an AttributeError.

## Rule 4: Use query() for Reads, write() for Commands

**Wrong:**

    def measure_voltage(self):
        self.send_command("MEAS:VOLT?")    # write, not query!
        return float(self.instrument.read())

**Right:**

    def measure_voltage(self):
        return float(self.query("MEAS:VOLT?"))

**Why:** `query()` handles the write-then-read sequence atomically, including timeout handling and error checking. Splitting into separate write/read calls is error-prone.

## Rule 5: Validate Numeric Inputs

**Wrong:**

    def set_voltage(self, channel, voltage):
        self.send_command(f"VOLT {voltage}")    # no validation!

**Right:**

    def set_voltage(self, channel, voltage):
        if not 0 <= voltage <= 30.0:
            raise ValueError(f"Voltage {voltage} out of range [0, 30.0]")
        self.send_command(f"VOLT {voltage}")

**Why:** Without validation, students can accidentally send dangerous voltages to instruments, or send out-of-range values that cause SCPI errors that are hard to debug.

## Rule 6: Validate Enum Inputs Against an ALLOWLIST

**Wrong:**

    def set_mode(self, mode):
        self.send_command(f"MODE {mode}")    # accepts anything!

**Right:**

    MODES_ALLOWLIST = frozenset({"DC", "AC", "RES", "FREQ"})

    def set_mode(self, mode):
        mode = mode.upper()
        if mode not in self.MODES_ALLOWLIST:
            raise ValueError(f"Invalid mode '{mode}'. Allowed: {self.MODES_ALLOWLIST}")
        self.send_command(f"MODE {mode}")

**Why:** Typos in mode names (e.g., "DVC" instead of "VDC") silently fail on some instruments. The ALLOWLIST catches them immediately with a clear error message.

## Rule 7: Always Implement __enter__ / __exit__

**Wrong:** Omitting context manager methods.

**Right:**

    def __enter__(self):
        self.disable_all_channels()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.disable_all_channels()

**Why:** `__exit__` must fire even after exceptions. This ensures instruments are left in a safe state if a script crashes partway through. The `with` statement pattern depends on this.

## Rule 8: Update self._cache Atomically with Every write()

**Wrong:**

    def set_voltage(self, channel, voltage):
        self.send_command(f"VOLT {voltage}")
        # forgot to update cache!

**Right:**

    def set_voltage(self, channel, voltage):
        self.send_command(f"VOLT {voltage}")
        self._voltage = voltage    # update immediately after write

**Why:** Getters return cached values (Rule 1). If the cache is not updated after a write, subsequent reads return stale data. The atomic update ensures cache and hardware are always in sync.

## Checking Contract Compliance

Run the `@scpi-contract-reviewer` subagent before any PR that touches driver code:

<!-- doc-test: skip reason="Claude Code subagent @-handle, not Python syntax" -->

    @scpi-contract-reviewer

This read-only reviewer checks all 8 rules and reports violations without modifying files.

## Summary Table

| # | Rule | Prevents |
|---|------|----------|
| 1 | No hardcoded getters | Stale/wrong data in tests and REPL |
| 2 | No `from time import sleep` | Slow tests (monkeypatch cannot intercept) |
| 3 | Always implement get_error() | AttributeError crashes in error handling |
| 4 | Use query() for reads | Race conditions, missed responses |
| 5 | Validate numeric inputs | Dangerous voltages, cryptic SCPI errors |
| 6 | Validate enum inputs | Silent failures from typos |
| 7 | Implement __enter__/__exit__ | Unsafe instrument state after crashes |
| 8 | Update cache atomically | Stale cached values after writes |
