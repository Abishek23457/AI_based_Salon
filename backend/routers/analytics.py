from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any
import models
from database import get_db

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/{salon_id}")
def get_analytics(salon_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Returns business analytics for a given salon."""

    # --- Booking Counts ---
    total_bookings = db.query(models.Booking).filter(
        models.Booking.salon_id == salon_id
    ).count()

    confirmed_bookings = db.query(models.Booking).filter(
        models.Booking.salon_id == salon_id,
        models.Booking.status == "confirmed"
    ).count()

    cancelled_bookings = db.query(models.Booking).filter(
        models.Booking.salon_id == salon_id,
        models.Booking.status == "cancelled"
    ).count()

    # --- Revenue: sum price of all confirmed bookings ---
    confirmed_booking_ids = db.query(models.Booking.service_id).filter(
        models.Booking.salon_id == salon_id,
        models.Booking.status == "confirmed"
    ).all()

    total_revenue = 0.0
    for (service_id,) in confirmed_booking_ids:
        svc = db.query(models.Service).filter(models.Service.id == service_id).first()
        if svc:
            total_revenue += svc.price

    # --- Top Services by booking count ---
    service_rows = db.query(
        models.Booking.service_id,
        func.count(models.Booking.id).label("count")
    ).filter(
        models.Booking.salon_id == salon_id,
        models.Booking.status != "cancelled"
    ).group_by(models.Booking.service_id).order_by(func.count(models.Booking.id).desc()).limit(3).all()

    top_services = []
    for service_id, count in service_rows:
        svc = db.query(models.Service).filter(models.Service.id == service_id).first()
        if svc:
            top_services.append({"name": svc.name, "bookings": count, "price": svc.price})

    # --- Staff count ---
    staff_count = db.query(models.Staff).filter(models.Staff.salon_id == salon_id).count()

    return {
        "salon_id": salon_id,
        "total_bookings": total_bookings,
        "confirmed_bookings": confirmed_bookings,
        "cancelled_bookings": cancelled_bookings,
        "total_revenue": round(total_revenue, 2),
        "staff_count": staff_count,
        "top_services": top_services,
    }

@router.get("/{salon_id}/call-logs")
def get_call_logs(salon_id: int, db: Session = Depends(get_db)):
    """Returns recent voice call logs for the salon."""
    logs = db.query(models.CallLog).filter(
        models.CallLog.salon_id == salon_id
    ).order_by(models.CallLog.created_at.desc()).limit(20).all()
    return logs
