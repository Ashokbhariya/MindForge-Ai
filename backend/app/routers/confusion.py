from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.confusion import ConfusionCreate, ConfusionOut
from app.crud import confusion
from app.database import get_db


router = APIRouter()

@router.post("/", response_model=ConfusionOut)
def create_confusion(conf_data: ConfusionCreate, db: Session = Depends(get_db)):
    return confusion.create_confusion_signal(db, conf_data)

@router.get("/{user_id}", response_model=list[ConfusionOut])
def get_user_confusions(user_id: str, db: Session = Depends(get_db)):
    return confusion.get_confusions_by_user(db, user_id)
