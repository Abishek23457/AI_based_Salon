"""
Gift Cards API Router for BookSmart AI
API endpoints for gift card management
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from gift_cards import gift_card_system, create_gift_card, validate_gift_card, redeem_gift_card, get_gift_card_details

router = APIRouter(prefix="/gift-cards", tags=["Gift Cards"])

class CreateGiftCardRequest(BaseModel):
    amount: float
    purchaser_name: str
    purchaser_email: str
    recipient_name: Optional[str] = None
    recipient_email: Optional[str] = None
    message: Optional[str] = None
    design_id: str = "elegant"

class RedeemGiftCardRequest(BaseModel):
    code: str
    amount: float
    customer_id: str
    booking_ref: Optional[str] = None

class ValidateRequest(BaseModel):
    code: str

@router.post("/create")
async def create_card(request: CreateGiftCardRequest):
    """Create a new gift card"""
    card = await create_gift_card(
        amount=request.amount,
        purchaser_name=request.purchaser_name,
        purchaser_email=request.purchaser_email,
        recipient_name=request.recipient_name,
        recipient_email=request.recipient_email,
        message=request.message,
        design_id=request.design_id
    )
    return {
        "success": True,
        "gift_card": {
            "code": card.code,
            "amount": card.amount,
            "balance": card.balance,
            "expires_at": card.expires_at.isoformat()
        }
    }

@router.post("/validate")
async def validate_card(request: ValidateRequest):
    """Validate gift card code"""
    result = await validate_gift_card(request.code)
    return result

@router.post("/redeem")
async def redeem_card(request: RedeemGiftCardRequest):
    """Redeem gift card"""
    result = await redeem_gift_card(
        request.code,
        request.amount,
        request.customer_id,
        request.booking_ref
    )
    if result.get("success"):
        return result
    raise HTTPException(status_code=400, detail=result.get("error", "Redemption failed"))

@router.get("/{code}")
async def get_card(code: str):
    """Get gift card details"""
    details = await get_gift_card_details(code)
    if details:
        return details
    raise HTTPException(status_code=404, detail="Gift card not found")

@router.get("/customer/{email}")
async def get_customer_cards(email: str):
    """Get all gift cards for a customer"""
    cards = gift_card_system.get_customer_cards(email)
    return {"cards": cards}

@router.get("/designs/available")
async def get_designs():
    """Get available gift card designs"""
    return {"designs": gift_card_system.get_available_designs()}

@router.get("/stats")
async def get_stats():
    """Get gift card statistics"""
    total_cards = len(gift_card_system.gift_cards)
    active_cards = sum(1 for c in gift_card_system.gift_cards.values() if c.status == "active")
    total_value = sum(c.balance for c in gift_card_system.gift_cards.values())
    
    return {
        "total_cards": total_cards,
        "active_cards": active_cards,
        "total_value_remaining": total_value
    }
