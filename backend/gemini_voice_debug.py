"""
Debug version of Gemini Voice Chat
"""
import asyncio
import pyaudio
import sys
from google import genai
from config import settings

print("="*60)
print("Gemini Voice Chat - Debug Mode")
print("="*60)

# Check API key
if not settings.GEMINI_API_KEY:
    print("\nERROR: GEMINI_API_KEY not set!")
    sys.exit(1)

print(f"\n[OK] API Key: {settings.GEMINI_API_KEY[:15]}...")

# Initialize client
print("\n[1/4] Initializing Gemini client...")
try:
    client = genai.Client(
        api_key=settings.GEMINI_API_KEY,
        http_options={'api_version': 'v1alpha'}
    )
    print("[OK] Client initialized")
except Exception as e:
    print(f"[ERROR] Failed to initialize: {e}")
    sys.exit(1)

# Check PyAudio
print("\n[2/4] Checking audio...")
try:
    audio = pyaudio.PyAudio()
    devices = audio.get_device_count()
    print(f"[OK] {devices} audio devices found")
    
    # List devices
    for i in range(min(devices, 5)):
        info = audio.get_device_info_by_index(i)
        print(f"   Device {i}: {info['name'][:40]}")
    
    audio.terminate()
except Exception as e:
    print(f"[ERROR] Audio check failed: {e}")
    sys.exit(1)

# Connect to live API
print("\n[3/4] Connecting to Gemini Live API...")
print("   This may take a few seconds...")

config = {
    "generation_config": {
        "response_modalities": ["audio"],
        "speech_config": {
            "voice_config": {
                "prebuilt_voice_config": {
                    "voice_name": "Aoede"
                }
            }
        }
    },
    "system_instruction": "You are a friendly receptionist for BookSmart AI Salon. Keep responses short."
}

async def test_connection():
    try:
        async with client.aio.live.connect(
            model="gemini-2.0-flash-exp",
            config=config
        ) as session:
            print("[OK] Connected to Live API!")
            print("\n[4/4] Starting voice stream...")
            
            # Initialize audio
            audio = pyaudio.PyAudio()
            
            mic = audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=1024
            )
            
            speaker = audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=24000,
                output=True
            )
            
            print("\n" + "="*60)
            print("LIVE - Start speaking now!")
            print("="*60)
            
            async def send():
                while True:
                    try:
                        data = mic.read(1024, exception_on_overflow=False)
                        await session.send(input=data)
                        await asyncio.sleep(0.001)
                    except:
                        break
            
            async def receive():
                async for msg in session.receive():
                    if msg.server_content and msg.server_content.model_turn:
                        for part in msg.server_content.model_turn.parts:
                            if part.inline_data:
                                speaker.write(part.inline_data.data)
                            if part.text:
                                print(f"\nAI: {part.text}")
            
            await asyncio.gather(send(), receive())
            
    except Exception as e:
        print(f"\n[ERROR] {e}")
        print("\nPossible issues:")
        print("1. API key may not have Live API access")
        print("2. Network connection issue")
        print("3. Model name may have changed")

try:
    asyncio.run(test_connection())
except KeyboardInterrupt:
    print("\n\nStopped by user")
except Exception as e:
    print(f"\n\nFatal error: {e}")
