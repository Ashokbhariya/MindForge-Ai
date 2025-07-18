from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session  # ✅ Use sync session
from app.schemas.learning_session import LearningSessionCreate, LearningSessionOut
from app.crud import learning_session
from app.database import get_db

router = APIRouter()

@router.post("/", response_model=LearningSessionOut)
def create_session(session_data: LearningSessionCreate, db: Session = Depends(get_db)):
    return learning_session.create_session(db, session_data)

@router.get("/{user_id}", response_model=list[LearningSessionOut])
def get_sessions(user_id: str, db: Session = Depends(get_db)):
    return learning_session.get_sessions_by_user(db, user_id)
