"""
Razorpay Payment Integration for BookSmart AI.
Creates payment orders and verifies payment signatures.
Falls back gracefully when keys are not configured.
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, Dict
from config import settings
from razorpay_integration import razorpay_service, create_payment_order, verify_razorpay_payment, process_refund, get_payment_details

router = APIRouter(prefix="/payments", tags=["Payments"])


class PaymentOrderRequest(BaseModel):
    booking_id: int
    amount: float  # in INR
    customer_name: str
    customer_email: Optional[str] = ""
    customer_phone: str


class PaymentOrderResponse(BaseModel):
    order_id: str
    amount: int  # in paise
    currency: str
    key_id: str
    booking_id: int


class PaymentVerifyRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    booking_id: int


@router.post("/create-order", response_model=PaymentOrderResponse)
def create_payment_order(body: PaymentOrderRequest):
    """Create a Razorpay order for advance booking payment."""
    key_id = settings.RAZORPAY_KEY_ID
    key_secret = settings.RAZORPAY_KEY_SECRET

    if not key_id or not key_secret:
        # Demo mode: return a mock order for frontend testing
        return PaymentOrderResponse(
            order_id=f"order_demo_{body.booking_id}",
            amount=int(body.amount * 100),
            currency="INR",
            key_id="rzp_demo_key",
            booking_id=body.booking_id,
        )

    try:
        import razorpay
        client = razorpay.Client(auth=(key_id, key_secret))

        order = client.order.create({
            "amount": int(body.amount * 100),  # Razorpay uses paise
            "currency": "INR",
            "receipt": f"booksmart_{body.booking_id}",
            "notes": {
                "customer_name": body.customer_name,
                "booking_id": body.booking_id,
            },
        })

        return PaymentOrderResponse(
            order_id=order["id"],
            amount=order["amount"],
            currency=order["currency"],
            key_id=key_id,
            booking_id=body.booking_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment order failed: {str(e)}")


@router.post("/verify")
def verify_payment(body: PaymentVerifyRequest):
    """Verify Razorpay payment signature after checkout."""
    key_id = settings.RAZORPAY_KEY_ID
    key_secret = settings.RAZORPAY_KEY_SECRET

    if not key_id or not key_secret:
        # Demo mode: always succeed
        return {"status": "verified_demo", "booking_id": body.booking_id}

    try:
        import razorpay
        client = razorpay.Client(auth=(key_id, key_secret))

        client.utility.verify_payment_signature({
            "razorpay_order_id": body.razorpay_order_id,
            "razorpay_payment_id": body.razorpay_payment_id,
            "razorpay_signature": body.razorpay_signature,
        })
        return {"status": "verified", "booking_id": body.booking_id, "payment_id": body.razorpay_payment_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Payment verification failed: {str(e)}")


class RefundRequest(BaseModel):
    payment_id: str
    amount: Optional[float] = None  # If None, full refund
    reason: Optional[str] = ""

class PaymentLinkRequest(BaseModel):
    amount: float
    description: str
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None

class WebhookPayload(BaseModel):
    event: str
    payload: Dict

@router.post("/refund")
async def refund_payment(request: RefundRequest):
    """Process refund for a payment"""
    try:
        result = await process_refund(
            request.payment_id,
            request.amount,
            {"reason": request.reason}
        )
        return {
            "success": True,
            "refund_id": result.get("id"),
            "amount": result.get("amount", 0) / 100,
            "status": result.get("status")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refund failed: {str(e)}")

@router.post("/create-link")
async def create_payment_link(request: PaymentLinkRequest):
    """Create a payment link for customer"""
    try:
        customer = {}
        if request.customer_name:
            customer["name"] = request.customer_name
        if request.customer_email:
            customer["email"] = request.customer_email
        if request.customer_phone:
            customer["contact"] = request.customer_phone
        
        link = razorpay_service.get_payment_link(
            request.amount,
            request.description,
            customer if customer else None
        )
        return {"success": True, "payment_link": link}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create payment link: {str(e)}")

@router.get("/payment/{payment_id}")
async def fetch_payment(payment_id: str):
    """Fetch payment details"""
    try:
        payment = await get_payment_details(payment_id)
        return {
            "payment_id": payment.get("id"),
            "status": payment.get("status"),
            "amount": payment.get("amount", 0) / 100,
            "method": payment.get("method"),
            "created_at": payment.get("created_at")
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Payment not found: {str(e)}")

@router.post("/webhook")
async def handle_webhook(request: Request):
    """Handle Razorpay webhook events"""
    try:
        payload = await request.body()
        signature = request.headers.get("X-Razorpay-Signature", "")
        
        # Verify webhook
        if not razorpay_service.verify_webhook(payload, signature):
            raise HTTPException(status_code=400, detail="Invalid webhook signature")
        
        import json
        data = json.loads(payload)
        event = data.get("event", "")
        
        # Handle event
        result = razorpay_service.handle_webhook(event, data)
        
        return {"status": "received", "processed": result}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Webhook processing failed: {str(e)}")

@router.get("/stats")
async def get_stats():
    """Get payment statistics"""
    return await razorpay_service.get_payment_stats()

@router.get("/status")
async def get_status():
    """Get Razorpay integration status"""
    return {
        "status": "active" if not razorpay_service.mock_mode else "mock_mode",
        "mock_mode": razorpay_service.mock_mode,
        "key_id_configured": bool(razorpay_service.key_id),
        "webhook_secret_configured": bool(razorpay_service.webhook_secret)
    }
