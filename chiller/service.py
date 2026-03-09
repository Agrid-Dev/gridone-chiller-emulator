from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .model import VALID_MODES, Chiller, default_setpoint_for_mode

_chiller = Chiller()


def get_chiller() -> Chiller:
    return _chiller


def chiller_snapshot() -> dict[str, Any]:
    # asdict keeps this in sync with the dataclass definition.
    return asdict(_chiller)


def update_chiller(
    *,
    enabled: bool | None = None,
    mode: int | None = None,
    setpoint_temperature: float | None = None,
) -> dict[str, Any]:
    if enabled is not None:
        _chiller.set_enabled(enabled)

    if mode is not None:
        if mode not in VALID_MODES:
            msg = f"Invalid mode {mode!r}, expected one of {VALID_MODES}"
            raise ValueError(msg)

        if setpoint_temperature is None:
            _chiller.set_mode(
                mode, setpoint_temperature=default_setpoint_for_mode(mode)
            )
        else:
            _chiller.set_mode(mode, setpoint_temperature=setpoint_temperature)
    elif setpoint_temperature is not None:
        _chiller.set_setpoint_temperature(setpoint_temperature)

    return chiller_snapshot()
