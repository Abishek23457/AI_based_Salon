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
    
    print("\n🔌 Connecting to AI Agent via OpenRouter...")
    
    # Use OpenRouter instead of Gemini Live API
    import requests
    
    openrouter_api_key = settings.OPENROUTER_API_KEY if hasattr(settings, 'OPENROUTER_API_KEY') else os.getenv('OPENROUTER_API_KEY')
    
    if not openrouter_api_key:
        print("\n❌ ERROR: OPENROUTER_API_KEY not found!")
        print("   Add your OpenRouter API key to .env file:")
        print("   OPENROUTER_API_KEY=your_key_here")
        return
    
    # Deepgram API for STT and TTS
    deepgram_api_key = settings.DEEPGRAM_API_KEY if hasattr(settings, 'DEEPGRAM_API_KEY') else os.getenv('DEEPGRAM_API_KEY')
    
    if not deepgram_api_key:
        print("\n❌ ERROR: DEEPGRAM_API_KEY not found!")
        print("   Add your Deepgram API key to .env file:")
        print("   DEEPGRAM_API_KEY=your_key_here")
        return
    
    # Initialize PyAudio
    p = pyaudio.PyAudio()
    
    try:
        print("\n✅ CONNECTED!")
        print("🎤 Voice Bot Ready - Start speaking now...\n")
        
        # Open microphone stream
        mic_stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
        
        # Open speaker stream
        speaker_stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=OUTPUT_RATE,
            output=True
        )
        
        print("You: ", end="", flush=True)
        
        while True:
            # Record audio
            frames = []
            silence_threshold = 40
            silent_chunks = 0
            min_speech_chunks = 10  # Require at least some speech
            speech_chunks = 0
            
            print("\nListening... (speak now)")
            
            while True:
                data = mic_stream.read(CHUNK, exception_on_overflow=False)
                frames.append(data)
                
                # Check for silence (improved energy threshold)
                audio_data = np.frombuffer(data, dtype=np.int16)
                energy = np.abs(audio_data).mean()
                
                if energy > 300:  # Speech threshold (lowered)
                    silent_chunks = 0
                    speech_chunks += 1
                else:
                    silent_chunks += 1
                    if silent_chunks > silence_threshold and speech_chunks > min_speech_chunks:
                        break
                
                # Max recording time (15 seconds)
                if len(frames) > 1500:
                    break
            
            # Convert audio to text using Deepgram STT
            print("\nProcessing speech...")
            
            # Save audio to temp file for STT
            import wave
            temp_audio = "temp_audio.wav"
            wf = wave.open(temp_audio, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            
            # Use Deepgram for STT
            try:
                with open(temp_audio, 'rb') as audio_file:
                    stt_response = requests.post(
                        f"https://api.deepgram.com/v1/listen?model=whisper-medium&language=en",
                        headers={
                            "Authorization": f"Token {deepgram_api_key}",
                            "Content-Type": "audio/wav"
                        },
                        data=audio_file
                    )
                
                if stt_response.status_code == 200:
                    stt_result = stt_response.json()
                    try:
                        channels = stt_result.get('results', {}).get('channels', [])
                        if channels and len(channels) > 0:
                            alternatives = channels[0].get('alternatives', [])
                            if alternatives and len(alternatives) > 0:
                                user_input = alternatives[0].get('transcript', '')
                            else:
                                user_input = ""
                        else:
                            user_input = ""
                        print(f"\nYou said: {user_input}")
                    except Exception as e:
                        print(f"\n❌ STT Parsing Error: {e}")
                        user_input = ""
                else:
                    print(f"\n❌ STT Error: {stt_response.text}")
                    user_input = ""
                    
            except Exception as e:
                print(f"\n❌ STT Error: {e}")
                user_input = ""
            
            # Clean up temp file
            try:
                os.remove(temp_audio)
            except:
                pass
            
            if not user_input or user_input.lower() == 'quit':
                break
            
            # Call OpenRouter API
            try:
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {openrouter_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "openai/gpt-4o-mini",  # or any OpenRouter model
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": user_input}
                        ]
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    ai_response = result['choices'][0]['message']['content']
                    print(f"\nAI: {ai_response}")
                    
                    # Convert AI response to speech using Windows SAPI
                    print("\n🔊 Speaking...")
                    try:
                        import win32com.client
                        speaker = win32com.client.Dispatch("SAPI.SpVoice")
                        speaker.Speak(ai_response)
                    except Exception as e:
                        print(f"\n❌ TTS Error: {e}")
                        # Fallback to print
                        print(f"AI: {ai_response}")
                    
                    print("\nYou: ", end="", flush=True)
                else:
                    print(f"\n❌ API Error: {response.text}")
                    
            except Exception as e:
                print(f"\n❌ Request Error: {e}")
            
    except KeyboardInterrupt:
        print("\n\n👋 Ending voice session...")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
    finally:
        # Cleanup
        try:
            mic_stream.stop_stream()
            mic_stream.close()
            speaker_stream.stop_stream()
            speaker_stream.close()
            p.terminate()
        except:
            pass
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
