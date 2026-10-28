from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.recommendation_service import recommendation_service

router = APIRouter()

@router.get('/users/{user_id}/recommendations')
def get_user_recommendations(user_id: str, db: Session = Depends(get_db)):
    try:
        return recommendation_service.get_recommendations(db, user_id=user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/recommendations/explain')
def explain_recommendation(user_id: str = Query('U001'), recommendation_id: str = Query(...), db: Session = Depends(get_db)):
    try:
        return recommendation_service.explain_recommendation(db, user_id=user_id, recommendation_id=recommendation_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))