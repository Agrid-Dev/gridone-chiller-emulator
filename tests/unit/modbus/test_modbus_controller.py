from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from pymodbus.datastore.sequential import ExcCodes

from chiller.modbus.modbus_controller import (
    ModbusChillerServer,
    _HoldingRegisters,
    _InputRegisters,
)
from chiller.modbus.registers import (
    REG_ENABLED,
    REG_INLET_TEMP,
    REG_MODE,
    REG_OUTDOOR_TEMP,
    REG_OUTLET_TEMP,
    REG_SETPOINT,
    REG_UNIT_STATE,
    TEMP_SCALE,
)

if TYPE_CHECKING:
    from tests.conftest import StubChiller


@pytest.fixture
def holding(stub: StubChiller) -> _HoldingRegisters:
    return _HoldingRegisters(stub)


@pytest.fixture
def inputs(stub: StubChiller) -> _InputRegisters:
    return _InputRegisters(stub)


# --- _HoldingRegisters reads ---


def test_holding_get_enabled_reflects_snapshot(
    holding: _HoldingRegisters, stub: StubChiller
) -> None:
    stub.enabled = True
    assert holding.getValues(REG_ENABLED) == [1]


def test_holding_get_mode_reflects_snapshot(
    holding: _HoldingRegisters, stub: StubChiller
) -> None:
    stub.mode = 1
    assert holding.getValues(REG_MODE) == [1]


def test_holding_get_setpoint_is_scaled(
    holding: _HoldingRegisters, stub: StubChiller
) -> None:
    stub.setpoint_temperature = 40.0
    assert holding.getValues(REG_SETPOINT) == [400]


# --- _HoldingRegisters writes ---


def test_write_enabled_calls_set_enabled(
    holding: _HoldingRegisters, stub: StubChiller
) -> None:
    holding.setValues(REG_ENABLED, [1])
    assert stub.enabled is True


def test_write_mode_calls_set_mode(
    holding: _HoldingRegisters, stub: StubChiller
) -> None:
    holding.setValues(REG_MODE, [1])
    assert stub.mode == 1


def test_write_setpoint_scales_correctly(
    holding: _HoldingRegisters, stub: StubChiller
) -> None:
    holding.setValues(REG_SETPOINT, [255])
    assert stub.setpoint_temperature == pytest.approx(255 / TEMP_SCALE)


def test_write_invalid_mode_returns_illegal_value(
    holding: _HoldingRegisters, stub: StubChiller
) -> None:
    result = holding.setValues(REG_MODE, [99])
    assert result == ExcCodes.ILLEGAL_VALUE
    assert stub.mode == 2  # unchanged


# --- _InputRegisters reads ---


def test_input_unit_state_reflects_snapshot(
    inputs: _InputRegisters, stub: StubChiller
) -> None:
    stub.unit_state = True
    assert inputs.getValues(REG_UNIT_STATE) == [1]


def test_input_inlet_temp_is_scaled(inputs: _InputRegisters, stub: StubChiller) -> None:
    stub.inlet_temperature = 12.5
    assert inputs.getValues(REG_INLET_TEMP) == [125]


def test_input_outlet_temp_is_scaled(
    inputs: _InputRegisters, stub: StubChiller
) -> None:
    stub.outlet_temperature = 40.0
    assert inputs.getValues(REG_OUTLET_TEMP) == [400]


def test_input_outdoor_temp_is_scaled(
    inputs: _InputRegisters, stub: StubChiller
) -> None:
    stub.outdoor_temperature = 15.0
    assert inputs.getValues(REG_OUTDOOR_TEMP) == [150]


# --- ModbusChillerServer construction ---


def test_server_constructs_without_starting(stub: StubChiller) -> None:
    server = ModbusChillerServer(stub)
    assert server._context is not None
