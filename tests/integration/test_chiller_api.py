from __future__ import annotations

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_snapshot_returns_all_fields() -> None:
    response = client.get("/chiller/snapshot")
    assert response.status_code == 200
    data = response.json()
    assert set(data.keys()) == {
        "enabled",
        "unit_state",
        "inlet_temperature",
        "outlet_temperature",
        "mode",
        "outdoor_temperature",
        "setpoint_temperature",
    }


def test_can_update_enabled() -> None:
    response = client.patch("/chiller", json={"enabled": True})
    assert response.status_code == 200
    data = response.json()
    assert data["enabled"] is True


def test_mode_change_without_setpoint_uses_default() -> None:
    response = client.patch("/chiller", json={"mode": 1})
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == 1
    assert data["setpoint_temperature"] == 40.0


def test_mode_change_with_setpoint_preserves_value() -> None:
    response = client.patch("/chiller", json={"mode": 2, "setpoint_temperature": 12.5})
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == 2
    assert data["setpoint_temperature"] == 12.5


def test_invalid_mode_returns_400() -> None:
    response = client.patch("/chiller", json={"mode": 3})
    assert response.status_code == 422
