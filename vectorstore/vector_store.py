import os
import json
import math
import hashlib
from typing import List, Dict
from pathlib import Path
from config.settings import DATA_DIR, PINECONE_API_KEY, PINECONE_INDEX_NAME

INDEX_FILE = DATA_DIR / "vector_index.json"

def compute_text_embedding(text: str, dim: int = 384) -> List[float]:
    """
    Computes a normalized 384-dimensional dense float vector for text.
    """
    words = text.lower().split()
    vec = [0.0] * dim
    for word in words:
        h = int(hashlib.md5(word.encode('utf-8')).hexdigest(), 16)
        idx = h % dim
        val = 1.0 + (h % 7) * 0.1
        vec[idx] += val
    
    norm = math.sqrt(sum(x * x for x in vec))
    if norm > 0:
        vec = [x / norm for x in vec]
    return vec

class HybridPineconeVectorStore:
    def __init__(self):
        self.chunks = []
        self.pinecone_index = None
        self.load_local_index()
        self.init_pinecone()
        
    def init_pinecone(self):
        if PINECONE_API_KEY:
            try:
                from pinecone import Pinecone, ServerlessSpec
                pc = Pinecone(api_key=PINECONE_API_KEY)
                idx_name = PINECONE_INDEX_NAME or "finsight-index"
                
                existing_indexes = [idx.name for idx in pc.list_indexes()]
                if idx_name not in existing_indexes:
                    try:
                        pc.create_index(
                            name=idx_name,
                            dimension=384,
                            metric="cosine",
                            spec=ServerlessSpec(cloud="aws", region="us-east-1")
                        )
                    except Exception as create_err:
                        print(f"Pinecone create_index notice: {create_err}")
                
                self.pinecone_index = pc.Index(idx_name)
                print(f"Pinecone vector index '{idx_name}' initialized successfully.")
            except Exception as e:
                print(f"Pinecone initialization notice ({e}). Falling back to local vector store.")
                self.pinecone_index = None

    def load_local_index(self):
        if INDEX_FILE.exists():
            try:
                with open(INDEX_FILE, 'r', encoding='utf-8') as f:
                    self.chunks = json.load(f)
            except Exception as e:
                print(f"Index load warning: {e}")
                self.chunks = []

    def save_local_index(self):
        with open(INDEX_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.chunks, f, indent=2)

    def add_chunks(self, chunks: List[Dict]):
        # Deduplicate chunks by chunk_id
        existing_ids = {c["chunk_id"] for c in self.chunks}
        new_chunks = [c for c in chunks if c["chunk_id"] not in existing_ids]
        self.chunks.extend(new_chunks)
        self.save_local_index()
        
        # Upsert to Pinecone Cloud Vector Store if available
        if self.pinecone_index and new_chunks:
            try:
                vectors_to_upsert = []
                for c in new_chunks:
                    content = c.get("content", "")
                    vec = compute_text_embedding(content)
                    vectors_to_upsert.append({
                        "id": c["chunk_id"],
                        "values": vec,
                        "metadata": {
                            "chunk_id": c.get("chunk_id", ""),
                            "doc_id": c.get("doc_id", ""),
                            "company_name": c.get("company_name", ""),
                            "fiscal_year": int(c.get("fiscal_year", 0)) if str(c.get("fiscal_year", "")).isdigit() else 0,
                            "section_title": c.get("section_title", ""),
                            "content": content
                        }
                    })
                self.pinecone_index.upsert(vectors=vectors_to_upsert)
                print(f"Successfully upserted {len(vectors_to_upsert)} vector embeddings to Pinecone.")
            except Exception as e:
                print(f"Pinecone vector upsert warning ({e}). Vector chunks saved locally.")

    def delete_chunks(self, doc_id: str):
        original_count = len(self.chunks)
        deleted_chunk_ids = [c["chunk_id"] for c in self.chunks if c.get("doc_id") == doc_id]
        self.chunks = [c for c in self.chunks if c.get("doc_id") != doc_id]
        self.save_local_index()

        if self.pinecone_index and deleted_chunk_ids:
            try:
                self.pinecone_index.delete(ids=deleted_chunk_ids)
                print(f"Deleted {len(deleted_chunk_ids)} chunks from Pinecone index.")
            except Exception as e:
                print(f"Pinecone delete warning ({e}).")

    def search(self, query: str, company_name: str = None, top_k: int = 4) -> List[Dict]:
        # 1. Try Pinecone vector search first
        if self.pinecone_index:
            try:
                query_vec = compute_text_embedding(query)
                filter_dict = {}
                if company_name:
                    filter_dict["company_name"] = {"$eq": company_name}

                res = self.pinecone_index.query(
                    vector=query_vec,
                    top_k=top_k,
                    filter=filter_dict if filter_dict else None,
                    include_metadata=True
                )
                matches = res.get("matches", [])
                if matches:
                    results = []
                    for m in matches:
                        meta = m.get("metadata", {})
                        results.append({
                            "chunk_id": meta.get("chunk_id", m.get("id")),
                            "doc_id": meta.get("doc_id", ""),
                            "company_name": meta.get("company_name", "Report"),
                            "fiscal_year": meta.get("fiscal_year", ""),
                            "section_title": meta.get("section_title", "Section"),
                            "content": meta.get("content", "")
                        })
                    return results
            except Exception as e:
                print(f"Pinecone vector search warning ({e}). Falling back to local store search.")

        # 2. Fallback to Local Vector Store
        return self._local_search(query, company_name=company_name, top_k=top_k)

    def _tokenize(self, text: str) -> List[str]:
        import re
        return re.findall(r'\w+', text.lower())

    def _local_search(self, query: str, company_name: str = None, top_k: int = 4) -> List[Dict]:
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

vector_store_instance = HybridPineconeVectorStore()

def get_vector_store():
    return vector_store_instance

