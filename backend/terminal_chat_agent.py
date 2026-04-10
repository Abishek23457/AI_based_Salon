"""
Terminal Chat Agent - Live text-based conversation with AI
Run this to chat with the BookSmart AI Receptionist in your terminal
"""
import asyncio
import sys
import requests
from datetime import datetime

# API Configuration
BASE_URL = "http://localhost:8000"
CHAT_ENDPOINT = f"{BASE_URL}/chat/receptionist"
HEALTH_ENDPOINT = f"{BASE_URL}/chat/health"

class TerminalChatAgent:
    def __init__(self):
        self.salon_id = "1"
        self.customer_name = "Terminal User"
        self.conversation_history = []
        
    def check_backend(self):
        """Check if backend is running"""
        try:
            response = requests.get(HEALTH_ENDPOINT, timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def send_message(self, message):
        """Send message to AI agent"""
        try:
            payload = {
                "message": message,
                "salon_id": self.salon_id,
                "customer_name": self.customer_name
            }
            response = requests.post(CHAT_ENDPOINT, json=payload, timeout=5)
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            print(f"\n[Error connecting to AI: {e}]")
            return None
    
    def print_banner(self):
        """Print welcome banner"""
        print("\n" + "="*60)
        print("    🤖  BookSmart AI - Terminal Chat Agent")
        print("="*60)
        print("\n    💬 Type your messages and press ENTER")
        print("    🚪 Type 'exit' or 'quit' to end conversation")
        print("    📋 Type 'history' to see conversation")
        print("    🔄 Type 'clear' to clear screen")
        print("\n" + "-"*60)
    
    def format_timestamp(self):
        """Get current timestamp"""
        return datetime.now().strftime("%H:%M:%S")
    
    async def run(self):
        """Main chat loop"""
        self.print_banner()
        
        # Check backend
        print("\n[🔍 Checking AI Agent connection...]")
        if not self.check_backend():
            print("[❌ Backend not running. Start it with: python main.py]")
            print(f"[📍 Expected at: {BASE_URL}]")
            return
        
        print("[✅ Connected to AI Agent!]")
        print("[🎤 Ready for conversation...\n]")
        
        # Welcome message
        welcome_response = self.send_message("hello")
        if welcome_response:
            ai_reply = welcome_response.get("ai_response", "Hello! How can I help?")
            print(f"[{self.format_timestamp()}] 🤖 Agent: {ai_reply}\n")
        
        # Chat loop
        while True:
            try:
                # Get user input
                user_input = input(f"[{self.format_timestamp()}] 👤 You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("\n[👋 Ending conversation. Goodbye!]")
                    break
                
                if user_input.lower() == 'history':
                    self.show_history()
                    continue
                
                if user_input.lower() == 'clear':
                    print("\n" * 50)
                    self.print_banner()
                    continue
                
                # Save to history
                self.conversation_history.append(("You", user_input))
                
                # Send to AI
                print(f"[{self.format_timestamp()}] ⏳ Agent is typing...")
                response = self.send_message(user_input)
                
                if response:
                    ai_reply = response.get("ai_response", "I'm here to help!")
                    self.conversation_history.append(("Agent", ai_reply))
                    print(f"\r[{self.format_timestamp()}] 🤖 Agent: {ai_reply}\n")
                else:
                    print(f"\r[{self.format_timestamp()}] ❌ Error: No response from AI\n")
                
            except KeyboardInterrupt:
                print("\n\n[👋 Conversation ended by user]")
                break
            except Exception as e:
                print(f"\n[Error: {e}]")
                continue
    
    def show_history(self):
        """Show conversation history"""
        print("\n" + "="*60)
        print("📜 CONVERSATION HISTORY")
        print("="*60)
        if not self.conversation_history:
            print("No messages yet.")
        else:
            for speaker, message in self.conversation_history[-10:]:  # Last 10 messages
                emoji = "👤" if speaker == "You" else "🤖"
                print(f"{emoji} {speaker}: {message}")
        print("="*60 + "\n")

def main():
    """Entry point"""
    chat = TerminalChatAgent()
    try:
        asyncio.run(chat.run())
    except Exception as e:
        print(f"\n[Fatal Error: {e}]")
        sys.exit(1)

if __name__ == "__main__":
    main()
