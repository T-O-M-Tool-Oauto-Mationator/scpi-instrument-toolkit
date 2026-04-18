# Chapter 10: Script Engine Internals

## Two-Phase Execution

Scripts execute in two phases:

1. **Expansion (compile time)** -- `expander.py` processes `for`, `repeat`, `array`, `call`, `import`, `export`, and variable substitution. Output is a flat list of commands with all loops unrolled.

2. **Runtime execution** -- `runner.py` executes the expanded commands. `while`, `if/elif/else`, `assert`, `break`, `continue` are handled at runtime because they depend on live values.

## The Expander

File: `lab_instruments/repl/script_engine/expander.py`

### Main entry point

<!-- doc-test: skip reason="function signature without body -- illustrative, not runnable" -->

    def expand_script_lines(
        lines: list[str],
        variables: dict[str, str],
        ctx: Any,
        depth: int = 0,
    ) -> list[tuple[str, str]]:

- `lines` -- raw script lines
- `variables` -- current variable values (for substitution)
- `depth` -- recursion depth (for nested `call` directives)
- Returns a list of `(command, source_annotation)` tuples

### For-loop expansion

When the expander encounters:

    for v 1.0 2.0 3.3 5.0
      psu set 1 {v}
      sleep 0.5
    end

It:

1. Collects the block between `for` and `end` using `_collect_block()`
2. Splits the value list: `["1.0", "2.0", "3.3", "5.0"]`
3. For each value, creates a copy of the variables dict with `v` set to that value
4. Recursively expands the block with the updated variables
5. Output is 4 copies of the block with `{v}` substituted

The expanded output looks like:

    ("__NOP__", "for v 1.0 2.0 3.3 5.0 -> v=1.0")
    ("psu set 1 1.0", "[v=1.0] psu set 1 {v}")
    ("sleep 0.5", "[v=1.0] sleep 0.5")
    ("__NOP__", "for v 1.0 2.0 3.3 5.0 -> v=2.0")
    ("psu set 1 2.0", "[v=2.0] psu set 1 {v}")
    ...

### Repeat expansion

    repeat 3
      dmm read
    end

Expands to 3 copies of `dmm read`, each annotated with the iteration number.

### Variable substitution

`substitute_expand(text, variables)` replaces `{varname}` with the current value. Only brace syntax is supported -- bare variable names are not substituted during expansion.

### Call directive

<!-- doc-test: skip reason="requires a saved sub-script named other_script on disk" -->

    call other_script

Loads `other_script` from the scripts library and recursively expands it. Variables are shared between caller and callee (same dict). Depth is incremented to prevent infinite recursion.

### Import/Export

<!-- doc-test: skip reason="REPL script-scope directives only valid inside a script, not at onecmd" -->

    import var_name           # make a variable available from parent scope
    export var_name           # pass a variable back to parent scope

These control variable visibility when scripts call sub-scripts.

## The Runner

File: `lab_instruments/repl/script_engine/runner.py`

The runner executes the expanded command list. It handles:

### While loops (runtime)

<!-- doc-test: skip reason="reference example -- i isn't initialized in this block" -->

    while i < 5
      i++
    end

While loops cannot be expanded at compile time because the condition depends on live values. The runner:

1. Evaluates the condition using `safe_eval()`
2. If true, executes the body
3. Repeats until the condition is false or `break` is encountered

### If/elif/else (runtime)

<!-- doc-test: skip reason="reference example -- voltage not set in this block" -->

    if voltage > 5.1
      verdict = "OVER"
    elif voltage < 4.9
      verdict = "UNDER"
    else
      verdict = "OK"
    end

The runner evaluates each condition in order and executes the first matching branch.

### Assert (runtime)

<!-- doc-test: skip reason="reference example -- voltage not set in this block" -->

    assert voltage > 0 "voltage must be positive"

Evaluates the condition. If false, stops the script with an error message.

### Break/Continue

<!-- doc-test: skip reason="break/continue only valid inside a while/for body" -->

    break        # exit the innermost while loop
    continue     # skip to the next iteration

## Variable Substitution Functions

Two functions handle variable substitution:

### substitute_expand (compile time)

File: `lab_instruments/repl/syntax.py`

<!-- doc-test: skip reason="function signature only, not a complete Python snippet" -->

    def substitute_expand(text: str, variables: dict[str, Any]) -> str:

Used during script expansion. Only replaces `{varname}` from the expansion-time variable dict.

### substitute_vars (runtime)

<!-- doc-test: skip reason="function signature only, not a complete Python snippet" -->

    def substitute_vars(text: str, script_vars: dict[str, Any],
                        measurements: MeasurementStore | None = None) -> str:

Used during command execution. Replaces `{varname}` from:
1. script_vars (user-assigned variables)
2. Measurement store labels (logged measurements)
3. The `last` keyword (most recent measurement)

## safe_eval

File: `lab_instruments/repl/syntax.py`

<!-- doc-test: skip reason="function signature only, not a complete Python snippet" -->

    def safe_eval(expr: str, names: dict[str, Any]) -> Any:

AST-based expression evaluator. Supports:
- Arithmetic: +, -, *, /, //, **, %
- Bitwise: &, |, <<, >>
- Comparisons: ==, !=, <, <=, >, >=
- Boolean: and, or, not
- Ternary: a if cond else b
- Functions: sqrt, sin, cos, log, round, abs, min, max, int, float, str, etc.
- Constants: pi, e, inf, nan, True, False
- Containers: [list], (tuple), subscript x[i]

No exec() or eval() -- everything is walked via AST nodes.

## Adding a New Directive

To add a new directive (e.g., `timeout 5`):

1. Add handling in `expander.py` in the main loop:

<!-- doc-test: skip reason="code fragment inside a markdown numbered-list step -- not standalone" -->

       if head == "timeout" and len(tokens) >= 2:
           timeout_val = float(tokens[1])
           variables["__timeout__"] = str(timeout_val)
           expanded.append(("__NOP__", f"timeout set to {timeout_val}s"))
           continue

2. If the directive needs runtime behavior, add handling in `runner.py` or `shell.py` instead.

3. Add tests for the new directive.

4. Document it in `docs/scripting.md`.
