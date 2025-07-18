from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from services.roadmap_service import generate_and_save_roadmap

router = APIRouter()

class PromptInput(BaseModel):
    prompt: str
    user_id: int

@router.post("/generate-roadmap")
def generate_roadmap(data: PromptInput, db: Session = Depends(get_db)):
    try:
        roadmap = generate_and_save_roadmap(data.prompt, data.user_id, db)
        return {"status": "success", "data": roadmap}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
