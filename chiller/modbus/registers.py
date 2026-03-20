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

# Scale factor applied to all temperature registers
TEMP_SCALE: int = 10

# --- Holding registers (R/W, FC3 read / FC6 write) ---
REG_ENABLED: int = 0  # 0 = off, 1 = on
REG_MODE: int = 1  # 1 = heat, 2 = cool
REG_SETPOINT: int = 2  # control_point

# --- Input registers (R/O, FC4 read) ---
REG_UNIT_RUN_STATUS: int = 0  # 0 = idle, 1 = run
REG_INLET_TEMP: int = 1  # inlet_temperature
REG_OUTLET_TEMP: int = 2  # outlet_temperature
REG_OUTDOOR_TEMP: int = 3  # outdoor_temperature

# --- Modbus ↔ domain mappings ---
MODE_TO_INT: dict[str, int] = {"heat": 1, "cool": 2}
INT_TO_MODE: dict[int, str] = {v: k for k, v in MODE_TO_INT.items()}

RUN_STATUS_TO_INT: dict[str, int] = {"run": 1, "idle": 0}
