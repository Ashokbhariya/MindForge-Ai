from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.models import LearningSession
from app.schemas.learning_session import LearningSessionCreate
import uuid
from fastapi import HTTPException

def create_session(db: Session, data: LearningSessionCreate):
    try:
        session = LearningSession(
            id=uuid.uuid4(),
            user_id=data.user_id,
            topic=data.topic,
            content_type=data.content_type,
            time_spent=data.time_spent,
            retention_score=data.retention_score,
            interaction_pattern=data.interaction_pattern,
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session
    except SQLAlchemyError as e:
        db.rollback()
        print("❌ Error creating session:", e)
        raise HTTPException(status_code=500, detail="Database error while creating session")

def get_sessions_by_user(db: Session, user_id: str):
    try:
        return db.query(LearningSession).filter(LearningSession.user_id == uuid.UUID(user_id)).all()
    except SQLAlchemyError as e:
        print("❌ Error fetching sessions:", e)
        raise HTTPException(status_code=500, detail="Error fetching sessions")
