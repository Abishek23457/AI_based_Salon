"""
Recurring Bookings System for BookSmart AI
Manages weekly, bi-weekly, and monthly recurring appointments
"""
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from enum import Enum
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class RecurringFrequency(str, Enum):
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"

class RecurringStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class RecurringBooking(BaseModel):
    id: str
    customer_id: str
    customer_name: str
    customer_phone: str
    customer_email: str
    service_id: str
    service_name: str
    staff_id: str
    staff_name: str
    
    # Recurring settings
    frequency: RecurringFrequency
    day_of_week: int  # 0=Monday, 6=Sunday
    time_slot: str
    start_date: datetime
    end_date: Optional[datetime] = None
    max_occurrences: Optional[int] = None
    
    # Status
    status: RecurringStatus = RecurringStatus.ACTIVE
    occurrences_created: int = 0
    last_created_date: Optional[datetime] = None
    
    created_at: datetime = None
    cancelled_at: Optional[datetime] = None
    cancel_reason: str = ""

class RecurringBookingService:
    """Recurring Bookings Management Service"""
    
    def __init__(self):
        self.recurring_bookings: Dict[str, RecurringBooking] = {}
        self.generated_bookings: List[Dict] = []
    
    def create_recurring_booking(self,
                                customer_id: str,
                                customer_name: str,
                                customer_phone: str,
                                customer_email: str,
                                service_id: str,
                                service_name: str,
                                staff_id: str,
                                staff_name: str,
                                frequency: RecurringFrequency,
                                day_of_week: int,
                                time_slot: str,
                                start_date: datetime,
                                end_date: datetime = None,
                                max_occurrences: int = None) -> RecurringBooking:
        """Create a new recurring booking pattern"""
        
        recurring = RecurringBooking(
            id=str(uuid.uuid4()),
            customer_id=customer_id,
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_email=customer_email,
            service_id=service_id,
            service_name=service_name,
            staff_id=staff_id,
            staff_name=staff_name,
            frequency=frequency,
            day_of_week=day_of_week,
            time_slot=time_slot,
            start_date=start_date,
            end_date=end_date,
            max_occurrences=max_occurrences,
            status=RecurringStatus.ACTIVE,
            created_at=datetime.now()
        )
        
        self.recurring_bookings[recurring.id] = recurring
        
        # Generate first batch of occurrences
        self._generate_occurrences(recurring.id, days_ahead=30)
        
        logger.info(f"[Recurring] Created {frequency} booking for {customer_name}")
        
        return recurring
    
    def _generate_occurrences(self, recurring_id: str, days_ahead: int = 30) -> List[Dict]:
        """Generate individual booking occurrences from recurring pattern"""
        if recurring_id not in self.recurring_bookings:
            return []
        
        recurring = self.recurring_bookings[recurring_id]
        
        if recurring.status != RecurringStatus.ACTIVE:
            return []
        
        # Check limits
        if recurring.max_occurrences and recurring.occurrences_created >= recurring.max_occurrences:
            recurring.status = RecurringStatus.COMPLETED
            return []
        
        if recurring.end_date and datetime.now() > recurring.end_date:
            recurring.status = RecurringStatus.COMPLETED
            return []
        
        occurrences = []
        current_date = recurring.start_date
        
        # Find next occurrence
        if recurring.last_created_date:
            current_date = recurring.last_created_date + timedelta(days=1)
        
        # Generate for the next X days
        end_generation = datetime.now() + timedelta(days=days_ahead)
        
        while current_date <= end_generation:
            # Check if this date matches the pattern
            if self._date_matches_pattern(current_date, recurring):
                # Check if not already created
                if not self._occurrence_exists(recurring_id, current_date):
                    occurrence = {
                        "id": str(uuid.uuid4()),
                        "recurring_id": recurring_id,
                        "customer_id": recurring.customer_id,
                        "customer_name": recurring.customer_name,
                        "service_id": recurring.service_id,
                        "service_name": recurring.service_name,
                        "staff_id": recurring.staff_id,
                        "staff_name": recurring.staff_name,
                        "date": current_date.strftime("%Y-%m-%d"),
                        "time": recurring.time_slot,
                        "status": "scheduled",
                        "created_at": datetime.now().isoformat()
                    }
                    
                    self.generated_bookings.append(occurrence)
                    occurrences.append(occurrence)
                    recurring.occurrences_created += 1
                    
                    # Check max occurrences
                    if recurring.max_occurrences and recurring.occurrences_created >= recurring.max_occurrences:
                        break
            
            current_date += timedelta(days=1)
        
        if occurrences:
            recurring.last_created_date = datetime.now()
            logger.info(f"[Recurring] Generated {len(occurrences)} occurrences for {recurring.customer_name}")
        
        return occurrences
    
    def _date_matches_pattern(self, date: datetime, recurring: RecurringBooking) -> bool:
        """Check if date matches recurring pattern"""
        # Check day of week
        if date.weekday() != recurring.day_of_week:
            return False
        
        # Check start date
        if date < recurring.start_date:
            return False
        
        # Check end date
        if recurring.end_date and date > recurring.end_date:
            return False
        
        # Check frequency
        if recurring.frequency == RecurringFrequency.WEEKLY:
            return True
        
        elif recurring.frequency == RecurringFrequency.BIWEEKLY:
            # Every other week
            weeks_diff = (date - recurring.start_date).days // 7
            return weeks_diff % 2 == 0
        
        elif recurring.frequency == RecurringFrequency.MONTHLY:
            # Same day of month
            return date.day == recurring.start_date.day
        
        return True
    
    def _occurrence_exists(self, recurring_id: str, date: datetime) -> bool:
        """Check if occurrence already exists for date"""
        date_str = date.strftime("%Y-%m-%d")
        return any(
            b["recurring_id"] == recurring_id and b["date"] == date_str 
            for b in self.generated_bookings
        )
    
    def pause_recurring(self, recurring_id: str, reason: str = "") -> bool:
        """Pause recurring bookings"""
        if recurring_id not in self.recurring_bookings:
            return False
        
        recurring = self.recurring_bookings[recurring_id]
        recurring.status = RecurringStatus.PAUSED
        
        logger.info(f"[Recurring] Paused {recurring_id}. Reason: {reason}")
        
        return True
    
    def resume_recurring(self, recurring_id: str) -> bool:
        """Resume paused recurring bookings"""
        if recurring_id not in self.recurring_bookings:
            return False
        
        recurring = self.recurring_bookings[recurring_id]
        recurring.status = RecurringStatus.ACTIVE
        
        # Generate next batch
        self._generate_occurrences(recurring_id, days_ahead=30)
        
        logger.info(f"[Recurring] Resumed {recurring_id}")
        
        return True
    
    def cancel_recurring(self, recurring_id: str, reason: str = "") -> bool:
        """Cancel recurring bookings"""
        if recurring_id not in self.recurring_bookings:
            return False
        
        recurring = self.recurring_bookings[recurring_id]
        recurring.status = RecurringStatus.CANCELLED
        recurring.cancelled_at = datetime.now()
        recurring.cancel_reason = reason
        
        # Cancel all future scheduled occurrences
        for booking in self.generated_bookings:
            if booking["recurring_id"] == recurring_id and booking["status"] == "scheduled":
                booking["status"] = "cancelled"
        
        logger.info(f"[Recurring] Cancelled {recurring_id}. Reason: {reason}")
        
        return True
    
    def update_recurring(self, recurring_id: str, **updates) -> bool:
        """Update recurring booking settings"""
        if recurring_id not in self.recurring_bookings:
            return False
        
        recurring = self.recurring_bookings[recurring_id]
        
        allowed_fields = ["frequency", "day_of_week", "time_slot", "staff_id", "staff_name", "max_occurrences"]
        
        for field, value in updates.items():
            if field in allowed_fields and hasattr(recurring, field):
                setattr(recurring, field, value)
        
        logger.info(f"[Recurring] Updated {recurring_id}")
        
        return True
    
    def get_recurring_bookings(self, customer_id: str = None, status: str = None) -> List[Dict]:
        """Get recurring bookings with optional filters"""
        results = []
        
        for recurring in self.recurring_bookings.values():
            if customer_id and recurring.customer_id != customer_id:
                continue
            if status and recurring.status != status:
                continue
            
            results.append({
                "id": recurring.id,
                "customer_name": recurring.customer_name,
                "service_name": recurring.service_name,
                "staff_name": recurring.staff_name,
                "frequency": recurring.frequency,
                "day_of_week": recurring.day_of_week,
                "time_slot": recurring.time_slot,
                "start_date": recurring.start_date.isoformat(),
                "end_date": recurring.end_date.isoformat() if recurring.end_date else None,
                "max_occurrences": recurring.max_occurrences,
                "occurrences_created": recurring.occurrences_created,
                "status": recurring.status,
                "created_at": recurring.created_at.isoformat()
            })
        
        return results
    
    def get_upcoming_occurrences(self, recurring_id: str = None, days: int = 30) -> List[Dict]:
        """Get upcoming booking occurrences"""
        today = datetime.now().strftime("%Y-%m-%d")
        future = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
        
        results = []
        for booking in self.generated_bookings:
            if recurring_id and booking["recurring_id"] != recurring_id:
                continue
            if booking["status"] != "scheduled":
                continue
            if today <= booking["date"] <= future:
                results.append(booking)
        
        return sorted(results, key=lambda x: x["date"])
    
    def get_stats(self) -> Dict:
        """Get recurring bookings statistics"""
        total = len(self.recurring_bookings)
        active = sum(1 for r in self.recurring_bookings.values() if r.status == RecurringStatus.ACTIVE)
        paused = sum(1 for r in self.recurring_bookings.values() if r.status == RecurringStatus.PAUSED)
        cancelled = sum(1 for r in self.recurring_bookings.values() if r.status == RecurringStatus.CANCELLED)
        completed = sum(1 for r in self.recurring_bookings.values() if r.status == RecurringStatus.COMPLETED)
        
        # Frequency breakdown
        frequencies = {}
        for r in self.recurring_bookings.values():
            freq = r.frequency
            frequencies[freq] = frequencies.get(freq, 0) + 1
        
        # Total occurrences generated
        total_occurrences = len(self.generated_bookings)
        upcoming = len([b for b in self.generated_bookings if b["status"] == "scheduled"])
        
        return {
            "total_patterns": total,
            "active": active,
            "paused": paused,
            "cancelled": cancelled,
            "completed": completed,
            "frequencies": frequencies,
            "total_occurrences_generated": total_occurrences,
            "upcoming_occurrences": upcoming
        }

# Initialize recurring booking service
recurring_service = RecurringBookingService()

# Convenience functions
async def create_weekly_booking(**kwargs):
    """Create weekly recurring booking"""
    return recurring_service.create_recurring_booking(frequency=RecurringFrequency.WEEKLY, **kwargs)

async def create_biweekly_booking(**kwargs):
    """Create bi-weekly recurring booking"""
    return recurring_service.create_recurring_booking(frequency=RecurringFrequency.BIWEEKLY, **kwargs)

async def create_monthly_booking(**kwargs):
    """Create monthly recurring booking"""
    return recurring_service.create_recurring_booking(frequency=RecurringFrequency.MONTHLY, **kwargs)

async def get_customer_recurring_bookings(customer_id: str):
    """Get customer's recurring bookings"""
    return recurring_service.get_recurring_bookings(customer_id=customer_id)

async def get_recurring_stats():
    """Get recurring bookings statistics"""
    return recurring_service.get_stats()
