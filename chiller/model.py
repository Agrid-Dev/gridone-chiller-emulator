from __future__ import annotations

from dataclasses import dataclass, field

VALID_MODES = (1, 2)


def default_setpoint_for_mode(mode: int) -> float:
    if mode not in VALID_MODES:
        msg = f"Invalid mode {mode!r}, expected one of {VALID_MODES}"
        raise ValueError(msg)
    return 40.0 if mode == 1 else 10.0


@dataclass
class Chiller:
    enabled: bool = False
    unit_state: bool = False
    inlet_temperature: float = 0.0
    outlet_temperature: float = 0.0
    mode: int = field(default=2)
    outdoor_temperature: float = 0.0
    setpoint_temperature: float = field(
        default_factory=lambda: default_setpoint_for_mode(2)
    )

    def set_enabled(self, enabled: bool) -> None:
        self.enabled = enabled

    def set_mode(self, mode: int, *, setpoint_temperature: float | None = None) -> None:
        if mode not in VALID_MODES:
            msg = f"Invalid mode {mode!r}, expected one of {VALID_MODES}"
            raise ValueError(msg)

        self.mode = mode

        if setpoint_temperature is not None:
            self.setpoint_temperature = setpoint_temperature
            return

        self.setpoint_temperature = default_setpoint_for_mode(mode)

    def set_setpoint_temperature(self, setpoint_temperature: float) -> None:
        self.setpoint_temperature = setpoint_temperature

    def snapshot(self) -> dict[str, bool | float | int]:
        return {
            "enabled": self.enabled,
            "unit_state": self.unit_state,
            "inlet_temperature": self.inlet_temperature,
            "outlet_temperature": self.outlet_temperature,
            "mode": self.mode,
            "outdoor_temperature": self.outdoor_temperature,
            "setpoint_temperature": self.setpoint_temperature,
        }
