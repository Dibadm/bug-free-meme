from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_health_endpoint(client: Any) -> None:
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_validate_user(client: Any) -> None:
    response = await client.post(
        "/api/v1/auth/validate",
        json={"telegram_id": 123456, "username": "testuser", "first_name": "Test"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["telegram_id"] == 123456
    assert data["username"] == "testuser"
