from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.learning_style import LearningStyleCreate, LearningStyleOut
from app.crud import learning_style as learning_style_crud  # <- renamed import
from app.database import get_db
from uuid import UUID

router = APIRouter(tags=["Learning Style"])

@router.post("/", response_model=LearningStyleOut)
def create_learning_style(
    style_data: LearningStyleCreate,
    db: Session = Depends(get_db)
):
    return learning_style_crud.create_learning_style(style_data, db)

@router.get("/{user_id}", response_model=LearningStyleOut)
def get_learning_style(user_id: UUID, db: Session = Depends(get_db)):
    return learning_style_crud.get_user_learning_style(user_id, db)
