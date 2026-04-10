"""
Production-Ready Google S2S Voice Handler for BookSmart AI
- Real-time Speech-to-Speech (S2S) via Exotel
- Full Call Logging, Transcription & MP3 Recording
- Barge-in (Interruption) Support
"""
import base64
import json
import struct
import asyncio
import httpx
import datetime
import os
import wave
# Removed audioop as it is deprecated in Python 3.13
import lameenc
from fastapi import APIRouter, WebSocket, Request, Form
from fastapi.responses import Response
from config import settings
from llm_chain import stream_chat
from gemini_live_service import GeminiLiveService
from database import SessionLocal
import models

router = APIRouter(tags=["Voice AI"])

GOOGLE_TTS_API_KEY = settings.GOOGLE_TTS_API_KEY
RECORDINGS_DIR = os.path.join(os.path.dirname(__file__), "recordings")
os.makedirs(RECORDINGS_DIR, exist_ok=True)

def _pcm_to_mulaw(pcm_data: bytes) -> bytes:
    """Convert 16-bit PCM samples to 8-bit μ-law for Exotel (Manual)."""
    MULAW_MAX = 0x1FFF
    MULAW_BIAS = 33
    result = bytearray()
    for i in range(0, len(pcm_data) - 1, 2):
        sample = struct.unpack_from("<h", pcm_data, i)[0]
        sign = (sample >> 8) & 0x80
        if sign:
            sample = -sample
        sample = min(sample + MULAW_BIAS, MULAW_MAX)
        exponent = 7
        for exp_val in [0x4000, 0x2000, 0x1000, 0x0800, 0x0400, 0x0200, 0x0100]:
            if sample >= exp_val:
                break
            exponent -= 1
        mantissa = (sample >> (exponent + 3)) & 0x0F
        mulaw_byte = ~(sign | (exponent << 4) | mantissa) & 0xFF
        result.append(mulaw_byte)
    return bytes(result)

def _mulaw_to_pcm(mulaw_data: bytes) -> bytes:
    """Convert 8-bit μ-law to 16-bit PCM (Manual)."""
    result = bytearray()
    for b in mulaw_data:
        # bitwise inversion
        b = ~b & 0xFF
        sign = b & 0x80
        exponent = (b >> 4) & 0x07
        mantissa = b & 0x0F
        sample = (mantissa << 3) + 132
        sample <<= exponent
        sample -= 132
        if sign:
            sample = -sample
        result.extend(struct.pack("<h", int(sample)))
    return bytes(result)

async def generate_tts_audio_chunk(text: str) -> bytes:
    if not GOOGLE_TTS_API_KEY:
        return b""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"https://texttospeech.googleapis.com/v1/text:synthesize?key={GOOGLE_TTS_API_KEY}",
                json={
                    "input": {"text": text},
                    "voice": {"languageCode": "en-IN", "name": "en-IN-Wavenet-D", "ssmlGender": "FEMALE"},
                    "audioConfig": {"audioEncoding": "LINEAR16", "sampleRateHertz": 8000},
                },
            )
            if response.status_code == 200:
                audio_content = base64.b64decode(response.json()["audioContent"])
                if audio_content[:4] == b"RIFF": audio_content = audio_content[44:]
                return _pcm_to_mulaw(audio_content)
    except Exception as e:
        print(f"[TTS] Error: {e}")
    return b""

async def transcribe_with_google(audio_bytes: bytes) -> str:
    if not GOOGLE_TTS_API_KEY: return ""
    try:
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"https://speech.googleapis.com/v1/speech:recognize?key={GOOGLE_TTS_API_KEY}",
                json={
                    "config": {"encoding": "MULAW", "sampleRateHertz": 8000, "languageCode": "en-IN"},
                    "audio": {"content": audio_b64},
                },
            )
            if response.status_code == 200:
                results = response.json().get("results", [])
                if results: return results[0].get("alternatives", [{}])[0].get("transcript", "")
    except Exception as e:
        print(f"[STT] Error: {e}")
    return ""

def save_voice_recording(call_sid: str, mulaw_audio: bytes):
    """Save μ-law bytes as playable WAV and MP3 files."""
    if not mulaw_audio: return None
    try:
        pcm_audio = _mulaw_to_pcm(mulaw_audio)
        wav_filename = f"{call_sid}.wav"
        wav_path = os.path.join(RECORDINGS_DIR, wav_filename)
        with wave.open(wav_path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(8000)
            wf.writeframes(pcm_audio)
        
        mp3_filename = f"{call_sid}.mp3"
        mp3_path = os.path.join(RECORDINGS_DIR, mp3_filename)
        encoder = lameenc.Encoder()
        encoder.set_bit_rate(64)
        encoder.set_in_sample_rate(8000)
        encoder.set_channels(1)
        encoder.set_quality(2)
        mp3_data = encoder.encode(pcm_audio)
        mp3_data += encoder.flush()
        with open(mp3_path, 'wb') as f:
            f.write(mp3_data)
        return f"/recordings/{mp3_filename}"
    except Exception as e:
        print(f"[Recording] Save failed: {e}")
        return None

@router.post("/incoming-call")
async def exotel_incoming_call(
    request: Request, 
    CallSid: str = Form(...), 
    From: str = Form(...)
):
    """Initial webhook from Exotel. Log the call and connect to WebSocket."""
    db = SessionLocal()
    try:
        log = db.query(models.CallLog).filter(models.CallLog.call_sid == CallSid).first()
        if not log:
            log = models.CallLog(
                call_sid=CallSid,
                from_number=From,
                salon_id=1,
                status="in-progress",
                created_at=datetime.datetime.utcnow()
            )
            db.add(log)
            db.commit()
    finally:
        db.close()

    host = request.headers.get("host", "localhost:8000")
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Connect>
        <Stream url="wss://{host}/exotel/ws/voice" />
    </Connect>
</Response>"""
    return Response(content=twiml, media_type="application/xml")

@router.websocket("/ws/voice")
async def exotel_voice_websocket(websocket: WebSocket):
    await websocket.accept()
    db = SessionLocal()
    salon_id = 1
    call_sid = None
    transcript_log = []
    full_audio_buffer = bytearray()
    audio_buffer = bytearray()
    
    live_service = GeminiLiveService(salon_id=salon_id)
    
    try:
        # Establish connection with Gemini Live API
        await live_service.connect()
        
        # Start a task to receive events from Gemini in parallel
        async def receive_from_gemini():
            try:
                async for event in live_service.receive_events():
                    if event["type"] == "audio":
                        audio_chunk = event["data"]
                        # Convert Gemini PCM to Exotel μ-law
                        mulaw_chunk = _pcm_to_mulaw(audio_chunk)
                        if mulaw_chunk:
                            # 1. Send to caller
                            await websocket.send_json({
                                "event": "media",
                                "media": {"payload": base64.b64encode(mulaw_chunk).decode("utf-8")}
                            })
                            # 2. Capture in buffer for dual-sided recording
                            full_audio_buffer.extend(mulaw_chunk)
                    
                    elif event["type"] == "text":
                        transcript_log.append(f"AI: {event['data']}")
                    
                    elif event["type"] == "thought":
                        transcript_log.append(f"AI Thought: {event['data']}")
                    
                    elif event["type"] == "tool":
                        transcript_log.append(f"Tool [{event['name']}]: {json.dumps(event['args'])} -> {json.dumps(event['result'])}")
                        # Map tool results to CallLog metadata
                        try:
                            log = db.query(models.CallLog).filter(models.CallLog.call_sid == call_sid).first()
                            if log:
                                if event["name"] == "book_appointment":
                                    log.service = event["args"].get("service_name")
                                    log.phone = event["args"].get("customer_phone")
                                    log.customer_name = event["args"].get("customer_name")
                                    log.booking_reference = event["result"].get("reference")
                                elif event["name"] == "check_availability":
                                    log.date = event["args"].get("date")
                                    log.time = event["args"].get("time")
                                db.commit()
                        except Exception as e:
                            print(f"[Metadata] Failed to update CallLog: {e}")

            except Exception as e:
                print(f"[Gemini Bridge] Error receiving: {e}")

        receive_task = asyncio.create_task(receive_from_gemini())

        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            
            if msg.get("event") == "media":
                if not call_sid and "streamSid" in msg:
                    call_sid = msg["streamSid"]

                # Decode Exotel μ-law to 8kHz PCM
                payload = base64.b64decode(msg["media"]["payload"])
                pcm_8k = _mulaw_to_pcm(payload)
                
                # Send to Gemini Live (service handles resampling to 16k)
                await live_service.send_audio(pcm_8k)
                
                # Also buffer for recording
                full_audio_buffer.extend(payload)

            elif msg.get("event") == "stop":
                break

        receive_task.cancel()
    except Exception as e:
        print(f"[S2S] WebSocket session ended: {e}")
    finally:
        if call_sid:
            recording_url = save_voice_recording(call_sid, bytes(full_audio_buffer))
            log = db.query(models.CallLog).filter(models.CallLog.call_sid == call_sid).first()
            if log:
                log.status = "completed"
                log.ai_transcript = "\n".join(transcript_log)
                log.recording_url = recording_url
                log.ended_at = datetime.datetime.utcnow()
                db.commit()
        db.close()
