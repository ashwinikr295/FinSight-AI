import json
from database.postgres_sql import get_connection

def get_metrics():
    """
    Fetches all extracted financial metrics and insights for the dashboard.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT doc_id, company_name, fiscal_year, revenue, net_income, 
               operating_income, cash_flow_operating, total_assets, total_liabilities,
               risk_factors, growth_drivers, executive_summary, created_at
        FROM kpi_metrics
        ORDER BY company_name ASC, fiscal_year DESC;
    """)
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for r in rows:
        results.append({
            "doc_id": str(r["doc_id"] or ""),
            "company_name": str(r["company_name"] or ""),
            "fiscal_year": r["fiscal_year"] or 2024,
            "revenue": str(r["revenue"] or "N/A"),
            "net_income": str(r["net_income"] or "N/A"),
            "operating_income": str(r["operating_income"] or "N/A"),
            "cash_flow_operating": str(r["cash_flow_operating"] or "N/A"),
            "total_assets": str(r["total_assets"] or "N/A"),
            "total_liabilities": str(r["total_liabilities"] or "N/A"),
            "risk_factors": json.loads(r["risk_factors"]) if r["risk_factors"] else [],
            "growth_drivers": json.loads(r["growth_drivers"]) if r["growth_drivers"] else [],
            "executive_summary": str(r["executive_summary"] or ""),
            "created_at": str(r["created_at"] or "")
        })
    return results

def get_document_list():
    """
    Fetches metadata of all uploaded documents safely.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, company_name, fiscal_year, filename, uploaded_at FROM documents ORDER BY uploaded_at DESC;")
    rows = cursor.fetchall()
    conn.close()
    
    docs = []
    for r in rows:
        uploaded_str = str(r["uploaded_at"] or "")
        docs.append({
            "id": str(r["id"] or ""),
            "company_name": str(r["company_name"] or ""),
            "fiscal_year": r["fiscal_year"] or 2024,
            "filename": str(r["filename"] or ""),
            "uploaded_at": uploaded_str[:10] if len(uploaded_str) >= 10 else "Recently"
        })
    return docs

def delete_document_record(doc_id: str):
    """
    Deletes document record and associated KPIs from database.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM kpi_metrics WHERE doc_id = ?;", (doc_id,))
    cursor.execute("DELETE FROM documents WHERE id = ?;", (doc_id,))
    conn.commit()
    conn.close()
    print(f"Deleted document {doc_id} from database.")