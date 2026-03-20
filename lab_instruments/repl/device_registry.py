"""Device resolution, selection, and capability queries."""

import re
from typing import Any, Dict, List, Optional

from lab_instruments.src.terminal import ColorPrinter

from .capabilities import DISPLAY_NAMES, DRIVER_CAPABILITIES, Capability


class DeviceRegistry:
    """Manages connected devices and resolves device references."""

    def __init__(self) -> None:
        self.devices: Dict[str, Any] = {}
        self.selected: Optional[str] = None
        self._device_override: Optional[str] = None

    def get_device(self, name: Optional[str]) -> Optional[Any]:
        """Return a device by name, or the selected device if name is None."""
        if not self.devices:
            ColorPrinter.warning("No instruments connected. Run 'scan' first.")
            return None

        if name is None:
            if self.selected is None:
                ColorPrinter.warning("No active instrument. Use 'use <name>'.")
                return None
            return self.devices.get(self.selected)

        if name not in self.devices:
            ColorPrinter.warning(f"Unknown instrument '{name}'. Available: {list(self.devices.keys())}")
            return None
        return self.devices.get(name)

    def resolve_type(self, device_type: str) -> Optional[str]:
        """Resolve a generic device type (e.g. 'psu') to a specific name (e.g. 'psu1').

        Uses _device_override if set (from numbered-device routing like 'psu1 set 5').
        """
        if self._device_override and self._device_override in self.devices:
            return self._device_override

        pattern = re.compile(rf"^{re.escape(device_type)}\d*$")
        candidates = [name for name in self.devices if pattern.match(name)]

        if not candidates:
            return None

        if len(candidates) == 1:
            return candidates[0]

        if self.selected and self.selected in candidates:
            return self.selected

        ColorPrinter.warning(
            f"Multiple {device_type.upper()}s found: {candidates}. "
            f"Use explicit name, e.g. '{candidates[0]}'."
        )
        return None

    def get_caps(self, device_or_name: Any) -> Capability:
        """Return capability flags for a device (by instance or name string)."""
        if isinstance(device_or_name, str):
            dev = self.devices.get(device_or_name)
            if dev is None:
                return Capability.NONE
        else:
            dev = device_or_name
        class_name = type(dev).__name__
        return DRIVER_CAPABILITIES.get(class_name, Capability.NONE)

    def has_cap(self, device_or_name: Any, cap: Capability) -> bool:
        """Check if a device has a specific capability."""
        return bool(self.get_caps(device_or_name) & cap)

    def display_name(self, device_or_name: Any) -> str:
        """Return the human-readable display name for a device."""
        if isinstance(device_or_name, str):
            dev = self.devices.get(device_or_name)
            if dev is None:
                return device_or_name
        else:
            dev = device_or_name
        class_name = type(dev).__name__
        return DISPLAY_NAMES.get(class_name, class_name)

    def channels_for(self, dev: Any, base_type: str) -> Optional[List[int]]:
        """Return the list of channel numbers for a device."""
        if hasattr(dev, "CHANNEL_MAP"):
            return sorted(dev.CHANNEL_MAP.keys())
        if base_type == "scope":
            return list(range(1, getattr(dev, "num_channels", 4) + 1))
        if base_type == "psu":
            caps = self.get_caps(dev)
            if caps & Capability.PSU_MULTI_CHANNEL:
                return [1, 2, 3]
            return [1]
        if base_type == "awg":
            return [1, 2]
        return None

    def capability_error(self, device_name: str, cap: Capability, feature_desc: str) -> str:
        """Format a helpful error message when a device lacks a capability.

        Searches all connected devices for alternatives that have the required cap.
        """
        dev = self.devices.get(device_name)
        display = self.display_name(device_name)
        base_type = re.sub(r"\d+$", "", device_name)

        msg = f"{device_name} ({display}) doesn't support {feature_desc}."

        # Search for alternatives
        hints = []
        for other_name, other_dev in self.devices.items():
            if other_name == device_name:
                continue
            other_base = re.sub(r"\d+$", "", other_name)
            if other_base != base_type:
                continue
            if self.has_cap(other_dev, cap):
                other_display = self.display_name(other_dev)
                hints.append(f"{other_name} ({other_display}) supports this")

        if hints:
            msg += f"\n  Hint: {hints[0]} — try: {hints[0].split(' ')[0]}"
        else:
            msg += f"\n  No other connected {base_type.upper()} supports this feature."

        return msg

    def base_type(self, device_name: str) -> str:
        """Return the base device type ('psu', 'awg', etc.) from a name like 'psu1'."""
        return re.sub(r"\d+$", "", device_name)
