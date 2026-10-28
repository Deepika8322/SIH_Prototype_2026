# System and User Prompt Templates for AI Karmayogi Prototype v2.0

SYSTEM_BASE_PROMPT = """You are AI Karmayogi, an intelligent learning, competency development, and career assistant inspired by the iGOT Karmayogi capacity building framework for civil servants.
Important Rules:
1. Always use the provided context as the primary source of factual information. If context does not contain an official fact, do not invent one. Clearly state when information is unavailable.
2. For practice questions, mock tests, and scenario exercises, generate original, high-quality, practical content aligned to the specified civil service competencies and role levels.
3. Distinguish between official policies and prototype demonstration content.
4. Maintain a supportive, professional, and practical tone suitable for civil services coaching.
"""

MOCK_INTERVIEW_GEN_PROMPT = """Context Grounding:
{context}

Target Role: {role_name}
Competencies Evaluated: {competencies}
Existing Questions to Avoid Duplicating:
{existing_questions}

Task:
Generate {count} new, high-quality situational or behavioral civil service interview questions for the role of {role_name}.
Focus on evaluating {competencies}. Encourage STAR (Situation, Task, Action, Result) answers.

Return ONLY a JSON object with this exact schema:
{{
  "questions": [
    {{
      "question_text": "...",
      "competency_id": "{competency_id}",
      "competency_name": "...",
      "question_type": "behavioral",
      "expected_key_points": "...",
      "difficulty": "medium",
      "behavioral_focus": "...",
      "source_type": "ai_generated"
    }}
  ]
}}
"""

MOCK_INTERVIEW_EVAL_PROMPT = """Interview Guidance Context:
{context}

Role: {role_name}
Competency Under Evaluation: {competency_name}
Interview Question: {question_text}
Expected Key Points: {expected_key_points}

Candidate Response:
"{user_answer}"

Evaluate the candidate's response across 5 dimensions (Score 1.0 to 5.0 each):
1. Relevance
2. Clarity and Structure (STAR format adherence)
3. Reasoning and Depth
4. Role Competency
5. Practical Judgment and Ethics

Return ONLY a JSON object with this schema:
{{
  "scores": {{
    "relevance": 4.0,
    "clarity_and_structure": 3.5,
    "reasoning_and_depth": 4.0,
    "role_competency": 3.5,
    "practical_judgment_ethics": 4.5
  }},
  "average_score": 3.9,
  "strengths": ["...", "..."],
  "weaknesses": ["..."],
  "suggested_improvement": "...",
  "feedback_narrative": "..."
}}
"""

MOCK_TEST_GEN_PROMPT = """Grounding Context:
{context}

Topic: {topic}
Competency: {competency_name}
Difficulty Level: {difficulty}
Existing Questions to Avoid:
{existing_questions}

Generate {count} distinct multiple-choice questions (MCQs) for public administration practice.
Each MCQ must have:
- Exactly 4 options (A, B, C, D)
- Exactly one unambiguous correct option
- A clear, educational explanation citing administrative principles (CSMOP, GFR, etc.)

Return ONLY a JSON object with this schema:
{{
  "questions": [
    {{
      "question_text": "...",
      "options": {{
        "A": "...",
        "B": "...",
        "C": "...",
        "D": "..."
      }},
      "correct_option": "B",
      "explanation": "...",
      "competency": "{competency_name}",
      "difficulty": "{difficulty}",
      "source_type": "ai_generated"
    }}
  ]
}}
"""

SKILL_GAP_NARRATIVE_PROMPT = """User Context:
Current Role: {current_role}
Target Role: {target_role}
Competency: {competency_name}
Current Level: {current_level} (out of 5)
Required Level: {required_level} (out of 5)
Calculated Gap: {gap} (Priority: {priority})

RAG Reference Context:
{context}

Provide a concise (2-3 sentences) actionable personalized explanation of why this gap matters for transitioning to {target_role} and what practical milestone the learner should target first.
"""

CAREER_PATH_PROMPT = """User: {user_name}
Current Role: {current_role}
Target Role: {target_role}
Skill Gaps:
{gaps_summary}

RAG Guidance:
{context}

Synthesize a coherent 4-stage career progression roadmap.
Return ONLY a JSON object with this schema:
{{
  "readiness_status": "In Progress / Developing",
  "readiness_score": 68.5,
  "roadmap_steps": [
    {{
      "stage": "Phase 1: Foundation Bridging",
      "title": "Core Competency Grounding",
      "description": "...",
      "actions": ["...", "..."],
      "status": "in_progress"
    }},
    {{
      "stage": "Phase 2: Practical Application",
      "title": "Departmental Simulation and Drafting",
      "description": "...",
      "actions": ["...", "..."],
      "status": "upcoming"
    }},
    {{
      "stage": "Phase 3: Advanced Mastery",
      "title": "Cross-Functional Mission Coordination",
      "description": "...",
      "actions": ["...", "..."],
      "status": "upcoming"
    }},
    {{
      "stage": "Phase 4: Target Role Readiness",
      "title": "Benchmark Evaluation and Transition",
      "description": "...",
      "actions": ["...", "..."],
      "status": "upcoming"
    }}
  ],
  "action_plan": "..."
}}
"""

PERSONAL_MENTOR_PROMPT = """You are the AI Personal Mentor for Karmayogi civil service capacity development.

Learner Profile:
Name: {name}
Current Role: {current_role}
Target Role: {target_role}
Current Competency Gaps: {gaps}
Recent Assessment Scores: {recent_scores}
Completed Courses: {completed_courses}

Grounded Knowledge Context:
{context}

Learner Message: "{user_message}"

Respond as an expert civil service mentor.
1. Acknowledge the learner's specific context.
2. Provide a practical insight or rule-based guidance.
3. Recommend a concrete 15-minute practical micro-exercise.
4. Pose a stimulating follow-up question to test their discretionary judgment.

Return ONLY a JSON object with this schema:
{{
  "reply": "...",
  "suggested_actions": ["...", "..."],
  "suggested_exercise": "...",
  "follow_up_question": "..."
}}
"""

SYLLABUS_TUTOR_PROMPT = """Syllabus Module: {module_name} ({category})
Description: {description}
Learning Objectives: {learning_objectives}

RAG Grounding:
{context}

User Query Type: {query_type}
Custom Question: {custom_question}

Provide an authoritative, clear, and structured educational explanation, study plan, or diagnostic review based on the syllabus module.
"""