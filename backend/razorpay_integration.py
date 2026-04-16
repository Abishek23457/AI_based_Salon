"""
Complete Razorpay Integration for BookSmart AI
Payment processing, webhooks, refunds, and payment management
"""
import razorpay
import hmac
import hashlib
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel
from config import settings
import logging

logger = logging.getLogger(__name__)

class PaymentStatus:
    CREATED = "created"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    REFUNDED = "refunded"
    FAILED = "failed"

class RazorpayIntegration:
    """Complete Razorpay Payment Service"""
    
    def __init__(self):
        self.key_id = getattr(settings, 'RAZORPAY_KEY_ID', '')
        self.key_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', '')
        self.webhook_secret = getattr(settings, 'RAZORPAY_WEBHOOK_SECRET', '')
        
        self.mock_mode = not all([self.key_id, self.key_secret])
        
        if not self.mock_mode:
            self.client = razorpay.Client(auth=(self.key_id, self.key_secret))
        else:
            self.client = None
            logger.info("[Razorpay] Running in mock mode")
        
        # In-memory storage for payments (use database in production)
        self.payments: Dict[str, Dict] = {}
        self.refunds: Dict[str, Dict] = {}
    
    def create_order(self, amount: float, currency: str = "INR", 
                    receipt: str = None, notes: Dict = None) -> Dict:
        """Create a new payment order"""
        
        if self.mock_mode:
            order_id = f"order_mock_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            order = {
                "id": order_id,
                "amount": int(amount * 100),
                "currency": currency,
                "receipt": receipt or f"receipt_{order_id}",
                "status": "created",
                "notes": notes or {}
            }
            logger.info(f"[Razorpay MOCK] Created order {order_id}")
            return order
        
        try:
            order_data = {
                "amount": int(amount * 100),  # Convert to paise
                "currency": currency,
                "receipt": receipt,
                "notes": notes or {}
            }
            
            order = self.client.order.create(data=order_data)
            logger.info(f"[Razorpay] Created order {order['id']}")
            return order
            
        except Exception as e:
            logger.error(f"[Razorpay] Failed to create order: {e}")
            raise
    
    def verify_payment(self, order_id: str, payment_id: str, signature: str) -> bool:
        """Verify payment signature"""
        
        if self.mock_mode:
            logger.info(f"[Razorpay MOCK] Verified payment {payment_id}")
            return True
        
        try:
            params = {
                "razorpay_order_id": order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature
            }
            
            self.client.utility.verify_payment_signature(params)
            logger.info(f"[Razorpay] Payment verified: {payment_id}")
            return True
            
        except Exception as e:
            logger.error(f"[Razorpay] Payment verification failed: {e}")
            return False
    
    def capture_payment(self, payment_id: str, amount: float) -> Dict:
        """Capture authorized payment"""
        
        if self.mock_mode:
            return {
                "id": payment_id,
                "status": "captured",
                "amount": int(amount * 100),
                "captured": True
            }
        
        try:
            capture_data = {"amount": int(amount * 100)}
            payment = self.client.payment.capture(payment_id, capture_data)
            logger.info(f"[Razorpay] Captured payment {payment_id}")
            return payment
            
        except Exception as e:
            logger.error(f"[Razorpay] Failed to capture payment: {e}")
            raise
    
    def fetch_payment(self, payment_id: str) -> Dict:
        """Fetch payment details"""
        
        if self.mock_mode:
            return self.payments.get(payment_id, {
                "id": payment_id,
                "status": "captured",
                "amount": 100000,
                "method": "card"
            })
        
        try:
            payment = self.client.payment.fetch(payment_id)
            return payment
            
        except Exception as e:
            logger.error(f"[Razorpay] Failed to fetch payment: {e}")
            raise
    
    def fetch_order(self, order_id: str) -> Dict:
        """Fetch order details"""
        
        if self.mock_mode:
            return {
                "id": order_id,
                "status": "paid",
                "amount": 100000,
                "amount_paid": 100000
            }
        
        try:
            order = self.client.order.fetch(order_id)
            return order
            
        except Exception as e:
            logger.error(f"[Razorpay] Failed to fetch order: {e}")
            raise
    
    def process_refund(self, payment_id: str, amount: float = None, 
                      notes: Dict = None) -> Dict:
        """Process refund for a payment"""
        
        refund_data = {
            "notes": notes or {}
        }
        
        if amount:
            refund_data["amount"] = int(amount * 100)
        
        if self.mock_mode:
            refund_id = f"refund_mock_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            refund = {
                "id": refund_id,
                "payment_id": payment_id,
                "amount": int(amount * 100) if amount else 100000,
                "status": "processed",
                "created_at": int(datetime.now().timestamp())
            }
            self.refunds[refund_id] = refund
            logger.info(f"[Razorpay MOCK] Processed refund {refund_id}")
            return refund
        
        try:
            refund = self.client.payment.refund(payment_id, refund_data)
            logger.info(f"[Razorpay] Processed refund {refund['id']}")
            return refund
            
        except Exception as e:
            logger.error(f"[Razorpay] Refund failed: {e}")
            raise
    
    def fetch_refund(self, refund_id: str) -> Dict:
        """Fetch refund details"""
        
        if self.mock_mode:
            return self.refunds.get(refund_id, {
                "id": refund_id,
                "status": "processed",
                "amount": 100000
            })
        
        try:
            refund = self.client.refund.fetch(refund_id)
            return refund
            
        except Exception as e:
            logger.error(f"[Razorpay] Failed to fetch refund: {e}")
            raise
    
    def verify_webhook(self, payload: bytes, signature: str) -> bool:
        """Verify webhook signature"""
        
        if self.mock_mode or not self.webhook_secret:
            return True
        
        try:
            expected_signature = hmac.new(
                self.webhook_secret.encode(),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(expected_signature, signature)
            
        except Exception as e:
            logger.error(f"[Razorpay] Webhook verification failed: {e}")
            return False
    
    def handle_webhook(self, event: str, payload: Dict) -> Dict:
        """Handle webhook events"""
        
        logger.info(f"[Razorpay] Webhook event: {event}")
        
        if event == "payment.captured":
            payment_id = payload.get("payload", {}).get("payment", {}).get("entity", {}).get("id")
            order_id = payload.get("payload", {}).get("payment", {}).get("entity", {}).get("order_id")
            
            # Update payment status
            self.payments[payment_id] = {
                "id": payment_id,
                "order_id": order_id,
                "status": "captured",
                "captured_at": datetime.now().isoformat()
            }
            
            return {"status": "success", "payment_id": payment_id}
        
        elif event == "payment.failed":
            payment_id = payload.get("payload", {}).get("payment", {}).get("entity", {}).get("id")
            
            self.payments[payment_id] = {
                "id": payment_id,
                "status": "failed",
                "failed_at": datetime.now().isoformat()
            }
            
            return {"status": "failed_recorded", "payment_id": payment_id}
        
        elif event == "refund.processed":
            refund_id = payload.get("payload", {}).get("refund", {}).get("entity", {}).get("id")
            
            return {"status": "refund_recorded", "refund_id": refund_id}
        
        return {"status": "ignored", "event": event}
    
    def get_payment_link(self, amount: float, description: str, 
                        customer: Dict = None) -> str:
        """Create a payment link"""
        
        if self.mock_mode:
            link_id = f"plink_mock_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            return f"https://razorpay.com/mock_payment/{link_id}"
        
        try:
            link_data = {
                "amount": int(amount * 100),
                "currency": "INR",
                "description": description,
                "customer": customer or {}
            }
            
            link = self.client.payment_link.create(link_data)
            return link.get("short_url", link.get("url"))
            
        except Exception as e:
            logger.error(f"[Razorpay] Failed to create payment link: {e}")
            raise
    
    def get_payment_stats(self) -> Dict:
        """Get payment statistics"""
        
        total_payments = len(self.payments)
        captured = sum(1 for p in self.payments.values() if p.get("status") == "captured")
        failed = sum(1 for p in self.payments.values() if p.get("status") == "failed")
        total_refunds = len(self.refunds)
        
        return {
            "total_payments": total_payments,
            "successful": captured,
            "failed": failed,
            "total_refunds": total_refunds,
            "mock_mode": self.mock_mode,
            "status": "active" if not self.mock_mode else "mock_mode"
        }

# Initialize Razorpay integration
razorpay_service = RazorpayIntegration()

# Convenience functions
async def create_payment_order(amount: float, receipt: str = None, notes: Dict = None):
    """Create a new payment order"""
    return razorpay_service.create_order(amount, receipt=receipt, notes=notes)

async def verify_razorpay_payment(order_id: str, payment_id: str, signature: str):
    """Verify Razorpay payment"""
    return razorpay_service.verify_payment(order_id, payment_id, signature)

async def process_refund(payment_id: str, amount: float = None, notes: Dict = None):
    """Process refund"""
    return razorpay_service.process_refund(payment_id, amount, notes)

async def get_payment_details(payment_id: str):
    """Get payment details"""
    return razorpay_service.fetch_payment(payment_id)

async def get_payment_stats():
    """Get payment statistics"""
    return razorpay_service.get_payment_stats()
