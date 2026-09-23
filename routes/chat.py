import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from rag.rag_pipeline import process_rag_query, process_rag_query_stream

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


@router.post("/chat/stream")
def chat_stream_endpoint(req: ChatRequest):
    if not req.query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    def sse_event_generator():
        try:
            for event in process_rag_query_stream(req.query, company_name=req.company_name):
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:
            print(f"Chat stream error: {e}")
            err_payload = {"type": "error", "content": str(e)}
            yield f"data: {json.dumps(err_payload)}\n\n"

    return StreamingResponse(sse_event_generator(), media_type="text/event-stream")

