"""
AI Style Recommendations for BookSmart AI
Personalized service recommendations based on customer history and preferences
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class CustomerPreference(BaseModel):
    customer_id: str
    preferred_services: List[str] = []
    preferred_staff: List[str] = []
    preferred_time_slots: List[str] = []  # e.g., "morning", "evening"
    preferred_days: List[str] = []  # e.g., "weekend", "weekday"
    budget_range: Dict[str, float] = {"min": 0, "max": 10000}
    style_preferences: List[str] = []  # e.g., "classic", "modern", "natural"
    product_preferences: List[str] = []
    last_updated: datetime = None

class StyleRecommendation(BaseModel):
    service_id: str
    service_name: str
    confidence_score: float  # 0-1
    reason: str
    estimated_price: float
    estimated_duration: int  # minutes
    staff_suggestion: Optional[str] = None
    complementary_services: List[str] = []

class AIRecommendationService:
    """AI-Powered Style Recommendation Service"""
    
    def __init__(self):
        self.customer_preferences: Dict[str, CustomerPreference] = {}
        self.service_categories = {
            "hair": ["Hair Styling", "Hair Coloring", "Hair Treatment", "Haircut"],
            "skin": ["Facial", "Skin Treatment", "Cleanup"],
            "nails": ["Manicure", "Pedicure", "Nail Art"],
            "spa": ["Massage", "Body Spa", "Aromatherapy"]
        }
    
    def update_customer_preferences(self, customer_id: str, booking_history: List[Dict], **preferences):
        """Update customer preferences from booking history"""
        
        # Extract preferences from history
        preferred_services = []
        preferred_staff = []
        time_slots = []
        days = []
        
        for booking in booking_history:
            if booking.get("service_name"):
                preferred_services.append(booking["service_name"])
            if booking.get("staff_name"):
                preferred_staff.append(booking["staff_name"])
            if booking.get("time_slot"):
                hour = int(booking["time_slot"].split(":")[0])
                if 6 <= hour < 12:
                    time_slots.append("morning")
                elif 12 <= hour < 17:
                    time_slots.append("afternoon")
                else:
                    time_slots.append("evening")
            if booking.get("date"):
                day = datetime.fromisoformat(booking["date"]).weekday()
                days.append("weekend" if day >= 5 else "weekday")
        
        # Count frequency
        from collections import Counter
        
        pref = CustomerPreference(
            customer_id=customer_id,
            preferred_services=list(dict.fromkeys(preferred_services))[:5],  # Top 5, preserve order
            preferred_staff=list(dict.fromkeys(preferred_staff))[:3],
            preferred_time_slots=list(dict.fromkeys(time_slots)),
            preferred_days=list(dict.fromkeys(days)),
            style_preferences=preferences.get("style_preferences", []),
            product_preferences=preferences.get("product_preferences", []),
            last_updated=datetime.now()
        )
        
        self.customer_preferences[customer_id] = pref
        
        logger.info(f"[AI Rec] Updated preferences for customer {customer_id}")
        
        return pref
    
    def get_recommendations(self, customer_id: str, context: str = None, 
                           available_services: List[Dict] = None) -> List[StyleRecommendation]:
        """Get personalized service recommendations"""
        
        pref = self.customer_preferences.get(customer_id)
        
        if not pref:
            # Return popular services as fallback
            return self._get_popular_recommendations(available_services)
        
        recommendations = []
        
        # 1. Based on preferred services (history-based)
        for service_name in pref.preferred_services[:3]:
            service = self._find_service(service_name, available_services)
            if service:
                recommendations.append(StyleRecommendation(
                    service_id=service.get("id", ""),
                    service_name=service["name"],
                    confidence_score=0.85,
                    reason=f"Based on your previous bookings",
                    estimated_price=service.get("price", 0),
                    estimated_duration=service.get("duration", 60),
                    staff_suggestion=pref.preferred_staff[0] if pref.preferred_staff else None
                ))
        
        # 2. Seasonal recommendations
        seasonal = self._get_seasonal_recommendations(available_services)
        recommendations.extend(seasonal)
        
        # 3. Trending services
        trending = self._get_trending_recommendations(available_services)
        recommendations.extend(trending)
        
        # 4. Complementary services
        if recommendations:
            complementary = self._get_complementary_services(recommendations[0], available_services)
            recommendations.extend(complementary)
        
        # Remove duplicates and sort by confidence
        seen = set()
        unique_recs = []
        for rec in recommendations:
            if rec.service_name not in seen:
                seen.add(rec.service_name)
                unique_recs.append(rec)
        
        unique_recs.sort(key=lambda x: x.confidence_score, reverse=True)
        
        return unique_recs[:5]  # Return top 5
    
    def _find_service(self, service_name: str, available_services: List[Dict]) -> Optional[Dict]:
        """Find service by name"""
        if not available_services:
            return {"name": service_name, "price": 1000, "duration": 60}
        
        for service in available_services:
            if service.get("name") == service_name:
                return service
        
        return None
    
    def _get_popular_recommendations(self, available_services: List[Dict]) -> List[StyleRecommendation]:
        """Get popular service recommendations"""
        popular_services = [
            {"name": "Hair Styling", "price": 800, "duration": 45},
            {"name": "Facial Treatment", "price": 1500, "duration": 60},
            {"name": "Hair Coloring", "price": 2000, "duration": 90}
        ]
        
        return [
            StyleRecommendation(
                service_id=str(i),
                service_name=s["name"],
                confidence_score=0.70,
                reason="Popular among our customers",
                estimated_price=s["price"],
                estimated_duration=s["duration"]
            )
            for i, s in enumerate(popular_services)
        ]
    
    def _get_seasonal_recommendations(self, available_services: List[Dict]) -> List[StyleRecommendation]:
        """Get season-based recommendations"""
        month = datetime.now().month
        
        # Summer months (March-June)
        if 3 <= month <= 6:
            seasonal_services = [
                {"name": "Summer Hair Care", "price": 1200, "duration": 60, "reason": "Perfect for summer"},
                {"name": "Cooling Facial", "price": 1000, "duration": 45, "reason": "Beat the heat"}
            ]
        # Winter months (November-February)
        elif month >= 11 or month <= 2:
            seasonal_services = [
                {"name": "Deep Conditioning", "price": 1500, "duration": 75, "reason": "Winter hair care"},
                {"name": "Hydrating Facial", "price": 1200, "duration": 60, "reason": "Combat winter dryness"}
            ]
        # Monsoon (July-October)
        else:
            seasonal_services = [
                {"name": "Anti-Frizz Treatment", "price": 1800, "duration": 60, "reason": "Monsoon essential"},
                {"name": "Skin Detox", "price": 2000, "duration": 90, "reason": "Post-monsoon care"}
            ]
        
        return [
            StyleRecommendation(
                service_id=str(i),
                service_name=s["name"],
                confidence_score=0.75,
                reason=s["reason"],
                estimated_price=s["price"],
                estimated_duration=s["duration"]
            )
            for i, s in enumerate(seasonal_services)
        ]
    
    def _get_trending_recommendations(self, available_services: List[Dict]) -> List[StyleRecommendation]:
        """Get trending service recommendations"""
        trending = [
            {"name": "Keratin Treatment", "price": 3500, "duration": 120, "reason": "Trending now"},
            {"name": "Hydra Facial", "price": 2500, "duration": 60, "reason": "Most booked this week"}
        ]
        
        return [
            StyleRecommendation(
                service_id=str(i),
                service_name=s["name"],
                confidence_score=0.80,
                reason=s["reason"],
                estimated_price=s["price"],
                estimated_duration=s["duration"]
            )
            for i, s in enumerate(trending)
        ]
    
    def _get_complementary_services(self, primary_rec: StyleRecommendation, 
                                    available_services: List[Dict]) -> List[StyleRecommendation]:
        """Get complementary services"""
        
        # Define service pairings
        pairings = {
            "Hair Styling": ["Hair Treatment", "Scalp Massage"],
            "Hair Coloring": ["Deep Conditioning", "Color Protection Treatment"],
            "Facial": ["Eye Treatment", "Neck & Decolletage"],
            "Manicure": ["Pedicure", "Hand Massage"]
        }
        
        complementary = []
        
        for primary, complements in pairings.items():
            if primary in primary_rec.service_name:
                for comp in complements:
                    complementary.append(StyleRecommendation(
                        service_id=str(hash(comp)),
                        service_name=comp,
                        confidence_score=0.65,
                        reason=f"Pairs well with {primary_rec.service_name}",
                        estimated_price=800,
                        estimated_duration=30
                    ))
        
        return complementary
    
    def predict_next_booking(self, customer_id: str) -> Dict:
        """Predict when customer is likely to book next"""
        pref = self.customer_preferences.get(customer_id)
        
        if not pref:
            return {
                "predicted_days": 30,
                "confidence": 0.5,
                "likely_services": ["General Service"],
                "suggested_time": "morning"
            }
        
        # Calculate average booking interval (mock calculation)
        avg_interval = 21  # days
        
        return {
            "predicted_days": avg_interval,
            "confidence": 0.72,
            "likely_services": pref.preferred_services[:3],
            "suggested_time": pref.preferred_time_slots[0] if pref.preferred_time_slots else "morning",
            "suggested_staff": pref.preferred_staff[0] if pref.preferred_staff else None
        }
    
    def get_churn_risk_customers(self) -> List[Dict]:
        """Identify customers at risk of churning"""
        at_risk = []
        
        for customer_id, pref in self.customer_preferences.items():
            # Customer hasn't booked in 60+ days
            if pref.last_updated and (datetime.now() - pref.last_updated).days > 60:
                at_risk.append({
                    "customer_id": customer_id,
                    "last_booking_days_ago": (datetime.now() - pref.last_updated).days,
                    "risk_level": "high" if (datetime.now() - pref.last_updated).days > 90 else "medium",
                    "suggested_action": "Send special offer or reminder"
                })
        
        return sorted(at_risk, key=lambda x: x["last_booking_days_ago"], reverse=True)
    
    def generate_personalized_offer(self, customer_id: str) -> Dict:
        """Generate personalized offer for customer"""
        pref = self.customer_preferences.get(customer_id)
        
        if not pref:
            return {
                "offer_title": "Welcome Back Special",
                "discount": 15,
                "applicable_services": ["All Services"],
                "valid_days": 7
            }
        
        # Based on preferred services
        preferred_service = pref.preferred_services[0] if pref.preferred_services else "All Services"
        
        return {
            "offer_title": f"Special on {preferred_service}",
            "discount": 20,
            "applicable_services": pref.preferred_services[:2],
            "suggested_staff": pref.preferred_staff[0] if pref.preferred_staff else None,
            "valid_days": 14,
            "personalized_message": f"Hi! We noticed you love {preferred_service}. Enjoy 20% off on your next visit!"
        }

# Initialize recommendation service
ai_recommendations = AIRecommendationService()

# Convenience functions
async def get_personalized_recommendations(customer_id: str, context: str = None):
    """Get personalized service recommendations"""
    return ai_recommendations.get_recommendations(customer_id, context)

async def update_customer_preferences(customer_id: str, booking_history: List[Dict], **kwargs):
    """Update customer preferences"""
    return ai_recommendations.update_customer_preferences(customer_id, booking_history, **kwargs)

async def predict_customer_next_booking(customer_id: str):
    """Predict when customer will book next"""
    return ai_recommendations.predict_next_booking(customer_id)

async def get_churn_risk_customers():
    """Get list of customers at churn risk"""
    return ai_recommendations.get_churn_risk_customers()

async def generate_personalized_offer(customer_id: str):
    """Generate personalized offer"""
    return ai_recommendations.generate_personalized_offer(customer_id)
