"""Deal CRUD and pipeline tests."""
import pytest
from httpx import AsyncClient


@pytest.fixture
async def auth_headers(client: AsyncClient):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "dealuser@example.com", "password": "secret123", "full_name": "Deal User"},
    )
    r = await client.post(
        "/api/v1/auth/login",
        json={"email": "dealuser@example.com", "password": "secret123"},
    )
    return {"Authorization": f"Bearer {r.json()['data']['tokens']['access_token']}"}


@pytest.fixture
async def contact_id(client: AsyncClient, auth_headers):
    r = await client.post(
        "/api/v1/contacts",
        json={"name": "Deal Contact", "email": "dealcontact@example.com"},
        headers=auth_headers,
    )
    return r.json()["data"]["id"]


@pytest.mark.asyncio
async def test_create_deal(client: AsyncClient, auth_headers, contact_id):
    r = await client.post(
        "/api/v1/deals",
        json={
            "title": "Big Deal",
            "contact_id": contact_id,
            "stage": "prospect",
            "value": 5000,
        },
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert r.json()["data"]["title"] == "Big Deal"
    assert r.json()["data"]["stage"] == "prospect"


@pytest.mark.asyncio
async def test_pipeline(client: AsyncClient, auth_headers, contact_id):
    await client.post(
        "/api/v1/deals",
        json={"title": "D1", "contact_id": contact_id, "stage": "prospect", "value": 100},
        headers=auth_headers,
    )
    r = await client.get("/api/v1/deals/pipeline", headers=auth_headers)
    assert r.status_code == 200
    assert "stages" in r.json()["data"]
