"""
Gemini 2.5 Flash Native Audio Dialog Integration
Real-time audio-to-audio conversations with unlimited requests
"""
import asyncio
import logging
from typing import Optional, Dict, Any
from google import genai
from google.genai import types
from config import settings

logger = logging.getLogger(__name__)

class Gemini25FlashAudio:
    """Gemini 2.5 Flash Native Audio Dialog Service"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'GEMINI_API_KEY', '')
        self.client = None
        self.model = "gemini-2.5-flash-preview-04-17"
        
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
            logger.info("[Gemini 2.5 Flash] Initialized successfully")
        else:
            logger.warning("[Gemini 2.5 Flash] No API key configured")
    
    async def audio_conversation(self, audio_data: bytes, context: str = "") -> Dict[str, Any]:
        """
        Process audio input and return audio response (native audio dialog)
        
        Args:
            audio_data: Raw audio bytes
            context: Conversation context
            
        Returns:
            Dict with response audio and text
        """
        if not self.client:
            return {
                "success": False,
                "error": "Gemini client not initialized",
                "text": "AI service not configured"
            }
        
        try:
            # Create audio part from input
            audio_part = types.Part.from_bytes(
                data=audio_data,
                mime_type="audio/wav"
            )
            
            # Build prompt with context
            prompt = f"""
You are BookSmart AI, a helpful salon assistant. 
Context: {context}

Respond naturally and helpfully to the user's voice input.
Keep responses concise and friendly.
"""
            
            # Generate response with audio
            response = self.client.models.generate_content(
                model=self.model,
                contents=[prompt, audio_part],
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO", "TEXT"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice="en-US-Journey-D"
                        )
                    )
                )
            )
            
            # Extract audio and text from response
            result = {
                "success": True,
                "text": response.text,
                "model": "gemini-2.5-flash",
                "context": context
            }
            
            # If audio response available
            if hasattr(response, 'candidates') and response.candidates:
                for candidate in response.candidates:
                    if hasattr(candidate, 'content') and candidate.content.parts:
                        for part in candidate.content.parts:
                            if hasattr(part, 'inline_data') and part.inline_data:
                                result["audio_data"] = part.inline_data.data
                                result["audio_mime_type"] = part.inline_data.mime_type
                                break
            
            logger.info(f"[Gemini 2.5 Flash] Audio response generated")
            return result
            
        except Exception as e:
            logger.error(f"[Gemini 2.5 Flash] Audio conversation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": "Sorry, I couldn't process that audio."
            }
    
    async def text_to_audio_response(self, text: str) -> Dict[str, Any]:
        """
        Convert text response to audio using Gemini 2.5 Flash
        
        Args:
            text: Text to convert to speech
            
        Returns:
            Dict with audio data
        """
        if not self.client:
            return {
                "success": False,
                "error": "Gemini client not initialized"
            }
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=text,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice="en-US-Journey-D"
                        )
                    )
                )
            )
            
            result = {"success": True, "text": text}
            
            if hasattr(response, 'candidates') and response.candidates:
                for candidate in response.candidates:
                    if hasattr(candidate, 'content') and candidate.content.parts:
                        for part in candidate.content.parts:
                            if hasattr(part, 'inline_data') and part.inline_data:
                                result["audio_data"] = part.inline_data.data
                                result["audio_mime_type"] = part.inline_data.mime_type
                                break
            
            return result
            
        except Exception as e:
            logger.error(f"[Gemini 2.5 Flash] TTS error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def chat_with_audio(self, message: str, conversation_history: list = None) -> Dict[str, Any]:
        """
        Chat with text input, return text + audio response
        
        Args:
            message: User message
            conversation_history: Previous messages
            
        Returns:
            Dict with text and audio response
        """
        if not self.client:
            return {
                "success": False,
                "error": "Gemini client not initialized",
                "text": "AI service not configured"
            }
        
        try:
            # Build conversation as simple strings
            contents = []
            
            # Add system prompt
            contents.append("""
You are BookSmart AI, a friendly salon assistant for BookSmart salon booking system.

Your role:
- Help customers book appointments
- Answer questions about services, prices, and availability
- Provide friendly, natural responses
- Keep conversations concise and helpful

Services offered:
- Haircuts, styling, coloring
- Spa treatments (facials, massages)
- Nail services
- Bridal packages
- Men's grooming

Pricing ranges from Rs.500 to Rs.5000
Location: Main Street, City Center
Hours: 9 AM - 8 PM daily

Be warm, professional, and helpful!
""")
            
            # Add conversation history
            if conversation_history:
                for msg in conversation_history:
                    contents.append(msg.get("content", ""))
            
            # Add current message
            contents.append(message)
            
            # Generate response with audio
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO", "TEXT"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice="en-US-Journey-D"
                        )
                    ),
                    temperature=0.7,
                    max_output_tokens=500
                )
            )
            
            result = {
                "success": True,
                "text": response.text,
                "model": "gemini-2.5-flash"
            }
            
            # Extract audio
            if hasattr(response, 'candidates') and response.candidates:
                for candidate in response.candidates:
                    if hasattr(candidate, 'content') and candidate.content.parts:
                        for part in candidate.content.parts:
                            if hasattr(part, 'inline_data') and part.inline_data:
                                result["audio_data"] = part.inline_data.data
                                result["audio_mime_type"] = part.inline_data.mime_type
                                break
            
            logger.info(f"[Gemini 2.5 Flash] Chat response generated")
            return result
            
        except Exception as e:
            logger.error(f"[Gemini 2.5 Flash] Chat error: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": "I apologize, but I'm having trouble responding right now."
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status"""
        return {
            "service": "Gemini 2.5 Flash Native Audio",
            "status": "active" if self.client else "inactive",
            "model": self.model,
            "api_key_configured": bool(self.api_key),
            "features": [
                "Native audio-to-audio dialog",
                "Text-to-speech",
                "Unlimited requests",
                "Low latency",
                "Natural voice"
            ]
        }

# Initialize service
gemini_25_flash = Gemini25FlashAudio()
