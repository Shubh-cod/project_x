"""Auth: register, login, logout, refresh."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "secret123", "full_name": "Test User"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert data["data"]["email"] == "test@example.com"
    assert "id" in data["data"]


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "dup@example.com", "password": "secret123", "full_name": "Dup"},
    )
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": "dup@example.com", "password": "other", "full_name": "Dup2"},
    )
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "login@example.com", "password": "secret123", "full_name": "Login User"},
    )
    r = await client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "secret123"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert "data" in data
    assert "tokens" in data["data"]
    assert "access_token" in data["data"]["tokens"]


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "bad@example.com", "password": "secret123", "full_name": "Bad"},
    )
    r = await client.post(
        "/api/v1/auth/login",
        json={"email": "bad@example.com", "password": "wrong"},
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_me_requires_auth(client: AsyncClient):
    r = await client.get("/api/v1/auth/me")
    assert r.status_code == 401  # No token -> UnauthorizedError
