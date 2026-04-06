# DeviceManager

Base class for all VISA-based instrument drivers. Wraps PyVISA to provide raw SCPI communication.

```python
from lab_instruments import DeviceManager
```

---

## Constructor

```python
DeviceManager(resource_name)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `resource_name` | `str` | VISA resource string (e.g., `"GPIB0::22::INSTR"`) |

---

## Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `connect()` | Open the VISA connection. Sets timeout to 5000 ms. | `None` |
| `disconnect()` | Close the VISA connection. | `None` |
| `send_command(command)` | Send a SCPI command (no response). | `None` |
| `query(command)` | Send a SCPI command and return the response. | `str` |
| `clear_status()` | Send `*CLS` to clear the status byte. | `None` |
| `reset()` | Send `*RST` and `*CLS` to reset the instrument. | `None` |

---

## Properties

| Property | Type | Description |
|----------|------|-------------|
| `resource_name` | `str` | The VISA address passed to the constructor |
| `instrument` | `pyvisa.Resource` | The underlying PyVISA resource (or `None` if not connected) |
| `rm` | `pyvisa.ResourceManager` | The PyVISA ResourceManager instance |

---

## Example: Raw SCPI

Use `DeviceManager` directly when your instrument isn't supported by a specific driver:

```python
from lab_instruments import DeviceManager

inst = DeviceManager("USB0::0x1AB1::0x0588::DS1ZA000000000::INSTR")
inst.connect()

# Identify
print(inst.query("*IDN?"))

# Reset
inst.reset()

# Send custom commands
inst.send_command(":CHANnel1:DISPlay ON")
inst.send_command(":TIMebase:SCALe 0.001")

# Query a value
freq = inst.query(":MEASure:FREQuency? CHANnel1")
print(f"Frequency: {freq}")

inst.disconnect()
```

---

## Subclassing

To create a driver for a new instrument, subclass `DeviceManager`:

```python
from lab_instruments.src.device_manager import DeviceManager

class MyInstrument(DeviceManager):
    def __init__(self, resource_name):
        super().__init__(resource_name)

    def measure_voltage(self):
        response = self.query("MEASURE:VOLTAGE?")
        return float(response.strip())
```

All built-in drivers follow this pattern. See any driver source file for a full example.
