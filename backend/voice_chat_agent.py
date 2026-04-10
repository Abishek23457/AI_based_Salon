"""
Voice Chat Agent - Speak LIVE with BookSmart AI Agent
Real-time voice conversation using Gemini 2.0 Flash Live API
"""
import asyncio
import os
import sys
import pyaudio
import numpy as np
from google import genai
from config import settings

# Audio Configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000  # Input rate
CHUNK = 1024
OUTPUT_RATE = 24000  # Gemini outputs at 24kHz

# BookSmart AI System Context
SYSTEM_PROMPT = """You are BookSmart AI, a friendly and professional salon receptionist for BookSmart AI Salon.

YOUR ROLE:
- Greet customers warmly when they call
- Help book appointments for salon services
- Answer questions about services, prices, hours, location
- Check availability and suggest times
- Be conversational but professional

SALON SERVICES:
- Haircut & Styling (30 min, ₹500)
- Hair Coloring (90 min, ₹2000)
- Facial Treatments (60 min, ₹1500)
- Manicure (45 min, ₹800)
- Pedicure (45 min, ₹800)
- Massage Therapy (60 min, ₹1800)
- Bridal Package (3 hours, ₹8000)

STYLISTS AVAILABLE:
- Priya: Haircut, Coloring, Bridal
- Rahul: Haircut, Facial, Massage
- Anita: Haircut, Coloring, Manicure, Pedicure
- Sonia: Facial, Manicure, Pedicure

HOURS: Mon-Sat 10AM-8PM, Sunday 10AM-5PM
LOCATION: 123 Main Street, City Center
CONTACT: +91-9876543210

CONVERSATION STYLE:
- Keep responses SHORT and CONVERSATIONAL (1-2 sentences)
- Speak naturally, like a real receptionist
- If they want to book, collect: service, date, time, name, phone
- Confirm details before finalizing
- Be helpful and friendly

IMPORTANT: You are in a voice call. Keep responses brief!"""

async def voice_chat_agent():
    """Main voice chat function"""
    print("\n" + "="*60)
    print("       🎙️  BookSmart AI - Voice Chat Agent")
    print("       (Real-time Speech-to-Speech)")
    print("="*60)
    print("\n📝 Instructions:")
    print("   • Speak naturally after you see '🎤 LIVE'")
    print("   • AI will respond with voice")
    print("   • Press Ctrl+C to end the call")
    print("\n" + "-"*60)
    
    # Check API key
    if not settings.GEMINI_API_KEY:
        print("\n❌ ERROR: GEMINI_API_KEY not found!")
        print("   Add your API key to .env file:")
        print("   GEMINI_API_KEY=your_key_here")
        return
    
    print("\n🔌 Connecting to AI Agent...")
    
    # Initialize Gemini client
    try:
        client = genai.Client(
            api_key=settings.GEMINI_API_KEY,
            http_options={'api_version': 'v1alpha'}
        )
    except Exception as e:
        print(f"\n❌ Failed to initialize AI client: {e}")
        return
    
    model_id = "gemini-2.0-flash-live-001"  # Live model
    
    config = {
        "generation_config": {
            "response_modalities": ["audio"],
            "speech_config": {
                "voice_config": {
                    "prebuilt_voice_config": {
                        "voice_name": "Aoede"  # Warm, friendly female voice
                    }
                }
            }
        },
        "system_instruction": SYSTEM_PROMPT
    }
    
    # Initialize PyAudio
    p = pyaudio.PyAudio()
    
    try:
        # Start the live connection
        async with client.aio.live.connect(model=model_id, config=config) as session:
            print("\n✅ CONNECTED!")
            print("🎤 LIVE - Start speaking now...\n")
            print("You: ", end="", flush=True)
            
            # Open microphone stream
            mic_stream = p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK
            )
            
            # Open speaker stream (Gemini outputs at 24kHz)
            speaker_stream = p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=OUTPUT_RATE,
                output=True
            )
            
            # Track if AI is speaking
            ai_speaking = False
            
            async def send_microphone_audio():
                """Continuously send mic audio to AI"""
                while True:
                    try:
                        # Read audio from microphone
                        data = mic_stream.read(CHUNK, exception_on_overflow=False)
                        # Send to AI session
                        await session.send(input=data)
                        await asyncio.sleep(0.001)  # Small delay
                    except Exception as e:
                        if "Stream closed" not in str(e):
                            print(f"\n[Mic Error: {e}]")
                        break
            
            async def receive_ai_audio():
                """Receive and play AI audio responses"""
                nonlocal ai_speaking
                while True:
                    try:
                        async for message in session.receive():
                            # Handle AI audio response
                            if message.server_content and message.server_content.model_turn:
                                for part in message.server_content.model_turn.parts:
                                    if part.inline_data:
                                        # Play audio through speakers
                                        ai_speaking = True
                                        speaker_stream.write(part.inline_data.data)
                                        ai_speaking = False
                                    
                                    # Handle text (for debugging)
                                    if part.text:
                                        if not ai_speaking:
                                            print(f"\nAI: {part.text}")
                                            print("\nYou: ", end="", flush=True)
                            
                            # Handle tool calls (for booking functions)
                            elif message.tool_call:
                                print(f"\n[Tool Call: {message.tool_call}]")
                                
                            # Handle interruptions
                            if message.server_content and message.server_content.interrupted:
                                print("\n[You interrupted - stopping AI...]")
                                speaker_stream.stop_stream()
                                speaker_stream.start_stream()
                                
                    except Exception as e:
                        if "Stream closed" not in str(e):
                            print(f"\n[AI Audio Error: {e}]")
                        break
            
            # Run both tasks concurrently
            await asyncio.gather(
                send_microphone_audio(),
                receive_ai_audio()
            )
            
    except KeyboardInterrupt:
        print("\n\n👋 Ending voice session...")
    except Exception as e:
        print(f"\n\n❌ Connection Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check if GEMINI_API_KEY is valid")
        print("2. Ensure microphone and speakers are connected")
        print("3. Try: pip install pyaudio google-genai")
    finally:
        # Cleanup
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
        p.terminate()
        print("\n✅ Session ended. Goodbye!")
        print("="*60)

def check_audio_devices():
    """Check available audio devices"""
    try:
        p = pyaudio.PyAudio()
        info = p.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        
        print("\n🎧 Audio Devices:")
        print("-" * 40)
        
        input_found = False
        output_found = False
        
        for i in range(numdevices):
            device_info = p.get_device_info_by_host_api_device_index(0, i)
            name = device_info.get('name')
            
            # Check input
            if device_info.get('maxInputChannels') > 0:
                print(f"  🎤 Input  {i}: {name}")
                input_found = True
                
            # Check output
            if device_info.get('maxOutputChannels') > 0:
                print(f"  🔊 Output {i}: {name}")
                output_found = True
        
        print("-" * 40)
        
        if not input_found:
            print("❌ No microphone found!")
        if not output_found:
            print("❌ No speakers found!")
        
        p.terminate()
        return input_found and output_found
        
    except Exception as e:
        print(f"\n❌ Error checking audio: {e}")
        return False

if __name__ == "__main__":
    print("🎙️  BookSmart AI Voice Chat Agent")
    
    # Check audio devices first
    if not check_audio_devices():
        print("\n⚠️  Audio device issue detected!")
        print("Please connect microphone and speakers, then try again.")
        sys.exit(1)
    
    # Start voice chat
    try:
        asyncio.run(voice_chat_agent())
    except KeyboardInterrupt:
        print("\n\nStopped by user.")
    except Exception as e:
        print(f"\n\nFatal Error: {e}")
        sys.exit(1)
