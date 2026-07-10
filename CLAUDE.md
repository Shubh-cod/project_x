# NovaCRM — Claude Code Guide

NovaCRM is a full-stack CRM application. The backend is a FastAPI API with PostgreSQL, Redis, and background workers; the frontend is a React SPA built with Vite, TypeScript, Tailwind CSS, and shadcn/ui.

## Repository Layout

```
project_x/
├── backend/                          # FastAPI API (Python 3.10+)
│   ├── app/
│   │   ├── api/v1/                   # Route handlers (thin — delegate to services)
│   │   ├── models/                   # SQLAlchemy ORM models
│   │   ├── schemas/                  # Pydantic request/response schemas
│   │   ├── services/                 # Business logic
│   │   ├── db/                       # Async engine, session, migrations base
│   │   ├── redis/                    # Redis client and cache helpers
│   │   ├── middleware/               # Logging, rate limiting
│   │   ├── workers/                  # ARQ background tasks
│   │   ├── utils/                    # Security, pagination, exceptions, enums
│   │   ├── config.py                 # Pydantic Settings (reads .env)
│   │   ├── dependencies.py           # get_db, get_current_user, role guards
│   │   └── main.py                   # App entry point
│   ├── alembic/                      # Database migrations
│   └── tests/                        # Pytest suite (in-memory SQLite)
└── frontend/
    └── nova-crm-core-main/           # React frontend (work here, not frontend/ root)
        └── src/
            ├── api/                  # API client + per-resource modules
            ├── pages/                # Route-level page components
            ├── components/           # Shared UI (ui/ = shadcn primitives)
            ├── contexts/             # React context (AuthContext)
            └── hooks/                # Custom hooks
```

## Development Commands

### Backend (`backend/`)

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # configure DATABASE_URL, REDIS_URL, SECRET_KEY
alembic upgrade head
uvicorn app.main:app --reload          # http://localhost:8000
pytest                                 # run test suite
```

API docs: `http://localhost:8000/docs`  
Health check: `GET /health`

### Frontend (`frontend/nova-crm-core-main/`)

```bash
npm install
npm run dev          # http://localhost:8080
npm run build
npm run lint
npm test             # vitest
```

Set `VITE_API_URL` (defaults to `http://localhost:8000/api/v1`).  
Backend CORS defaults to `http://localhost:3000` — update `CORS_ORIGINS` in `.env` to include port `8080` if needed.

## Architecture Conventions

### Backend: layered design

1. **Routes** (`app/api/v1/*.py`) — parse input, call service, return `APIResponse`
2. **Services** (`app/services/*.py`) — business logic, DB queries, cache invalidation, activity logging
3. **Models** (`app/models/*.py`) — SQLAlchemy ORM; all extend `BaseModel` (UUID `id`, `created_at`, `updated_at`)
4. **Schemas** (`app/schemas/*.py`) — Pydantic validation; separate Create/Update/Response types

All API responses use the standard envelope:

```python
APIResponse(data=..., message="...", success=True)
```

Paginated lists wrap items in `PaginatedResponse` inside `data`:

```python
{ "items": [...], "total": N, "page": 1, "page_size": 20, "pages": N }
```

Auth uses JWT bearer tokens. Dependencies: `CurrentUser`, `AdminUser`, `ManagerUser`, `DBSession`.

Soft deletes use `is_deleted` on models. New entities set `owner_id` from the current user.

### Frontend: API + React Query

- `src/api/client.ts` — shared fetch wrapper; handles JWT refresh on 401; unwraps `body.data`
- `src/api/*.api.ts` — one module per resource (e.g. `contacts.api.ts`)
- Pages use `@tanstack/react-query` for data fetching and mutations
- Auth state lives in `AuthContext`; tokens stored in `localStorage`
- Protected routes use `<ProtectedRoute>` wrapper in `App.tsx`
- UI primitives live in `src/components/ui/` (shadcn) — prefer reusing these over custom markup
- Path alias: `@/` → `src/`

### Adding a new feature (typical flow)

**Backend:**
1. Model in `app/models/`
2. Schemas in `app/schemas/`
3. Service functions in `app/services/`
4. Routes in `app/api/v1/`
5. Register router in `app/api/v1/router.py`
6. Alembic migration if schema changes
7. Tests in `tests/`

**Frontend:**
1. Types in `src/api/types.ts`
2. API module in `src/api/`
3. Page and/or dialog in `src/pages/` or `src/components/dialogs/`
4. Route in `App.tsx` if new page

## Domain Model

Core CRM entities: **Contacts**, **Leads**, **Deals**, **Tasks**, **Activities**, **Notes**, **Tags**, **Automation Rules**, **Email Logs**.

Relationships: contacts can have leads and deals; leads can convert to deals; tasks and activities attach to entities; notes and tags are polymorphic.

## Testing

- **Backend**: pytest with `asyncio_mode = auto`; in-memory SQLite via `aiosqlite`; Redis mocked in `conftest.py`
- **Frontend**: vitest + testing-library; example test in `src/test/`

Run backend tests before submitting API changes. Do not hit the production database in tests.

## Code Style

### Python
- Async throughout (SQLAlchemy asyncio, `async def` routes)
- Use existing custom exceptions from `app/utils/exceptions.py` (`NotFoundError`, `UnauthorizedError`, etc.)
- Invalidate Redis caches via service helpers after mutations (search, dashboard)
- Log meaningful events via `app.utils.logging.logger`

### TypeScript/React
- Functional components only
- Use `react-hook-form` + `zod` for forms
- Toast notifications via `sonner` (`toast.success`, `toast.error`)
- Debounce search inputs with `useDebounce`
- Invalidate React Query cache keys after mutations (e.g. `queryClient.invalidateQueries({ queryKey: ["contacts"] })`)

## Important Notes

- Frontend app lives in `frontend/nova-crm-core-main/`, not `frontend/` directly
- Do not commit `.env` files or secrets
- `automation_rules` table is also ensured at startup in `main.py` lifespan (additive, outside Alembic)
- API prefix is `/api/v1`; frontend client already includes this in `BASE_URL`
- Keep changes focused — match existing patterns in neighboring files rather than introducing new abstractions

## Key Files to Read First

| Area | Files |
|------|-------|
| Backend entry | `backend/app/main.py`, `backend/app/config.py` |
| Auth | `backend/app/api/v1/auth.py`, `backend/app/dependencies.py`, `frontend/.../contexts/AuthContext.tsx` |
| API pattern | `backend/app/api/v1/contacts.py`, `backend/app/services/contact_service.py` |
| Frontend routing | `frontend/nova-crm-core-main/src/App.tsx` |
| API client | `frontend/nova-crm-core-main/src/api/client.ts` |
| Page pattern | `frontend/nova-crm-core-main/src/pages/ContactsPage.tsx` |
