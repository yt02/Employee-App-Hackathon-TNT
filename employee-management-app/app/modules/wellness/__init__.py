"""
Wellness Module
Handles wellness programs, activity logging, and statistics
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict

# Get the project root directory (3 levels up from this file)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
PROGRAMS_FILE = os.path.join(PROJECT_ROOT, 'data', 'mock_data', 'wellness_programs.json')
LOGS_FILE = os.path.join(PROJECT_ROOT, 'data', 'mock_data', 'wellness_logs.json')

def load_programs() -> List[Dict]:
    """Load wellness programs from JSON file"""
    try:
        with open(PROGRAMS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def load_logs() -> List[Dict]:
    """Load wellness logs from JSON file"""
    try:
        with open(LOGS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_logs(logs: List[Dict]):
    """Save wellness logs to JSON file"""
    with open(LOGS_FILE, 'w') as f:
        json.dump(logs, f, indent=4)

def save_programs(programs: List[Dict]):
    """Save wellness programs to JSON file"""
    with open(PROGRAMS_FILE, 'w') as f:
        json.dump(programs, f, indent=4)

def view_activities(category: Optional[str] = None) -> Dict:
    """View available wellness programs/activities"""
    programs = load_programs()
    
    # Apply filters
    if category:
        programs = [p for p in programs if p['category'] == category]
    
    return {
        "success": True,
        "data": programs
    }

def join_activity(user_id: str, program_id: str) -> Dict:
    """Join a wellness program"""
    programs = load_programs()
    
    # Find the program
    program = next((p for p in programs if p['program_id'] == program_id), None)
    if not program:
        return {"success": False, "message": "Program not found"}
    
    # Check capacity
    if program['enrolled_count'] >= program['max_participants']:
        return {"success": False, "message": "Program is full"}
    
    # Increment enrolled count
    program['enrolled_count'] += 1
    save_programs(programs)
    
    return {
        "success": True,
        "message": f"Successfully joined {program['title']}",
        "data": program
    }

def log_wellness(
    user_id: str,
    activity_type: str,
    value: float,
    unit: str,
    date: Optional[str] = None,
    notes: str = ""
) -> Dict:
    """Log a wellness activity"""
    logs = load_logs()
    
    # Generate log ID
    log_id = f"LOG_{str(len(logs) + 1).zfill(3)}"
    
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    new_log = {
        "log_id": log_id,
        "user_id": user_id,
        "date": date,
        "activity_type": activity_type,
        "value": value,
        "unit": unit,
        "notes": notes,
        "created_at": datetime.now().isoformat()
    }
    
    logs.append(new_log)
    save_logs(logs)
    
    return {
        "success": True,
        "message": "Wellness activity logged successfully",
        "data": new_log
    }

def view_wellness_stats(user_id: str, month: Optional[str] = None) -> Dict:
    """View user's wellness statistics"""
    logs = load_logs()
    
    # Filter logs for this user
    user_logs = [log for log in logs if log['user_id'] == user_id]
    
    # Filter by month if specified
    if month:
        user_logs = [log for log in user_logs if log['date'].startswith(month)]
    
    # Calculate statistics by activity type
    stats = defaultdict(lambda: {"total": 0, "count": 0, "unit": ""})
    
    for log in user_logs:
        activity_type = log['activity_type']
        stats[activity_type]["total"] += log['value']
        stats[activity_type]["count"] += 1
        stats[activity_type]["unit"] = log['unit']
    
    # Format statistics
    formatted_stats = []
    for activity_type, data in stats.items():
        formatted_stats.append({
            "activity_type": activity_type,
            "total": data["total"],
            "count": data["count"],
            "average": round(data["total"] / data["count"], 2) if data["count"] > 0 else 0,
            "unit": data["unit"]
        })
    
    return {
        "success": True,
        "data": {
            "statistics": formatted_stats,
            "recent_logs": user_logs[-10:]  # Last 10 logs
        }
    }

