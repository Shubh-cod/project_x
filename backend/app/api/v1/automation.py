"""Automation rules CRUD API."""
from uuid import UUID
from fastapi import APIRouter, Query
from app.dependencies import DBSession, CurrentUser
from app.schemas.automation_rule import (
    AutomationRuleCreate,
    AutomationRuleUpdate,
    AutomationRuleResponse,
)
from app.schemas.common import APIResponse
from app.utils.exceptions import NotFoundError
from app.services import automation_service

router = APIRouter(prefix="/automation", tags=["automation"])


@router.get("/rules", response_model=APIResponse)
async def list_rules(
    db: DBSession,
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    items, total = await automation_service.list_rules(db, user_id=current_user.id, page=page, page_size=page_size)
    pages = (total + page_size - 1) // page_size if page_size else 0
    return APIResponse(
        data={
            "items": [AutomationRuleResponse.model_validate(r) for r in items],
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": pages,
        },
        success=True,
    )


@router.post("/rules", response_model=APIResponse)
async def create_rule(
    data: AutomationRuleCreate,
    db: DBSession,
    current_user: CurrentUser,
):
    rule = await automation_service.create_rule(db, data, current_user.id)
    return APIResponse(
        data=AutomationRuleResponse.model_validate(rule),
        message="Automation rule created",
        success=True,
    )


@router.patch("/rules/{rule_id}", response_model=APIResponse)
async def update_rule(
    rule_id: UUID,
    data: AutomationRuleUpdate,
    db: DBSession,
    current_user: CurrentUser,
):
    rule = await automation_service.update_rule(db, rule_id, data, user_id=current_user.id)
    if not rule:
        raise NotFoundError("Automation rule not found")
    return APIResponse(
        data=AutomationRuleResponse.model_validate(rule),
        message="Automation rule updated",
        success=True,
    )


@router.delete("/rules/{rule_id}", response_model=APIResponse)
async def delete_rule(
    rule_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
):
    ok = await automation_service.delete_rule(db, rule_id, user_id=current_user.id)
    if not ok:
        raise NotFoundError("Automation rule not found")
    return APIResponse(message="Automation rule deleted", success=True)
