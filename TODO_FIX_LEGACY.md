# Legacy Code Inventory

This document catalogues all legacy code, backward-compatibility shims, deprecated
syntax, and compatibility stubs found in the codebase. Each entry includes the
file, line numbers, a description of the issue, and a suggested remediation.

---

## 1. Deprecated `set` Variable Assignment Syntax

**Files:**
- `lab_instruments/repl/commands/variables.py:335-353`
- `docs/scripting.md` (lines 507-515)

**Description:**
The old `set varname expr` syntax for variable assignment is deprecated in favor of
`varname = value`. The `do_set` handler now rejects variable assignment attempts
with an error message, but the command still exists to handle `-e`/`+e` flags and
to display current variables.

**Suggested fix:**
Once all users/scripts have migrated to `var = expr`, remove the `do_set` method
entirely and move `-e`/`+e` handling to a dedicated command (e.g., `error-mode`).

---

## 2. Legacy `input` Command

**File:** `lab_instruments/repl/commands/variables.py:63-65`

**Description:**
The `do_input` method is a stub for the old `input varname prompt` syntax. It only
prints an error directing users to the new `varname = input [prompt]` form.

**Suggested fix:**
Remove `do_input` once the deprecation period is over. It provides no functionality
beyond an error message.

---

## 3. Legacy PSU Channel Protocol (`CHANNEL_MAP`)

**File:** `lab_instruments/repl/commands/psu.py:12-40`

**Description:**
The `_resolve_channel` function supports two channel resolution protocols:
1. **New:** `CHANNEL_FROM_NUMBER` (enum-based)
2. **Legacy:** `CHANNEL_MAP` (positional string keys)

The legacy path uses `getattr(dev, "CHANNEL_MAP", {})` to fall back to the old
string-based protocol when the new enum-based protocol is not available.

**Suggested fix:**
Migrate all PSU drivers to use `CHANNEL_FROM_NUMBER`. Once complete, remove the
`CHANNEL_MAP` fallback branch from `_resolve_channel`.

---

## 4. Backward-Compatibility Properties on `InstrumentREPL`

**File:** `lab_instruments/repl/shell.py:156-293`

**Description:**
After refactoring state into `ReplContext`, a large block of backward-compatibility
properties was added to `InstrumentREPL` so that external code (and tests) could
continue accessing state directly on the shell object. These include:

| Property | Delegates to |
|---|---|
| `devices` / `devices.setter` | `ctx.registry.devices` |
| `selected` / `selected.setter` | `ctx.registry.selected` |
| `measurements` / `measurements.setter` | `ctx.measurements.entries` |
| `_script_vars` / setter | `ctx.script_vars` |
| `_command_had_error` / setter | `ctx.command_had_error` |
| `_exit_on_error` / setter | `ctx.exit_on_error` |
| `_in_script` / setter | `ctx.in_script` |
| `_in_debugger` / setter | `ctx.in_debugger` |
| `_interrupt_requested` / setter | `ctx.interrupt_requested` |
| `_safety_limits` / setter | `ctx.safety_limits` |
| `_awg_channel_state` / setter | `ctx.awg_channel_state` |
| `scripts` / setter | `ctx.scripts` |
| `_record_script` / setter | `ctx.record_script` |
| `test_results` / setter | `ctx.test_results` |
| `_report_title` / setter | `ctx.report_title` |
| `_report_operator` / setter | `ctx.report_operator` |
| `_report_screenshots` / setter | `ctx.report_screenshots` |

**Suggested fix:**
Update all callers (including tests) to access `ctx` directly, then delete these
~140 lines of wrapper properties.

---

## 5. Backward-Compatibility Methods on `InstrumentREPL`

**File:** `lab_instruments/repl/shell.py:531-533, 940-1017`

**Description:**
Several methods exist solely as backward-compatibility wrappers:

- `_error(message)` (line 531) -- delegates to `ctx.error(message)`
- `_expand_script_lines(...)` (line 943) -- delegates to `expand_script_lines`
  from `script_engine.expander` (comment says "used by test_safety_limits.py")
- `_run_expanded(...)` (line 956) -- delegates to `run_expanded`
- `_run_script_lines(...)` (line 961) -- calls `_expand_script_lines` + `_run_expanded`
- `_record_measurement(...)` (line 965) -- delegates to `ctx.measurements.record`
- `_update_awg_state(...)` (line 968) -- delegates to `_safety.update_awg_state`
- `_check_psu_limits(...)` (line 971) -- delegates to `_safety.check_psu_limits`
- `_check_awg_limits(...)` (line 974) -- delegates to `_safety.check_awg_limits`
- `_check_psu_output_allowed(...)` (line 979) -- delegates to `_safety.check_psu_output_allowed`
- `_check_awg_output_allowed(...)` (line 982) -- delegates to `_safety.check_awg_output_allowed`
- `_retroactive_limit_check_all()` (line 985) -- delegates to `_safety.retroactive_limit_check_all`
- `_collect_limits(...)` (line 988) -- delegates to `_safety.collect_limits`
- `_query_awg_state(...)` (line 991) -- delegates to `_safety.query_awg_state`
- `_query_psu_state(...)` (line 994) -- delegates to `_safety.query_psu_state`
- `_data_dir_override` property (line 997) -- delegates to `ctx._data_dir_override`
- `_scripts_dir_override` property (line 1005) -- delegates to `ctx._scripts_dir_override`
- `_get_data_dir()` (line 1013) -- delegates to `ctx.get_data_dir()`
- `_get_scripts_dir()` (line 1016) -- delegates to `ctx.get_scripts_dir()`

**Suggested fix:**
Update callers (especially test files) to call through `ctx` or the `_safety`
subsystem directly, then remove these wrapper methods.

---

## 6. `MeasurementStore.entries` Backward-Compatibility Property

**File:** `lab_instruments/repl/measurement_store.py:45-48`

**Description:**
The `entries` property exposes the internal `_entries` list directly for backward
compatibility. The docstring explicitly says "for backward compat".

**Suggested fix:**
Audit callers. If all access goes through `MeasurementStore` methods, remove the
`entries` property and make `_entries` truly private.

---

## 7. `__LIVEPLOT__` Legacy Marker Protocol

**File:** `lab_instruments/repl/commands/plot.py:188-190`

**Description:**
When no GUI callback (`ctx.on_liveplot`) is registered, the liveplot command prints
a magic string `__LIVEPLOT__:...` to stdout. The GUI console widget
(`lab_instruments/gui/widgets/console.py:214`) parses this marker to intercept
liveplot requests.

This stdout-based signaling is fragile and is explicitly labeled "Fallback marker
for non-GUI / legacy usage".

**Suggested fix:**
Replace the magic-string protocol with a proper event/callback mechanism. The GUI
already uses `ctx.on_liveplot`; ensure all environments register a callback.

---

## 8. SCPI Compatibility Stubs on Non-SCPI Devices

### 8a. NI PXIe-4139

**File:** `lab_instruments/src/ni_pxie_4139.py:314-346`

**Description:**
The NI PXIe-4139 driver (which uses NI-DCPower, not SCPI) implements SCPI
compatibility stubs so it can be used with the REPL framework:

- `query(cmd)` -- returns a hardcoded IDN-like string
- `send_command(cmd)` -- no-op
- `get_error()` -- returns "not supported on NI_PXIe_4139"

### 8b. TI EV2300

**File:** `lab_instruments/src/ev2300.py:1044-1062`

**Description:**
The EV2300 driver (HID-based, not SCPI) also implements SCPI stubs:

- `query(cmd)` -- returns a hardcoded IDN-like string
- `send_command(cmd)` -- no-op
- `clear_status()` -- no-op

### 8c. EV2300 SMBusTransport Compatibility

**File:** `lab_instruments/src/ev2300.py:1064-1079`

**Description:**
Additional compatibility layer implementing `open_device()` and `close_device()`
methods to conform to the SMBusTransport protocol interface.

**Suggested fix:**
Define a formal `InstrumentProtocol` (abstract base class or `Protocol`) that all
drivers implement. This would replace ad-hoc stubs with explicit interface
contracts. Non-SCPI devices would implement the protocol natively rather than
faking SCPI methods.

---

## 9. Legacy REPL Architecture (Monolithic `repl.py`)

**File:** `CONTRIBUTING.md:85`

**Description:**
The contributing guide references the current REPL package as a "modular replacement
for old repl.py", indicating that the codebase was refactored from a monolithic
single-file REPL. The backward-compatibility properties and methods in
`InstrumentREPL` (items 4 and 5 above) are remnants of this refactor.

**Suggested fix:**
Complete the migration by removing all backward-compatibility shims once tests and
external consumers are updated. Update `CONTRIBUTING.md` to remove the "old repl.py"
reference.

---

## 10. Backward-Compatibility Test Suite

**File:** `tests/test_repl_modules.py:1986-2089`

**Description:**
A dedicated test class with ~20 tests exists solely to verify backward-compatibility
properties and methods on `InstrumentREPL`:

- `test_backward_compat_devices_property`
- `test_backward_compat_selected_property`
- `test_backward_compat_measurements_property`
- `test_backward_compat_script_vars`
- `test_backward_compat_error_flag`
- `test_backward_compat_exit_on_error`
- `test_backward_compat_in_script`
- `test_backward_compat_in_debugger`
- `test_backward_compat_interrupt_requested`
- `test_backward_compat_safety_limits`
- `test_backward_compat_awg_channel_state`
- `test_backward_compat_scripts`
- `test_backward_compat_record_script`
- `test_backward_compat_test_results`
- `test_backward_compat_report_title`
- `test_backward_compat_report_operator`
- `test_backward_compat_report_screenshots`
- `test_backward_compat_data_dir`
- `test_backward_compat_scripts_dir`
- `test_record_measurement_compat`
- `test_expand_script_lines_compat`
- `test_error_compat`
- `test_get_data_dir_compat`
- `test_get_scripts_dir_compat`

**Suggested fix:**
When the backward-compatibility layer (items 4 and 5) is removed, delete these
tests. Ensure equivalent coverage exists for the `ReplContext` and subsystem APIs
they delegate to.

---

## Summary

| # | Category | Location | Priority |
|---|---|---|---|
| 1 | Deprecated `set` syntax | `repl/commands/variables.py` | Low |
| 2 | Legacy `input` command | `repl/commands/variables.py` | Low |
| 3 | Legacy PSU channel protocol | `repl/commands/psu.py` | Medium |
| 4 | Backward-compat properties (~140 LOC) | `repl/shell.py` | High |
| 5 | Backward-compat methods (~80 LOC) | `repl/shell.py` | High |
| 6 | `MeasurementStore.entries` compat | `repl/measurement_store.py` | Low |
| 7 | `__LIVEPLOT__` magic string protocol | `repl/commands/plot.py` | Medium |
| 8 | SCPI stubs on non-SCPI devices | `src/ni_pxie_4139.py`, `src/ev2300.py` | Medium |
| 9 | Old monolithic REPL reference | `CONTRIBUTING.md` | Low |
| 10 | Backward-compat test suite | `tests/test_repl_modules.py` | High (depends on 4+5) |
