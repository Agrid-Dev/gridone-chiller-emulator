from __future__ import annotations

import pytest

from chiller.domain import Mode
from chiller.simulation import (
    BUILDING_LOAD_RATE,
    HEAT_LOSS_RATE,
    REGULATION_RATE,
    HeatLossController,
    RegulationController,
)

HEAT = Mode.HEAT
COOL = Mode.COOL
DT = 1.0  # 1-second tick


class TestHeatLossController:
    # --- Ambient drift (unit idle) ---

    def test_idle_water_hotter_than_outdoor_cools_down(self) -> None:
        """Idle water above outdoor temp must lose heat — delta is negative."""
        assert (
            HeatLossController().delta_temperature(
                outdoor_temp=15.0, water_temp=45.0, dt=DT
            )
            < 0
        )

    def test_idle_water_colder_than_outdoor_warms_up(self) -> None:
        """Idle water below outdoor temp must gain heat — delta is positive."""
        assert (
            HeatLossController().delta_temperature(
                outdoor_temp=15.0, water_temp=5.0, dt=DT
            )
            > 0
        )

    def test_idle_water_equal_to_outdoor_no_change(self) -> None:
        """No heat exchange when water is already at outdoor temperature."""
        assert (
            HeatLossController().delta_temperature(
                outdoor_temp=15.0, water_temp=15.0, dt=DT
            )
            == 0.0
        )

    def test_idle_ambient_magnitude(self) -> None:
        """Ambient delta equals k * |outdoor - water| * dt."""
        ctrl = HeatLossController()
        outdoor, water = 15.0, 45.0
        expected = pytest.approx(HEAT_LOSS_RATE * abs(outdoor - water) * DT)
        assert (
            abs(ctrl.delta_temperature(outdoor_temp=outdoor, water_temp=water, dt=DT))
            == expected
        )

    # --- Building load (unit circulating) ---

    def test_circulating_cool_mode_adds_heat(self) -> None:
        """While circulating in COOL mode the building adds heat — delta is greater than ambient alone."""
        ctrl = HeatLossController()
        idle_delta = ctrl.delta_temperature(outdoor_temp=15.0, water_temp=10.0, dt=DT)
        circ_delta = ctrl.delta_temperature(
            outdoor_temp=15.0, water_temp=10.0, dt=DT, unit_circulating=True, mode=COOL
        )
        assert circ_delta > idle_delta

    def test_circulating_heat_mode_removes_heat(self) -> None:
        """While circulating in HEAT mode the building absorbs heat — delta is less than ambient alone."""
        ctrl = HeatLossController()
        idle_delta = ctrl.delta_temperature(outdoor_temp=15.0, water_temp=40.0, dt=DT)
        circ_delta = ctrl.delta_temperature(
            outdoor_temp=15.0, water_temp=40.0, dt=DT, unit_circulating=True, mode=HEAT
        )
        assert circ_delta < idle_delta

    def test_circulating_building_load_magnitude(self) -> None:
        """Building load component equals BUILDING_LOAD_RATE * dt on top of ambient."""
        ctrl = HeatLossController()
        outdoor, water = 15.0, 10.0
        ambient = ctrl.delta_temperature(outdoor_temp=outdoor, water_temp=water, dt=DT)
        circ = ctrl.delta_temperature(
            outdoor_temp=outdoor,
            water_temp=water,
            dt=DT,
            unit_circulating=True,
            mode=COOL,
        )
        assert circ - ambient == pytest.approx(BUILDING_LOAD_RATE * DT)


class TestRegulationController:
    # heat mode

    def test_heat_activates_below_lower_threshold(self) -> None:
        """Unit turns ON when temp drops below setpoint - hysteresis."""
        ctrl = RegulationController()
        delta = ctrl.delta_temperature(
            setpoint=40.0, temperature=37.9, mode=HEAT, dt=DT
        )
        assert ctrl.is_active
        assert delta > 0

    def test_heat_stays_inactive_within_band(self) -> None:
        """No activation when temperature is inside the hysteresis band."""
        ctrl = RegulationController()
        ctrl.delta_temperature(setpoint=40.0, temperature=39.0, mode=HEAT, dt=DT)
        assert not ctrl.is_active

    def test_heat_deactivates_above_upper_threshold(self) -> None:
        """Unit turns OFF when temp exceeds setpoint + hysteresis."""
        ctrl = RegulationController()
        ctrl.delta_temperature(setpoint=40.0, temperature=37.9, mode=HEAT, dt=DT)
        assert ctrl.is_active
        ctrl.delta_temperature(setpoint=40.0, temperature=42.1, mode=HEAT, dt=DT)
        assert not ctrl.is_active

    def test_heat_active_returns_positive_delta(self) -> None:
        ctrl = RegulationController()
        delta = ctrl.delta_temperature(
            setpoint=40.0, temperature=37.9, mode=HEAT, dt=DT
        )
        assert delta == pytest.approx(REGULATION_RATE * DT)

    # cool mode

    def test_cool_activates_above_upper_threshold(self) -> None:
        """Unit turns ON when temp rises above setpoint + hysteresis."""
        ctrl = RegulationController()
        delta = ctrl.delta_temperature(
            setpoint=10.0, temperature=12.1, mode=COOL, dt=DT
        )
        assert ctrl.is_active
        assert delta < 0

    def test_cool_stays_inactive_within_band(self) -> None:
        ctrl = RegulationController()
        ctrl.delta_temperature(setpoint=10.0, temperature=11.0, mode=COOL, dt=DT)
        assert not ctrl.is_active

    def test_cool_deactivates_below_lower_threshold(self) -> None:
        """Unit turns OFF when temp drops below setpoint - hysteresis."""
        ctrl = RegulationController()
        ctrl.delta_temperature(setpoint=10.0, temperature=12.1, mode=COOL, dt=DT)
        assert ctrl.is_active
        ctrl.delta_temperature(setpoint=10.0, temperature=7.9, mode=COOL, dt=DT)
        assert not ctrl.is_active

    def test_cool_active_returns_negative_delta(self) -> None:
        ctrl = RegulationController()
        delta = ctrl.delta_temperature(
            setpoint=10.0, temperature=12.1, mode=COOL, dt=DT
        )
        assert delta == pytest.approx(-REGULATION_RATE * DT)

    # reset

    def test_reset_deactivates_active_controller(self) -> None:
        ctrl = RegulationController()
        ctrl.delta_temperature(setpoint=40.0, temperature=37.9, mode=HEAT, dt=DT)
        assert ctrl.is_active
        ctrl.reset()
        assert not ctrl.is_active

    def test_inactive_controller_returns_zero_delta(self) -> None:
        ctrl = RegulationController()
        delta = ctrl.delta_temperature(
            setpoint=40.0, temperature=40.0, mode=HEAT, dt=DT
        )
        assert delta == 0.0
