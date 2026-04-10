import datetime
import re
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import models, schemas
from database import get_db
from routers.bookings import _check_conflicts
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from auth_utils import decode_token

router = APIRouter(tags=["AI Chat"])

class ChatRequest(schemas.BaseModel):
    salon_id: str | None = None
    message: str

class ChatResponse(schemas.BaseModel):
    answer: str

_security_optional = HTTPBearer(auto_error=False)

def _get_optional_user(credentials: HTTPAuthorizationCredentials | None = Depends(_security_optional)) -> dict | None:
    if not credentials:
        return None
    try:
        return decode_token(credentials.credentials)
    except Exception:
        return None

def _parse_datetime_from_message(message: str) -> datetime.datetime | None:
    match = re.search(r"(\d{4}-\d{2}-\d{2})(?:[ T](\d{1,2}:\d{2}))?", message)
    if not match:
        return None

    date_part = match.group(1)
    time_part = match.group(2) or "10:00"
    try:
        return datetime.datetime.strptime(f"{date_part} {time_part}", "%Y-%m-%d %H:%M")
    except ValueError:
        return None

def _parse_phone_from_message(message: str) -> str | None:
    match = re.search(r"(\+?\d[\d\-\s]{8,14}\d)", message)
    if not match:
        return None
    return re.sub(r"[^\d+]", "", match.group(1))

def _parse_name_from_message(message: str) -> str | None:
    match = re.search(r"(?:name\s*(?:is|:)\s*)([a-zA-Z][a-zA-Z\s]{1,40})", message, flags=re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

def _parse_email_from_message(message: str) -> str:
    match = re.search(r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", message)
    return match.group(1) if match else ""

def _find_service_in_message(message: str, services: list[models.Service]) -> models.Service | None:
    lower = message.lower()
    for service in services:
        if service.name.lower() in lower:
            return service
    return None

def _is_booking_intent(message: str) -> bool:
    lower = message.lower()
    keywords = ("book", "booking", "appointment", "reserve", "schedule")
    return any(word in lower for word in keywords)

def _local_assistant_reply(db: Session, salon_id: int, message: str) -> str:
    lower = message.lower()
    services = db.query(models.Service).filter(models.Service.salon_id == salon_id).all()
    if not services:
        services = db.query(models.Service).all()

    if any(k in lower for k in ("service", "price", "cost", "menu", "offer")):
        if not services:
            return "I can help with booking. Please tell me the service, date/time, your name, and phone number."
        summary = ", ".join([f"{s.name} (Rs {int(s.price)})" for s in services[:6]])
        return f"Our available services include: {summary}. To book, share service + date/time + your name + phone."

    if any(k in lower for k in ("hello", "hi", "hey")):
        return "Hi! I can help you book an appointment. Please share service name, date/time (YYYY-MM-DD HH:MM), your name, and phone."

    return "I can help book your session. Please send: service name, date/time (YYYY-MM-DD HH:MM), your name, and phone number."

def _handle_booking_request(db: Session, salon_id: int, message: str) -> str:
    services = db.query(models.Service).filter(models.Service.salon_id == salon_id).all()
    if not services:
        services = db.query(models.Service).all()

    service = _find_service_in_message(message, services)
    appointment_time = _parse_datetime_from_message(message)
    customer_name = _parse_name_from_message(message)
    customer_phone = _parse_phone_from_message(message)
    customer_email = _parse_email_from_message(message)

    missing = []
    if not service:
        missing.append("service name")
    if not appointment_time:
        missing.append("date/time in YYYY-MM-DD HH:MM")
    if not customer_name:
        missing.append("name (example: name is Priya Sharma)")
    if not customer_phone:
        missing.append("phone number")

    if missing:
        service_hint = ", ".join([s.name for s in services[:5]]) if services else "service not configured"
        return (
            "To book your session, I still need: "
            + ", ".join(missing)
            + f". Available services: {service_hint}. "
              "Example: Book Haircut on 2026-04-10 15:30, name is Priya Sharma, phone +919876543210."
        )

    if appointment_time <= datetime.datetime.utcnow():
        return "Please provide a future date/time for booking."

    conflict = _check_conflicts(db, service.id, None, appointment_time)
    if conflict:
        return (
            f"That slot is already occupied by booking #{conflict.id}. "
            "Please share another date/time."
        )

    booking = models.Booking(
        salon_id=salon_id,
        service_id=service.id,
        staff_id=None,
        customer_name=customer_name,
        customer_phone=customer_phone,
        customer_email=customer_email,
        appointment_time=appointment_time,
        status="confirmed",
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)

    return (
        f"Done. Your booking is confirmed (ID #{booking.id}) for {service.name} on "
        f"{appointment_time.strftime('%d %b %Y at %I:%M %p')}."
    )

@router.post("/", response_model=ChatResponse)
def handle_chat(
    req: ChatRequest,
    db: Session = Depends(get_db),
    current_user: dict | None = Depends(_get_optional_user),
):
    # Prefer authenticated user's salon_id (from auth module).
    salon_id: int
    if current_user and "salon_id" in current_user:
        salon_id = int(current_user["salon_id"])
    else:
        try:
            salon_id = int(req.salon_id or "1")
        except ValueError:
            salon_id = 1

    if _is_booking_intent(req.message):
        return {"answer": _handle_booking_request(db, salon_id, req.message)}

    try:
        from llm_chain import execute_chat
        return {"answer": execute_chat(db, salon_id, req.message)}
    except Exception as e:
        print(f"[Chat] Falling back to local assistant due to: {e}")
        return {"answer": _local_assistant_reply(db, salon_id, req.message)}

@router.post("/ingest/{salon_id}")
def trigger_ingestion(salon_id: int, db: Session = Depends(get_db)):
    services_db = db.query(models.Service).filter(models.Service.salon_id == salon_id).all()
    staff_db = db.query(models.Staff).filter(models.Staff.salon_id == salon_id).all()
    
    data = {
        "services": [{"name": s.name, "price": s.price, "duration_minutes": s.duration_minutes, "description": s.description} for s in services_db],
        "staff": [{"name": s.name, "working_hours": s.working_hours} for s in staff_db],
        "policies": "Standard cancellation policy: 24h notice required."
    }
    
    from rag_pipeline import ingest_salon_data
    ingest_salon_data(str(salon_id), data)
    return {"status": "success", "salon_id": salon_id, "documents_indexed": len(services_db) + len(staff_db)}
