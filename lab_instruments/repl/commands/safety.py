"""Safety limit system: limit checking, collection, and enforcement."""

import contextlib
import re
from typing import Any, Dict, Optional

from lab_instruments.src.terminal import ColorPrinter

from ..context import ReplContext


class SafetySystem:
    """Manages safety limits and output-enable guards for PSU and AWG."""

    def __init__(self, ctx: ReplContext) -> None:
        self.ctx = ctx

    def collect_limits(self, device_name: str, device_type: str, channel: Optional[int]) -> Dict[str, float]:
        lookup_keys = [
            (device_name, channel),
            (device_name, None),
            (device_type, channel),
            (device_type, None),
        ]
        seen: set = set()
        merged: Dict[str, float] = {}
        for k in lookup_keys:
            if k in seen:
                continue
            seen.add(k)
            for param_key, val in self.ctx.safety_limits.get(k, {}).items():
                if param_key.endswith("_upper"):
                    if param_key not in merged or val < merged[param_key]:
                        merged[param_key] = val
                elif param_key.endswith("_lower") and (param_key not in merged or val > merged[param_key]):
                    merged[param_key] = val
        return merged

    def check_psu_limits(self, device_name: str, channel: Optional[int], voltage=None, current=None) -> bool:
        device_type = re.sub(r"\d+$", "", device_name)
        limits = self.collect_limits(device_name, device_type, channel)
        if not limits:
            return True
        ch_str = f" ch{channel}" if channel is not None else ""
        if voltage is not None:
            if "voltage_upper" in limits and voltage > limits["voltage_upper"]:
                self.ctx.error(
                    f"Safety limit exceeded: {device_name}{ch_str} voltage {voltage}V > {limits['voltage_upper']}V"
                )
                return False
            if "voltage_lower" in limits and voltage < limits["voltage_lower"]:
                self.ctx.error(
                    f"Safety limit exceeded: {device_name}{ch_str} voltage {voltage}V < {limits['voltage_lower']}V"
                )
                return False
        if current is not None:
            if "current_upper" in limits and current > limits["current_upper"]:
                self.ctx.error(
                    f"Safety limit exceeded: {device_name}{ch_str} current {current}A > {limits['current_upper']}A"
                )
                return False
            if "current_lower" in limits and current < limits["current_lower"]:
                self.ctx.error(
                    f"Safety limit exceeded: {device_name}{ch_str} current {current}A < {limits['current_lower']}A"
                )
                return False
        return True

    def query_awg_state(self, device_name: str, channel: int) -> Dict[str, Any]:
        dev = self.ctx.registry.devices.get(device_name)
        if dev is None:
            return {"vpp": None, "offset": None, "freq": None}
        vpp = offset = freq = None
        try:
            if hasattr(dev, "get_amplitude"):
                vpp = dev.get_amplitude(channel)
        except Exception:
            pass
        try:
            if hasattr(dev, "get_offset"):
                offset = dev.get_offset(channel)
        except Exception:
            pass
        try:
            if hasattr(dev, "get_frequency"):
                freq = dev.get_frequency(channel)
        except Exception:
            pass
        cached = self.ctx.awg_channel_state.get((device_name, channel), {})
        if vpp is None:
            vpp = cached.get("vpp")
        if offset is None:
            offset = cached.get("offset")
        return {"vpp": vpp, "offset": offset, "freq": freq}

    def query_psu_state(self, device_name: str) -> Dict[str, Any]:
        dev = self.ctx.registry.devices.get(device_name)
        if dev is None:
            return {"voltage": None, "current": None}
        voltage = current = None
        try:
            if hasattr(dev, "get_voltage_setpoint"):
                voltage = dev.get_voltage_setpoint()
        except Exception:
            pass
        try:
            if hasattr(dev, "get_current_limit"):
                current = dev.get_current_limit()
        except Exception:
            pass
        return {"voltage": voltage, "current": current}

    def update_awg_state(self, device_name: str, channel: int, vpp=None, offset=None) -> None:
        key = (device_name, channel)
        self.ctx.awg_channel_state.setdefault(key, {"vpp": None, "offset": None})
        if vpp is not None:
            self.ctx.awg_channel_state[key]["vpp"] = vpp
        if offset is not None:
            self.ctx.awg_channel_state[key]["offset"] = offset

    def check_awg_limits(self, device_name: str, channel: int, new_vpp=None, new_offset=None, new_freq=None) -> bool:
        device_type = re.sub(r"\d+$", "", device_name)
        limits = self.collect_limits(device_name, device_type, channel)
        if not limits:
            return True
        queried = self.query_awg_state(device_name, channel)
        vpp = new_vpp if new_vpp is not None else queried.get("vpp")
        offset = new_offset if new_offset is not None else (queried.get("offset") or 0.0)

        if vpp is None:
            vpp_limit_keys = {"vpp_upper", "vpeak_upper", "vtrough_lower", "vpeak_lower", "vtrough_upper"}
            if any(k in limits for k in vpp_limit_keys):
                self.ctx.error(
                    f"Safety: AWG CH{channel} amplitude unknown — specify amp= to confirm it is within limits"
                )
                return False
            vpp = 0.0

        if "vpp_upper" in limits and vpp > limits["vpp_upper"]:
            self.ctx.error(f"Safety limit exceeded: AWG Vpp {vpp}V > {limits['vpp_upper']}V")
            return False

        if new_freq is not None:
            if "freq_upper" in limits and new_freq > limits["freq_upper"]:
                self.ctx.error(f"Safety limit exceeded: AWG freq {new_freq}Hz > {limits['freq_upper']}Hz")
                return False
            if "freq_lower" in limits and new_freq < limits["freq_lower"]:
                self.ctx.error(f"Safety limit exceeded: AWG freq {new_freq}Hz < {limits['freq_lower']}Hz")
                return False

        peak = offset + vpp / 2.0
        trough = offset - vpp / 2.0

        if "vpeak_upper" in limits and peak > limits["vpeak_upper"]:
            self.ctx.error(f"Safety limit exceeded: AWG peak {peak:.4g}V > {limits['vpeak_upper']}V")
            return False
        if "vtrough_lower" in limits and trough < limits["vtrough_lower"]:
            self.ctx.error(f"Safety limit exceeded: AWG trough {trough:.4g}V < {limits['vtrough_lower']}V")
            return False
        if "vpeak_lower" in limits and peak < limits["vpeak_lower"]:
            self.ctx.error(f"Safety limit exceeded: AWG peak {peak:.4g}V < {limits['vpeak_lower']}V")
            return False
        if "vtrough_upper" in limits and trough > limits["vtrough_upper"]:
            self.ctx.error(f"Safety limit exceeded: AWG trough {trough:.4g}V > {limits['vtrough_upper']}V")
            return False

        return True

    def check_psu_output_allowed(self, device_name: str) -> bool:
        device_type = re.sub(r"\d+$", "", device_name)
        limits = self.collect_limits(device_name, device_type, None)
        if not limits:
            return True
        state = self.query_psu_state(device_name)
        voltage = state.get("voltage")
        current = state.get("current")
        if voltage is None and current is None:
            self.ctx.error(
                f"SAFETY BLOCKED: {device_name} output enable refused — limits are set but instrument state is unknown"
            )
            return False
        if voltage is not None:
            if "voltage_upper" in limits and voltage > limits["voltage_upper"]:
                self.ctx.error(
                    f"SAFETY BLOCKED: {device_name} voltage {voltage}V > limit {limits['voltage_upper']}V — reduce voltage before enabling output"
                )
                return False
            if "voltage_lower" in limits and voltage < limits["voltage_lower"]:
                self.ctx.error(f"SAFETY BLOCKED: {device_name} voltage {voltage}V < limit {limits['voltage_lower']}V")
                return False
        if current is not None:
            if "current_upper" in limits and current > limits["current_upper"]:
                self.ctx.error(
                    f"SAFETY BLOCKED: {device_name} current {current}A > limit {limits['current_upper']}A — reduce current limit before enabling output"
                )
                return False
            if "current_lower" in limits and current < limits["current_lower"]:
                self.ctx.error(f"SAFETY BLOCKED: {device_name} current {current}A < limit {limits['current_lower']}A")
                return False
        return True

    def check_awg_output_allowed(self, device_name: str, channel: int) -> bool:
        device_type = re.sub(r"\d+$", "", device_name)
        limits = self.collect_limits(device_name, device_type, channel)
        if not limits:
            return True
        state = self.query_awg_state(device_name, channel)
        vpp = state.get("vpp")
        offset = state.get("offset")
        freq = state.get("freq")
        if vpp is None and offset is None and freq is None:
            self.ctx.error(
                f"SAFETY BLOCKED: {device_name} ch{channel} output enable refused — limits are set but instrument state is unknown"
            )
            return False
        vpp = vpp if vpp is not None else 0.0
        offset = offset if offset is not None else 0.0
        peak = offset + vpp / 2.0
        trough = offset - vpp / 2.0
        if "vpp_upper" in limits and vpp > limits["vpp_upper"]:
            self.ctx.error(
                f"SAFETY BLOCKED: {device_name} ch{channel} Vpp {vpp}V > limit {limits['vpp_upper']}V — reduce amplitude before enabling output"
            )
            return False
        if "vpeak_upper" in limits and peak > limits["vpeak_upper"]:
            self.ctx.error(
                f"SAFETY BLOCKED: {device_name} ch{channel} peak {peak:.4g}V > limit {limits['vpeak_upper']}V — reduce amplitude/offset before enabling output"
            )
            return False
        if "vtrough_lower" in limits and trough < limits["vtrough_lower"]:
            self.ctx.error(
                f"SAFETY BLOCKED: {device_name} ch{channel} trough {trough:.4g}V < limit {limits['vtrough_lower']}V — adjust offset before enabling output"
            )
            return False
        if "vpeak_lower" in limits and peak < limits["vpeak_lower"]:
            self.ctx.error(
                f"SAFETY BLOCKED: {device_name} ch{channel} peak {peak:.4g}V < limit {limits['vpeak_lower']}V"
            )
            return False
        if "vtrough_upper" in limits and trough > limits["vtrough_upper"]:
            self.ctx.error(
                f"SAFETY BLOCKED: {device_name} ch{channel} trough {trough:.4g}V > limit {limits['vtrough_upper']}V"
            )
            return False
        if freq is not None:
            if "freq_upper" in limits and freq > limits["freq_upper"]:
                self.ctx.error(
                    f"SAFETY BLOCKED: {device_name} ch{channel} freq {freq}Hz > limit {limits['freq_upper']}Hz"
                )
                return False
            if "freq_lower" in limits and freq < limits["freq_lower"]:
                self.ctx.error(
                    f"SAFETY BLOCKED: {device_name} ch{channel} freq {freq}Hz < limit {limits['freq_lower']}Hz"
                )
                return False
        return True

    def retroactive_limit_check_all(self) -> None:
        for dev_name, dev in self.ctx.registry.devices.items():
            dev_type = re.sub(r"\d+$", "", dev_name)
            if dev_type == "psu":
                self._retro_check_psu(dev_name, dev)
            elif dev_type == "awg":
                self._retro_check_awg(dev_name, dev)

    def _retro_check_psu(self, dev_name: str, dev: Any) -> None:
        psu_state = self.query_psu_state(dev_name)
        v = psu_state.get("voltage")
        i = psu_state.get("current")
        dev_type = re.sub(r"\d+$", "", dev_name)
        limits = self.collect_limits(dev_name, dev_type, None)
        output_on = False
        try:
            if hasattr(dev, "get_output_state"):
                output_on = dev.get_output_state()
        except Exception:
            pass
        violated = False
        if v is not None:
            if "voltage_upper" in limits and v > limits["voltage_upper"]:
                violated = True
                if output_on:
                    ColorPrinter.error(
                        f"SAFETY ENFORCED: {dev_name} setpoint {v}V exceeds limit {limits['voltage_upper']}V — output auto-disabled"
                    )
                else:
                    ColorPrinter.warning(
                        f"Retroactive: {dev_name} setpoint {v}V already exceeds limit {limits['voltage_upper']}V — consider reducing output"
                    )
            if "voltage_lower" in limits and v < limits["voltage_lower"]:
                violated = True
                if output_on:
                    ColorPrinter.error(
                        f"SAFETY ENFORCED: {dev_name} setpoint {v}V below limit {limits['voltage_lower']}V — output auto-disabled"
                    )
                else:
                    ColorPrinter.warning(
                        f"Retroactive: {dev_name} setpoint {v}V already below limit {limits['voltage_lower']}V"
                    )
        if i is not None:
            if "current_upper" in limits and i > limits["current_upper"]:
                violated = True
                if output_on:
                    ColorPrinter.error(
                        f"SAFETY ENFORCED: {dev_name} current limit {i}A exceeds limit {limits['current_upper']}A — output auto-disabled"
                    )
                else:
                    ColorPrinter.warning(
                        f"Retroactive: {dev_name} current limit {i}A already exceeds limit {limits['current_upper']}A"
                    )
            if "current_lower" in limits and i < limits["current_lower"]:
                violated = True
                if output_on:
                    ColorPrinter.error(
                        f"SAFETY ENFORCED: {dev_name} current limit {i}A below limit {limits['current_lower']}A — output auto-disabled"
                    )
                else:
                    ColorPrinter.warning(
                        f"Retroactive: {dev_name} current limit {i}A already below limit {limits['current_lower']}A"
                    )
        if violated and output_on:
            with contextlib.suppress(Exception):
                dev.enable_output(False)

    def _retro_check_awg(self, dev_name: str, dev: Any) -> None:
        dev_type = re.sub(r"\d+$", "", dev_name)
        for awg_ch in (1, 2):
            queried = self.query_awg_state(dev_name, awg_ch)
            limits = self.collect_limits(dev_name, dev_type, awg_ch)
            if not limits:
                continue
            vpp = queried.get("vpp")
            offset = queried.get("offset")
            freq = queried.get("freq")
            if vpp is None and offset is None and freq is None:
                continue
            vpp_val = vpp if vpp is not None else 0.0
            offset_val = offset if offset is not None else 0.0
            peak = offset_val + vpp_val / 2.0
            trough = offset_val - vpp_val / 2.0
            ch_on = False
            try:
                if hasattr(dev, "get_output_state"):
                    ch_on = dev.get_output_state(awg_ch)
            except Exception:
                pass
            violated = False
            if vpp is not None and "vpp_upper" in limits and vpp_val > limits["vpp_upper"]:
                violated = True
                if ch_on:
                    ColorPrinter.error(
                        f"SAFETY ENFORCED: {dev_name} ch{awg_ch} Vpp {vpp_val}V exceeds limit {limits['vpp_upper']}V — output auto-disabled"
                    )
                else:
                    ColorPrinter.warning(
                        f"Retroactive: {dev_name} ch{awg_ch} Vpp {vpp_val}V already exceeds limit {limits['vpp_upper']}V"
                    )
            if "vpeak_upper" in limits and peak > limits["vpeak_upper"]:
                violated = True
                if ch_on:
                    ColorPrinter.error(
                        f"SAFETY ENFORCED: {dev_name} ch{awg_ch} peak {peak:.4g}V exceeds limit {limits['vpeak_upper']}V — output auto-disabled"
                    )
                else:
                    ColorPrinter.warning(
                        f"Retroactive: {dev_name} ch{awg_ch} peak {peak:.4g}V already exceeds limit {limits['vpeak_upper']}V"
                    )
            if "vtrough_lower" in limits and trough < limits["vtrough_lower"]:
                violated = True
                if ch_on:
                    ColorPrinter.error(
                        f"SAFETY ENFORCED: {dev_name} ch{awg_ch} trough {trough:.4g}V below limit {limits['vtrough_lower']}V — output auto-disabled"
                    )
                else:
                    ColorPrinter.warning(
                        f"Retroactive: {dev_name} ch{awg_ch} trough {trough:.4g}V already below limit {limits['vtrough_lower']}V"
                    )
            if vpp is not None and "vpp_lower" in limits and vpp_val < limits["vpp_lower"]:
                violated = True
                if ch_on:
                    ColorPrinter.error(
                        f"SAFETY ENFORCED: {dev_name} ch{awg_ch} Vpp {vpp_val}V below limit {limits['vpp_lower']}V — output auto-disabled"
                    )
                else:
                    ColorPrinter.warning(
                        f"Retroactive: {dev_name} ch{awg_ch} Vpp {vpp_val}V already below limit {limits['vpp_lower']}V"
                    )
            if freq is not None:
                if "freq_upper" in limits and freq > limits["freq_upper"]:
                    violated = True
                    if ch_on:
                        ColorPrinter.error(
                            f"SAFETY ENFORCED: {dev_name} ch{awg_ch} freq {freq}Hz exceeds limit {limits['freq_upper']}Hz — output auto-disabled"
                        )
                    else:
                        ColorPrinter.warning(
                            f"Retroactive: {dev_name} ch{awg_ch} freq {freq}Hz already exceeds limit {limits['freq_upper']}Hz"
                        )
            elif "freq_upper" in limits or "freq_lower" in limits:
                ColorPrinter.warning(
                    f"Retroactive: {dev_name} ch{awg_ch} frequency limit set but current freq unknown — verify manually"
                )
            if violated and ch_on:
                try:
                    dev.enable_output(awg_ch, False)
                except TypeError:
                    try:
                        kw = {f"ch{awg_ch}": False}
                        dev.enable_output(**kw)
                    except Exception:
                        pass
