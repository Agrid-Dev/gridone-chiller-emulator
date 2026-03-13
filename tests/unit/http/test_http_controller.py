from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from chiller.http.http_controller import create_router
from tests.conftest import StubChiller


@pytest.fixture
def client() -> TestClient:
    app = FastAPI()
    app.include_router(create_router(StubChiller()))
    return TestClient(app)


def test_snapshot_returns_all_fields(client: TestClient) -> None:
    response = client.get("/chiller/snapshot")
    assert response.status_code == 200
    assert set(response.json().keys()) == {
        "enabled",
        "unit_state",
        "inlet_temperature",
        "outlet_temperature",
        "mode",
        "outdoor_temperature",
        "setpoint_temperature",
    }


def test_can_update_enabled(client: TestClient) -> None:
    response = client.patch("/chiller", json={"enabled": True})
    assert response.status_code == 200
    assert response.json()["enabled"] is True


def test_mode_change_without_setpoint_uses_default(client: TestClient) -> None:
    response = client.patch("/chiller", json={"mode": 1})
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == 1
    assert data["setpoint_temperature"] == 40.0


def test_mode_change_with_setpoint_preserves_value(client: TestClient) -> None:
    response = client.patch("/chiller", json={"mode": 2, "setpoint_temperature": 12.5})
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == 2
    assert data["setpoint_temperature"] == 12.5


def test_invalid_mode_returns_422(client: TestClient) -> None:
    response = client.patch("/chiller", json={"mode": 3})
    assert response.status_code == 422
