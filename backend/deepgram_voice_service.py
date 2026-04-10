"""
Deepgram Voice Service for BookSmart AI
Real-time Speech-to-Text (STT) and Text-to-Speech (TTS)
Docs: https://developers.deepgram.com/docs/getting-started-with-pre-recorded-audio
"""
import os
import asyncio
import websockets
import json
import pyaudio
import numpy as np
from config import settings
from typing import Optional, Callable
import logging

logger = logging.getLogger(__name__)

# Deepgram Configuration
DEEPGRAM_STT_URL = "wss://api.deepgram.com/v1/listen"
DEEPGRAM_TTS_URL = "https://api.deepgram.com/v1/speak"

# Audio Settings
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000  # 16kHz for Deepgram
CHUNK = 1024


class DeepgramVoiceService:
    """Deepgram Voice Service for real-time STT and TTS"""
    
    def __init__(self):
        self.api_key = settings.DEEPGRAM_API_KEY
        self.is_listening = False
        self.audio = pyaudio.PyAudio()
        self.on_transcript: Optional[Callable[[str], None]] = None
        
        if not self.api_key:
            logger.warning("DEEPGRAM_API_KEY not set! Voice features will not work.")
    
    async def stream_microphone(self, websocket):
        """Stream microphone audio to Deepgram"""
        stream = self.audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
        
        try:
            while self.is_listening:
                data = stream.read(CHUNK, exception_on_overflow=False)
                await websocket.send(data)
                await asyncio.sleep(0.001)
        except Exception as e:
            logger.error(f"Microphone stream error: {e}")
        finally:
            stream.stop_stream()
            stream.close()
    
    async def receive_transcriptions(self, websocket):
        """Receive transcriptions from Deepgram"""
        try:
            async for message in websocket:
                data = json.loads(message)
                
                # Get transcript
                channel = data.get("channel", {})
                alternatives = channel.get("alternatives", [{}])
                transcript = alternatives[0].get("transcript", "")
                is_final = data.get("is_final", False)
                
                if transcript and is_final and self.on_transcript:
                    logger.info(f"Transcript: {transcript}")
                    self.on_transcript(transcript)
                    
        except Exception as e:
            logger.error(f"Transcription receive error: {e}")
    
    async def start_listening(self, on_transcript_callback: Callable[[str], None]):
        """Start real-time speech recognition"""
        if not self.api_key:
            logger.error("Cannot start listening: DEEPGRAM_API_KEY not set")
            return False
        
        self.on_transcript = on_transcript_callback
        self.is_listening = True
        
        # WebSocket URL with parameters
        url = f"{DEEPGRAM_STT_URL}?encoding=linear16&sample_rate=16000&channels=1&language=en-IN&model=nova-2&smart_format=true&interim_results=false"
        
        try:
            async with websockets.connect(
                url,
                additional_headers={"Authorization": f"Token {self.api_key}"}
            ) as websocket:
                logger.info("Connected to Deepgram STT WebSocket")
                
                # Run microphone streaming and transcription receiving concurrently
                await asyncio.gather(
                    self.stream_microphone(websocket),
                    self.receive_transcriptions(websocket)
                )
                
        except Exception as e:
            logger.error(f"Deepgram connection error: {e}")
            self.is_listening = False
            return False
        
        return True
    
    def stop_listening(self):
        """Stop listening"""
        self.is_listening = False
        logger.info("Stopped listening")
    
    async def text_to_speech(self, text: str, voice: str = "aura-asteria-en") -> bytes:
        """Convert text to speech using Deepgram TTS"""
        if not self.api_key:
            logger.error("Cannot do TTS: DEEPGRAM_API_KEY not set")
            return b""
        
        url = f"{DEEPGRAM_TTS_URL}?model={voice}"
        headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json"
        }
        data = json.dumps({"text": text})
        
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, data=data) as response:
                    if response.status == 200:
                        audio_data = await response.read()
                        logger.info(f"TTS generated: {len(audio_data)} bytes")
                        return audio_data
                    else:
                        error_text = await response.text()
                        logger.error(f"TTS error: {response.status} - {error_text}")
                        return b""
        except Exception as e:
            logger.error(f"TTS request error: {e}")
            return b""
    
    def play_audio(self, audio_data: bytes):
        """Play audio through speakers"""
        try:
            stream = self.audio.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                output=True
            )
            
            # Write audio data in chunks
            chunk_size = 1024
            for i in range(0, len(audio_data), chunk_size):
                chunk = audio_data[i:i+chunk_size]
                stream.write(chunk)
            
            stream.stop_stream()
            stream.close()
            
        except Exception as e:
            logger.error(f"Audio playback error: {e}")
    
    def cleanup(self):
        """Cleanup resources"""
        self.stop_listening()
        self.audio.terminate()
        logger.info("Deepgram voice service cleaned up")


class DeepgramVoiceAgent:
    """High-level voice agent using Deepgram"""
    
    def __init__(self):
        self.voice_service = DeepgramVoiceService()
        self.conversation_history = []
        self.is_running = False
    
    async def start_conversation(self, on_user_speech: Callable[[str], None], on_ai_response: Callable[[str], None]):
        """Start a voice conversation"""
        self.is_running = True
        
        # Callback when user speaks
        async def handle_transcript(text: str):
            logger.info(f"User said: {text}")
            on_user_speech(text)
            
            # Get AI response (you'll integrate with your LLM here)
            ai_response = await self.get_ai_response(text)
            on_ai_response(ai_response)
            
            # Convert to speech and play
            audio_data = await self.voice_service.text_to_speech(ai_response)
            if audio_data:
                self.voice_service.play_audio(audio_data)
        
        # Start listening
        await self.voice_service.start_listening(handle_transcript)
    
    async def get_ai_response(self, user_message: str) -> str:
        """Get AI response - integrate with your LLM"""
        # Placeholder - integrate with your existing AI service
        # For now, return a simple response
        responses = {
            "hello": "Hello! Welcome to BookSmart AI Salon. How can I help you today?",
            "hi": "Hi there! What can I do for you?",
            "booking": "I can help you book an appointment. What service would you like?",
            "services": "We offer haircuts, styling, coloring, facials, manicures, pedicures, and massages.",
            "hours": "We're open Monday to Saturday 10 AM to 8 PM, and Sunday 10 AM to 5 PM.",
            "price": "Our prices vary by service. Haircuts start at ₹500. What service are you interested in?",
            "location": "We're located at 123 Main Street, City Center.",
            "contact": "You can reach us at +91-9876543210 or email info@booksmart.ai"
        }
        
        # Check for keywords
        message_lower = user_message.lower()
        for keyword, response in responses.items():
            if keyword in message_lower:
                return response
        
        return "I'm here to help! Could you tell me more about what you need?"
    
    def stop(self):
        """Stop the conversation"""
        self.is_running = False
        self.voice_service.stop_listening()
    
    def cleanup(self):
        """Cleanup"""
        self.stop()
        self.voice_service.cleanup()


# Convenience function for simple TTS
def speak_text(text: str, voice: str = "aura-asteria-en"):
    """Simple text-to-speech function"""
    import requests
    
    api_key = settings.DEEPGRAM_API_KEY
    if not api_key:
        print("Error: DEEPGRAM_API_KEY not set")
        return
    
    url = f"https://api.deepgram.com/v1/speak?model={voice}"
    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "application/json"
    }
    data = {"text": text}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            # Save to temp file and play
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as f:
                f.write(response.content)
                temp_file = f.name
            
            # Play audio
            os.system(f'start {temp_file}')  # Windows
            print(f"Speaking: {text}")
        else:
            print(f"TTS Error: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    # Test the service
    print("🎙️ Deepgram Voice Service Test")
    print("=" * 50)
    
    if not settings.DEEPGRAM_API_KEY:
        print("❌ Please set DEEPGRAM_API_KEY in .env")
        exit(1)
    
    print("✅ API Key configured")
    print("\nTest 1: Text-to-Speech")
    speak_text("Hello! This is BookSmart AI using Deepgram voice.")
    
    print("\n✅ Test complete!")
