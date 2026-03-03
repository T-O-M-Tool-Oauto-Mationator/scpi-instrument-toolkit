# SCPI Driver Best-Practice Compliance Audit

Audit date: 2026-03-03
Baseline: 526 passing tests, 16 skipped (PDF report tests excluded — env issue)

## Per-Driver Violation Table

| Driver | BP-01 Interface | BP-02 write/query | BP-03 Ordering | BP-04 Cached | BP-05 Validation | BP-06 Context Mgr | BP-07 Timing | BP-08 Mock |
|--------|----------------|-------------------|----------------|-------------|------------------|-------------------|-------------|-----------|
| DeviceManager (base) | `write()` missing | OK | N/A | N/A | N/A | N/A | N/A | N/A |
| HP_E3631A | OK (inherits) | OK | OK | OK | OK | OK | N/A | N/A |
| HP_34401A | OK | OK | OK | OK | OK | OK | OK | N/A |
| BK_4063 | OK | OK | OK | OK | OK | OK | N/A | N/A |
| Keysight_EDU33212A | OK | OK | OK | OK | OK | OK | N/A | N/A |
| MATRIX_MPS6010H | OK | OK | OK | OK | OK | OK | N/A | N/A |
| Tektronix_MSO2024 | OK | OK | OK | OK | OK | OK | N/A | N/A |
| **JDS6600_Generator** | `get_error()` missing | OK | OK | OK | OK | **`__enter__`/`__exit__` missing** | OK | N/A |
| **Rigol_DHO804** | `get_error()` missing | OK | OK | N/A | OK | **`__enter__`/`__exit__` missing** | OK | N/A |
| **Owon_XDM1041** | OK | OK | OK | N/A | OK | **`__exit__` is no-op** | **time imported inside methods** | N/A |
| **MockBase** | `write()`/`get_error()` missing | N/A | N/A | N/A | N/A | N/A | N/A | **Yes** |
| **MockPSU** | N/A | N/A | N/A | **`measure_*()` hardcoded** | N/A | N/A | N/A | **Yes** |
| **MockMPS6010H** | N/A | N/A | N/A | N/A | **No validation** | N/A | N/A | **Yes** |
| **MockAWG** | N/A | N/A | N/A | **`set_waveform()` no-op** | N/A | N/A | N/A | **Yes** |

## Prioritized Fix Order

Fixes are ordered by dependency — base classes first, then leaves.

| Priority | Component | BP IDs | Severity | Est. Lines Changed |
|----------|-----------|--------|----------|-------------------|
| 1 | DeviceManager: add `write()` | BP-01 | Critical | +5 |
| 2 | MockBase: add `write()`, `get_error()` | BP-01, BP-08 | Critical | +8 |
| 2 | MockPSU: `measure_*()` track setpoint | BP-04, BP-08 | Critical | +6 |
| 2 | MockMPS6010H: input validation | BP-05, BP-08 | Minor | +18 |
| 2 | MockAWG: track waveform in `set_waveform()` | BP-08 | Minor | +4 |
| 3 | JDS6600: add `get_error()`, `__enter__`, `__exit__` | BP-01, BP-06 | Critical | +15 |
| 4 | Rigol_DHO804: add `get_error()`, `__enter__`, `__exit__` | BP-01, BP-06 | Critical | +15 |
| 5 | Owon_XDM1041: improve `__exit__`, move time import | BP-06, BP-07 | Minor | +5 / -3 |

## Items Not Changed (by design)

- HP_E3631A, BK_4063, Keysight_EDU33212A, Tektronix_MSO2024: already compliant
- No new numeric validation added to drivers with model-dependent ranges (HP_E3631A channel limits, BK_4063 amplitude) — deferred to avoid breaking existing workflows
- Rigol_DHO804's pattern of calling `self.instrument.write()` directly (156 sites): not refactored — works correctly and churn risk outweighs benefit
