# Installation

## Requirements

- Python 3.8 or later
- pip

---

## Install from PyPI

```bash
pip install scpi-instrument-toolkit
```

This installs the `scpi-repl` command and all required dependencies automatically.

---

## Install from source

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
    ```

    If `scpi-repl` is not recognised after install, see [Troubleshooting](troubleshooting.md).

=== "macOS"
    Install Python via [Homebrew](https://brew.sh) (recommended):

    ```bash
    brew install python
    pip3 install scpi-instrument-toolkit
    ```

    Or download the macOS installer from [python.org](https://www.python.org/downloads/).

=== "Linux (Debian/Ubuntu)"
    ```bash
    sudo apt update
    sudo apt install python3 python3-pip
    pip3 install scpi-instrument-toolkit
    ```

    Serial instruments also require adding your user to the `dialout` group — see [Troubleshooting](troubleshooting.md#serial-port-permission-denied-linux).

=== "Linux (Arch)"
    ```bash
    sudo pacman -S python python-pip
    pip install scpi-instrument-toolkit
    ```

    Serial instruments also require adding your user to the `uucp` group — see [Troubleshooting](troubleshooting.md#serial-port-permission-denied-linux).

---

## Optional extras

| Extra | Command | Purpose |
|-------|---------|---------|
| NI PXIe-4139 SMU | `pip install nidcpower` | NI DCPower driver for PXIe SMU |
| Docs build | `pip install scpi-instrument-toolkit[docs]` | Build HTML docs locally with MkDocs |
| Test suite | `pip install scpi-instrument-toolkit[test]` | Run unit/integration tests |

---

## Verify the installation

```bash
scpi-repl --mock
```

This launches the REPL with simulated instruments — no hardware required. Type `help` for available commands.

---

## Upgrading

```bash
pip install --upgrade scpi-instrument-toolkit
```
