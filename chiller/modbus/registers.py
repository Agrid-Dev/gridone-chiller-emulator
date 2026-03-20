"""Modbus register map for the chiller emulator.

All addresses are 0-based. Temperature registers are int16 scaled by TEMP_SCALE.
"""

from __future__ import annotations

from chiller.domain import Mode

# Scale factor applied to all temperature registers
TEMP_SCALE: int = 10

# --- Holding registers (R/W) ---
# Index 0 is unused padding: ModbusDeviceContext adds 1 to every address before
# accessing the datastore, so client address N reads values[N+1].
REG_ENABLED: int = 1
REG_MODE: int = 2
REG_SETPOINT: int = 3

# --- Input registers (R/O) ---
REG_UNIT_RUN_STATUS: int = 1
REG_INLET_TEMP: int = 2
REG_OUTLET_TEMP: int = 3
REG_OUTDOOR_TEMP: int = 4

# --- Modbus ↔ domain mappings ---
MODE_TO_INT: dict[Mode, int] = {Mode.HEAT: 1, Mode.COOL: 2}
INT_TO_MODE: dict[int, Mode] = {v: k for k, v in MODE_TO_INT.items()}

RUN_STATUS_TO_INT: dict[str, int] = {"run": 1, "idle": 0}
