from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
import models, schemas
from database import get_db

router = APIRouter(prefix="/staff", tags=["Staff"])

@router.get("/", response_model=list[schemas.Staff])
def list_staff(salon_id: int = 1, db: Session = Depends(get_db)):
    return db.query(models.Staff).filter(models.Staff.salon_id == salon_id).all()

@router.get("/count", response_model=Dict[str, Any])
def get_staff_count(salon_id: int = 1, db: Session = Depends(get_db)):
    """Get current staff count and statistics"""
    total_count = db.query(models.Staff).filter(models.Staff.salon_id == salon_id).count()
    
    # Get active staff (with upcoming bookings)
    active_staff = db.query(models.Staff).filter(
        models.Staff.salon_id == salon_id
    ).join(models.Booking).filter(
        models.Booking.appointment_time > func.now(),
        models.Booking.status == "confirmed"
    ).distinct().count()
    
    return {
        "total_count": total_count,
        "active_count": active_staff,
        "available_count": total_count - active_staff
    }

@router.post("/", response_model=schemas.Staff)
def create_staff(payload: schemas.StaffCreate, salon_id: int = 1, db: Session = Depends(get_db)):
    # Check if staff member with same name already exists
    existing = db.query(models.Staff).filter(
        models.Staff.salon_id == salon_id,
        models.Staff.name == payload.name
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Staff member with this name already exists")
    
    s = models.Staff(salon_id=salon_id, **payload.model_dump())
    db.add(s)
    db.commit()
    db.refresh(s)
    
    # Auto-ingest new staff data into AI
    try:
        from rag_pipeline import ingest_salon_data
        services_db = db.query(models.Service).filter(models.Service.salon_id == salon_id).all()
        staff_db = db.query(models.Staff).filter(models.Staff.salon_id == salon_id).all()
        
        data = {
            "services": [{"name": svc.name, "price": svc.price, "duration_minutes": svc.duration_minutes, "description": svc.description or "Professional service"} for svc in services_db],
            "staff": [{"name": stf.name, "working_hours": stf.working_hours} for stf in staff_db],
            "policies": "Standard cancellation policy: 24h notice required. Late cancellations may incur a fee. Walk-ins welcome based on availability."
        }
        ingest_salon_data(str(salon_id), data)
    except Exception as e:
        print(f"Could not update AI index: {e}")
    
    return s

@router.put("/{staff_id}", response_model=schemas.Staff)
def update_staff(staff_id: int, staff: schemas.StaffCreate, db: Session = Depends(get_db)):
    """Update staff member details"""
    db_staff = db.query(models.Staff).filter(models.Staff.id == staff_id).first()
    if not db_staff:
        raise HTTPException(status_code=404, detail="Staff member not found")
    
    db_staff.name = staff.name
    db_staff.working_hours = staff.working_hours
    db.commit()
    db.refresh(db_staff)
    return db_staff

@router.delete("/{staff_id}")
def delete_staff(staff_id: int, db: Session = Depends(get_db)):
    """Remove a staff member"""
    db_staff = db.query(models.Staff).filter(models.Staff.id == staff_id).first()
    if not db_staff:
        raise HTTPException(status_code=404, detail="Staff member not found")
    
    # Check if staff has upcoming bookings
    upcoming_bookings = db.query(models.Booking).filter(
        models.Booking.staff_id == staff_id,
        models.Booking.appointment_time > func.now(),
        models.Booking.status == "confirmed"
    ).count()
    
    if upcoming_bookings > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete staff member with {upcoming_bookings} upcoming bookings"
        )
    
    db.delete(db_staff)
    db.commit()
    
    # Update AI index after deletion
    try:
        from rag_pipeline import ingest_salon_data
        salon_id = db_staff.salon_id
        services_db = db.query(models.Service).filter(models.Service.salon_id == salon_id).all()
        staff_db = db.query(models.Staff).filter(models.Staff.salon_id == salon_id).all()
        
        data = {
            "services": [{"name": s.name, "price": s.price, "duration_minutes": s.duration_minutes, "description": s.description or "Professional service"} for s in services_db],
            "staff": [{"name": s.name, "working_hours": s.working_hours} for s in staff_db],
            "policies": "Standard cancellation policy: 24h notice required. Late cancellations may incur a fee. Walk-ins welcome based on availability."
        }
        ingest_salon_data(str(salon_id), data)
    except Exception as e:
        print(f"Could not update AI index: {e}")
    
    return {"message": f"Staff member {staff_id} deleted successfully"}

@router.post("/batch-update")
def batch_update_staff_count(action: str, count: int, salon_id: int = 1, db: Session = Depends(get_db)):
    """Batch add or remove staff members"""
    if action not in ["add", "remove"]:
        raise HTTPException(status_code=400, detail="Action must be 'add' or 'remove'")
    
    if count <= 0:
        raise HTTPException(status_code=400, detail="Count must be greater than 0")
    
    current_staff = db.query(models.Staff).filter(models.Staff.salon_id == salon_id).all()
    
    if action == "remove":
        if len(current_staff) < count:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot remove {count} staff members. Only {len(current_staff)} available"
            )
        
        # Remove staff with no upcoming bookings first
        removable_staff = []
        for staff in current_staff:
            upcoming = db.query(models.Booking).filter(
                models.Booking.staff_id == staff.id,
                models.Booking.appointment_time > func.now(),
                models.Booking.status == "confirmed"
            ).count()
            
            if upcoming == 0:
                removable_staff.append(staff)
        
        if len(removable_staff) < count:
            raise HTTPException(
                status_code=400,
                detail=f"Only {len(removable_staff)} staff members can be safely removed (no upcoming bookings)"
            )
        
        # Remove the specified number of staff
        for i in range(count):
            db.delete(removable_staff[i])
        
        db.commit()
        
        message = f"Successfully removed {count} staff members"
    
    else:  # add
        # Add new staff members with default details
        for i in range(count):
            new_staff = models.Staff(
                salon_id=salon_id,
                name=f"Staff Member {len(current_staff) + i + 1}",
                working_hours="9:00 AM - 6:00 PM"
            )
            db.add(new_staff)
        
        db.commit()
        message = f"Successfully added {count} new staff members"
    
    # Update AI index
    try:
        from rag_pipeline import ingest_salon_data
        services_db = db.query(models.Service).filter(models.Service.salon_id == salon_id).all()
        staff_db = db.query(models.Staff).filter(models.Staff.salon_id == salon_id).all()
        
        data = {
            "services": [{"name": s.name, "price": s.price, "duration_minutes": s.duration_minutes, "description": s.description or "Professional service"} for s in services_db],
            "staff": [{"name": s.name, "working_hours": s.working_hours} for s in staff_db],
            "policies": "Standard cancellation policy: 24h notice required. Late cancellations may incur a fee. Walk-ins welcome based on availability."
        }
        ingest_salon_data(str(salon_id), data)
    except Exception as e:
        print(f"Could not update AI index: {e}")
    
    return {"message": message, "action": action, "count": count}
