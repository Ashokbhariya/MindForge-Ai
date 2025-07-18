from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.question import QuestionCreate, QuestionOut
from app.crud import question
from app.database import get_db

router = APIRouter(tags=["Questions"]) 

@router.post("/", response_model=QuestionOut)
def create_question(question_data: QuestionCreate, db: Session = Depends(get_db)):
    return question.create_question(db, question_data)

@router.get("/", response_model=list[QuestionOut])
def list_questions(db: Session = Depends(get_db)):
    return question.get_all_questions(db)
