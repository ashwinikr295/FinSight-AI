from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from rag.rag_pipeline import process_rag_query

router = APIRouter()

class ChatRequest(BaseModel):
    query: str
    company_name: Optional[str] = None

@router.post("/chat")
def chat_endpoint(req: ChatRequest):
    if not req.query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    
    try:
        res = process_rag_query(req.query, company_name=req.company_name)
        return res
    except Exception as e:
        print(f"Chat RAG error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
