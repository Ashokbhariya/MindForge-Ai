from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.question import QuestionCreate, QuestionOut
from app.crud import question
from app.database import get_db
from pydantic import BaseModel
# from services.quiz_service import get_quiz, evaluate_quiz_attempt  # optional: remove if not used elsewhere
from app.models import Question
from services.confusion_service import get_confusion_summary

import os
import json
import requests


router = APIRouter(tags=["Questions & Quiz"])

# ---------------- CRUD QUESTIONS ----------------
@router.post("/", response_model=QuestionOut)
def create_question(question_data: QuestionCreate, db: Session = Depends(get_db)):
    return question.create_question(db, question_data)

@router.get("/", response_model=list[QuestionOut])
def list_questions(db: Session = Depends(get_db)):
    return question.get_all_questions(db)

# ---------------- ❌ COMMENTED CONFLICTING QUIZ ROUTES ONLY ----------------

# Commented to avoid conflict with new `/api/quiz/generate`
# class QuizRequest(BaseModel):
#     topic: str
#     num_questions: int = 10

# @router.post("/quiz/generate")
# def generate_quiz(data: QuizRequest, db: Session = Depends(get_db)):
#     ...
#     (LLAMA logic skipped intentionally)

# @router.get("/quiz/{topic}")
# def fetch_quiz(topic: str, db: Session = Depends(get_db)):
#     quiz = get_quiz(topic, db)
#     if not quiz:
#         raise HTTPException(status_code=404, detail="No quiz available.")
#     return {"status": "success", "topic": topic, "quiz": quiz}

# class QuizSubmission(BaseModel):
#     topic: str
#     answers: dict  # Example: {"0": "Option A", "1": "Option C", ...}

# @router.post("/quiz/submit")
# def submit_quiz(data: QuizSubmission, db: Session = Depends(get_db)):
#     try:
#         quiz = get_quiz(data.topic, db)
#         if not quiz:
#             raise HTTPException(status_code=404, detail="Quiz not found for the topic.")

#         score_data = evaluate_quiz_attempt(data.answers, quiz)
#         return {
#             "status": "success",
#             "topic": data.topic,
#             "score": score_data["score"],
#             "total": score_data["total"],
#             "correct_questions": score_data["correct_questions"],
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
