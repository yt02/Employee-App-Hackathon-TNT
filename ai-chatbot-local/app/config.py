import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from the project root (parent of app directory)
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Microsoft Foundry Agent Configuration
# Microsoft Foundry Agent Configuration
AZURE_CONNECTION_STRING = os.getenv("AZURE_CONNECTION_STRING", "")
AZURE_AGENT_ID = os.getenv("AZURE_AGENT_ID", "")

# Multi-Agent Routing IDs
AZURE_ORCHESTRATOR_ID = os.getenv("AZURE_ORCHESTRATOR_ID", AZURE_AGENT_ID)
AZURE_LEAVE_AGENT_ID = os.getenv("AZURE_LEAVE_AGENT_ID", "")
AZURE_ROOM_AGENT_ID = os.getenv("AZURE_ROOM_AGENT_ID", "")
AZURE_IT_AGENT_ID = os.getenv("AZURE_IT_AGENT_ID", "")
AZURE_HR_AGENT_ID = os.getenv("AZURE_HR_AGENT_ID", "")
AZURE_VISITOR_AGENT_ID = os.getenv("AZURE_VISITOR_AGENT_ID", "")
AZURE_SHUTTLE_AGENT_ID = os.getenv("AZURE_SHUTTLE_AGENT_ID", "")
AZURE_ROUTER_AGENT_ID = os.getenv("AZURE_ROUTER_AGENT_ID", "")
