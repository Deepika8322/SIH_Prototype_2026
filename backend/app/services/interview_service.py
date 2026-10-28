import uuid
import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.entities import InterviewQuestion, Role, Competency, RoleCompetency, Course, InterviewAttempt
from app.services.rag_service import rag_service
from app.services.llm_service import llm_service
from app.prompts.templates import MOCK_INTERVIEW_GEN_PROMPT, MOCK_INTERVIEW_EVAL_PROMPT

# In-memory interview session manager
INTERVIEW_SESSIONS: Dict[str, Dict[str, Any]] = {}

class InterviewService:
    def start_interview(self, db: Session, user_id: str, role_id: str, competency_id: Optional[str] = "Auto", question_count: int = 5) -> Dict[str, Any]:
        session_id = f"INT_{uuid.uuid4().hex[:8].upper()}"

        role = db.query(Role).filter(Role.role_id == role_id).first()
        role_name = role.role_name if role else "Civil Service Officer"

        # 1. Retrieve existing interview questions from SQLite
        query = db.query(InterviewQuestion).filter(InterviewQuestion.role_id == role_id)
        if competency_id and competency_id != "Auto":
            query = query.filter(InterviewQuestion.competency_id == competency_id)
        
        db_qs = query.all()

        questions_list = []
        for idx, q in enumerate(db_qs[:question_count], start=1):
            comp = db.query(Competency).filter(Competency.competency_id == q.competency_id).first()
            comp_name = comp.competency_name if comp else "General Public Administration"
            questions_list.append({
                "question_index": idx,
                "question_id": q.question_id,
                "question_text": q.question_text,
                "competency_id": q.competency_id,
                "competency_name": comp_name,
                "expected_key_points": q.expected_key_points or "Applied STAR method and administrative rules.",
                "difficulty": q.difficulty,
                "behavioral_focus": q.behavioral_focus or "Public Administration",
                "source_type": "prototype_dataset"
            })

        retrieved_count = len(questions_list)
        needed = max(0, question_count - retrieved_count)

        # 2. Dynamic generation if needed
        if needed > 0:
            target_comp_name = "Core Role Competencies"
            if competency_id and competency_id != "Auto":
                tc = db.query(Competency).filter(Competency.competency_id == competency_id).first()
                if tc:
                    target_comp_name = tc.competency_name
            else:
                # Get competencies associated with this role
                rcs = db.query(RoleCompetency).filter(RoleCompetency.role_id == role_id).all()
                cnames = []
                for rc in rcs:
                    c = db.query(Competency).filter(Competency.competency_id == rc.competency_id).first()
                    if c:
                        cnames.append(c.competency_name)
                if cnames:
                    target_comp_name = ", ".join(cnames[:3])

            rag_chunks = rag_service.search(f"{role_name} interview questions competency", top_k=3, filter_doc_type="interview")
            context = rag_service.format_context_for_prompt(rag_chunks)

            existing_str = "\n".join([f"- {q['question_text']}" for q in questions_list])

            prompt = MOCK_INTERVIEW_GEN_PROMPT.format(
                context=context,
                role_name=role_name,
                competencies=target_comp_name,
                competency_id=competency_id if competency_id != "Auto" else "C001",
                existing_questions=existing_str if existing_str else "None",
                count=needed
            )

            gen_result = llm_service.generate_json("You are an expert civil service interview board member.", prompt, schema_type="mock_interview_gen")
            raw_gen_qs = gen_result.get("questions", [])

            for gq in raw_gen_qs:
                q_text = gq.get("question_text", "").strip()
                if not q_text:
                    continue
                curr_idx = len(questions_list) + 1
                questions_list.append({
                    "question_index": curr_idx,
                    "question_id": f"GEN_IQ_{uuid.uuid4().hex[:6].upper()}",
                    "question_text": q_text,
                    "competency_id": gq.get("competency_id", "C001"),
                    "competency_name": gq.get("competency_name", target_comp_name),
                    "expected_key_points": gq.get("expected_key_points", "Structured STAR answer with rule grounding."),
                    "difficulty": gq.get("difficulty", "medium"),
                    "behavioral_focus": gq.get("behavioral_focus", "Decision Making & Ethics"),
                    "source_type": "ai_generated"
                })
                if len(questions_list) >= question_count:
                    break

        final_questions = questions_list[:question_count]

        # Save session
        INTERVIEW_SESSIONS[session_id] = {
            "session_id": session_id,
            "user_id": user_id,
            "role_id": role_id,
            "role_name": role_name,
            "questions": final_questions,
            "evaluations": {},
            "current_index": 1,
            "created_at": datetime.datetime.utcnow()
        }

        return {
            "session_id": session_id,
            "role_id": role_id,
            "role_name": role_name,
            "total_questions": len(final_questions),
            "questions": final_questions
        }

    def evaluate_answer(self, db: Session, session_id: str, question_index: int, user_answer: str) -> Dict[str, Any]:
        session_data = INTERVIEW_SESSIONS.get(session_id)
        if not session_data:
            raise ValueError(f"Interview session {session_id} not found or expired.")

        questions = session_data["questions"]
        if question_index < 1 or question_index > len(questions):
            raise ValueError(f"Invalid question index {question_index}")

        current_q = questions[question_index - 1]

        # RAG context for evaluation
        rag_chunks = rag_service.search("mock interview star evaluation scoring framework", top_k=2, filter_doc_type="interview")
        context = rag_service.format_context_for_prompt(rag_chunks)

        prompt = MOCK_INTERVIEW_EVAL_PROMPT.format(
            context=context,
            role_name=session_data["role_name"],
            competency_name=current_q["competency_name"],
            question_text=current_q["question_text"],
            expected_key_points=current_q["expected_key_points"],
            user_answer=user_answer
        )

        eval_resp = llm_service.generate_json("You are an expert civil service interview assessor.", prompt, schema_type="mock_interview_eval")

        scores = eval_resp.get("scores", {
            "relevance": 3.8,
            "clarity_and_structure": 3.8,
            "reasoning_and_depth": 3.8,
            "role_competency": 3.8,
            "practical_judgment_ethics": 4.0
        })
        avg_score = eval_resp.get("average_score", 3.8)
        strengths = eval_resp.get("strengths", ["Clear understanding of basic administrative responsibilities."])
        weaknesses = eval_resp.get("weaknesses", ["Could provide more quantifiable evidence of outcomes."])
        improvement = eval_resp.get("suggested_improvement", "Adopt the STAR structure explicitly.")
        narrative = eval_resp.get("feedback_narrative", "Good response with practical grounding.")

        # Store evaluation in session
        session_data["evaluations"][question_index] = {
            "question": current_q,
            "user_answer": user_answer,
            "scores": scores,
            "average_score": avg_score,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "improvement": improvement
        }

        is_last = (question_index >= len(questions))

        # If last question, record in SQLite
        if is_last:
            all_scores = [ev["average_score"] for ev in session_data["evaluations"].values()]
            overall_score = round(sum(all_scores) / max(1, len(all_scores)), 2)
            
            all_strengths = []
            all_weaknesses = []
            for ev in session_data["evaluations"].values():
                all_strengths.extend(ev.get("strengths", []))
                all_weaknesses.extend(ev.get("weaknesses", []))

            attempt = InterviewAttempt(
                session_id=session_id,
                user_id=session_data["user_id"],
                role_id=session_data["role_id"],
                competency_id=current_q["competency_id"],
                overall_score=overall_score,
                strengths="; ".join(all_strengths[:3]),
                weaknesses="; ".join(all_weaknesses[:3]),
                feedback=narrative,
                created_at=datetime.datetime.utcnow()
            )
            db.add(attempt)
            db.commit()

        return {
            "session_id": session_id,
            "question_index": question_index,
            "scores": scores,
            "average_score": avg_score,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "suggested_improvement": improvement,
            "competency_evaluated": current_q["competency_name"],
            "feedback_narrative": narrative,
            "is_last_question": is_last
        }

    def get_interview_report(self, db: Session, session_id: str) -> Dict[str, Any]:
        session_data = INTERVIEW_SESSIONS.get(session_id)
        if not session_data:
            # Check SQLite DB
            db_attempt = db.query(InterviewAttempt).filter(InterviewAttempt.session_id == session_id).first()
            if db_attempt:
                role = db.query(Role).filter(Role.role_id == db_attempt.role_id).first()
                return {
                    "session_id": session_id,
                    "role_name": role.role_name if role else "Civil Service Officer",
                    "overall_score": db_attempt.overall_score,
                    "total_questions": 5,
                    "summary": db_attempt.feedback or "Mock interview completed.",
                    "strengths_overview": db_attempt.strengths.split("; ") if db_attempt.strengths else [],
                    "areas_for_growth": db_attempt.weaknesses.split("; ") if db_attempt.weaknesses else [],
                    "recommended_courses": [],
                    "recommended_actions": ["Review STAR response techniques.", "Take Project Management mock test."]
                }
            raise ValueError(f"Interview session {session_id} not found.")

        evals = list(session_data["evaluations"].values())
        all_scores = [ev["average_score"] for ev in evals]
        overall_score = round(sum(all_scores) / max(1, len(all_scores)), 2) if all_scores else 3.5

        all_strengths = []
        all_weaknesses = []
        for ev in evals:
            all_strengths.extend(ev.get("strengths", []))
            all_weaknesses.extend(ev.get("weaknesses", []))

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
            "session_id": session_id,
            "role_name": session_data["role_name"],
            "overall_score": overall_score,
            "total_questions": len(session_data["questions"]),
            "summary": f"Completed {len(evals)} interview questions for {session_data['role_name']}. Overall readiness rating is {overall_score}/5.0.",
            "strengths_overview": list(set(all_strengths))[:4],
            "areas_for_growth": list(set(all_weaknesses))[:4],
            "recommended_courses": rec_courses,
            "recommended_actions": [
                "Practice STAR format for situational questions, focusing on measurable results.",
                "Review General Financial Rules (GFR) procurement thresholds and SLA compliance.",
                "Attempt a scenario mock assessment before taking the next interview round."
            ]
        }

interview_service = InterviewService()