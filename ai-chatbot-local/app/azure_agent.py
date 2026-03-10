"""
Azure AI Agent Integration with Function Calling

This module connects to the Microsoft Azure AI Foundry Agent and handles
the complete function calling lifecycle:
1. Send user message to the agent
2. Agent decides if a tool call is needed
3. SDK auto-executes the tool via ToolSet callables
4. Agent generates a friendly response including tool results
"""

from datetime import date, datetime
import json
import os
import time
import threading
import queue
import re
import traceback
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.core.credentials import AccessToken
from app.config import (
    AZURE_CONNECTION_STRING, 
    AZURE_AGENT_ID,
    AZURE_ORCHESTRATOR_ID,
    AZURE_LEAVE_AGENT_ID,
    AZURE_ROOM_AGENT_ID,
    AZURE_IT_AGENT_ID,
    AZURE_HR_AGENT_ID,
    AZURE_VISITOR_AGENT_ID,
    AZURE_SHUTTLE_AGENT_ID
)
from app.tools import (
    toolset, 
    orchestrator_toolset, 
    leave_toolset, 
    room_toolset, 
    it_toolset,
    hr_toolset,
    visitor_toolset,
    shuttle_toolset
)

class _StaticTokenCredential:
    """Wraps a static bearer token. Used when AZURE_ACCESS_TOKEN is set (hackathon UAT workaround)."""
    def __init__(self, token: str):
        self._token = token
    def get_token(self, *scopes, **kwargs):
        print(f"🔑 Credential requested for scopes: {scopes}")
        # Treat token as valid for 1 hour from when it was loaded
        return AccessToken(self._token, int(time.time()) + 3600)

def get_credential():
    """
    Returns the best available credential in this order:
    1. AZURE_ACCESS_TOKEN env var  → static token (UAT workaround when role assignment is blocked)
    2. ManagedIdentityCredential   → Azure App Service system-assigned identity
    3. DefaultAzureCredential      → falls back to az login for local dev
    """
    # Debug: print all ENV keys starting with AZURE
    azure_envs = [k for k in os.environ.keys() if k.startswith("AZURE_")]
    print(f"DEBUG: Available Azure Envs: {azure_envs}")
    
    static_token = os.getenv("AZURE_ACCESS_TOKEN")
    if static_token:
        print(f"🔑 Using AZURE_ACCESS_TOKEN (length: {len(static_token)})")
        return _StaticTokenCredential(static_token)
        
    try:
        # If we are in Azure App Service, this usually succeeds but might lack permissions
        if os.getenv("IDENTITY_ENDPOINT"):
             print("ℹ️ Identity endpoint detected, trying ManagedIdentityCredential...")
             cred = ManagedIdentityCredential()
             return cred
    except Exception as e:
        print(f"ℹ️ ManagedIdentity init failed: {e}")

    print("ℹ️ Falling back to DefaultAzureCredential (az login)")
# Lazy-loaded client and agents dictionary
_project_client = None
_agents = {}
_agent_lock = threading.Lock()

def get_agent(agent_type="orchestrator"):
    """
    Lazy load the Azure AI Project client and a specific sub-agent.
    Returns: (client, agent_instance, agent_toolset)
    """
    global _project_client, _agents
    
    with _agent_lock:
        if _project_client is None:
            _project_client = AIProjectClient.from_connection_string(
                credential=get_credential(),
                conn_str=AZURE_CONNECTION_STRING,
            )

    # Determine which agent ID and matching tools to load
    agent_mapping = {
        "orchestrator": (AZURE_ORCHESTRATOR_ID or AZURE_AGENT_ID, orchestrator_toolset),
        "leave": (AZURE_LEAVE_AGENT_ID, leave_toolset),
        "room": (AZURE_ROOM_AGENT_ID, room_toolset),
        "it": (AZURE_IT_AGENT_ID, it_toolset),
        "hr": (AZURE_HR_AGENT_ID, hr_toolset),
        "visitor": (AZURE_VISITOR_AGENT_ID, visitor_toolset),
        "shuttle": (AZURE_SHUTTLE_AGENT_ID, shuttle_toolset),
        "legacy": (AZURE_AGENT_ID, toolset) # Fallback to original
    }
    
    # If the user hasn't configured sub-agents, fallback to monolithic legacy agent
    if not AZURE_LEAVE_AGENT_ID and agent_type != "legacy":
        print(f"⚠️ Multi-Agent ID missing for {agent_type}, falling back to legacy monolithic agent.")
        agent_type = "legacy"
        
    target_id, target_tools = agent_mapping.get(agent_type, agent_mapping["legacy"])

    if target_id not in _agents:
        try:
            # Fetch the agent instance from Azure
            agent_instance = _project_client.agents.get_agent(target_id)
            
            # Only update the agent if we have custom python tools to inject
            # This completely prevents accidental deletion of native Vector Stores
            if target_tools and target_tools.definitions:
                print(f"🔄 Syncing python tools to {agent_type.upper()} agent...")
                # Preserve native Azure tools
                final_tools = list(target_tools.definitions)
                if hasattr(agent_instance, 'tools') and agent_instance.tools:
                    for tool in agent_instance.tools:
                        tool_type = tool.type if hasattr(tool, 'type') else (tool.get('type', '') if isinstance(tool, dict) else '')
                        if tool_type in ['file_search', 'code_interpreter']:
                            final_tools.append(tool)

                update_kwargs = {
                    "agent_id": agent_instance.id,
                }
                
                # We also MUST pass tool_resources back in, otherwise Azure silently deletes them
                if hasattr(agent_instance, 'tool_resources') and getattr(agent_instance, 'tool_resources', None):
                    update_kwargs["tool_resources"] = agent_instance.tool_resources
                    
                    # Ensure file_search tool is preserved if resources exist
                    if hasattr(agent_instance.tool_resources, 'file_search') and getattr(agent_instance.tool_resources, 'file_search', None):
                        has_fs = any(getattr(t, 'type', '') == 'file_search' or (isinstance(t, dict) and t.get('type') == 'file_search') for t in final_tools)
                        if not has_fs:
                            try:
                                from azure.ai.projects.models import FileSearchToolDefinition
                                final_tools.append(FileSearchToolDefinition())
                            except ImportError:
                                final_tools.append({"type": "file_search"})

                    # Ensure code_interpreter tool is preserved if resources exist
                    if hasattr(agent_instance.tool_resources, 'code_interpreter') and getattr(agent_instance.tool_resources, 'code_interpreter', None):
                        has_ci = any(getattr(t, 'type', '') == 'code_interpreter' or (isinstance(t, dict) and t.get('type') == 'code_interpreter') for t in final_tools)
                        if not has_ci:
                            try:
                                from azure.ai.projects.models import CodeInterpreterToolDefinition
                                final_tools.append(CodeInterpreterToolDefinition())
                            except ImportError:
                                final_tools.append({"type": "code_interpreter"})

                # Sync instructions if prompt file exists
                prompt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "AGENT_PROMPTS")
                prompt_file_map = {
                    "orchestrator": "1_ORCHESTRATOR.md",
                    "leave": "2_LEAVE_AGENT.md",
                    "room": "3_ROOM_AGENT.md",
                    "it": "4_IT_AGENT.md",
                    "hr": "4_HR_AGENT.md",
                    "visitor": "5_VISITOR_AGENT.md",
                    "shuttle": "6_SHUTTLE_AGENT.md"
                }
                
                if agent_type in prompt_file_map:
                    filepath = os.path.join(prompt_path, prompt_file_map[agent_type])
                    if os.path.exists(filepath):
                        print(f"📄 Syncing local prompt for {agent_type.upper()}...")
                        with open(filepath, 'r', encoding='utf-8') as f:
                            instructions = f.read()
                            # Clean instructions (strip line numbers if they were accidentally included during editing)
                            instructions = re.sub(r'^\d+: ', '', instructions, flags=re.MULTILINE)
                            update_kwargs["instructions"] = instructions

                update_kwargs["tools"] = final_tools

                _project_client.agents.update_agent(**update_kwargs)
            else:
                print(f"⏩ Cleaning custom tools for {agent_type.upper()} agent (enforcing native configuration)")
                final_tools = []
                if hasattr(agent_instance, 'tools') and agent_instance.tools:
                    for tool in agent_instance.tools:
                        tool_type = tool.type if hasattr(tool, 'type') else (tool.get('type', '') if isinstance(tool, dict) else '')
                        if tool_type in ['file_search', 'code_interpreter']:
                            final_tools.append(tool)
                            
                update_kwargs = {
                    "agent_id": agent_instance.id,
                    "tools": final_tools
                }
                if hasattr(agent_instance, 'tool_resources') and getattr(agent_instance, 'tool_resources', None):
                    update_kwargs["tool_resources"] = agent_instance.tool_resources
                    
                    # Ensure file_search tool is preserved if resources exist
                    if hasattr(agent_instance.tool_resources, 'file_search') and getattr(agent_instance.tool_resources, 'file_search', None):
                        has_fs = any(getattr(t, 'type', '') == 'file_search' or (isinstance(t, dict) and t.get('type') == 'file_search') for t in final_tools)
                        if not has_fs:
                            try:
                                from azure.ai.projects.models import FileSearchToolDefinition
                                final_tools.append(FileSearchToolDefinition())
                            except ImportError:
                                final_tools.append({"type": "file_search"})

                    # Ensure code_interpreter tool is preserved if resources exist
                    if hasattr(agent_instance.tool_resources, 'code_interpreter') and getattr(agent_instance.tool_resources, 'code_interpreter', None):
                        has_ci = any(getattr(t, 'type', '') == 'code_interpreter' or (isinstance(t, dict) and t.get('type') == 'code_interpreter') for t in final_tools)
                        if not has_ci:
                            try:
                                from azure.ai.projects.models import CodeInterpreterToolDefinition
                                final_tools.append(CodeInterpreterToolDefinition())
                            except ImportError:
                                final_tools.append({"type": "code_interpreter"})

                update_kwargs["tools"] = final_tools
                    
                _project_client.agents.update_agent(**update_kwargs)
            
            _agents[target_id] = agent_instance
            print(f"✅ Booted Azure {agent_type.upper()} agent: {agent_instance.id}")
        except Exception as e:
            print(f"❌ Error booting {agent_type} agent: {e}")
            raise

    return _project_client, _agents[target_id], target_tools


DATA_DIR = "data"
THREADS_FILE = os.path.join(DATA_DIR, "threads.json")

def get_thread_for_user(user_id: str):
    """Get or create a persistent Azure AI thread for a specific user to maintain memory."""
    client, _, _ = get_agent("legacy")
    
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    threads = {}
    if os.path.exists(THREADS_FILE):
        try:
            with open(THREADS_FILE, 'r') as f:
                threads = json.load(f)
        except Exception:
            threads = {}
            
    if user_id in threads:
        thread_id = threads[user_id]
        try:
            # Verify thread exists in Azure
            thread = client.agents.get_thread(thread_id)
            print(f"🔄 Reusing existing thread {thread_id} for user {user_id}")
            return thread
        except Exception:
            pass
            
    thread = client.agents.create_thread()
    threads[user_id] = thread.id
    try:
        with open(THREADS_FILE, 'w') as f:
            json.dump(threads, f, indent=2)
    except Exception:
        pass
        
    return thread

def clear_thread_for_user(user_id: str):
    """Delete a user's persistent thread mapping to force a fresh conversation."""
    if os.path.exists(THREADS_FILE):
        try:
            with open(THREADS_FILE, 'r') as f:
                threads = json.load(f)
            if user_id in threads:
                del threads[user_id]
                with open(THREADS_FILE, 'w') as f:
                    json.dump(threads, f, indent=2)
                print(f"🗑️ Cleared stuck thread cache for {user_id}")
        except Exception:
            pass

def get_user_id_for_thread(thread_id: str):
    """Reverse-lookup user_id from persisted thread mapping."""
    if not os.path.exists(THREADS_FILE):
        return None
    try:
        with open(THREADS_FILE, "r", encoding="utf-8") as f:
            threads = json.load(f)
        for user_id, mapped_thread_id in threads.items():
            if mapped_thread_id == thread_id:
                return user_id
    except Exception:
        return None
    return None

def _ensure_message_created(client, thread_id: str, user_id: str, question: str):
    """Helper to safely create user message, attempting recovery if thread is stuck."""
    today = date.today().strftime("%Y-%m-%d")
    contextual_message = (
        f"[System Context: user_id={user_id}, current_date={today}]\n"
        f"User message: {question}"
    )

    try:
        client.agents.create_message(
            thread_id=thread_id,
            role="user",
            content=contextual_message,
        )
    except Exception as e:
        if "while a run" in str(e) and "is active" in str(e):
            print(f"⚠️ Thread {thread_id} is stuck. Auto-recovering...")
            clear_thread_for_user(user_id)
            thread = get_thread_for_user(user_id)
            client.agents.create_message(
                thread_id=thread.id,
                role="user",
                content=contextual_message,
            )
            return thread.id
        else:
            raise e
    return thread_id
def get_fast_intent(question: str) -> str:
    """Classify the user intent locally without waking up the massive Orchestrator Agent."""
    try:
        # Standard heuristic matching
        question_lower = question.lower()
        if "leave" in question_lower or "vacation" in question_lower or "time off" in question_lower or "mc" in question_lower:
            return "LEAVE"
        elif "room" in question_lower or "book" in question_lower or "meeting" in question_lower:
            return "ROOM"
        elif any(k in question_lower for k in ["visitor", "guest", "evisitor", "pre register", "appointment", "arrival", "lobby", "register"]):
            return "VISITOR"
        elif "shuttle" in question_lower or "bus" in question_lower or "route" in question_lower:
            return "SHUTTLE"
        elif "it" in question_lower or "ticket" in question_lower or "laptop" in question_lower or "fix" in question_lower:
            return "IT"
        elif "hr" in question_lower or "policy" in question_lower or "handbook" in question_lower or "allowed" in question_lower:
            return "HR"
            
        print("⚡ Fast Pre-Router: Falling back to Orchestrator for complex query")
        return "UNKNOWN"
    except Exception as e:
        print(f"Fast intent router failed: {e}")
        return "UNKNOWN"

def ask_agent_stream(question: str, user_id: str = "emp_001"):
    """
    Generator function that streams responses out to the frontend as Server-Sent Events (SSE).
    It still handles tool calling and Orchestrator routing natively, but yields text as it's generated.
    """
    try:
        from typing import Any
        from azure.ai.projects.models import MessageDeltaChunk, MessageDeltaTextContent, AgentEventHandler
        
        class ToolOutputQueueHandler(AgentEventHandler):
            def __init__(self, q):
                super().__init__()
                self.q = q
                
            def on_message_delta(self, delta) -> None:
                # In the Azure SDK, the delta argument is actually a MessageDeltaChunk
                delta_obj = getattr(delta, "delta", delta)
                if hasattr(delta_obj, "content"):
                    for content_part in delta_obj.content:
                        if type(content_part).__name__ == "MessageDeltaTextContent":
                            val = getattr(content_part.text, "value", "")
                            self.q.put(("text", val))

            def on_unhandled_event(self, event_type: str, event_data: Any, **kwargs: Any) -> None:
                # Catch the run.created event to get the resume run ID. The Azure SDK represents this as a dict payload.
                if event_type == "thread.run.created":
                    run_id = event_data.get("id") if isinstance(event_data, dict) else getattr(event_data, "id", None)
                    self.q.put(("run_id", run_id))
                    
            def on_error(self, data: str) -> None:
                self.q.put(("error", data))

        # 1. Fast Intent Classification
        fast_intent = get_fast_intent(question)
        if fast_intent in ["LEAVE", "ROOM", "IT", "HR", "VISITOR", "SHUTTLE"]:
            print(f"⚡ Fast Pre-Router caught intent: {fast_intent}")
            client, active_agent, active_toolset = get_agent(fast_intent.lower())
        else:
            client, active_agent, active_toolset = get_agent("orchestrator")
            
        thread = get_thread_for_user(user_id)
        thread_id = _ensure_message_created(client, thread.id, user_id, question)

        # 2. Execution logic inside a recursive-like loop to handle Handoffs and Tool Calls
        def stream_agent_execution(agent_instance, agent_tools, is_handoff=False):
            current_run_id = None
            
            with client.agents.create_stream(thread_id=thread_id, agent_id=agent_instance.id) as stream:
                for event in stream:
                    # Capture the run ID from the first ThreadRun event
                    if type(event).__name__ == "tuple" and len(event) >= 2:
                        event_type, payload = event[0], event[1]
                        
                        if event_type == "thread.run.created":
                            current_run_id = payload.get("id") if isinstance(payload, dict) else getattr(payload, "id", None)
                            
                        elif event_type == "thread.message.delta":
                            # The payload is a MessageDelta object
                            delta = getattr(payload, "delta", None)
                            if delta and hasattr(delta, "content"):
                                for content_part in delta.content:
                                    if type(content_part).__name__ == "MessageDeltaTextContent":
                                        text_val = getattr(content_part.text, "value", "")
                                        if text_val:
                                            yield f"data: {json.dumps({'type': 'content', 'text': text_val})}\n\n"
                    
            if not current_run_id:
                yield f"data: {json.dumps({'type': 'error', 'text': 'Failed to capture Run ID from stream.'})}\n\n"
                return
                
            # Outside the stream, check if we halted for a required action
            run = client.agents.get_run(thread_id, current_run_id)
            if run.status == "requires_action":
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                routed_target = None
                
                # Check for routing handoff from orchestrator first
                if not is_handoff and tool_calls and tool_calls[0].function.name.startswith("route_to_"):
                    route_name = tool_calls[0].function.name
                    if "leave" in route_name: routed_target = "leave"
                    elif "room" in route_name: routed_target = "room"
                    elif "it" in route_name: routed_target = "it"
                    elif "hr" in route_name: routed_target = "hr"
                    elif "visitor" in route_name: routed_target = "visitor"
                    elif "shuttle" in route_name: routed_target = "shuttle"
                    
                    if routed_target:
                        print(f"🔀 Orchestrator routing to: {route_name}")
                        try:
                            client.agents.cancel_run(thread_id=thread_id, run_id=run.id)
                        except Exception as e:
                            print(f"⚠️ Warning: Cancel run safely ignored due to timeout: {e}")
                        
                        # Fetch the new agent and stream directly into the same generator
                        _, sub_agent, sub_tools = get_agent(routed_target)
                        yield from stream_agent_execution(sub_agent, sub_tools, is_handoff=True)
                        return # End the original generator so it doesn't try to continue

                # Look for destructive tools requiring user confirmation
                destructive_tools = ["apply_leave", "book_meeting_room", "create_ticket", "register_visitor"]
                for tool_call in tool_calls:
                    if tool_call.function.name in destructive_tools:
                        print(f"⏸️ Pausing stream for confirmation: {tool_call.function.name}")
                        yield f"data: {json.dumps({'type': 'confirmation_required', 'thread_id': thread_id, 'run_id': run.id, 'tool_call_id': tool_call.id, 'tool_name': tool_call.function.name, 'arguments': json.loads(tool_call.function.arguments)})}\n\n"
                        return # Pause streaming completely until frontend hits /chat/confirm
                
                # Otherwise, execute tools automatically and resume streaming
                print(f"⚙️ Streaming agent executing {len(tool_calls)} tool(s)...")
                # Send a visual indicator to UI that we are thinking
                action_names = [tc.function.name for tc in tool_calls]
                yield f"data: {json.dumps({'type': 'action_started', 'actions': action_names})}\n\n"
                
                tool_outputs = agent_tools.execute_tool_calls(tool_calls)
                
                # We must start a NEW stream to submit the tool outputs
                resume_run_id = None
                
                # submit_tool_outputs_to_stream requires an event_handler and is a blocking call. 
                # We wrap it in a thread and pipe events to a queue so we can yield them asynchronously.
                q = queue.Queue()
                handler = ToolOutputQueueHandler(q)
                
                def run_submit():
                    try:
                        client.agents.submit_tool_outputs_to_stream(
                            thread_id=thread_id,
                            run_id=run.id,
                            tool_outputs=tool_outputs,
                            event_handler=handler
                        )
                        handler.until_done()
                    except Exception as e:
                        q.put(("error", str(e)))
                    finally:
                        q.put(("done", None))
                        
                t = threading.Thread(target=run_submit)
                t.start()
                
                while True:
                    evt_type, val = q.get()
                    if evt_type == "done":
                        break
                    elif evt_type == "run_id":
                        resume_run_id = val
                    elif evt_type == "text" and val:
                        yield f"data: {json.dumps({'type': 'content', 'text': val})}\n\n"
                    elif evt_type == "error":
                        yield f"data: {json.dumps({'type': 'error', 'text': f'Tool stream error: {val}'})}\n\n"
                    
                # Evaluate if it halted for MORE actions recursively
                if resume_run_id:
                    run = client.agents.get_run(thread_id, resume_run_id)
                # Technically we could recurse if it asked for more tools, but normally one loop suffices.
            
            if run.status == "failed":
                yield f"data: {json.dumps({'type': 'error', 'text': f'Agent run failed: {run.last_error}'})}\n\n"
        
        # Start the execution 
        yield from stream_agent_execution(active_agent, active_toolset)

        # Let frontend know the stream is structurally complete
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    except Exception as e:
        print(f"❌ Error in ask_agent_stream: {e}")
        traceback.print_exc()
        yield f"data: {json.dumps({'type': 'error', 'text': str(e)})}\n\n"
        
def ask_agent(question: str, user_id: str = "emp_001") -> str:
    """
    Send a question to the Multi-Agent Orchestrator. 
    It determines the correct sub-agent, intercepts routing, and seamlessly 
    swaps the active agent to fulfill the user's request.
    """
    try:
        # 0. Fast Pre-Routing
        fast_intent = get_fast_intent(question)
        
        if fast_intent in ["LEAVE", "ROOM", "IT", "HR", "VISITOR", "SHUTTLE"]:
            print(f"⚡ Fast Pre-Router caught intent: {fast_intent}")
            agent_type = fast_intent.lower()
        else:
            agent_type = "orchestrator"
            
        # 1. Start with the chosen Agent
        client, active_agent, active_toolset = get_agent(agent_type)
        thread = get_thread_for_user(user_id)

        # 2. Add Contextual User Message
        today = date.today().strftime("%Y-%m-%d")
        contextual_message = (
            f"[System Context: user_id={user_id}, current_date={today}]\n"
            f"User message: {question}"
        )

        try:
            client.agents.create_message(
                thread_id=thread.id,
                role="user",
                content=contextual_message,
            )
        except Exception as e:
            # Self-healing logic: If previous thread is stuck awaiting confirmation 
            # (e.g., user refreshed the tab and skipped it), we reset the thread.
            if "while a run" in str(e) and "is active" in str(e):
                print(f"⚠️ Thread {thread.id} is stuck. Auto-recovering...")
                clear_thread_for_user(user_id)
                thread = get_thread_for_user(user_id)
                client.agents.create_message(
                    thread_id=thread.id,
                    role="user",
                    content=contextual_message,
                )
            else:
                raise e

        # 3. Execution Loop with Handoff logic
        routed_target = None
        
        run = client.agents.create_run(
            thread_id=thread.id,
            agent_id=active_agent.id
        )

        while run.status in ["queued", "in_progress", "requires_action"]:
            time.sleep(1)
            run = client.agents.get_run(thread_id=thread.id, run_id=run.id)

            if run.status == "requires_action":
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                
                # Check if the Orchestrator is trying to route
                if tool_calls and tool_calls[0].function.name.startswith("route_to_"):
                    route_name = tool_calls[0].function.name
                    print(f"🔀 Orchestrator is routing to: {route_name}")
                    
                    if "leave" in route_name: routed_target = "leave"
                    elif "room" in route_name: routed_target = "room"
                    elif "it" in route_name: routed_target = "it"
                    elif "hr" in route_name: routed_target = "hr"
                    elif "visitor" in route_name: routed_target = "visitor"
                    elif "shuttle" in route_name: routed_target = "shuttle"
                    
                    # Cancel the orchestrator run so it stops processing
                    try:
                        client.agents.cancel_run(thread_id=thread.id, run_id=run.id)
                    except Exception as e:
                        print(f"⚠️ Warning: Cancel run safely ignored due to timeout: {e}")
                    break
                
                # Standard tool execution for sub-agents
                print(f"⚙️ Agent executing {len(tool_calls)} tool(s)...")
                
                # Check for destructive tools requiring user confirmation
                destructive_tools = ["apply_leave", "book_meeting_room", "create_ticket", "register_visitor"]
                for tool_call in tool_calls:
                    if tool_call.function.name in destructive_tools:
                        print(f"⏸️ Pausing execution for user confirmation of {tool_call.function.name}")
                        return {
                            "type": "confirmation_required",
                            "requires_confirmation": True,
                            "thread_id": thread.id,
                            "run_id": run.id,
                            "tool_call_id": tool_call.id,
                            "tool_name": tool_call.function.name,
                            "arguments": json.loads(tool_call.function.arguments)
                        }
                        
                tool_outputs = active_toolset.execute_tool_calls(tool_calls)
                
                client.agents.submit_tool_outputs_to_run(
                    thread_id=thread.id, 
                    run_id=run.id, 
                    tool_outputs=tool_outputs
                )

        # 4. Perform Sub-Agent Handoff if trigger was fired
        if routed_target:
            client, sub_agent, sub_toolset = get_agent(routed_target)
            print(f"🚀 Handing off to specialized agent: {routed_target.upper()}")
            
            # Start a NEW run on the SAME thread using the SUB-AGENT
            run = client.agents.create_run(
                thread_id=thread.id,
                agent_id=sub_agent.id
            )
            
            # Sub-agent execution loop
            while run.status in ["queued", "in_progress", "requires_action"]:
                time.sleep(1)
                run = client.agents.get_run(thread_id=thread.id, run_id=run.id)

                if run.status == "requires_action":
                    tool_calls = run.required_action.submit_tool_outputs.tool_calls
                    print(f"⚙️ Sub-Agent ({routed_target}) executing {len(tool_calls)} tool(s)...")
                    
                    # Intercept destructive tools requiring user confirmation
                    destructive_tools = ["apply_leave", "book_meeting_room", "create_ticket", "register_visitor"]
                    for tool_call in tool_calls:
                        if tool_call.function.name in destructive_tools:
                            print(f"⏸️ Pausing execution for user confirmation of {tool_call.function.name} in sub-agent")
                            return {
                                "type": "confirmation_required",
                                "requires_confirmation": True,
                                "thread_id": thread.id,
                                "run_id": run.id,
                                "tool_call_id": tool_call.id,
                                "tool_name": tool_call.function.name,
                                "arguments": json.loads(tool_call.function.arguments)
                            }
                            
                    tool_outputs = sub_toolset.execute_tool_calls(tool_calls)
                    
                    client.agents.submit_tool_outputs_to_run(
                        thread_id=thread.id, 
                        run_id=run.id, 
                        tool_outputs=tool_outputs
                    )

        # 5. Check outcome and retrieve final response
        if run.status == "failed":
            print(f"⚠️ Agent run failed: {run.last_error}")
            return {"type": "error", "text": "I'm sorry, I encountered an error processing your request."}

        # Fetch messages to show final response
        messages = client.agents.list_messages(thread_id=thread.id)
        if hasattr(messages, "data"):
            for msg in messages.data:
                if msg.role == "assistant":
                    for content_item in msg.content:
                        if hasattr(content_item, "text"):
                            return {"type": "message", "text": content_item.text.value}

        return {"type": "message", "text": "I apologize, but I couldn't generate a response."}

    except Exception as e:
        print(f"❌ Error in ask_agent: {e}")
        traceback.print_exc()
        return {"type": "error", "text": f"I encountered an error: {str(e)}"}

def confirm_tool_execution(thread_id: str, run_id: str, tool_call_id: str, tool_name: str, arguments: dict, confirmed: bool) -> dict:
    """
    Resume an agent thread after explicit user confirmation (or cancellation) of a pending tool call.
    """
    try:
        client, _, _ = get_agent()
        
        if confirmed:
            print(f"✅ User CONFIRMED execution of {tool_name}")
            # Map the string name back to the actual callable in our toolset
            # We can use our toolset dispatcher to execute just this one tool call manually
            
            # Reconstruct the tool output structure
            # Since we already have the raw arguments dict from the client, we reconstruct it cleanly
            function_args = json.dumps(arguments)
            
            try:
                if tool_name == "apply_leave":
                    from app.tools import apply_leave
                    output_str = apply_leave(**arguments)
                elif tool_name == "book_meeting_room":
                    from app.tools import book_meeting_room
                    output_str = book_meeting_room(**arguments)
                elif tool_name == "create_ticket":
                    from app.tools import create_ticket
                    output_str = create_ticket(**arguments)
                elif tool_name == "register_visitor":
                    from app.tools import register_visitor

                    visitor_args = dict(arguments or {})
                    if not visitor_args.get("host_id"):
                        inferred_user_id = get_user_id_for_thread(thread_id)
                        if inferred_user_id:
                            visitor_args["host_id"] = inferred_user_id

                    # Ensure all expected fields exist so manual confirmation payloads remain robust.
                    visitor_args.setdefault("visitor_name", "")
                    visitor_args.setdefault("company", "")
                    visitor_args.setdefault("date", "")
                    visitor_args.setdefault("time", "")
                    visitor_args.setdefault("purpose", "")
                    visitor_args.setdefault("visitor_ic", "")
                    visitor_args.setdefault("visitor_email", "")
                    visitor_args.setdefault("to_date", "")
                    visitor_args.setdefault("looking_for", "")

                    output_str = register_visitor(**visitor_args)
                else:
                    output_str = json.dumps({"error": f"Unknown tool capability: {tool_name}"})
            except Exception as e:
                output_str = json.dumps({"error": f"Tool execution failed: {str(e)}"})
            
            tool_outputs = [{"tool_call_id": tool_call_id, "output": output_str}]
        else:
            print(f"❌ User CANCELLED execution of {tool_name}")
            tool_outputs = [{"tool_call_id": tool_call_id, "output": json.dumps({"status": "cancelled", "message": "The user decided not to proceed with this action."})}]
            
        # Submit the results back to the agent
        client.agents.submit_tool_outputs_to_run(
            thread_id=thread_id, 
            run_id=run_id, 
            tool_outputs=tool_outputs
        )
        
        # Resume polling the run status until completed
        import time
        run = client.agents.get_run(thread_id=thread_id, run_id=run_id)
        while run.status in ["queued", "in_progress", "requires_action"]:
            time.sleep(1)
            run = client.agents.get_run(thread_id=thread_id, run_id=run_id)
            
            # Note: For simplicity in this implementation, we assume a single blocked tool call resolution
            # If it queues ANOTHER tool call immediately, we execute it automatically here unless it's ALSO destructive.
            # To be thoroughly safe, we duplicate the interception block:
            if run.status == "requires_action":
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                if tool_calls:
                    destructive_tools = ["apply_leave", "book_meeting_room", "create_ticket", "register_visitor"]
                    for tool_call in tool_calls:
                        if tool_call.function.name in destructive_tools:
                            return {
                                "type": "confirmation_required",
                                "requires_confirmation": True,
                                "thread_id": thread_id,
                                "run_id": run.id,
                                "tool_call_id": tool_call.id,
                                "tool_name": tool_call.function.name,
                                "arguments": json.loads(tool_call.function.arguments)
                            }
                    
                    t_outputs = toolset.execute_tool_calls(tool_calls)
                    client.agents.submit_tool_outputs_to_run(thread_id=thread_id, run_id=run.id, tool_outputs=t_outputs)

        if run.status == "failed":
            return {"type": "error", "text": f"Agent run failed after Tool execution: {run.last_error}"}

        # Retrieve messages from the thread
        messages = client.agents.list_messages(thread_id=thread_id)

        # Extract the assistant's final response
        if hasattr(messages, "data"):
            for msg in messages.data:
                if msg.role == "assistant":
                    for content_item in msg.content:
                        if hasattr(content_item, "text"):
                            return {"type": "message", "text": content_item.text.value}
                            
        return {"type": "message", "text": "Action completed, but no response generated."}
        
    except Exception as e:
        print(f"❌ Error in confirm_tool_execution: {e}")
        traceback.print_exc()
        return {"type": "error", "text": f"Failed to resume execution: {str(e)}"}
