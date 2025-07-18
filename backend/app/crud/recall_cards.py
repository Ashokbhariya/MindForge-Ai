from sqlalchemy.orm import Session
from app.models.models import RecallCard
from app.schemas.recall_cards import RecallCardCreate
from fastapi import HTTPException
import uuid
import traceback

def create_recall_card(db: Session, data: RecallCardCreate):
    try:
        new_card = RecallCard(
            id=uuid.uuid4(),
            user_id=data.user_id,
            topic=data.topic,
            keywords=data.keywords,
            diagram_image_url=data.diagram_image_url,
            analogy=data.analogy
        )
        db.add(new_card)
        db.commit()
        db.refresh(new_card)
        return new_card
    except Exception as e:
        db.rollback()
        print("❌ Error in Recall Card creation:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Error creating recall card")

def get_recall_cards_by_user(db: Session, user_id):
    try:
        return db.query(RecallCard).filter(RecallCard.user_id == user_id).all()
    except Exception as e:
        print("❌ Error fetching recall cards:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Error fetching recall cards")
