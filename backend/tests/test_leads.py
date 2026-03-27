"""Lead CRUD and convert tests."""
import pytest
from httpx import AsyncClient


@pytest.fixture
async def auth_headers(client: AsyncClient):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "leaduser@example.com", "password": "secret123", "full_name": "Lead User"},
    )
    r = await client.post(
        "/api/v1/auth/login",
        json={"email": "leaduser@example.com", "password": "secret123"},
    )
    token = r.json()["data"]["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def contact_id(client: AsyncClient, auth_headers):
    r = await client.post(
        "/api/v1/contacts",
        json={"name": "Lead Contact", "email": "leadcontact@example.com"},
        headers=auth_headers,
    )
    return r.json()["data"]["id"]


@pytest.mark.asyncio
async def test_create_lead(client: AsyncClient, auth_headers, contact_id):
    r = await client.post(
        "/api/v1/leads",
        json={
            "title": "Big Deal Lead",
            "contact_id": contact_id,
            "source": "web",
            "status": "new",
        },
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert r.json()["data"]["title"] == "Big Deal Lead"
    assert r.json()["data"]["status"] == "new"


@pytest.mark.asyncio
async def test_list_leads(client: AsyncClient, auth_headers, contact_id):
    await client.post(
        "/api/v1/leads",
        json={"title": "Lead 1", "contact_id": contact_id},
        headers=auth_headers,
    )
    r = await client.get("/api/v1/leads", headers=auth_headers)
    assert r.status_code == 200
    assert "items" in r.json()["data"]


@pytest.mark.asyncio
async def test_convert_lead(client: AsyncClient, auth_headers, contact_id):
    lr = await client.post(
        "/api/v1/leads",
        json={"title": "Convert Me", "contact_id": contact_id},
        headers=auth_headers,
    )
    lead_id = lr.json()["data"]["id"]
    r = await client.post(
        f"/api/v1/leads/{lead_id}/convert",
        json={"create_deal": True, "deal_title": "First Deal", "deal_value": 1000},
        headers=auth_headers,
    )
    assert r.status_code == 200
    data = r.json()["data"]
    assert "contact" in data
    assert "deal" in data
