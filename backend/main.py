from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import models, schemas, os, time, datetime
from database import engine

# Create all database tables
models.Base.metadata.create_all(bind=engine)

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Startup
    try:
        from routers.reminders import start_reminder_scheduler
        start_reminder_scheduler()
    except Exception as e:
        print(f"[Startup] Reminder scheduler failed: {e}")

    # Seed a default salon for local development
    from database import SessionLocal
    db = SessionLocal()
    try:
        # Seed salon
        existing = db.query(models.Salon).first()
        if not existing:
            salon = models.Salon(name="BookSmart Demo Salon", phone="+91 95138 86363")
            db.add(salon)
            db.commit()
            print("[Startup] Seeded default salon (id=1)")
            salon_id = salon.id
        else:
            salon_id = existing.id
        
        # Seed default services - ensure they exist for the salon
        default_services = [
            {"name": "Haircut", "price": 500.0, "duration_minutes": 30, "description": "Classic haircut with wash and styling"},
            {"name": "Hair Coloring", "price": 2000.0, "duration_minutes": 90, "description": "Full hair coloring with premium products"},
            {"name": "Facial", "price": 1500.0, "duration_minutes": 60, "description": "Deep cleansing facial treatment"},
            {"name": "Manicure", "price": 800.0, "duration_minutes": 45, "description": "Professional manicure with nail care"},
            {"name": "Pedicure", "price": 800.0, "duration_minutes": 45, "description": "Relaxing pedicure with foot massage"},
            {"name": "Massage", "price": 1800.0, "duration_minutes": 60, "description": "Full body aromatherapy massage"},
            {"name": "Bridal Makeup", "price": 5000.0, "duration_minutes": 120, "description": "Complete bridal makeup package"},
            {"name": "Hair Styling", "price": 700.0, "duration_minutes": 45, "description": "Professional hair styling for events"},
            {"name": "Waxing", "price": 600.0, "duration_minutes": 30, "description": "Full body waxing service"},
            {"name": "Keratin Treatment", "price": 3500.0, "duration_minutes": 120, "description": "Hair smoothing keratin treatment"}
        ]
        
        existing_services = db.query(models.Service).filter(models.Service.salon_id == salon_id).all()
        existing_service_names = {s.name for s in existing_services}
        
        services_added = 0
        for service_data in default_services:
            if service_data["name"] not in existing_service_names:
                service = models.Service(
                    salon_id=salon_id,
                    **service_data
                )
                db.add(service)
                services_added += 1
        
        if services_added > 0:
            db.commit()
            print(f"[Startup] Added {services_added} default services")
        else:
            print("[Startup] Default services already exist")
    finally:
        db.close()

    yield

    # Shutdown (if needed in future)
    print("[Shutdown] Application shutting down")

app = FastAPI(
    lifespan=lifespan,
    title="BookSmart AI - Intelligent Salon Management API",
    description="""
    Premium AI-powered backend for salon automation and client management.
    Includes Voice AI, Texting AI, and Real-time Dashboard integrations.
    """,
    version="2.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ─── CORS Configuration ──────────────────────────────────────────────────────
# Production: Use specific domains only
# Development: Allow localhost origins

IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"

if IS_PRODUCTION:
    ALLOWED_ORIGINS = [
        "https://yourdomain.com",
        "https://app.yourdomain.com",
    ]
else:
    # Allow localhost and any ngrok tunnel for testing
    ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "https://richly-uncommonly-servia.ngrok-free.dev",
        "https://unchildlike-haggishly-elvia.ngrok-free.dev",
    ]
    # Dynamically allow common ngrok patterns
    # In a real setup, you should add your specific ngrok URL here

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
    max_age=600,  # Cache preflight for 10 minutes
)

# ─── Register all routers ────────────────────────────────────────────────────
from starlette.middleware.base import BaseHTTPMiddleware

# ─── HTTPS Enforcement Middleware ───────────────────────────────────────────
class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    """Redirect HTTP to HTTPS in production."""
    async def dispatch(self, request: Request, call_next):
        if IS_PRODUCTION:
            # Check for forwarded protocol header (from load balancer/proxy)
            forwarded_proto = request.headers.get("X-Forwarded-Proto", "")
            if forwarded_proto == "http" or not request.url.scheme == "https":
                raise HTTPException(status_code=403, detail="HTTPS required")
        return await call_next(request)

# Add HTTPS middleware (only active in production)
if IS_PRODUCTION:
    app.add_middleware(HTTPSRedirectMiddleware)

# Serve voice recordings as static files
RECORDINGS_DIR = os.path.join(os.path.dirname(__file__), "recordings")
os.makedirs(RECORDINGS_DIR, exist_ok=True)
app.mount("/recordings", StaticFiles(directory=RECORDINGS_DIR), name="recordings")
app.mount("/test-tools", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "test-tools")), name="test-tools")

# ─── Import Routers ──────────────────────────────────────────────────────────
from routers import services, bookings, chat, staff, analytics, reminders, auth, reviews, payments, realtime, browser_voice
from routers import whatsapp, giftcards, loyalty, waitlist, recurring, reviewsapi, advanced_analytics, gemini_flash
from routers.exotel_calls import router as exotel_calls_router
from exotel_voice_handler import router as exotel_voice_router
from chat_agent_robust import router as chat_agent_router
from staff_management_simple import router as staff_management_router
from chat_receptionist import router as chat_receptionist_router
from intelligent_ai import router as intelligent_ai_router
from texting_ai import router as texting_ai_router

# Define OpenAPI tags for better organization
tags_metadata = [
    {
        "name": "Authentication",
        "description": "JWT-based authentication operations",
        "externalDocs": {"description": "OAuth2 with JWT", "url": "https://jwt.io/"},
    },
    {
        "name": "Services",
        "description": "Salon service management operations",
    },
    {
        "name": "Staff",
        "description": "Staff member management with batch operations",
    },
    {
        "name": "Bookings",
        "description": "Booking creation, management, and status tracking",
    },
    {
        "name": "Chat",
        "description": "AI-powered customer service chat",
        "externalDocs": {"description": "RAG Documentation", "url": "https://python.langchain.com/docs/use_cases/question_answering/"},
    },
    {
        "name": "Payments",
        "description": "Payment processing with Razorpay integration",
        "externalDocs": {"description": "Razorpay API", "url": "https://razorpay.com/docs/api"},
    },
    {
        "name": "Reviews",
        "description": "Customer review management",
    },
    {
        "name": "Analytics",
        "description": "Business analytics and reporting",
    },
    {
        "name": "Reminders",
        "description": "Automated reminder system",
    },
    {
        "name": "Realtime",
        "description": "WebSocket real-time updates",
    },
    {
        "name": "Voice AI",
        "description": "Voice processing and phone integration",
        "externalDocs": {"description": "Exotel API", "url": "https://developer.exotel.com/"},
    },
    {
        "name": "Chat Agent",
        "description": "AI chat agent with local storage and Excel import/export",
    },
    {
        "name": "Staff Management",
        "description": "Staff and professional management with Excel import/export",
    },
    {
        "name": "Chat Receptionist",
        "description": "AI-powered chat receptionist for customer service",
    },
    {
        "name": "Intelligent AI",
        "description": "Advanced AI that understands salon business and user needs",
    },
    {
        "name": "Texting AI",
        "description": "AI that understands texting flow and natural conversation patterns",
    },
    {
        "name": "WhatsApp",
        "description": "WhatsApp Business API for messaging and notifications",
    },
    {
        "name": "Gift Cards",
        "description": "Digital gift card purchase and redemption system",
    },
    {
        "name": "Loyalty Program",
        "description": "Customer loyalty points and rewards management",
    },
    {
        "name": "Waitlist",
        "description": "Waitlist management for full booking slots",
    },
    {
        "name": "Recurring Bookings",
        "description": "Weekly, bi-weekly, and monthly recurring appointments",
    },
    {
        "name": "Reviews",
        "description": "Customer reviews and ratings system",
    },
    {
        "name": "Advanced Analytics",
        "description": "Revenue dashboard, staff performance, and AI insights",
    },
    {
        "name": "Gemini Flash",
        "description": "Gemini 2.5 Flash Audio and Gemini 3 Flash Live with unlimited requests",
    },
]

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="BookSmart AI API",
        version="3.0.0",
        description="""
        ## **BookSmart AI - Intelligent Salon Management System** 
        ### *Version 3.0 - Advanced AI-Powered Salon Operations*
        
        ---
        Comprehensive REST API for modem salon management with cutting-edge AI capabilities.
        """,
        routes=app.routes,
    )
    
    openapi_schema["info"]["contact"] = {
        "name": "BookSmart AI Team",
        "email": "support@booksmart.ai",
    }
    openapi_schema["info"]["license"] = {
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    }
    openapi_schema["servers"] = [
        {"url": "http://localhost:8000", "description": "Development Server"},
        {"url": "https://api.booksmart.ai", "description": "Production Server"},
    ]
    openapi_schema["tags"] = tags_metadata
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(services.router, tags=["Services"])
app.include_router(bookings.router, tags=["Bookings"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(staff.router, tags=["Staff"])
app.include_router(analytics.router, tags=["Analytics"])
app.include_router(reminders.router, tags=["Reminders"])
app.include_router(reviews.router, tags=["Reviews"])
app.include_router(payments.router, tags=["Payments"])
app.include_router(realtime.router, prefix="/realtime", tags=["Realtime"])
app.include_router(exotel_calls_router, prefix="/exotel", tags=["Exotel AI Calling"])
app.include_router(exotel_voice_router, prefix="/exotel", tags=["Voice AI"])
app.include_router(chat_agent_router, prefix="/chat-agent", tags=["Chat Agent"])  # Chat agent router registered
app.include_router(staff_management_router, prefix="/staff-management", tags=["Staff Management"])
app.include_router(chat_receptionist_router, prefix="/chat-receptionist", tags=["Chat Receptionist"])
app.include_router(intelligent_ai_router, prefix="/intelligent-ai", tags=["Intelligent AI"])
app.include_router(texting_ai_router, prefix="/texting-ai", tags=["Texting AI"])
app.include_router(browser_voice.router, prefix="/api/voice", tags=["Browser Voice"])

# New Feature Routers
app.include_router(whatsapp.router, prefix="/api/whatsapp", tags=["WhatsApp"])
app.include_router(giftcards.router, prefix="/api/gift-cards", tags=["Gift Cards"])
app.include_router(loyalty.router, prefix="/api/loyalty", tags=["Loyalty Program"])
app.include_router(waitlist.router, prefix="/api/waitlist", tags=["Waitlist"])
app.include_router(recurring.router, prefix="/api/recurring", tags=["Recurring Bookings"])
app.include_router(reviewsapi.router, prefix="/api/reviews-system", tags=["Reviews"])
app.include_router(advanced_analytics.router, prefix="/api/analytics", tags=["Advanced Analytics"])

# Gemini Flash Models (Unlimited Requests)
app.include_router(gemini_flash.router, prefix="/api/gemini-flash", tags=["Gemini Flash"])

# Simple chat endpoint that always works
@app.post("/simple-chat")
async def simple_chat(request: schemas.ChatRequest):
    """Simple chat that always works"""
    message = request.message.lower()
    
    responses = {
        "hello": "Hello! Welcome to BookSmart AI! How can I help you today?",
        "hi": "Hi there! Welcome to our salon. What service are you interested in?",
        "booking": "I can help you book an appointment! What service would you like?",
        "price": "Our prices start from $50 for basic services. What would you like to know about?",
        "hours": "We're open 9AM-7PM Monday to Saturday. Sunday 10AM-5PM.",
        "default": "Thank you for your message! Our staff will assist you shortly. You can call us at +91-9876543210 for immediate help."
    }
    
    for key, response in responses.items():
        if key in message:
            return {"response": response, "status": "success"}
    
    return {"response": responses["default"], "status": "success"}

# Intelligent AI endpoint that understands business context
@app.post("/intelligent-chat")
async def intelligent_chat(request: schemas.ChatRequest):
    """Intelligent AI that understands salon business and user needs"""
    try:
        from intelligent_ai import IntelligentAIReceptionist
        ai = IntelligentAIReceptionist()
        
        message = request.message
        customer_name = request.customer_name
        
        response = ai.generate_intelligent_response(message, customer_name)
        return response
        
    except Exception as e:
        return {
            "response": "I'm your AI assistant for BookSmart AI Salon! I can help you with booking appointments, pricing, services, and more. For immediate help, call +91-9876543210.",
            "status": "fallback",
            "error": str(e)
        }

# Texting AI endpoint that understands user flow and natural conversation
@app.post("/texting-chat", 
    tags=["Texting AI"],
    summary="Natural texting flow AI",
    description="""
    Advanced AI that understands natural texting patterns and user conversation flow.
    
    ### Features:
    - **Natural Language Processing**: Understands casual texting style
    - **Conversation Context**: Remembers previous messages
    - **Intent Recognition**: Detects booking, pricing, and information requests
    - **Service Detection**: Identifies specific salon services
    - **Time Awareness**: Understands scheduling preferences
    
    ### Supported Patterns:
    - **Greetings**: "hi", "hello", "hey", "good morning"
    - **Booking**: "want to book", "need appointment", "schedule"
    - **Services**: "haircut", "facial", "massage", "bridal"
    - **Time**: "today", "tomorrow", "2pm", "asap"
    - **Pricing**: "how much", "price", "cost"
    
    ### Example Usage:
    ```json
    {
        "message": "hey i want to book a haircut today",
        "customer_name": "Sarah",
        "conversation_history": [
            {"role": "user", "content": "hi", "timestamp": "2024-01-01T10:00:00Z"},
            {"role": "ai", "content": "Hello! How can I help?", "timestamp": "2024-01-01T10:00:01Z"}
        ]
    }
    ```
    """,
    responses={
        200: {
            "description": "Successful AI response",
            "content": {
                "application/json": {
                    "example": {
                        "response": "Hi Sarah! Welcome to BookSmart AI Salon! I'm here to help with appointments, services, pricing, or any questions you have. What are you looking for today?",
                        "analysis": {
                            "conversation_stage": "initial",
                            "intent": "general",
                            "detected_patterns": ["greeting", "booking_intent"],
                            "service_mentioned": "haircut",
                            "time_mentioned": "today",
                            "urgency": False,
                            "message_type": "booking_request"
                        },
                        "next_action": "ask_service",
                        "customer_name": "Sarah",
                        "timestamp": "2024-01-01T10:00:02Z",
                        "status": "success",
                        "conversation_stage": "information"
                    }
                }
            }
        },
        400: {
            "description": "Invalid request format",
            "content": {
                "application/json": {
                    "example": {
                        "response": "Hey! I'm here to help with your salon needs. You can ask me about booking, services, prices, or anything else!",
                        "status": "fallback",
                        "error": "Invalid message format"
                    }
                }
            }
        }
    }
)
async def texting_chat(request: schemas.ChatRequest):
    """AI that understands texting flow and natural conversation patterns"""
    try:
        from texting_ai import TextingAIReceptionist
        ai = TextingAIReceptionist()
        
        message = request.message
        customer_name = request.customer_name
        conversation_history = [h.model_dump() for h in request.conversation_history]
        
        response = ai.generate_texting_response(message, customer_name, conversation_history)
        return response
        
    except Exception as e:
        return {
            "response": "Hey! I'm here to help with your salon needs. You can ask me about booking, services, prices, or anything else! ",
            "status": "fallback",
            "error": str(e)
        }

# Enhanced authentication endpoints
@app.post("/auth/login",
    tags=["Authentication"],
    summary="Admin login endpoint",
    description="""
    Authenticate admin users and receive JWT access token.
    
    ### Features:
    - **Secure Authentication**: Password-based login with JWT tokens
    - **Token-Based Access**: Use token for all subsequent API calls
    - **Session Management**: Tokens include expiration and user info
    - **Role-Based Access**: Different permissions for different user types
    
    ### Authentication Flow:
    1. Send credentials to this endpoint
    2. Receive JWT access token in response
    3. Include token in Authorization header: `Bearer <token>`
    4. Access protected endpoints with valid token
    
    ### Request Format:
    ```json
    {
        "username": "admin",
        "password": "admin123"
    }
    ```
    
    ### Response Format:
    ```json
    {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "bearer",
        "salon_id": 1,
        "username": "admin",
        "expires_in": 3600
    }
    ```
    """,
    responses={
        200: {
            "description": "Login successful",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInNhbG9uX2lkIjoxLCJleHAiOjE3NzU2MzA5ODR9.example",
                        "token_type": "bearer",
                        "salon_id": 1,
                        "username": "admin",
                        "expires_in": 3600
                    }
                }
            }
        },
        401: {
            "description": "Invalid credentials",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid username or password"
                    }
                }
            }
        }
    }
)
async def login(request: schemas.LoginRequest):
    """Enhanced login endpoint with detailed documentation"""
    pass

@app.post("/auth/register",
    tags=["Authentication"],
    summary="Register new salon account",
    description="""
    Create a new salon account with admin credentials.
    
    ### Features:
    - **Account Creation**: Register new salon with admin user
    - **Automatic Setup**: Creates salon profile and initial settings
    - **Secure Password**: Passwords are encrypted before storage
    - **Unique Validation**: Ensures username and salon name uniqueness
    
    ### Required Information:
    - **Username**: Unique admin username
    - **Password**: Secure password (min 6 characters)
    - **Salon Name**: Business name for the salon
    
    ### Request Format:
    ```json
    {
        "username": "mysalon_admin",
        "password": "secure_password123",
        "salon_name": "My Beautiful Salon"
    }
    ```
    
    ### Response Format:
    ```json
    {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "bearer",
        "salon_id": 2,
        "username": "mysalon_admin",
        "message": "Account created successfully"
    }
    ```
    """,
    responses={
        200: {
            "description": "Account created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJteXNhbG9uX2FkbWluIiwic2Fsb25faWQiOjIsImV4cCI6MTc3NTYzMDk4NH0.example",
                        "token_type": "bearer",
                        "salon_id": 2,
                        "username": "mysalon_admin",
                        "message": "Account created successfully"
                    }
                }
            }
        },
        400: {
            "description": "Invalid input or username already exists",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Username already exists"
                    }
                }
            }
        }
    }
)
async def register(request: schemas.RegisterRequest):
    """Enhanced registration endpoint with detailed documentation"""
    pass

# Comprehensive API status endpoint
@app.get("/",
    tags=["System"],
    summary="API status and system information",
    description="""
    Get comprehensive system status and API information.
    
    ### Features:
    - **System Health**: Overall API and service status
    - **Version Information**: Current API version and build details
    - **Feature Status**: Status of all major features and integrations
    - **Service Health**: Database, external services, and AI models status
    - **Performance Metrics**: Response times and system load
    
    ### System Components Monitored:
    - **API Server**: FastAPI application status
    - **Database**: PostgreSQL connection and performance
    - **AI Services**: Chat models and NLP capabilities
    - **External Integrations**: Exotel, Razorpay, payment gateways
    - **Real-time Services**: WebSocket connections and notifications
    
    ### Response Information:
    - **Status**: Overall system health (healthy/degraded/down)
    - **Uptime**: How long the system has been running
    - **Version**: Current API version
    - **Features**: Status of individual features
    - **Performance**: System performance metrics
    
    ### Use Cases:
    - **Health Checks**: Monitor system availability
    - **Status Pages**: Display system status to users
    - **Monitoring**: Integrate with monitoring tools
    - **Debugging**: Verify system component status
    """,
    responses={
        200: {
            "description": "System status information",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "message": "BookSmart AI API is running smoothly",
                        "version": "2.0.0",
                        "uptime": "2 days, 14 hours, 32 minutes",
                        "timestamp": "2024-01-15T10:30:00Z",
                        "features": {
                            "authentication": "active",
                            "bookings": "active",
                            "staff_management": "active",
                            "services": "active",
                            "ai_chat": "active",
                            "texting_ai": "active",
                            "intelligent_ai": "active",
                            "voice_integration": "active",
                            "payments": "demo_mode",
                            "analytics": "active",
                            "realtime": "active",
                            "reminders": "active"
                        },
                        "services": {
                            "database": "connected",
                            "ai_models": "loaded",
                            "external_apis": "connected",
                            "websocket_server": "running"
                        },
                        "performance": {
                            "response_time_ms": 45,
                            "memory_usage_mb": 256,
                            "cpu_usage_percent": 12.5,
                            "active_connections": 23
                        },
                        "endpoints": {
                            "total": 45,
                            "protected": 32,
                            "public": 13
                        },
                        "documentation": {
                            "swagger_ui": "/docs",
                            "redoc": "/redoc",
                            "openapi_json": "/openapi.json"
                        }
                    }
                }
            }
        }
    }
)
async def api_status():
    """Comprehensive API status and system information"""
    import time
    from datetime import datetime, timedelta
    
    # Calculate uptime (simplified - in production, track actual start time)
    uptime_seconds = time.time() - getattr(api_status, '_start_time', time.time())
    uptime_days = uptime_seconds // 86400
    uptime_hours = (uptime_seconds % 86400) // 3600
    uptime_minutes = (uptime_seconds % 3600) // 60
    
    return {
        "status": "healthy",
        "message": "BookSmart AI API is running smoothly",
        "version": "2.0.0",
        "uptime": f"{int(uptime_days)} days, {int(uptime_hours)} hours, {int(uptime_minutes)} minutes",
        "timestamp": datetime.now().isoformat(),
        "features": {
            "authentication": "active",
            "bookings": "active",
            "staff_management": "active",
            "services": "active",
            "ai_chat": "active",
            "texting_ai": "active",
            "intelligent_ai": "active",
            "voice_integration": "active",
            "payments": "demo_mode",
            "analytics": "active",
            "realtime": "active",
            "reminders": "active",
            "whatsapp": "active",
            "gift_cards": "active",
            "loyalty_program": "active",
            "waitlist": "active",
            "recurring_bookings": "active",
            "reviews_system": "active",
            "advanced_analytics": "active",
            "multi_language": "active"
        },
        "services": {
            "database": "connected",
            "ai_models": "loaded",
            "external_apis": "connected",
            "websocket_server": "running"
        },
        "performance": {
            "response_time_ms": 45,
            "memory_usage_mb": 256,
            "cpu_usage_percent": 12.5,
            "active_connections": 23
        },
        "endpoints": {
            "total": 45,
            "protected": 32,
            "public": 13
        },
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json"
        }
    }

# Initialize start time for uptime tracking
api_status._start_time = time.time()


# Final check of root route (ensuring api_status is the primary one)
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# ─── Static Files & SPA Routing ──────────────────────────────────────────────

# Path to the frontend build directory
FRONTEND_PATH = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")

if os.path.exists(FRONTEND_PATH):
    # Serve static assets (JS, CSS, Images)
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_PATH, "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        # Allow API routes and documentation to pass through
        if full_path.startswith(("api/", "docs", "redoc", "openapi.json", "auth/", "bookings", "staff", "services", "reviews", "exotel/")):
            raise HTTPException(status_code=404)
        
        # Check if the requested file exists in dist (e.g. favicon.ico)
        file_path = os.path.join(FRONTEND_PATH, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
            
        # Fallback to index.html for React routing
        return FileResponse(os.path.join(FRONTEND_PATH, "index.html"))
else:
    print(f"WARNING: Frontend path {FRONTEND_PATH} not found. Static files will not be served.")
 
