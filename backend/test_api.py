from fastapi.testclient import TestClient
from main import app
from database import Base, engine
import pytest

# Create all tables synchronously for the test payload scope
Base.metadata.create_all(bind=engine)

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert "message" in body
    assert "BookSmart AI API" in body["message"]

def test_create_service():
    payload = {
        "name": "Test Haircut",
        "duration_minutes": 30,
        "price": 500.0,
        "description": "A quick test trim via pytest"
    }
    response = client.post("/services/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Haircut"
    assert "id" in data

def test_get_services():
    response = client.get("/services/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

def test_ai_chat_mock():
    payload = {
        "salon_id": "1",
        "message": "Hi, what time are you open?"
    }
    # Test that the chat endpoint successfully proxies to the Langchain chain without crashing
    response = client.post("/chat", json=payload)
    assert response.status_code == 200
    assert "answer" in response.json()
