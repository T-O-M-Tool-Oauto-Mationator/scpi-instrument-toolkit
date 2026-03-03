## Summary
Enforce a 9-point best-practice contract across all SCPI instrument drivers and mocks. This PR adds missing interface methods (write, get_error), context manager safety (__enter__/__exit__) to JDS6600 and Rigol DHO804, fixes mock state fidelity so measurements track setpoints, adds input validation to MockMPS6010H, and improves timing injectability in the Owon XDM1041 driver.

## Compliance Checklist
| Contract | Description | Status |
|----------|-------------|--------|
| BP-01 | Interface completeness | Done |
| BP-02 | write vs query discipline | Done |
| BP-03 | Command ordering enforcement | Done |
| BP-04 | Cached readback | Done |
| BP-05 | Input validation | Done |
| BP-06 | Context manager safety | Done |
| BP-07 | Timing injectability | Done |
| BP-08 | Mock state fidelity | Done |
| BP-09 | Test coverage | Done |

## Files Changed
```
 docs/scpi_audit.md                       | 44 ++++++++++++++++++
 lab_instruments/mock_instruments.py      | 40 +++++++++++++++--
 lab_instruments/src/device_manager.py    |  4 ++
 lab_instruments/src/jds6600_generator.py | 13 ++++++
 lab_instruments/src/owon_xdm1041.py      | 10 ++---
 lab_instruments/src/rigol_dho804.py      | 21 +++++++++
 tests/conftest.py                        |  5 ++-
 tests/test_awg.py                        | 29 ++++++++++++
 tests/test_dmm.py                        | 22 +++++++++
 tests/test_mock_instruments.py           | 76 ++++++++++++++++++++++++++++++++
 tests/test_scope.py                      | 34 ++++++++++++++
 11 files changed, 288 insertions(+), 10 deletions(-)
```

## Test Results
- Tests before: 526 passed, 16 skipped, 0 failed
- Tests after:  551 passed, 16 skipped, 0 failed
- 25 new tests added covering all fixed behaviors

## Audit Report
See `docs/scpi_audit.md` for the full per-driver violation table.

## Breaking Changes
None. All public APIs are preserved. Only internal state management and
missing methods were added.
