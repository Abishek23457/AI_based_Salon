import asyncio
import base64
import json
import numpy as np
from fastapi import APIRouter, WebSocket
from gemini_live_service import GeminiLiveService
from database import SessionLocal
import models

router = APIRouter(tags=["Browser Voice"])

@router.websocket("/ws/browser")
async def browser_voice_websocket(websocket: WebSocket):
    await websocket.accept()
    
    # Initialize the Gemini Live Service
    # (Using salon_id=1 as default for testing)
    live_service = GeminiLiveService(salon_id=1)
    
    try:
        # 1. Connect to Gemini Live API
        await live_service.connect()
        
        # 2. Start a task to receive events from Gemini and send to Browser
        async def receive_from_gemini():
            try:
                async for event in live_service.receive_events():
                    # Send everything to browser (audio for playback, text/tool for UI)
                    if event["type"] == "audio":
                        # Gemini returns 24kHz PCM. 
                        # We send it as is; Browser can handle 24kHz easily.
                        audio_b64 = base64.b64encode(event["data"]).decode("utf-8")
                        await websocket.send_json({"type": "audio", "data": audio_b64})
                    else:
                        await websocket.send_json(event)
            except Exception as e:
                print(f"[Browser Bridge] Gemini receive error: {e}")
                await websocket.send_json({"type": "error", "message": str(e)})

        receive_task = asyncio.create_task(receive_from_gemini())

        # 3. Main loop to receive audio from Browser
        while True:
            # Expecting JSON with "type" and "data" (base64 audio) or "event"
            message = await websocket.receive_text()
            msg = json.loads(message)
            
            if msg.get("type") == "audio" and live_service.session:
                audio_data = base64.b64decode(msg["data"])
                # Send to session
                await live_service.session.send(input=audio_data)
            
            elif msg.get("type") == "process" and live_service.is_openrouter:
                # In OpenRouter mode, the client tells us when silence was detected
                # We process the accumulated buffer
                if hasattr(live_service.session, 'audio_buffer'):
                    full_audio = b"".join(live_service.session.audio_buffer)
                    live_service.session.audio_buffer = [] # Clear for next turn
                    # Process in background so we can still receive
                    asyncio.create_task(live_service.session.process_utterance(full_audio))

            elif msg.get("type") == "stop":
                break

    except Exception as e:
        print(f"[Browser Bridge] Session closed: {e}")
    finally:
        if 'receive_task' in locals():
            receive_task.cancel()
        await websocket.close()
