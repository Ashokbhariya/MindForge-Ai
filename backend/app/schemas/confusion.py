from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class ConfusionBase(BaseModel):
    user_id: UUID
    topic: str
    question_id: UUID
    confusion_score: float
    ai_feedback: str

class ConfusionCreate(ConfusionBase):
    pass

class ConfusionOut(ConfusionBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True  # updated for Pydantic v2


