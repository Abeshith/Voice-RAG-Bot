"""
Automated Voice Bot Demo - Minimal test without UI overhead
Runs multi-turn conversation automatically
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import asyncio
import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

class VoiceBotDemo:
    """Automated voice bot conversation"""
    
    def __init__(self, customer_id: str = "CUST_001"):
        self.customer_id = customer_id
        self.session_id = None
        self.turn = 0
    
    def start_session(self) -> bool:
        """Start voice bot session"""
        try:
            resp = requests.post(
                f"{BASE_URL}/voice-bot/start",
                json={"customer_id": self.customer_id},
                timeout=60
            )
            if resp.status_code == 200:
                data = resp.json()
                self.session_id = data.get("session_id")
                greeting = data.get("greeting", "")
                audio = data.get("audio_path", "")
                print(f"✅ Session started: {self.session_id}")
                print(f"   Bot: {greeting}")
                if audio:
                    print(f"   🔊 Audio: {audio}")
                return True
            else:
                print(f"❌ Start failed: {resp.status_code}")
                return False
        except Exception as e:
            print(f"❌ Start error: {str(e)}")
            return False
    
    def send_message(self, user_message: str) -> bool:
        """Send message to bot"""
        if not self.session_id:
            print("❌ No active session")
            return False
        
        try:
            self.turn += 1
            print(f"\n--- Turn {self.turn} ---")
            print(f"You: {user_message}")
            
            resp = requests.post(
                f"{BASE_URL}/voice-bot/message",
                params={"user_message": user_message},
                timeout=120
            )
            
            if resp.status_code == 200:
                data = resp.json()
                bot_response = data.get("response", "")
                audio = data.get("audio_path", "")
                sentiment = data.get("sentiment", "")
                intent = data.get("intent", "")
                
                print(f"Bot: {bot_response}")
                print(f"Intent: {intent} | Sentiment: {sentiment}")
                if audio:
                    print(f"🔊 Audio: {audio}")
                
                status = data.get("status", "")
                return status == "listening"
            else:
                print(f"❌ Message failed: {resp.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
    
    def end_session(self):
        """End session"""
        try:
            resp = requests.post(
                f"{BASE_URL}/voice-bot/end",
                timeout=30
            )
            if resp.status_code == 200:
                data = resp.json()
                farewell = data.get("farewell", "")
                print(f"\n✅ Session ended")
                print(f"   {farewell}")
        except Exception as e:
            print(f"⚠️  End error: {str(e)}")

async def main():
    """Run demo conversation"""
    print("\n" + "="*60)
    print("🤖 VOICE BOT AUTOMATED DEMO")
    print("="*60 + "\n")
    
    bot = VoiceBotDemo("CUST_001")
    
    # Start session
    if not bot.start_session():
        return
    
    # Multi-turn conversation
    messages = [
        "What is your return policy?",
        "Can I return my laptop if it's defective?"
    ]
    
    for msg in messages:
        if not bot.send_message(msg):
            break
    
    # End
    bot.end_session()
    print("\n" + "="*60)
    print("✅ DEMO COMPLETE")
    print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
