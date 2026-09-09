from database.postgres_sql import get_connection

def create_tables():
    """
    Creates necessary tables for documents, KPI metrics, and business insights.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Documents table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            company_name TEXT NOT NULL,
            fiscal_year INTEGER NOT NULL,
            filename TEXT NOT NULL,
            markdown_path TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Financial KPI Metrics & Business Insights table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kpi_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_id TEXT UNIQUE,
            company_name TEXT NOT NULL,
            fiscal_year INTEGER NOT NULL,
            revenue TEXT,
            net_income TEXT,
            operating_income TEXT,
            cash_flow_operating TEXT,
            total_assets TEXT,
            total_liabilities TEXT,
            risk_factors TEXT,
            growth_drivers TEXT,
            executive_summary TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (doc_id) REFERENCES documents(id)
        );
    """)
    
    conn.commit()
    conn.close()
    print("Database tables created/verified successfully.")