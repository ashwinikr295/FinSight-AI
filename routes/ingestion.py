import os
import shutil
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from config.settings import RAW_PDF_DIR
from ingestion.ingest_documents import process_and_ingest_document
from database.metrics import get_document_list, delete_document_record
from vectorstore.vector_store import get_vector_store

router = APIRouter()

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    company_name: str = Form(...),
    fiscal_year: int = Form(...)
):
    try:
        os.makedirs(RAW_PDF_DIR, exist_ok=True)
        file_path = os.path.join(RAW_PDF_DIR, file.filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        res = process_and_ingest_document(file_path, company_name, fiscal_year)
        return res
    except Exception as e:
        print(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents")
def list_documents():
    return get_document_list()

@router.delete("/documents/{doc_id}")
def delete_document(doc_id: str):
    try:
        # Delete from database
        delete_document_record(doc_id)
        # Delete from vector store
        vs = get_vector_store()
        vs.delete_chunks(doc_id)
        return {"status": "success", "message": f"Document {doc_id} deleted successfully."}
    except Exception as e:
        print(f"Delete error: {e}")
        raise HTTPException(status_code=500, detail=str(e))