from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.models import ConfusionSignal
from app.schemas.confusion import ConfusionCreate
from fastapi import HTTPException
import uuid

def create_confusion_signal(db: Session, data: ConfusionCreate):
    confusion = ConfusionSignal(
        id=uuid.uuid4(),
        user_id=data.user_id,
        topic=data.topic,
        question_id=data.question_id,
        confusion_score=data.confusion_score,
        ai_feedback=data.ai_feedback,
    )
    try:
        db.add(confusion)
        db.commit()
        db.refresh(confusion)
        return confusion
    except SQLAlchemyError as e:
        db.rollback()
        print("Error creating confusion:", e)
        raise HTTPException(status_code=500, detail="Database error while creating confusion signal")


def get_confusions_by_user(db: Session, user_id: str):
    try:
        return db.query(ConfusionSignal).filter(ConfusionSignal.user_id == uuid.UUID(user_id)).all()
    except SQLAlchemyError as e:
        print("Error fetching confusions:", e)
        raise HTTPException(status_code=500, detail="Database error while fetching confusions")
