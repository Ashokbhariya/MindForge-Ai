from sqlalchemy.orm import Session
from app.models.models import Question
from app.schemas.question import QuestionCreate
import random

def create_question(db: Session, q: QuestionCreate):
    new_q = Question(**q.dict())
    db.add(new_q)
    db.commit()
    db.refresh(new_q)
    return new_q

def get_all_questions(db: Session):
    return db.query(Question).all()

def get_random_questions(db: Session, topic: str, limit: int = 5):
    questions = db.query(Question).filter(Question.topic == topic).all()
    random.shuffle(questions)
    return questions[:limit]