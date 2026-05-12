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
