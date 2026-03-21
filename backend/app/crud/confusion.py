from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from app.models.models import ConfusionSignal, Question
from app.schemas.confusion import ConfusionCreate, ConfusionSignalCreate
import uuid


def create_confusion_signal(db: Session, data: ConfusionCreate):
    try:
        confusion = ConfusionSignal(
            id=uuid.uuid4(),
            user_id=uuid.UUID(str(data.user_id)),
            topic=data.topic,
            question_id=uuid.UUID(str(data.question_id)),
            confusion_score=data.confusion_score,
            ai_feedback=data.ai_feedback,
        )
        db.add(confusion)
        db.commit()
        db.refresh(confusion)
        return confusion
    except SQLAlchemyError as e:
        db.rollback()
        print("Error creating confusion:", e)
        raise HTTPException(status_code=500, detail="Database error while creating confusion signal")
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid UUID format for user_id or question_id")


def get_confusions_by_user(db: Session, user_id: str):
    try:
        user_uuid = uuid.UUID(str(user_id))
        return db.query(ConfusionSignal).filter(ConfusionSignal.user_id == user_uuid).all()
    except SQLAlchemyError as e:
        print("Error fetching confusions:", e)
        raise HTTPException(status_code=500, detail="Database error while fetching confusions")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format for user_id")


def evaluate_quiz_attempt(db: Session, answers: list):
    score = 0
    feedback = []

    for ans in answers:
        question = db.query(Question).filter(Question.id == ans.question_id).first()
        if question:
            is_correct = question.answer_text.strip().lower() == ans.answer.strip().lower()
            if is_correct:
                score += 1
            feedback.append({
                "question": question.question_text,
                "correct_answer": question.answer_text,
                "your_answer": ans.answer,
                "is_correct": is_correct
            })

    total = len(answers)
    percentage = (score / total) * 100 if total > 0 else 0

    return {
        "score": score,
        "total": total,
        "percentage": percentage,
        "feedback": feedback
    }


# ✅ NEW FUNCTION: Minimal confusion signal when score < 75%
def create_simple_signal(db: Session, data: ConfusionSignalCreate):
    try:
        signal = ConfusionSignal(
            id=uuid.uuid4(),
            user_id=uuid.UUID(str(data.user_id)),
            topic=data.topic,
            message=data.message  # message field added in model
        )
        db.add(signal)
        db.commit()
        db.refresh(signal)
        return signal
    except Exception as e:
        db.rollback()
        print("Error saving signal:", e)
        raise HTTPException(status_code=500, detail="Could not save confusion signal")
