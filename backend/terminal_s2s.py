import asyncio
import os
import sys
import pyaudio
import base64
from google import genai
from config import settings

# Audio Configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000 
CHUNK = 1024  

async def terminal_s2s():
    print("\n" + "="*50)
    print("      BookSmart AI | Terminal S2S Agent")
    print("      (Talking to Gemini 2.0 Flash Live)")
    print("="*50)
    print("Status: Initializing...")

    # Initialize client for Google AI Studio (Default)
    # Using v1alpha specifically for the Multimodal Live API
    client = genai.Client(
        api_key=settings.GEMINI_API_KEY,
        http_options={'api_version': 'v1alpha'}
    )
    
    model_id = "gemini-2.0-flash"
    
    config = {
        "generation_config": {
            "response_modalities": ["audio"],
        },
        "system_instruction": "You are a warm receptionist. Keep it very short."
    }

    p = pyaudio.PyAudio()

    try:
        # Start the connection
        async with client.aio.live.connect(model=model_id, config=config) as session:
            print("[System] S2S Agent LIVE. Start speaking now!\n")

            # Open Microphone
            mic_stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
            # Open Speaker (24kHz is standard Gemini output)
            speaker_stream = p.open(format=FORMAT, channels=CHANNELS, rate=24000, output=True)

            async def send_mic_audio():
                while True:
                    try:
                        data = mic_stream.read(CHUNK, exception_on_overflow=False)
                        await session.send(input=data)
                        await asyncio.sleep(0.01)
                    except Exception as e:
                        print(f"Mic Error: {e}")
                        break

            async def receive_ai_audio():
                async for message in session.receive():
                    if message.server_content and message.server_content.model_turn:
                        for part in message.server_content.model_turn.parts:
                            if part.inline_data:
                                speaker_stream.write(part.inline_data.data)
                            if part.text:
                                print(f"AI: {part.text}")
                    elif message.tool_call:
                        print("\n[Tool Call Requested]")

            await asyncio.gather(send_mic_audio(), receive_ai_audio())

    except Exception as e:
        print(f"\n[Connection Error] {e}")
        print("\nPossible fix: Check if your API key has 'Multimodal Live API' access in AI Studio.")
    finally:
        p.terminate()
        print("\nSession ended.")

if __name__ == "__main__":
    try:
        asyncio.run(terminal_s2s())
    except KeyboardInterrupt:
        print("\nStopped.")
