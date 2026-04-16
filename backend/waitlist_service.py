"""
Waitlist Management System for BookSmart AI
Manages customers waiting for available slots
"""
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class WaitlistStatus:
    WAITING = "waiting"
    NOTIFIED = "notified"
    CONVERTED = "converted"  # Successfully booked
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class WaitlistEntry(BaseModel):
    id: str
    customer_id: str
    customer_name: str
    customer_phone: str
    customer_email: str
    preferred_service: str
    preferred_date_start: datetime
    preferred_date_end: Optional[datetime] = None
    preferred_time_range: str  # e.g., "morning", "afternoon", "evening"
    priority: int = 0  # Higher number = higher priority
    status: str = WaitlistStatus.WAITING
    created_at: datetime = None
    notified_at: Optional[datetime] = None
    converted_at: Optional[datetime] = None
    notes: str = ""

class WaitlistService:
    """Waitlist Management Service"""
    
    def __init__(self):
        self.waitlist: Dict[str, WaitlistEntry] = {}
        self.notification_history: List[Dict] = []
    
    def add_to_waitlist(self,
                       customer_id: str,
                       customer_name: str,
                       customer_phone: str,
                       customer_email: str,
                       preferred_service: str,
                       preferred_date_start: datetime,
                       preferred_date_end: datetime = None,
                       preferred_time_range: str = "any",
                       priority: int = 0,
                       notes: str = "") -> WaitlistEntry:
        """Add customer to waitlist"""
        
        entry = WaitlistEntry(
            id=str(uuid.uuid4()),
            customer_id=customer_id,
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_email=customer_email,
            preferred_service=preferred_service,
            preferred_date_start=preferred_date_start,
            preferred_date_end=preferred_date_end or preferred_date_start + timedelta(days=7),
            preferred_time_range=preferred_time_range,
            priority=priority,
            status=WaitlistStatus.WAITING,
            created_at=datetime.now(),
            notes=notes
        )
        
        self.waitlist[entry.id] = entry
        logger.info(f"[Waitlist] Added {customer_name} for {preferred_service}")
        
        return entry
    
    def find_matches_for_slot(self, service: str, date: datetime, time_slot: str) -> List[WaitlistEntry]:
        """Find waitlist entries matching an available slot"""
        matches = []
        
        for entry in self.waitlist.values():
            if entry.status != WaitlistStatus.WAITING:
                continue
            
            # Check if entry is expired (older than 30 days)
            if datetime.now() - entry.created_at > timedelta(days=30):
                entry.status = WaitlistStatus.EXPIRED
                continue
            
            # Check service match
            if entry.preferred_service != service and entry.preferred_service != "any":
                continue
            
            # Check date range
            if not (entry.preferred_date_start <= date <= entry.preferred_date_end):
                continue
            
            # Check time range preference
            if not self._time_matches_preference(time_slot, entry.preferred_time_range):
                continue
            
            matches.append(entry)
        
        # Sort by priority (high to low) and creation date (oldest first)
        matches.sort(key=lambda x: (-x.priority, x.created_at))
        
        return matches
    
    def _time_matches_preference(self, time_slot: str, preference: str) -> bool:
        """Check if time slot matches customer's time preference"""
        if preference == "any":
            return True
        
        try:
            hour = int(time_slot.split(":")[0])
            
            time_ranges = {
                "morning": (8, 12),
                "afternoon": (12, 17),
                "evening": (17, 21),
                "early_morning": (6, 10),
                "late_evening": (19, 22)
            }
            
            if preference in time_ranges:
                start, end = time_ranges[preference]
                return start <= hour < end
        except:
            pass
        
        return True
    
    def notify_customer(self, entry_id: str, available_slot: dict) -> bool:
        """Notify customer about available slot"""
        if entry_id not in self.waitlist:
            return False
        
        entry = self.waitlist[entry_id]
        
        if entry.status != WaitlistStatus.WAITING:
            return False
        
        entry.status = WaitlistStatus.NOTIFIED
        entry.notified_at = datetime.now()
        
        # Record notification
        self.notification_history.append({
            "entry_id": entry_id,
            "customer_name": entry.customer_name,
            "slot": available_slot,
            "notified_at": entry.notified_at.isoformat()
        })
        
        logger.info(f"[Waitlist] Notified {entry.customer_name} about available slot")
        
        return True
    
    def convert_to_booking(self, entry_id: str, booking_ref: str) -> bool:
        """Mark waitlist entry as converted to booking"""
        if entry_id not in self.waitlist:
            return False
        
        entry = self.waitlist[entry_id]
        entry.status = WaitlistStatus.CONVERTED
        entry.converted_at = datetime.now()
        
        logger.info(f"[Waitlist] Entry {entry_id} converted to booking {booking_ref}")
        
        return True
    
    def remove_from_waitlist(self, entry_id: str, reason: str = "") -> bool:
        """Remove entry from waitlist"""
        if entry_id not in self.waitlist:
            return False
        
        entry = self.waitlist[entry_id]
        entry.status = WaitlistStatus.CANCELLED
        
        logger.info(f"[Waitlist] Removed {entry.customer_name}. Reason: {reason}")
        
        return True
    
    def get_waitlist(self, status: str = None, service: str = None) -> List[Dict]:
        """Get waitlist entries with optional filters"""
        entries = []
        
        for entry in self.waitlist.values():
            if status and entry.status != status:
                continue
            if service and entry.preferred_service != service:
                continue
            
            entries.append({
                "id": entry.id,
                "customer_name": entry.customer_name,
                "customer_phone": entry.customer_phone,
                "preferred_service": entry.preferred_service,
                "preferred_date_start": entry.preferred_date_start.isoformat(),
                "preferred_date_end": entry.preferred_date_end.isoformat(),
                "preferred_time_range": entry.preferred_time_range,
                "priority": entry.priority,
                "status": entry.status,
                "created_at": entry.created_at.isoformat(),
                "waiting_days": (datetime.now() - entry.created_at).days
            })
        
        # Sort by priority and creation date
        entries.sort(key=lambda x: (-x["priority"], x["created_at"]))
        
        return entries
    
    def get_stats(self) -> Dict:
        """Get waitlist statistics"""
        total = len(self.waitlist)
        waiting = sum(1 for e in self.waitlist.values() if e.status == WaitlistStatus.WAITING)
        notified = sum(1 for e in self.waitlist.values() if e.status == WaitlistStatus.NOTIFIED)
        converted = sum(1 for e in self.waitlist.values() if e.status == WaitlistStatus.CONVERTED)
        expired = sum(1 for e in self.waitlist.values() if e.status == WaitlistStatus.EXPIRED)
        
        # Service breakdown
        services = {}
        for entry in self.waitlist.values():
            if entry.status == WaitlistStatus.WAITING:
                svc = entry.preferred_service
                services[svc] = services.get(svc, 0) + 1
        
        return {
            "total_entries": total,
            "waiting": waiting,
            "notified": notified,
            "converted": converted,
            "expired": expired,
            "conversion_rate": (converted / total * 100) if total > 0 else 0,
            "services_waiting": services,
            "average_wait_days": sum(
                (datetime.now() - e.created_at).days 
                for e in self.waitlist.values() 
                if e.status == WaitlistStatus.WAITING
            ) / waiting if waiting > 0 else 0
        }

# Initialize waitlist service
waitlist_service = WaitlistService()

# Convenience functions
async def add_customer_to_waitlist(customer_id: str, customer_name: str, customer_phone: str,
                                   customer_email: str, preferred_service: str,
                                   preferred_date_start: datetime, **kwargs):
    """Add customer to waitlist"""
    return waitlist_service.add_to_waitlist(
        customer_id, customer_name, customer_phone, customer_email,
        preferred_service, preferred_date_start, **kwargs
    )

async def check_waitlist_matches(service: str, date: datetime, time_slot: str):
    """Find waitlist matches for available slot"""
    return waitlist_service.find_matches_for_slot(service, date, time_slot)

async def notify_waitlist_customer(entry_id: str, available_slot: dict):
    """Notify customer about available slot"""
    return waitlist_service.notify_customer(entry_id, available_slot)

async def get_waitlist_stats():
    """Get waitlist statistics"""
    return waitlist_service.get_stats()
