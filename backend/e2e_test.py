"""
End-to-End Test Suite for BookSmart AI
Tests all major functionality end-to-end
"""
import asyncio
import aiohttp
import json
from datetime import datetime

class EndToEndTest:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.test_results = []
        
    async def run_test(self, test_name, test_func):
        """Run a single test and log results"""
        print(f"\n{'='*50}")
        print(f"TEST: {test_name}")
        print(f"{'='*50}")
        
        try:
            result = await test_func()
            self.test_results.append({
                "test": test_name,
                "status": "PASS",
                "result": result,
                "timestamp": datetime.now().isoformat()
            })
            print(f"PASS: {test_name}")
            return True
        except Exception as e:
            self.test_results.append({
                "test": test_name,
                "status": "FAIL",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            print(f"FAIL: {test_name} - {str(e)}")
            return False
    
    async def test_backend_health(self):
        """Test backend health"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/") as response:
                data = await response.json()
                assert response.status == 200
                assert "BookSmart AI" in data["message"]
                return data
    
    async def test_texting_ai_chat(self):
        """Test texting AI chat functionality"""
        test_messages = [
            "hey i want to book a haircut today",
            "how much for facial",
            "what are your hours",
            "thanks sounds good"
        ]
        
        async with aiohttp.ClientSession() as session:
            for message in test_messages:
                async with session.post(f"{self.base_url}/texting-chat", 
                    json={"message": message, "customer_name": "TestUser"}) as response:
                    data = await response.json()
                    assert response.status == 200
                    assert "response" in data
                    assert len(data["response"]) > 0
                    print(f"Message: {message}")
                    print(f"AI Response: {data['response']}")
        
        return "Texting AI working correctly"
    
    async def test_user_registration(self):
        """Test user registration"""
        import random
        import string
        
        # Generate unique username
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        unique_username = f"testuser_{random_suffix}"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/auth/register",
                json={
                    "username": unique_username,
                    "password": "testpass123",
                    "salon_name": "Test Salon E2E"
                }) as response:
                data = await response.json()
                assert response.status == 200
                assert "access_token" in data
                return {"username": unique_username, "data": data}
    
    async def test_user_login(self):
        """Test user login"""
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/auth/login",
                json={
                    "username": "admin",
                    "password": "admin123"
                }) as response:
                data = await response.json()
                assert response.status == 200
                assert "access_token" in data
                return data
    
    async def test_exotel_config(self):
        """Test Exotel configuration"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/exotel/app-config") as response:
                data = await response.json()
                assert response.status == 200
                assert "app_name" in data
                return data
    
    async def test_staff_management(self):
        """Test staff management endpoints"""
        async with aiohttp.ClientSession() as session:
            # Test get staff
            async with session.get(f"{self.base_url}/staff-management/staff") as response:
                data = await response.json()
                assert response.status == 200
                assert "staff" in data
                return data
    
    async def test_frontend_accessibility(self):
        """Test frontend is accessible"""
        async with aiohttp.ClientSession() as session:
            async with session.get(self.frontend_url) as response:
                assert response.status == 200
                content = await response.text()
                assert "BookSmart AI" in content
                return "Frontend accessible"
    
    async def test_api_proxy(self):
        """Test frontend API proxy to backend"""
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.frontend_url}/api/texting-chat",
                json={"message": "test", "customer_name": "Test"}) as response:
                data = await response.json()
                assert response.status == 200
                assert "response" in data
                return "API proxy working"
    
    async def test_chat_conversation_flow(self):
        """Test complete chat conversation flow"""
        conversation = [
            "hi",
            "i want to book a haircut",
            "today",
            "2pm",
            "yes confirm"
        ]
        
        async with aiohttp.ClientSession() as session:
            conversation_history = []
            
            for message in conversation:
                async with session.post(f"{self.base_url}/texting-chat",
                    json={
                        "message": message,
                        "customer_name": "John",
                        "conversation_history": conversation_history
                    }) as response:
                    data = await response.json()
                    assert response.status == 200
                    assert "response" in data
                    assert "analysis" in data
                    
                    conversation_history.append({
                        "role": "user",
                        "content": message,
                        "timestamp": datetime.now().isoformat()
                    })
                    conversation_history.append({
                        "role": "ai",
                        "content": data["response"],
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    print(f"User: {message}")
                    print(f"AI: {data['response']}")
                    print(f"Stage: {data['analysis']['conversation_stage']}")
                    print("-" * 30)
        
        return "Conversation flow working correctly"
    
    async def run_all_tests(self):
        """Run all end-to-end tests"""
        print("Starting BookSmart AI End-to-End Tests")
        print(f"Backend URL: {self.base_url}")
        print(f"Frontend URL: {self.frontend_url}")
        
        tests = [
            ("Backend Health Check", self.test_backend_health),
            ("Frontend Accessibility", self.test_frontend_accessibility),
            ("API Proxy Test", self.test_api_proxy),
            ("Texting AI Chat", self.test_texting_ai_chat),
            ("User Registration", self.test_user_registration),
            ("User Login", self.test_user_login),
            ("Exotel Configuration", self.test_exotel_config),
            ("Staff Management", self.test_staff_management),
            ("Chat Conversation Flow", self.test_chat_conversation_flow),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            if await self.run_test(test_name, test_func):
                passed += 1
        
        # Generate test report
        print(f"\n{'='*60}")
        print("END-TO-END TEST REPORT")
        print(f"{'='*60}")
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("ALL TESTS PASSED! System is fully operational.")
        else:
            print("Some tests failed. Check the logs above.")
        
        # Save test results
        with open("e2e_test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\nTest results saved to: e2e_test_results.json")
        return passed == total

# Run the tests
async def main():
    tester = EndToEndTest()
    success = await tester.run_all_tests()
    return success

if __name__ == "__main__":
    asyncio.run(main())
