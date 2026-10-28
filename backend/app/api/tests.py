from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.entities import Competency, MockTestQuestion
from app.schemas.schemas import TestGenerateRequest, TestSubmitRequest
from app.services.test_service import test_service

router = APIRouter()

@router.get('/test/topics')
def get_test_topics(db: Session = Depends(get_db)):
    comps = db.query(Competency).all()
    topics_from_qs = db.query(MockTestQuestion.topic).distinct().all()
    topic_set = set([t[0] for t in topics_from_qs if t[0]])
    for c in comps:
        topic_set.add(c.competency_name)
    return {
        'topics': sorted(list(topic_set)),
        'competencies': [{'competency_id': c.competency_id, 'competency_name': c.competency_name} for c in comps]
    }

@router.post('/test/generate')
def generate_mock_test(req: TestGenerateRequest, db: Session = Depends(get_db)):
    try:
        return test_service.generate_test(
            db,
            user_id=req.user_id,
            topic=req.topic,
            competency_id=req.competency_id,
            difficulty=req.difficulty,
            count=req.count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/test/{test_id}/submit')
def submit_mock_test(test_id: str, req: TestSubmitRequest, db: Session = Depends(get_db)):
    try:
        return test_service.submit_test(
            db,
            user_id=req.user_id,
            test_id=test_id,
            user_answers=req.answers,
            client_meta=req.questions_meta
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))