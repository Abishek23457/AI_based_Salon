"""
Appointment Reminder Service using APScheduler.
Runs a background job every hour that scans for confirmed bookings
happening within the next 24 hours and sends a reminder SMS.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import datetime
import models
from database import SessionLocal

router = APIRouter(prefix="/reminders", tags=["Reminders"])

# Track which bookings have had reminders sent to avoid duplicates
_sent_reminders: set = set()

def _send_reminders_job():
    """Background job: find upcoming bookings (within 24h) and SMS the customer."""
    db: Session = SessionLocal()
    try:
        now = datetime.datetime.utcnow()
        window_end = now + datetime.timedelta(hours=24)

        upcoming = db.query(models.Booking).filter(
            models.Booking.status == "confirmed",
            models.Booking.appointment_time >= now,
            models.Booking.appointment_time <= window_end,
        ).all()

        for booking in upcoming:
            if booking.id in _sent_reminders:
                continue

            service = db.query(models.Service).filter(
                models.Service.id == booking.service_id
            ).first()
            service_name = service.name if service else "your appointment"

            try:
                from exotel_client import send_reminder_sms
                import asyncio
                asyncio.create_task(send_reminder_sms(
                    to_number=booking.customer_phone,
                    customer_name=booking.customer_name,
                    service=service_name,
                    time=booking.appointment_time.strftime("%d %b %Y at %I:%M %p"),
                ))
                _sent_reminders.add(booking.id)
                print(f"[Reminder] Sent SMS reminder for booking #{booking.id} to {booking.customer_phone}")
            except Exception as e:
                print(f"[Reminder] Failed for booking #{booking.id}: {e}")
    finally:
        db.close()


def start_reminder_scheduler():
    """Call once at app startup to begin the background scheduler."""
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        _send_reminders_job,
        trigger=IntervalTrigger(hours=1),
        id="appointment_reminders",
        replace_existing=True,
        next_run_time=datetime.datetime.utcnow(),  # Run once immediately on startup
    )
    scheduler.start()
    print("[Scheduler] Appointment reminder job started (runs every hour).")
    return scheduler


# Expose a manual trigger endpoint for dashboard use
@router.post("/trigger")
def manually_trigger_reminders():
    """Manually trigger the reminder scan. Useful for testing."""
    _send_reminders_job()
    return {"status": "done", "message": "Reminder scan completed."}
