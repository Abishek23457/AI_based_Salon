"""
Simple Voice Chat - Record → Transcribe → AI → Speak
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
        print("       🎙️  BookSmart AI - Simple Voice Chat")
        print("="*60)
        print("\n📝 How it works:")
        print("   1. Press ENTER to start recording")
        print("   2. Speak for 3-5 seconds")
        print("   3. Recording stops automatically")
        print("   4. AI transcribes → responds → speaks")
        print("   5. Press Ctrl+C to exit")
        print("\n" + "-"*60)
    
    def record_audio(self, duration=5):
        """Record audio for specified duration"""
        print(f"\n🎤 Recording for {duration} seconds... ", end="", flush=True)
        
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
                print("●", end="", flush=True)
        
        print(" ✓")
        
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
            print("❌ DEEPGRAM_API_KEY not set!")
            return None
        
        print("📝 Transcribing... ", end="", flush=True)
        
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
                print(f"✓")
                return transcript
            else:
                print(f"✗ (Error {response.status_code})")
                print(f"   {response.text[:100]}")
                return None
                
        except Exception as e:
            print(f"✗ Error: {e}")
            return None
    
    def get_ai_response(self, user_message):
        """Get AI response using Groq"""
        if not settings.GROQ_API_KEY:
            print("❌ GROQ_API_KEY not set!")
            return "I'm not configured properly. Please contact support."
        
        print("🤖 AI thinking... ", end="", flush=True)
        
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            
            system_prompt = """You are BookSmart AI, a friendly salon receptionist.
You help customers book appointments. Keep responses SHORT (1-2 sentences).
Services: Haircut, Coloring, Facial, Manicure, Pedicure, Massage.
Hours: Mon-Sat 10AM-8PM, Sun 10AM-5PM."""
            
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
                ai_response = result["choices"][0]["message"]["content"]
                print("✓")
                return ai_response
            else:
                print(f"✗ (Error {response.status_code})")
                return "I'm having trouble. Please try again."
                
        except Exception as e:
            print(f"✗ Error: {e}")
            return "Sorry, I couldn't process that."
    
    def speak_response(self, text):
        """Convert text to speech using Deepgram TTS"""
        if not settings.DEEPGRAM_API_KEY:
            print("❌ Cannot speak: DEEPGRAM_API_KEY not set")
            return
        
        print("🔊 Speaking... ", end="", flush=True)
        
        try:
            url = "https://api.deepgram.com/v1/speak?model=aura-asteria-en"
            headers = {
                "Authorization": f"Token {settings.DEEPGRAM_API_KEY}",
                "Content-Type": "application/json"
            }
            data = json.dumps({"text": text})
            
            response = requests.post(url, headers=headers, data=data, timeout=15)
            
            if response.status_code == 200:
                audio_data = response.content
                
                # Play audio
                stream = self.audio.open(
                    format=FORMAT,
                    channels=CHANNELS,
                    rate=24000,  # Deepgram TTS outputs at 24kHz
                    output=True
                )
                
                # Write in chunks
                chunk_size = 1024
                for i in range(0, len(audio_data), chunk_size):
                    chunk = audio_data[i:i+chunk_size]
                    stream.write(chunk)
                
                stream.stop_stream()
                stream.close()
                print("✓")
            else:
                print(f"✗ (Error {response.status_code})")
                
        except Exception as e:
            print(f"✗ Error: {e}")
    
    async def run(self):
        """Main chat loop"""
        self.print_banner()
        
        # Check API keys
        if not settings.DEEPGRAM_API_KEY:
            print("❌ DEEPGRAM_API_KEY not found!")
            print("   Add to .env: DEEPGRAM_API_KEY=your_key")
            return
        
        if not settings.GROQ_API_KEY:
            print("❌ GROQ_API_KEY not found!")
            print("   Add to .env: GROQ_API_KEY=your_key")
            return
        
        print(f"✅ Deepgram API: {settings.DEEPGRAM_API_KEY[:10]}...")
        print(f"✅ Groq API: {settings.GROQ_API_KEY[:10]}...")
        print("\n🎤 Ready! Press ENTER to start speaking.\n")
        
        while True:
            try:
                # Wait for user to press ENTER
                input("[Press ENTER to speak (or Ctrl+C to exit)]")
                
                # Record audio
                audio_file = self.record_audio(duration=5)
                
                # Transcribe
                user_text = self.transcribe_audio(audio_file)
                
                # Cleanup temp file
                os.unlink(audio_file)
                
                if not user_text:
                    print("❌ Could not understand. Try again.")
                    continue
                
                print(f"👤 You said: \"{user_text}\"")
                
                # Get AI response
                ai_response = self.get_ai_response(user_text)
                print(f"🤖 AI: \"{ai_response}\"")
                
                # Speak response
                self.speak_response(ai_response)
                
                print()  # Blank line for readability
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
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
