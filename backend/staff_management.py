"""
Staff and Professional Management with Excel Import/Export
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel
import models
from database import get_db

router = APIRouter(prefix="/staff-management", tags=["Staff Management"])

# Local storage files
STAFF_DATA_FILE = "staff_data.json"
PROFESSIONAL_DATA_FILE = "professional_data.json"

# Pydantic models for data validation
class StaffCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    role: str
    specialization: Optional[str] = None
    working_hours: Optional[str] = None
    salary: Optional[float] = None
    hire_date: Optional[str] = None

class ProfessionalCreate(BaseModel):
    name: str
    profession: str
    experience_years: Optional[int] = None
    certifications: Optional[str] = None
    specialties: Optional[str] = None
    hourly_rate: Optional[float] = None
    availability: Optional[str] = None
    contact_info: Optional[str] = None

def load_staff_data() -> List[Dict]:
    """Load staff data from local storage"""
    try:
        if os.path.exists(STAFF_DATA_FILE):
            with open(STAFF_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error loading staff data: {e}")
        return []

def save_staff_data(data: List[Dict]):
    """Save staff data to local storage"""
    try:
        with open(STAFF_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving staff data: {e}")

def load_professional_data() -> List[Dict]:
    """Load professional data from local storage"""
    try:
        if os.path.exists(PROFESSIONAL_DATA_FILE):
            with open(PROFESSIONAL_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error loading professional data: {e}")
        return []

def save_professional_data(data: List[Dict]):
    """Save professional data to local storage"""
    try:
        with open(PROFESSIONAL_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving professional data: {e}")

# Staff Management Endpoints
@router.get("/staff")
async def get_all_staff():
    """Get all staff members"""
    staff = load_staff_data()
    return {"staff": staff, "total": len(staff)}

@router.post("/staff")
async def create_staff(staff: StaffCreate):
    """Create a new staff member"""
    try:
        staff_list = load_staff_data()
        
        new_staff = {
            "id": len(staff_list) + 1,
            "name": staff.name,
            "email": staff.email,
            "phone": staff.phone,
            "role": staff.role,
            "specialization": staff.specialization,
            "working_hours": staff.working_hours,
            "salary": staff.salary,
            "hire_date": staff.hire_date or datetime.now().strftime("%Y-%m-%d"),
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        staff_list.append(new_staff)
        save_staff_data(staff_list)
        
        return {"message": "Staff member created successfully", "staff": new_staff}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating staff: {str(e)}")

@router.put("/staff/{staff_id}")
async def update_staff(staff_id: int, staff: StaffCreate):
    """Update staff member details"""
    try:
        staff_list = load_staff_data()
        
        for i, staff_member in enumerate(staff_list):
            if staff_member.get('id') == staff_id:
                staff_list[i] = {
                    "id": staff_id,
                    "name": staff.name,
                    "email": staff.email,
                    "phone": staff.phone,
                    "role": staff.role,
                    "specialization": staff.specialization,
                    "working_hours": staff.working_hours,
                    "salary": staff.salary,
                    "hire_date": staff.hire_date,
                    "updated_at": datetime.now().isoformat(),
                    "status": staff_member.get("status", "active")
                }
                save_staff_data(staff_list)
                return {"message": "Staff member updated successfully", "staff": staff_list[i]}
        
        raise HTTPException(status_code=404, detail="Staff member not found")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating staff: {str(e)}")

@router.delete("/staff/{staff_id}")
async def delete_staff(staff_id: int):
    """Delete a staff member"""
    try:
        staff_list = load_staff_data()
        staff_list = [staff for staff in staff_list if staff.get('id') != staff_id]
        save_staff_data(staff_list)
        return {"message": "Staff member deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting staff: {str(e)}")

# Professional Management Endpoints
@router.get("/professionals")
async def get_all_professionals():
    """Get all professionals"""
    professionals = load_professional_data()
    return {"professionals": professionals, "total": len(professionals)}

@router.post("/professionals")
async def create_professional(professional: ProfessionalCreate):
    """Create a new professional"""
    try:
        professional_list = load_professional_data()
        
        new_professional = {
            "id": len(professional_list) + 1,
            "name": professional.name,
            "profession": professional.profession,
            "experience_years": professional.experience_years,
            "certifications": professional.certifications,
            "specialties": professional.specialties,
            "hourly_rate": professional.hourly_rate,
            "availability": professional.availability,
            "contact_info": professional.contact_info,
            "created_at": datetime.now().isoformat(),
            "status": "available"
        }
        
        professional_list.append(new_professional)
        save_professional_data(professional_list)
        
        return {"message": "Professional created successfully", "professional": new_professional}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating professional: {str(e)}")

@router.put("/professionals/{professional_id}")
async def update_professional(professional_id: int, professional: ProfessionalCreate):
    """Update professional details"""
    try:
        professional_list = load_professional_data()
        
        for i, prof in enumerate(professional_list):
            if prof.get('id') == professional_id:
                professional_list[i] = {
                    "id": professional_id,
                    "name": professional.name,
                    "profession": professional.profession,
                    "experience_years": professional.experience_years,
                    "certifications": professional.certifications,
                    "specialties": professional.specialties,
                    "hourly_rate": professional.hourly_rate,
                    "availability": professional.availability,
                    "contact_info": professional.contact_info,
                    "updated_at": datetime.now().isoformat(),
                    "status": prof.get("status", "available")
                }
                save_professional_data(professional_list)
                return {"message": "Professional updated successfully", "professional": professional_list[i]}
        
        raise HTTPException(status_code=404, detail="Professional not found")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating professional: {str(e)}")

@router.delete("/professionals/{professional_id}")
async def delete_professional(professional_id: int):
    """Delete a professional"""
    try:
        professional_list = load_professional_data()
        professional_list = [prof for prof in professional_list if prof.get('id') != professional_id]
        save_professional_data(professional_list)
        return {"message": "Professional deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting professional: {str(e)}")

# Excel Import/Export Endpoints
@router.post("/import/staff")
async def import_staff_excel(file: UploadFile = File(...)):
    """Import staff data from Excel file"""
    try:
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Only Excel files are supported")
        
        content = await file.read()
        
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            df = pd.read_excel(temp_file_path)
            
            # Expected columns: name, email, phone, role, specialization, working_hours, salary, hire_date
            required_columns = ['name', 'role']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise HTTPException(status_code=400, detail=f"Missing required columns: {missing_columns}")
            
            # Convert to list of dictionaries
            staff_list = df.to_dict('records')
            
            # Add IDs and timestamps
            existing_staff = load_staff_data()
            next_id = max([s.get('id', 0) for s in existing_staff], default=0) + 1
            
            for staff in staff_list:
                staff['id'] = next_id
                staff['created_at'] = datetime.now().isoformat()
                staff['status'] = 'active'
                if not staff.get('hire_date'):
                    staff['hire_date'] = datetime.now().strftime("%Y-%m-%d")
                next_id += 1
            
            # Merge with existing staff
            all_staff = existing_staff + staff_list
            save_staff_data(all_staff)
            
            return {
                "message": f"Successfully imported {len(staff_list)} staff members",
                "imported_count": len(staff_list),
                "total_staff": len(all_staff),
                "preview": staff_list[:3]
            }
        finally:
            os.unlink(temp_file_path)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import error: {str(e)}")

@router.post("/import/professionals")
async def import_professionals_excel(file: UploadFile = File(...)):
    """Import professionals data from Excel file"""
    try:
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Only Excel files are supported")
        
        content = await file.read()
        
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            df = pd.read_excel(temp_file_path)
            
            # Expected columns: name, profession, experience_years, certifications, specialties, hourly_rate, availability, contact_info
            required_columns = ['name', 'profession']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise HTTPException(status_code=400, detail=f"Missing required columns: {missing_columns}")
            
            # Convert to list of dictionaries
            professional_list = df.to_dict('records')
            
            # Add IDs and timestamps
            existing_professionals = load_professional_data()
            next_id = max([p.get('id', 0) for p in existing_professionals], default=0) + 1
            
            for professional in professional_list:
                professional['id'] = next_id
                professional['created_at'] = datetime.now().isoformat()
                professional['status'] = 'available'
                next_id += 1
            
            # Merge with existing professionals
            all_professionals = existing_professionals + professional_list
            save_professional_data(all_professionals)
            
            return {
                "message": f"Successfully imported {len(professional_list)} professionals",
                "imported_count": len(professional_list),
                "total_professionals": len(all_professionals),
                "preview": professional_list[:3]
            }
        finally:
            os.unlink(temp_file_path)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import error: {str(e)}")

@router.get("/export/staff")
async def export_staff_excel():
    """Export staff data to Excel file"""
    try:
        staff = load_staff_data()
        
        if not staff:
            raise HTTPException(status_code=404, detail="No staff data to export")
        
        df = pd.DataFrame(staff)
        
        filename = f"staff_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = f"temp_{filename}"
        df.to_excel(filepath, index=False)
        
        with open(filepath, 'rb') as f:
            content = f.read()
        
        os.remove(filepath)
        
        return Response(
            content=content,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export error: {str(e)}")

@router.get("/export/professionals")
async def export_professionals_excel():
    """Export professionals data to Excel file"""
    try:
        professionals = load_professional_data()
        
        if not professionals:
            raise HTTPException(status_code=404, detail="No professional data to export")
        
        df = pd.DataFrame(professionals)
        
        filename = f"professionals_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = f"temp_{filename}"
        df.to_excel(filepath, index=False)
        
        with open(filepath, 'rb') as f:
            content = f.read()
        
        os.remove(filepath)
        
        return Response(
            content=content,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export error: {str(e)}")

@router.get("/templates/staff")
async def get_staff_template():
    """Get Excel template for staff import"""
    try:
        template_data = [
            {
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "+1234567890",
                "role": "Hair Stylist",
                "specialization": "Hair Cutting, Coloring",
                "working_hours": "9:00 AM - 6:00 PM",
                "salary": 3000.00,
                "hire_date": "2024-01-15"
            },
            {
                "name": "Jane Smith",
                "email": "jane@example.com",
                "phone": "+1234567891",
                "role": "Beautician",
                "specialization": "Facials, Makeup",
                "working_hours": "10:00 AM - 7:00 PM",
                "salary": 2800.00,
                "hire_date": "2024-02-01"
            }
        ]
        
        df = pd.DataFrame(template_data)
        filename = "staff_import_template.xlsx"
        filepath = f"temp_{filename}"
        df.to_excel(filepath, index=False)
        
        with open(filepath, 'rb') as f:
            content = f.read()
        
        os.remove(filepath)
        
        return Response(
            content=content,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Template generation error: {str(e)}")

@router.get("/templates/professionals")
async def get_professional_template():
    """Get Excel template for professionals import"""
    try:
        template_data = [
            {
                "name": "Dr. Sarah Johnson",
                "profession": "Dermatologist",
                "experience_years": 10,
                "certifications": "MBBS, MD Dermatology",
                "specialties": "Acne Treatment, Anti-aging",
                "hourly_rate": 150.00,
                "availability": "Mon-Fri 9AM-5PM",
                "contact_info": "+1234567892"
            },
            {
                "name": "Mike Wilson",
                "profession": "Massage Therapist",
                "experience_years": 7,
                "certifications": "Licensed Massage Therapist",
                "specialties": "Swedish Massage, Deep Tissue",
                "hourly_rate": 80.00,
                "availability": "Tue-Sat 10AM-8PM",
                "contact_info": "+1234567893"
            }
        ]
        
        df = pd.DataFrame(template_data)
        filename = "professionals_import_template.xlsx"
        filepath = f"temp_{filename}"
        df.to_excel(filepath, index=False)
        
        with open(filepath, 'rb') as f:
            content = f.read()
        
        os.remove(filepath)
        
        return Response(
            content=content,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Template generation error: {str(e)}")
