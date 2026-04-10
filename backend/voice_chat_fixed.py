"""
Simple Voice Chat - Record -> Transcribe -> AI -> Speak
Reliable version without WebSocket complexity
"""
import asyncio
import os
import sys
import wave
import tempfile
import requests
import json
import pyaudio
from datetime import datetime
from config import settings

# Audio settings
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024

class SimpleVoiceChat:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.conversation_history = []
        
    def print_banner(self):
        print("\n" + "="*60)
        print("       BookSmart AI - Simple Voice Chat")
        print("="*60)
        print("\nHow it works:")
        print("   1. Press ENTER to start recording")
        print("   2. Speak for 3-5 seconds")
        print("   3. Recording stops automatically")
        print("   4. AI transcribes -> responds -> speaks")
        print("   5. Press Ctrl+C to exit")
        print("\n" + "-"*60)
    
    def record_audio(self, duration=5):
        """Record audio for specified duration"""
        print(f"\n[Recording for {duration} seconds...] ", end="", flush=True)
        
        stream = self.audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
        
        frames = []
        for i in range(int(RATE / CHUNK * duration)):
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)
            if i % 15 == 0:
                print(".", end="", flush=True)
        
        print(" DONE")
        
        stream.stop_stream()
        stream.close()
        
        # Save to temp WAV file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as f:
            wf = wave.open(f.name, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(self.audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            return f.name
    
    def transcribe_audio(self, audio_file):
        """Transcribe audio using Deepgram"""
        if not settings.DEEPGRAM_API_KEY:
            print("[ERROR] DEEPGRAM_API_KEY not set!")
            return None
        
        print("[Transcribing...] ", end="", flush=True)
        
        try:
            url = "https://api.deepgram.com/v1/listen"
            headers = {
                "Authorization": f"Token {settings.DEEPGRAM_API_KEY}",
                "Content-Type": "audio/wav"
            }
            
            with open(audio_file, 'rb') as f:
                response = requests.post(url, headers=headers, data=f, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                transcript = result.get("results", {}).get("channels", [{}])[0].get("alternatives", [{}])[0].get("transcript", "")
                print(f"OK")
                return transcript
            else:
                print(f"ERROR {response.status_code}")
                print(f"   {response.text[:100]}")
                return None
                
        except Exception as e:
            print(f"ERROR: {e}")
            return None
    
    def get_ai_response(self, user_message):
        """Get AI response using Gemini or OpenRouter"""
        print("[AI thinking...] ", end="", flush=True)
        
        try:
            # Detect OpenRouter key
            if settings.GEMINI_API_KEY.startswith("sk-or-v1-"):
                url = "https://openrouter.ai/api/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {settings.GEMINI_API_KEY}",
                    "Content-Type": "application/json"
                }
                
                system_prompt = """You are BookSmart AI, a friendly salon receptionist.
You help customers book appointments. Keep responses SHORT (1-2 sentences).
Services: Haircut, Coloring, Facial, Manicure, Pedicure, Massage.
Hours: Mon-Sat 10AM-8PM, Sun 10AM-5PM."""
                
                data = {
                    "model": "google/gemini-2.0-flash-001",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    "max_tokens": 150
                }
                
                response = requests.post(url, headers=headers, json=data, timeout=12)
                
                if response.status_code == 200:
                    result = response.json()
                    answer = result["choices"][0]["message"]["content"]
                    print("OK (OpenRouter)")
                    return answer
                else:
                    print(f"ERROR {response.status_code} (OpenRouter)")
                    print(f"   {response.text[:100]}")
                    return "Sorry, I'm having trouble connecting to the OpenRouter service."

            # Native Gemini SDK (for AIza... keys)
            elif settings.GEMINI_API_KEY:
                from google import genai
                client = genai.Client(api_key=settings.GEMINI_API_KEY)
                
                system_prompt = """You are BookSmart AI, a friendly salon receptionist.
You help customers book appointments. Keep responses SHORT (1-2 sentences).
Services: Haircut, Coloring, Facial, Manicure, Pedicure, Massage.
Hours: Mon-Sat 10AM-8PM, Sun 10AM-5PM."""
                
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    config={"system_instruction": system_prompt},
                    contents=user_message
                )
                
                print("OK (Google)")
                return response.text
            
            # Fallback to Groq
            elif settings.GROQ_API_KEY:
                url = "https://api.groq.com/openai/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                    "Content-Type": "application/json"
                }
                
                system_prompt = """You are BookSmart AI, a friendly salon receptionist.
Keep responses SHORT (1-2 sentences)."""
                
                data = {
                    "model": "llama3-8b-8192",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    "max_tokens": 100,
                    "temperature": 0.7
                }
                
                response = requests.post(url, headers=headers, json=data, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    print("OK")
                    return result["choices"][0]["message"]["content"]
                else:
                    print(f"ERROR {response.status_code}")
                    return "I'm having trouble. Please try again."
            else:
                print("ERROR: No AI API key set")
                return "I'm not configured properly."
                
        except Exception as e:
            print(f"ERROR: {e}")
            return "Sorry, I couldn't process that."
    
    def speak_response(self, text):
        """Convert text to speech using Deepgram TTS"""
        if not settings.DEEPGRAM_API_KEY:
            print("[TTS: DEEPGRAM_API_KEY not set - printing only]")
            print(f"AI: {text}")
            return
        
        print("[Speaking...] ", end="", flush=True)
        
        try:
            # Deepgram Aura TTS — request linear16 PCM so pyaudio can play it directly
            url = (
                "https://api.deepgram.com/v1/speak"
                "?model=aura-asteria-en"
                "&encoding=linear16"
                "&sample_rate=24000"
                "&container=none"
            )
            headers = {
                "Authorization": f"Token {settings.DEEPGRAM_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = json.dumps({"text": text[:500]})
            
            response = requests.post(url, headers=headers, data=payload, timeout=15)
            
            if response.status_code == 200:
                audio_data = response.content
                
                if len(audio_data) < 100:
                    print("WARNING: Empty audio received")
                    print(f"AI: {text}")
                    return
                
                # Play audio through speakers
                stream = self.audio.open(
                    format=FORMAT,
                    channels=CHANNELS,
                    rate=24000,
                    output=True
                )
                
                # Write in chunks for smooth playback
                chunk_size = 2048
                for i in range(0, len(audio_data), chunk_size):
                    chunk = audio_data[i:i+chunk_size]
                    stream.write(chunk)
                
                stream.stop_stream()
                stream.close()
                print("OK")
            else:
                print(f"ERROR {response.status_code}: {response.text[:80]}")
                print(f"AI: {text}")
                
        except Exception as e:
            print(f"ERROR: {e}")
            print(f"AI: {text}")
    
    async def run(self):
        """Main chat loop"""
        self.print_banner()
        
        # Check API keys
        if not settings.DEEPGRAM_API_KEY:
            print("[ERROR] DEEPGRAM_API_KEY not found!")
            print("   Add to .env: DEEPGRAM_API_KEY=your_key")
            return
        
        if not settings.GEMINI_API_KEY and not settings.GROQ_API_KEY:
            print("[ERROR] No AI API key found!")
            print("   Add to .env: GEMINI_API_KEY=your_key")
            return
        
        print(f"[OK] Deepgram API: {settings.DEEPGRAM_API_KEY[:10]}...")
        if settings.GEMINI_API_KEY:
            print(f"[OK] Gemini API: {settings.GEMINI_API_KEY[:10]}...")
        if settings.GROQ_API_KEY:
            print(f"[OK] Groq API: {settings.GROQ_API_KEY[:10]}...")
        print("\n[Ready! Press ENTER to speak]\n")
        
        while True:
            try:
                input("[Press ENTER to speak (or Ctrl+C to exit)]")
                
                # Record audio
                audio_file = self.record_audio(duration=5)
                
                # Transcribe
                user_text = self.transcribe_audio(audio_file)
                
                # Cleanup temp file
                os.unlink(audio_file)
                
                if not user_text:
                    print("[Could not understand. Try again.]")
                    continue
                
                print(f"\nYou: \"{user_text}\"")
                
                # Get AI response
                ai_response = self.get_ai_response(user_text)
                print(f"AI: \"{ai_response}\"")
                
                # Speak response
                self.speak_response(ai_response)
                
                print()  # Blank line for readability
                
            except KeyboardInterrupt:
                print("\n\n[Goodbye!]")
                break
            except Exception as e:
                print(f"\n[Error: {e}]")
                continue
        
        self.audio.terminate()

def main():
    chat = SimpleVoiceChat()
    try:
        asyncio.run(chat.run())
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
