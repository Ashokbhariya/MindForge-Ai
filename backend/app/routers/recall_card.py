from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session  # ✅ Use sync session
from app.schemas.recall_cards import RecallCardCreate, RecallCardOut
from app.crud import recall_cards
from app.database import get_db

router = APIRouter()

@router.post("/", response_model=RecallCardOut)
def create_card(card_data: RecallCardCreate, db: Session = Depends(get_db)):
    return recall_cards.create_recall_card(db, card_data)

@router.get("/{user_id}", response_model=list[RecallCardOut])
def get_user_cards(user_id: str, db: Session = Depends(get_db)):
    return recall_cards.get_recall_cards_by_user(db, user_id)
