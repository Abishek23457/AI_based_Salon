"""
Simple Gemini Voice Chat - Record + Transcribe + AI + Speak
Uses standard Gemini API (no Live API required)
"""
import wave
import tempfile
import requests
import pyaudio
import json
from config import settings

# Audio settings
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024

def record_audio(duration=5):
    """Record audio from microphone"""
    print(f"\n[Recording for {duration} seconds...]")
    
    audio = pyaudio.PyAudio()
    stream = audio.open(
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
    
    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    # Save to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as f:
        wf = wave.open(f.name, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(pyaudio.PyAudio().get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        return f.name

def transcribe_with_gemini(audio_file):
    """Upload audio to Gemini and get transcription"""
    print("[Sending to Gemini for transcription...]")
    
    try:
        from google import genai
        
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        # Upload audio file
        audio_file_obj = client.files.upload(file=audio_file)
        
        # Transcribe
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=["Transcribe this audio:", audio_file_obj]
        )
        
        return response.text
        
    except Exception as e:
        print(f"[Transcription error: {e}]")
        return None

def chat_with_gemini(message):
    """Get AI response from Gemini"""
    print("[AI is thinking...]")
    
    try:
        from google import genai
        
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        system_prompt = """You are BookSmart AI, a friendly salon receptionist.
Services: Haircut (Rs. 500), Coloring (Rs. 2000), Facial (Rs. 1500), Manicure/Pedicure (Rs. 800), Massage (Rs. 1800)
Keep responses SHORT (1-2 sentences), friendly and conversational."""
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            config={"system_instruction": system_prompt},
            contents=message
        )
        
        return response.text
        
    except Exception as e:
        print(f"[Chat error: {e}]")
        return "I'm sorry, I couldn't process that."

def speak_with_deepgram(text):
    """Convert text to speech using Deepgram"""
    if not settings.DEEPGRAM_API_KEY:
        print("[DEEPGRAM_API_KEY not set - printing only]")
        print(f"AI would say: {text}")
        return
    
    print("[Speaking...]")
    
    try:
        url = "https://api.deepgram.com/v1/speak?model=aura-asteria-en"
        headers = {
            "Authorization": f"Token {settings.DEEPGRAM_API_KEY}",
            "Content-Type": "application/json"
        }
        data = json.dumps({"text": text})
        
        response = requests.post(url, headers=headers, data=data, timeout=15)
        
        if response.status_code == 200:
            # Play audio
            audio = pyaudio.PyAudio()
            stream = audio.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=24000,
                output=True
            )
            
            # Write in chunks
            chunk_size = 1024
            audio_data = response.content
            for i in range(0, len(audio_data), chunk_size):
                chunk = audio_data[i:i+chunk_size]
                stream.write(chunk)
            
            stream.stop_stream()
            stream.close()
            audio.terminate()
            print("[Done speaking]")
        else:
            print(f"[TTS error: {response.status_code}]")
            print(f"AI: {text}")
            
    except Exception as e:
        print(f"[TTS error: {e}]")
        print(f"AI: {text}")

def main():
    """Main loop"""
    print("="*60)
    print("Gemini Voice Chat - Simple Version")
    print("="*60)
    print("\nHow it works:")
    print("  1. Press ENTER to record (5 seconds)")
    print("  2. Gemini transcribes your speech")
    print("  3. AI responds")
    print("  4. AI speaks the response")
    print("  5. Press Ctrl+C to exit")
    print("="*60)
    
    # Check API keys
    if not settings.GEMINI_API_KEY:
        print("\nERROR: GEMINI_API_KEY not set!")
        print("Add to .env: GEMINI_API_KEY=your_key")
        return
    
    print(f"\nOK: Gemini API connected")
    
    while True:
        try:
            input("\n[Press ENTER to speak (or Ctrl+C to exit)]")
            
            # Record
            audio_file = record_audio(duration=5)
            
            # Transcribe with Gemini
            user_text = transcribe_with_gemini(audio_file)
            
            # Cleanup
            import os
            os.unlink(audio_file)
            
            if not user_text:
                print("[Could not understand. Try again.]")
                continue
            
            print(f"\nYou: {user_text}")
            
            # Get AI response
            ai_response = chat_with_gemini(user_text)
            print(f"AI: {ai_response}")
            
            # Speak response
            speak_with_deepgram(ai_response)
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")
            continue

if __name__ == "__main__":
    main()
