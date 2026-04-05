from pydantic import BaseModel
from typing import List, Optional, Any


class QuizCreate(BaseModel):
    topic: str
    count: int = 10


class AnswerItem(BaseModel):
    question_id: Any
    selected_answer: Optional[str] = None


class QuizSubmitRequest(BaseModel):
    topic: str
    answers: List[AnswerItem]
    user_id: Optional[str] = None      # ← THIS IS THE KEY ADDITION


class QuizSubmitResponse(BaseModel):
    message: str
    attempt_id: int


class QuizOut(BaseModel):
    id: int
    topic: str
    questions: List[dict]

    class Config:
        from_attributes = True