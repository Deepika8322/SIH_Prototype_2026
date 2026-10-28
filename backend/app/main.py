import os
import sys
from pathlib import Path

# Add backend directory to sys.path
BASE_BACKEND = Path(__file__).resolve().parent.parent
if str(BASE_BACKEND) not in sys.path:
    sys.path.insert(0, str(BASE_BACKEND))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import settings
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

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="AI Karmayogi Prototype v2.0 - RAG + LLM Competency, Learning, Development and Career Assistant"
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers
app.include_router(dashboard.router, prefix="/api", tags=["Dashboard & Passport"])
app.include_router(skill_gap.router, prefix="/api", tags=["Skill Gap Analysis"])
app.include_router(career.router, prefix="/api", tags=["Career Path Planner"])
app.include_router(interview.router, prefix="/api", tags=["AI Mock Interview"])
app.include_router(tests.router, prefix="/api", tags=["AI Mock Test"])
app.include_router(mentor.router, prefix="/api", tags=["AI Personal Mentor"])
app.include_router(recommendations.router, prefix="/api", tags=["Learning Recommendations"])
app.include_router(syllabus.router, prefix="/api", tags=["Common Syllabus"])

@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "llm_provider": settings.LLM_PROVIDER,
        "llm_model": settings.LLM_MODEL
    }

# Static file serving for Frontend
STATIC_DIR = settings.BASE_DIR / "frontend" / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @app.get("/")
    def serve_frontend_root():
        index_file = STATIC_DIR / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return {"message": "Frontend static file index.html not found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
