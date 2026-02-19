# Customer Feedback Portal

A two-page web application built with **FastAPI** (REST backend) and **Flask** (HTML frontend).

## Architecture

```
Customer Browser  ──►  Flask (port 5000)  ──►  FastAPI (port 8000)  ──►  SQLite DB
```

- **FastAPI** — REST API: stores and retrieves feedback from SQLite
- **Flask** — Serves the two HTML pages; calls FastAPI via HTTP

## Pages

| URL | Description |
|-----|-------------|
| `http://localhost:5000/` | Customer feedback submission form |
| `http://localhost:5000/admin` | Admin dashboard — view & respond to all feedback |

## Quick Start

### 1. Install dependencies

```bash
cd feedback-portal
pip install -r requirements.txt
```

### 2. Start the FastAPI backend (Terminal 1)

**Option A:** Using uvicorn command
```bash
cd backend
uvicorn main:app --reload --port 8000
```

**Option B:** Direct Python execution
```bash
cd backend
python main.py
```

### 3. Start the Flask frontend (Terminal 2)

```bash
cd frontend
python app.py
```

### 4. Open in browser

- Customer form → http://localhost:5000
- Admin panel  → http://localhost:5000/admin
- API docs     → http://localhost:8000/docs

## Project Structure

```
feedback-portal/
├── backend/
│   ├── main.py        # FastAPI app & API routes
│   ├── models.py      # SQLAlchemy model + Pydantic schemas
│   └── database.py    # SQLite engine & session factory
├── frontend/
│   ├── app.py         # Flask app & route handlers
│   └── templates/
│       ├── base.html      # Shared navbar / layout
│       ├── feedback.html  # Page 1 – Customer feedback form
│       └── admin.html     # Page 2 – Admin response dashboard
├── requirements.txt
└── README.md
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/feedback` | Submit new feedback |
| `GET`  | `/feedback` | List all feedback |
| `GET`  | `/feedback/{id}` | Get single feedback |
| `POST` | `/feedback/{id}/respond` | Add/update admin response |
| `DELETE` | `/feedback/{id}` | Delete a feedback entry |

## Testing

### Running Selenium UI Tests

The suite includes 26 Selenium-based UI tests validating both the customer form and admin dashboard.

**Prerequisites:**
```bash
pip install selenium webdriver-manager
```

**Start all services first:**
1. FastAPI backend on port 8000
2. Flask frontend on port 5000

**Run the tests:**
```bash
cd feedback-portal
python tests/test_ui.py
```

**Test results** are saved to `tests/TestResults_YYYYMMDD_HHMMSS.txt`

Test Coverage:
- **TC_F01–TC_F11** — Customer feedback form (submission, validation, UI interactions)
- **TC_A01–TC_A15** — Admin dashboard (stats, feedback display, responding, deletion)
