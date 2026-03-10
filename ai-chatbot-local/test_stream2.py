import os
from typing import Any
import json
from dotenv import load_dotenv

load_dotenv()
from app.azure_agent import get_agent, get_thread_for_user

client, active_agent, active_toolset = get_agent("orchestrator")
thread = get_thread_for_user("emp_001")

client.agents.create_message(
    thread_id=thread.id,
    role="user",
    content="Hello"
)

with client.agents.create_stream(
    thread_id=thread.id,
    agent_id=active_agent.id
) as stream:
    for event in stream:
        print(f"EVENT: {type(event).__name__}")
        if type(event).__name__ == "tuple":
            print(f"  Tuple[0]: {event[0]}")
            
print("Done")
