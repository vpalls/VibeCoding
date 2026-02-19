from datetime import datetime
from typing import List

import database
import models
from database import get_db
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# Create tables on startup
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Customer Feedback API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/feedback", response_model=models.FeedbackOut, status_code=201)
def create_feedback(feedback: models.FeedbackCreate, db: Session = Depends(get_db)):
    """Customer submits new feedback."""
    if not 1 <= feedback.rating <= 5:
        raise HTTPException(status_code=422, detail="Rating must be between 1 and 5.")
    db_feedback = models.Feedback(**feedback.model_dump())
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback


@app.get("/feedback", response_model=List[models.FeedbackOut])
def list_feedback(db: Session = Depends(get_db)):
    """Return all feedback, newest first."""
    return (
        db.query(models.Feedback)
        .order_by(models.Feedback.created_at.desc())
        .all()
    )


@app.get("/feedback/{feedback_id}", response_model=models.FeedbackOut)
def get_feedback(feedback_id: int, db: Session = Depends(get_db)):
    """Return a single feedback entry."""
    fb = db.query(models.Feedback).filter(models.Feedback.id == feedback_id).first()
    if not fb:
        raise HTTPException(status_code=404, detail="Feedback not found.")
    return fb


@app.delete("/feedback/{feedback_id}", status_code=204)
def delete_feedback(feedback_id: int, db: Session = Depends(get_db)):
    """Admin deletes a feedback entry."""
    fb = db.query(models.Feedback).filter(models.Feedback.id == feedback_id).first()
    if not fb:
        raise HTTPException(status_code=404, detail="Feedback not found.")
    db.delete(fb)
    db.commit()


@app.post("/feedback/{feedback_id}/respond", response_model=models.FeedbackOut)
def respond_to_feedback(
    feedback_id: int,
    body: models.FeedbackResponseCreate,
    db: Session = Depends(get_db),
):
    """Admin adds or updates the response to a feedback entry."""
    fb = db.query(models.Feedback).filter(models.Feedback.id == feedback_id).first()
    if not fb:
        raise HTTPException(status_code=404, detail="Feedback not found.")
    fb.response = body.response
    fb.responded_at = datetime.utcnow()
    db.commit()
    db.refresh(fb)
    return fb


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
