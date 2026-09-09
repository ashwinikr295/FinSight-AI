from fastapi import APIRouter
from database.metrics import get_metrics, get_document_list

router = APIRouter()

@router.get("/metrics")
def get_dashboard_metrics():
    return get_metrics()

@router.get("/insights")
def get_insights():
    metrics = get_metrics()
    insights_list = []
    for m in metrics:
        insights_list.append({
            "company_name": m["company_name"],
            "fiscal_year": m["fiscal_year"],
            "risk_factors": m["risk_factors"],
            "growth_drivers": m["growth_drivers"],
            "executive_summary": m["executive_summary"]
        })
    return insights_list