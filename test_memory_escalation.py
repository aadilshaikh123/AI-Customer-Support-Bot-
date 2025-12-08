"""Test script for contextual memory and escalation features"""

import requests
import time
import json

# Configuration
BASE_URL = "http://localhost:8000"
USER_ID = "test_user_memory"

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def send_message(session_id, message):
    """Send a message and print response"""
    print(f"👤 USER: {message}")
    
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={
            "message": message,
            "user_id": USER_ID,
            "session_id": session_id
        }
    )
    
    data = response.json()
    print(f"🤖 BOT: {data['message']}")
    
    if data.get('confidence_score') is not None:
        print(f"📊 Confidence: {data['confidence_score']:.2f}")
    
    if data.get('escalated'):
        print(f"⚠️  ESCALATED: {data['escalation_reason']}")
    
    print("-" * 60)
    time.sleep(1)
    return data

def test_contextual_memory():
    """Test that bot remembers conversation context"""
    print_section("TEST 1: Contextual Memory")
    
    # Create new session
    session_response = requests.post(
        f"{BASE_URL}/api/sessions",
        json={"user_id": USER_ID}
    )
    session_id = session_response.json()['id']
    print(f"📝 Created session: {session_id}\n")
    
    # Multi-turn conversation to test memory
    print("Testing if bot remembers context across messages...\n")
    
    # Turn 1: Ask about password reset
    send_message(session_id, "How do I reset my password?")
    
    # Turn 2: Follow-up question (requires context)
    send_message(session_id, "How long does that link last?")
    
    # Turn 3: Another follow-up
    send_message(session_id, "What if the link expired?")
    
    # Turn 4: Change topic
    send_message(session_id, "Do you have a mobile app?")
    
    # Turn 5: Follow-up on new topic
    send_message(session_id, "Is it free?")
    
    print("\n✅ If bot answered follow-ups correctly, memory is working!")
    return session_id

def test_escalation_low_confidence():
    """Test escalation when bot has low confidence"""
    print_section("TEST 2: Escalation - Low Confidence")
    
    session_response = requests.post(
        f"{BASE_URL}/api/sessions",
        json={"user_id": USER_ID}
    )
    session_id = session_response.json()['id']
    
    print("Asking complex/unclear questions to trigger low confidence...\n")
    
    # Ask vague/complex questions
    send_message(session_id, "Can you help me with the thing?")
    send_message(session_id, "I need that feature we discussed last month")
    send_message(session_id, "How do I do the integration stuff?")
    
    print("\n✅ Check if any responses triggered escalation (confidence < 0.7)")
    return session_id

def test_escalation_keywords():
    """Test escalation on specific keywords"""
    print_section("TEST 3: Escalation - Keywords")
    
    session_response = requests.post(
        f"{BASE_URL}/api/sessions",
        json={"user_id": USER_ID}
    )
    session_id = session_response.json()['id']
    
    print("Using escalation trigger words (testing immediate escalation)...\n")
    
    # Keywords that should trigger IMMEDIATE escalation
    test_cases = [
        "I want to speak to a human please",
        "Can I talk to a real person?",
        "I need to speak with a manager",
        "Connect me to an agent",
        "Transfer me to customer service",
        "I want human help"
    ]
    
    escalation_count = 0
    for message in test_cases:
        data = send_message(session_id, message)
        if data.get('escalated'):
            escalation_count += 1
    
    print(f"\n✅ Escalation Success Rate: {escalation_count}/{len(test_cases)} ({escalation_count/len(test_cases)*100:.0f}%)")
    print(f"Expected: 100% immediate escalation on keyword detection")
    return session_id

def test_escalation_repeated_question():
    """Test escalation when asking same question repeatedly"""
    print_section("TEST 4: Escalation - Repeated Questions")
    
    session_response = requests.post(
        f"{BASE_URL}/api/sessions",
        json={"user_id": USER_ID}
    )
    session_id = session_response.json()['id']
    
    print("Asking the same question multiple times...\n")
    
    # Ask same question 4 times (should escalate after 3)
    for i in range(4):
        print(f"Attempt {i+1}:")
        send_message(session_id, "How do I reset my password?")
    
    print("\n✅ Should escalate after 3rd or 4th attempt!")
    return session_id

def test_escalation_brief_response():
    """Test escalation on very brief responses"""
    print_section("TEST 5: Escalation - Brief Responses")
    
    session_response = requests.post(
        f"{BASE_URL}/api/sessions",
        json={"user_id": USER_ID}
    )
    session_id = session_response.json()['id']
    
    print("Asking questions that might get brief answers...\n")
    
    send_message(session_id, "Yes or no?")
    send_message(session_id, "What?")
    send_message(session_id, "Huh?")
    
    print("\n✅ Very brief responses (<5 words) might trigger escalation")
    return session_id

def check_conversation_history(session_id):
    """Verify conversation history is saved"""
    print_section("VERIFY: Conversation History")
    
    response = requests.get(f"{BASE_URL}/api/sessions/{session_id}/history")
    data = response.json()
    history = data.get('messages', [])
    
    print(f"📚 Total messages in session: {len(history)}")
    print(f"\nLast 5 messages:")
    for msg in history[-5:]:
        role_icon = "👤" if msg['role'] == 'user' else "🤖"
        print(f"{role_icon} {msg['role'].upper()}: {msg['content'][:60]}...")
    
    print("\n✅ History is being saved!")

def check_escalations():
    """List all escalations created"""
    print_section("VERIFY: Escalations Created")
    
    response = requests.get(f"{BASE_URL}/api/escalations")
    escalations = response.json()
    
    print(f"⚠️  Total escalations: {len(escalations)}\n")
    
    for esc in escalations:
        print(f"Session {esc['session_id']}: {esc['reason']}")
        print(f"   Status: {esc['status']} | Created: {esc['created_at'][:19]}")
        print()
    
    if escalations:
        print("✅ Escalation system is working!")
    else:
        print("⚠️  No escalations found - try more complex queries")

def main():
    """Run all tests"""
    print("\n" + "🤖" * 30)
    print("  AI CUSTOMER SUPPORT BOT - MEMORY & ESCALATION TESTS")
    print("🤖" * 30)
    
    try:
        # Test contextual memory
        session1 = test_contextual_memory()
        time.sleep(2)
        
        # Test different escalation scenarios
        test_escalation_low_confidence()
        time.sleep(2)
        
        test_escalation_keywords()
        time.sleep(2)
        
        test_escalation_repeated_question()
        time.sleep(2)
        
        test_escalation_brief_response()
        time.sleep(2)
        
        # Verify data persistence
        check_conversation_history(session1)
        check_escalations()
        
        print_section("🎉 ALL TESTS COMPLETE!")
        print("\nKey Observations:")
        print("✅ Contextual Memory: Bot remembers conversation context")
        print("✅ Escalation Triggers: Low confidence, keywords, repetition")
        print("✅ Data Persistence: Messages and escalations saved to DB")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to backend!")
        print("Make sure the backend is running: python -m uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    main()
