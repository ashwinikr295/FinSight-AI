import json
from database.postgres_sql import get_connection

def save_kpi_metrics(doc_id: str, company_name: str, fiscal_year: int, kpis: dict):
    """
    Saves extracted 8 financial KPIs and insights into the database.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    risk_factors_json = json.dumps(kpis.get("risk_factors", []))
    growth_drivers_json = json.dumps(kpis.get("growth_drivers", []))
    
    cursor.execute("""
        INSERT INTO kpi_metrics (
            doc_id, company_name, fiscal_year, revenue, net_income, 
            operating_income, cash_flow_operating, total_assets, total_liabilities,
            risk_factors, growth_drivers, executive_summary
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(doc_id) DO UPDATE SET
            company_name=excluded.company_name,
            fiscal_year=excluded.fiscal_year,
            revenue=excluded.revenue,
            net_income=excluded.net_income,
            operating_income=excluded.operating_income,
            cash_flow_operating=excluded.cash_flow_operating,
            total_assets=excluded.total_assets,
            total_liabilities=excluded.total_liabilities,
            risk_factors=excluded.risk_factors,
            growth_drivers=excluded.growth_drivers,
            executive_summary=excluded.executive_summary;
    """, (
        doc_id,
        company_name,
        fiscal_year,
        str(kpis.get("revenue", "N/A")),
        str(kpis.get("net_income", "N/A")),
        str(kpis.get("operating_income", "N/A")),
        str(kpis.get("cash_flow_operating", "N/A")),
        str(kpis.get("total_assets", "N/A")),
        str(kpis.get("total_liabilities", "N/A")),
        risk_factors_json,
        growth_drivers_json,
        str(kpis.get("executive_summary", ""))
    ))
    
    conn.commit()
    conn.close()
    print(f"Saved KPIs for {company_name} ({fiscal_year}) successfully.")

def save_document_record(doc_id: str, company_name: str, fiscal_year: int, filename: str, markdown_path: str):
    """
    Saves document metadata record.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO documents (id, company_name, fiscal_year, filename, markdown_path)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            company_name=excluded.company_name,
            fiscal_year=excluded.fiscal_year,
            filename=excluded.filename,
            markdown_path=excluded.markdown_path;
    """, (doc_id, company_name, fiscal_year, filename, markdown_path))
    conn.commit()
    conn.close()