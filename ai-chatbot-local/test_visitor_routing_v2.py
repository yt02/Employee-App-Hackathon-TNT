import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.azure_agent import get_fast_intent

def test_visitor_routing():
    test_cases = [
        "I want to register an evisitor",
        "pre register guest",
        "appointment for tomorrow",
        "register a visit",
        "someone is at the lobby",
        "arrival of guest",
        "visitor registration",
        "e-visitor"
    ]
    
    print("🚀 Starting Visitor Routing Verification...\n")
    all_passed = True
    
    for phrase in test_cases:
        intent = get_fast_intent(phrase)
        status = "✅ PASSED" if intent == "VISITOR" else "❌ FAILED"
        print(f"[{status}] Phrase: '{phrase}' -> Intent: {intent}")
        if intent != "VISITOR":
            all_passed = False
            
    print("\n" + ("🎉 All visitor routing tests passed!" if all_passed else "⚠️ Some tests failed."))

if __name__ == "__main__":
    test_visitor_routing()
