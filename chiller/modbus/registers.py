"""Modbus register map for the chiller emulator.

All addresses are 0-based. Temperature registers are int16 scaled by TEMP_SCALE.
"""

from __future__ import annotations

from chiller.domain import Mode

# Scale factor applied to all temperature registers
TEMP_SCALE: int = 10

# --- Holding registers (R/W) ---
REG_ENABLED: int = 0
REG_MODE: int = 1
REG_SETPOINT: int = 2

# --- Input registers (R/O) ---
REG_UNIT_RUN_STATUS: int = 0
REG_INLET_TEMP: int = 1
REG_OUTLET_TEMP: int = 2
REG_OUTDOOR_TEMP: int = 3

# --- Modbus ↔ domain mappings ---
MODE_TO_INT: dict[Mode, int] = {Mode.HEAT: 1, Mode.COOL: 2}
INT_TO_MODE: dict[int, Mode] = {v: k for k, v in MODE_TO_INT.items()}

RUN_STATUS_TO_INT: dict[str, int] = {"run": 1, "idle": 0}
