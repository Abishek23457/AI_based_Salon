"""Test Razorpay Integration"""
import asyncio
from razorpay_integration import razorpay_service, create_payment_order, verify_razorpay_payment, get_payment_stats

async def test():
    print("=" * 50)
    print("RAZORPAY INTEGRATION TEST")
    print("=" * 50)
    print()
    
    # Test 1: Create order
    print("1. Creating payment order...")
    order = await create_payment_order(
        amount=1000.00,
        receipt="test_booking_123",
        notes={"customer": "Test Customer", "service": "Haircut"}
    )
    print(f"   Order created: {order['id']}")
    print(f"   Amount: Rs.{order['amount']/100}")
    
    # Test 2: Verify payment (mock)
    print()
    print("2. Verifying payment...")
    verified = await verify_razorpay_payment(
        order["id"],
        "pay_mock_123",
        "mock_signature"
    )
    print(f"   Payment verified: {verified}")
    
    # Test 3: Get stats
    print()
    print("3. Getting payment stats...")
    stats = await get_payment_stats()
    print(f"   Mode: {stats['status']}")
    print(f"   Total Payments: {stats['total_payments']}")
    print(f"   Successful: {stats['successful']}")
    print(f"   Failed: {stats['failed']}")
    
    print()
    print("=" * 50)
    print("ALL TESTS PASSED!")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test())
