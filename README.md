# AI Karmayogi Prototype v2.0
## RAG + LLM Competency, Learning, Development and Career Assistant

> **Disclaimer:** This is an independent AI prototype inspired by the capacity-building principles of the National Programme for Civil Services Capacity Building (NPCSCB / Mission Karmayogi / iGOT). It is **not** an official Government of India recruitment, promotion, transfer, or competency-decision system.

---

## 🌟 Key Features

1. **AI Mock Interview Simulator (Feature 1)**:
   - Target role & competency selection.
   - Situational & STAR (Situation, Task, Action, Result) response format.
   - 5-Dimension scoring (1.0 to 5.0 on Relevance, Clarity, Reasoning, Role Competency, and Ethics/Judgment).
   - Dynamic question generation fallback when the question bank is insufficient.
   - Comprehensive performance report and action roadmap.

2. **Skill Gap Analysis (Feature 2)**:
   - Deterministic arithmetic calculation: `gap = required_level - current_level`.
   - Priority tagging (Meets Target, Small, Moderate, High Priority).
   - Direct links to iGOT learning tracks and diagnostic assessments.
   - RAG-grounded personalized growth narratives.

3. **Career Path Planner (Feature 3)**:
   - Current Role → Target Role progression roadmaps.
   - 4-Phase interactive developmental milestones (Foundation, Simulation, Advanced Mastery, Benchmark Transition).
   - Readiness benchmark percentage calculation.

4. **Common Syllabus & AI Tutor (Feature 4)**:
   - 6 core public administration curriculum modules.
   - Interactive grounded AI Syllabus Tutor (Study plans, diagnostic quiz reviews, and learning objectives).

5. **Dynamic AI Mock Tests (Feature 5)**:
   - Retrieval + LLM Dynamic Generation fallback (Mode C: e.g. 3 Database MCQs + 7 on-the-fly Generated MCQs).
   - Automatic competency level upgrades in SQLite when scoring $\ge 75\%$.
   - Comprehensive administrative explanations (GFR, CSMOP, Citizen Charter).

6. **AI Personal Mentor (Feature 6)**:
   - Profile-aware continuous coaching assistant.
   - Suggested action steps, 15-minute practical micro-exercises, and discretionary judgment follow-up questions.

7. **Explainable Recommendations Engine (Feature 7)**:
   - Grounded "Why am I seeing this?" modal with full evidence chain.
   - Clear source credibility indicators (*Official/Verified Reference*, *Prototype Data*, *AI Generated*).

8. **Competency Progress Passport**:
   - Central learner development record tracking competency level progress (1 to 5 scale), test history, and interview history.
   - One-click demo progress reset tool.

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+ installed.

### 2. Install Dependencies
```bash
cd karmayogi-ai
pip install -r backend/requirements.txt
```

### 3. Seed Database & Ingest Knowledge Repository
```bash
python scripts/seed_database.py
python scripts/ingest_rag.py
```

### 4. Launch Application
```bash
python backend/app/main.py
```
Open your browser at **[http://localhost:8000](http://localhost:8000)**.

### 5. Run Automated Tests
```bash
pytest backend/tests/test_karmayogi.py -v
```

---

## 🏗️ Architecture

```
                    USER
                      │
                      ▼
              APPLICATION BACKEND (FastAPI)
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
   STRUCTURED DB             RAG / VECTOR DB
   Users, Roles,             Competencies, Guides,
   Skills, Scores,           Syllabus, Mentoring
   Questions (SQLite)        Knowledge (Chroma/JSON)
          │                       │
          └───────────┬───────────┘
                      ▼
                     LLM (Gemini / OpenAI / Fallback)
                      │
      ┌───────────┬───┴───────┬───────────┐
      ▼           ▼           ▼           ▼
  INTERVIEW   SKILL GAP    CAREER     MOCK TEST / MENTOR
```
