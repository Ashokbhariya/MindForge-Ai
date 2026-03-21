from pydantic import BaseModel
from datetime import datetime
from typing import List
from uuid import UUID

class RecallCardBase(BaseModel):
    topic: str
    keywords: List[str]
    diagram_image_url: str
    analogy: str

class RecallCardCreate(RecallCardBase):
    user_id: UUID

class RecallCardOut(RecallCardBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True  
