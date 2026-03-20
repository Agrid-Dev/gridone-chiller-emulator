from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from chiller.domain import Mode  # noqa: TC001 — needed at runtime by Pydantic


class ChillerSnapshot(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    enabled: bool
    unit_run_status: str
    inlet_temperature: float
    outlet_temperature: float
    mode: Mode
    outdoor_temperature: float
    setpoint_temperature: float


class ChillerUpdate(BaseModel):
    enabled: bool | None = Field(default=None)
    mode: Mode | None = Field(default=None)
    setpoint_temperature: float | None = Field(default=None)
