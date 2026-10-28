from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# Dashboard
class DashboardResponse(BaseModel):
    user_id: str
    name: str
    current_role: Dict[str, Any]
    target_role: Optional[Dict[str, Any]]
    overall_progress_percent: float
    competencies_count: int
    top_skill_gaps: List[Dict[str, Any]]
    courses_in_progress: List[Dict[str, Any]]
    recent_test_scores: List[Dict[str, Any]]
    recent_interviews: List[Dict[str, Any]]
    recommended_next_action: Dict[str, Any]
    prototype_disclaimer: str

# Skill Gap
class SkillGapItem(BaseModel):
    competency_id: str
    competency_name: str
    competency_type: str
    current_level: int
    required_level: int
    gap: int
    priority: str
    recommended_courses: List[Dict[str, Any]]
    practice_activity: str
    recommended_assessment: str
    ai_explanation: Optional[str] = None
    source_label: str = 'Prototype Competency Data'

class SkillGapsResponse(BaseModel):
    user_id: str
    current_role: str
    target_role: Optional[str]
    gaps: List[SkillGapItem]
    overall_summary: str

# Career Path
class CareerRecommendRequest(BaseModel):
    user_id: str
    target_role_id: str

class CareerRoadmapStep(BaseModel):
    stage: str
    title: str
    description: str
    actions: List[str]
    status: str

class CareerRecommendResponse(BaseModel):
    user_id: str
    current_role_name: str
    target_role_name: str
    typical_timeline_months: int
    readiness_status: str
    readiness_score: float
    target_competencies: List[Dict[str, Any]]
    roadmap_steps: List[CareerRoadmapStep]
    recommended_courses: List[Dict[str, Any]]
    action_plan: str
    disclaimer: str

# Mock Interview
class InterviewStartRequest(BaseModel):
    user_id: str
    role_id: str
    competency_id: Optional[str] = 'Auto'
    question_count: int = 5

class InterviewQuestionItem(BaseModel):
    question_index: int
    question_id: str
    question_text: str
    competency_id: str
    competency_name: str
    difficulty: str
    behavioral_focus: str
    source_type: str

class InterviewStartResponse(BaseModel):
    session_id: str
    role_id: str
    role_name: str
    total_questions: int
    questions: List[InterviewQuestionItem]

class InterviewAnswerRequest(BaseModel):
    session_id: str
    question_index: int
    user_answer: str

class InterviewDimensionScore(BaseModel):
    relevance: float
    clarity_and_structure: float
    reasoning_and_depth: float
    role_competency: float
    practical_judgment_ethics: float

class InterviewAnswerResponse(BaseModel):
    session_id: str
    question_index: int
    scores: InterviewDimensionScore
    average_score: float
    strengths: List[str]
    weaknesses: List[str]
    suggested_improvement: str
    competency_evaluated: str
    feedback_narrative: str
    is_last_question: bool

class InterviewResultResponse(BaseModel):
    session_id: str
    role_name: str
    overall_score: float
    total_questions: int
    summary: str
    strengths_overview: List[str]
    areas_for_growth: List[str]
    recommended_courses: List[Dict[str, Any]]
    recommended_actions: List[str]

# Mock Test
class TestGenerateRequest(BaseModel):
    user_id: str
    topic: str
    competency_id: Optional[str] = None
    difficulty: str = 'medium'
    count: int = 10

class TestQuestionItem(BaseModel):
    question_id: str
    question_text: str
    topic: str
    competency_name: str
    difficulty: str
    options: Dict[str, str] # {'A': '...', 'B': '...', 'C': '...', 'D': '...'}
    source_type: str

class TestGenerateResponse(BaseModel):
    test_id: str
    topic: str
    difficulty: str
    total_questions: int
    retrieved_count: int
    generated_count: int
    questions: List[TestQuestionItem]

class TestSubmitRequest(BaseModel):
    user_id: str
    test_id: str
    answers: Dict[str, str] # {question_id: selected_option}
    questions_meta: Optional[List[Dict[str, Any]]] = None

class TestQuestionReview(BaseModel):
    question_id: str
    question_text: str
    user_answer: Optional[str]
    correct_answer: str
    is_correct: bool
    explanation: str
    source_type: str

class TestSubmitResponse(BaseModel):
    test_id: str
    user_id: str
    score: int
    total_questions: int
    percentage: float
    passed: bool
    reviews: List[TestQuestionReview]
    ai_feedback: str
    recommended_courses: List[Dict[str, Any]]
    competency_updated: Optional[Dict[str, Any]] = None

# AI Personal Mentor
class MentorChatRequest(BaseModel):
    user_id: str
    message: str
    session_context: Optional[Dict[str, Any]] = None

class MentorChatResponse(BaseModel):
    user_id: str
    reply: str
    suggested_actions: List[str]
    suggested_exercise: Optional[str] = None
    related_courses: List[Dict[str, Any]] = []
    rag_sources: List[str] = []

# Syllabus
class SyllabusModuleItem(BaseModel):
    module_id: str
    module_name: str
    category: str
    description: str
    duration_hours: int
    learning_objectives: List[str]
    related_competencies: List[str]
    related_courses: List[Dict[str, Any]]

class SyllabusTutorRequest(BaseModel):
    module_id: str
    query_type: str # 'explain', 'study_plan', 'quiz', 'skills'
    custom_question: Optional[str] = None

class SyllabusTutorResponse(BaseModel):
    module_id: str
    response_type: str
    content: str
    rag_source: str

# Recommendations
class RecommendationItem(BaseModel):
    recommendation_id: str
    title: str
    type: str # 'course', 'practice', 'assessment'
    competency_name: str
    description: str
    priority: str
    source_type: str # 'Official/Authoritative', 'Verified Reference', 'Prototype Data', 'AI Generated'
    why_explanation: str
    action_payload: Dict[str, Any]

class RecommendationExplainResponse(BaseModel):
    recommendation_id: str
    current_level: int
    target_level: int
    gap: int
    evidence: List[str]
    expected_outcome: str
    source_category: str
    disclaimer: str
