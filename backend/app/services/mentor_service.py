from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.entities import User, Role, Competency, UserCompetency, Course, TestAttempt, InterviewAttempt
from app.services.rag_service import rag_service
from app.services.llm_service import llm_service
from app.prompts.templates import PERSONAL_MENTOR_PROMPT

class MentorService:
    def chat(self, db: Session, user_id: str, message: str, session_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")

        current_role = db.query(Role).filter(Role.role_id == user.current_role_id).first()
        target_role = db.query(Role).filter(Role.role_id == user.target_role_id).first()

        # Gather user context
        user_comps = db.query(UserCompetency).filter(UserCompetency.user_id == user_id).all()
        gaps_list = []
        for uc in user_comps:
            c = db.query(Competency).filter(Competency.competency_id == uc.competency_id).first()
            if c:
                gaps_list.append(f"{c.competency_name} (Current Level {uc.current_level}/5, Assessment Score: {uc.assessment_score}%)")

        recent_tests = db.query(TestAttempt).filter(TestAttempt.user_id == user_id).order_by(TestAttempt.id.desc()).limit(2).all()
        test_scores_str = ", ".join([f"{t.topic}: {t.score}/{t.total_questions} ({t.percentage}%)" for t in recent_tests]) if recent_tests else "No recent test attempts"

        # RAG Search for mentor guidance & domain knowledge
        rag_chunks = rag_service.search(f"{message} civil service competency guidance mentoring", top_k=3, filter_doc_type="mentor")
        if not rag_chunks:
            rag_chunks = rag_service.search(message, top_k=3)
        context = rag_service.format_context_for_prompt(rag_chunks)
        rag_sources = list(set([c.get("source", "knowledge_base.md") for c in rag_chunks]))

        prompt = PERSONAL_MENTOR_PROMPT.format(
            name=user.name,
            current_role=current_role.role_name if current_role else "Section Officer",
            target_role=target_role.role_name if target_role else "Project Officer",
            gaps="; ".join(gaps_list[:3]),
            recent_scores=test_scores_str,
            completed_courses="Effective Government Noting & Drafting (CSMOP)",
            context=context,
            user_message=message
        )

        mentor_resp = llm_service.generate_json("You are an inspiring and pragmatic civil service personal mentor.", prompt, schema_type="mentor")

        reply_text = mentor_resp.get("reply", "Welcome! I am your AI Karmayogi personal mentor. How can I assist your competency development today?")
        actions = mentor_resp.get("suggested_actions", [
            "Review your latest skill gap analysis",
            "Attempt a quick 5-question mock test",
            "Explore the Project Management syllabus module"
        ])
        exercise = mentor_resp.get("suggested_exercise", "Take 10 minutes to list the critical milestone risks in your current departmental project.")

        # Find relevant courses
        courses = db.query(Course).limit(2).all()
        rec_courses = [{
            "course_id": c.course_id,
            "course_title": c.course_title,
            "provider": c.provider,
            "duration_hours": c.duration_hours,
            "difficulty": c.difficulty,
            "course_url": c.course_url
        } for c in courses]

        return {
            "user_id": user_id,
            "reply": reply_text,
            "suggested_actions": actions,
            "suggested_exercise": exercise,
            "related_courses": rec_courses,
            "rag_sources": rag_sources
        }

mentor_service = MentorService()