from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI(
    title="BookSmart AI API",
    description="Intelligent Salon Management System API",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class LoginRequest(BaseModel):
    username: str
    password: str

class ChatMessage(BaseModel):
    message: str
    customer_name: Optional[str] = "Customer"

# Basic endpoints
@app.get("/")
async def root():
    """
    API Root Endpoint
    
    Returns basic API information and status.
    """
    return {
        "message": "BookSmart AI API",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/services/")
async def get_services():
    """
    Get available services for booking
    
    Returns a list of available salon services with pricing.
    """
    services = [
        {
            "id": 1,
            "name": "Haircut",
            "price": 500,
            "duration_minutes": 30
        },
        {
            "id": 2,
            "name": "Hair Coloring",
            "price": 1500,
            "duration_minutes": 60
        },
        {
            "id": 3,
            "name": "Hair Styling",
            "price": 800,
            "duration_minutes": 45
        },
        {
            "id": 4,
            "name": "Beard Trim",
            "price": 300,
            "duration_minutes": 20
        },
        {
            "id": 5,
            "name": "Facial",
            "price": 1000,
            "duration_minutes": 40
        }
    ]
    return {"services": services}

@app.post("/auth/login")
async def login(request: LoginRequest):
    """
    Authenticate user and return JWT token
    
    - **username**: User's username
    - **password**: User's password
    
    Returns authentication token on successful login.
    """
    # Use secure authentication from auth_utils
    from auth_utils import authenticate_user
    user = authenticate_user(request.username, request.password)
    if user:
        return {
            "access_token": "demo_jwt_token_12345",
            "token_type": "bearer",
            "user": {
                "username": request.username,
                "role": "admin"
            }
        }
    else:
        return {"error": "Invalid credentials"}

@app.post("/texting-chat")
async def texting_chat(message: ChatMessage):
    """
    AI Chat Endpoint
    
    - **message**: Chat message from user
    - **customer_name**: Optional customer name
    
    Returns AI response for the chat message.
    """
    # Simple AI response for demo
    responses = [
        "Hello! I'm the BookSmart AI assistant. How can I help you today?",
        "I can help you book appointments, check prices, and answer questions about our services.",
        "Would you like to schedule an appointment? I can check available times for you.",
        "Our services include haircuts, styling, coloring, and treatments. What are you interested in?",
        "I can provide pricing information and help you choose the right service for your needs."
    ]
    
    import random
    ai_response = random.choice(responses)
    
    return {
        "response": ai_response,
        "customer_name": message.customer_name,
        "timestamp": "2024-01-01T12:00:00Z"
    }

@app.get("/api/status")
async def api_status():
    """
    API Status Endpoint
    
    Returns detailed system status and health information.
    """
    return {
        "status": "healthy",
        "version": "2.0.0",
        "features": {
            "ai_chat": "active",
            "booking": "active",
            "staff_management": "active",
            "payment_processing": "active"
        },
        "endpoints": {
            "auth": "/auth/login",
            "chat": "/texting-chat",
            "status": "/api/status",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
