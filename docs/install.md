# Installation

## Requirements

- Python 3.10 or later (use **3.12** if you plan to drive the toolkit from NI TestStand - see [NI TestStand Setup](teststand.md))
- pip
- `git` on PATH (the install pulls from the GitHub repo - `pip install scpi-instrument-toolkit` does NOT work; the package is not on PyPI)

---

## Install from GitHub

The toolkit is distributed as a `git+https://` install, not a PyPI package. Run:

```bash
pip install "git+https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git"
```

This installs the `scpi-repl` command and all required dependencies automatically.

!!! warning "`scpi-instrument-toolkit` is NOT on PyPI"
    Running `pip install scpi-instrument-toolkit` will fail with `Could not find a version that satisfies the requirement scpi-instrument-toolkit`. Always use the `git+https://...` form above.

---

## Install from source (for development)

```bash
git clone https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git
cd scpi-instrument-toolkit
pip install -e .
```

---

## Platform notes

=== "Windows"
    Python installers from [python.org](https://www.python.org/downloads/) include pip. During installation, check **"Add Python to PATH"**.

    After installation, verify:

    ```powershell
    python --version
    pip --version
    git --version
    ```

    Then install with the git+ URL above. If you are on a TAMU managed machine and do not have git yet, run [`setup-tamu.ps1`](troubleshooting.md#first-time-setup-on-tamu-managed-windows-machines) first - it installs git and Python in one shot.

    If `scpi-repl` is not recognised after install, see [Troubleshooting](troubleshooting.md).

=== "macOS"
    Install Python and git via [Homebrew](https://brew.sh) (recommended):

    ```bash
    brew install python git
    pip3 install "git+https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git"
    ```

    Or download the macOS installer from [python.org](https://www.python.org/downloads/).

=== "Linux (Debian/Ubuntu)"
    ```bash
    sudo apt update
    sudo apt install python3 python3-pip git
    pip3 install "git+https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git"
    ```

    Serial instruments communicate via device files (`/dev/ttyUSB*`, `/dev/ttyACM*`) owned by the `dialout` group — your user must be a member. See [Troubleshooting](troubleshooting.md#serial-port-permission-denied-linux).

=== "Linux (Arch)"
    ```bash
    sudo pacman -S python python-pip git
    pip install "git+https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git"
    ```

    Serial instruments communicate via device files (`/dev/ttyUSB*`, `/dev/ttyACM*`) owned by the `uucp` group — your user must be a member. See [Troubleshooting](troubleshooting.md#serial-port-permission-denied-linux).

---

## Optional extras

| Extra | Command | Purpose |
|-------|---------|---------|
| NI PXIe-4139 SMU | `pip install nidcpower` | NI DCPower driver for PXIe SMU — required only if you have NI PXIe-4139 hardware |
| Docs build | `pip install "scpi-instrument-toolkit[docs] @ git+https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git"` | Build HTML docs locally with MkDocs |
| Test suite | `pip install "scpi-instrument-toolkit[test] @ git+https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git"` | Run unit/integration tests |

---

## Verify the installation

```bash
scpi-repl --mock
```

This launches the REPL with simulated instruments — no hardware required. Type `help` for available commands.

---

## Upgrading

```bash
pip install --upgrade "git+https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git"
```

To pull the latest nightly:

```bash
pip install --upgrade --force-reinstall "git+https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git@dev/nightly"
```

---

## Vendor drivers

The Python install above is enough for `--mock` mode and any instruments that speak SCPI over an OS-native serial / Ethernet path. **Real hardware needs the matching vendor driver installed once per machine.** Pick only the drivers for the instruments you actually have.

### NI-VISA runtime — required for almost every real instrument

NI-VISA is the underlying VISA backend that the toolkit's `pyvisa` dependency talks to. You need it for:

- Any **USB-TMC** instrument (Keysight DMMs / PSUs, Rigol scopes, Tektronix scopes, BK function generators, etc.)
- Any **GPIB** instrument
- Any **VXI-11 / HiSLIP** instrument over Ethernet

Skip this only if every instrument you plan to use is mocked, raw serial (`/dev/ttyUSB*`, COMx with no VISA), or accessed through a non-VISA driver below.

1. Download the runtime from [ni.com/en/support/downloads/drivers/download.ni-visa.html](https://www.ni.com/en/support/downloads/drivers/download.ni-visa.html).
2. Run the installer. **Admin rights required**, takes about 5–10 minutes on Windows.
3. Restart your terminal so the new PATH entries take effect.
4. Verify with `python -c "import pyvisa; print(pyvisa.ResourceManager().list_resources())"` — you should see `('ASRLn::INSTR', ...)` style strings and no `OSError`.

!!! note "TAMU managed machines"
    NI-VISA installs cleanly on TAMU-managed Windows machines because the installer is signed and submitted through the standard MSI path. You still need the admin password / TA assist for the one-time install.

### NI-DCPower — only if you have an NI PXIe-4139 SMU

If you're driving an NI PXIe-4139 source-measure unit, install the NI-DCPower driver **and** the Python binding:

1. Download NI-DCPower from [ni.com/downloads/drivers/](https://www.ni.com/en/support/downloads/drivers.html) (admin required).
2. After NI-DCPower is installed, add the Python binding:

    ```bash
    pip install nidcpower
    ```

The toolkit's PXIe-4139 driver imports `nidcpower` at scan time — without it, the SMU won't enumerate.

### EV2300 USB-to-I2C bridge — no separate driver needed

The original TI EV2300A enumerates as a generic USB-HID device on all three OSes; the toolkit talks to it via `hidapi` (pulled in by the `hid` extra). To install the optional `hid` extra:

```bash
pip install "scpi-instrument-toolkit[hid] @ git+https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git"
```

If your kit ships an in-house STM32 replacement instead (Adafruit Feather STM32F405 + FeatherWing), no additional setup is needed at runtime — the bridge enumerates with the same USB descriptor and the existing driver picks it up. Re-flashing the firmware does need extra tools; see the **Flashing the STM32 bridge** section in the [TA Developer Guide Ch 12](https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit/blob/main/manuals/ta-developer/ch12_stm32_bridge.md).

### Vendor utilities — only for one-off troubleshooting

You don't need these to use the toolkit, but TAs and instructors usually install them on lab bench machines so they can fall back to vendor software for cross-checks:

- **Keysight Connection Expert** — verifies Keysight USB / GPIB / LXI links; ships with the IO Libraries Suite.
- **NI MAX** — bundled with NI-VISA. Useful for checking that VISA can see your instruments before launching the REPL.
- **TI BQStudio** — only relevant if you're working with the BQ76920 EVM via the EV2300 bridge.

All three are admin-installer-required Windows-only tools. Skip if you don't already use them.

!!! warning "Only one program can hold a VISA resource at a time"
    If `scan` in the REPL reports "Resource busy" or "Cannot open resource", close NI MAX / Keysight Connection Expert / a second `scpi-repl` first. The lock is exclusive.
