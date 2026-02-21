# SCPI Instrument Toolkit

A tool for controlling lab instruments (oscilloscopes, power supplies, multimeters, and function generators) from your computer.

## Supported Instruments

| Instrument | Type |
|---|---|
| Tektronix MSO2024 | Oscilloscope |
| Rigol DHO804 | Oscilloscope |
| HP E3631A | Power Supply |
| HP 34401A | Multimeter |
| BK Precision 4063 | Function Generator |
| Keysight EDU33212A | Function Generator |
| OWON XDM1041 | Multimeter |
| Matrix MPS6010H | Power Supply |
| JDS6600 | Function Generator |

---

## Installation

You need **Python 3.8 or newer** installed on your computer. You can check by opening a terminal and running:

```
python --version
```

If you don't have Python, download it from [python.org](https://www.python.org/downloads/).

### Install the toolkit

Open a terminal and run:

```
pip install git+https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git
```

That's it. This installs everything including the `scpi-repl` command.

> **Note:** You also need [NI-VISA](https://www.ni.com/en/support/downloads/drivers/download.ni-visa.html) installed for the tool to detect instruments over USB or GPIB.

---

## Using the REPL

The REPL (Read-Eval-Print Loop) is an interactive terminal where you type commands to control your instruments.

### Start it

```
scpi-repl
```

It will automatically scan for connected instruments and show you what it found.

### Try it without any instruments

If you just want to explore the tool without connecting anything:

```
scpi-repl --mock
```

This uses fake instruments so you can test commands safely.

---

## Basic Commands

Once the REPL is running, here are the most useful commands:

| Command | What it does |
|---|---|
| `help` | Show all available commands |
| `list` | Show connected instruments |
| `scan` | Re-scan for instruments |
| `psu output on` | Turn on the power supply |
| `psu set 5.0 0.5` | Set PSU to 5V, 0.5A limit |
| `psu meas v` | Measure output voltage |
| `dmm meas vdc` | Measure DC voltage |
| `dmm read` | Take a reading |
| `awg wave 1 sine freq=1000 amp=2.0` | Output a 1kHz sine wave |
| `scope measure 1 FREQUENCY` | Measure frequency on channel 1 |
| `scope autoset` | Auto-configure the scope |
| `state safe` | Put all instruments in a safe state |
| `exit` | Quit |

Type `help <command>` for more detail on any command. For example: `help psu`

---

## Saving and Running Scripts

You can save sequences of commands as scripts so you don't have to type them every time.

```
script new my_setup
```

This opens a text editor. Type your commands (one per line), save, and close. Then run it with:

```
script run my_setup
```

Scripts are saved in a file called `.repl_scripts.json` in whatever folder you launched `scpi-repl` from.

---

## Updating

To get the latest version:

```
pip install --upgrade git+https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git
```
