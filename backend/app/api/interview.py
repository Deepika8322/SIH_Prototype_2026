from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.schemas import InterviewStartRequest, InterviewAnswerRequest
from app.services.interview_service import interview_service

router = APIRouter()

@router.post('/interview/start')
def start_interview(req: InterviewStartRequest, db: Session = Depends(get_db)):
    try:
        return interview_service.start_interview(
            db,
            user_id=req.user_id,
            role_id=req.role_id,
            competency_id=req.competency_id,
            question_count=req.question_count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/interview/{session_id}/answer')
def answer_interview(session_id: str, req: InterviewAnswerRequest, db: Session = Depends(get_db)):
    try:
        return interview_service.evaluate_answer(
            db,
            session_id=session_id,
            question_index=req.question_index,
            user_answer=req.user_answer
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/interview/{session_id}/result')
def get_interview_result(session_id: str, db: Session = Depends(get_db)):
    try:
        return interview_service.get_interview_report(db, session_id=session_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))