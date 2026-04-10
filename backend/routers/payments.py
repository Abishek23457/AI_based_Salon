"""
Razorpay Payment Integration for BookSmart AI.
Creates payment orders and verifies payment signatures.
Falls back gracefully when keys are not configured.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from config import settings

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
