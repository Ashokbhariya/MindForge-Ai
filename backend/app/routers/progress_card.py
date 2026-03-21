from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import LearningSession, QuizResult, User
from uuid import UUID as UUID_Type

router = APIRouter(
    prefix="/progress-card",
    tags=["Progress Card"]
)

@router.get("/{user_id}/data")
def get_progress_data(user_id: UUID_Type, db: Session = Depends(get_db)):
    # ✅ Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 📚 Get all learning sessions
    learning_sessions = db.query(LearningSession).filter(
        LearningSession.user_id == user_id
    ).all()

    # 🏆 Get all quiz results
    quiz_results = db.query(QuizResult).filter(
        QuizResult.user_id == user_id
    ).all()

    # 📤 Send raw data (frontend will do calculations)
    return {
        "learning_sessions": [
            {
                "retention_score": s.retention_score,
                "completed": getattr(s, "completed", False)
            }
            for s in learning_sessions
        ],
        "quiz_results": [
            {"score": q.score}
            for q in quiz_results
        ]
    }
