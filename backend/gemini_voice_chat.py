"""
Gemini Voice Chat - Live Speech-to-Speech
Uses Google Gemini 2.0 Flash Live API for real-time voice conversation
"""
import asyncio
import pyaudio
import sys
import os
from google import genai
from config import settings

# Audio Configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
INPUT_RATE = 16000   # Input: 16kHz
OUTPUT_RATE = 24000  # Gemini outputs at 24kHz
CHUNK = 1024

class GeminiVoiceChat:
    """Live voice chat with Gemini 2.0 Flash"""
    
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.client = None
        self.session = None
        self.is_running = False
        
    def print_banner(self):
        print("\n" + "="*60)
        print("       🎙️  Gemini 2.0 Flash - Live Voice Chat")
        print("="*60)
        print("\n📝 Instructions:")
        print("   • Speak naturally when you see '🎤 LIVE'")
        print("   • AI responds immediately with voice")
        print("   • Press Ctrl+C to exit")
        print("\n" + "-"*60)
    
    async def initialize(self):
        """Initialize Gemini client"""
        if not settings.GEMINI_API_KEY:
            print("\n❌ ERROR: GEMINI_API_KEY not found!")
            print("   Add to .env: GEMINI_API_KEY=your_key")
            return False
        
        try:
            self.client = genai.Client(
                api_key=settings.GEMINI_API_KEY,
                http_options={'api_version': 'v1alpha'}
            )
            print(f"✅ Gemini API: {settings.GEMINI_API_KEY[:15]}...")
            return True
        except Exception as e:
            print(f"\n❌ Failed to initialize Gemini: {e}")
            return False
    
    async def run_chat(self):
        """Main voice chat loop"""
        self.print_banner()
        
        # Initialize
        if not await self.initialize():
            return
        
        # Configuration for live session
        config = {
            "generation_config": {
                "response_modalities": ["audio"],
                "speech_config": {
                    "voice_config": {
                        "prebuilt_voice_config": {
                            "voice_name": "Aoede"  # Warm, friendly voice
                        }
                    }
                }
            },
            "system_instruction": """You are BookSmart AI, a friendly salon receptionist for BookSmart AI Salon.

SERVICES:
- Haircut (30 min, ₹500)
- Hair Coloring (90 min, ₹2000)  
- Facial (60 min, ₹1500)
- Manicure/Pedicure (45 min, ₹800)
- Massage (60 min, ₹1800)

STYLISTS: Priya, Rahul, Anita, Sonia
HOURS: Mon-Sat 10AM-8PM, Sun 10AM-5PM

Keep responses SHORT and conversational (1-2 sentences). Speak naturally like a real receptionist."""
        }
        
        print("🔌 Connecting to Gemini Live API...")
        
        try:
            async with self.client.aio.live.connect(
                model="gemini-2.0-flash-live-001",
                config=config
            ) as session:
                
                self.session = session
                self.is_running = True
                
                print("\n✅ CONNECTED!")
                print("🎤 LIVE - Start speaking now...\n")
                print("You: ", end="", flush=True)
                
                # Open microphone
                mic_stream = self.audio.open(
                    format=FORMAT,
                    channels=CHANNELS,
                    rate=INPUT_RATE,
                    input=True,
                    frames_per_buffer=CHUNK
                )
                
                # Open speaker (24kHz for Gemini output)
                speaker_stream = self.audio.open(
                    format=FORMAT,
                    channels=CHANNELS,
                    rate=OUTPUT_RATE,
                    output=True
                )
                
                async def send_audio():
                    """Send microphone audio to Gemini"""
                    while self.is_running:
                        try:
                            data = mic_stream.read(CHUNK, exception_on_overflow=False)
                            await session.send(input=data)
                            await asyncio.sleep(0.001)
                        except Exception as e:
                            if "Stream closed" not in str(e):
                                print(f"\n[Mic error: {e}]")
                            break
                
                async def receive_audio():
                    """Receive AI audio responses"""
                    while self.is_running:
                        try:
                            async for message in session.receive():
                                # Handle audio response
                                if message.server_content and message.server_content.model_turn:
                                    for part in message.server_content.model_turn.parts:
                                        if part.inline_data:
                                            # Play audio
                                            speaker_stream.write(part.inline_data.data)
                                        
                                        if part.text:
                                            print(f"\n🤖 AI: {part.text}")
                                            print("\nYou: ", end="", flush=True)
                                
                                # Handle interruption
                                if message.server_content and message.server_content.interrupted:
                                    print("\n[You interrupted - stopping...]")
                                    speaker_stream.stop_stream()
                                    speaker_stream.start_stream()
                                    print("You: ", end="", flush=True)
                                    
                        except Exception as e:
                            if "Stream closed" not in str(e):
                                print(f"\n[AI error: {e}]")
                            break
                
                # Run both tasks
                await asyncio.gather(send_audio(), receive_audio())
                
        except KeyboardInterrupt:
            print("\n\n👋 Stopping voice chat...")
        except Exception as e:
            print(f"\n\n❌ Error: {e}")
            print("\nTroubleshooting:")
            print("1. Check if GEMINI_API_KEY is valid")
            print("2. Ensure mic and speakers are connected")
            print("3. Try: pip install google-genai pyaudio")
        finally:
            self.is_running = False
            try:
                mic_stream.stop_stream()
                mic_stream.close()
            except:
                pass
            try:
                speaker_stream.stop_stream()
                speaker_stream.close()
            except:
                pass
            self.audio.terminate()
            print("\n✅ Session ended.")
            print("="*60)

def main():
    chat = GeminiVoiceChat()
    try:
        asyncio.run(chat.run_chat())
    except KeyboardInterrupt:
        print("\n\nStopped by user.")
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
