"""Aggregates all v1 routers."""
from fastapi import APIRouter
from app.config import get_settings
from app.api.v1 import auth, users, contacts, leads, deals, tasks, notes, tags, dashboard, search, email_logs, activities, automation

settings = get_settings()
api_router = APIRouter(prefix=settings.api_v1_prefix)

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(contacts.router)
api_router.include_router(leads.router)
api_router.include_router(deals.router)
api_router.include_router(tasks.router)
api_router.include_router(notes.router)
api_router.include_router(tags.router)
api_router.include_router(dashboard.router)
api_router.include_router(search.router)
api_router.include_router(email_logs.router)
api_router.include_router(activities.router)
api_router.include_router(automation.router)

