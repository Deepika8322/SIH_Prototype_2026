from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.services.skill_gap_service import skill_gap_service

router = APIRouter()

@router.get('/users/{user_id}/skill-gaps')
def get_user_skill_gaps(user_id: str, target_role_id: Optional[str] = Query(None), db: Session = Depends(get_db)):
    try:
        return skill_gap_service.calculate_gaps(db, user_id=user_id, target_role_id=target_role_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))