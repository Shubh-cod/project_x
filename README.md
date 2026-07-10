# NovaCRM

A professional full-stack CRM platform for managing contacts, leads, deals, tasks, and sales pipelines.

## Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS, shadcn/ui, TanStack Query, Recharts |
| **Backend** | FastAPI, SQLAlchemy (async), PostgreSQL, Redis, ARQ |
| **Auth** | JWT with refresh tokens |

## Quick Start

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
# Configure .env with DATABASE_URL, REDIS_URL, SECRET_KEY
alembic upgrade head
uvicorn app.main:app --reload
```

API: `http://localhost:8000` · Docs: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend/nova-crm-core-main
npm install
npm run dev
```

App: `http://localhost:8080`

Set `VITE_API_URL=http://localhost:8000/api/v1` and update backend `CORS_ORIGINS` to include `http://localhost:8080`.

## Features

- **Contact Management** — CRUD, tags, CSV import, soft delete with cascade
- **Lead Tracking** — Status pipeline, priority, conversion to deals
- **Deal Pipeline** — Kanban view, stage tracking, probability, value analytics
- **Tasks** — Due dates, priorities, entity linking, overdue detection
- **Dashboard** — Pipeline charts, value distribution, team performance, activity feed
- **Automation** — Rule-based task creation on triggers
- **Global Search** — Cross-entity search with direct navigation
- **Dark Mode** — System-aware theme toggle

## Project Structure

```
project_x/
├── backend/          # FastAPI API
├── frontend/
│   └── nova-crm-core-main/   # React SPA
├── CLAUDE.md         # AI assistant guide
└── README.md
```

See [CLAUDE.md](./CLAUDE.md) for development conventions and architecture details.
