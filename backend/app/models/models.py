import uuid
from sqlalchemy import Column, DateTime, String, Text, Float, Boolean, Integer, TIMESTAMP, ForeignKey, ARRAY, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy.orm import relationship
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    career_goal = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SkillScanResult(Base):
    __tablename__ = "skill_scan_results"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    career_goal = Column(Text, nullable=False)
    recommended_pathway = Column(JSONB, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class LearningSession(Base):
    __tablename__ = "learning_sessions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    topic = Column(Text, nullable=False)
    content_type = Column(String, nullable=False)
    time_spent = Column(Integer, nullable=False)
    retention_score = Column(Float, nullable=False)
    interaction_pattern = Column(JSONB, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class ConfusionSignal(Base):
    __tablename__ = "confusion_signals"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    topic = Column(Text)
    question_id = Column(UUID(as_uuid=True))
    confusion_score = Column(Float)
    ai_feedback = Column(Text)
    message = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class RecallCard(Base):
    __tablename__ = "recall_cards"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    topic = Column(Text, nullable=False)
    keywords = Column(ARRAY(Text), nullable=False)
    diagram_image_url = Column(Text, nullable=False)
    analogy = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class KnowledgeDecayEvent(Base):
    __tablename__ = "knowledge_decay_events"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic = Column(Text, nullable=False)
    last_interaction = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    predicted_forget_score = Column(Float, nullable=False)
    review_suggested = Column(Boolean, nullable=False, default=False)
    decay_model_type = Column(String, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class Question(Base):
    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic = Column(Text)
    question_text = Column(Text)
    answer_text = Column(Text)
    concept_tags = Column(ARRAY(Text))
    difficulty = Column(Integer)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class LearningStyle(Base):
    __tablename__ = "learning_styles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    dominant_style = Column(String, nullable=False)
    style_scores = Column(JSONB)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())


class Roadmap(Base):
    __tablename__ = "roadmaps"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    topic = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    level = Column(String, nullable=True, default="beginner")
    # ✅ ADDED: created_at for proper history sorting
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    subtopics = relationship("SubTopic", back_populates="roadmap", cascade="all, delete")


class SubTopic(Base):
    __tablename__ = "subtopics"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    roadmap_id = Column(UUID(as_uuid=True), ForeignKey("roadmaps.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    roadmap = relationship("Roadmap", back_populates="subtopics")


class QuizResult(Base):
    __tablename__ = "quiz_results"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    topic = Column(String, nullable=False)
    score = Column(Integer)
    total_questions = Column(Integer)
    timestamp = Column(TIMESTAMP(timezone=False), server_default=func.now())


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, nullable=False)
    questions = Column(JSON, nullable=False)


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, nullable=False)
    selected_answers = Column(JSON, nullable=False)
    user_id = Column(String, nullable=True) 
    submitted_at = Column(DateTime, default=datetime.utcnow)