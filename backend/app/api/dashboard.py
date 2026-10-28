from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.entities import User, Role, Competency, UserCompetency, UserCourseProgress, Course, TestAttempt, InterviewAttempt, RoleCompetency
import datetime

router = APIRouter()

@router.get('/dashboard/{user_id}')
def get_dashboard(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    current_role = db.query(Role).filter(Role.role_id == user.current_role_id).first()
    target_role = db.query(Role).filter(Role.role_id == user.target_role_id).first()

    # User competencies
    user_comps = db.query(UserCompetency).filter(UserCompetency.user_id == user_id).all()
    comp_count = len(user_comps)
    avg_score = sum(c.assessment_score for c in user_comps) / max(1, comp_count) if comp_count else 0.0

    # Skill gaps for target role
    target_role_id = user.target_role_id or 'R002'
    target_rcs = db.query(RoleCompetency).filter(RoleCompetency.role_id == target_role_id).all()
    user_comp_map = {uc.competency_id: uc for uc in user_comps}
    
    top_gaps = []
    for rc in target_rcs:
        comp = db.query(Competency).filter(Competency.competency_id == rc.competency_id).first()
        if not comp:
            continue
        u_comp = user_comp_map.get(rc.competency_id)
        c_lvl = u_comp.current_level if u_comp else 1
        r_lvl = rc.required_level
        gap = r_lvl - c_lvl
        if gap > 0:
            top_gaps.append({
                'competency_id': comp.competency_id,
                'competency_name': comp.competency_name,
                'current_level': c_lvl,
                'required_level': r_lvl,
                'gap': gap,
                'priority': rc.priority or 'High'
            })
    top_gaps.sort(key=lambda x: x['gap'], reverse=True)

    # Courses in progress
    course_progs = db.query(UserCourseProgress).filter(UserCourseProgress.user_id == user_id).all()
    courses_data = []
    for cp in course_progs:
        c = db.query(Course).filter(Course.course_id == cp.course_id).first()
        if c:
            courses_data.append({
                'course_id': c.course_id,
                'course_title': c.course_title,
                'provider': c.provider,
                'status': cp.status,
                'progress_percent': cp.progress_percent,
                'course_url': c.course_url
            })

    # Recent test scores
    recent_tests = db.query(TestAttempt).filter(TestAttempt.user_id == user_id).order_by(TestAttempt.id.desc()).limit(3).all()
    tests_data = [{
        'id': t.id,
        'topic': t.topic,
        'difficulty': t.difficulty,
        'score': t.score,
        'total_questions': t.total_questions,
        'percentage': t.percentage,
        'created_at': t.created_at.strftime('%Y-%m-%d %H:%M') if t.created_at else ''
    } for t in recent_tests]

    # Recent interviews
    recent_interviews = db.query(InterviewAttempt).filter(InterviewAttempt.user_id == user_id).order_by(InterviewAttempt.id.desc()).limit(2).all()
    interviews_data = [{
        'id': i.id,
        'session_id': i.session_id,
        'overall_score': i.overall_score,
        'strengths': i.strengths,
        'feedback': i.feedback,
        'created_at': i.created_at.strftime('%Y-%m-%d %H:%M') if i.created_at else ''
    } for i in recent_interviews]

    return {
        'user_id': user.user_id,
        'name': user.name,
        'department': user.department,
        'current_role': {
            'role_id': current_role.role_id if current_role else '',
            'role_name': current_role.role_name if current_role else 'Section Officer',
            'department': current_role.department if current_role else ''
        },
        'target_role': {
            'role_id': target_role.role_id if target_role else 'R002',
            'role_name': target_role.role_name if target_role else 'Project Officer',
            'department': target_role.department if target_role else ''
        },
        'overall_progress_percent': round(avg_score, 1),
        'competencies_count': comp_count,
        'top_skill_gaps': top_gaps[:3],
        'courses_in_progress': courses_data,
        'recent_test_scores': tests_data,
        'recent_interviews': interviews_data,
        'recommended_next_action': {
            'title': 'Bridge Project Management Gap (Level 2 -> Level 4)',
            'type': 'course_and_test',
            'description': 'Complete Module 1 of Project Management Essentials and take the 5-question diagnostic mock assessment.',
            'action_link': '/tests'
        },
        'prototype_disclaimer': 'This is a prototype inspired by Karmayogi/iGOT for demonstration. It is not an official government recruitment, transfer, or eligibility system.'
    }

@router.get('/passport/{user_id}')
def get_passport(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    user_comps = db.query(UserCompetency).filter(UserCompetency.user_id == user_id).all()
    comps_data = []
    for uc in user_comps:
        comp = db.query(Competency).filter(Competency.competency_id == uc.competency_id).first()
        if comp:
            comps_data.append({
                'competency_id': comp.competency_id,
                'competency_name': comp.competency_name,
                'competency_type': comp.competency_type,
                'current_level': uc.current_level,
                'assessment_score': uc.assessment_score,
                'last_assessed': uc.last_assessed.strftime('%Y-%m-%d') if uc.last_assessed else '2024-01-15'
            })

    test_history = db.query(TestAttempt).filter(TestAttempt.user_id == user_id).order_by(TestAttempt.id.desc()).all()
    interview_history = db.query(InterviewAttempt).filter(InterviewAttempt.user_id == user_id).order_by(InterviewAttempt.id.desc()).all()

    return {
        'user_id': user.user_id,
        'name': user.name,
        'current_role_id': user.current_role_id,
        'target_role_id': user.target_role_id,
        'competencies': comps_data,
        'test_history': [{
            'topic': t.topic,
            'score': t.score,
            'total_questions': t.total_questions,
            'percentage': t.percentage,
            'date': t.created_at.strftime('%Y-%m-%d %H:%M') if t.created_at else ''
        } for t in test_history],
        'interview_history': [{
            'session_id': i.session_id,
            'overall_score': i.overall_score,
            'feedback': i.feedback,
            'date': i.created_at.strftime('%Y-%m-%d %H:%M') if i.created_at else ''
        } for i in interview_history],
        'disclaimer': 'The Progress Passport is a prototype development record and does not constitute an official government service book entry.'
    }

@router.post('/passport/{user_id}/reset')
def reset_user_progress(user_id: str, db: Session = Depends(get_db)):
    # Reset competencies to baseline demo state
    baseline = [
        ('C001', 2, 65.0),
        ('C002', 2, 60.0),
        ('C003', 3, 85.0),
        ('C004', 4, 90.0),
        ('C005', 2, 58.0),
        ('C006', 3, 78.0),
        ('C007', 2, 70.0)
    ]
    for cid, lvl, score in baseline:
        uc = db.query(UserCompetency).filter(UserCompetency.user_id == user_id, UserCompetency.competency_id == cid).first()
        if uc:
            uc.current_level = lvl
            uc.assessment_score = score
            uc.last_assessed = datetime.datetime.utcnow()
    db.commit()
    return {'status': 'success', 'message': f'Progress state for demo user {user_id} successfully reset to baseline.'}