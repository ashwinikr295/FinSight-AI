import os
from database.create_table import create_tables
from database.save_metrics import save_kpi_metrics, save_document_record
from vectorstore.vector_store import get_vector_store
from ingestion.pdf_to_markdown import convert_pdf_to_markdown
from ingestion.semantic_chunker import create_semantic_chunks
from config.settings import RAW_PDF_DIR

SAMPLE_REPORTS = [
    {
        "doc_id": "doc_tesla_2024",
        "company_name": "Tesla, Inc.",
        "fiscal_year": 2024,
        "filename": "Tesla_2024_10K.pdf",
        "content": """# Annual Report 2024 - Tesla, Inc.
**Company**: Tesla, Inc.
**Fiscal Year**: 2024

## 1. Executive Financial Highlights
Tesla, Inc. announced its financial results for fiscal year 2024. Total revenue reached $96,773,000,000, driven by expanded vehicle deliveries, energy storage deployment growth, and increased services revenue. Net income for the year was $14,997,000,000, while operating income reached $8,891,000,000. Cash flow from operating activities was robust at $13,256,000,000. The balance sheet remains strong with Total Assets of $106,618,000,000 against Total Liabilities of $43,009,000,000.

## 2. Revenue & Profitability Analysis
Why did revenue increase in 2024? Revenue growth in 2024 was primarily driven by a 24% year-over-year increase in Megapack and Energy Storage business revenue, higher vehicle deliveries across Model Y and Model 3 worldwide, and expanding Full Self-Driving (FSD) subscription revenue streams. Operating cash flow improved due to operational efficiencies and disciplined cost control across Gigafactories in Shanghai, Austin, and Berlin.

## 3. Key Risk Factors
- Global EV price competition and automotive margin compression.
- Supply chain disruptions for critical battery raw materials like lithium and nickel.
- Regulatory changes governing autonomous driving technology across key export markets.
- Foreign exchange volatility affecting international sales conversion.

## 4. Key Growth Drivers
- Rapid scaling of Energy Storage deployment (Megapack and Powerwall installations).
- Continuous improvement in Full Self-Driving (FSD) v12 neural network capabilities and licensing opportunities.
- Production ramps for Next-Generation low-cost vehicle platform.
- Expansion of Supercharger network licensing and non-Tesla charging revenue.
""",
        "kpis": {
            "revenue": "$96,773,000,000",
            "net_income": "$14,997,000,000",
            "operating_income": "$8,891,000,000",
            "cash_flow_operating": "$13,256,000,000",
            "total_assets": "$106,618,000,000",
            "total_liabilities": "$43,009,000,000",
            "risk_factors": [
                "Global EV price competition and automotive margin compression.",
                "Supply chain disruptions for critical battery raw materials like lithium and nickel.",
                "Regulatory changes governing autonomous driving technology across key export markets.",
                "Foreign exchange volatility affecting international sales conversion."
            ],
            "growth_drivers": [
                "Rapid scaling of Energy Storage deployment (Megapack and Powerwall installations).",
                "Continuous improvement in Full Self-Driving (FSD) v12 neural network capabilities.",
                "Production ramps for Next-Generation low-cost vehicle platform.",
                "Expansion of Supercharger network licensing and non-Tesla charging revenue."
            ],
            "executive_summary": "Tesla recorded $96.77B in total revenue and $14.99B in net income for FY2024, supported by $13.25B in operating cash flow and rapid expansion in Energy Storage deployment."
        }
    },
    {
        "doc_id": "doc_apple_2024",
        "company_name": "Apple Inc.",
        "fiscal_year": 2024,
        "filename": "Apple_2024_10K.pdf",
        "content": """# Annual Report 2024 - Apple Inc.
**Company**: Apple Inc.
**Fiscal Year**: 2024

## 1. Executive Financial Summary
Apple Inc. reported total revenue of $391,035,000,000 for fiscal year 2024. Net income reached $93,736,000,000 with Operating Income of $123,216,000,000. Cash Flow from Operating Activities totaled $108,812,000,000. Total Assets stood at $364,980,000,000 while Total Liabilities were $308,030,000,000.

## 2. Revenue Performance & Growth
Why did revenue increase in 2024? Apple's revenue growth was propelled by record Services segment revenue (App Store, Apple Music, iCloud, Apple Pay), along with strong demand for iPhone 16 Pro models equipped with Apple Intelligence AI features. International sales accounted for over 58% of total net revenue.

## 3. Major Business Risks
- Geopolitical tensions affecting semiconductor and component manufacturing in East Asia.
- Increasing antitrust scrutiny on App Store commission rates and digital services regulation in the EU.
- Currency exchange rate fluctuations across European and Asian markets.

## 4. Primary Growth Opportunities
- Integration of Apple Intelligence generative AI features across iPhone, iPad, and Mac ecosystems.
- High-margin Services expansion surpassing $100 billion annual run-rate.
- Penetration in rapidly growing emerging markets including India and Southeast Asia.
""",
        "kpis": {
            "revenue": "$391,035,000,000",
            "net_income": "$93,736,000,000",
            "operating_income": "$123,216,000,000",
            "cash_flow_operating": "$108,812,000,000",
            "total_assets": "$364,980,000,000",
            "total_liabilities": "$308,030,000,000",
            "risk_factors": [
                "Geopolitical tensions affecting semiconductor and component manufacturing in East Asia.",
                "Increasing antitrust scrutiny on App Store commission rates and digital services regulation in the EU.",
                "Currency exchange rate fluctuations across European and Asian markets."
            ],
            "growth_drivers": [
                "Integration of Apple Intelligence generative AI features across iPhone, iPad, and Mac ecosystems.",
                "High-margin Services expansion surpassing $100 billion annual run-rate.",
                "Penetration in rapidly growing emerging markets including India and Southeast Asia."
            ],
            "executive_summary": "Apple Inc. achieved $391.03B in net revenue and $93.73B in net income in FY2024, driven by all-time high Services revenue and strong balance sheet cash flow generation."
        }
    }
]

def seed_sample_data_if_empty():
    create_tables()
    vs = get_vector_store()
    
    for item in SAMPLE_REPORTS:
        doc_id = item["doc_id"]
        c_name = item["company_name"]
        f_year = item["fiscal_year"]
        fname = item["filename"]
        content = item["content"]
        
        # Save sample file into raw_pdfs
        pdf_mock_path = os.path.join(RAW_PDF_DIR, fname)
        if not os.path.exists(pdf_mock_path):
            with open(pdf_mock_path, "w", encoding="utf-8") as f:
                f.write(content)
                
        # Save Document Record
        save_document_record(doc_id, c_name, f_year, fname, pdf_mock_path)
        
        # Save KPIs into DB
        save_kpi_metrics(doc_id, c_name, f_year, item["kpis"])
        
        # Create & Store Semantic Chunks
        chunks = create_semantic_chunks(content, c_name, f_year, doc_id)
        vs.add_chunks(chunks)

    print("Sample financial data seeded successfully.")

if __name__ == "__main__":
    seed_sample_data_if_empty()
