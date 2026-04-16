"""
Recurring Bookings API Router for BookSmart AI
API endpoints for recurring appointment management
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from recurring_bookings import recurring_service, create_weekly_booking, create_biweekly_booking, create_monthly_booking

router = APIRouter(prefix="/recurring", tags=["Recurring Bookings"])

class CreateRecurringRequest(BaseModel):
    customer_id: str
    customer_name: str
    customer_phone: str
    customer_email: str
    service_id: str
    service_name: str
    staff_id: str
    staff_name: str
    frequency: str  # weekly, biweekly, monthly
    day_of_week: int  # 0-6 (Monday-Sunday)
    time_slot: str
    start_date: datetime
    end_date: Optional[datetime] = None
    max_occurrences: Optional[int] = None

class UpdateRecurringRequest(BaseModel):
    frequency: Optional[str] = None
    day_of_week: Optional[int] = None
    time_slot: Optional[str] = None
    staff_id: Optional[str] = None
    staff_name: Optional[str] = None
    max_occurrences: Optional[int] = None

@router.post("/create")
async def create_recurring(request: CreateRecurringRequest):
    """Create recurring booking pattern"""
    if request.frequency == "weekly":
        recurring = await create_weekly_booking(**request.model_dump())
    elif request.frequency == "biweekly":
        recurring = await create_biweekly_booking(**request.model_dump())
    elif request.frequency == "monthly":
        recurring = await create_monthly_booking(**request.model_dump())
    else:
        raise HTTPException(status_code=400, detail="Invalid frequency")
    
    return {
        "success": True,
        "recurring_id": recurring.id,
        "frequency": recurring.frequency,
        "occurrences_created": recurring.occurrences_created
    }

@router.get("/customer/{customer_id}")
async def get_customer_recurring(customer_id: str):
    """Get customer's recurring bookings"""
    bookings = recurring_service.get_recurring_bookings(customer_id=customer_id)
    return {"recurring_bookings": bookings}

@router.get("/{recurring_id}/occurrences")
async def get_occurrences(recurring_id: str, days: int = 30):
    """Get upcoming occurrences for a recurring booking"""
    occurrences = recurring_service.get_upcoming_occurrences(recurring_id, days)
    return {"occurrences": occurrences}

@router.post("/{recurring_id}/pause")
async def pause_recurring(recurring_id: str, reason: str = ""):
    """Pause recurring bookings"""
    success = recurring_service.pause_recurring(recurring_id, reason)
    if success:
        return {"success": True, "message": "Recurring bookings paused"}
    raise HTTPException(status_code=404, detail="Recurring booking not found")

@router.post("/{recurring_id}/resume")
async def resume_recurring(recurring_id: str):
    """Resume paused recurring bookings"""
    success = recurring_service.resume_recurring(recurring_id)
    if success:
        return {"success": True, "message": "Recurring bookings resumed"}
    raise HTTPException(status_code=404, detail="Recurring booking not found")

@router.post("/{recurring_id}/cancel")
async def cancel_recurring(recurring_id: str, reason: str = ""):
    """Cancel recurring bookings"""
    success = recurring_service.cancel_recurring(recurring_id, reason)
    if success:
        return {"success": True, "message": "Recurring bookings cancelled"}
    raise HTTPException(status_code=404, detail="Recurring booking not found")

@router.put("/{recurring_id}")
async def update_recurring(recurring_id: str, request: UpdateRecurringRequest):
    """Update recurring booking settings"""
    updates = {k: v for k, v in request.model_dump().items() if v is not None}
    success = recurring_service.update_recurring(recurring_id, **updates)
    if success:
        return {"success": True, "message": "Recurring booking updated"}
    raise HTTPException(status_code=404, detail="Recurring booking not found")

@router.get("/stats")
async def get_stats():
    """Get recurring bookings statistics"""
    return recurring_service.get_stats()
