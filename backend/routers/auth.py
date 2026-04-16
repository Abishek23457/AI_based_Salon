"""
Authentication router: login, register, and token validation.
Provides JWT-based authentication for admin users.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
import models
from database import get_db
from auth_utils import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter()


class RegisterRequest(BaseModel):
    username: str
    password: str
    salon_name: str


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    salon_id: int
    username: str


@router.post("/register", 
    response_model=TokenResponse,
    summary="Register new admin user",
    description="Create a new admin account and salon. Returns JWT token for immediate authentication.",
    responses={
        200: {"description": "User registered successfully", "model": TokenResponse},
        400: {"description": "Username already taken"}
    }
)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new admin user + salon."""
    existing = db.query(models.AdminUser).filter(models.AdminUser.username == body.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")

    # Create salon
    salon = models.Salon(name=body.salon_name, phone="")
    db.add(salon)
    db.commit()
    db.refresh(salon)

    # Create admin user
    user = models.AdminUser(
        username=body.username,
        password_hash=hash_password(body.password),
        salon_id=salon.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.username, "salon_id": salon.id})
    return TokenResponse(access_token=token, salon_id=salon.id, username=user.username)


@router.post("/login", 
    response_model=TokenResponse,
    summary="Login with credentials",
    description="Authenticate with username and password. Returns JWT token for API access.",
    responses={
        200: {"description": "Login successful", "model": TokenResponse},
        401: {"description": "Invalid credentials"}
    }
)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    """Login with username and password."""
    user = db.query(models.AdminUser).filter(models.AdminUser.username == body.username).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.username, "salon_id": user.salon_id})
    return TokenResponse(access_token=token, salon_id=user.salon_id, username=user.username)


@router.get("/me", 
    summary="Get current user info",
    description="Validate JWT token and return current user information. Requires Authorization header.",
    responses={
        200: {"description": "Token is valid"},
        401: {"description": "Invalid or expired token"}
    }
)
def get_me(current_user: dict = Depends(get_current_user)):
    """Validate token and return current user info."""
    return {"username": current_user["sub"], "salon_id": current_user["salon_id"]}
