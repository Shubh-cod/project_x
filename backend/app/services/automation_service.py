"""Automation service: CRUD for rules + trigger execution engine."""
import logging
from uuid import UUID
from datetime import datetime, timezone, timedelta
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.automation_rule import AutomationRule
from app.models.task import Task
from app.services.activity_service import log as activity_log
from app.utils.pagination import paginate
from app.schemas.automation_rule import AutomationRuleCreate, AutomationRuleUpdate

logger = logging.getLogger("novacrm.automation")


# ── CRUD ──────────────────────────────────────────────────────────────

async def create_rule(
    session: AsyncSession,
    data: AutomationRuleCreate,
    user_id: Optional[UUID] = None,
) -> AutomationRule:
    rule = AutomationRule(
        name=data.name,
        trigger_event=data.trigger_event,
        conditions=data.conditions,
        action_type=data.action_type,
        action_config=data.action_config,
        is_active=data.is_active,
        created_by=user_id,
    )
    session.add(rule)
    await session.flush()
    await session.refresh(rule)
    return rule


async def get_rule_by_id(session: AsyncSession, rule_id: UUID) -> AutomationRule | None:
    result = await session.execute(
        select(AutomationRule).where(AutomationRule.id == rule_id)
    )
    return result.scalar_one_or_none()


async def list_rules(
    session: AsyncSession,
    page: int = 1,
    page_size: int = 50,
) -> tuple[list[AutomationRule], int]:
    q = select(AutomationRule).order_by(AutomationRule.created_at.desc())
    return await paginate(session, q, page, page_size)


async def update_rule(
    session: AsyncSession,
    rule_id: UUID,
    data: AutomationRuleUpdate,
) -> AutomationRule | None:
    rule = await get_rule_by_id(session, rule_id)
    if not rule:
        return None
    if data.name is not None:
        rule.name = data.name
    if data.trigger_event is not None:
        rule.trigger_event = data.trigger_event
    if data.conditions is not None:
        rule.conditions = data.conditions
    if data.action_type is not None:
        rule.action_type = data.action_type
    if data.action_config is not None:
        rule.action_config = data.action_config
    if data.is_active is not None:
        rule.is_active = data.is_active
    await session.flush()
    await session.refresh(rule)
    return rule


async def delete_rule(session: AsyncSession, rule_id: UUID) -> bool:
    rule = await get_rule_by_id(session, rule_id)
    if not rule:
        return False
    await session.delete(rule)
    await session.flush()
    return True


# ── Trigger Execution ─────────────────────────────────────────────────

async def execute_trigger(
    session: AsyncSession,
    trigger_event: str,
    context: dict[str, Any],
) -> list[Task]:
    """
    Find all active rules matching trigger_event and execute their actions.
    Returns list of created tasks. Non-fatal: logs errors but doesn't raise.
    """
    created_tasks: list[Task] = []
    try:
        result = await session.execute(
            select(AutomationRule).where(
                AutomationRule.trigger_event == trigger_event,
                AutomationRule.is_active == True,
            )
        )
        rules = list(result.scalars().all())

        for rule in rules:
            try:
                if rule.action_type == "create_task":
                    task = await _execute_create_task(session, rule, context)
                    if task:
                        created_tasks.append(task)
            except Exception as e:
                logger.error(
                    f"Automation rule '{rule.name}' (id={rule.id}) failed: {e}"
                )
    except Exception as e:
        logger.error(f"execute_trigger({trigger_event}) failed: {e}")

    return created_tasks


async def _execute_create_task(
    session: AsyncSession,
    rule: AutomationRule,
    context: dict[str, Any],
) -> Task | None:
    """Create a task based on rule's action_config and trigger context."""
    config = rule.action_config or {}
    title_template = config.get("title_template", "Auto task: {trigger_event}")
    priority = config.get("priority", "medium")
    due_in_hours = config.get("due_in_hours", 24)

    # Build title from template + context
    title = title_template
    for key, val in context.items():
        title = title.replace(f"{{{key}}}", str(val) if val else "")
    title = f"[Auto] {title}"

    due_date = datetime.now(timezone.utc) + timedelta(hours=due_in_hours)

    # Determine linked entity
    linked_to_type = None
    linked_to_id = None
    if "lead_id" in context:
        linked_to_type = "lead"
        linked_to_id = context["lead_id"]
    elif "deal_id" in context:
        linked_to_type = "deal"
        linked_to_id = context["deal_id"]
    elif "contact_id" in context and context["contact_id"]:
        linked_to_type = "contact"
        linked_to_id = context["contact_id"]

    assigned_to = context.get("user_id")

    task = Task(
        title=title,
        description=f"Auto-created by rule: {rule.name}",
        due_date=due_date,
        priority=priority,
        status="todo",
        linked_to_type=linked_to_type,
        linked_to_id=linked_to_id,
        assigned_to=assigned_to,
    )
    session.add(task)
    await session.flush()

    # Log the automation activity
    entity_type = linked_to_type or "task"
    entity_id = linked_to_id or task.id
    await activity_log(
        session,
        entity_type,
        entity_id,
        "auto_task_created",
        assigned_to,
        {
            "task_id": str(task.id),
            "task_title": title,
            "rule_name": rule.name,
            "entity_name": context.get("entity_name", title),
        },
    )

    logger.info(
        f"Automation '{rule.name}' created task '{title}' (id={task.id})"
    )
    return task


# ── Seed Default Rules ────────────────────────────────────────────────

async def seed_default_rules(session: AsyncSession) -> None:
    """Create default automation rules if none exist."""
    result = await session.execute(
        select(AutomationRule).limit(1)
    )
    if result.scalar_one_or_none() is not None:
        return  # Rules already exist, skip seeding

    defaults = [
        AutomationRuleCreate(
            name="Follow up on new lead",
            trigger_event="lead_created",
            action_type="create_task",
            action_config={
                "title_template": "Follow up: {lead_title}",
                "priority": "high",
                "due_in_hours": 24,
            },
            is_active=True,
        ),
        AutomationRuleCreate(
            name="Check stale deal",
            trigger_event="deal_stale",
            action_type="create_task",
            action_config={
                "title_template": "Check in: {deal_title}",
                "priority": "medium",
                "due_in_hours": 2,
            },
            is_active=True,
        ),
    ]
    for rule_data in defaults:
        await create_rule(session, rule_data)
    logger.info("Seeded 2 default automation rules")
