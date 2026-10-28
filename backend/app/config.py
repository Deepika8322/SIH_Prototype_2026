import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / '.env')

class Settings:
    PROJECT_NAME: str = 'AI Karmayogi Prototype v2.0'
    PROJECT_VERSION: str = '2.0.0'
    BASE_DIR: Path = BASE_DIR
    
    # SQLite Database
    DATABASE_URL: str = os.getenv('DATABASE_URL', f'sqlite:///{BASE_DIR}/karmayogi.db')
    
    # RAG / Vector Store
    RAG_DOCS_DIR: Path = BASE_DIR / 'data' / 'rag_documents'
    CHROMA_DIR: Path = BASE_DIR / 'data' / 'chroma'
    TOP_K_RETRIEVAL: int = int(os.getenv('TOP_K_RETRIEVAL', '4'))
    
    # LLM Settings
    LLM_PROVIDER: str = os.getenv('LLM_PROVIDER', 'auto')
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')
    GEMINI_API_KEY: str = os.getenv('GEMINI_API_KEY', '')
    LLM_MODEL: str = os.getenv('LLM_MODEL', 'gemini-2.5-flash')
    
settings = Settings()
