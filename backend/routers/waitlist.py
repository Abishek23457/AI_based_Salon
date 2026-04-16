"""
Waitlist API Router for BookSmart AI
API endpoints for waitlist management
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from waitlist_service import waitlist_service, add_customer_to_waitlist, check_waitlist_matches, notify_waitlist_customer

router = APIRouter(prefix="/waitlist", tags=["Waitlist"])

class AddToWaitlistRequest(BaseModel):
    customer_id: str
    customer_name: str
    customer_phone: str
    customer_email: str
    preferred_service: str
    preferred_date_start: datetime
    preferred_date_end: Optional[datetime] = None
    preferred_time_range: str = "any"
    priority: int = 0
    notes: str = ""

class NotifyRequest(BaseModel):
    entry_id: str
    available_slot: dict

@router.post("/add")
async def add_to_waitlist(request: AddToWaitlistRequest):
    """Add customer to waitlist"""
    entry = await add_customer_to_waitlist(
        request.customer_id,
        request.customer_name,
        request.customer_phone,
        request.customer_email,
        request.preferred_service,
        request.preferred_date_start,
        preferred_date_end=request.preferred_date_end,
        preferred_time_range=request.preferred_time_range,
        priority=request.priority,
        notes=request.notes
    )
    return {
        "success": True,
        "waitlist_id": entry.id,
        "position": len([e for e in waitlist_service.waitlist.values() if e.status == "waiting"])
    }

@router.get("/check-matches")
async def check_matches(service: str, date: datetime, time_slot: str):
    """Check for waitlist matches when a slot opens"""
    matches = await check_waitlist_matches(service, date, time_slot)
    return {
        "matches": [
            {
                "id": m.id,
                "customer_name": m.customer_name,
                "customer_phone": m.customer_phone,
                "priority": m.priority,
                "waiting_since": m.created_at.isoformat()
            }
            for m in matches
        ]
    }

@router.post("/notify")
async def notify_customer(request: NotifyRequest):
    """Notify customer about available slot"""
    success = await notify_waitlist_customer(request.entry_id, request.available_slot)
    if success:
        return {"success": True, "message": "Customer notified"}
    raise HTTPException(status_code=400, detail="Failed to notify customer")

@router.get("/entries")
async def get_entries(status: Optional[str] = None, service: Optional[str] = None):
    """Get waitlist entries with optional filters"""
    entries = waitlist_service.get_waitlist(status=status, service=service)
    return {"entries": entries}

@router.get("/{entry_id}/remove")
async def remove_entry(entry_id: str, reason: str = ""):
    """Remove entry from waitlist"""
    success = waitlist_service.remove_from_waitlist(entry_id, reason)
    if success:
        return {"success": True}
    raise HTTPException(status_code=404, detail="Entry not found")

@router.get("/stats")
async def get_stats():
    """Get waitlist statistics"""
    return waitlist_service.get_stats()
