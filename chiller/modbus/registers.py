"""Modbus register map for the chiller emulator.

All addresses are 0-based. Temperature registers are int16 scaled by TEMP_SCALE.

Holding registers (R/W — FC3 read, FC6 write)
----------------------------------------------
  0  REG_ENABLED           0 = off, 1 = on
  1  REG_MODE              1 = heat, 2 = cool
  2  REG_SETPOINT          setpoint_temperature * TEMP_SCALE

Input registers (R/O — FC4 read)
---------------------------------
  0  REG_UNIT_RUN_STATUS   0 = idle, 1 = run
  1  REG_INLET_TEMP        inlet_temperature * TEMP_SCALE
  2  REG_OUTLET_TEMP       outlet_temperature * TEMP_SCALE
  3  REG_OUTDOOR_TEMP      outdoor_temperature * TEMP_SCALE
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
