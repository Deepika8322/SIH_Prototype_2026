import os
import csv
import sys
from pathlib import Path
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))

from app.database import engine, Base, SessionLocal
from app.models.entities import (
    User, Role, Competency, RoleCompetency, Course, CareerPath,
    InterviewQuestion, MockTestQuestion, SyllabusModule, MentorGuidance,
    UserCompetency, UserCourseProgress, TestAttempt, InterviewAttempt
)

BASE_DIR = Path(__file__).resolve().parent.parent
STRUCTURED_DIR = BASE_DIR / 'data' / 'structured'

def seed():
    print('Initializing database tables...')
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 1. Roles
        with open(STRUCTURED_DIR / 'roles.csv', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                db.add(Role(
                    role_id=row['role_id'],
                    role_name=row['role_name'],
                    department=row['department'],
                    description=row['description'],
                    level_min=int(row['level_min']),
                    level_max=int(row['level_max'])
                ))
        
        # 2. Competencies
        with open(STRUCTURED_DIR / 'competencies.csv', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                db.add(Competency(
                    competency_id=row['competency_id'],
                    competency_name=row['competency_name'],
                    competency_type=row['competency_type'],
                    description=row['description'],
                    level_1_description=row['level_1_description'],
                    level_2_description=row['level_2_description'],
                    level_3_description=row['level_3_description'],
                    level_4_description=row['level_4_description'],
                    level_5_description=row['level_5_description']
                ))

        # 3. Role Competencies
        with open(STRUCTURED_DIR / 'role_competency_matrix.csv', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                db.add(RoleCompetency(
                    role_id=row['role_id'],
                    competency_id=row['competency_id'],
                    required_level=int(row['required_level']),
                    priority=row['priority']
                ))

        # 4. Courses
        with open(STRUCTURED_DIR / 'courses.csv', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                db.add(Course(
                    course_id=row['course_id'],
                    course_title=row['course_title'],
                    competency_id=row['competency_id'],
                    provider=row['provider'],
                    duration_hours=int(row['duration_hours']),
                    description=row['description'],
                    difficulty=row['difficulty'],
                    course_url=row['course_url']
                ))

        # 5. Users
        with open(STRUCTURED_DIR / 'sample_users.csv', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                db.add(User(
                    user_id=row['user_id'],
                    name=row['name'],
                    email=row['email'],
                    current_role_id=row['current_role_id'],
                    target_role_id=row['target_role_id'],
                    department=row['department'],
                    date_joined=row['date_joined']
                ))

        # 6. Interview Questions
        with open(STRUCTURED_DIR / 'interview_questions.csv', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                db.add(InterviewQuestion(
                    question_id=row['question_id'],
                    role_id=row['role_id'],
                    competency_id=row['competency_id'],
                    question_text=row['question_text'],
                    question_type=row['question_type'],
                    expected_key_points=row['expected_key_points'],
                    difficulty=row['difficulty'],
                    behavioral_focus=row['behavioral_focus']
                ))

        # 7. Mock Test Questions
        with open(STRUCTURED_DIR / 'mock_test_questions.csv', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                db.add(MockTestQuestion(
                    question_id=row['question_id'],
                    topic=row['topic'],
                    competency_id=row['competency_id'],
                    difficulty=row['difficulty'],
                    question_text=row['question_text'],
                    option_a=row['option_a'],
                    option_b=row['option_b'],
                    option_c=row['option_c'],
                    option_d=row['option_d'],
                    correct_option=row['correct_option'],
                    explanation=row['explanation'],
                    source_type=row['source_type']
                ))

        # 8. Syllabus
        with open(STRUCTURED_DIR / 'common_syllabus.csv', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                db.add(SyllabusModule(
                    module_id=row['module_id'],
                    module_name=row['module_name'],
                    category=row['category'],
                    description=row['description'],
                    duration_hours=int(row['duration_hours']),
                    learning_objectives=row['learning_objectives'],
                    related_competencies=row['related_competencies']
                ))

        # 9. Career Paths
        with open(STRUCTURED_DIR / 'career_paths.csv', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                db.add(CareerPath(
                    path_id=row['path_id'],
                    from_role_id=row['from_role_id'],
                    to_role_id=row['to_role_id'],
                    typical_timeline_months=int(row['typical_timeline_months']),
                    prerequisite_competencies=row['prerequisite_competencies'],
                    recommended_action_plan=row['recommended_action_plan']
                ))

        # 10. Mentor Guidance
        with open(STRUCTURED_DIR / 'mentor_guidance.csv', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                db.add(MentorGuidance(
                    guidance_id=row['guidance_id'],
                    competency_id=row['competency_id'],
                    gap_level=int(row['gap_level']),
                    coaching_tip=row['coaching_tip'],
                    suggested_exercise=row['suggested_exercise'],
                    follow_up_prompt=row['follow_up_prompt']
                ))

        # Baseline Competencies for Demo User U001 (Aarav Sharma - Section Officer)
        # Decision Making: 2 (Required for SO: 3, for Project Officer: 4 -> Gap = 2)
        # Project Management: 2 (Required for SO: 2, for Project Officer: 4 -> Gap = 2)
        # Public Service Ethics: 3 (Required for SO: 3 -> Meets target)
        # Govt Communication: 4 (Required for SO: 4 -> Meets target)
        # Digital Governance: 2 (Required for SO: 2, for Project Officer: 4 -> Gap = 2)
        # Public Procurement: 3 (Required for SO: 3 -> Meets target)
        # Citizen Centricity: 2 (Required for SO: 2, for Project Officer: 3 -> Gap = 1)
        user_comps = [
            ('U001', 'C001', 2, 65.0),
            ('U001', 'C002', 2, 60.0),
            ('U001', 'C003', 3, 85.0),
            ('U001', 'C004', 4, 90.0),
            ('U001', 'C005', 2, 58.0),
            ('U001', 'C006', 3, 78.0),
            ('U001', 'C007', 2, 70.0),
            
            # User U002 Priya
            ('U002', 'C001', 3, 75.0),
            ('U002', 'C002', 3, 80.0),
            ('U002', 'C003', 3, 82.0),
            ('U002', 'C004', 3, 75.0),
            ('U002', 'C005', 4, 88.0),
            ('U002', 'C006', 3, 72.0),
            ('U002', 'C007', 3, 80.0),
        ]
        for uid, cid, lvl, score in user_comps:
            db.add(UserCompetency(
                user_id=uid,
                competency_id=cid,
                current_level=lvl,
                assessment_score=score,
                last_assessed=datetime.utcnow()
            ))

        # Initial Course Progress
        db.add(UserCourseProgress(user_id='U001', course_id='CRS003', status='completed', progress_percent=100, completed_at=datetime.utcnow()))
        db.add(UserCourseProgress(user_id='U001', course_id='CRS001', status='in_progress', progress_percent=45, completed_at=None))
        db.add(UserCourseProgress(user_id='U001', course_id='CRS002', status='in_progress', progress_percent=20, completed_at=None))

        # Initial Test Attempts
        db.add(TestAttempt(user_id='U001', topic='Government Communication', difficulty='foundational', score=9, total_questions=10, percentage=90.0, created_at=datetime.utcnow()))
        db.add(TestAttempt(user_id='U001', topic='Project Management', difficulty='medium', score=6, total_questions=10, percentage=60.0, created_at=datetime.utcnow()))

        # Initial Interview Attempt
        db.add(InterviewAttempt(
            session_id='INIT_SESS_001',
            user_id='U001',
            role_id='R001',
            competency_id='C004',
            overall_score=4.2,
            strengths='Structured CSMOP file noting logic; objective legal reference citations.',
            weaknesses='Could elaborate more on proactive risk management in inter-ministerial coordination.',
            feedback='Strong command over secretariat office procedures. Ready to transition toward project management scenarios.',
            created_at=datetime.utcnow()
        ))

        db.commit()
        print('Database successfully seeded with 10 tables, sample users, baseline competencies, and demo history!')
    except Exception as e:
        db.rollback()
        print(f'Error seeding database: {e}')
        raise e
    finally:
        db.close()

if __name__ == '__main__':
    seed()
