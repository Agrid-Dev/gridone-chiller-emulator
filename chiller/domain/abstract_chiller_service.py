from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


class InvalidInputError(ValueError):
    """Raised when a caller supplies an invalid value to the chiller."""


@dataclass(frozen=True)
class ChillerSnapshot:
    enabled: bool
    unit_state: bool
    inlet_temperature: float
    outlet_temperature: float
    mode: int
    outdoor_temperature: float
    setpoint_temperature: float


class ChillerService(ABC):
    """Abstract interface for the chiller emulator."""

    @abstractmethod
    def snapshot(self) -> ChillerSnapshot:
        """Return a snapshot of the current chiller state."""

    @abstractmethod
    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the chiller."""

    @abstractmethod
    def set_mode(self, mode: int, *, setpoint_temperature: float | None = None) -> None:
        """Set operating mode (1=heat, 2=cool)."""

    @abstractmethod
    def set_setpoint_temperature(self, setpoint_temperature: float) -> None:
        """Update the target outlet temperature."""
