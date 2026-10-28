from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.entities import Role
from app.schemas.schemas import CareerRecommendRequest
from app.services.career_service import career_service

router = APIRouter()

@router.get('/roles')
def list_roles(db: Session = Depends(get_db)):
    roles = db.query(Role).all()
    return [{
        'role_id': r.role_id,
        'role_name': r.role_name,
        'department': r.department,
        'description': r.description,
        'level_min': r.level_min,
        'level_max': r.level_max
    } for r in roles]

@router.post('/career/recommend')
def recommend_career(req: CareerRecommendRequest, db: Session = Depends(get_db)):
    try:
        return career_service.recommend_path(db, user_id=req.user_id, target_role_id=req.target_role_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))