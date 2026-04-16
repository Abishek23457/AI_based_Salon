"""
Gift Cards System for BookSmart AI
Digital gift card purchase, redemption, and management
"""
import uuid
import random
import string
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class GiftCardStatus:
    ACTIVE = "active"
    REDEEMED = "redeemed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class GiftCard(BaseModel):
    id: str
    code: str
    amount: float
    balance: float
    purchaser_name: str
    purchaser_email: str
    recipient_name: Optional[str] = None
    recipient_email: Optional[str] = None
    message: Optional[str] = None
    status: str = GiftCardStatus.ACTIVE
    created_at: datetime = None
    expires_at: datetime = None
    redeemed_at: Optional[datetime] = None
    redeemed_by: Optional[str] = None
    transactions: List[Dict] = []

class GiftCardSystem:
    """Digital Gift Card Management System"""
    
    DEFAULT_EXPIRY_DAYS = 365  # 1 year validity
    
    def __init__(self):
        self.gift_cards: Dict[str, GiftCard] = {}  # code -> GiftCard
        self.designs = [
            {"id": "elegant", "name": "Elegant Gold", "theme": "gold"},
            {"id": "modern", "name": "Modern Black", "theme": "dark"},
            {"id": "festive", "name": "Festive Red", "theme": "red"},
            {"id": "nature", "name": "Nature Green", "theme": "green"}
        ]
    
    def generate_code(self) -> str:
        """Generate unique gift card code"""
        # Format: BS-XXXX-XXXX-XXXX
        parts = [''.join(random.choices(string.ascii_uppercase + string.digits, k=4)) for _ in range(3)]
        return f"BS-{parts[0]}-{parts[1]}-{parts[2]}"
    
    def create_gift_card(self, amount: float, purchaser_name: str, purchaser_email: str,
                        recipient_name: str = None, recipient_email: str = None,
                        message: str = None, design_id: str = "elegant") -> GiftCard:
        """Create a new gift card"""
        code = self.generate_code()
        while code in self.gift_cards:  # Ensure uniqueness
            code = self.generate_code()
        
        now = datetime.now()
        gift_card = GiftCard(
            id=str(uuid.uuid4()),
            code=code,
            amount=amount,
            balance=amount,
            purchaser_name=purchaser_name,
            purchaser_email=purchaser_email,
            recipient_name=recipient_name,
            recipient_email=recipient_email,
            message=message,
            created_at=now,
            expires_at=now + timedelta(days=self.DEFAULT_EXPIRY_DAYS),
            transactions=[{
                "type": "creation",
                "amount": amount,
                "timestamp": now.isoformat(),
                "description": "Gift card purchased"
            }]
        )
        
        self.gift_cards[code] = gift_card
        logger.info(f"[GiftCard] Created {code} for ₹{amount}")
        
        return gift_card
    
    def validate_card(self, code: str) -> dict:
        """Validate gift card code"""
        code = code.upper().replace(" ", "")
        
        if code not in self.gift_cards:
            return {"valid": False, "error": "Invalid gift card code"}
        
        card = self.gift_cards[code]
        
        # Check expiry
        if datetime.now() > card.expires_at:
            card.status = GiftCardStatus.EXPIRED
            return {"valid": False, "error": "Gift card has expired", "expired_at": card.expires_at.isoformat()}
        
        # Check status
        if card.status == GiftCardStatus.REDEEMED:
            return {"valid": False, "error": "Gift card has been fully redeemed"}
        
        if card.status == GiftCardStatus.CANCELLED:
            return {"valid": False, "error": "Gift card has been cancelled"}
        
        return {
            "valid": True,
            "code": code,
            "balance": card.balance,
            "original_amount": card.amount,
            "expires_at": card.expires_at.isoformat(),
            "recipient_name": card.recipient_name
        }
    
    def redeem(self, code: str, amount: float, customer_id: str, booking_ref: str = None) -> dict:
        """Redeem amount from gift card"""
        validation = self.validate_card(code)
        if not validation["valid"]:
            return validation
        
        card = self.gift_cards[code]
        
        # Check balance
        if amount > card.balance:
            return {
                "success": False,
                "error": f"Insufficient balance. Available: ₹{card.balance}, Requested: ₹{amount}"
            }
        
        # Deduct amount
        card.balance -= amount
        now = datetime.now()
        
        transaction = {
            "type": "redemption",
            "amount": -amount,
            "timestamp": now.isoformat(),
            "customer_id": customer_id,
            "booking_ref": booking_ref,
            "description": f"Redeemed ₹{amount}"
        }
        card.transactions.append(transaction)
        
        # Update status if fully redeemed
        if card.balance <= 0:
            card.status = GiftCardStatus.REDEEMED
            card.redeemed_at = now
            card.redeemed_by = customer_id
        
        logger.info(f"[GiftCard] Redeemed ₹{amount} from {code}. Balance: ₹{card.balance}")
        
        return {
            "success": True,
            "amount_redeemed": amount,
            "remaining_balance": card.balance,
            "code": code,
            "is_fully_redeemed": card.balance <= 0
        }
    
    def get_card_details(self, code: str) -> Optional[dict]:
        """Get full gift card details"""
        code = code.upper().replace(" ", "")
        
        if code not in self.gift_cards:
            return None
        
        card = self.gift_cards[code]
        
        return {
            "id": card.id,
            "code": card.code,
            "amount": card.amount,
            "balance": card.balance,
            "purchaser_name": card.purchaser_name,
            "purchaser_email": card.purchaser_email,
            "recipient_name": card.recipient_name,
            "recipient_email": card.recipient_email,
            "message": card.message,
            "status": card.status,
            "created_at": card.created_at.isoformat(),
            "expires_at": card.expires_at.isoformat(),
            "redeemed_at": card.redeemed_at.isoformat() if card.redeemed_at else None,
            "transactions": card.transactions
        }
    
    def get_customer_cards(self, email: str) -> List[dict]:
        """Get all gift cards purchased or received by email"""
        cards = []
        
        for card in self.gift_cards.values():
            if card.purchaser_email == email or card.recipient_email == email:
                cards.append({
                    "code": card.code,
                    "amount": card.amount,
                    "balance": card.balance,
                    "status": card.status,
                    "expires_at": card.expires_at.isoformat(),
                    "is_purchaser": card.purchaser_email == email
                })
        
        return cards
    
    def get_available_designs(self) -> List[dict]:
        """Get available gift card designs"""
        return self.designs

# Initialize gift card system
gift_card_system = GiftCardSystem()

# Convenience functions
async def create_gift_card(amount: float, purchaser_name: str, purchaser_email: str,
                           recipient_name: str = None, recipient_email: str = None,
                           message: str = None, design_id: str = "elegant"):
    """Create a new gift card"""
    return gift_card_system.create_gift_card(
        amount, purchaser_name, purchaser_email,
        recipient_name, recipient_email, message, design_id
    )

async def validate_gift_card(code: str):
    """Validate gift card code"""
    return gift_card_system.validate_card(code)

async def redeem_gift_card(code: str, amount: float, customer_id: str, booking_ref: str = None):
    """Redeem gift card"""
    return gift_card_system.redeem(code, amount, customer_id, booking_ref)

async def get_gift_card_details(code: str):
    """Get gift card details"""
    return gift_card_system.get_card_details(code)
