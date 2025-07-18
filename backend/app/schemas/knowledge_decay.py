from pydantic import BaseModel
import uuid
from datetime import datetime

class KnowledgeDecayBase(BaseModel):
    topic: str
    last_interaction: datetime
    predicted_forget_score: float
    review_suggested: bool
    decay_model_type: str

class KnowledgeDecayCreate(KnowledgeDecayBase):
    user_id: uuid.UUID

class KnowledgeDecayOut(KnowledgeDecayBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True
