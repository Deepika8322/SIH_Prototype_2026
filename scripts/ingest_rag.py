import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))

from app.services.rag_service import rag_service

if __name__ == '__main__':
    print('Starting RAG document ingestion...')
    rag_service.ingest()
    print('RAG knowledge base successfully created and indexed!')
