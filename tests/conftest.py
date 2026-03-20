from __future__ import annotations

import pytest

from chiller.chiller import OUTDOOR_TEMPERATURE
from chiller.domain import ChillerService, ChillerSnapshot, InvalidInputError, Mode


class StubChiller(ChillerService):
    """ChillerService stub for controller-level tests."""

    def __init__(self) -> None:
        self.enabled = False
        self.mode = Mode.COOL
        self.setpoint_temperature = 10.0
        self.unit_run_status = "idle"
        self.inlet_temperature = 10.0
        self.outlet_temperature = 10.0
        self.outdoor_temperature = OUTDOOR_TEMPERATURE

    def snapshot(self) -> ChillerSnapshot:
        return ChillerSnapshot(
            enabled=self.enabled,
            unit_run_status=self.unit_run_status,
            inlet_temperature=self.inlet_temperature,
            outlet_temperature=self.outlet_temperature,
            mode=self.mode,
            outdoor_temperature=self.outdoor_temperature,
            setpoint_temperature=self.setpoint_temperature,
        )

    def set_enabled(self, enabled: bool) -> None:
        self.enabled = enabled

    def set_mode(
        self, mode: Mode | str, *, setpoint_temperature: float | None = None
    ) -> None:
        try:
            mode = Mode(mode)
        except ValueError:
            msg = f"Invalid mode {mode!r}"
            raise InvalidInputError(msg) from None
        self.mode = mode
        default = 40.0 if mode == Mode.HEAT else 10.0
        self.setpoint_temperature = (
            setpoint_temperature if setpoint_temperature is not None else default
        )

    def set_setpoint_temperature(self, setpoint_temperature: float) -> None:
        self.setpoint_temperature = setpoint_temperature


@pytest.fixture
def stub() -> StubChiller:
    return StubChiller()
