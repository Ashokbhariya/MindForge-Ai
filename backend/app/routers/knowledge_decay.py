from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.knowledge_decay import KnowledgeDecayCreate, KnowledgeDecayOut
from app.database import get_db
from app.crud import knowledge_decay

router = APIRouter()

@router.post("/", response_model=KnowledgeDecayOut)
def create_decay(data: KnowledgeDecayCreate, db: Session = Depends(get_db)):
    return knowledge_decay.create_decay_event(db, data)

@router.get("/{user_id}", response_model=list[KnowledgeDecayOut])
def get_decay(user_id: str, db: Session = Depends(get_db)):
    return knowledge_decay.get_decay_by_user(db, user_id)
