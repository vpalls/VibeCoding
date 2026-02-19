# Project: Customer Feedback Portal

## Architecture

```
Customer Browser ──► Flask (port 5000) ──► FastAPI (port 8000) ──► SQLite (feedback.db)
```

- **Backend:** FastAPI — REST API, data persistence, business logic
- **Frontend:** Flask — HTML pages via Jinja2 templates, calls backend over HTTP
- **Database:** SQLite file at `feedback.db` (project root)

## Key Files

| File | Purpose |
|------|---------|
| `backend/main.py` | FastAPI app, all API routes, CORS config |
| `backend/models.py` | SQLAlchemy `Feedback` ORM model + Pydantic schemas |
| `backend/database.py` | SQLite engine, `SessionLocal`, `get_db` dependency |
| `frontend/app.py` | Flask app, HTML route handlers |
| `frontend/templates/base.html` | Shared layout (Bootstrap 5, navbar, flash messages) |
| `frontend/templates/feedback.html` | Customer feedback submission form |
| `frontend/templates/admin.html` | Admin dashboard (view + respond to feedback) |

## API Endpoints (FastAPI, port 8000)

| Method | Route | Schema In | Schema Out | Notes |
|--------|-------|-----------|------------|-------|
| GET | `/health` | — | `{"status":"ok"}` | Health check |
| POST | `/feedback` | `FeedbackCreate` | `FeedbackOut` | Returns 201; rating must be 1–5 |
| GET | `/feedback` | — | `List[FeedbackOut]` | Ordered by `created_at` DESC |
| GET | `/feedback/{id}` | — | `FeedbackOut` | 404 if not found |
| POST | `/feedback/{id}/respond` | `FeedbackResponseCreate` | `FeedbackOut` | Sets `responded_at` timestamp |

## Flask Routes (port 5000)

| Method | Route | Template | Description |
|--------|-------|----------|-------------|
| GET/POST | `/` | `feedback.html` | Customer feedback form |
| GET | `/admin` | `admin.html` | Admin dashboard |
| POST | `/admin/respond/<id>` | redirects to `/admin` | Submit admin response |

## Database Schema — `feedbacks` table

| Column | Type | Constraints |
|--------|------|-------------|
| id | Integer | PK, auto-increment |
| name | String(100) | NOT NULL |
| email | String(150) | NOT NULL |
| message | Text | NOT NULL |
| rating | Integer | NOT NULL, 1–5 |
| response | Text | nullable |
| created_at | DateTime | default: `func.now()` |
| responded_at | DateTime | nullable |

## Pydantic Schemas

- `FeedbackCreate` — input for `POST /feedback`
- `FeedbackResponseCreate` — input for `POST /feedback/{id}/respond` (field: `response`)
- `FeedbackOut` — response shape for all endpoints; `from_attributes = True`

## Conventions

- **Python:** snake_case for functions and variables; PascalCase for classes
- **SQLAlchemy model:** `Feedback` class → `feedbacks` table
- **Pydantic schemas:** named with action suffix (`Create`, `Out`, `ResponseCreate`)
- **DB session:** always use `db: Session = Depends(get_db)` in FastAPI routes
- **Error responses:** `HTTPException` with appropriate status codes (404, 422)
- **Input validation:** Pydantic handles types; custom logic (e.g. rating range) in the route
- **Flask forms:** strip whitespace from all form inputs before sending to the API

## Dev Commands

```bash
# Start FastAPI backend (Terminal 1)
cd backend
uvicorn main:app --reload --port 8000

# Start Flask frontend (Terminal 2)
cd frontend
python app.py

# Interactive API docs
open http://localhost:8000/docs

# Run tests (once tests are added)
pytest backend/tests/ -v
```

## Important Notes

- CORS is locked to `http://localhost:5000` — update `allow_origins` in `main.py` for other environments
- No authentication on any endpoint — the admin dashboard is completely open
- `feedback.db` is created automatically on first backend startup
- Frontend calls backend with a 5-second timeout; connection errors show flash messages
- Do NOT use `check_same_thread=False` removal — SQLite requires it for FastAPI's async workers
