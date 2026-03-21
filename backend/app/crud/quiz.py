# from sqlalchemy.orm import Session
# from app.models import QuestionsAnswers
# from app.schemas.quiz import QuizAttemptCreate
# import random
# from models.models import QuestionsAnswers


# def generate_quiz_attempt(db: Session, quiz_data: QuizAttemptCreate):
#     level = quiz_data.level
#     topic = quiz_data.topic

#     questions = (
#         db.query(QuestionsAnswers)
#         .filter(QuestionsAnswers.level == level, QuestionsAnswers.topic == topic)
#         .all()
#     )

#     if len(questions) < 10:
#         raise Exception("Not enough questions available for this level and topic.")

#     selected_questions = random.sample(questions, 10)
#     return selected_questions
