from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.models import SkillScanResult
from app.schemas.skill_scan import SkillScanCreate
import uuid
from fastapi import HTTPException

def create_skill_scan(db: Session, data: SkillScanCreate):
    try:
        new_scan = SkillScanResult(
            id=uuid.uuid4(),
            user_id=data.user_id,
            career_goal=data.career_goal,
            recommended_pathway=data.recommended_pathway
        )
        db.add(new_scan)
        db.commit()
        db.refresh(new_scan)
        return new_scan
    except SQLAlchemyError as e:
        print("❌ DB Error during skill scan:", e)
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error while creating skill scan")
    
def get_skill_scans_by_user(db: Session, user_id: str):
    try:
        return db.query(SkillScanResult).filter(SkillScanResult.user_id == uuid.UUID(user_id)).all()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    except SQLAlchemyError as e:
        print("❌ Error fetching skill scans:", e)
        raise HTTPException(status_code=500, detail="Error fetching skill scans")

