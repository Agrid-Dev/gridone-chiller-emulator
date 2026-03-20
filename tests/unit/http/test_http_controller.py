from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from chiller.http.http_controller import router
from tests.conftest import StubChiller


@pytest.fixture
def client() -> TestClient:
    app = FastAPI()
    app.state.chiller = StubChiller()
    app.include_router(router)
    return TestClient(app)


def test_snapshot_returns_all_fields(client: TestClient) -> None:
    response = client.get("/chiller/snapshot")
    assert response.status_code == 200
    assert set(response.json().keys()) == {
        "enabled",
        "unit_run_status",
        "inlet_temperature",
        "outlet_temperature",
        "mode",
        "outdoor_temperature",
        "setpoint_temperature",
    }


def test_snapshot_returns_string_mode(client: TestClient) -> None:
    response = client.get("/chiller/snapshot")
    assert response.json()["mode"] == "cool"


def test_snapshot_returns_string_run_status(client: TestClient) -> None:
    response = client.get("/chiller/snapshot")
    assert response.json()["unit_run_status"] == "idle"


def test_can_update_enabled(client: TestClient) -> None:
    response = client.patch("/chiller", json={"enabled": True})
    assert response.status_code == 200
    assert response.json()["enabled"] is True


def test_mode_change_without_setpoint_temperature_uses_default(
    client: TestClient,
) -> None:
    response = client.patch("/chiller", json={"mode": "heat"})
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "heat"
    assert data["setpoint_temperature"] == 40.0


def test_mode_change_with_setpoint_temperature_preserves_value(
    client: TestClient,
) -> None:
    response = client.patch(
        "/chiller", json={"mode": "cool", "setpoint_temperature": 12.5}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "cool"
    assert data["setpoint_temperature"] == 12.5


def test_invalid_mode_returns_422(client: TestClient) -> None:
    response = client.patch("/chiller", json={"mode": "turbo"})
    assert response.status_code == 422
