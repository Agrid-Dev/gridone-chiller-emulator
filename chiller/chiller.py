from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field

from chiller.domain import ChillerService, ChillerSnapshot, InvalidInputError
from chiller.simulation import HeatLossController, RegulationController

VALID_MODES = (1, 2)
OUTDOOR_TEMPERATURE: float = 15.0


def default_setpoint_for_mode(mode: int) -> float:
    if mode not in VALID_MODES:
        msg = f"Invalid mode {mode!r}, expected one of {VALID_MODES}"
        raise InvalidInputError(msg)
    return 40.0 if mode == 1 else 10.0


@dataclass
class Chiller(ChillerService):
    enabled: bool = False
    mode: int = field(default=2)
    setpoint_temperature: float = field(
        default_factory=lambda: default_setpoint_for_mode(2)
    )

    # Simulation state
    _temperature: float = field(default=0.0, init=False, repr=False)
    _unit_state: bool = field(default=False, init=False, repr=False)

    # Controllers
    _regulation: RegulationController = field(
        default_factory=RegulationController, init=False, repr=False
    )
    _heat_loss: HeatLossController = field(
        default_factory=HeatLossController, init=False, repr=False
    )
    _lock: threading.RLock = field(
        default_factory=threading.RLock, init=False, repr=False
    )

    def __post_init__(self) -> None:
        self._temperature = self.setpoint_temperature

    # Simulation core

    def _update(self, dt: float) -> None:
        with self._lock:
            if self.enabled:
                delta_reg = self._regulation.delta_temperature(
                    self.setpoint_temperature, self._temperature, self.mode, dt
                )
                self._unit_state = self._regulation.is_active
            else:
                delta_reg = 0.0
                self._unit_state = False
                self._regulation.reset()

            delta_loss = self._heat_loss.delta_temperature(self.mode, dt)
            self._temperature += delta_reg + delta_loss

    def run(self, interval: float = 1.0) -> None:
        """Start the simulation loop."""
        while True:
            self._update(interval)
            time.sleep(interval)

    # Public setters

    def set_enabled(self, enabled: bool) -> None:
        with self._lock:
            self.enabled = enabled

    def set_mode(self, mode: int, *, setpoint_temperature: float | None = None) -> None:
        if mode not in VALID_MODES:
            msg = f"Invalid mode {mode!r}, expected one of {VALID_MODES}"
            raise InvalidInputError(msg)
        with self._lock:
            self.mode = mode
            self.setpoint_temperature = (
                setpoint_temperature
                if setpoint_temperature is not None
                else default_setpoint_for_mode(mode)
            )
            self._regulation.reset()

    def set_setpoint_temperature(self, setpoint_temperature: float) -> None:
        with self._lock:
            self.setpoint_temperature = setpoint_temperature

    # Snapshot

    def snapshot(self) -> ChillerSnapshot:
        with self._lock:
            return ChillerSnapshot(
                enabled=self.enabled,
                unit_state=self._unit_state,
                inlet_temperature=self._temperature,
                outlet_temperature=self._temperature,
                mode=self.mode,
                outdoor_temperature=OUTDOOR_TEMPERATURE,
                setpoint_temperature=self.setpoint_temperature,
            )
