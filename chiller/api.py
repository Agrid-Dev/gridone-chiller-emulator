from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .schemas import ChillerSnapshot, ChillerUpdate
from .service import chiller_snapshot, update_chiller

router = APIRouter(prefix="/chiller", tags=["chiller"])


@router.get("/snapshot", response_model=ChillerSnapshot)
def get_snapshot() -> ChillerSnapshot:
    return ChillerSnapshot.model_validate(chiller_snapshot())


@router.patch("", response_model=ChillerSnapshot)
def patch_chiller(payload: ChillerUpdate) -> ChillerSnapshot:
    try:
        updated = update_chiller(
            enabled=payload.enabled,
            mode=payload.mode,
            setpoint_temperature=payload.setpoint_temperature,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ChillerSnapshot.model_validate(updated)
