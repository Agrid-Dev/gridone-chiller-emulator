"""Modbus TCP controller for the chiller emulator."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pymodbus.datastore import (
    ModbusDeviceContext,
    ModbusSequentialDataBlock,
    ModbusServerContext,
)
from pymodbus.datastore.sequential import ExcCodes
from pymodbus.server import StartTcpServer

from chiller.domain import InvalidInputError

from .registers import (
    INT_TO_MODE,
    MODE_TO_INT,
    REG_ENABLED,
    REG_INLET_TEMP,
    REG_MODE,
    REG_OUTDOOR_TEMP,
    REG_OUTLET_TEMP,
    REG_SETPOINT,
    REG_UNIT_RUN_STATUS,
    RUN_STATUS_TO_INT,
    TEMP_SCALE,
)

if TYPE_CHECKING:
    from chiller.domain import ChillerService

_NUM_HOLDING = 4  # index 0 is unused padding (ModbusDeviceContext address+1 offset)
_NUM_INPUT = 5  # index 0 is unused padding


class _HoldingRegisters(ModbusSequentialDataBlock):
    """Holding registers (R/W). Writes are forwarded to the chiller service."""

    def __init__(self, chiller: ChillerService) -> None:
        super().__init__(0, [0] * _NUM_HOLDING)
        self._chiller = chiller

    def getValues(self, address: int, count: int = 1) -> list[int]:  # noqa: N802
        """Sync from snapshot so reads always reflect authoritative state."""
        snap = self._chiller.snapshot()
        self.values[REG_ENABLED] = int(snap.enabled)
        self.values[REG_MODE] = MODE_TO_INT[snap.mode]
        self.values[REG_SETPOINT] = round(snap.setpoint_temperature * TEMP_SCALE)
        return super().getValues(address, count)  # type: ignore[return-value]  # ty: ignore[invalid-return-type]

    def setValues(self, address: int, values: list[int]) -> None | ExcCodes:  # noqa: N802
        """Write to the chiller service; return ILLEGAL_VALUE on validation error."""
        if not isinstance(values, list):
            values = [values]
        for offset, raw in enumerate(values):
            reg = address + offset
            if reg == REG_MODE and int(raw) not in INT_TO_MODE:
                return ExcCodes.ILLEGAL_VALUE
            try:
                if reg == REG_ENABLED:
                    self._chiller.set_enabled(bool(raw))
                elif reg == REG_MODE:
                    self._chiller.set_mode(INT_TO_MODE[int(raw)])
                elif reg == REG_SETPOINT:
                    self._chiller.set_setpoint_temperature(raw / TEMP_SCALE)
            except InvalidInputError:
                return ExcCodes.ILLEGAL_VALUE
        return super().setValues(address, values)


class _InputRegisters(ModbusSequentialDataBlock):
    """Input registers (R/O). Always reflects the live chiller snapshot."""

    def __init__(self, chiller: ChillerService) -> None:
        super().__init__(0, [0] * _NUM_INPUT)
        self._chiller = chiller

    def getValues(self, address: int, count: int = 1) -> list[int]:  # noqa: N802
        snap = self._chiller.snapshot()
        self.values[REG_UNIT_RUN_STATUS] = RUN_STATUS_TO_INT[snap.unit_run_status]
        self.values[REG_INLET_TEMP] = round(snap.inlet_temperature * TEMP_SCALE)
        self.values[REG_OUTLET_TEMP] = round(snap.outlet_temperature * TEMP_SCALE)
        self.values[REG_OUTDOOR_TEMP] = round(snap.outdoor_temperature * TEMP_SCALE)
        return super().getValues(address, count)  # type: ignore[return-value]  # ty: ignore[invalid-return-type]


class ModbusChillerServer:
    """Modbus TCP server bound to a ChillerService instance."""

    def __init__(self, chiller: ChillerService) -> None:
        self._context = ModbusServerContext(
            devices=ModbusDeviceContext(
                hr=_HoldingRegisters(chiller),
                ir=_InputRegisters(chiller),
            ),
            single=True,
        )

    def start(self, host: str = "0.0.0.0", port: int = 5020) -> None:  # noqa: S104
        """Start the blocking Modbus TCP server."""
        StartTcpServer(self._context, address=(host, port))
