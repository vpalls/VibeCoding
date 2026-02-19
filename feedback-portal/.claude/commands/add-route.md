Add a new FastAPI route to `backend/main.py` for: $ARGUMENTS

Follow the existing patterns in this project:

1. **Schema first** — if the route needs new input or output shapes, add Pydantic schemas to `backend/models.py` following the naming pattern (`<Resource>Create`, `<Resource>Out`, etc.). Use `from_attributes = True` in the `Config` class for any `Out` schema.

2. **Route function** — add the route to `backend/main.py` with:
   - Correct HTTP method decorator (`@app.get`, `@app.post`, etc.)
   - `response_model=` declared
   - `db: Session = Depends(get_db)` as a parameter
   - `HTTPException(status_code=404, detail="...")` if querying by ID
   - Any custom validation (e.g. range checks) done inline before DB writes

3. **DB query patterns** — follow the existing style:
   - Single record: `db.query(Model).filter(Model.id == id).first()`
   - All records: `db.query(Model).order_by(...).all()`
   - Create: `db.add(obj)` → `db.commit()` → `db.refresh(obj)` → `return obj`
   - Update: set fields directly on the ORM object → `db.commit()` → `db.refresh(obj)`

4. **No auth needed** — the project currently has no authentication.

After writing the code, show the complete new route function and any new schemas added.
