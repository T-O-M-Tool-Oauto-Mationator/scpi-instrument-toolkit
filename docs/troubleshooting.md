# Troubleshooting

## `scpi-repl` is not recognized

Pip installs `scpi-repl` to the Python `Scripts` folder, which may not be on your PATH. There are three scenarios:

---

### Standard Windows — self-healing fix

Run the module form once:

```powershell
python -m lab_instruments
```

The toolkit automatically adds the Scripts folder to your user PATH via the Windows registry (no admin required) and prints:

```
[scpi] Added Python Scripts to your PATH (C:\...\Scripts).
[scpi] Open a new terminal and 'scpi-repl' will work.
```

Open a **new** PowerShell window and `scpi-repl` will work from then on.

---

### Managed machines (TAMU VOAL and similar)

On machines where group policy blocks user registry edits, the automatic fix above fails silently. Use one of these instead:

!!! tip "Permanent workaround — always launch with the module form"
    ```powershell
    python -m lab_instruments
    python -m lab_instruments --mock
    ```
    All flags work the same way. This is the recommended method on any machine where you cannot permanently modify PATH.

!!! note "Session-only PATH fix — enables `scpi-repl` for this terminal window"
    ```powershell
    $pyPath = python -c "import sys, os; print(os.path.join(sys.prefix, 'Scripts'))"
    $env:Path += ";$pyPath"
    scpi-repl
    ```
    You'll need to run these two lines again each time you open a new terminal.

---

## NI-VISA not found

The toolkit needs [NI-VISA](https://www.ni.com/en/support/downloads/drivers/download.ni-visa.html) to communicate with instruments over USB or GPIB. If you see an error about VISA not being found, download and install NI-VISA from the link above, then restart your terminal and try again.

If you just want to explore the tool without any hardware, use mock mode — no VISA required:

```powershell
python -m lab_instruments --mock
```
