"""
Advanced Analytics API Router for BookSmart AI
API endpoints for revenue dashboard, staff performance, and AI insights
"""
from fastapi import APIRouter
from datetime import datetime, timedelta
from typing import Optional
from analytics_dashboard import analytics_dashboard, get_revenue_dashboard, get_staff_analytics, get_business_summary
from ai_recommendations import ai_recommendations, get_personalized_recommendations, predict_customer_next_booking, get_churn_risk_customers

router = APIRouter(prefix="/advanced-analytics", tags=["Advanced Analytics"])

@router.get("/dashboard")
async def get_dashboard():
    """Get complete business dashboard summary"""
    return await get_business_summary()

@router.get("/revenue")
async def get_revenue(
    days: int = 30,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """Get revenue analytics for date range"""
    if not start_date:
        start_date = datetime.now() - timedelta(days=days)
    if not end_date:
        end_date = datetime.now()
    
    return await get_revenue_dashboard(start_date, end_date)

@router.get("/staff-performance")
async def get_staff_performance(staff_id: Optional[str] = None):
    """Get staff performance analytics"""
    return await get_staff_analytics(staff_id)

@router.get("/customers")
async def get_customer_analytics():
    """Get customer behavior analytics"""
    return analytics_dashboard.get_customer_analytics()

@router.get("/services/popularity")
async def get_service_popularity():
    """Get service booking analytics"""
    return analytics_dashboard.get_service_popularity()

@router.get("/demand-forecast")
async def get_demand_forecast(days_ahead: int = 7):
    """Predict upcoming demand"""
    return analytics_dashboard.predict_demand(days_ahead)

@router.get("/recommendations/{customer_id}")
async def get_recommendations(customer_id: str, context: Optional[str] = None):
    """Get personalized service recommendations for customer"""
    recommendations = await get_personalized_recommendations(customer_id, context)
    return {
        "customer_id": customer_id,
        "recommendations": [
            {
                "service_id": r.service_id,
                "service_name": r.service_name,
                "confidence": r.confidence_score,
                "reason": r.reason,
                "price": r.estimated_price,
                "duration": r.estimated_duration
            }
            for r in recommendations
        ]
    }

@router.get("/predict-next-booking/{customer_id}")
async def predict_next_booking(customer_id: str):
    """Predict when customer is likely to book next"""
    return await predict_customer_next_booking(customer_id)

@router.get("/churn-risk")
async def get_churn_risk():
    """Get list of customers at churn risk"""
    at_risk = await get_churn_risk_customers()
    return {
        "at_risk_customers": at_risk,
        "total_at_risk": len(at_risk)
    }

@router.get("/today")
async def get_today_stats():
    """Get today's business stats"""
    dashboard = await get_business_summary()
    return dashboard.get("today", {})

@router.get("/this-week")
async def get_week_stats():
    """Get this week's business stats"""
    dashboard = await get_business_summary()
    return dashboard.get("this_week", {})
