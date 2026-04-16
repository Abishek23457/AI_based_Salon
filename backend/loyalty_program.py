"""
Loyalty Program System for BookSmart AI
Manages customer points, rewards, and tier-based benefits
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class LoyaltyTier:
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"

class LoyaltyPoints(BaseModel):
    customer_id: str
    total_points: int = 0
    lifetime_points: int = 0
    tier: str = LoyaltyTier.BRONZE
    last_activity: datetime = None
    rewards_redeemed: int = 0

class LoyaltyReward(BaseModel):
    id: str
    name: str
    description: str
    points_required: int
    discount_value: float
    is_active: bool = True

class LoyaltyProgram:
    """Customer Loyalty Program Manager"""
    
    TIER_THRESHOLDS = {
        LoyaltyTier.BRONZE: 0,
        LoyaltyTier.SILVER: 500,
        LoyaltyTier.GOLD: 1500,
        LoyaltyTier.PLATINUM: 5000
    }
    
    POINTS_PER_BOOKING = 10  # Base points
    POINTS_PER_RUPEE = 1     # 1 point per rupee spent
    
    def __init__(self):
        self.customer_points: Dict[str, LoyaltyPoints] = {}
        self.available_rewards: List[LoyaltyReward] = [
            LoyaltyReward(
                id="discount_10",
                name="10% Off",
                description="10% discount on any service",
                points_required=100,
                discount_value=0.10
            ),
            LoyaltyReward(
                id="discount_20",
                name="20% Off",
                description="20% discount on any service",
                points_required=250,
                discount_value=0.20
            ),
            LoyaltyReward(
                id="free_service",
                name="Free Basic Service",
                description="One free basic service",
                points_required=500,
                discount_value=1.0
            ),
            LoyaltyReward(
                id="premium_discount",
                name="30% Off Premium",
                description="30% off premium services",
                points_required=750,
                discount_value=0.30
            )
        ]
    
    def get_or_create_account(self, customer_id: str) -> LoyaltyPoints:
        """Get or create loyalty account for customer"""
        if customer_id not in self.customer_points:
            self.customer_points[customer_id] = LoyaltyPoints(
                customer_id=customer_id,
                total_points=0,
                lifetime_points=0,
                tier=LoyaltyTier.BRONZE,
                last_activity=datetime.now()
            )
            logger.info(f"[Loyalty] Created new account for {customer_id}")
        return self.customer_points[customer_id]
    
    def calculate_tier(self, lifetime_points: int) -> str:
        """Calculate tier based on lifetime points"""
        current_tier = LoyaltyTier.BRONZE
        for tier, threshold in sorted(self.TIER_THRESHOLDS.items(), key=lambda x: x[1], reverse=True):
            if lifetime_points >= threshold:
                return tier
        return current_tier
    
    def add_points(self, customer_id: str, booking_amount: float, service_name: str = None) -> dict:
        """Add points for a booking"""
        account = self.get_or_create_account(customer_id)
        
        # Calculate points
        base_points = self.POINTS_PER_BOOKING
        spend_points = int(booking_amount * self.POINTS_PER_RUPEE)
        total_earned = base_points + spend_points
        
        # Update account
        account.total_points += total_earned
        account.lifetime_points += total_earned
        account.last_activity = datetime.now()
        
        # Check for tier upgrade
        new_tier = self.calculate_tier(account.lifetime_points)
        tier_upgraded = new_tier != account.tier
        account.tier = new_tier
        
        if tier_upgraded:
            logger.info(f"[Loyalty] Customer {customer_id} upgraded to {new_tier} tier!")
        
        logger.info(f"[Loyalty] Added {total_earned} points to {customer_id}. Total: {account.total_points}")
        
        return {
            "points_earned": total_earned,
            "total_points": account.total_points,
            "lifetime_points": account.lifetime_points,
            "tier": account.tier,
            "tier_upgraded": tier_upgraded
        }
    
    def redeem_reward(self, customer_id: str, reward_id: str) -> dict:
        """Redeem points for a reward"""
        account = self.get_or_create_account(customer_id)
        
        # Find reward
        reward = next((r for r in self.available_rewards if r.id == reward_id and r.is_active), None)
        if not reward:
            return {"success": False, "error": "Reward not found or inactive"}
        
        # Check points
        if account.total_points < reward.points_required:
            return {
                "success": False, 
                "error": f"Insufficient points. Need {reward.points_required}, have {account.total_points}"
            }
        
        # Deduct points
        account.total_points -= reward.points_required
        account.rewards_redeemed += 1
        account.last_activity = datetime.now()
        
        logger.info(f"[Loyalty] {customer_id} redeemed {reward.name} for {reward.points_required} points")
        
        return {
            "success": True,
            "reward": reward.name,
            "discount_value": reward.discount_value,
            "points_remaining": account.total_points
        }
    
    def get_account_summary(self, customer_id: str) -> dict:
        """Get loyalty account summary"""
        account = self.get_or_create_account(customer_id)
        
        # Calculate next tier progress
        tiers = sorted(self.TIER_THRESHOLDS.items(), key=lambda x: x[1])
        current_tier_points = self.TIER_THRESHOLDS.get(account.tier, 0)
        next_tier = None
        next_tier_threshold = None
        
        for tier, threshold in tiers:
            if threshold > current_tier_points:
                next_tier = tier
                next_tier_threshold = threshold
                break
        
        progress = {
            "current": account.lifetime_points - current_tier_points,
            "required": next_tier_threshold - current_tier_points if next_tier_threshold else 0,
            "next_tier": next_tier
        }
        
        return {
            "customer_id": customer_id,
            "total_points": account.total_points,
            "lifetime_points": account.lifetime_points,
            "tier": account.tier,
            "rewards_redeemed": account.rewards_redeemed,
            "tier_progress": progress,
            "available_rewards": [
                {
                    "id": r.id,
                    "name": r.name,
                    "description": r.description,
                    "points_required": r.points_required,
                    "can_redeem": account.total_points >= r.points_required
                }
                for r in self.available_rewards if r.is_active
            ]
        }
    
    def get_tier_benefits(self, tier: str) -> List[str]:
        """Get benefits for a tier"""
        benefits = {
            LoyaltyTier.BRONZE: [
                "Earn 1 point per ₹1 spent",
                "Birthday month 5% discount"
            ],
            LoyaltyTier.SILVER: [
                "Earn 1.2 points per ₹1 spent",
                "Birthday month 10% discount",
                "Priority booking"
            ],
            LoyaltyTier.GOLD: [
                "Earn 1.5 points per ₹1 spent",
                "Birthday month 15% discount",
                "Priority booking",
                "Free consultation"
            ],
            LoyaltyTier.PLATINUM: [
                "Earn 2 points per ₹1 spent",
                "Birthday month 20% discount",
                "VIP priority booking",
                "Free consultation",
                "Exclusive access to new services"
            ]
        }
        return benefits.get(tier, [])

# Initialize loyalty program
loyalty_program = LoyaltyProgram()

# Convenience functions
async def add_loyalty_points(customer_id: str, booking_amount: float, service_name: str = None):
    """Add loyalty points for a booking"""
    return loyalty_program.add_points(customer_id, booking_amount, service_name)

async def redeem_loyalty_reward(customer_id: str, reward_id: str):
    """Redeem loyalty points for a reward"""
    return loyalty_program.redeem_reward(customer_id, reward_id)

async def get_loyalty_summary(customer_id: str):
    """Get customer loyalty summary"""
    return loyalty_program.get_account_summary(customer_id)
