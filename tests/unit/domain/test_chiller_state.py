from __future__ import annotations

import pytest

from chiller.chiller import Chiller, default_setpoint_for_mode
from chiller.domain import Mode


def test_defaults_match_mode() -> None:
    chiller = Chiller()
    assert chiller.mode == Mode.COOL
    assert chiller.setpoint_temperature == default_setpoint_for_mode(Mode.COOL)


def test_set_enabled() -> None:
    chiller = Chiller()
    chiller.set_enabled(True)
    assert chiller.enabled is True


def test_set_mode_updates_default_setpoint_temperature_when_not_provided() -> None:
    chiller = Chiller()
    chiller.set_mode(Mode.HEAT)
    assert chiller.mode == Mode.HEAT
    assert chiller.setpoint_temperature == default_setpoint_for_mode(Mode.HEAT)


def test_set_mode_with_explicit_setpoint_temperature_preserves_value() -> None:
    chiller = Chiller()
    chiller.set_mode(Mode.HEAT, setpoint_temperature=30.0)
    assert chiller.mode == Mode.HEAT
    assert chiller.setpoint_temperature == 30.0


def test_invalid_mode_raises_value_error() -> None:
    chiller = Chiller()
    with pytest.raises(ValueError, match="Invalid mode"):
        chiller.set_mode("turbo")
