"""Full CRM flow end-to-end tests."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_full_crm_flow(client: AsyncClient):
    # 1. Register/Login
    reg_data = {
        "email": "fullflow@example.com",
        "password": "testpassword",
        "full_name": "Full Flow User",
    }
    await client.post("/api/v1/auth/register", json=reg_data)
    
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "fullflow@example.com", "password": "testpassword"},
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["data"]["tokens"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Dashboard
    dash_resp = await client.get("/api/v1/dashboard", headers=headers)
    assert dash_resp.status_code == 200
    assert dash_resp.json()["success"] is True

    # 3. Create Contact
    contact_data = {
        "name": "Jane Smith",
        "email": "jane@example.com",
        "company": "Tech Solutions",
    }
    contact_resp = await client.post("/api/v1/contacts", json=contact_data, headers=headers)
    assert contact_resp.status_code == 200
    contact_id = contact_resp.json()["data"]["id"]

    # 4. Create Lead
    lead_data = {
        "title": "Cloud Migration",
        "contact_id": contact_id,
        "source": "website",
        "status": "new",
        "priority": "medium",
        "estimated_value": 15000.0,
    }
    lead_resp = await client.post("/api/v1/leads", json=lead_data, headers=headers)
    assert lead_resp.status_code == 200
    lead_id = lead_resp.json()["data"]["id"]

    # 5. Create Deal
    deal_data = {
        "title": "Cloud Migration - Phase 1",
        "contact_id": contact_id,
        "lead_id": lead_id,
        "stage": "prospect",
        "value": 5000.0,
        "currency": "USD",
    }
    deal_resp = await client.post("/api/v1/deals", json=deal_data, headers=headers)
    assert deal_resp.status_code == 200
    deal_id = deal_resp.json()["data"]["id"]

    # 6. Create Task
    task_data = {
        "title": "Call Jane about Migration",
        "due_at": "2026-03-30T10:00:00Z",
        "linked_to_type": "contact",
        "linked_to_id": contact_id,
    }
    task_resp = await client.post("/api/v1/tasks", json=task_data, headers=headers)
    assert task_resp.status_code == 200

    # 7. Search
    search_resp = await client.get("/api/v1/search?q=Jane", headers=headers)
    assert search_resp.status_code == 200
    assert len(search_resp.json()["data"]["contacts"]) >= 1
