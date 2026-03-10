"""Meeting Room Management Module"""
import json
import os
from typing import Dict, List, Optional
from datetime import datetime
import uuid
from .db import get_db

def get_available_rooms() -> List[Dict]:
    """Get all available meeting rooms"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM rooms")
        rows = cursor.fetchall()
        
        rooms = []
        for row in rows:
            room = dict(row)
            # Reconstruct the features list from the JSON string
            if "features_json" in room and room["features_json"]:
                room["features"] = json.loads(room["features_json"])
                del room["features_json"]
            rooms.append(room)
        return rooms

def search_meeting_rooms(date: str, start_time: str, end_time: str, capacity: Optional[int] = None, features: Optional[str] = None) -> Dict:
    """
    Search for available meeting rooms matching criteria.
    """
    rooms = get_available_rooms()
    available_rooms = []
    
    # Filter by capacity and features
    for room in rooms:
        # Check capacity
        if capacity and room['capacity'] < capacity:
            continue
            
        # Check features
        if features:
            req_features = [f.strip().lower() for f in features.split(',')]
            room_features = [f.lower() for f in room.get('features', [])]
            if not all(rf in room_features for rf in req_features):
                continue
                
        # Check availability on date/time
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM room_bookings 
                WHERE room_id = ? AND date = ? AND status != 'cancelled'
            """, (room['room_id'], date))
            
            existing_bookings = cursor.fetchall()
            is_available = True
            for booking_row in existing_bookings:
                booking = dict(booking_row)
                if not (end_time <= booking['start_time'] or start_time >= booking['end_time']):
                    is_available = False
                    break
                    
        if is_available:
            available_rooms.append(room)
            
    if not available_rooms:
        return {
            "success": False,
            "message": "No meeting rooms found matching those exact requirements for that time."
        }
        
    message = "Here are the available meeting rooms matching your criteria:\n\n"
    message += "```room-list\n"
    # only include essential info for AI
    simpl_rooms = [{"room_id": r["room_id"], "name": r["name"], "capacity": r["capacity"], "features": r.get("features", [])} for r in available_rooms]
    message += json.dumps(simpl_rooms, indent=2)
    message += "\n```\n"
    
    return {
        "success": True,
        "message": message,
        "rooms": available_rooms
    }

def book_meeting_room(user_id: str, room_id: str, date: str, start_time: str, end_time: str, purpose: str = "") -> Dict:
    """
    Book a meeting room
    Returns: {"success": bool, "message": str, "booking_id": str}
    """
    rooms = get_available_rooms()
    room = next((r for r in rooms if r['room_id'] == room_id), None)
    
    if not room:
        # Try to find room by name
        room = next((r for r in rooms if r['name'].lower() == room_id.lower()), None)
        if room:
            room_id = room['room_id']
        else:
            return {
                "success": False,
                "message": f"Room '{room_id}' not found. Available rooms: {', '.join([r['name'] for r in rooms])}"
            }
            
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check if room is available at that time
        cursor.execute("""
            SELECT * FROM room_bookings 
            WHERE room_id = ? AND date = ? AND status != 'cancelled'
        """, (room_id, date))
        
        existing_bookings = cursor.fetchall()
        for booking_row in existing_bookings:
            booking = dict(booking_row)
            # Check time overlap
            if not (end_time <= booking['start_time'] or start_time >= booking['end_time']):
                # Find next available slot for the same duration
                try:
                    start_dt = datetime.strptime(start_time, "%H:%M")
                    end_dt = datetime.strptime(end_time, "%H:%M")
                    duration = end_dt - start_dt
                    
                    # Sort bookings to find an opening
                    sorted_bookings = sorted([dict(b) for b in existing_bookings], key=lambda x: x['start_time'])
                    next_start = None
                    last_end = "08:00" # Assume work day starts at 8
                    
                    for b in sorted_bookings:
                        if b['start_time'] >= booking['end_time']: 
                            # we only care about slots after the blocking booking
                            continue
                        last_end = max(last_end, b['end_time'])
                    
                    # Next slot would realistically be the end of the booking that blocked us, or later
                    possible_start_dt = datetime.strptime(booking['end_time'], "%H:%M")
                    possible_end_dt = possible_start_dt + duration
                    
                    next_start = possible_start_dt.strftime("%H:%M")
                    next_end = possible_end_dt.strftime("%H:%M")
                    
                    # Re-verify this proposed slot doesn't overlap later bookings
                    is_valid_next = True
                    for b in sorted_bookings:
                        if not (next_end <= b['start_time'] or next_start >= b['end_time']):
                            is_valid_next = False
                            break
                    
                    if is_valid_next and possible_end_dt <= datetime.strptime("18:00", "%H:%M"): # Assume work day ends at 18:00
                        return {
                            "success": False,
                            "message": f"Room '{room['name']}' is already booked from {booking['start_time']} to {booking['end_time']} on {date}. \n\nHowever, it IS available later from {next_start} to {next_end}. Should I book that instead?"
                        }
                except Exception:
                    pass # Ignore if time parsing fails, fallback to standard rejection

                return {
                    "success": False,
                    "message": f"Room '{room['name']}' is already booked from {booking['start_time']} to {booking['end_time']} on {date}."
                }
        
        # Create booking
        booking_id = f"RB{str(uuid.uuid4())[:8].upper()}"
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("""
            INSERT INTO room_bookings (
                booking_id, room_id, user_id, date, start_time, end_time, purpose, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'confirmed', ?)
        """, (booking_id, room_id, user_id, date, start_time, end_time, purpose, created_at))
        
        conn.commit()
    
    return {
        "success": True,
        "message": f"Meeting room '{room['name']}' booked successfully! Booking ID: {booking_id}. Reserved for {date} from {start_time} to {end_time}.",
        "booking_id": booking_id,
        "room_name": room['name']
    }

def get_user_bookings(user_id: str) -> List[Dict]:
    """Get all bookings for a user with room names"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT rb.*, r.name as room_name 
            FROM room_bookings rb
            LEFT JOIN rooms r ON rb.room_id = r.room_id
            WHERE rb.user_id = ? AND rb.status != 'cancelled'
        """, (user_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def list_available_rooms() -> Dict:
    """
    List all available meeting rooms
    Returns: {"success": bool, "message": str, "rooms": list}
    """
    rooms = get_available_rooms()
    
    if not rooms:
        return {
            "success": False,
            "message": "No meeting rooms found"
        }
    
    message = "Here are the available meeting rooms:\n\n"
    message += "```room-list\n"
    message += json.dumps(rooms, indent=2)
    message += "\n```\n"
    
    return {
        "success": True,
        "message": message,
        "rooms": rooms
    }

