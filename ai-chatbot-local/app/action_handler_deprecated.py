"""Action Handler - Detects intents and executes employee management actions"""
import re
from datetime import datetime, timedelta
from typing import Dict, Optional
from app.modules import leave_manager, room_manager, ticket_manager

# Default user for testing (can be replaced with actual authentication)
DEFAULT_USER_ID = "emp_001"

def parse_date_from_text(text: str) -> Optional[str]:
    """
    Parse date from natural language text
    Returns date in YYYY-MM-DD format
    """
    text_lower = text.lower()
    today = datetime.now()
    
    # Check for specific patterns
    if "today" in text_lower:
        return today.strftime("%Y-%m-%d")
    elif "tomorrow" in text_lower:
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")
    elif "next week" in text_lower:
        return (today + timedelta(days=7)).strftime("%Y-%m-%d")
    elif "next month" in text_lower:
        return (today + timedelta(days=30)).strftime("%Y-%m-%d")
    
    # Try to find date in YYYY-MM-DD format
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', text)
    if date_match:
        return date_match.group(1)
    
    # Try to find date in DD/MM/YYYY or MM/DD/YYYY format
    date_match = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', text)
    if date_match:
        day, month, year = date_match.groups()
        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
    
    return None

def extract_number_of_days(text: str) -> Optional[int]:
    """Extract number of days from text"""
    # Look for patterns like "2 days", "3 day", "one week"
    patterns = [
        (r'(\d+)\s*days?', lambda x: int(x)),
        (r'one\s+day', lambda x: 1),
        (r'two\s+days?', lambda x: 2),
        (r'three\s+days?', lambda x: 3),
        (r'one\s+week', lambda x: 7),
        (r'two\s+weeks?', lambda x: 14),
    ]
    
    text_lower = text.lower()
    for pattern, converter in patterns:
        match = re.search(pattern, text_lower)
        if match:
            if match.groups():
                return converter(match.group(1))
            else:
                return converter(None)
    
    return None

def detect_and_execute_action(user_message: str, user_id: str = DEFAULT_USER_ID) -> Optional[Dict]:
    """
    Detect intent from user message and execute corresponding action
    Returns: {"action_taken": bool, "result": dict} or None if no action detected
    """
    message_lower = user_message.lower()
    
    # ===== LEAVE MANAGEMENT =====
    
    # Check leave balance
    if any(keyword in message_lower for keyword in ["leave balance", "how many leave", "check leave", "remaining leave"]):
        result = leave_manager.check_leave_balance(user_id)
        return {
            "action_taken": True,
            "action_type": "check_leave_balance",
            "result": result
        }
    
    # Apply for leave
    if any(keyword in message_lower for keyword in ["apply leave", "apply for leave", "request leave", "take leave", "book leave"]):
        # Determine leave type
        leave_type = "annual_leave"  # default
        if "medical" in message_lower or "sick" in message_lower:
            leave_type = "medical_leave"
        elif "unpaid" in message_lower:
            leave_type = "unpaid_leave"
        
        # Extract dates
        start_date = parse_date_from_text(user_message)
        days = extract_number_of_days(user_message)
        
        if start_date and days:
            end_date = (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=days-1)).strftime("%Y-%m-%d")
            result = leave_manager.apply_leave(user_id, leave_type, start_date, end_date, "Applied via AI assistant")
            return {
                "action_taken": True,
                "action_type": "apply_leave",
                "result": result
            }
        elif start_date:
            # Default to 1 day if no days specified
            result = leave_manager.apply_leave(user_id, leave_type, start_date, start_date, "Applied via AI assistant")
            return {
                "action_taken": True,
                "action_type": "apply_leave",
                "result": result
            }
    
    # ===== MEETING ROOM BOOKING =====
    
    # List available rooms
    if any(keyword in message_lower for keyword in ["available rooms", "list rooms", "show rooms", "meeting rooms"]):
        result = room_manager.list_available_rooms()
        return {
            "action_taken": True,
            "action_type": "list_rooms",
            "result": result
        }
    
    # Book meeting room
    if any(keyword in message_lower for keyword in ["book room", "book meeting room", "reserve room", "book a room"]):
        # Extract room name/id
        room_id = None
        rooms = room_manager.get_available_rooms()
        for room in rooms:
            if room['name'].lower() in message_lower or room['room_id'].lower() in message_lower:
                room_id = room['room_id']
                break
        
        # Extract date and time
        date = parse_date_from_text(user_message)
        
        # Extract time (simple pattern matching)
        time_match = re.search(r'(\d{1,2})\s*(am|pm|:00)', message_lower)
        start_time = "14:00"  # default 2pm
        end_time = "15:00"    # default 1 hour
        
        if time_match:
            hour = int(time_match.group(1))
            if 'pm' in message_lower and hour < 12:
                hour += 12
            start_time = f"{hour:02d}:00"
            end_time = f"{(hour+1):02d}:00"
        
        if room_id and date:
            result = room_manager.book_meeting_room(user_id, room_id, date, start_time, end_time, "Booked via AI assistant")
            return {
                "action_taken": True,
                "action_type": "book_room",
                "result": result
            }
    
    # ===== IT SUPPORT TICKETS =====
    
    # Check ticket status
    if any(keyword in message_lower for keyword in ["ticket status", "check ticket", "my tickets"]):
        result = ticket_manager.check_ticket_status(user_id)
        return {
            "action_taken": True,
            "action_type": "check_tickets",
            "result": result
        }
    
    # Create IT support ticket
    if any(keyword in message_lower for keyword in ["create ticket", "submit ticket", "it support", "technical issue", "report issue"]):
        # Determine category
        category = "other"
        if "hardware" in message_lower or "computer" in message_lower or "laptop" in message_lower:
            category = "hardware"
        elif "software" in message_lower or "application" in message_lower or "program" in message_lower:
            category = "software"
        elif "network" in message_lower or "wifi" in message_lower or "internet" in message_lower:
            category = "network"
        elif "access" in message_lower or "password" in message_lower or "login" in message_lower:
            category = "access"
        
        # Determine priority
        priority = "medium"
        if "urgent" in message_lower or "critical" in message_lower or "emergency" in message_lower:
            priority = "urgent"
        elif "high" in message_lower or "important" in message_lower:
            priority = "high"
        elif "low" in message_lower:
            priority = "low"
        
        result = ticket_manager.create_ticket(user_id, category, "Issue reported via AI assistant", user_message, priority)
        return {
            "action_taken": True,
            "action_type": "create_ticket",
            "result": result
        }
    
    # No action detected
    return None

