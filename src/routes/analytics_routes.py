# Analytics and Reporting Endpoints

from fastapi import APIRouter, Depends, Query
from typing import Optional
from src.analytics.metrics import analytics
from src.utils.auth import verify_token

router = APIRouter(prefix="/analytics", tags=["Analytics & Reporting"])

@router.get("/dashboard")
async def get_analytics_dashboard(current_user: str = Depends(verify_token)):
    """
    Get comprehensive analytics dashboard with key metrics.
    Includes claims, authorizations, scheme statistics, and trends.
    """
    return analytics.get_summary_dashboard()

@router.get("/schemes")
async def get_scheme_statistics(
    scheme_name: Optional[str] = Query(None, description="Specific scheme name"),
    current_user: str = Depends(verify_token)
):
    """Get statistics for medical schemes"""
    return {
        "scheme_statistics": analytics.get_scheme_statistics(scheme_name)
    }

@router.get("/procedures/top")
async def get_top_procedures(
    limit: int = Query(10, ge=1, le=100, description="Number of top procedures"),
    current_user: str = Depends(verify_token)
):
    """Get most frequently used procedures"""
    return {
        "top_procedures": analytics.get_top_procedures(limit)
    }

@router.get("/trends/daily")
async def get_daily_trends(
    days: int = Query(30, ge=1, le=365, description="Number of days"),
    current_user: str = Depends(verify_token)
):
    """Get daily operational trends"""
    return {
        "period_days": days,
        "trends": analytics.get_daily_trends(days)
    }

@router.get("/approval-rates")
async def get_approval_rates(current_user: str = Depends(verify_token)):
    """Get approval rates for claims and authorizations"""
    return analytics.get_approval_rates()

@router.get("/health-metrics")
async def get_population_health_metrics(current_user: str = Depends(verify_token)):
    """
    Get population health metrics.
    Useful for identifying trends and resource utilization.
    """
    dashboard = analytics.get_summary_dashboard()
    
    return {
        "population_metrics": {
            "total_patients_served": len(set(
                c.get("patient_id") for c in analytics.metrics["claims"] 
                if c.get("patient_id")
            )),
            "total_procedures": sum(analytics.metrics["procedures"].values()),
            "unique_procedure_types": len(analytics.metrics["procedures"]),
            "average_claim_amount": (
                sum(c["amount"] for c in analytics.metrics["claims"]) / 
                len(analytics.metrics["claims"])
            ) if analytics.metrics["claims"] else 0
        },
        "resource_utilization": {
            "top_procedures": dashboard["top_procedures"][:5],
            "scheme_distribution": dashboard["scheme_statistics"]
        }
    }
