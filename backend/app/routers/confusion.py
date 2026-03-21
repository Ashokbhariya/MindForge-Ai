from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.confusion import ConfusionCreate, ConfusionOut, QuizAttempt
from app.crud import confusion, question
from app.database import get_db

router = APIRouter()

# --- Confusion Signal CRUD ---
@router.post("/", response_model=ConfusionOut)
def create_confusion(conf_data: ConfusionCreate, db: Session = Depends(get_db)):
    return confusion.create_confusion_signal(db, conf_data)

@router.get("/{user_id}", response_model=list[ConfusionOut])
def get_user_confusions(user_id: str, db: Session = Depends(get_db)):
    return confusion.get_confusions_by_user(db, user_id)

# --- Quiz Feature ---
@router.get("/quiz/{topic}")
def get_quiz(topic: str, db: Session = Depends(get_db)):
    return question.get_random_questions(db, topic)

@router.post("/quiz/attempt")
def attempt_quiz(attempt: QuizAttempt, db: Session = Depends(get_db)):
    return confusion.evaluate_quiz_attempt(db, attempt.answers)
