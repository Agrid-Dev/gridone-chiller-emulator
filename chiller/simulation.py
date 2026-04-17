from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from chiller.domain import Mode

REGULATION_RATE: float = 0.05  # °C/s — heat/cool rate when unit is active
HEAT_LOSS_RATE: float = 0.0002  # thermal exchange coefficient (°C/s per °C difference)
BUILDING_LOAD_RATE: float = 0.01  # °C/s — building heat exchange while circulating


def _mode_sign(mode: Mode) -> float:
    """Returns +1.0 for heat mode, -1.0 for cool mode."""
    return 1.0 if mode == "heat" else -1.0


@dataclass
class HeatLossController:
    """
    Models two heat transfer effects on the water circuit:

    1. Ambient drift (always active):
       When the unit is idle and water sits in pipes, it drifts toward the
       outdoor temperature following Newton's law of cooling:
           delta = k * (outdoor_temp - water_temp) * dt
       This gives a bounded equilibrium — water can never drift past outdoor temp.

    2. Building load (active only when the unit is circulating):
       When water is pumped through the building, it picks up heat (COOL mode)
       or loses heat (HEAT mode) at a roughly constant rate driven by the
       building's thermal demand. This is added on top of ambient drift.
    """

    ambient_rate: float = HEAT_LOSS_RATE
    building_rate: float = BUILDING_LOAD_RATE

    def delta_temperature(
        self,
        outdoor_temp: float,
        water_temp: float,
        dt: float,
        *,
        unit_circulating: bool = False,
        mode: Mode | None = None,
    ) -> float:
        # Ambient drift: always pulls water toward outdoor temperature.
        # Positive when water is colder than outdoor, negative when hotter.
        ambient = self.ambient_rate * (outdoor_temp - water_temp) * dt

        if not unit_circulating or mode is None:
            return ambient

        # Building load: constant heat exchange driven by the building demand.
        # In COOL mode the building adds heat to the cold water circuit (+).
        # In HEAT mode the building absorbs heat from the hot water circuit (-).
        building = -_mode_sign(mode) * self.building_rate * dt

        return ambient + building


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
