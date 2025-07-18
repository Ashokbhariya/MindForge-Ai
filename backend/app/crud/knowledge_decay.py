from sqlalchemy.orm import Session
from app.models.models import KnowledgeDecayEvent
from app.schemas.knowledge_decay import KnowledgeDecayCreate
from fastapi import HTTPException
import uuid
import traceback

def create_decay_event(db: Session, data: KnowledgeDecayCreate):
    try:
        event = KnowledgeDecayEvent(
            id=uuid.uuid4(),
            user_id=data.user_id,
            topic=data.topic,
            last_interaction=data.last_interaction,
            predicted_forget_score=data.predicted_forget_score,
            review_suggested=data.review_suggested,
            decay_model_type=data.decay_model_type
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event
    except Exception as e:
        db.rollback()
        print("❌ Error in create_decay_event:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Database error while creating decay event")


def get_decay_by_user(db: Session, user_id: str):
    try:
        return db.query(KnowledgeDecayEvent).filter(KnowledgeDecayEvent.user_id == uuid.UUID(user_id)).all()
    except Exception as e:
        print("❌ Error fetching decay events:", e)
        raise HTTPException(status_code=500, detail="Error fetching decay events")
