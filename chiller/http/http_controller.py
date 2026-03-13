from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, HTTPException

from .schemas import ChillerSnapshot, ChillerUpdate

if TYPE_CHECKING:
    from chiller.domain.service import ChillerService


def create_router(chiller: ChillerService) -> APIRouter:
    """Build the chiller HTTP router bound to chiller."""
    router = APIRouter(prefix="/chiller", tags=["chiller"])

    @router.get("/snapshot", response_model=ChillerSnapshot)
    def get_snapshot() -> ChillerSnapshot:
        return ChillerSnapshot.model_validate(chiller.snapshot())

    @router.patch("", response_model=ChillerSnapshot)
    def patch_chiller(payload: ChillerUpdate) -> ChillerSnapshot:
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
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return ChillerSnapshot.model_validate(updated)

    return router
