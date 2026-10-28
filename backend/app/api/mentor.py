from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.schemas import MentorChatRequest
from app.services.mentor_service import mentor_service

router = APIRouter()

@router.post('/mentor/chat')
def mentor_chat(req: MentorChatRequest, db: Session = Depends(get_db)):
    try:
        return mentor_service.chat(db, user_id=req.user_id, message=req.message, session_context=req.session_context)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))