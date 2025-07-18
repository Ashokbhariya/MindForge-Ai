from sqlalchemy.orm import Session
from app.models.models import LearningStyle
from app.schemas.learning_style import LearningStyleCreate
import uuid

def create_learning_style(data: LearningStyleCreate, db: Session):
    new_style = LearningStyle(
        id=uuid.uuid4(),
        user_id=data.user_id,
        dominant_style=data.dominant_style,
        style_scores=data.style_scores
    )
    db.add(new_style)
    db.commit()
    db.refresh(new_style)
    return new_style

def get_user_learning_style(user_id: uuid.UUID, db: Session):
    return db.query(LearningStyle).filter(LearningStyle.user_id == user_id).first()
