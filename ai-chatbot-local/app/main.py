from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
from app.chat import ask
from app.azure_agent import confirm_tool_execution, ask_agent_stream
from app.modules.db import get_db
import os
import json
import sys
import threading
import io
import migrate_to_postgres_v2

app = FastAPI()
print("FASTAPI_STARTUP_MARKER_V2_DEBUG_ACTIVE")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory
static_path = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

# Get path to mock data directory
mock_data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "mock_data")

class ChatRequest(BaseModel):
    message: str
    user_id: str = "emp_001"  # Default user for testing

class ConfirmRequest(BaseModel):
    thread_id: str
    run_id: str
    tool_call_id: str
    tool_name: str
    arguments: Dict[str, Any]
    confirmed: bool

import sys
import threading

print("FASTAPI_STARTUP_MARKER_V3_FINAL", flush=True)

@app.on_event("startup")
def pre_warm_agents():
    def _warmup():
        print("🔥 Starting background pre-warming of Azure Agents...", flush=True)
        try:
            from app.azure_agent import get_agent
            from app.config import AZURE_LEAVE_AGENT_ID, AZURE_ROOM_AGENT_ID, AZURE_IT_AGENT_ID, AZURE_HR_AGENT_ID
            
            get_agent("orchestrator")
            if AZURE_LEAVE_AGENT_ID: get_agent("leave")
            if AZURE_ROOM_AGENT_ID: get_agent("room")
            if AZURE_IT_AGENT_ID: get_agent("it")
            if AZURE_HR_AGENT_ID: get_agent("hr")
            
            print("✅ All Azure Agents pre-warmed and ready.", flush=True)
        except Exception as e:
            print(f"⚠️ Pre-warm failed: {e}", flush=True)
            
    threading.Thread(target=_warmup, daemon=True).start()
    
    # Run migrations on startup (safe for Postgres)
    if os.environ.get("DATABASE_URL"):
        try:
            print("🚀 Running database migrations for Azure (V2)...", flush=True)
            migrate_to_postgres_v2.migrate()
            print("✅ Database migrations completed.", flush=True)
        except Exception as e:
            print(f"⚠️ Migration failed: {e}", flush=True)

@app.get("/")
async def read_root():
    return {"message": "Hello World V3", "diag": "diag_active"}

@app.get("/api/admin/migrate")
async def run_migration_manually():
    try:
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            migrate_to_postgres_v2.migrate()
        
        return {"success": True, "output": f.getvalue()}
    except Exception as e:
        import traceback
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": "v3.final"}

@app.post("/api/auth/login")
async def login(req: Dict[str, str]):
    """Authenticate user against PostgreSQL/SQLite"""
    username = req.get("username")
    password = req.get("password")
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()
            
            if user:
                # Remove password
                user_data = dict(user)
                if "password" in user_data:
                    del user_data["password"]
                return JSONResponse(content={"success": True, "data": user_data})
                
            return JSONResponse(content={"success": False, "message": "Invalid username or password"}, status_code=401)
    except Exception as e:
        return JSONResponse(content={"success": False, "message": f"Database error: {str(e)}"}, status_code=500)

@app.get("/api/user/{user_id}")
async def get_user(user_id: str):
    """Fetch user data by user_id"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            user = cursor.fetchone()
            
            if user:
                return JSONResponse(content={"success": True, "data": dict(user)})
                
            return JSONResponse(content={"error": "User not found"}, status_code=404)
    except Exception as e:
        return JSONResponse(content={"error": f"Database error: {str(e)}"}, status_code=500)

# Unified endpoints for Mobile App Core features
@app.get("/api/leave/balance/{user_id}")
async def get_leave_balance_api(user_id: str):
    try:
        from app.modules.leave_manager import get_leave_balance
        balance = get_leave_balance(user_id)
        if balance:
            data = {
                "annual": balance["annual_leave"]["remaining"],
                "sick": balance["medical_leave"]["remaining"],
                "personal": balance["unpaid_leave"]["remaining"]
            }
            return JSONResponse(content={"success": True, "data": data})
        return JSONResponse(content={"success": False, "message": "Balance not found for user"}, status_code=404)
    except Exception as e:
        print(f"❌ Error in get_leave_balance_api: {str(e)}")
        return JSONResponse(content={"success": False, "message": f"Server error: {str(e)}"}, status_code=500)

@app.post("/api/leave/apply/{user_id}")
async def apply_leave_api(user_id: str, req: Dict[str, Any]):
    try:
        from app.modules.leave_manager import apply_leave
        # Map mobile app fields to backend fields
        leave_type_map = {
            "annual": "annual_leave",
            "sick": "medical_leave",
            "personal": "unpaid_leave"
        }
        leave_type = leave_type_map.get(req.get("leave_type"), "annual_leave")
        result = apply_leave(
            user_id=user_id,
            leave_type=leave_type,
            start_date=req.get("start_date"),
            end_date=req.get("end_date"),
            reason=req.get("reason", "")
        )
        return JSONResponse(content=result)
    except Exception as e:
        print(f"❌ Error in apply_leave_api: {str(e)}")
        return JSONResponse(content={"success": False, "message": f"Server error: {str(e)}"}, status_code=500)

@app.get("/api/leave/history/{user_id}")
async def get_leave_history_api(user_id: str):
    from app.modules.leave_manager import get_leave_requests
    history = get_leave_requests(user_id)
    return JSONResponse(content={"success": True, "data": history})

@app.get("/api/rooms/list")
async def get_rooms_api():
    try:
        from app.modules.room_manager import get_available_rooms
        rooms = get_available_rooms()
        # Format for mobile app (ensure facilities is a list)
        formatted_rooms = []
        for r in rooms:
            formatted_rooms.append({
                "room_id": r["room_id"],
                "name": r["name"],
                "capacity": r["capacity"],
                "facilities": r.get("features", [])
            })
        return JSONResponse(content={"success": True, "data": formatted_rooms})
    except Exception as e:
        print(f"❌ Error in get_rooms_api: {str(e)}")
        return JSONResponse(content={"success": False, "message": f"Server error: {str(e)}"}, status_code=500)

@app.post("/api/rooms/book/{user_id}")
async def book_room_api(user_id: str, req: Dict[str, Any]):
    from app.modules.room_manager import book_meeting_room
    result = book_meeting_room(
        user_id=user_id,
        room_id=req.get("room_id"),
        date=req.get("date"),
        start_time=req.get("start_time"),
        end_time=req.get("end_time"),
        purpose=req.get("purpose", "")
    )
    return JSONResponse(content=result)

@app.get("/api/rooms/bookings/{user_id}")
async def get_room_bookings_api(user_id: str):
    from app.modules.room_manager import get_user_bookings
    bookings = get_user_bookings(user_id)
    # The mobile app expects room_name, add it if missing
    from app.modules.room_manager import get_available_rooms
    rooms = {r["room_id"]: r["name"] for r in get_available_rooms()}
    for b in bookings:
        if "room_name" not in b:
            b["room_name"] = rooms.get(b["room_id"], "Unknown Room")
    return JSONResponse(content={"success": True, "data": bookings})

@app.delete("/api/rooms/cancel/{booking_id}/{user_id}")
async def cancel_room_booking_api(booking_id: str, user_id: str):
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE room_bookings SET status = 'cancelled' WHERE booking_id = ? AND user_id = ?", (booking_id, user_id))
            conn.commit()
            return JSONResponse(content={"success": True, "message": "Booking cancelled"})
    except Exception as e:
        return JSONResponse(content={"success": False, "message": str(e)}, status_code=500)

@app.get("/api/tickets/{user_id}")
async def get_tickets_api(user_id: str):
    from app.modules.ticket_manager import get_user_tickets
    tickets = get_user_tickets(user_id)
    return JSONResponse(content={"success": True, "data": tickets})

@app.post("/api/tickets/create/{user_id}")
async def create_ticket_api(user_id: str, req: Dict[str, Any]):
    from app.modules.ticket_manager import create_ticket
    result = create_ticket(
        user_id=user_id,
        category=req.get("category", "other"),
        subject=req.get("title", "No Subject"), # Mobile app sends 'title'
        description=req.get("description", ""),
        priority=req.get("priority", "medium")
    )
    return JSONResponse(content=result)

# Mock endpoints for Shuttle, Visitor
@app.get("/api/shuttle/routes")
async def get_shuttle_routes():
    # Mock data as these modules are not fully implemented
    routes = [
        {"id": "SH001", "name": "North Route", "departure_time": "08:00", "stops": ["HQ", "Station A", "Office B"]},
        {"id": "SH002", "name": "East Route", "departure_time": "08:30", "stops": ["HQ", "Station C", "Office D"]}
    ]
    return JSONResponse(content={"success": True, "data": routes})

@app.post("/api/shuttle/book/{user_id}")
async def book_shuttle_api(user_id: str, req: Dict[str, Any]):
    return JSONResponse(content={"success": True, "message": "Shuttle booked successfully"})

@app.get("/api/shuttle/bookings/{user_id}")
async def get_shuttle_bookings_api(user_id: str):
    return JSONResponse(content={"success": True, "data": []})

@app.get("/api/visitors")
async def get_visitors_api(host_employee_id: str):
    try:
        from app.modules.visitor_manager import get_user_visitors
        visitors = get_user_visitors(host_employee_id)
        return JSONResponse(content={"success": True, "data": visitors})
    except Exception as e:
        print(f"❌ Error in get_visitors_api: {str(e)}")
        return JSONResponse(content={"success": False, "message": f"Server error: {str(e)}"}, status_code=500)

@app.post("/api/visitors/register")
async def register_visitor_api(req: Dict[str, Any]):
    try:
        from app.modules.visitor_manager import register_visitor
        result = register_visitor(
            host_id=req.get("host_id"),
            visitor_name=req.get("visitor_name"),
            company=req.get("company", ""),
            date=req.get("date"),
            time=req.get("time"),
            purpose=req.get("purpose", ""),
            visitor_ic=req.get("visitor_ic"),
            visitor_email=req.get("visitor_email", ""),
            to_date=req.get("to_date", ""),
            looking_for=req.get("looking_for")
        )
        return JSONResponse(content=result)
    except Exception as e:
        print(f"❌ Error in register_visitor_api: {str(e)}")
        return JSONResponse(content={"success": False, "message": f"Server error: {str(e)}"}, status_code=500)

@app.post("/chat")
async def chat(req: ChatRequest):
    """
    Chat endpoint - returns JSON with answer and optional action results
    """
    response_str = ask(req.message, req.user_id)

    try:
        # Parse the JSON response from ask()
        response_data = json.loads(response_str)
        return JSONResponse(content=response_data)
    except json.JSONDecodeError:
        # Fallback if response is not JSON
        return JSONResponse(content={
            "answer": response_str,
            "action_taken": False
        })
        
@app.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    """
    Streaming Chat endpoint - yields SSE containing partial text or tool invocation data.
    """
    return StreamingResponse(
        ask_agent_stream(req.message, req.user_id),
        media_type="text/event-stream"
    )

@app.post("/chat/confirm")
async def confirm_action(req: ConfirmRequest):
    """
    Confirm endpoint - resumes an agent thread after explicit tool confirmation
    """
    response_dict = confirm_tool_execution(
        thread_id=req.thread_id,
        run_id=req.run_id,
        tool_call_id=req.tool_call_id,
        tool_name=req.tool_name,
        arguments=req.arguments,
        confirmed=req.confirmed
    )
    
    if response_dict.get("type") == "error":
        return JSONResponse(content={
            "answer": response_dict.get("text", "An error occurred."),
            "action_taken": False,
            "error": True
        })
        
    return JSONResponse(content={
        "answer": response_dict.get("text", "Tool executed successfully."),
        "action_taken": req.confirmed,
        "requires_confirmation": False
    })

@app.get("/debug/auth")
async def debug_auth():
    """Diagnostic endpoint to check environment variables and credential status"""
    azure_envs = {k: ("SET (len: " + str(len(os.environ[k])) + ")" if os.environ.get(k) else "MISSING") 
                  for k in os.environ.keys() if k.startswith("AZURE_") or "IDENTITY" in k or k == "PYTHONPATH"}
    
    token = os.environ.get("AZURE_ACCESS_TOKEN", "")
    token_preview = f"{token[:10]}...{token[-10:]}" if len(token) > 20 else "SHORT/EMPTY"
    
    db_diag = {"provider": "unknown", "status": "unknown"}
    try:
        with get_db() as conn:
            from app.modules.db import PgConnectionWrapper
            provider = "PostgreSQL" if isinstance(conn, PgConnectionWrapper) else "SQLite"
            db_diag["provider"] = provider
            
            cursor = conn.cursor()
            if provider == "PostgreSQL":
                cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            else:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            
            tables = [row.get("table_name") if provider == "PostgreSQL" else row.get("name") for row in cursor.fetchall()]
            db_diag["status"] = "connected"
            db_diag["table_count"] = len(tables)
            db_diag["tables"] = sorted(tables)
            
            # Inspect specific table schemas
            db_diag["inspections"] = {}
            for table in ["leave_balances", "visitors"]:
                if table in tables:
                    cursor.execute(f"SELECT * FROM {table} LIMIT 1")
                    row = cursor.fetchone()
                    db_diag["inspections"][table] = {
                        "exists": True,
                        "columns": list(row.keys()) if row else "EMPTY TABLE"
                    }
                else:
                    db_diag["inspections"][table] = {"exists": False}

    except Exception as e:
        db_diag["status"] = "error"
        db_diag["error"] = str(e)

    # Capture migration log from global if needed, for now just a marker
    migration_status = "STABLE" if "visitors" in db_diag.get("tables", []) else "PENDING_MIGRATION"

    return {
        "status": "online",
        "v": "V17_FORCE_SYNC",
        "migration": migration_status,
        "azure_envs": azure_envs,
        "token_preview": token_preview,
        "db": db_diag,
        "cwd": os.getcwd(),
        "files_count": len(os.listdir(".")),
        "m_files": [f for f in os.listdir(".") if f.lower().startswith('m')],
        "files_preview": sorted(os.listdir("."))[0:15] 
    }
