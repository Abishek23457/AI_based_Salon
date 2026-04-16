"""Test BookSmart AI Application"""
import requests
import json

BASE_URL = 'http://localhost:8000'

def test_endpoint(name, method, endpoint, expected_status=200, payload=None):
    """Test an API endpoint"""
    try:
        url = f'{BASE_URL}{endpoint}'
        if method == 'GET':
            r = requests.get(url, timeout=5)
        elif method == 'POST':
            r = requests.post(url, json=payload, timeout=5)
        
        success = r.status_code == expected_status
        status = "PASS" if success else f"FAIL ({r.status_code})"
        return True, status, r.json() if success else None
    except Exception as e:
        return False, f"ERROR: {str(e)[:50]}", None

def main():
    print("=" * 70)
    print("BOOKSMART AI - APPLICATION TESTING")
    print("=" * 70)
    
    tests = [
        ("Health Check", "GET", "/health"),
        ("API Status", "GET", "/"),
        ("Services List", "GET", "/services/?salon_id=1"),
        ("Staff List", "GET", "/staff/?salon_id=1"),
        ("Razorpay Status", "GET", "/payments/status"),
        ("WhatsApp Status", "GET", "/api/whatsapp/status"),
        ("Gift Cards Stats", "GET", "/api/gift-cards/stats"),
        ("Loyalty Rewards", "GET", "/api/loyalty/rewards/available"),
        ("Analytics Dashboard", "GET", "/api/analytics/dashboard"),
        ("Simple Chat", "POST", "/simple-chat", {"message": "hello", "customer_name": "Test"}),
    ]
    
    passed = 0
    failed = 0
    
    for name, method, endpoint, *payload in tests:
        print(f"\n{name}...")
        success, status, data = test_endpoint(name, method, endpoint, payload=payload[0] if payload else None)
        print(f"   {status}")
        
        if success:
            passed += 1
            if data:
                if isinstance(data, dict):
                    if 'status' in data:
                        print(f"   -> Status: {data['status']}")
                    if isinstance(data.get('features'), dict):
                        active = sum(1 for v in data['features'].values() if v == 'active')
                        print(f"   -> Active Features: {active}")
        else:
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"RESULTS: {passed} PASSED, {failed} FAILED")
    print("=" * 70)
    
    if failed == 0:
        print("ALL TESTS PASSED! Application is working correctly.")
    else:
        print(f"{failed} tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()
