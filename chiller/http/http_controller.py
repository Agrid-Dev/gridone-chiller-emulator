from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request

from chiller.domain import ChillerService, InvalidInputError

from .schemas import ChillerSnapshot, ChillerUpdate


def _get_chiller(request: Request) -> ChillerService:
    return request.app.state.chiller


ChillerDep = Annotated[ChillerService, Depends(_get_chiller)]

router = APIRouter(prefix="/chiller", tags=["chiller"])


@router.get("/snapshot", response_model=ChillerSnapshot)
def get_snapshot(chiller: ChillerDep) -> ChillerSnapshot:
    return ChillerSnapshot.model_validate(chiller.snapshot())


@router.patch("", response_model=ChillerSnapshot)
def patch_chiller(payload: ChillerUpdate, chiller: ChillerDep) -> ChillerSnapshot:
    try:
        if payload.enabled is not None:
            chiller.set_enabled(payload.enabled)

        if payload.mode is not None:
            chiller.set_mode(
                payload.mode,
                setpoint_temperature=payload.setpoint_temperature,
            )
        elif payload.setpoint_temperature is not None:
            chiller.set_setpoint_temperature(payload.setpoint_temperature)

        updated = chiller.snapshot()
    except InvalidInputError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ChillerSnapshot.model_validate(updated)
