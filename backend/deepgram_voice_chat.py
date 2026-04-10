"""
Deepgram Voice Chat - Terminal Interface
Real-time voice conversation with BookSmart AI using Deepgram
Docs: https://developers.deepgram.com/docs/getting-started-with-live-streaming-audio
"""
import asyncio
import os
import sys
import signal
import pyaudio
from datetime import datetime
from deepgram_voice_service import DeepgramVoiceAgent
from config import settings

class TerminalVoiceChat:
    """Terminal-based voice chat with Deepgram"""
    
    def __init__(self):
        self.agent = DeepgramVoiceAgent()
        self.is_running = False
        self.conversation_log = []
        
    def print_banner(self):
        """Print welcome banner"""
        print("\n" + "="*60)
        print("       🎙️  Deepgram Voice Chat Agent")
        print("       (Real-time Speech-to-Speech)")
        print("="*60)
        print("\n📝 Instructions:")
        print("   • Press ENTER to start speaking")
        print("   • Speak clearly into your microphone")
        print("   • The AI will respond with voice")
        print("   • Press Ctrl+C to end the conversation")
        print("\n" + "-"*60)
    
    def format_timestamp(self):
        """Get current timestamp"""
        return datetime.now().strftime("%H:%M:%S")
    
    def on_user_speech(self, text: str):
        """Handle user speech"""
        print(f"\n[{self.format_timestamp()}] 👤 You: {text}")
        self.conversation_log.append(("You", text))
    
    def on_ai_response(self, text: str):
        """Handle AI response"""
        print(f"[{self.format_timestamp()}] 🤖 AI: {text}")
        self.conversation_log.append(("AI", text))
        print("\n[Press ENTER to speak, Ctrl+C to exit]")
    
    async def run(self):
        """Main voice chat loop"""
        self.print_banner()
        
        # Check API key
        if not settings.DEEPGRAM_API_KEY:
            print("\n❌ ERROR: DEEPGRAM_API_KEY not found!")
            print("   Add to .env: DEEPGRAM_API_KEY=your_key_here")
            print("   Get your key: https://console.deepgram.com/signup")
            return
        
        print(f"\n✅ Deepgram API Key: {settings.DEEPGRAM_API_KEY[:10]}...")
        print("🎧 Checking audio devices...")
        
        # Check audio
        try:
            audio = pyaudio.PyAudio()
            input_devices = []
            output_devices = []
            
            for i in range(audio.get_device_count()):
                info = audio.get_device_info_by_index(i)
                if info['maxInputChannels'] > 0:
                    input_devices.append(info['name'])
                if info['maxOutputChannels'] > 0:
                    output_devices.append(info['name'])
            
            audio.terminate()
            
            if input_devices:
                print(f"   🎤 Microphones found: {len(input_devices)}")
            else:
                print("   ❌ No microphone found!")
                return
                
            if output_devices:
                print(f"   🔊 Speakers found: {len(output_devices)}")
            else:
                print("   ❌ No speakers found!")
                return
                
        except Exception as e:
            print(f"   ❌ Audio check failed: {e}")
            return
        
        print("\n" + "="*60)
        print("       🎙️  READY - Press ENTER to speak")
        print("="*60)
        
        self.is_running = True
        
        # Start voice agent in background
        agent_task = asyncio.create_task(
            self.agent.start_conversation(
                on_user_speech=self.on_user_speech,
                on_ai_response=self.on_ai_response
            )
        )
        
        try:
            while self.is_running:
                # Wait for user to press ENTER to speak
                await asyncio.get_event_loop().run_in_executor(
                    None, 
                    lambda: input("\n[Press ENTER when ready to speak...]")
                )
                
                if not self.is_running:
                    break
                
                print("🎤 Listening... (speak now)")
                # The agent is already listening via WebSocket
                # Wait a moment for the transcript to come through
                await asyncio.sleep(0.5)
                
        except KeyboardInterrupt:
            print("\n\n👋 Stopping voice chat...")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        finally:
            self.is_running = False
            self.agent.cleanup()
            agent_task.cancel()
            try:
                await agent_task
            except asyncio.CancelledError:
                pass
    
    def show_history(self):
        """Show conversation history"""
        print("\n" + "="*60)
        print("📜 CONVERSATION HISTORY")
        print("="*60)
        if not self.conversation_log:
            print("No conversation yet.")
        else:
            for speaker, text in self.conversation_log:
                emoji = "👤" if speaker == "You" else "🤖"
                print(f"{emoji} {speaker}: {text}")
        print("="*60 + "\n")


async def test_tts():
    """Quick TTS test"""
    print("\n🧪 Testing Deepgram TTS...")
    
    from deepgram_voice_service import DeepgramVoiceService
    
    service = DeepgramVoiceService()
    
    test_messages = [
        "Hello! I'm BookSmart AI, your salon assistant.",
        "I can help you book appointments and answer questions.",
        "What service are you looking for today?"
    ]
    
    for msg in test_messages:
        print(f"\n🔊 Speaking: {msg}")
        audio = await service.text_to_speech(msg)
        if audio:
            service.play_audio(audio)
            await asyncio.sleep(1)
        else:
            print("❌ Failed to generate audio")


def main():
    """Entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Deepgram Voice Chat")
    parser.add_argument("--test-tts", action="store_true", help="Test text-to-speech only")
    parser.add_argument("--history", action="store_true", help="Show conversation history after")
    args = parser.parse_args()
    
    if args.test_tts:
        asyncio.run(test_tts())
    else:
        chat = TerminalVoiceChat()
        try:
            asyncio.run(chat.run())
            if args.history:
                chat.show_history()
        except Exception as e:
            print(f"\n❌ Fatal Error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
