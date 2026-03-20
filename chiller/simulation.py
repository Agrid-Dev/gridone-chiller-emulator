from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from chiller.domain import Mode

REGULATION_RATE: float = 0.05  # °C/s — heat/cool rate when unit is active
HEAT_LOSS_RATE: float = 0.0002  # °C/s — constant thermal loss


def _mode_sign(mode: Mode) -> float:
    """Returns +1.0 for heat mode, -1.0 for cool mode."""
    return 1.0 if mode == "heat" else -1.0


@dataclass
class HeatLossController:
    """Constant-rate thermal loss, always active regardless of unit state."""

    rate: float = HEAT_LOSS_RATE

    def delta_temperature(self, mode: Mode, dt: float) -> float:
        return -_mode_sign(mode) * self.rate * dt


@dataclass
class RegulationController:
    """Hysteresis-based on/off controller that drives temperature toward setpoint."""

    hysteresis: float = 2.0
    rate: float = REGULATION_RATE
    _active: bool = field(default=False, init=False, repr=False)

    @property
    def is_active(self) -> bool:
        return self._active

    def reset(self) -> None:
        self._active = False

    def _update_state(self, setpoint: float, temperature: float, mode: Mode) -> None:
        sign = _mode_sign(mode)
        if sign * temperature < sign * setpoint - self.hysteresis:
            self._active = True
        elif sign * temperature > sign * setpoint + self.hysteresis:
            self._active = False

    def delta_temperature(
        self, setpoint: float, temperature: float, mode: Mode, dt: float
    ) -> float:
        self._update_state(setpoint, temperature, mode)
        if not self._active:
            return 0.0
        return _mode_sign(mode) * self.rate * dt
