from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.entities import User, Role, Competency, RoleCompetency, UserCompetency, Course
from app.services.rag_service import rag_service
from app.services.llm_service import llm_service
from app.prompts.templates import SKILL_GAP_NARRATIVE_PROMPT

class SkillGapService:
    def calculate_gaps(self, db: Session, user_id: str, target_role_id: Optional[str] = None) -> Dict[str, Any]:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")

        current_role = db.query(Role).filter(Role.role_id == user.current_role_id).first()
        target_role_id = target_role_id or user.target_role_id or user.current_role_id
        target_role = db.query(Role).filter(Role.role_id == target_role_id).first()

        # Load target role requirements
        role_comps = db.query(RoleCompetency).filter(RoleCompetency.role_id == target_role_id).all()
        
        # Load user's current competency levels
        user_comps = {uc.competency_id: uc for uc in db.query(UserCompetency).filter(UserCompetency.user_id == user_id).all()}
        
        gaps_list = []
        for rc in role_comps:
            comp = db.query(Competency).filter(Competency.competency_id == rc.competency_id).first()
            if not comp:
                continue

            user_comp = user_comps.get(rc.competency_id)
            current_lvl = user_comp.current_level if user_comp else 1
            req_lvl = rc.required_level
            
            # Deterministic arithmetic: gap = required - current
            gap = req_lvl - current_lvl

            if gap <= 0:
                priority = "Meets Target"
            elif gap == 1:
                priority = "Small Gap (Low Priority)"
            elif gap == 2:
                priority = "Moderate Gap (Medium Priority)"
            else:
                priority = "High-Priority Gap"

            # Get linked courses from SQLite
            courses = db.query(Course).filter(Course.competency_id == rc.competency_id).all()
            course_items = [{
                "course_id": c.course_id,
                "course_title": c.course_title,
                "provider": c.provider,
                "duration_hours": c.duration_hours,
                "difficulty": c.difficulty,
                "course_url": c.course_url
            } for c in courses]

            # RAG context for competency
            rag_chunks = rag_service.search(f"{comp.competency_name} competency", top_k=2)
            context = rag_service.format_context_for_prompt(rag_chunks)

            # Generate concise personalized explanation
            prompt = SKILL_GAP_NARRATIVE_PROMPT.format(
                current_role=current_role.role_name if current_role else "Learner",
                target_role=target_role.role_name if target_role else "Target Role",
                competency_name=comp.competency_name,
                current_level=current_lvl,
                required_level=req_lvl,
                gap=gap,
                priority=priority,
                context=context
            )
            ai_exp = llm_service.generate_text("You are an expert civil service career coach.", prompt)

            gaps_list.append({
                "competency_id": comp.competency_id,
                "competency_name": comp.competency_name,
                "competency_type": comp.competency_type,
                "current_level": current_lvl,
                "required_level": req_lvl,
                "gap": gap,
                "priority": priority,
                "recommended_courses": course_items,
                "practice_activity": f"Scenario-based drafting and simulation exercise for {comp.competency_name}.",
                "recommended_assessment": f"{comp.competency_name} Diagnostic Mock Assessment (Level {req_lvl})",
                "ai_explanation": ai_exp,
                "source_label": "Prototype Competency Matrix + RAG Grounding"
            })

        # Sort: highest gap first
        gaps_list.sort(key=lambda x: x["gap"], reverse=True)

        summary = f"Identified {len(gaps_list)} competencies for role {target_role.role_name if target_role else 'Target'}. "
        high_gaps = [g['competency_name'] for g in gaps_list if g['gap'] >= 2]
        if high_gaps:
            summary += f"Key focus areas requiring structured development: {', '.join(high_gaps)}."
        else:
            summary += "Your current competency profile closely aligns with target role expectations."

        return {
            "user_id": user_id,
            "current_role": current_role.role_name if current_role else "Unknown",
            "target_role": target_role.role_name if target_role else "Unknown",
            "gaps": gaps_list,
            "overall_summary": summary
        }

skill_gap_service = SkillGapService()