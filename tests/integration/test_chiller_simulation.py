from __future__ import annotations

from chiller.chiller import Chiller
from chiller.domain import Mode

HEAT = Mode.HEAT
COOL = Mode.COOL
DT = 1.0  # 1-second tick


def _chiller_at(temperature: float, *, setpoint: float, mode: Mode = HEAT) -> Chiller:
    """Return a Chiller whose internal temperature starts at `temperature`."""
    chiller = Chiller(mode=mode, setpoint_temperature=temperature)
    chiller.setpoint_temperature = setpoint
    return chiller


class TestChillerSimulation:
    def test_disabled_chiller_never_activates_unit(self) -> None:
        chiller = _chiller_at(30.0, setpoint=40.0)  # well below threshold (38°C)
        chiller.set_enabled(False)
        for _ in range(10):
            chiller._update(DT)
        assert chiller.snapshot().unit_run_status == "idle"

    def test_enabled_chiller_activates_below_threshold(self) -> None:
        chiller = _chiller_at(37.9, setpoint=40.0)  # 37.9 < 38.0 (= 40 - 2)
        chiller.set_enabled(True)
        chiller._update(DT)
        assert chiller.snapshot().unit_run_status == "run"

    def test_temperature_rises_when_unit_active_in_heat_mode(self) -> None:
        chiller = _chiller_at(37.9, setpoint=40.0)
        chiller.set_enabled(True)
        before = chiller.snapshot().outlet_temperature
        chiller._update(DT)
        assert chiller.snapshot().outlet_temperature > before

    def test_temperature_falls_when_unit_inactive_in_heat_mode(self) -> None:
        # Starts at setpoint — within band [38, 42] — unit stays off
        chiller = Chiller(mode=HEAT, setpoint_temperature=40.0)
        chiller.set_enabled(True)
        before = chiller.snapshot().outlet_temperature
        chiller._update(DT)
        assert chiller.snapshot().outlet_temperature < before

    def test_unit_deactivates_when_disabled(self) -> None:
        chiller = _chiller_at(37.9, setpoint=40.0)
        chiller.set_enabled(True)
        chiller._update(DT)
        assert chiller.snapshot().unit_run_status == "run"

        chiller.set_enabled(False)
        chiller._update(DT)
        assert chiller.snapshot().unit_run_status == "idle"

    def test_inlet_equals_outlet(self) -> None:
        chiller = _chiller_at(37.9, setpoint=40.0)
        chiller.set_enabled(True)
        for _ in range(20):
            chiller._update(DT)
            s = chiller.snapshot()
            assert s.inlet_temperature == s.outlet_temperature
