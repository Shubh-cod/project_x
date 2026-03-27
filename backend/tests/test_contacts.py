"""Contact CRUD tests."""
import pytest
from httpx import AsyncClient


@pytest.fixture
async def auth_headers(client: AsyncClient):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "agent@example.com", "password": "secret123", "full_name": "Agent"},
    )
    r = await client.post(
        "/api/v1/auth/login",
        json={"email": "agent@example.com", "password": "secret123"},
    )
    token = r.json()["data"]["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_create_contact(client: AsyncClient, auth_headers):
    r = await client.post(
        "/api/v1/contacts",
        json={
            "name": "Acme Corp",
            "email": "acme@example.com",
            "company": "Acme",
        },
        headers=auth_headers,
    )
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert data["data"]["name"] == "Acme Corp"
    assert data["data"]["email"] == "acme@example.com"


@pytest.mark.asyncio
async def test_list_contacts(client: AsyncClient, auth_headers):
    await client.post(
        "/api/v1/contacts",
        json={"name": "Contact One", "email": "one@example.com"},
        headers=auth_headers,
    )
    r = await client.get("/api/v1/contacts", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert "items" in data["data"]
    assert data["data"]["total"] >= 1


@pytest.mark.asyncio
async def test_get_contact(client: AsyncClient, auth_headers):
    cr = await client.post(
        "/api/v1/contacts",
        json={"name": "Get Me", "email": "get@example.com"},
        headers=auth_headers,
    )
    cid = cr.json()["data"]["id"]
    r = await client.get(f"/api/v1/contacts/{cid}", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["data"]["name"] == "Get Me"


@pytest.mark.asyncio
async def test_update_contact(client: AsyncClient, auth_headers):
    cr = await client.post(
        "/api/v1/contacts",
        json={"name": "Original", "email": "orig@example.com"},
        headers=auth_headers,
    )
    cid = cr.json()["data"]["id"]
    r = await client.patch(
        f"/api/v1/contacts/{cid}",
        json={"name": "Updated"},
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert r.json()["data"]["name"] == "Updated"


@pytest.mark.asyncio
async def test_delete_contact(client: AsyncClient, auth_headers):
    cr = await client.post(
        "/api/v1/contacts",
        json={"name": "To Delete", "email": "del@example.com"},
        headers=auth_headers,
    )
    cid = cr.json()["data"]["id"]
    r = await client.delete(f"/api/v1/contacts/{cid}", headers=auth_headers)
    assert r.status_code == 200
    r2 = await client.get(f"/api/v1/contacts/{cid}", headers=auth_headers)
    assert r2.status_code == 404
