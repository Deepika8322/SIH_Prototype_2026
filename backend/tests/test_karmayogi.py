import os
import sys
import pytest

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app'))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.api import (
    dashboard,
    skill_gap,
    career,
    interview,
    tests,
    mentor,
    recommendations,
    syllabus
)
from app.schemas.schemas import (
    CareerRecommendRequest,
    InterviewStartRequest,
    InterviewAnswerRequest,
    TestGenerateRequest,
    TestSubmitRequest,
    MentorChatRequest,
    SyllabusTutorRequest
)
from app.services.rag_service import rag_service

@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def test_health_check():
    from app.main import health_check
    data = health_check()
    assert data['status'] == 'healthy'
    assert 'AI Karmayogi' in data['project']

def test_dashboard_user(db):
    data = dashboard.get_dashboard('U001', db)
    assert data['user_id'] == 'U001'
    assert 'Aarav' in data['name']
    assert data['current_role']['role_name'] == 'Section Officer'
    assert data['target_role']['role_name'] == 'Project Officer'
    assert len(data['top_skill_gaps']) > 0
    assert 'prototype_disclaimer' in data

def test_skill_gaps_calculation(db):
    data = skill_gap.get_user_skill_gaps('U001', target_role_id='R002', db=db)
    assert data['user_id'] == 'U001'
    assert len(data['gaps']) > 0
    
    for gap in data['gaps']:
        assert gap['gap'] == gap['required_level'] - gap['current_level']
        assert 'recommended_courses' in gap
        assert 'source_label' in gap

def test_career_roadmap(db):
    req = CareerRecommendRequest(user_id='U001', target_role_id='R002')
    data = career.recommend_career(req, db)
    assert data['current_role_name'] == 'Section Officer'
    assert data['target_role_name'] == 'Project Officer'
    assert data['readiness_score'] > 0
    assert len(data['roadmap_steps']) >= 3
    assert 'disclaimer' in data

def test_mock_interview_flow(db):
    # 1. Start Interview
    req = InterviewStartRequest(
        user_id='U001',
        role_id='R002',
        competency_id='Auto',
        question_count=3
    )
    start_data = interview.start_interview(req, db)
    session_id = start_data['session_id']
    assert len(start_data['questions']) == 3

    # 2. Submit Answer
    ans_req = InterviewAnswerRequest(
        session_id=session_id,
        question_index=1,
        user_answer='In my previous role as Section Officer, Situation was an urgent cabinet note delay. Task was to align finance and law wings. Action: I scheduled a same-day joint consultation referencing CSMOP rules. Result: Cabinet note cleared in 24 hours.'
    )
    ans_data = interview.answer_interview(session_id, ans_req, db)
    assert 'scores' in ans_data
    assert ans_data['average_score'] >= 1.0
    assert len(ans_data['strengths']) > 0

    # 3. Get Result Report
    res_data = interview.get_interview_result(session_id, db)
    assert 'overall_score' in res_data
    assert 'summary' in res_data

def test_dynamic_mock_test_generation_and_submission(db):
    # Request 10 questions (tests retrieval + dynamic LLM generation fallback Mode C)
    gen_req = TestGenerateRequest(
        user_id='U001',
        topic='Project Management',
        difficulty='medium',
        count=10
    )
    gen_data = tests.generate_mock_test(gen_req, db)
    test_id = gen_data['test_id']
    assert gen_data['total_questions'] == 10
    assert gen_data['retrieved_count'] + gen_data['generated_count'] == 10
    assert len(gen_data['questions']) == 10

    # Test question format
    q1 = gen_data['questions'][0]
    assert 'options' in q1
    assert 'A' in q1['options']
    assert 'B' in q1['options']

    # Submit test answers
    answers = {q['question_id']: 'B' for q in gen_data['questions']}
    sub_req = TestSubmitRequest(
        user_id='U001',
        test_id=test_id,
        answers=answers
    )
    sub_data = tests.submit_mock_test(test_id, sub_req, db)
    assert sub_data['total_questions'] == 10
    assert 'percentage' in sub_data
    assert len(sub_data['reviews']) == 10

def test_mentor_chat(db):
    req = MentorChatRequest(
        user_id='U001',
        message='How can I improve my discretionary decision making under GFR 2017?'
    )
    data = mentor.mentor_chat(req, db)
    assert 'reply' in data
    assert len(data['suggested_actions']) > 0
    assert 'rag_sources' in data

def test_syllabus_and_tutor(db):
    # Listing
    modules = syllabus.list_syllabus(db)
    assert len(modules) >= 6

    # AI Tutor Query
    tutor_req = SyllabusTutorRequest(
        module_id=modules[0]['module_id'],
        query_type='explain'
    )
    tutor_data = syllabus.ask_syllabus_tutor(tutor_req, db)
    assert 'content' in tutor_data
    assert 'rag_source' in tutor_data

def test_passport_and_reset(db):
    # Passport View
    pass_data = dashboard.get_passport('U001', db)
    assert len(pass_data['competencies']) == 7

    # Reset Baseline
    reset_data = dashboard.reset_user_progress('U001', db)
    assert reset_data['status'] == 'success'

def test_recommendation_explain(db):
    data = recommendations.explain_recommendation(user_id='U001', recommendation_id='REC_001', db=db)
    assert 'evidence' in data
    assert 'expected_outcome' in data
