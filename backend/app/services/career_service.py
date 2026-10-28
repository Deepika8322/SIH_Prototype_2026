from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models.entities import User, Role, CareerPath, Course, RoleCompetency, Competency, UserCompetency
from app.services.rag_service import rag_service
from app.services.llm_service import llm_service
from app.prompts.templates import CAREER_PATH_PROMPT

class CareerService:
    def recommend_path(self, db: Session, user_id: str, target_role_id: str) -> Dict[str, Any]:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")

        current_role = db.query(Role).filter(Role.role_id == user.current_role_id).first()
        target_role = db.query(Role).filter(Role.role_id == target_role_id).first()
        if not target_role:
            raise ValueError(f"Target role {target_role_id} not found")

        # Find static career path mapping if exists
        cpath = db.query(CareerPath).filter(
            CareerPath.from_role_id == user.current_role_id,
            CareerPath.to_role_id == target_role_id
        ).first()

        timeline = cpath.typical_timeline_months if cpath else 12

        # Evaluate target competencies vs current user competencies
        target_rcs = db.query(RoleCompetency).filter(RoleCompetency.role_id == target_role_id).all()
        user_comps = {uc.competency_id: uc for uc in db.query(UserCompetency).filter(UserCompetency.user_id == user_id).all()}

        target_comps_data = []
        total_req_points = 0
        total_user_points = 0
        gaps_summary_lines = []

        all_courses = []
        for rc in target_rcs:
            comp = db.query(Competency).filter(Competency.competency_id == rc.competency_id).first()
            if not comp:
                continue
            user_comp = user_comps.get(rc.competency_id)
            current_lvl = user_comp.current_level if user_comp else 1
            req_lvl = rc.required_level
            gap = max(0, req_lvl - current_lvl)
            
            total_req_points += req_lvl
            total_user_points += min(current_lvl, req_lvl)

            gaps_summary_lines.append(f"- {comp.competency_name}: Current Level {current_lvl} -> Required Level {req_lvl} (Gap: {gap})")

            # Courses for this competency
            courses = db.query(Course).filter(Course.competency_id == rc.competency_id).all()
            for c in courses:
                all_courses.append({
                    "course_id": c.course_id,
                    "course_title": c.course_title,
                    "competency_name": comp.competency_name,
                    "provider": c.provider,
                    "duration_hours": c.duration_hours,
                    "difficulty": c.difficulty,
                    "course_url": c.course_url
                })

            target_comps_data.append({
                "competency_id": comp.competency_id,
                "competency_name": comp.competency_name,
                "current_level": current_lvl,
                "required_level": req_lvl,
                "gap": gap,
                "priority": rc.priority
            })

        readiness_score = round((total_user_points / max(1, total_req_points)) * 100.0, 1)
        
        # RAG grounding
        rag_chunks = rag_service.search(f"career path {target_role.role_name}", top_k=3, filter_doc_type="career")
        context = rag_service.format_context_for_prompt(rag_chunks)

        # Call LLM to generate narrative and roadmap
        prompt = CAREER_PATH_PROMPT.format(
            user_name=user.name,
            current_role=current_role.role_name if current_role else "Current Role",
            target_role=target_role.role_name,
            gaps_summary="\n".join(gaps_summary_lines),
            context=context
        )
        llm_resp = llm_service.generate_json("You are an expert civil service career progression advisor.", prompt, schema_type="career")

        roadmap_steps = llm_resp.get("roadmap_steps", [])
        readiness_status = llm_resp.get("readiness_status", "Developing (Readiness ~70%)")
        action_plan = llm_resp.get("action_plan", cpath.recommended_action_plan if cpath else "Follow the phased competency development sequence.")

        # Deduplicate courses
        seen_cids = set()
        unique_courses = []
        for c in all_courses:
            if c["course_id"] not in seen_cids:
                seen_cids.add(c["course_id"])
                unique_courses.append(c)

        return {
            "user_id": user_id,
            "current_role_name": current_role.role_name if current_role else "Current Role",
            "target_role_name": target_role.role_name,
            "typical_timeline_months": timeline,
            "readiness_status": readiness_status,
            "readiness_score": readiness_score,
            "target_competencies": target_comps_data,
            "roadmap_steps": roadmap_steps,
            "recommended_courses": unique_courses,
            "action_plan": action_plan,
            "disclaimer": "Career recommendations are illustrative for the prototype and must NOT be presented as official government promotion, recruitment, transfer or eligibility rules."
        }

career_service = CareerService()