Add a new Flask route to `frontend/app.py` for: $ARGUMENTS

Follow the existing patterns in this project:

**1. Route handler**
- Use `@app.route(...)` with explicit `methods=[...]`
- Strip whitespace from all form inputs: `request.form.get("field", "").strip()`
- Wrap all `requests` calls in try/except catching `requests.exceptions.ConnectionError` separately from general exceptions
- Always use `timeout=5` on every `requests` call
- Use `flash("message", "success"|"danger"|"warning")` for user feedback
- Redirect after POST: `return redirect(url_for("route_function_name"))`

**2. API calls**
- Base URL is `API_BASE = "http://localhost:8000"` (already defined at top of `app.py`)
- Use `requests.get(f"{API_BASE}/...")` or `requests.post(..., json=payload, ...)`
- Call `resp.raise_for_status()` after every request to catch HTTP errors

**3. Template (if a new page is needed)**
- Extend `base.html`: `{% extends "base.html" %}`
- Use `{% block content %}...{% endblock %}`
- Use Bootstrap 5 classes consistent with the existing templates
- Display flash messages via `get_flashed_messages()` — already handled in `base.html`

**4. No auth required** — the project currently has no authentication.

Show the complete new route handler and any new template content needed.
