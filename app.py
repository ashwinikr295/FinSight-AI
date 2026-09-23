import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

from database.postgres_sql import create_database
from database.create_table import create_tables
from database.metrics import get_metrics, get_document_list
from seed_sample_data import seed_sample_data_if_empty
from routes.ingestion import router as ingestion_router
from routes.chat import router as chat_router
from routes.dashboard import router as dashboard_router
from routes.health import router as health_router

load_dotenv()

app = FastAPI(
    title="FinSight AI - Investor Intelligence Platform",
    description="RAG-enabled Financial Document Intelligence Platform with KPI extraction, Executive Dashboards, and Interactive AI Assistant.",
    version="2.0.0"
)

@app.on_event("startup")
def startup_event():
    """
    Initialize database, tables, vector store, and pre-seeded sample financial data.
    """
    create_database()
    create_tables()
    try:
        seed_sample_data_if_empty()
    except Exception as e:
        print(f"Sample data seed warning: {e}")

# Mount static and template files
BASE_PATH = Path(__file__).resolve().parent
static_dir = BASE_PATH / "static"
templates_dir = BASE_PATH / "templates"
os.makedirs(static_dir, exist_ok=True)
os.makedirs(templates_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
templates = Jinja2Templates(directory=str(templates_dir))


# Include Routers
app.include_router(ingestion_router, prefix="/api", tags=["Ingestion"])
app.include_router(chat_router, prefix="/api", tags=["Chat"])
app.include_router(dashboard_router, prefix="/api", tags=["Dashboard"])
app.include_router(health_router, tags=["Health"])

@app.get("/")
def dashboard(request: Request):
    """
    Render main FinSight AI Investor Intelligence Platform dashboard UI.
    """
    metrics_data = get_metrics()
    doc_list = get_document_list()
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        context={
            "metrics": metrics_data,
            "documents": doc_list,
            "total_companies": len(set(m["company_name"] for m in metrics_data)),
            "total_reports": len(metrics_data)
        }
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)