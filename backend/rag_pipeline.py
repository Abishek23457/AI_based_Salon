"""
RAG Pipeline with Booking Integration
Enhanced to include slot availability and stylist information
"""
import os
from datetime import datetime, timedelta
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# Setup Embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


def ingest_salon_data(salon_id: str, data: dict):
    """Ingest salon data including services, staff, and booking slots."""
    docs = []
    
    # Ingest Services with Pricing
    if "services" in data:
        for svc in data["services"]:
            docs.append(Document(
                page_content=f"""Service: {svc['name']}
Price: ₹{svc['price']}
Duration: {svc['duration_minutes']} minutes
Available Stylists: {', '.join(svc.get('stylists', ['Any']))}
Description: {svc.get('description', 'Professional salon service')}""",
                metadata={"salon_id": salon_id, "type": "service", "service_name": svc['name']}
            ))
    
    # Ingest Staff with Specialties
    if "staff" in data:
        for stf in data["staff"]:
            docs.append(Document(
                page_content=f"""Stylist: {stf['name']}
Working Hours: {stf.get('working_hours', '10 AM - 8 PM')}
Specialties: {stf.get('specialties', 'All services')}
Experience: {stf.get('experience', 'Professional stylist')}""",
                metadata={"salon_id": salon_id, "type": "staff", "stylist_name": stf['name']}
            ))
    
    # Ingest Slot Availability Info
    total_slots = data.get("total_slots_per_day", 50)
    slot_duration = data.get("slot_duration_minutes", 30)
    
    docs.append(Document(
        page_content=f"""Booking Information:
Total Slots Per Day: {total_slots}
Slot Duration: {slot_duration} minutes
Opening Hours: {data.get('opening_time', '10:00 AM')} - {data.get('closing_time', '8:00 PM')}
Advanced Booking: Up to 7 days ahead
Cancellation: Please call 2 hours before appointment""",
        metadata={"salon_id": salon_id, "type": "booking_info"}
    ))
    
    # Ingest Custom Policies
    if "policies" in data:
        docs.append(Document(
            page_content=f"Policies: {data['policies']}",
            metadata={"salon_id": salon_id, "type": "policy"}
        ))
    
    # Ingest Availability Status (can be updated dynamically)
    if "availability" in data:
        avail = data["availability"]
        docs.append(Document(
            page_content=f"""Current Availability:
Date: {avail.get('date', 'Today')}
Available Slots: {avail.get('available_slots', 50)} out of {total_slots}
Popular Times: {avail.get('popular_times', '10 AM, 2 PM, 4 PM')}
Next Available: {avail.get('next_available', 'Today at 2 PM')}""",
            metadata={"salon_id": salon_id, "type": "availability"}
        ))
    
    # Chunk and store
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_docs = splitter.split_documents(docs)
    
    # Build local FAISS vector store
    vectorstore = FAISS.from_documents(split_docs, embeddings)
    
    # Save isolated index per tenant
    os.makedirs(f"./vector_indexes/{salon_id}", exist_ok=True)
    vectorstore.save_local(f"./vector_indexes/{salon_id}")
    
    return vectorstore


def get_retriever(salon_id: str):
    """Get retriever for salon with booking data."""
    path = f"./vector_indexes/{salon_id}"
    if not os.path.exists(path):
        return None
    
    vectorstore = FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)
    
    # MMR for diverse results
    return vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": 6, "fetch_k": 15})


def query_booking_info(salon_id: str, query: str) -> list:
    """Query booking-related information from the vector store."""
    retriever = get_retriever(salon_id)
    if not retriever:
        return []
    
    # Search for relevant documents
    docs = retriever.invoke(query)
    
    # Filter by relevance and type
    results = []
    for doc in docs:
        if doc.metadata.get("type") in ["service", "staff", "booking_info", "availability"]:
            results.append({
                "content": doc.page_content,
                "type": doc.metadata.get("type"),
                "metadata": doc.metadata
            })
    
    return results


def update_availability(salon_id: str, date: str, available_slots: int):
    """Update availability information for a specific date."""
    path = f"./vector_indexes/{salon_id}"
    if not os.path.exists(path):
        return False
    
    try:
        vectorstore = FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)
        
        # Add updated availability document
        avail_doc = Document(
            page_content=f"""Current Availability:
Date: {date}
Available Slots: {available_slots} out of 50
Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}""",
            metadata={"salon_id": salon_id, "type": "availability", "date": date}
        )
        
        # Add to existing index
        vectorstore.add_documents([avail_doc])
        vectorstore.save_local(path)
        
        return True
    except Exception as e:
        print(f"[RAG] Error updating availability: {e}")
        return False
