"""
Analytics Dashboard for BookSmart AI
Revenue tracking, staff performance, and business insights
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class AnalyticsDashboard:
    """Business Analytics and Reporting Dashboard"""
    
    def __init__(self):
        self.bookings_data = []
        self.revenue_data = []
    
    def calculate_revenue_metrics(self, start_date: datetime, end_date: datetime) -> Dict:
        """Calculate revenue metrics for date range"""
        
        # Mock data - in production, query database
        total_revenue = 0
        total_bookings = 0
        services_revenue = defaultdict(float)
        daily_revenue = defaultdict(float)
        
        # Calculate metrics
        metrics = {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "total_revenue": 125000,  # Mock: ₹1.25L
            "total_bookings": 85,
            "average_booking_value": 1470,  # ₹1,470 avg
            "comparison_last_period": {
                "revenue_change": 15.5,  # +15.5%
                "bookings_change": 8.2   # +8.2%
            },
            "revenue_by_service": {
                "Hair Styling": 35000,
                "Facial Treatment": 42000,
                "Manicure & Pedicure": 28000,
                "Hair Coloring": 20000
            },
            "revenue_by_staff": {
                "Priya Sharma": 45000,
                "Raj Kumar": 38000,
                "Anita Desai": 42000
            },
            "daily_trend": [
                {"date": "2026-04-10", "revenue": 18000, "bookings": 12},
                {"date": "2026-04-11", "revenue": 22000, "bookings": 15},
                {"date": "2026-04-12", "revenue": 15000, "bookings": 10},
                {"date": "2026-04-13", "revenue": 19000, "bookings": 13},
                {"date": "2026-04-14", "revenue": 25000, "bookings": 18},
                {"date": "2026-04-15", "revenue": 16000, "bookings": 11},
                {"date": "2026-04-16", "revenue": 15000, "bookings": 6}  # Today (partial)
            ],
            "peak_hours": [
                {"hour": "10:00", "bookings": 8},
                {"hour": "11:00", "bookings": 12},
                {"hour": "14:00", "bookings": 10},
                {"hour": "16:00", "bookings": 15},
                {"hour": "18:00", "bookings": 18}
            ]
        }
        
        return metrics
    
    def get_staff_performance(self, staff_id: str = None, period_days: int = 30) -> Dict:
        """Get staff performance analytics"""
        
        # Mock staff performance data
        all_staff = [
            {
                "staff_id": "1",
                "name": "Priya Sharma",
                "role": "Senior Stylist",
                "bookings": 45,
                "revenue": 45000,
                "rating": 4.8,
                "completion_rate": 98.5,
                "repeat_customers": 32,
                "top_services": ["Hair Styling", "Hair Coloring"],
                "avg_service_time": 45  # minutes
            },
            {
                "staff_id": "2",
                "name": "Raj Kumar",
                "role": "Color Specialist",
                "bookings": 38,
                "revenue": 38000,
                "rating": 4.6,
                "completion_rate": 96.0,
                "repeat_customers": 28,
                "top_services": ["Hair Coloring", "Highlights"],
                "avg_service_time": 60
            },
            {
                "staff_id": "3",
                "name": "Anita Desai",
                "role": "Beauty Expert",
                "bookings": 42,
                "revenue": 42000,
                "rating": 4.9,
                "completion_rate": 99.0,
                "repeat_customers": 35,
                "top_services": ["Facial", "Manicure"],
                "avg_service_time": 50
            }
        ]
        
        if staff_id:
            staff = next((s for s in all_staff if s["staff_id"] == staff_id), None)
            return staff or {}
        
        return {
            "staff_count": len(all_staff),
            "staff": all_staff,
            "top_performer": max(all_staff, key=lambda x: x["revenue"]),
            "total_staff_revenue": sum(s["revenue"] for s in all_staff),
            "avg_staff_rating": sum(s["rating"] for s in all_staff) / len(all_staff)
        }
    
    def get_customer_analytics(self) -> Dict:
        """Get customer behavior analytics"""
        
        return {
            "total_customers": 450,
            "new_customers_this_month": 28,
            "returning_customers": 322,
            "customer_retention_rate": 71.5,  # %
            "avg_visits_per_customer": 3.2,
            "top_customers": [
                {"name": "Neha Gupta", "visits": 12, "total_spend": 18000},
                {"name": "Rahul Mehta", "visits": 10, "total_spend": 15000},
                {"name": "Sonia Kapoor", "visits": 8, "total_spend": 12000}
            ],
            "customer_segments": {
                "vip": 45,      # High spenders
                "regular": 180, # Consistent visitors
                "occasional": 150, # Infrequent
                "at_risk": 75   # Haven't visited in 60+ days
            },
            "satisfaction_score": 4.7,  # Out of 5
            "nps_score": 72  # Net Promoter Score
        }
    
    def get_service_popularity(self) -> Dict:
        """Get service booking analytics"""
        
        services = [
            {
                "service_id": "1",
                "name": "Hair Styling",
                "category": "Hair",
                "total_bookings": 156,
                "revenue": 78000,
                "avg_rating": 4.7,
                "popularity_trend": "up",
                "peak_days": ["Saturday", "Sunday"],
                "avg_duration": 45
            },
            {
                "service_id": "2",
                "name": "Facial Treatment",
                "category": "Skin",
                "total_bookings": 134,
                "revenue": 67000,
                "avg_rating": 4.8,
                "popularity_trend": "stable",
                "peak_days": ["Friday", "Saturday"],
                "avg_duration": 60
            },
            {
                "service_id": "3",
                "name": "Manicure & Pedicure",
                "category": "Nails",
                "total_bookings": 98,
                "revenue": 34300,
                "avg_rating": 4.5,
                "popularity_trend": "up",
                "peak_days": ["Saturday", "Sunday"],
                "avg_duration": 50
            },
            {
                "service_id": "4",
                "name": "Hair Coloring",
                "category": "Hair",
                "total_bookings": 87,
                "revenue": 52200,
                "avg_rating": 4.6,
                "popularity_trend": "down",
                "peak_days": ["Thursday", "Friday"],
                "avg_duration": 90
            }
        ]
        
        return {
            "services": services,
            "most_popular": max(services, key=lambda x: x["total_bookings"]),
            "highest_rated": max(services, key=lambda x: x["avg_rating"]),
            "trending_up": [s for s in services if s["popularity_trend"] == "up"],
            "categories": {
                "Hair": {"bookings": 243, "revenue": 130200},
                "Skin": {"bookings": 134, "revenue": 67000},
                "Nails": {"bookings": 98, "revenue": 34300}
            }
        }
    
    def predict_demand(self, days_ahead: int = 7) -> Dict:
        """Predict upcoming demand based on historical data"""
        
        today = datetime.now()
        predictions = []
        
        for i in range(days_ahead):
            date = today + timedelta(days=i)
            is_weekend = date.weekday() >= 5
            
            # Mock prediction logic
            predicted_bookings = 18 if is_weekend else 12
            predicted_revenue = 25000 if is_weekend else 16000
            
            predictions.append({
                "date": date.strftime("%Y-%m-%d"),
                "day": date.strftime("%A"),
                "is_weekend": is_weekend,
                "predicted_bookings": predicted_bookings,
                "predicted_revenue": predicted_revenue,
                "confidence": 0.85,
                "peak_hours": ["11:00", "14:00", "16:00", "18:00"]
            })
        
        return {
            "predictions": predictions,
            "total_predicted_bookings": sum(p["predicted_bookings"] for p in predictions),
            "total_predicted_revenue": sum(p["predicted_revenue"] for p in predictions),
            "recommended_staffing": {
                "weekdays": 2,
                "weekends": 3
            }
        }
    
    def get_dashboard_summary(self) -> Dict:
        """Get complete dashboard summary"""
        
        today = datetime.now()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        return {
            "today": {
                "bookings": 6,
                "revenue": 8500,
                "upcoming_appointments": 4
            },
            "this_week": self.calculate_revenue_metrics(week_ago, today),
            "this_month": {
                "total_revenue": 485000,
                "total_bookings": 320,
                "new_customers": 28,
                "vs_last_month": {
                    "revenue_change": 12.5,
                    "bookings_change": 8.3
                }
            },
            "staff_performance": self.get_staff_performance(),
            "customer_analytics": self.get_customer_analytics(),
            "service_popularity": self.get_service_popularity(),
            "demand_forecast": self.predict_demand()
        }

# Initialize analytics dashboard
analytics_dashboard = AnalyticsDashboard()

# Convenience functions
async def get_revenue_dashboard(start_date: datetime = None, end_date: datetime = None):
    """Get revenue analytics dashboard"""
    if not start_date:
        start_date = datetime.now() - timedelta(days=30)
    if not end_date:
        end_date = datetime.now()
    return analytics_dashboard.calculate_revenue_metrics(start_date, end_date)

async def get_staff_analytics(staff_id: str = None):
    """Get staff performance analytics"""
    return analytics_dashboard.get_staff_performance(staff_id)

async def get_business_summary():
    """Get complete business dashboard summary"""
    return analytics_dashboard.get_dashboard_summary()
