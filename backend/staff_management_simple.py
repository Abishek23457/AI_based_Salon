"""
Simple Staff Management Test
"""
from fastapi import APIRouter

router = APIRouter(prefix="/staff-management", tags=["Staff Management"])

@router.get("/test")
async def test_endpoint():
    """Test endpoint for staff management"""
    return {"message": "Staff management is working!", "status": "active"}

@router.get("/staff")
async def get_staff():
    """Get all staff members"""
    return {"staff": [], "total": 0, "message": "No staff data yet"}
