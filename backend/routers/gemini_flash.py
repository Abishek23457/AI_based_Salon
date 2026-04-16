"""
Gemini Flash Models API Router
Routes for Gemini 2.5 Flash Audio and Gemini 3 Flash Live
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import base64
from gemini_2_5_flash_audio import gemini_25_flash
from gemini_3_flash_live import gemini_3_flash_live

router = APIRouter(tags=["Gemini Flash"])

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    conversation_history: Optional[List[dict]] = None

class AudioChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[dict]] = None

class LiveSessionRequest(BaseModel):
    session_id: str
    context: Optional[str] = ""

class StreamChatRequest(BaseModel):
    session_id: str
    message: str

# Gemini 2.5 Flash Audio Endpoints

@router.post("/audio/chat")
async def audio_chat(request: AudioChatRequest):
    """Chat with Gemini 2.5 Flash - returns text + audio"""
    result = await gemini_25_flash.chat_with_audio(
        request.message,
        request.conversation_history or []
    )
    return result

@router.post("/audio/text-to-speech")
async def text_to_speech(text: str):
    """Convert text to speech using Gemini 2.5 Flash"""
    result = await gemini_25_flash.text_to_audio_response(text)
    return result

@router.get("/audio/status")
async def get_audio_status():
    """Get Gemini 2.5 Flash Audio status"""
    return gemini_25_flash.get_status()

# Gemini 3 Flash Live Endpoints

@router.post("/live/create-session")
async def create_live_session(request: LiveSessionRequest):
    """Create a new live streaming session"""
    result = await gemini_3_flash_live.create_live_session(
        request.session_id,
        request.context or ""
    )
    return result

@router.post("/live/chat")
async def live_chat(request: ChatRequest):
    """Chat with Gemini 3 Flash Live (non-streaming)"""
    session_id = request.session_id or "default"
    result = await gemini_3_flash_live.chat(session_id, request.message)
    return result

@router.post("/live/session/{session_id}/info")
async def get_session_info(session_id: str):
    """Get live session information"""
    result = await gemini_3_flash_live.get_session_info(session_id)
    return result

@router.delete("/live/session/{session_id}")
async def close_session(session_id: str):
    """Close a live session"""
    result = await gemini_3_flash_live.close_session(session_id)
    return result

@router.get("/live/status")
async def get_live_status():
    """Get Gemini 3 Flash Live status"""
    return gemini_3_flash_live.get_status()

# Unified Chat Endpoint (uses Gemini 3 Flash Live by default)

@router.post("/chat")
async def unified_chat(request: ChatRequest):
    """
    Unified chat endpoint using Gemini 3 Flash Live
    Provides unlimited requests with context awareness
    """
    session_id = request.session_id or "default"
    result = await gemini_3_flash_live.chat(session_id, request.message)
    return result

@router.get("/status")
async def get_all_status():
    """Get status of all Gemini Flash services"""
    return {
        "gemini_25_flash_audio": gemini_25_flash.get_status(),
        "gemini_3_flash_live": gemini_3_flash_live.get_status(),
        "unlimited_requests": True,
        "recommended_model": "gemini-3-flash-live"
    }
