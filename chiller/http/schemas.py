from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ChillerSnapshot(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    enabled: bool
    unit_run_status: str
    inlet_temperature: float
    outlet_temperature: float
    mode: Literal["heat", "cool"]
    outdoor_temperature: float
    setpoint_temperature: float


class ChillerUpdate(BaseModel):
    enabled: bool | None = Field(default=None)
    mode: Literal["heat", "cool"] | None = Field(default=None)
    setpoint_temperature: float | None = Field(default=None)
