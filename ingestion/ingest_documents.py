import os
import uuid
from pathlib import Path

from config.settings import RAW_PDF_DIR
from ingestion.pdf_to_markdown import convert_pdf_to_markdown
from ingestion.semantic_chunker import create_semantic_chunks
from vectorstore.vector_store import get_vector_store
from rag.kpi_extractor_rag import extract_financial_kpis
from database.save_metrics import save_kpi_metrics, save_document_record

def process_and_ingest_document(file_path: str, company_name: str, fiscal_year: int) -> dict:
    """
    Executes end-to-end ingestion pipeline:
    PDF -> Markdown -> Semantic Chunking -> Vector Store -> 8-KPI Extractor -> Database Save.
    """
    filename = Path(file_path).name
    doc_id = f"doc_{uuid.uuid4().hex[:8]}"

    print(f"Starting ingestion for {company_name} ({fiscal_year}) - {filename}...")

    # 1. Convert PDF to Markdown
    markdown_path = convert_pdf_to_markdown(file_path, company_name, fiscal_year)
    
    with open(markdown_path, 'r', encoding='utf-8') as f:
        markdown_text = f.read()

    # 2. Save Document Metadata Record
    save_document_record(doc_id, company_name, fiscal_year, filename, markdown_path)

    # 3. Create Semantic Chunks
    chunks = create_semantic_chunks(markdown_text, company_name, fiscal_year, doc_id)

    # 4. Add Chunks to Vector Store
    vs = get_vector_store()
    vs.add_chunks(chunks)

    # 5. Extract 8 Financial KPIs and Business Insights
    kpis = extract_financial_kpis(markdown_text, company_name, fiscal_year)

    # 6. Save KPIs into Database
    save_kpi_metrics(doc_id, company_name, fiscal_year, kpis)

    print(f"Successfully processed and ingested {company_name} ({fiscal_year})!")

    return {
        "status": "success",
        "doc_id": doc_id,
        "company_name": company_name,
        "fiscal_year": fiscal_year,
        "filename": filename,
        "chunks_created": len(chunks),
        "kpis_extracted": kpis
    }