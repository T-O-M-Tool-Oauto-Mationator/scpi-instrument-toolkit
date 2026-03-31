"""Command dispatcher abstraction.

Currently using InstrumentREPL, but in the future we can use a gRPC Dispatcher.
"""

from __future__ import annotations

import contextlib
import io
import threading
from collections.abc import Callable
from typing import Protocol, runtime_checkable


@runtime_checkable
class CommandDispatcher(Protocol):
    """Protocol for a command dispatcher."""

    def handle_command(self, command: str, line_callback: Callable[[str], None] | None = None) -> str:
        """Handle a command and return the response.

        If *line_callback* is provided, each chunk of output is forwarded to it
        in real-time (for streaming to TUI).  The full output is still returned.
        """
        ...

    def get_completions(self, text: str) -> list[str]:
        """Return sorted completion candidates for the given text prefix."""
        ...

    def get_measurement_snapshot(self) -> list[dict]:
        """Return a copy of all recorded measurements safe to read from the event loop."""
        ...

    def get_script_names(self) -> list[str]:
        """Return sorted list of loaded script names."""
        ...

    def get_vars_snapshot(self) -> dict[str, str]:
        """Return a copy of current script variable bindings."""
        ...

    def get_safety_snapshot(self) -> dict:
        """Return a summary of current safety state."""
        ...

    def get_instrument_detail(self, device_name: str) -> dict:
        """Return live status detail for a single instrument.

        The returned dict always contains ``type``, ``name``, and
        ``display_name``.  Remaining keys vary by instrument type.
        On communication error the dict contains an ``error`` key instead.
        """
        ...

    def save_instrument_state(self, device_name: str) -> dict:
        """Capture current instrument state as a restorable snapshot."""
        ...

    def restore_instrument_state(self, device_name: str, snapshot: dict) -> None:
        """Restore a previously saved instrument state."""
        ...


class _StreamingWriter(io.TextIOBase):
    """A writable stream that forwards each write to a callback AND a buffer."""

    def __init__(self, callback: Callable[[str], None]) -> None:
        super().__init__()
        self._callback = callback
        self._buf = io.StringIO()

    def write(self, s: str) -> int:
        self._buf.write(s)
        if s:
            self._callback(s)
        return len(s)

    def getvalue(self) -> str:
        return self._buf.getvalue()


class LocalDispatcher:
    """Run a command in process. One InstrumentRepl instance is reused to preserve session state."""

    def __init__(self, mock: bool = False) -> None:
        if mock:
            from lab_instruments import mock_instruments
            from lab_instruments.src import discovery as _disc

            _disc.InstrumentDiscovery.__init__ = lambda self: None
            _disc.InstrumentDiscovery.scan = lambda self, verbose=True: mock_instruments.get_mock_devices(verbose)

        from lab_instruments.repl.shell import InstrumentRepl

        self.repl = InstrumentRepl()
        self._lock = threading.Lock()

    def handle_command(self, command: str, line_callback: Callable[[str], None] | None = None) -> str:
        """Handle a command and return the response."""
        with self._lock:
            if line_callback is not None:
                stream = _StreamingWriter(line_callback)
                with contextlib.redirect_stdout(stream):  # type: ignore[type-var]
                    self.repl.onecmd(command)
                return stream.getvalue()
            else:
                with contextlib.redirect_stdout(io.StringIO()) as f:
                    self.repl.onecmd(command)
                return f.getvalue()

    def get_device_snapshot(self) -> list[dict]:
        """Return a snapshot of connected devices safe to read from the event loop.

        Each dict has: name, display_name, selected (bool), base_type.
        Returns copies of primitive values - never a live reference.
        """
        registry = self.repl.ctx.registry
        result = []
        for name in sorted(registry.devices):
            dev = registry.devices[name]
            status = "connected"
            try:
                if hasattr(dev, "query"):
                    dev.query("*IDN?")
            except Exception:  # noqa: BLE001
                status = "error"
            result.append(
                {
                    "name": name,
                    "display_name": registry.display_name(name),
                    "selected": name == registry.selected,
                    "base_type": registry.base_type(name),
                    "status": status,
                }
            )
        return result

    def get_measurement_snapshot(self) -> list[dict]:
        """Return a copy of all recorded measurements safe to read from the event loop.

        Each dict has: label, value, unit, source.
        Returns copies - never live references into MeasurementStore.
        """
        return [dict(e) for e in self.repl.ctx.measurements.entries]

    def get_script_names(self) -> list[str]:
        """Return sorted list of loaded script names."""
        return sorted(self.repl.ctx.scripts.keys())

    def get_script_content(self, name: str) -> str:
        """Return the content of a script as a single string."""
        lines = self.repl.ctx.scripts.get(name, [])
        return "\n".join(lines)

    def save_script_content(self, name: str, content: str) -> None:
        """Save script content (string) to memory and disk."""
        lines = content.split("\n")
        self.repl.ctx.scripts[name] = lines
        # Persist to disk
        script_path = self.repl.ctx.script_file(name)
        from pathlib import Path

        Path(script_path).parent.mkdir(parents=True, exist_ok=True)
        with open(script_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

    def delete_script(self, name: str) -> None:
        """Delete a script from memory and disk."""
        self.repl.ctx.scripts.pop(name, None)
        script_path = self.repl.ctx.script_file(name)
        from pathlib import Path

        Path(script_path).unlink(missing_ok=True)

    def get_vars_snapshot(self) -> dict[str, str]:
        """Return a copy of current script variable bindings."""
        return dict(self.repl.ctx.script_vars)

    def get_safety_snapshot(self) -> dict:
        """Return a summary of current safety state.

        Keys: limit_count (int), active_script (bool), exit_on_error (bool),
        limits (list[dict]) with per-entry device/channel/parameter/value.
        """
        ctx = self.repl.ctx
        limits_detail: list[dict] = []
        for (device_str, channel), params in ctx.safety_limits.items():
            for param_name, value in params.items():
                limits_detail.append(
                    {
                        "device": device_str,
                        "channel": channel,
                        "parameter": param_name,
                        "value": value,
                    }
                )
        meas_count = len(ctx.measurements.entries) if hasattr(ctx, "measurements") else 0
        data_dir = str(ctx.get_data_dir()) if hasattr(ctx, "get_data_dir") else ""
        return {
            "limit_count": len(limits_detail),
            "active_script": ctx.in_script,
            "exit_on_error": ctx.exit_on_error,
            "limits": limits_detail,
            "measurement_count": meas_count,
            "data_dir": data_dir,
        }

    def get_instrument_detail(self, device_name: str) -> dict:
        """Return live status for a single instrument, keyed by type."""
        registry = self.repl.ctx.registry
        dev = registry.devices.get(device_name)
        if dev is None:
            return {"type": "unknown", "name": device_name, "display_name": device_name, "error": "not found"}

        base = registry.base_type(device_name)
        display = registry.display_name(device_name)
        caps = registry.get_caps(dev)
        result: dict = {"type": base, "name": device_name, "display_name": display}

        try:
            if base == "psu":
                result.update(self._detail_psu(dev, caps))
            elif base == "dmm":
                result.update(self._detail_dmm(dev))
            elif base == "awg":
                result.update(self._detail_awg(dev))
            elif base == "scope":
                result.update(self._detail_scope(dev))
            elif base == "ev2300":
                result.update(self._detail_ev2300(dev))
        except Exception as exc:  # noqa: BLE001
            result["error"] = str(exc)

        return result

    # -- per-type detail helpers -----------------------------------------------

    @staticmethod
    def _detail_psu(dev: object, caps: object) -> dict:
        from lab_instruments.repl.capabilities import Capability

        is_smu = hasattr(dev, "get_output_mode")
        if is_smu:
            vi = dev.measure_vi() if hasattr(dev, "measure_vi") else {}
            return {
                "subtype": "smu",
                "output_mode": dev.get_output_mode(),
                "voltage_set": dev.get_voltage_setpoint(),
                "current_limit": dev.get_current_limit(),
                "voltage_meas": vi.get("voltage", 0.0),
                "current_meas": vi.get("current", 0.0),
                "in_compliance": vi.get("in_compliance", False),
                "temperature": dev.read_temperature() if hasattr(dev, "read_temperature") else None,
                "output": dev.get_output_state(),
            }

        multi = bool(caps & Capability.PSU_MULTI_CHANNEL)
        has_readback = bool(caps & Capability.PSU_READBACK)
        channels: list[dict] = []

        if multi and hasattr(dev, "CHANNEL_MAP"):
            # Save/restore selected channel to avoid mutating device state
            prev_ch = getattr(dev, "_selected_ch", None)
            try:
                for ch_key, ch_label in dev.CHANNEL_MAP.items():
                    ch_info: dict = {"id": ch_key, "label": ch_label}
                    if hasattr(dev, "select_channel"):
                        dev.select_channel(ch_key)
                    ch_info["voltage_set"] = dev.get_voltage_setpoint()
                    ch_info["current_limit"] = dev.get_current_limit()
                    if has_readback:
                        ch_info["voltage_meas"] = dev.measure_voltage(ch_key)
                        ch_info["current_meas"] = dev.measure_current(ch_key)
                    ch_info["output"] = dev.get_output_state(ch_key)
                    channels.append(ch_info)
            finally:
                if prev_ch is not None and hasattr(dev, "select_channel"):
                    dev.select_channel(prev_ch)
        else:
            ch_info = {
                "id": 1,
                "label": "CH1",
                "voltage_set": dev.get_voltage_setpoint(),
                "current_limit": dev.get_current_limit(),
                "output": dev.get_output_state(),
            }
            if has_readback:
                ch_info["voltage_meas"] = dev.measure_voltage()
                ch_info["current_meas"] = dev.measure_current()
            channels.append(ch_info)

        return {"channels": channels}

    @staticmethod
    def _detail_dmm(dev: object) -> dict:
        # Prefer fetch() (non-triggering) over read() (triggers new measurement)
        if hasattr(dev, "fetch"):
            try:
                reading = dev.fetch()
            except Exception:  # noqa: BLE001
                reading = dev.read() if hasattr(dev, "read") else None
        elif hasattr(dev, "read"):
            reading = dev.read()
        else:
            reading = None
        return {"last_reading": reading}

    @staticmethod
    def _detail_awg(dev: object) -> dict:
        channels: list[dict] = []
        for ch in (1, 2):
            ch_info: dict = {"id": ch}
            if hasattr(dev, "get_frequency"):
                ch_info["frequency"] = dev.get_frequency(ch)
            if hasattr(dev, "get_amplitude"):
                ch_info["amplitude"] = dev.get_amplitude(ch)
            if hasattr(dev, "get_offset"):
                ch_info["offset"] = dev.get_offset(ch)
            if hasattr(dev, "get_output_state"):
                ch_info["output"] = dev.get_output_state(ch)
            channels.append(ch_info)
        return {"channels": channels}

    @staticmethod
    def _detail_scope(dev: object) -> dict:
        num_ch = getattr(dev, "num_channels", 4)
        trigger = dev.get_trigger_status() if hasattr(dev, "get_trigger_status") else "unknown"
        return {"trigger_status": trigger, "num_channels": num_ch}

    @staticmethod
    def _detail_ev2300(dev: object) -> dict:
        info = dev.get_device_info() if hasattr(dev, "get_device_info") else {}
        return {
            "connected": getattr(dev, "is_open", False) if hasattr(dev, "is_open") else True,
            "serial": info.get("serial", "N/A"),
            "product": info.get("product", "N/A"),
        }

    def save_instrument_state(self, device_name: str) -> dict:
        """Capture current settable parameters as a restorable snapshot."""
        registry = self.repl.ctx.registry
        dev = registry.devices.get(device_name)
        if dev is None:
            return {}
        base = registry.base_type(device_name)
        snap: dict = {"type": base, "name": device_name}
        try:
            if base == "psu" and hasattr(dev, "get_output_mode"):
                # SMU
                snap["output_mode"] = dev.get_output_mode()
                snap["voltage"] = dev.get_voltage_setpoint()
                snap["current"] = dev.get_current_limit()
                snap["output"] = dev.get_output_state()
            elif base == "psu":
                snap["voltage"] = dev.get_voltage_setpoint()
                snap["current"] = dev.get_current_limit()
                snap["output"] = dev.get_output_state()
            elif base == "awg":
                channels = []
                for ch in (1, 2):
                    ch_snap: dict = {"id": ch}
                    if hasattr(dev, "get_frequency"):
                        ch_snap["frequency"] = dev.get_frequency(ch)
                    if hasattr(dev, "get_amplitude"):
                        ch_snap["amplitude"] = dev.get_amplitude(ch)
                    if hasattr(dev, "get_offset"):
                        ch_snap["offset"] = dev.get_offset(ch)
                    if hasattr(dev, "get_output_state"):
                        ch_snap["output"] = dev.get_output_state(ch)
                    channels.append(ch_snap)
                snap["channels"] = channels
        except Exception as exc:  # noqa: BLE001
            snap["error"] = str(exc)
        return snap

    def restore_instrument_state(self, device_name: str, snapshot: dict) -> None:
        """Restore a previously saved instrument state."""
        registry = self.repl.ctx.registry
        dev = registry.devices.get(device_name)
        if dev is None:
            return
        base = snapshot.get("type", "")
        try:
            if base == "psu" and "output_mode" in snapshot:
                # SMU
                if snapshot.get("output_mode") == "voltage":
                    dev.set_voltage(snapshot.get("voltage", 0))
                    dev.set_current_limit(snapshot.get("current", 0.1))
                else:
                    dev.set_current_mode(snapshot.get("current", 0), snapshot.get("voltage", 5))
                dev.enable_output(snapshot.get("output", False))
            elif base == "psu":
                dev.set_voltage(snapshot.get("voltage", 0))
                dev.set_current_limit(snapshot.get("current", 0.1))
                dev.enable_output(snapshot.get("output", False))
            elif base == "awg":
                for ch_snap in snapshot.get("channels", []):
                    ch = ch_snap["id"]
                    if "frequency" in ch_snap and hasattr(dev, "set_frequency"):
                        dev.set_frequency(ch, ch_snap["frequency"])
                    if "amplitude" in ch_snap and hasattr(dev, "set_amplitude"):
                        dev.set_amplitude(ch, ch_snap["amplitude"])
                    if "offset" in ch_snap and hasattr(dev, "set_offset"):
                        dev.set_offset(ch, ch_snap["offset"])
                    if "output" in ch_snap and hasattr(dev, "enable_output"):
                        dev.enable_output(ch, ch_snap["output"])
        except Exception:  # noqa: BLE001
            raise

    def get_completions(self, text: str) -> list[str]:
        """Return sorted, deduplicated completion candidates for text.

        Calls both completenames (top-level verbs) and completedefault
        (sub-command arguments) to cover the full REPL command space.
        Safe to call from any thread - reads only REPL method names and
        context state, no I/O.
        """
        results: list[str] = []
        with contextlib.suppress(Exception):
            results.extend(self.repl.completenames(text, text, 0, len(text)))
        with contextlib.suppress(Exception):
            results.extend(self.repl.completedefault(text, text, 0, len(text)))
        seen: set[str] = set()
        deduped: list[str] = []
        for r in results:
            if r not in seen:
                seen.add(r)
                deduped.append(r)
        return sorted(deduped)
