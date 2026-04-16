"""
Loyalty Program API Router for BookSmart AI
API endpoints for loyalty points and rewards
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from loyalty_program import loyalty_program, add_loyalty_points, redeem_loyalty_reward, get_loyalty_summary

router = APIRouter(prefix="/loyalty", tags=["Loyalty Program"])

class AddPointsRequest(BaseModel):
    customer_id: str
    booking_amount: float
    service_name: Optional[str] = None

class RedeemRewardRequest(BaseModel):
    customer_id: str
    reward_id: str

@router.get("/{customer_id}/summary")
async def get_summary(customer_id: str):
    """Get customer loyalty summary"""
    summary = await get_loyalty_summary(customer_id)
    return summary

@router.post("/{customer_id}/add-points")
async def add_points(request: AddPointsRequest):
    """Add loyalty points for a booking"""
    result = await add_loyalty_points(
        request.customer_id,
        request.booking_amount,
        request.service_name
    )
    return result

@router.post("/{customer_id}/redeem")
async def redeem(request: RedeemRewardRequest):
    """Redeem loyalty points for a reward"""
    result = await redeem_loyalty_reward(request.customer_id, request.reward_id)
    if result.get("success"):
        return result
    raise HTTPException(status_code=400, detail=result.get("error", "Redemption failed"))

@router.get("/{customer_id}/benefits")
async def get_benefits(customer_id: str):
    """Get tier benefits for customer"""
    summary = await get_loyalty_summary(customer_id)
    tier = summary.get("tier", "bronze")
    benefits = loyalty_program.get_tier_benefits(tier)
    return {
        "tier": tier,
        "benefits": benefits
    }

@router.get("/rewards/available")
async def get_available_rewards():
    """Get all available rewards"""
    return {
        "rewards": [
            {
                "id": r.id,
                "name": r.name,
                "description": r.description,
                "points_required": r.points_required,
                "discount_value": r.discount_value
            }
            for r in loyalty_program.available_rewards
        ]
    }

@router.get("/stats")
async def get_stats():
    """Get loyalty program statistics"""
    total_members = len(loyalty_program.customer_points)
    tier_counts = {}
    total_points_issued = 0
    
    for account in loyalty_program.customer_points.values():
        tier_counts[account.tier] = tier_counts.get(account.tier, 0) + 1
        total_points_issued += account.lifetime_points
    
    return {
        "total_members": total_members,
        "tier_distribution": tier_counts,
        "total_points_issued": total_points_issued
    }
