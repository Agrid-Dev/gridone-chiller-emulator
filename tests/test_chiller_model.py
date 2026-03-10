from __future__ import annotations

import pytest

from chiller.chiller import Chiller, default_setpoint_for_mode


def test_defaults_match_mode() -> None:
    chiller = Chiller()
    assert chiller.mode == 2
    assert chiller.setpoint_temperature == default_setpoint_for_mode(2)


def test_set_enabled() -> None:
    chiller = Chiller()
    chiller.set_enabled(True)
    assert chiller.enabled is True


def test_set_mode_updates_default_setpoint_when_not_provided() -> None:
    chiller = Chiller()
    chiller.set_mode(1)
    assert chiller.mode == 1
    assert chiller.setpoint_temperature == default_setpoint_for_mode(1)


def test_set_mode_with_explicit_setpoint_preserves_value() -> None:
    chiller = Chiller()
    chiller.set_mode(1, setpoint_temperature=30.0)
    assert chiller.mode == 1
    assert chiller.setpoint_temperature == 30.0


def test_invalid_mode_raises_value_error() -> None:
    chiller = Chiller()
    with pytest.raises(ValueError, match="Invalid mode"):
        chiller.set_mode(3)
