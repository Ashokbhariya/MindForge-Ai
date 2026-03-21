# from fastapi import APIRouter, Depends, HTTPException, Path
# from fastapi.responses import JSONResponse
# from sqlalchemy.orm import Session

# from app.schemas.quiz import QuizCreate, QuizOut, QuizSubmitRequest, QuizSubmitResponse
# from app.database import get_db
# from app.models.models import Question, QuizAttempt,QuizResult
# from services.quiz_service import get_quiz
# from datetime import datetime

# router = APIRouter()


# # ✅ 1. Generate quiz
# @router.post("/quiz/generate", response_model=QuizOut)
# def generate_quiz(quiz_data: QuizCreate, db: Session = Depends(get_db)):
#     response = get_quiz(quiz_data.topic,db,quiz_data.count)
#     return JSONResponse(status_code=200,content={"quiz": response})


# #✅ 2. Submit quiz answers
# @router.post("/quiz/submit", response_model=QuizSubmitResponse)
# def submit_quiz(data: QuizSubmitRequest, db: Session = Depends(get_db)):
#     print(data.answers)
#     attempt = QuizAttempt(
#         topic=data.topic,
#         selected_answers=data.answers
#     )
#     db.add(attempt)
#     db.commit()
#     db.refresh(attempt)

#     return QuizSubmitResponse(
#         message="Quiz submitted successfully",
#         attempt_id=attempt.id
#     )

# # we are currently not returning question ids saved in db, thats why we cant compare the results accurately. the questions fetched are not in order when comparing.

# # @router.get("/quiz/score/{attempt_id}")
# # def get_score(attempt_id: int = Path(...), db: Session = Depends(get_db)):
# #     attempt = db.query(QuizAttempt).filter(QuizAttempt.id == attempt_id).first()
# #     if not attempt:
# #         raise HTTPException(status_code=404, detail="Quiz attempt not found.")

# #     selected_answers = attempt.selected_answers  # Dict like: {"0": "Option A", ...}
# #     topic = attempt.topic

# #     # Fetch relevant questions
# #     questions = db.query(Question).filter(Question.topic == topic).all()

# #     correct = 0
# #     total = len(questions)
# #     weak_topics = []

# #     for idx, question in enumerate(questions):
# #         user_answer = selected_answers.get(str(idx))
# #         if user_answer == question.answer_text:
# #             correct += 1
# #         else:
# #             weak_topics.append(", ".join(question.concept_tags))

# #     score_percent = (correct / total) * 100

# #     return {
# #         "status": "success",
# #         "topic": topic,
# #         "score": correct,
# #         "total": total,
# #         "percentage": score_percent,
# #         "weak_topics": weak_topics
# #     }

# @router.get("/quiz/score/{attempt_id}")
# def get_score(attempt_id: int = Path(...), db: Session = Depends(get_db)):

#     attempt = db.query(QuizAttempt).filter(QuizAttempt.id == attempt_id).first()
#     if not attempt:
#         raise HTTPException(status_code=404, detail="Quiz attempt not found.")
#     print(attempt.selected_answers)
#     # selected_answers is now a list of dicts
#     selected_answers = attempt.selected_answers  # [{question_id, selected_answer}, ...]
#     topic = attempt.topic
#     # Extract all question_ids from the attempt
#     question_ids = [entry["question_id"] for entry in selected_answers]

#     # Fetch only relevant questions from DB
#     questions = db.query(Question).filter(Question.id.in_(question_ids)).all()

#     # Convert selected answers to a dictionary for quick lookup
#     answer_lookup = {entry["question_id"]: entry["selected_answer"] for entry in selected_answers}

#     correct = 0
#     weak_topics = []

#     for question in questions:
#         user_answer = answer_lookup.get(str(question.id))
#         if user_answer == question.answer_text:
#             correct += 1
#         else:
#             weak_topics.extend(question.concept_tags)  # assumes concept_tags is a list

#     total = len(questions)
#     score_percent = (correct / total) * 100 if total else 0
#     result = QuizResult(
#         topic=topic,
#         score=correct,
#         total_questions=total,
#         timestamp = datetime.now()

#     )
#     db.add(result)
#     db.commit()
#     db.refresh(result)
#     return {
#         "status": "success",
#         "topic": topic,
#         "score": correct,
#         "total": total,
#         "percentage": score_percent,
#         "weak_topics": list(set(weak_topics))  # remove duplicates
#     }


from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List

from app.schemas.quiz import QuizCreate, QuizOut, QuizSubmitRequest, QuizSubmitResponse
from app.database import get_db
from app.models.models import Question, QuizAttempt, QuizResult
from app.auth.auth_bearer import JWTBearer
from app.auth.auth_handler import decode_access_token
from services.quiz_service import get_quiz
from datetime import datetime

router = APIRouter()


def get_current_user_id(token: str = Depends(JWTBearer())) -> str:
    """✅ Extract user_id from JWT token."""
    payload = decode_access_token(token)
    if not payload or "user_id" not in payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload["user_id"]


# ✅ 1. Generate quiz
@router.post("/quiz/generate", response_model=QuizOut)
def generate_quiz(quiz_data: QuizCreate, db: Session = Depends(get_db)):
    response = get_quiz(quiz_data.topic, db, quiz_data.count)
    return JSONResponse(status_code=200, content={"quiz": response})


# ✅ 2. Submit quiz answers
@router.post("/quiz/submit", response_model=QuizSubmitResponse)
def submit_quiz(data: QuizSubmitRequest, db: Session = Depends(get_db)):
    attempt = QuizAttempt(
        topic=data.topic,
        selected_answers=data.answers
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return QuizSubmitResponse(
        message="Quiz submitted successfully",
        attempt_id=attempt.id
    )


# ✅ 3. Score quiz — now correctly attaches user_id
@router.get("/quiz/score/{attempt_id}")
def get_score(
    attempt_id: int = Path(...),
    db: Session = Depends(get_db),
    # Make auth optional: if token is present use it, otherwise user_id stays None
    # To enforce auth, swap the line below with: user_id: str = Depends(get_current_user_id)
    token: str = Depends(JWTBearer(auto_error=False))
):
    attempt = db.query(QuizAttempt).filter(QuizAttempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Quiz attempt not found.")

    selected_answers = attempt.selected_answers
    topic = attempt.topic
    question_ids = [entry["question_id"] for entry in selected_answers]

    questions = db.query(Question).filter(Question.id.in_(question_ids)).all()
    answer_lookup = {
        entry["question_id"]: entry["selected_answer"]
        for entry in selected_answers
    }

    correct = 0
    weak_topics = []
    for question in questions:
        user_answer = answer_lookup.get(str(question.id))
        if user_answer == question.answer_text:
            correct += 1
        else:
            weak_topics.extend(question.concept_tags)

    total = len(questions)
    score_percent = (correct / total) * 100 if total else 0

    # ✅ Extract user_id from token if provided
    user_id = None
    if token:
        try:
            payload = decode_access_token(token)
            user_id = payload.get("user_id")
        except Exception:
            pass

    result = QuizResult(
        user_id=user_id,  # ✅ Now correctly set instead of always None
        topic=topic,
        score=correct,
        total_questions=total,
        timestamp=datetime.now()
    )
    db.add(result)
    db.commit()
    db.refresh(result)

    return {
        "status": "success",
        "topic": topic,
        "score": correct,
        "total": total,
        "percentage": round(score_percent, 2),
        "weak_topics": list(set(weak_topics))
    }


# ✅ 4. Flashcard endpoint — was missing entirely (caused 404)
@router.post("/flashcard")
def generate_flashcard(data: dict, db: Session = Depends(get_db)):
    """
    Generate a flashcard for a given topic/question.
    Expects: { "topic": str, "question_id": str (optional) }
    """
    topic = data.get("topic")
    if not topic:
        raise HTTPException(status_code=400, detail="topic is required")

    # Fetch a question from DB for this topic to use as flashcard
    question = db.query(Question).filter(Question.topic == topic).first()
    if not question:
        raise HTTPException(status_code=404, detail=f"No questions found for topic: {topic}")

    return {
        "topic": topic,
        "question": question.question_text,
        "answer": question.answer_text,
        "concept_tags": question.concept_tags,
        "difficulty": question.difficulty
    }


# ✅ 5. Get all flashcards for a topic
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
            "difficulty": q.difficulty
        }
        for q in questions
    ]