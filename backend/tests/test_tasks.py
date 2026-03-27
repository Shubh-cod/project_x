"""Task CRUD and overdue tests."""
import pytest
from httpx import AsyncClient


@pytest.fixture
async def auth_headers(client: AsyncClient):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "taskuser@example.com", "password": "secret123", "full_name": "Task User"},
    )
    r = await client.post(
        "/api/v1/auth/login",
        json={"email": "taskuser@example.com", "password": "secret123"},
    )
    return {"Authorization": f"Bearer {r.json()['data']['tokens']['access_token']}"}


@pytest.mark.asyncio
async def test_create_task(client: AsyncClient, auth_headers):
    r = await client.post(
        "/api/v1/tasks",
        json={"title": "Call client", "priority": "high", "status": "todo"},
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert r.json()["data"]["title"] == "Call client"


@pytest.mark.asyncio
async def test_list_tasks(client: AsyncClient, auth_headers):
    await client.post(
        "/api/v1/tasks",
        json={"title": "Task One"},
        headers=auth_headers,
    )
    r = await client.get("/api/v1/tasks", headers=auth_headers)
    assert r.status_code == 200
    assert "items" in r.json()["data"]


@pytest.mark.asyncio
async def test_overdue_tasks(client: AsyncClient, auth_headers):
    r = await client.get("/api/v1/tasks/overdue", headers=auth_headers)
    assert r.status_code == 200
    assert isinstance(r.json()["data"], list)
