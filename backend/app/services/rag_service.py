import os
import json
import re
import math
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.config import settings

class RAGService:
    def __init__(self):
        self.docs_dir = Path(settings.RAG_DOCS_DIR)
        self.store_dir = Path(settings.CHROMA_DIR)
        self.store_file = self.store_dir / 'rag_store.json'
        self.chunks: List[Dict[str, Any]] = []
        self._load_store()

    def _load_store(self):
        if self.store_file.exists():
            try:
                with open(self.store_file, 'r', encoding='utf-8') as f:
                    self.chunks = json.load(f)
            except Exception as e:
                print(f'Warning: Could not load vector store: {e}')
                self.chunks = []
        if not self.chunks:
            self.ingest()

    def _tokenize(self, text: str) -> List[str]:
        words = re.findall(r'\w+', text.lower())
        return [w for w in words if len(w) > 2]

    def chunk_document(self, filename: str, content: str) -> List[Dict[str, Any]]:
        chunks = []
        sections = re.split(r'\n(?=##?\s)', content)
        doc_type = 'general'
        if 'competency' in filename:
            doc_type = 'competency'
        elif 'interview' in filename:
            doc_type = 'interview'
        elif 'skill_gap' in filename:
            doc_type = 'skill_gap'
        elif 'mentor' in filename:
            doc_type = 'mentor'
        elif 'career' in filename:
            doc_type = 'career'
        elif 'syllabus' in filename:
            doc_type = 'syllabus'

        for idx, sec in enumerate(sections):
            sec = sec.strip()
            if not sec:
                continue
            first_line = sec.splitlines()[0] if sec.splitlines() else ''
            topic = first_line.replace('#', '').strip()
            
            chunks.append({
                'chunk_id': f'{filename}_{idx}',
                'source': filename,
                'document_type': doc_type,
                'topic': topic,
                'content': sec,
                'tokens': self._tokenize(sec)
            })
        return chunks

    def ingest(self):
        self.store_dir.mkdir(parents=True, exist_ok=True)
        all_chunks = []
        if self.docs_dir.exists():
            for file_path in self.docs_dir.glob('*.md'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                chunks = self.chunk_document(file_path.name, content)
                all_chunks.extend(chunks)

        self.chunks = all_chunks
        with open(self.store_file, 'w', encoding='utf-8') as f:
            json.dump(self.chunks, f, indent=2)
        print(f'RAG Ingestion complete: {len(self.chunks)} chunks stored in {self.store_file}')

    def search(self, query: str, top_k: int = 4, filter_doc_type: Optional[str] = None) -> List[Dict[str, Any]]:
        if not self.chunks:
            self._load_store()

        query_tokens = set(self._tokenize(query))
        if not query_tokens:
            return self.chunks[:top_k]

        scored_chunks = []
        for chunk in self.chunks:
            if filter_doc_type and chunk.get('document_type') != filter_doc_type:
                continue

            chunk_tokens = chunk.get('tokens', [])
            if not chunk_tokens:
                continue

            # TF-IDF / BM25 style relevance scoring
            overlap = 0
            for qt in query_tokens:
                count = chunk_tokens.count(qt)
                if count > 0:
                    # boost exact keyword matches
                    overlap += (1 + math.log(count)) * (1.5 if qt in chunk.get('topic', '').lower() else 1.0)

            score = overlap / (math.sqrt(len(chunk_tokens)) + 1.0)
            if score > 0:
                scored_chunks.append((score, chunk))

        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        top_results = [item[1] for item in scored_chunks[:top_k]]
        
        # Fallback if no specific overlap
        if not top_results and self.chunks:
            filtered = [c for c in self.chunks if (not filter_doc_type or c.get('document_type') == filter_doc_type)]
            top_results = filtered[:top_k] if filtered else self.chunks[:top_k]

        return top_results

    def format_context_for_prompt(self, chunks: List[Dict[str, Any]]) -> str:
        if not chunks:
            return 'No specific grounding context found in the knowledge repository.'
        formatted = []
        for idx, c in enumerate(chunks, start=1):
            source = c.get('source', 'Unknown')
            topic = c.get('topic', '')
            content = c.get('content', '').strip()
            formatted.append(f'--- [Source {idx}: {source} | Topic: {topic}] ---\n{content}')
        return '\n\n'.join(formatted)

rag_service = RAGService()
