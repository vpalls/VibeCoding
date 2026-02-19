Write pytest tests for the selected code or for: $ARGUMENTS

This project has no tests yet. Create them in `backend/tests/`.

## Setup to include (only once, in `backend/tests/conftest.py` if it doesn't exist)

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from database import Base, get_db

TEST_DATABASE_URL = "sqlite:///./test_feedback.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
```

## Test patterns to follow

- Use `client.post(...)`, `client.get(...)` from the `client` fixture
- Assert `response.status_code` first, then `response.json()` fields
- Test the happy path, then edge cases (missing fields, invalid rating, 404s)
- Name tests `test_<action>_<scenario>` e.g. `test_create_feedback_invalid_rating`

## Existing endpoints to cover if not specified

- `POST /feedback` — valid submission, rating out of range (0, 6), missing fields
- `GET /feedback` — empty list, multiple items ordered newest first
- `GET /feedback/{id}` — found, not found (404)
- `POST /feedback/{id}/respond` — success, not found (404), sets `responded_at`

Write the full test file content ready to save.
