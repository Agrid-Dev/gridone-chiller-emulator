from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ChillerSnapshot(BaseModel):
    enabled: bool
    unit_state: bool
    inlet_temperature: float
    outlet_temperature: float
    mode: Literal[1, 2]
    outdoor_temperature: float
    setpoint_temperature: float


class ChillerUpdate(BaseModel):
    enabled: bool | None = Field(default=None)
    mode: Literal[1, 2] | None = Field(default=None)
    setpoint_temperature: float | None = Field(default=None)
