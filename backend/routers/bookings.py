"""
Bookings router with:
- Booking conflict detection (Enhancement #4)
- Email notifications on booking creation (Enhancement #7)
- Real-time WebSocket broadcast on booking events (Enhancement #8)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import datetime
import models, schemas
from database import get_db

router = APIRouter(prefix="/bookings", tags=["Bookings"])


def _check_conflicts(db: Session, service_id: int, staff_id: int | None, appointment_time: datetime.datetime, exclude_id: int | None = None):
    """Check if the requested time slot conflicts with existing bookings."""
    service = db.query(models.Service).filter(models.Service.id == service_id).first()
    duration = service.duration_minutes if service else 60

    new_start = appointment_time
    new_end = appointment_time + datetime.timedelta(minutes=duration)

    # Find all confirmed bookings that could overlap
    query = db.query(models.Booking).filter(
        models.Booking.status == "confirmed",
    )
    if staff_id:
        query = query.filter(models.Booking.staff_id == staff_id)

    if exclude_id:
        query = query.filter(models.Booking.id != exclude_id)

    existing_bookings = query.all()

    for booking in existing_bookings:
        b_service = db.query(models.Service).filter(models.Service.id == booking.service_id).first()
        b_duration = b_service.duration_minutes if b_service else 60
        b_start = booking.appointment_time
        b_end = b_start + datetime.timedelta(minutes=b_duration)

        # Overlap check: new booking starts before existing ends AND new booking ends after existing starts
        if new_start < b_end and new_end > b_start:
            return booking

    return None


@router.post("/", response_model=schemas.Booking)
def create_booking(booking: schemas.BookingCreate, db: Session = Depends(get_db)):
    service = db.query(models.Service).filter(models.Service.id == booking.service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    # ── Conflict Detection ───────────────────────────────────
    conflict = _check_conflicts(db, booking.service_id, booking.staff_id, booking.appointment_time)
    if conflict:
        raise HTTPException(
            status_code=409,
            detail=f"Time slot conflict: an existing booking (#{conflict.id}) for {conflict.customer_name} overlaps with this time. Please choose a different time."
        )

    db_booking = models.Booking(**booking.model_dump())
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)

    # ── SMS Notification ─────────────────────────────────────
    try:
        from exotel_client import send_booking_sms
        import asyncio
        asyncio.create_task(send_booking_sms(booking.customer_phone, booking.customer_name, service.name, str(booking.appointment_time)))
    except Exception as e:
        print("Could not send SMS: ", e)

    # ── Email Notification ───────────────────────────────────
    if booking.customer_email:
        try:
            from email_client import send_booking_email
            send_booking_email(
                to_email=booking.customer_email,
                customer_name=booking.customer_name,
                service_name=service.name,
                appointment_time=booking.appointment_time.strftime("%d %b %Y at %I:%M %p"),
            )
        except Exception as e:
            print(f"Could not send email: {e}")

    # ── Real-time Broadcast ──────────────────────────────────
    try:
        from routers.realtime import broadcast_sync
        broadcast_sync("new_booking", {
            "id": db_booking.id,
            "customer_name": db_booking.customer_name,
            "service": service.name,
            "time": str(db_booking.appointment_time),
        })
    except Exception:
        pass

    return db_booking


@router.get("/", response_model=List[schemas.Booking])
def get_bookings(salon_id: int = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    query = db.query(models.Booking).order_by(models.Booking.id.desc())
    if salon_id:
        query = query.filter(models.Booking.salon_id == salon_id)
    return query.offset(skip).limit(limit).all()

@router.get("/check-availability")
def check_availability(service_id: int, appointment_time: str, salon_id: int = None, db: Session = Depends(get_db)):
    """Check if a time slot is available for booking"""
    from datetime import datetime, timedelta
    
    try:
        appt_time = datetime.fromisoformat(appointment_time.replace('Z', '+00:00'))
    except:
        raise HTTPException(status_code=400, detail="Invalid appointment time format")
    
    # Get service duration
    service = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    duration = service.duration_minutes or 30
    end_time = appt_time + timedelta(minutes=duration)
    
    # Check for conflicting bookings
    query = db.query(models.Booking).filter(
        models.Booking.service_id == service_id,
        models.Booking.status != "cancelled"
    )
    
    if salon_id:
        query = query.filter(models.Booking.salon_id == salon_id)
    
    # Check for overlapping time slots
    conflicts = []
    existing_bookings = query.all()
    
    for booking in existing_bookings:
        booking_time = booking.appointment_time
        booking_end = booking_time + timedelta(minutes=booking.service.duration_minutes or 30)
        
        # Check if time ranges overlap
        if (appt_time < booking_end) and (end_time > booking_time):
            conflicts.append({
                "booking_id": booking.id,
                "time": str(booking_time),
                "customer": booking.customer_name
            })
    
    return {
        "available": len(conflicts) == 0,
        "conflicts": conflicts,
        "requested_time": str(appt_time),
        "end_time": str(end_time),
        "service": service.name,
        "duration_minutes": duration
    }


@router.get("/{booking_id}", response_model=schemas.Booking)
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking


@router.patch("/{booking_id}/cancel", response_model=schemas.Booking)
def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.status == "cancelled":
        raise HTTPException(status_code=400, detail="Booking is already cancelled")
    booking.status = "cancelled"
    db.commit()
    db.refresh(booking)

    # ── Real-time Broadcast ──────────────────────────────────
    try:
        from routers.realtime import broadcast_sync
        broadcast_sync("booking_cancelled", {"id": booking.id, "customer_name": booking.customer_name})
    except Exception:
        pass

    return booking


class RescheduleRequest(schemas.BaseModel):
    appointment_time: datetime.datetime


@router.patch("/{booking_id}/reschedule", response_model=schemas.Booking)
def reschedule_booking(booking_id: int, body: RescheduleRequest, db: Session = Depends(get_db)):
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.status == "cancelled":
        raise HTTPException(status_code=400, detail="Cannot reschedule a cancelled booking")
    if body.appointment_time <= datetime.datetime.utcnow():
        raise HTTPException(status_code=400, detail="New appointment time must be in the future")

    # ── Conflict Detection on reschedule ─────────────────────
    conflict = _check_conflicts(db, booking.service_id, booking.staff_id, body.appointment_time, exclude_id=booking.id)
    if conflict:
        raise HTTPException(
            status_code=409,
            detail=f"Time slot conflict: an existing booking (#{conflict.id}) overlaps with this new time."
        )

    booking.appointment_time = body.appointment_time
    db.commit()
    db.refresh(booking)
    return booking
