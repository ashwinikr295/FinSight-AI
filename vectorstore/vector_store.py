import os
import json
import math
from typing import List, Dict
from pathlib import Path
from config.settings import DATA_DIR

INDEX_FILE = DATA_DIR / "vector_index.json"

class LocalVectorStore:
    def __init__(self):
        self.chunks = []
        self.load_index()
        
    def load_index(self):
        if INDEX_FILE.exists():
            try:
                with open(INDEX_FILE, 'r', encoding='utf-8') as f:
                    self.chunks = json.load(f)
            except Exception as e:
                print(f"Index load warning: {e}")
                self.chunks = []

    def save_index(self):
        with open(INDEX_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.chunks, f, indent=2)

    def add_chunks(self, chunks: List[Dict]):
        # Deduplicate chunks by chunk_id
        existing_ids = {c["chunk_id"] for c in self.chunks}
        new_chunks = [c for c in chunks if c["chunk_id"] not in existing_ids]
        self.chunks.extend(new_chunks)
        self.save_index()
        print(f"Added {len(new_chunks)} chunks to vector index. Total: {len(self.chunks)}")

    def delete_chunks(self, doc_id: str):
        original_count = len(self.chunks)
        self.chunks = [c for c in self.chunks if c.get("doc_id") != doc_id]
        self.save_index()
        print(f"Removed {original_count - len(self.chunks)} chunks for doc {doc_id}.")

    def _tokenize(self, text: str) -> List[str]:
        import re
        return re.findall(r'\w+', text.lower())

    def search(self, query: str, company_name: str = None, top_k: int = 4) -> List[Dict]:
        query_tokens = set(self._tokenize(query))
        results = []

        for chunk in self.chunks:
            if company_name and chunk.get("company_name", "").lower() != company_name.lower():
                continue

            content = chunk.get("content", "")
            content_tokens = self._tokenize(content)
            
            if not content_tokens:
                continue

            token_count = len(content_tokens)
            matches = sum(1 for t in query_tokens if t in content_tokens)
            
            score = matches / (math.log(token_count) + 1.0)
            
            if any(term in content.lower() for term in ["revenue", "net income", "operating income", "cash flow", "assets", "liabilities", "risk"]):
                score *= 1.25

            if score > 0.0:
                results.append({
                    "chunk": chunk,
                    "score": round(score, 4)
                })

        results.sort(key=lambda x: x["score"], reverse=True)
        return [r["chunk"] for r in results[:top_k]]

vector_store_instance = LocalVectorStore()

def get_vector_store():
    return vector_store_instance
