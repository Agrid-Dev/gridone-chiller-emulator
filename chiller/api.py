from __future__ import annotations

import threading

from fastapi import APIRouter, HTTPException

from .chiller import Chiller
from .schemas import ChillerSnapshot, ChillerUpdate

router = APIRouter(prefix="/chiller", tags=["chiller"])

_chiller = Chiller()


def start_simulation(interval: float = 1.0) -> None:
    """Start the chiller simulation loop in a background daemon thread."""
    thread = threading.Thread(target=_chiller.run, args=(interval,), daemon=True)
    thread.start()


@router.get("/snapshot", response_model=ChillerSnapshot)
def get_snapshot() -> ChillerSnapshot:
    return ChillerSnapshot.model_validate(_chiller.snapshot())


@router.patch("", response_model=ChillerSnapshot)
def patch_chiller(payload: ChillerUpdate) -> ChillerSnapshot:
    try:
        if payload.enabled is not None:
            _chiller.set_enabled(payload.enabled)

        if payload.mode is not None:
            _chiller.set_mode(
                payload.mode,
                setpoint_temperature=payload.setpoint_temperature,
            )
        elif payload.setpoint_temperature is not None:
            _chiller.set_setpoint_temperature(payload.setpoint_temperature)

        updated = _chiller.snapshot()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ChillerSnapshot.model_validate(updated)
