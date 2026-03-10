import os
from dotenv import load_dotenv

load_dotenv()
from app.agent_azure import get_agent_response

def test_room_booking():
    print("Testing Room Agent: find me a room with whiteboard for 4 people tomorrow at 2 PM for an hour")
    response, _ = get_agent_response("emp_001", "find me a room with whiteboard for 4 people tomorrow at 2 PM for an hour")
    print(f"Response:\n{response.get('text', '')}")

def test_leave_booking():
    print("\n\nTesting Leave Agent: apply 8 days paternity leave next week")
    response, _ = get_agent_response("emp_001", "apply 8 days paternity leave next week")
    print(f"Response:\n{response.get('text', '')}")

    print("\n\nTesting Leave Agent: how many days of AL do I have left?")
    response, _ = get_agent_response("emp_001", "how many days of AL do I have left?")
    print(f"Response:\n{response.get('text', '')}")

if __name__ == "__main__":
    test_room_booking()
    test_leave_booking()
