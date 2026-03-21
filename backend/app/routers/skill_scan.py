from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session  # ✅ Sync session
from app.schemas.skill_scan import SkillScanCreate, SkillScanOut
from app.crud import skill_scan
from app.database import get_db

router = APIRouter()

@router.post("/", response_model=SkillScanOut)
def create_skill_result(skill_data: SkillScanCreate, db: Session = Depends(get_db)):
    return skill_scan.create_skill_scan(db, skill_data)

@router.get("/{user_id}", response_model=list[SkillScanOut])
def get_user_skill_scans(user_id: str, db: Session = Depends(get_db)):
    return skill_scan.get_skill_scans_by_user(db, user_id)
