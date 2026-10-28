import uuid
import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.entities import MockTestQuestion, Competency, Course, TestAttempt, UserCompetency
from app.services.rag_service import rag_service
from app.services.llm_service import llm_service
from app.prompts.templates import MOCK_TEST_GEN_PROMPT

# In-memory store for active test questions to validate against during submission
ACTIVE_TESTS: Dict[str, Dict[str, Any]] = {}

class TestService:
    def generate_test(self, db: Session, user_id: str, topic: str, competency_id: Optional[str] = None, difficulty: str = "medium", count: int = 5) -> Dict[str, Any]:
        test_id = f"TEST_{uuid.uuid4().hex[:8].upper()}"

        # 1. Retrieve existing matching questions from SQLite
        query = db.query(MockTestQuestion)
        if competency_id:
            query = query.filter(MockTestQuestion.competency_id == competency_id)
        elif topic and topic != "All":
            query = query.filter(MockTestQuestion.topic.ilike(f"%{topic}%"))
        
        if difficulty and difficulty != "all":
            query = query.filter(MockTestQuestion.difficulty.ilike(difficulty))

        existing_db_questions = query.all()
        
        retrieved_questions = []
        for q in existing_db_questions[:count]:
            retrieved_questions.append({
                "question_id": q.question_id,
                "question_text": q.question_text,
                "topic": q.topic,
                "competency_name": q.topic,
                "difficulty": q.difficulty,
                "options": {
                    "A": q.option_a,
                    "B": q.option_b,
                    "C": q.option_c,
                    "D": q.option_d
                },
                "correct_option": q.correct_option,
                "explanation": q.explanation,
                "source_type": q.source_type or "prototype_dataset"
            })

        retrieved_count = len(retrieved_questions)
        needed = max(0, count - retrieved_count)
        generated_questions = []

        # 2. Dynamic generation if needed
        if needed > 0:
            comp_name = topic
            if competency_id:
                c = db.query(Competency).filter(Competency.competency_id == competency_id).first()
                if c:
                    comp_name = c.competency_name

            # RAG grounding
            rag_chunks = rag_service.search(f"{topic} {comp_name} public administration", top_k=3)
            context = rag_service.format_context_for_prompt(rag_chunks)

            existing_texts = "\n".join([f"- {q['question_text']}" for q in retrieved_questions])

            prompt = MOCK_TEST_GEN_PROMPT.format(
                context=context,
                topic=topic,
                competency_name=comp_name,
                difficulty=difficulty,
                existing_questions=existing_texts if existing_texts else "None",
                count=needed
            )

            gen_result = llm_service.generate_json("You are an expert test creator for civil service examinations.", prompt, schema_type="mock_test")
            raw_gen_qs = gen_result.get("questions", [])

            # Validate each generated question
            for idx, gq in enumerate(raw_gen_qs, start=1):
                q_text = gq.get("question_text", "").strip()
                opts = gq.get("options", {})
                corr = gq.get("correct_option", "B").strip().upper()
                exp = gq.get("explanation", "Standard civil service administrative principle applies.")

                # Schema checks
                if not q_text or len(opts) < 4:
                    continue
                if corr not in ["A", "B", "C", "D"]:
                    corr = "B"

                generated_questions.append({
                    "question_id": f"GEN_Q_{uuid.uuid4().hex[:6].upper()}",
                    "question_text": q_text,
                    "topic": topic,
                    "competency_name": comp_name,
                    "difficulty": difficulty,
                    "options": opts,
                    "correct_option": corr,
                    "explanation": exp,
                    "source_type": "ai_generated"
                })

        # Combined pool
        all_questions = retrieved_questions + generated_questions
        # Trim to requested count
        final_questions = all_questions[:count]

        # Save metadata for validation during submission
        ACTIVE_TESTS[test_id] = {
            "test_id": test_id,
            "user_id": user_id,
            "topic": topic,
            "difficulty": difficulty,
            "questions_map": {q["question_id"]: q for q in final_questions}
        }

        # Format for client (strip correct_option & explanation so user cannot cheat)
        client_questions = []
        for q in final_questions:
            client_questions.append({
                "question_id": q["question_id"],
                "question_text": q["question_text"],
                "topic": q["topic"],
                "competency_name": q["competency_name"],
                "difficulty": q["difficulty"],
                "options": q["options"],
                "source_type": q["source_type"]
            })

        return {
            "test_id": test_id,
            "topic": topic,
            "difficulty": difficulty,
            "total_questions": len(final_questions),
            "retrieved_count": min(retrieved_count, len(final_questions)),
            "generated_count": max(0, len(final_questions) - min(retrieved_count, len(final_questions))),
            "questions": client_questions
        }

    def submit_test(self, db: Session, user_id: str, test_id: str, user_answers: Dict[str, str], client_meta: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        test_data = ACTIVE_TESTS.get(test_id)
        
        # Reconstruct questions map if restarted or cached
        questions_map = {}
        topic = "General Assessment"
        difficulty = "medium"

        if test_data:
            questions_map = test_data["questions_map"]
            topic = test_data["topic"]
            difficulty = test_data["difficulty"]
        elif client_meta:
            for item in client_meta:
                questions_map[item["question_id"]] = item
                topic = item.get("topic", topic)
                difficulty = item.get("difficulty", difficulty)
        else:
            # Fallback to DB questions
            db_qs = db.query(MockTestQuestion).all()
            for q in db_qs:
                questions_map[q.question_id] = {
                    "question_id": q.question_id,
                    "question_text": q.question_text,
                    "correct_option": q.correct_option,
                    "explanation": q.explanation,
                    "source_type": q.source_type
                }

        correct_count = 0
        total_count = len(user_answers) if user_answers else len(questions_map)
        reviews = []

        for q_id, q_item in questions_map.items():
            user_opt = user_answers.get(q_id)
            correct_opt = q_item.get("correct_option", "B")
            is_correct = (user_opt == correct_opt) if user_opt else False
            if is_correct:
                correct_count += 1

            reviews.append({
                "question_id": q_id,
                "question_text": q_item.get("question_text", "Question"),
                "user_answer": user_opt,
                "correct_answer": correct_opt,
                "is_correct": is_correct,
                "explanation": q_item.get("explanation", "Verified administrative procedure."),
                "source_type": q_item.get("source_type", "prototype_dataset")
            })

        percentage = round((correct_count / max(1, len(reviews))) * 100.0, 1)
        passed = percentage >= 60.0

        # Deterministic score recording in SQLite
        attempt = TestAttempt(
            user_id=user_id,
            topic=topic,
            difficulty=difficulty,
            score=correct_count,
            total_questions=len(reviews),
            percentage=percentage,
            created_at=datetime.datetime.utcnow()
        )
        db.add(attempt)

        # Potential Competency Progress update
        competency_updated = None
        if percentage >= 75.0:
            # Find matching competency
            matched_comp = db.query(Competency).filter(Competency.competency_name.ilike(f"%{topic}%")).first()
            if matched_comp:
                user_comp = db.query(UserCompetency).filter(
                    UserCompetency.user_id == user_id,
                    UserCompetency.competency_id == matched_comp.competency_id
                ).first()
                if user_comp:
                    old_score = user_comp.assessment_score
                    user_comp.assessment_score = max(user_comp.assessment_score, percentage)
                    if percentage >= 85.0 and user_comp.current_level < 5:
                        user_comp.current_level += 1
                    user_comp.last_assessed = datetime.datetime.utcnow()
                    competency_updated = {
                        "competency_name": matched_comp.competency_name,
                        "current_level": user_comp.current_level,
                        "new_score": user_comp.assessment_score
                    }

        db.commit()

        # Recommended Courses
        courses = db.query(Course).limit(2).all()
        rec_courses = [{
            "course_id": c.course_id,
            "course_title": c.course_title,
            "provider": c.provider,
            "duration_hours": c.duration_hours,
            "difficulty": c.difficulty,
            "course_url": c.course_url
        } for c in courses]

        feedback_narrative = (
            f"You scored {correct_count}/{len(reviews)} ({percentage}%). "
            + ("Excellent performance! You demonstrate strong proficiency in these administrative concepts." if passed else
               "Good practice attempt. Review the detailed answer explanations and study the recommended courses below to bridge remaining gaps.")
        )

        return {
            "test_id": test_id,
            "user_id": user_id,
            "score": correct_count,
            "total_questions": len(reviews),
            "percentage": percentage,
            "passed": passed,
            "reviews": reviews,
            "ai_feedback": feedback_narrative,
            "recommended_courses": rec_courses,
            "competency_updated": competency_updated
        }

test_service = TestService()