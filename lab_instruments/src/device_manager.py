import pyvisa


class DeviceManager:
    """
    Base class for SCPI instrument management using PyVISA.
    """

    def __init__(self, resource_name):
        self.rm = pyvisa.ResourceManager()
        self.resource_name = resource_name
        self.instrument = None

    def connect(self):
        """Connects to the instrument."""
        try:
            self.instrument = self.rm.open_resource(self.resource_name)
            self.instrument.timeout = 10000  # 10 seconds for slower instruments
            self.instrument.read_termination = "\n"
            print(f"Connected to {self.resource_name}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to connect to {self.resource_name}: {e}")
            raise

    def disconnect(self):
        """Disconnects from the instrument."""
        if self.instrument:
            self.instrument.close()
            self.instrument = None
            print(f"Disconnected from {self.resource_name}")

    def send_command(self, command):
        """Sends a command to the instrument without waiting for a response."""
        if self.instrument:
            self.instrument.write(command)
            print(f"Sent command: {command}")
        else:
            raise ConnectionError("Instrument not connected.")

    def query(self, command):
        """Sends a command and returns the response."""
        if self.instrument:
            response = self.instrument.query(command)
            return response.strip()
        else:
            raise ConnectionError("Instrument not connected.")

    def clear_status(self):
        """Clears the instrument status byte."""
        self.send_command("*CLS")

    def reset(self):
        """Resets the DMM to a known state."""
        self.send_command("*RST")
        self.clear_status()
