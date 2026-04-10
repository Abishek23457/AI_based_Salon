import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
import models

def setup_sample_data():
    db = SessionLocal()
    try:
        # Check if salon exists
        salon = db.query(models.Salon).filter(models.Salon.id == 1).first()
        if not salon:
            salon = models.Salon(name="BookSmart Demo Salon", phone="+91 95138 86363")
            db.add(salon)
            db.commit()
            db.refresh(salon)
            print(f"Created salon: {salon.name} (ID: {salon.id})")
        else:
            print(f"Using existing salon: {salon.name} (ID: {salon.id})")

        # Add sample services
        services = [
            {"name": "Haircut", "duration_minutes": 30, "price": 500.0, "description": "Professional haircut with styling"},
            {"name": "Hair Color", "duration_minutes": 90, "price": 1500.0, "description": "Full hair coloring service"},
            {"name": "Facial", "duration_minutes": 60, "price": 800.0, "description": "Rejuvenating facial treatment"},
            {"name": "Manicure", "duration_minutes": 45, "price": 400.0, "description": "Classic manicure with nail polish"},
            {"name": "Pedicure", "duration_minutes": 60, "price": 600.0, "description": "Complete pedicure treatment"},
            {"name": "Hair Spa", "duration_minutes": 45, "price": 700.0, "description": "Deep conditioning hair spa treatment"},
        ]

        for service_data in services:
            existing = db.query(models.Service).filter(
                models.Service.salon_id == salon.id,
                models.Service.name == service_data["name"]
            ).first()
            if not existing:
                service = models.Service(
                    salon_id=salon.id,
                    **service_data
                )
                db.add(service)
                print(f"Added service: {service_data['name']}")
            else:
                print(f"Service already exists: {service_data['name']}")

        # Add sample staff
        staff_data = [
            {"name": "Sarah Johnson", "working_hours": "9:00 AM - 6:00 PM"},
            {"name": "Michael Chen", "working_hours": "10:00 AM - 8:00 PM"},
            {"name": "Emma Wilson", "working_hours": "8:00 AM - 4:00 PM"},
        ]

        for staff_member in staff_data:
            existing = db.query(models.Staff).filter(
                models.Staff.salon_id == salon.id,
                models.Staff.name == staff_member["name"]
            ).first()
            if not existing:
                staff = models.Staff(
                    salon_id=salon.id,
                    **staff_member
                )
                db.add(staff)
                print(f"Added staff: {staff_member['name']}")
            else:
                print(f"Staff already exists: {staff_member['name']}")

        db.commit()
        print(f"\nSetup complete! Salon ID: {salon.id}")
        print(f"Services: {len(db.query(models.Service).filter(models.Service.salon_id == salon.id).all())}")
        print(f"Staff: {len(db.query(models.Staff).filter(models.Staff.salon_id == salon.id).all())}")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    setup_sample_data()
