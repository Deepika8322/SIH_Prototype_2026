from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.entities import SyllabusModule, Course
from app.schemas.schemas import SyllabusTutorRequest
from app.services.rag_service import rag_service
from app.services.llm_service import llm_service
from app.prompts.templates import SYLLABUS_TUTOR_PROMPT

router = APIRouter()

@router.get('/syllabus')
def list_syllabus(db: Session = Depends(get_db)):
    modules = db.query(SyllabusModule).all()
    result = []
    for m in modules:
        # Related courses
        courses = db.query(Course).limit(2).all()
        result.append({
            'module_id': m.module_id,
            'module_name': m.module_name,
            'category': m.category,
            'description': m.description,
            'duration_hours': m.duration_hours,
            'learning_objectives': [obj.strip() for obj in m.learning_objectives.split('\n') if obj.strip()],
            'related_competencies': [c.strip() for c in m.related_competencies.split(',') if c.strip()],
            'related_courses': [{
                'course_id': c.course_id,
                'course_title': c.course_title,
                'provider': c.provider,
                'duration_hours': c.duration_hours,
                'difficulty': c.difficulty,
                'course_url': c.course_url
            } for c in courses]
        })
    return result

@router.get('/syllabus/{module_id}')
def get_syllabus_module(module_id: str, db: Session = Depends(get_db)):
    m = db.query(SyllabusModule).filter(SyllabusModule.module_id == module_id).first()
    if not m:
        raise HTTPException(status_code=404, detail='Syllabus module not found')
    courses = db.query(Course).limit(2).all()
    return {
        'module_id': m.module_id,
        'module_name': m.module_name,
        'category': m.category,
        'description': m.description,
        'duration_hours': m.duration_hours,
        'learning_objectives': [obj.strip() for obj in m.learning_objectives.split('\n') if obj.strip()],
        'related_competencies': [c.strip() for c in m.related_competencies.split(',') if c.strip()],
        'related_courses': [{
            'course_id': c.course_id,
            'course_title': c.course_title,
            'provider': c.provider,
            'duration_hours': c.duration_hours,
            'difficulty': c.difficulty,
            'course_url': c.course_url
        } for c in courses]
    }

@router.post('/syllabus/tutor')
def ask_syllabus_tutor(req: SyllabusTutorRequest, db: Session = Depends(get_db)):
    m = db.query(SyllabusModule).filter(SyllabusModule.module_id == req.module_id).first()
    if not m:
        raise HTTPException(status_code=404, detail='Syllabus module not found')

    # RAG search
    rag_chunks = rag_service.search(f"{m.module_name} {req.query_type} syllabus", top_k=3, filter_doc_type="syllabus")
    context = rag_service.format_context_for_prompt(rag_chunks)
    source_tag = rag_chunks[0].get("source", "common_syllabus.md") if rag_chunks else "common_syllabus.md"

    prompt = SYLLABUS_TUTOR_PROMPT.format(
        module_name=m.module_name,
        category=m.category,
        description=m.description,
        learning_objectives=m.learning_objectives,
        context=context,
        query_type=req.query_type,
        custom_question=req.custom_question or "Provide guidance for this module."
    )

    tutor_reply = llm_service.generate_text("You are an expert civil service curriculum tutor.", prompt)

    return {
        'module_id': m.module_id,
        'response_type': req.query_type,
        'content': tutor_reply,
        'rag_source': source_tag
    }