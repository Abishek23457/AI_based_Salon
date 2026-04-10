import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
import models
from rag_pipeline import ingest_salon_data

def ingest_salon():
    db = SessionLocal()
    try:
        salon_id = 1
        
        # Get services and staff data
        services_db = db.query(models.Service).filter(models.Service.salon_id == salon_id).all()
        staff_db = db.query(models.Staff).filter(models.Staff.salon_id == salon_id).all()
        
        data = {
            "services": [
                {
                    "name": s.name, 
                    "price": s.price, 
                    "duration_minutes": s.duration_minutes, 
                    "description": s.description or "Professional service"
                } for s in services_db
            ],
            "staff": [
                {"name": s.name, "working_hours": s.working_hours} for s in staff_db
            ],
            "policies": "Standard cancellation policy: 24h notice required. Late cancellations may incur a fee. Walk-ins welcome based on availability."
        }
        
        print(f"Ingesting data for salon {salon_id}:")
        print(f"Services: {len(data['services'])}")
        print(f"Staff: {len(data['staff'])}")
        
        # Ingest data
        vectorstore = ingest_salon_data(str(salon_id), data)
        print(f"Successfully ingested data for salon {salon_id}")
        
        # Test retrieval
        from rag_pipeline import get_retriever
        retriever = get_retriever(str(salon_id))
        if retriever:
            docs = retriever.invoke("What services do you offer?")
            print(f"Retrieved {len(docs)} documents for test query")
            for doc in docs[:2]:
                print(f"  - {doc.page_content[:100]}...")
        else:
            print("Failed to create retriever")
            
    except Exception as e:
        print(f"Error during ingestion: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    ingest_salon()
