"""
Chat module — Routes user messages to the Azure AI Agent.

The agent handles all intent detection and tool execution via function calling.
This module simply forwards the message and returns the response.
"""

import json
from app.azure_agent import ask_agent


def ask(question: str, user_id: str = "emp_001") -> str:
    """
    Answer a user question using the Azure AI Agent.

    The agent automatically detects intent, calls the appropriate tools
    (leave management, room booking, IT tickets), and generates a
    friendly response — all via native function calling.

    Args:
        question: The user's natural language message.
        user_id: Employee ID for context.

    Returns:
        JSON string with the answer and metadata.
    """
    try:
        response_dict = ask_agent(question, user_id)
        
        if response_dict.get("type") == "error":
            return json.dumps({
                "answer": response_dict.get("text", "An error occurred."),
                "action_taken": False,
                "error": True
            })
            
        if response_dict.get("type") == "confirmation_required":
            return json.dumps({
                "answer": "I need your confirmation to proceed with this action.",
                "action_taken": False,
                "requires_confirmation": True,
                "confirmation_data": {
                    "thread_id": response_dict["thread_id"],
                    "run_id": response_dict["run_id"],
                    "tool_call_id": response_dict["tool_call_id"],
                    "tool_name": response_dict["tool_name"],
                    "arguments": response_dict["arguments"]
                }
            })

        answer = response_dict.get("text", "")
        requires_confirmation = False
        if "[CONFIRM_ACTION]" in answer:
            requires_confirmation = True
            answer = answer.replace("[CONFIRM_ACTION]", "").strip()

        return json.dumps({
            "answer": answer,
            "action_taken": False,
            "requires_confirmation": requires_confirmation
        })
    except Exception as e:
        print(f"Error in ask(): {e}")
        return json.dumps({
            "answer": f"I apologize, but I encountered an error: {str(e)}",
            "action_taken": False,
            "error": str(e),
        })
