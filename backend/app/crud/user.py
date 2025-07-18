from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.models import User
from app.schemas.user import UserCreate
from fastapi import HTTPException
import uuid

def create_user(db: Session, user_data: UserCreate):
    new_user = User(
        id=uuid.uuid4(),
        name=user_data.name,
        email=user_data.email,
        password_hash=user_data.password_hash,
        career_goal=user_data.career_goal
    )
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except SQLAlchemyError as e:
        db.rollback()
        import traceback
        traceback.print_exc()  # <-- ADD THIS LINE TO SHOW THE REAL ERROR
        raise HTTPException(status_code=500, detail="Database error while creating user")

def get_user_by_id(db: Session, user_id: str):
    try:
        return db.query(User).filter(User.id == uuid.UUID(user_id)).first()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    except SQLAlchemyError as e:
        print("Error while fetching user:", e)
        raise HTTPException(status_code=500, detail="Database error while fetching user")
