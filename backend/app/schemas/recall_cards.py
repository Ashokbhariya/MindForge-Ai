from pydantic import BaseModel
import uuid
from datetime import datetime

class RecallCardBase(BaseModel):
    topic: str
    keywords: list[str]
    diagram_image_url: str
    analogy: str

class RecallCardCreate(RecallCardBase):
    user_id: uuid.UUID

class RecallCardOut(RecallCardBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True
