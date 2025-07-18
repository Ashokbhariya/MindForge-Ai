from sqlalchemy.orm import Session
from app.models.models import Question
from app.schemas.question import QuestionCreate

def create_question(db: Session, q: QuestionCreate):
    new_q = Question(**q.dict())
    db.add(new_q)
    db.commit()
    db.refresh(new_q)
    return new_q

def get_all_questions(db: Session):
    return db.query(Question).all()