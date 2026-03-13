from __future__ import annotations

import pytest

from chiller.domain.simulation import (
    HEAT_LOSS_RATE,
    REGULATION_RATE,
    HeatLossController,
    RegulationController,
)

HEAT = 1
COOL = 2
DT = 1.0  # 1-second tick


class TestHeatLossController:
    def test_heat_mode_returns_negative_delta(self) -> None:
        """Water cools in heat mode — loss opposes the heating direction."""
        assert HeatLossController().delta_temperature(HEAT, DT) < 0

    def test_cool_mode_returns_positive_delta(self) -> None:
        """Water warms in cool mode — loss opposes the cooling direction."""
        assert HeatLossController().delta_temperature(COOL, DT) > 0

    def test_magnitude_equals_rate_times_dt(self) -> None:
        ctrl = HeatLossController()
        expected = pytest.approx(HEAT_LOSS_RATE * DT)
        assert abs(ctrl.delta_temperature(HEAT, DT)) == expected
        assert abs(ctrl.delta_temperature(COOL, DT)) == expected

    def test_heat_and_cool_deltas_are_symmetric(self) -> None:
        ctrl = HeatLossController()
        heat = ctrl.delta_temperature(HEAT, DT)
        cool = ctrl.delta_temperature(COOL, DT)
        assert heat == pytest.approx(-cool)


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
