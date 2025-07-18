from pydantic import BaseModel

class RoadmapRequest(BaseModel):
    prompt: str
    level: str  # like "beginner", "intermediate", "advanced"
