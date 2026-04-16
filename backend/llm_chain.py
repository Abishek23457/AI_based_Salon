from __future__ import annotations

from sqlalchemy.orm import Session

import models
from rag_pipeline import get_retriever
from config import settings

SYSTEM_PROMPT = """You are BookSmart's AI salon receptionist.
Tone: warm, concise, professional, human-like.
Goals:
1) Help the customer quickly.
2) Give clear service and price information only if available in context.
3) If customer wants to book, ask for missing details: service, date/time, name, phone.
4) Never invent unavailable pricing or staff schedules.
5) If information is missing from context, say you can connect them to the human team.

Use the context below when available:
{context}
"""

def _get_gemini_llm():
    if not settings.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not configured")
    from langchain_google_genai import ChatGoogleGenerativeAI
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.4,
    )

def _build_context(salon_id: str) -> str:
    """Fetch top docs from tenant retriever; return compact text context."""
    retriever = get_retriever(salon_id)
    if not retriever:
        return "No indexed salon context available yet."

    docs = retriever.invoke("services, pricing, staff availability, booking policy")
    if not docs:
        return "No indexed salon context available yet."
    return "\n\n".join(d.page_content for d in docs[:6])

def _build_db_snapshot(db: Session, salon_id: int) -> str:
    salon = db.query(models.Salon).filter(models.Salon.id == salon_id).first()
    services = db.query(models.Service).filter(models.Service.salon_id == salon_id).all()
    staff = db.query(models.Staff).filter(models.Staff.salon_id == salon_id).all()

    lines: list[str] = []
    if salon:
        lines.append(f"Salon: {salon.name} (id={salon.id})")

    if services:
        lines.append("Services:")
        for s in services[:20]:
            price = f"Rs {int(s.price)}" if s.price is not None else "N/A"
            lines.append(f"- {s.name}: {price}, {s.duration_minutes} min. {s.description or ''}".strip())
    else:
        lines.append("Services: none configured.")

    if staff:
        lines.append("Staff:")
        for st in staff[:20]:
            lines.append(f"- {st.name}: {st.working_hours}")
    else:
        lines.append("Staff: none configured.")

    return "\n".join(lines)

def execute_chat(db: Session, salon_id: int, query: str) -> str:
    try:
        db_context = _build_db_snapshot(db, salon_id)
        rag_context = _build_context(str(salon_id))
        context = f"{db_context}\n\nRAG context:\n{rag_context}"
        llm = _get_gemini_llm()
        prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            f"Customer message: {query}\n\n"
            "Reply as the receptionist in 1-3 short sentences."
        ).format(context=context)
        result = llm.invoke(prompt)
        answer = getattr(result, "content", "").strip()
        return answer or "I can help you with services and booking. Please share your preferred service and time."
    except Exception as e:
        print(f"[LLM] Chat execution failed: {e}")
        return "I can help with booking. Please share service name, preferred date/time, your name, and phone number."

def stream_chat(db: Session, salon_id: int, query: str):
    """Stream AI tokens for real-time S2S processing."""
    try:
        db_context = _build_db_snapshot(db, salon_id)
        rag_context = _build_context(str(salon_id))
        context = f"{db_context}\n\nRAG context:\n{rag_context}"
        llm = _get_gemini_llm()
        prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            f"Customer message: {query}\n\n"
            "Reply as the receptionist in 1-2 VERY short sentences. Be direct."
        ).format(context=context)
        
        for chunk in llm.stream(prompt):
            content = getattr(chunk, "content", "")
            if content:
                yield content
    except Exception as e:
        print(f"[LLM Stream] Failed: {e}")
        yield "I can help you with your salon booking."
