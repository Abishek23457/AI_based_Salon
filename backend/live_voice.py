import os
import sys
import json
import time
import queue
import asyncio
import threading
import numpy as np
import pyaudio
import requests
from dotenv import load_dotenv
from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    LiveTranscriptionEvents,
    LiveOptions,
)

# Load environment variables
load_dotenv()

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
OPENROUTER_API_KEY = os.getenv("GEMINI_API_KEY") # User uses GEMINI_API_KEY but it's an OpenRouter key

# ─── Configuration ───────────────────────────────────────────────────────────
RATE = 16000
CHUNK = 1024
CHANNELS = 1
FORMAT = pyaudio.paInt16

# Voice Settings
VOICE = "aura-asteria-en"

# Queues for data flow
transcript_queue = queue.Queue()
audio_playback_queue = queue.Queue()

class VoiceAgent:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.mic_stream = None
        self.output_stream = None
        self.dg_client = DeepgramClient(DEEPGRAM_API_KEY)
        self.is_running = True
        self.is_thinking = False

    def start_audio(self):
        # Input Stream
        self.mic_stream = self.p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
        
        # Output Stream
        self.output_stream = self.p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=24000, # Deepgram TTS default
            output=True
        )

    def stop_audio(self):
        if self.mic_stream:
            self.mic_stream.stop_stream()
            self.mic_stream.close()
        if self.output_stream:
            self.output_stream.stop_stream()
            self.output_stream.close()
        self.p.terminate()

    async def run(self):
        self.start_audio()
        print("\n" + "="*60)
        print("      INSTANT BookSmart AI  |  Live Voice Agent ⚡")
        print("="*60)
        print("  Status: Always Listening & Responding")
        print("  [Press Ctrl+C to exit]\n")

        # Start Playback Thread
        threading.Thread(target=self.playback_worker, daemon=True).start()

        # Start Deepgram Live (Updated for SDK v3+)
        dg_connection = self.dg_client.listen.websocket.v("1")
        
        def on_message(self_dg, result, **kwargs):
            try:
                # Some versions pass result as a LiveResult object, some as JSON
                sentence = result.channel.alternatives[0].transcript
                if len(sentence.strip()) == 0:
                    return
                
                if result.is_final:
                    print(f"  You: {sentence}")
                    # Start AI processing in a task
                    asyncio.create_task(self.process_with_ai(sentence))
            except Exception as e:
                # Fallback for different SDK response formats
                pass

        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
        
        # Connect to Deepgram
        options = LiveOptions(
            model="nova-2",
            language="en-US",
            smart_format=True,
            encoding="linear16",
            channels=1,
            sample_rate=16000,
            endpointing=250, 
        )
        
        if not dg_connection.start(options):
            print("Failed to connect to Deepgram")
            return

        # Main Mic -> Deepgram Loop
        try:
            while self.is_running:
                data = self.mic_stream.read(CHUNK, exception_on_overflow=False)
                dg_connection.send(data)
                await asyncio.sleep(0.01)
        except KeyboardInterrupt:
            self.is_running = False
        finally:
            dg_connection.finish()
            self.stop_audio()

    async def process_with_ai(self, text):
        """Streaming AI Response + Streaming TTS."""
        if self.is_thinking: return # Avoid overlapping turns
        self.is_thinking = True
        
        try:
            print("  AI: ", end="", flush=True)
            
            # 1. Start OpenRouter Streaming
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "google/gemini-2.0-flash-001",
                "messages": [
                    {"role": "system", "content": "You are a warm salon receptionist. Keep it short (1-2 sentences)."},
                    {"role": "user", "content": text}
                ],
                "stream": True
            }
            
            import httpx
            async with httpx.AsyncClient() as client:
                async with client.stream("POST", url, headers=headers, json=payload, timeout=20) as resp:
                    current_sentence = ""
                    word_count = 0
                    async for line in resp.aiter_lines():
                        if not line.startswith("data: "): continue
                        if line == "data: [DONE]": break
                        
                        try:
                            data = json.loads(line[6:])
                            token = data["choices"][0]["delta"].get("content", "")
                            if token:
                                print(token, end="", flush=True)
                                current_sentence += token
                                
                                # Split by space to count words
                                words = current_sentence.split()
                                
                                # Trigger TTS every 3 words OR on punctuation
                                if len(words) >= 4 or any(c in token for c in [".", "!", "?", "\n"]):
                                    if current_sentence.strip():
                                        asyncio.create_task(self.stream_tts(current_sentence.strip()))
                                        current_sentence = ""
                        except:
                            continue
                    
                    # Last bit
                    if current_sentence.strip():
                        asyncio.create_task(self.stream_tts(current_sentence.strip()))
            
            print("\n")
        finally:
            self.is_thinking = False

    async def stream_tts(self, text):
        """Fetch TTS chunks and put in playback queue."""
        url = f"https://api.deepgram.com/v1/speak?model={VOICE}&encoding=linear16&sample_rate=24000&container=none"
        headers = {
            "Authorization": f"Token {DEEPGRAM_API_KEY}",
            "Content-Type": "application/json"
        }
        
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, headers=headers, json={"text": text}, timeout=10)
                if resp.status_code == 200:
                    audio_playback_queue.put(resp.content)
        except Exception as e:
            print(f"\n[TTS Error] {e}")

    def playback_worker(self):
        """Reads audio chunks from the queue and plays them."""
        while self.is_running:
            try:
                chunk = audio_playback_queue.get(timeout=0.1)
                if chunk:
                    self.output_stream.write(chunk)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[Playback Error] {e}")

def main():
    agent = VoiceAgent()
    try:
        asyncio.run(agent.run())
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
