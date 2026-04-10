from pydantic import BaseModel, EmailStr, constr, ConfigDict
from typing import List, Optional
from enum import Enum
import datetime


# ─── ENUM DEFINITIONS ─────────────────────────────────────────────

class BookingStatus(str, Enum):
    confirmed = "confirmed"
    cancelled = "cancelled"
    completed = "completed"
    pending = "pending"


class ChatRole(str, Enum):
    user = "user"
    assistant = "assistant"
    system = "system"


class CallDirection(str, Enum):
    incoming = "incoming"
    outgoing = "outgoing"


class CallStatus(str, Enum):
    initiated = "initiated"
    ringing = "ringing"
    in_progress = "in-progress"
    completed = "completed"
    failed = "failed"
    transferred = "transferred"


# ─── SERVICE SCHEMAS ─────────────────────────────────────────────

class ServiceBase(BaseModel):
    name: str
    duration_minutes: int
    price: float
    description: Optional[str] = None


class ServiceCreate(ServiceBase):
    pass


class Service(ServiceBase):
    id: int
    salon_id: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)


# ─── STAFF SCHEMAS ─────────────────────────────────────────────

class StaffBase(BaseModel):
    name: str
    working_hours: str


class StaffCreate(StaffBase):
    pass


class Staff(StaffBase):
    id: int
    salon_id: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)


# ─── BOOKING SCHEMAS ─────────────────────────────────────────────

class BookingBase(BaseModel):
    customer_name: str
    customer_phone: constr(pattern=r'^\+?[0-9]{10,15}$')
    customer_email: Optional[EmailStr] = None
    appointment_time: datetime.datetime
    service_id: int
    staff_id: Optional[int] = None


class BookingCreate(BookingBase):
    pass


class Booking(BookingBase):
    id: int
    status: BookingStatus
    salon_id: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)


# ─── CHAT / AI SCHEMAS ─────────────────────────────────────────────

class ChatHistoryItem(BaseModel):
    role: ChatRole
    content: str
    timestamp: Optional[str] = None


class ChatRequest(BaseModel):
    message: str
    customer_name: Optional[str] = "Customer"
    conversation_history: Optional[List[ChatHistoryItem]] = []


# ─── AUTH SCHEMAS ─────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    salon_name: str
