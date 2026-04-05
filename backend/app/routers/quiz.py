from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.models.models import Question, QuizAttempt, QuizResult, ConfusionSignal, Roadmap
from app.schemas.quiz import QuizCreate, QuizSubmitRequest, QuizSubmitResponse
from app.database import get_db
from services.quiz_service import get_quiz
from uuid import UUID
from typing import Optional
import uuid

router = APIRouter()


# ── 1. Generate quiz ──────────────────────────────────────────────────────────
@router.post("/quiz/generate")
def generate_quiz(quiz_data: QuizCreate, db: Session = Depends(get_db)):
    response = get_quiz(quiz_data.topic, db, quiz_data.count)
    return JSONResponse(status_code=200, content={"questions": response})


# ── 2. Submit quiz answers ────────────────────────────────────────────────────
# FIX: user_id is now reliably stored as a string in quiz_attempts
@router.post("/quiz/submit", response_model=QuizSubmitResponse)
def submit_quiz(data: QuizSubmitRequest, db: Session = Depends(get_db)):
    serialized_answers = [
        a.model_dump() if hasattr(a, "model_dump") else a.dict()
        for a in data.answers
    ]

    attempt = QuizAttempt(
        topic=data.topic,
        selected_answers=serialized_answers,
        user_id=str(data.user_id) if data.user_id else None,  # FIX: always cast to str
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return QuizSubmitResponse(
        message="Quiz submitted successfully",
        attempt_id=attempt.id
    )


# ── 3. Get score + save QuizResult + save ConfusionSignals ───────────────────
# FIX 1: user_id resolved from attempt record reliably
# FIX 2: weak topics saved as ConfusionSignal rows
@router.get("/score/{attempt_id}")
def get_score(attempt_id: int, user_id: Optional[str] = None, db: Session = Depends(get_db)):
    attempt = db.query(QuizAttempt).filter(QuizAttempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")

    answers = attempt.selected_answers
    correct = 0
    weak_topics = []
    scored = 0

    for ans in answers:
        q_id = ans.get("question_id")
        selected = ans.get("selected_answer")
        if not q_id:
            continue
        try:
            question = db.query(Question).filter(
                Question.id == UUID(str(q_id))
            ).first()
        except Exception:
            continue

        if question is None:
            continue

        scored += 1
        if selected and selected == question.answer_text:
            correct += 1
        else:
            tag = question.concept_tags[0] if question.concept_tags else attempt.topic
            weak_topics.append(tag)

    total = scored if scored > 0 else len(answers)
    percentage = round((correct / total) * 100, 2) if total > 0 else 0

    # FIX: resolve user_id — prefer query param, fall back to stored value
    resolved_user_id = user_id or (
        str(attempt.user_id) if getattr(attempt, "user_id", None) else None
    )

    # Save quiz result with proper UUID type so filtering works
    result = QuizResult(
        user_id=UUID(resolved_user_id) if resolved_user_id else None,
        topic=attempt.topic,
        score=correct,
        total_questions=total,
    )
    db.add(result)

    # FIX: Save ConfusionSignal for each weak topic so confusion detector shows data
    if resolved_user_id and weak_topics:
        unique_weak = list(set(weak_topics))
        for topic in unique_weak:
            signal = ConfusionSignal(
                id=uuid.uuid4(),
                user_id=UUID(resolved_user_id),
                topic=topic,
                message=f"You answered questions on '{topic}' incorrectly. Review this topic.",
                confusion_score=round(1.0 - (correct / total), 2) if total > 0 else 1.0,
            )
            db.add(signal)

    db.commit()

    return {
        "score": correct,
        "total": total,
        "percentage": percentage,
        "weak_topics": list(set(weak_topics)),
    }


# ── 4. Get quiz results filtered by user_id ───────────────────────────────────
@router.get("/quiz/results")
def get_all_quiz_results(user_id: Optional[str] = Query(None), db: Session = Depends(get_db)):
    query = db.query(QuizResult)
    if user_id:
        try:
            query = query.filter(QuizResult.user_id == UUID(user_id))
        except ValueError:
            return []
    results = query.order_by(QuizResult.timestamp.asc()).all()
    return [
        {
            "topic": r.topic,
            "score": r.score,
            "total_questions": r.total_questions,
            "timestamp": r.timestamp.isoformat() if r.timestamp else None,
        }
        for r in results
    ]


# ── 5. Get confusion topics filtered by user_id ───────────────────────────────
@router.get("/quiz/confusion-topics")
def get_confusion_topics(user_id: Optional[str] = Query(None), db: Session = Depends(get_db)):
    query = db.query(ConfusionSignal)
    if user_id:
        try:
            query = query.filter(ConfusionSignal.user_id == UUID(user_id))
        except ValueError:
            return []
    signals = query.order_by(ConfusionSignal.created_at.desc()).all()
    return [
        {
            "topic": s.topic,
            "message": s.message,
            "confusion_score": s.confusion_score,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in signals
    ]


# ── 6. Roadmap history for a user ─────────────────────────────────────────────
@router.get("/roadmap/user/{user_id}/history")
def get_user_roadmap_history(user_id: UUID, db: Session = Depends(get_db)):
    roadmaps = db.query(Roadmap).filter(Roadmap.user_id == user_id).order_by(Roadmap.id.desc()).all()
    return [
        {
            "id": str(r.id),
            "topic": r.topic,
            "level": r.level,
            "description": r.description,
            "subtopics": [{"title": st.title, "description": st.description} for st in r.subtopics],
        }
        for r in roadmaps
    ]


# ── 7. Latest roadmap for a user ──────────────────────────────────────────────
@router.get("/roadmap/user/{user_id}/latest")
def get_user_latest_roadmap(user_id: UUID, db: Session = Depends(get_db)):
    roadmap = db.query(Roadmap).filter(Roadmap.user_id == user_id).order_by(Roadmap.id.desc()).first()
    if not roadmap:
        return {}
    return {
        "id": str(roadmap.id),
        "topic": roadmap.topic,
        "level": roadmap.level,
        "description": roadmap.description,
    }


# ── 8. Flashcard endpoints ─────────────────────────────────────────────────────
@router.post("/flashcard")
def generate_flashcard(data: dict, db: Session = Depends(get_db)):
    topic = data.get("topic")
    if not topic:
        raise HTTPException(status_code=400, detail="topic is required")
    question = db.query(Question).filter(Question.topic == topic).first()
    if not question:
        raise HTTPException(status_code=404, detail=f"No questions found for topic: {topic}")
    return {
        "topic": topic,
        "question": question.question_text,
        "answer": question.answer_text,
        "concept_tags": question.concept_tags,
        "difficulty": question.difficulty,
    }


@router.get("/flashcard/{topic}")
def get_flashcards(topic: str, db: Session = Depends(get_db)):
    questions = db.query(Question).filter(Question.topic == topic).all()
    if not questions:
        raise HTTPException(status_code=404, detail=f"No flashcards found for topic: {topic}")
    return [
        {
            "id": str(q.id),
            "question": q.question_text,
            "answer": q.answer_text,
            "concept_tags": q.concept_tags,
            "difficulty": q.difficulty,
        }
        for q in questions
    ]