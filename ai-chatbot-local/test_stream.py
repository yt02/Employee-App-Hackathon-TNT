import os
import json
from dotenv import load_dotenv

load_dotenv()
from app.azure_agent import get_agent, get_thread_for_user

client, active_agent, toolset = get_agent("legacy")
thread = get_thread_for_user("emp_001")

print(f"Agent ID: {active_agent.id}")
print(f"Thread ID: {thread.id}")

print("Available methods on client.agents:")
print(dir(client.agents))

# Test if create_stream exists
if hasattr(client.agents, "create_stream"):
    print("create_stream is available!")
else:
    print("create_stream is NOT available.")
