import asyncio
import base64
import json
import os
from typing import AsyncGenerator
import numpy as np
from google import genai
from config import settings
from database import SessionLocal
import models
import datetime

class EmulatedLiveSession:
    """Mock session for OpenRouter to mimic Google Live SDK interface."""
    def __init__(self, service):
        self.service = service
        self.audio_buffer = []
        self.is_connected = True
        self.current_responses = asyncio.Queue()

    async def send(self, input=None, end_of_stream=False, tool_response=None):
        if input:
            self.audio_buffer.append(input)
        
        # If we received enough audio, or 'end_of_stream' is sent, trigger AI
        # For simplicity in this app, we'll let the router/frontend handle the 'process' trigger
        # but the interface remains compatible.

    async def receive(self):
        """Yields messages from the response queue."""
        while self.is_connected:
            msg = await self.current_responses.get()
            if msg == "STOP": break
            yield msg

    async def process_utterance(self, audio_bytes: bytes):
        """Internal: Process a full audio utterance using STT -> LLM (Streaming) -> TTS."""
        import tempfile
        import wave
        import requests
        import httpx
        
        # 1. Transcribe (Deepgram - using existing logic for simplicity but optimized)
        url = "https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true"
        headers = {"Authorization": f"Token {settings.DEEPGRAM_API_KEY}", "Content-Type": "audio/wav"}
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            with wave.open(tmp.name, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(16000)
                wf.writeframes(audio_bytes)
            
            with open(tmp.name, "rb") as f:
                resp = requests.post(url, headers=headers, data=f, timeout=10)
        
        transcript = ""
        if resp.status_code == 200:
            transcript = resp.json().get("results", {}).get("channels", [{}])[0].get("alternatives", [{}])[0].get("transcript", "")
        
        if not transcript: return

        # 2. OpenRouter Chat (Streaming)
        api_url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {"Authorization": f"Bearer {settings.GEMINI_API_KEY}"}
        payload = {
            "model": "google/gemini-2.0-flash-001",
            "messages": [{"role": "system", "content": "You are a warm salon receptionist. Short (1-2 sentences)."}, {"role": "user", "content": transcript}],
            "stream": True
        }
        
        async with httpx.AsyncClient() as client:
            async with client.stream("POST", api_url, headers=headers, json=payload, timeout=20) as resp:
                full_text = ""
                sentence_buffer = ""
                async for line in resp.aiter_lines():
                    if not line.startswith("data: "): continue
                    if line == "data: [DONE]": break
                    try:
                        data = json.loads(line[6:])
                        token = data["choices"][0]["delta"].get("content", "")
                        if token:
                            full_text += token
                            sentence_buffer += token
                            
                            # Count words in buffer
                            word_count = len(sentence_buffer.strip().split())
                            
                            # Trigger TTS every 4 words OR on punctuation
                            if word_count >= 4 or any(c in token for c in [".", "!", "?", "\n"]):
                                await self._speak_and_emit(sentence_buffer.strip())
                                sentence_buffer = ""
                    except: continue
                
                if sentence_buffer.strip():
                    await self._speak_and_emit(sentence_buffer.strip())

    async def _speak_and_emit(self, text):
        """Helper to get TTS and emit to websocket queue."""
        if not text: return
        import requests
        tts_url = "https://api.deepgram.com/v1/speak?model=aura-asteria-en&encoding=linear16&sample_rate=24000&container=none"
        headers = {"Authorization": f"Token {settings.DEEPGRAM_API_KEY}", "Content-Type": "application/json"}
        resp = requests.post(tts_url, headers=headers, json={"text": text}, timeout=10)
        
        if resp.status_code == 200:
            mock_msg = type('obj', (object,), {
                'server_content': type('obj', (object,), {
                    'model_turn': type('obj', (object,), {
                        'parts': [type('obj', (object,), {'inline_data': type('obj', (object,), {'data': resp.content}), 'text': text})]
                    })
                }),
                'tool_call': None
            })
            await self.current_responses.put(mock_msg)

    async def __aenter__(self): return self
    async def __aexit__(self, exc_type, exc_val, exc_tb): self.is_connected = False

class GeminiLiveService:
    """Service to handle interaction with Gemini, supporting both native Live SDK and OpenRouter emulation."""
    
    def __init__(self, salon_id: int = 1):
        self.salon_id = salon_id
        self.model_id = "gemini-2.0-flash" 
        self.is_openrouter = settings.GEMINI_API_KEY.startswith("sk-or-v1-")
        
        if not self.is_openrouter:
            self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        else:
            self.client = None
            
        self.session = None
        self._context_manager = None

    async def connect(self):
        """Establish session (live or emulated)."""
        if not self.is_openrouter:
            config = {
                "generation_config": {
                    "response_modalities": ["audio"],
                    "speech_config": {"voice_config": {"prebuilt_voice_config": {"voice_name": "Puck"}}}
                },
                "system_instruction": "You are a warm salon receptionist. Short responses."
            }
            self._context_manager = self.client.aio.live.connect(model=self.model_id, config=config)
            self.session = await self._context_manager.__aenter__()
        else:
            # OpenRouter Emulation
            self.session = EmulatedLiveSession(self)
        return self.session

    async def disconnect(self):
        if not self.is_openrouter and self._context_manager:
            await self._context_manager.__aexit__(None, None, None)
        elif self.session:
            await self.session.__aexit__(None, None, None)
        self.session = None

    async def receive_events(self) -> AsyncGenerator[dict, None]:
        """Bridge events from the session to the service caller."""
        if not self.session: return

        if not self.is_openrouter:
            async for message in self.session.receive():
                if message.server_content and message.server_content.model_turn:
                    for part in message.server_content.model_turn.parts:
                        if part.inline_data:
                            yield {"type": "audio", "data": self._resample_24k_to_8k(part.inline_data.data)}
                        if part.text:
                            yield {"type": "text", "data": part.text}
                if message.tool_call:
                    # (Function calling omitted for brevity in emulated mode, but kept for SDK)
                    pass
        else:
            # Emulated events
            async for message in self.session.receive():
                if message.server_content and message.server_content.model_turn:
                    # Emulated mode returns 24k directly now
                    for part in message.server_content.model_turn.parts:
                        if part.inline_data:
                            yield {"type": "audio", "data": part.inline_data.data}
                        if part.text:
                            yield {"type": "text", "data": part.text}

    def _resample_24k_to_8k(self, audio_24k: bytes) -> bytes:
        audio_np = np.frombuffer(audio_24k, dtype=np.int16)
        audio_8k = audio_np[::3]
        return audio_8k.tobytes()

    async def send_audio(self, audio_pcm_16k: bytes):
        """Send audio to the session."""
        if self.session:
            await self.session.send(input=audio_pcm_16k)


    async def _handle_function_call(self, call) -> dict:
        """Execute the requested tool."""
        db = SessionLocal()
        try:
            if call.name == "search_services":
                query = call.args.get("query", "").lower()
                services = db.query(models.Service).filter(models.Service.salon_id == self.salon_id).all()
                results = [{"name": s.name, "price": s.price} for s in services if query in s.name.lower()]
                return {"services": results or "No services found matching that description."}

            elif call.name == "check_availability":
                date_str = call.args.get("date")
                time_str = call.args.get("time")
                try:
                    appt_time = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
                    from routers.bookings import _check_conflicts
                    conflict = _check_conflicts(db, None, None, appt_time)
                    if conflict:
                        return {"available": False, "message": "That slot is already booked. Please suggest another time."}
                    return {"available": True, "message": f"Yes, {date_str} at {time_str} is available."}
                except ValueError:
                    return {"available": False, "message": "Invalid date or time format. Please use YYYY-MM-DD and HH:MM."}

            elif call.name == "book_appointment":
                service_name = call.args.get("service_name")
                customer_name = call.args.get("customer_name")
                customer_phone = call.args.get("customer_phone")
                time_str = call.args.get("appointment_time")
                
                try:
                    service = db.query(models.Service).filter(
                        models.Service.salon_id == self.salon_id,
                        models.Service.name.ilike(f"%{service_name}%")
                    ).first()
                    
                    if not service:
                        return {"status": "error", "message": f"Service '{service_name}' not found."}

                    appt_time = datetime.datetime.fromisoformat(time_str.replace("Z", "+00:00"))
                    
                    booking = models.Booking(
                        salon_id=self.salon_id,
                        service_id=service.id,
                        customer_name=customer_name,
                        customer_phone=customer_phone,
                        appointment_time=appt_time,
                        status="confirmed"
                    )
                    db.add(booking)
                    db.commit()
                    db.refresh(booking)
                    
                    return {
                        "status": "success", 
                        "reference": f"BK{booking.id}",
                        "message": f"Booking confirmed for {service_name} at {time_str}."
                    }
                except Exception as e:
                    return {"status": "error", "message": f"Failed to book: {str(e)}"}
            
            return {"error": "Unknown function"}
        finally:
            db.close()
