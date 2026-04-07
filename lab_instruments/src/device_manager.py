import pyvisa


class DeviceManager:
    """Base class for SCPI instrument drivers using PyVISA.

    All instrument drivers inherit from this class and gain a shared
    PyVISA connection lifecycle (connect / disconnect) plus thin wrappers
    around the two most common SCPI operations: write-only commands and
    query-response commands.

    Attributes:
        resource_name: VISA resource string passed at construction time,
            e.g. ``"USB0::0x0957::0x2807::MY12345678::INSTR"``.
        instrument: The open ``pyvisa.Resource`` object, or ``None`` when
            not connected.
    """

    def __init__(self, resource_name):
        """Create a DeviceManager for the given VISA resource.

        Args:
            resource_name: VISA resource string that identifies the
                instrument (e.g. ``"GPIB0::5::INSTR"`` or
                ``"USB0::0x0957::...::INSTR"``).
        """
        self.rm = pyvisa.ResourceManager()
        self.resource_name = resource_name
        self.instrument = None

    def connect(self):
        """Open a PyVISA session to the instrument.

        Sets a 5-second timeout and ``"\\n"`` read termination on the
        session.  Prints a confirmation message on success.

        Raises:
            pyvisa.VisaIOError: If the resource cannot be opened (e.g.
                instrument is off, address is wrong, or no VISA driver
                is installed).
        """
        try:
            self.instrument = self.rm.open_resource(self.resource_name)
            self.instrument.timeout = 5000
            self.instrument.read_termination = "\n"
            print(f"Connected to {self.resource_name}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to connect to {self.resource_name}: {e}")
            raise

    def disconnect(self):
        """Close the PyVISA session and release the instrument handle.

        Safe to call even when not connected — does nothing if
        ``self.instrument`` is already ``None``.
        """
        if self.instrument:
            self.instrument.close()
            self.instrument = None
            print(f"Disconnected from {self.resource_name}")

    def send_command(self, command):
        """Write a SCPI command to the instrument (fire-and-forget).

        Args:
            command: SCPI command string, e.g. ``":CHAN1:DISP ON"``.

        Raises:
            ConnectionError: If the instrument session is not open.
        """
        if self.instrument:
            self.instrument.write(command)
            print(f"Sent command: {command}")
        else:
            raise ConnectionError("Instrument not connected.")

    def query(self, command):
        """Write a SCPI command and return the instrument's response.

        Args:
            command: SCPI query string, e.g. ``"*IDN?"``.

        Returns:
            The response string with leading/trailing whitespace stripped.

        Raises:
            ConnectionError: If the instrument session is not open.
        """
        if self.instrument:
            response = self.instrument.query(command)
            return response.strip()
        else:
            raise ConnectionError("Instrument not connected.")

    def clear_status(self):
        """Send ``*CLS`` to clear the instrument's status registers.

        Clears the Standard Event Status Register (SESR), the Status Byte
        Register (STB), and the error queue.  Typically called during
        initialisation before issuing other commands.
        """
        self.send_command("*CLS")

    def reset(self):
        """Send ``*RST`` followed by ``*CLS`` to restore factory defaults.

        Resets all instrument settings to their power-on defaults and then
        clears the status registers.  Use at the start of a test sequence
        to guarantee a known instrument state.
        """
        self.send_command("*RST")
        self.clear_status()
