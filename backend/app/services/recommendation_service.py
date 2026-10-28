from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.entities import User, Course, RoleCompetency, Competency, UserCompetency

class RecommendationService:
    def get_recommendations(self, db: Session, user_id: str) -> List[Dict[str, Any]]:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")

        target_role_id = user.target_role_id or "R002"
        role_comps = db.query(RoleCompetency).filter(RoleCompetency.role_id == target_role_id).all()
        user_comps = {uc.competency_id: uc for uc in db.query(UserCompetency).filter(UserCompetency.user_id == user_id).all()}

        recommendations = []
        rec_idx = 1

        for rc in role_comps:
            comp = db.query(Competency).filter(Competency.competency_id == rc.competency_id).first()
            if not comp:
                continue

            user_comp = user_comps.get(rc.competency_id)
            current_lvl = user_comp.current_level if user_comp else 1
            req_lvl = rc.required_level
            gap = req_lvl - current_lvl

            if gap > 0:
                # 1. Course Recommendation
                course = db.query(Course).filter(Course.competency_id == rc.competency_id).first()
                if course:
                    recommendations.append({
                        "recommendation_id": f"REC_CRS_{rec_idx}",
                        "title": course.course_title,
                        "type": "course",
                        "competency_name": comp.competency_name,
                        "description": course.description,
                        "priority": rc.priority or "High",
                        "source_type": "Verified Reference",
                        "why_explanation": f"You are at Level {current_lvl} in {comp.competency_name}, while target role '{user.target_role_id}' requires Level {req_lvl} (Gap: {gap}). This course provides core conceptual grounding.",
                        "action_payload": {"course_id": course.course_id, "url": course.course_url}
                    })
                    rec_idx += 1

                # 2. Practice Activity
                recommendations.append({
                    "recommendation_id": f"REC_PRAC_{rec_idx}",
                    "title": f"Applied Simulation: {comp.competency_name}",
                    "type": "practice",
                    "competency_name": comp.competency_name,
                    "description": f"Complete a 15-minute scenario exercise on real-world discretionary decisions for {comp.competency_name}.",
                    "priority": "Medium",
                    "source_type": "AI Generated",
                    "why_explanation": f"Grounded in your recent practice score. Practical simulation accelerates retention between Level {current_lvl} and Level {req_lvl}.",
                    "action_payload": {"competency_id": comp.competency_id, "topic": comp.competency_name}
                })
                rec_idx += 1

                # 3. Assessment Recommendation
                recommendations.append({
                    "recommendation_id": f"REC_TEST_{rec_idx}",
                    "title": f"{comp.competency_name} Diagnostic Mock Test",
                    "type": "assessment",
                    "competency_name": comp.competency_name,
                    "description": f"Take a 5-10 question mock test to validate your readiness at Level {req_lvl}.",
                    "priority": rc.priority or "High",
                    "source_type": "Prototype Data",
                    "why_explanation": f"Validates whether your competency proficiency has reached the required benchmark of Level {req_lvl}.",
                    "action_payload": {"topic": comp.competency_name, "competency_id": comp.competency_id}
                })
                rec_idx += 1

        return recommendations

    def explain_recommendation(self, db: Session, user_id: str, recommendation_id: str) -> Dict[str, Any]:
        return {
            "recommendation_id": recommendation_id,
            "current_level": 2,
            "target_level": 4,
            "gap": 2,
            "evidence": [
                "User Competency Profile indicates Level 2 in Project Management (Baseline Score: 60%)",
                "Target Role (Project Officer - R002) requires Level 4 proficiency",
                "Grounded in National Civil Service Competency Framework & Taxonomy",
                "Previous test attempt completed with 60% accuracy"
            ],
            "expected_outcome": "Upon completion of course, simulation, and mock test with score >= 80%, competency level updates to Level 3/4.",
            "source_category": "Verified Public Administration Learning Material",
            "disclaimer": "This recommendation is based on prototype competency data and does not constitute an official government career eligibility determination."
        }

recommendation_service = RecommendationService()