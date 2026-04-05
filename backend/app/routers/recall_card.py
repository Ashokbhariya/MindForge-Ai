from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from pydantic import BaseModel
from typing import List, Optional
import json

from app.schemas.recall_cards import RecallCardCreate, RecallCardOut
from app.crud import recall_cards
from app.database import get_db
from app.groq_llm import generate_summary_for_topic, generate_flashcard_for_topic

router = APIRouter(tags=["Recall Cards"])


class SummaryRequest(BaseModel):
    topic: str


class SummaryResponse(BaseModel):
    topic: str
    overview: str
    points: List[str]
    keywords: List[str]
    use_cases: List[str]
    analogy: str
    tip: str


class FlashcardResponse(BaseModel):
    front_title: str
    front_subtitle: str
    back_definition: str
    back_points: List[str]
    back_analogy: str
    keywords: List[str]


@router.post("/", response_model=RecallCardOut)
def create_card(card_data: RecallCardCreate, db: Session = Depends(get_db)):
    return recall_cards.create_recall_card(db, card_data)


@router.post("/generate", response_model=FlashcardResponse)
def generate_recall_card(card_data: RecallCardCreate, db: Session = Depends(get_db)):
    try:
        fc = generate_flashcard_for_topic(card_data.topic)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")

    recall_cards.create_recall_card(
        db,
        RecallCardCreate(
            user_id=card_data.user_id,
            topic=card_data.topic,
            keywords=fc.get("keywords", [card_data.topic]),
            diagram_image_url=f"https://dummyimage.com/600x400/000/fff&text={card_data.topic.replace(' ', '+')}",
            analogy=fc.get("back_analogy", ""),
        ),
    )

    return FlashcardResponse(
        front_title=fc.get("front_title", card_data.topic),
        front_subtitle=fc.get("front_subtitle", ""),
        back_definition=fc.get("back_definition", ""),
        back_points=fc.get("back_points", []),
        back_analogy=fc.get("back_analogy", ""),
        keywords=fc.get("keywords", []),
    )


@router.post("/summary", response_model=SummaryResponse)
def generate_summary(request: SummaryRequest):
    if not request.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty")
    try:
        raw = generate_summary_for_topic(request.topic)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")

    # Try parsing as rich JSON first
    try:
        data = json.loads(raw)
        return SummaryResponse(
            topic=request.topic,
            overview=data.get("overview", ""),
            points=data.get("points", []),
            keywords=data.get("keywords", []),
            use_cases=data.get("use_cases", []),
            analogy=data.get("analogy", ""),
            tip=data.get("tip", ""),
        )
    except Exception:
        # Fallback: parse plain text as before
        lines    = [line.strip("•-*# ").strip() for line in raw.splitlines() if line.strip()]
        analogy  = lines[0] if lines else ""
        points   = lines[1:8] if len(lines) > 1 else lines
        keywords = [p.split(":")[0].split("–")[0].strip() for p in lines[:5]]
        return SummaryResponse(
            topic=request.topic,
            overview="",
            points=points,
            keywords=keywords,
            use_cases=[],
            analogy=analogy,
            tip="",
        )


@router.get("/{user_id}", response_model=List[RecallCardOut])
def get_user_cards(user_id: UUID, db: Session = Depends(get_db)):
    return recall_cards.get_recall_cards_by_user(db, user_id)