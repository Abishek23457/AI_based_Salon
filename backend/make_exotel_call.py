"""
Make a phone call using Exotel with Voice Bot integration
This script initiates a phone call to a specified number using the Exotel API
and connects it to the voice bot for AI-powered conversation
"""
import asyncio
from exotel_client import exotel_client
import sys

async def make_call(to_number: str, app_name: str = None, mock: bool = False):
    """Make a phone call to the specified number"""
    if mock:
        print(f"\n🧪 MOCK MODE - Simulating call to {to_number}...")
        print(f"🤖 Simulating Voice Bot AI connection...")
        print(f"✅ Mock call initiated successfully!")
        print(f"Call SID: mock_call_sid")
        print(f"Status: in-progress")
        print(f"\n🎙️ Voice Bot would handle the call automatically")
        print(f"📝 Call would be logged and transcribed")
        return

    print(f"\n📞 Initiating call to {to_number}...")
    print(f"🤖 Connecting to Voice Bot AI...")
    
    result = await exotel_client.make_call(
        to_number=to_number,
        app_name=app_name or "1221019"  # Default Exotel App ID
    )
    
    if result:
        print(f"✅ Call initiated successfully!")
        print(f"Call SID: {result.get('Call', {}).get('Sid')}")
        print(f"Status: {result.get('Call', {}).get('Status')}")
        print(f"\n🎙️ Voice Bot will handle the call automatically")
        print(f"📝 Call will be logged and transcribed")
    else:
        print("❌ Failed to initiate call")
        print(f"\n💡 Try mock mode for testing: py make_exotel_call.py {to_number} --mock")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: py make_exotel_call.py <phone_number> [app_name] [--mock]")
        print("Example: py make_exotel_call.py 8072462345")
        print("Example: py make_exotel_call.py 8072462345 my_voice_app")
        print("Example: py make_exotel_call.py 8072462345 --mock  (for testing without KYC)")
        sys.exit(1)
    
    phone_number = sys.argv[1]
    app_name = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != "--mock" else None
    mock = "--mock" in sys.argv
    
    asyncio.run(make_call(phone_number, app_name, mock))
