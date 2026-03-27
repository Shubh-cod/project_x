# NovaCRM Backend

A robust, high-performance CRM backend built with FastAPI, PostgreSQL, and Redis.

## 🚀 Features

- **Asynchronous API**: Built with FastAPI for high performance and modern Python features.
- **Persistent Storage**: PostgreSQL with SQLAlchemy (asyncio) for reliable data management.
- **Database Migrations**: Alembic for version-controlled database schema changes.
- **Secure Authentication**: JWT-based authentication with password hashing using bcrypt.
- **Background Jobs**: Integrated with Redis and `arq` for asynchronous task processing.
- **Rate Limiting**: Custom middleware to prevent API abuse.
- **Structured Logging**: Integrated logging for better observability.
- **Automated Testing**: Comprehensive test suite using Pytest and aiosqlite for isolated testing.

---

## 🏗️ Architecture & Folder Structure

```text
backend/
├── alembic/                # Database migration scripts
├── alembic.ini             # Alembic configuration
├── app/
│   ├── api/
│   │   └── v1/             # API Router versions
│   │       ├── auth.py     # Authentication endpoints (Login/Register)
│   │       ├── users.py    # User management
│   │       ├── contacts.py # Contact management
│   │       ├── leads.py    # Lead tracking
│   │       ├── deals.py    # Sales deal management
│   │       ├── tasks.py    # CRM task management
│   │       ├── dashboard.py# Analytics and reporting
│   │       └── ...         # Other specialized modules
│   ├── config.py           # Application settings (Pydantic Settings)
│   ├── db/                 # Database connection and base models
│   ├── models/             # SQLAlchemy ORM models
│   ├── schemas/            # Pydantic validation schemas
│   ├── redis/              # Redis client and configuration
│   ├── middleware/         # Custom FastAPI middleware (CORS, Logging, RateLimit)
│   ├── utils/              # Helper functions and exceptions
│   └── main.py             # Application entry point
├── data/                   # Local data storage (ignored by Git)
├── tests/                  # Pytest test suite
├── .env                    # Environment variables (template provided)
├── requirements.txt        # Project dependencies
└── pytest.ini              # Pytest configuration
```

---

## 🛠️ Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL
- Redis

### Setup Instructions

1. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Copy `.env` from the template provided and fill in your values:
   ```bash
   # Required variables
   DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/novacrm
   REDIS_URL=redis://localhost:6379/0
   SECRET_KEY=your-secure-secret-key
   ```

4. **Run Database Migrations**:
   ```bash
   alembic upgrade head
   ```

5. **Start the Development Server**:
   ```bash
   uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`.
Access the interactive documentation at `http://localhost:8000/docs`.

---

## 🧪 Testing

Run the test suite using Pytest:
```bash
pytest
```
The tests use `aiosqlite` for an isolated, asynchronous SQLite database to ensure the main database remains untouched.

---

## 📡 API Endpoints (v1)

| Module | Endpoint | Description |
| :--- | :--- | :--- |
| **Auth** | `/api/v1/auth/login` | Authenticate user and get JWT |
| **Auth** | `/api/v1/auth/register` | Create a new user account |
| **Contacts** | `/api/v1/contacts/` | List and create contacts |
| **Leads** | `/api/v1/leads/` | Manage sales leads |
| **Deals** | `/api/v1/deals/` | Track sales deals |
| **Tasks** | `/api/v1/tasks/` | Manage CRM follow-up tasks |
| **Health** | `/health` | Check API, DB, and Redis status |

---

## 🔐 Security & Auth

- **JWT Tokens**: Bearer token authentication.
- **CORS**: Configurable cross-origin resource sharing.
- **Rate Limiting**: Protects endpoints from brute-force and abuse.
- **Hashed Passwords**: Never stored in plain text.
