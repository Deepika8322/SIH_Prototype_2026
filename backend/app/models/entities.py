import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from app.database import Base

class User(Base):
    __tablename__ = 'users'
    user_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    current_role_id = Column(String, ForeignKey('roles.role_id'))
    target_role_id = Column(String, ForeignKey('roles.role_id'))
    department = Column(String)
    date_joined = Column(String)

class Role(Base):
    __tablename__ = 'roles'
    role_id = Column(String, primary_key=True, index=True)
    role_name = Column(String, nullable=False)
    department = Column(String)
    description = Column(Text)
    level_min = Column(Integer)
    level_max = Column(Integer)

class Competency(Base):
    __tablename__ = 'competencies'
    competency_id = Column(String, primary_key=True, index=True)
    competency_name = Column(String, nullable=False)
    competency_type = Column(String)
    description = Column(Text)
    level_1_description = Column(Text)
    level_2_description = Column(Text)
    level_3_description = Column(Text)
    level_4_description = Column(Text)
    level_5_description = Column(Text)

class RoleCompetency(Base):
    __tablename__ = 'role_competencies'
    id = Column(Integer, primary_key=True, autoincrement=True)
    role_id = Column(String, ForeignKey('roles.role_id'), index=True)
    competency_id = Column(String, ForeignKey('competencies.competency_id'), index=True)
    required_level = Column(Integer, nullable=False)
    priority = Column(String)

class Course(Base):
    __tablename__ = 'courses'
    course_id = Column(String, primary_key=True, index=True)
    course_title = Column(String, nullable=False)
    competency_id = Column(String, ForeignKey('competencies.competency_id'))
    provider = Column(String)
    duration_hours = Column(Integer)
    description = Column(Text)
    difficulty = Column(String)
    course_url = Column(String)

class CareerPath(Base):
    __tablename__ = 'career_paths'
    path_id = Column(String, primary_key=True, index=True)
    from_role_id = Column(String, ForeignKey('roles.role_id'))
    to_role_id = Column(String, ForeignKey('roles.role_id'))
    typical_timeline_months = Column(Integer)
    prerequisite_competencies = Column(Text)
    recommended_action_plan = Column(Text)

class InterviewQuestion(Base):
    __tablename__ = 'interview_questions'
    question_id = Column(String, primary_key=True, index=True)
    role_id = Column(String, ForeignKey('roles.role_id'))
    competency_id = Column(String, ForeignKey('competencies.competency_id'))
    question_text = Column(Text, nullable=False)
    question_type = Column(String)
    expected_key_points = Column(Text)
    difficulty = Column(String)
    behavioral_focus = Column(String)

class MockTestQuestion(Base):
    __tablename__ = 'mock_test_questions'
    question_id = Column(String, primary_key=True, index=True)
    topic = Column(String)
    competency_id = Column(String, ForeignKey('competencies.competency_id'))
    difficulty = Column(String)
    question_text = Column(Text, nullable=False)
    option_a = Column(Text, nullable=False)
    option_b = Column(Text, nullable=False)
    option_c = Column(Text, nullable=False)
    option_d = Column(Text, nullable=False)
    correct_option = Column(String, nullable=False)
    explanation = Column(Text)
    source_type = Column(String, default='prototype_dataset')

class SyllabusModule(Base):
    __tablename__ = 'syllabus'
    module_id = Column(String, primary_key=True, index=True)
    module_name = Column(String, nullable=False)
    category = Column(String)
    description = Column(Text)
    duration_hours = Column(Integer)
    learning_objectives = Column(Text)
    related_competencies = Column(String)

class MentorGuidance(Base):
    __tablename__ = 'mentor_guidance'
    guidance_id = Column(String, primary_key=True, index=True)
    competency_id = Column(String, ForeignKey('competencies.competency_id'))
    gap_level = Column(Integer)
    coaching_tip = Column(Text)
    suggested_exercise = Column(Text)
    follow_up_prompt = Column(Text)

class UserCompetency(Base):
    __tablename__ = 'user_competencies'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('users.user_id'), index=True)
    competency_id = Column(String, ForeignKey('competencies.competency_id'), index=True)
    current_level = Column(Integer, default=1)
    assessment_score = Column(Float, default=70.0)
    last_assessed = Column(DateTime, default=datetime.datetime.utcnow)

class UserCourseProgress(Base):
    __tablename__ = 'user_course_progress'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('users.user_id'), index=True)
    course_id = Column(String, ForeignKey('courses.course_id'))
    status = Column(String, default='in_progress')
    progress_percent = Column(Integer, default=0)
    completed_at = Column(DateTime, nullable=True)

class TestAttempt(Base):
    __tablename__ = 'test_attempts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('users.user_id'), index=True)
    topic = Column(String)
    difficulty = Column(String)
    score = Column(Integer)
    total_questions = Column(Integer)
    percentage = Column(Float)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class InterviewAttempt(Base):
    __tablename__ = 'interview_attempts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, index=True)
    user_id = Column(String, ForeignKey('users.user_id'), index=True)
    role_id = Column(String, ForeignKey('roles.role_id'))
    competency_id = Column(String)
    overall_score = Column(Float)
    strengths = Column(Text)
    weaknesses = Column(Text)
    feedback = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
