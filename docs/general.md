# General Commands

These commands work regardless of which instrument is active.

---

## scan

Re-scan for connected VISA instruments and connect any new ones found.

```
scan
```

Instruments are identified by querying `*IDN?` and matched against the [supported instrument list](instruments.md). They are assigned names like `psu1`, `dmm1`, `scope1`, `awg1`. If multiple of the same type are found they are numbered: `psu1`, `psu2`, etc.

Already-connected instruments keep their current state — a re-scan will **not** turn off a PSU that is actively sourcing. Only newly discovered instruments are initialised to safe defaults.

!!! tip
    You don't need to run `scan` manually on startup — the REPL scans automatically when it launches.

---

## force_scan

Disconnect all instruments, re-scan from scratch, and reset every output to safe defaults (0 V, off).

```
force_scan
```

Use this when you want a clean slate — for example, at the start of a new test sequence where you need all instruments back to a known-safe state.

!!! warning
    This will turn off all instrument outputs. If a PSU is actively sourcing, its output will be disabled and zeroed.

---

## disconnect

Remove a connected instrument from the current session without rescanning.

```
disconnect <name>
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `name` | required | Instrument name as shown by `list` (e.g. `psu1`, `scope2`) |

The device is removed from the REPL's device list. If it was the active selection, the selection is cleared. Use `scan` to rediscover it.

```
disconnect psu1    # remove psu1 from the session
```

!!! note
    This does not physically disconnect the instrument — it just removes it from the device list. Run `scan` to bring it back.

---

## list

Show all currently connected instruments.

```
list
```

Displays each instrument's assigned name, model, and whether it is currently active (set via `use`).

---

## use

Set the active instrument for subsequent generic commands.

```
use <name>
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `name` | required | Instrument name as shown by `list` (e.g. `psu1`, `scope2`) |

When only one instrument of a type is connected it is selected automatically. With multiple of the same type you must `use` the desired one before using generic commands like `psu set`.

```
use psu1          # make psu1 active
psu set 5.0       # acts on psu1

use psu2          # switch to psu2
psu set 12.0      # now acts on psu2
```

!!! tip "Direct addressing"
    You can skip `use` entirely by prefixing the instrument name to any command:
    <!-- doc-test: skip reason="reference snippet -- docs mock has only psu1" -->
    ```
    psu1 set 5.0
    psu2 set 12.0
    ```
    This does not change the active selection.

---

## idn

Query a instrument's identification string (`*IDN?`).

```
idn [name]
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `name` | optional | Instrument to query. Defaults to the active instrument if omitted. |

The response is the instrument's manufacturer, model, serial number, and firmware version.

<!-- doc-test: skip reason="bare 'idn' needs a prior 'use' -- this block shows usage patterns" -->
```
idn           # query active instrument
idn scope1    # query scope1 specifically
```

---

## raw

Send a raw SCPI command or query directly.

```
raw <command>
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `command` | required | Any SCPI string. If it ends with `?` the response is printed. |

```
raw *RST              # reset the instrument
raw OUTP:STAT ON      # send a command
raw MEAS:VOLT:DC?     # query — prints the response
```

!!! note
    `raw` sends to the **active** instrument. Use `use <name>` first if needed, or prefix the command: `psu1 raw *RST`.

---

## state

Set the active instrument to a named state.

```
state <on|off|safe|reset>
```

| Value | Effect |
|-------|--------|
| `on` | Enable output |
| `off` | Disable output |
| `safe` | Outputs off, returns to safe defaults |
| `reset` | Sends `*RST` — restores factory defaults |

```
state safe     # safe state on active instrument
state reset    # factory reset active instrument
```

---

## all

Apply a state to **every** connected instrument simultaneously.

```
all <on|off|safe|reset>
```

Same values as `state`. Useful as a quick emergency stop or to reset everything before a new test.

```
all safe      # put everything in safe state
all off       # turn off all outputs
```

---

## sleep

Pause for a specified duration.

```
sleep <duration>[unit]
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `duration` | required | Duration to pause. A bare number is treated as seconds. Append a unit suffix for other scales. |

| Suffix | Meaning | Example |
|--------|---------|---------|
| *(none)* | seconds | `sleep 1.0` |
| `s` | seconds | `sleep 1.5s` |
| `ms` | milliseconds | `sleep 500ms` |
| `us` | microseconds | `sleep 100us` |
| `m` | minutes | `sleep 2m` |

```
sleep 1.0       # wait 1 second
sleep 0.5       # wait 500 ms
sleep 500ms     # same — 500 ms
sleep 100us     # 100 microseconds
```

Also valid as a [script directive](scripting.md#timing): `sleep {delay}`

---

## status

Show all connected instruments and which one is currently active.

```bash
status
```

Identical to `list`. See the `list` command for full details. `status` exists as a convenience alias.

---

## close

Disconnect all instruments and release VISA resources.

```bash
close
```

Use `scan` to reconnect after closing.

---

## docs

Open the full documentation in your web browser — REPL commands, Python API, scripting, and more.

```bash
docs
```

Serves the bundled MkDocs site via a local HTTP server on a random port. If the site has not been built yet and `mkdocs.yml` is present, it automatically runs `mkdocs build` first.

!!! tip
    The HTTP server stays alive for the rest of the session. Calling `docs` again reuses the same port — no second server is started.

!!! note
    Auto-build requires: `pip install mkdocs-material`

---

## clear

Clear the terminal screen.

```
clear
```

---

## reload

Restart the REPL process, disconnecting all instruments.

```
reload
```

---

## version

Print the installed version of the toolkit.

```
version
```

---

## exit

Close the REPL and disconnect all instruments safely.

```
exit
```
