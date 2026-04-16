"""
Gemini 3 Flash Live Integration
Real-time live streaming conversations with unlimited requests
"""
import asyncio
import logging
from typing import Optional, Dict, Any, AsyncGenerator
from google import genai
from google.genai import types
from config import settings

logger = logging.getLogger(__name__)

class Gemini3FlashLive:
    """Gemini 3 Flash Live Streaming Service"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'GEMINI_API_KEY', '')
        self.client = None
        self.model = "gemini-2.5-flash"
        self.live_sessions = {}
        
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
            logger.info("[Gemini 3 Flash Live] Initialized successfully")
        else:
            logger.warning("[Gemini 3 Flash Live] No API key configured")
    
    async def create_live_session(self, session_id: str, context: str = "") -> Dict[str, Any]:
        """
        Create a live streaming session
        
        Args:
            session_id: Unique session identifier
            context: Initial context for the session
            
        Returns:
            Dict with session details
        """
        if not self.client:
            return {
                "success": False,
                "error": "Gemini client not initialized"
            }
        
        try:
            # Initialize session with context
            session = {
                "session_id": session_id,
                "context": context,
                "messages": [],
                "created_at": asyncio.get_event_loop().time()
            }
            
            self.live_sessions[session_id] = session
            logger.info(f"[Gemini 3 Flash Live] Session {session_id} created")
            
            return {
                "success": True,
                "session_id": session_id,
                "model": self.model
            }
            
        except Exception as e:
            logger.error(f"[Gemini 3 Flash Live] Session creation error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def stream_chat(self, session_id: str, message: str) -> AsyncGenerator[str, None]:
        """
        Stream chat responses in real-time
        
        Args:
            session_id: Session identifier
            message: User message
            
        Yields:
            Chunks of response text
        """
        if not self.client:
            yield "AI service not configured"
            return
        
        if session_id not in self.live_sessions:
            yield "Session not found"
            return
        
        session = self.live_sessions[session_id]
        
        try:
            # Add user message to history
            session["messages"].append({"role": "user", "content": message})
            
            # Build conversation as simple strings
            contents = []
            
            # System prompt
            contents.append(f"""
You are BookSmart AI, a helpful salon assistant.
Context: {session.get('context', '')}

Help customers with:
- Booking appointments
- Service information
- Pricing and availability
- General salon inquiries

Be friendly, concise, and helpful.
""")
            
            # Add message history
            for msg in session["messages"][-5:]:  # Last 5 messages
                contents.append(msg["content"])
            
            # Stream response
            response = self.client.models.generate_content_stream(
                model=self.model,
                contents=contents,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=1000
                )
            )
            
            full_response = ""
            
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    yield chunk.text
            
            # Add AI response to history
            session["messages"].append({"role": "model", "content": full_response})
            
            logger.info(f"[Gemini 3 Flash Live] Streamed response for session {session_id}")
            
        except Exception as e:
            logger.error(f"[Gemini 3 Flash Live] Stream error: {e}")
            yield f"Error: {str(e)}"
    
    async def chat(self, session_id: str, message: str) -> Dict[str, Any]:
        """
        Non-streaming chat with live model
        
        Args:
            session_id: Session identifier
            message: User message
            
        Returns:
            Dict with response
        """
        if not self.client:
            return {
                "success": False,
                "error": "Gemini client not initialized",
                "response": "AI service not configured"
            }
        
        if session_id not in self.live_sessions:
            # Auto-create session
            await self.create_live_session(session_id)
        
        session = self.live_sessions[session_id]
        
        try:
            # Build conversation as simple strings
            contents = []
            
            # System prompt
            contents.append(f"""
You are BookSmart AI, a helpful salon assistant for BookSmart booking system.

Services:
- Haircuts: Rs.500-2000
- Styling: Rs.1000-3000
- Coloring: Rs.1500-5000
- Spa: Rs.2000-4000
- Nails: Rs.500-2000
- Bridal: Rs.10000-50000

Location: Main Street, City Center
Hours: 9 AM - 8 PM daily

Help customers book appointments and answer questions naturally and friendly.
""")
            
            # Add conversation history
            for msg in session["messages"][-10:]:  # Last 10 messages
                contents.append(msg["content"])
            
            # Add current message
            contents.append(message)
            
            # Generate response
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=800
                )
            )
            
            # Add to history
            session["messages"].append({"role": "user", "content": message})
            session["messages"].append({"role": "model", "content": response.text})
            
            logger.info(f"[Gemini 3 Flash Live] Chat response for session {session_id}")
            
            return {
                "success": True,
                "response": response.text,
                "session_id": session_id,
                "model": self.model,
                "message_count": len(session["messages"])
            }
            
        except Exception as e:
            logger.error(f"[Gemini 3 Flash Live] Chat error: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "I apologize, but I'm having trouble responding."
            }
    
    async def close_session(self, session_id: str) -> Dict[str, Any]:
        """
        Close a live session
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dict with result
        """
        if session_id in self.live_sessions:
            del self.live_sessions[session_id]
            logger.info(f"[Gemini 3 Flash Live] Session {session_id} closed")
            return {"success": True}
        
        return {"success": False, "error": "Session not found"}
    
    async def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """
        Get session information
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dict with session details
        """
        if session_id in self.live_sessions:
            session = self.live_sessions[session_id]
            return {
                "success": True,
                "session_id": session_id,
                "message_count": len(session["messages"]),
                "created_at": session["created_at"],
                "context": session.get("context", "")
            }
        
        return {"success": False, "error": "Session not found"}
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status"""
        return {
            "service": "Gemini 3 Flash Live",
            "status": "active" if self.client else "inactive",
            "model": self.model,
            "api_key_configured": bool(self.api_key),
            "active_sessions": len(self.live_sessions),
            "features": [
                "Real-time streaming",
                "Unlimited requests",
                "Session management",
                "Context awareness",
                "Low latency",
                "Natural conversation"
            ]
        }

# Initialize service
gemini_3_flash_live = Gemini3FlashLive()
