# Chapter 5: Adding Bundled Examples

## The EXAMPLES Dict

Bundled examples live in `lab_instruments/examples.py` as a Python dictionary:

    EXAMPLES = {
        "psu_dmm_test": {
            "description": "Set PSU to a voltage, measure with DMM, log result",
            "lines": [
                "# psu_dmm_test",
                "voltage = 5.0",
                "label = vtest",
                "",
                "psu1 chan 1 on",
                "psu1 set 1 {voltage}",
                "sleep 0.5",
                "{label} = dmm1 meas unit=V",
                "log print",
            ],
            "code": '''
    """PSU + DMM voltage test -- Python API version."""
    import time
    psu.set_voltage(1, 5.0)
    time.sleep(0.5)
    v = dmm.read()
    print(f"Measured: {v} V")
            ''',
        },
    }

### Required fields

- **Key**: example name (string, lowercase with underscores, e.g., "my_new_test")
- **"description"**: one-line summary shown by the `examples` command
- **"lines"**: list of SCPI script lines (the REPL script version)

### Optional fields

- **"code"**: Python source code string (the Python API version). If provided, `examples load` creates both a `.scpi` and a `.py` file.

## Naming Conventions

- Use lowercase with underscores: `voltage_sweep`, `psu_dmm_test`
- Keep names short but descriptive
- Prefix with the primary instrument type when possible: `psu_ramp`, `awg_scope_check`

## Writing the Script Lines

Each entry in "lines" is one REPL command:

- Use `{var}` for variable substitution
- Define default values at the top so users can override: `voltage = 5.0`
- Add comments with `#` for documentation
- Include `log print` at the end to show results
- Use descriptive labels: `v_{v}` in loops creates `v_1.0`, `v_2.0`, etc.

## Syncing with docs/examples.md

Every EXAMPLES entry should have a matching section in `docs/examples.md`:

    ## my_new_test

    **Description here.**

    **Script source:**

    ```text
    # my_new_test
    voltage = 5.0
    ...
    ```

### Checking sync

Run the validation script:

    python scripts/validate_doc_examples.py

This reports:
- SYNC -- docs match the EXAMPLES dict
- DRIFT -- docs have diverged (first differing line is shown)
- MISSING -- example exists in code but not in docs

### Running examples in mock mode

The validation script also runs every example with mock instruments:

    python scripts/validate_doc_examples.py --run-only

All examples must PASS (exit without uncaught exceptions).

## Adding a New Example

1. Add the entry to `EXAMPLES` dict in `examples.py`
2. Add the corresponding section to `docs/examples.md`
3. Run `python scripts/validate_doc_examples.py` -- should show SYNC and PASS
4. Include the example addition in the same commit as any related feature

## Tips

- Test your example in `--mock` mode before committing
- Avoid `pause` and `input` in example scripts -- they block non-interactive testing
- Use `sleep 0.5` for realistic settling times
- Include both SCPI (`lines`) and Python (`code`) versions when possible
- Keep examples under 30 lines -- they should demonstrate one concept clearly
