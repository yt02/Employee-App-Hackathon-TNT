"""Meeting Room Booking Module - Room Management and Booking"""
import json
import os
from typing import Optional, Dict, List
from datetime import datetime, time

DATA_DIR = "data/mock_data"
ROOMS_FILE = os.path.join(DATA_DIR, "rooms.json")
BOOKINGS_FILE = os.path.join(DATA_DIR, "room_bookings.json")

def load_rooms() -> List[Dict]:
    """Load rooms from JSON file"""
    with open(ROOMS_FILE, 'r') as f:
        return json.load(f)

def load_bookings() -> List[Dict]:
    """Load bookings from JSON file"""
    with open(BOOKINGS_FILE, 'r') as f:
        return json.load(f)

def save_bookings(bookings: List[Dict]):
    """Save bookings to JSON file"""
    with open(BOOKINGS_FILE, 'w') as f:
        json.dump(bookings, f, indent=2)

def list_rooms() -> List[Dict]:
    """
    Get list of all meeting rooms
    """
    return load_rooms()

def get_room(room_id: str) -> Optional[Dict]:
    """
    Get room details by room_id
    """
    rooms = load_rooms()
    for room in rooms:
        if room['room_id'] == room_id:
            return room
    return None

def check_availability(room_id: str, date: str, start_time: str, end_time: str) -> Dict:
    """
    Check if a room is available for the given date and time
    Returns availability status and conflicting bookings if any
    """
    bookings = load_bookings()
    
    # Find bookings for this room on this date
    room_bookings = [
        b for b in bookings 
        if b['room_id'] == room_id and b['date'] == date and b['status'] == 'confirmed'
    ]
    
    # Check for time conflicts
    conflicts = []
    for booking in room_bookings:
        # Convert times to comparable format
        req_start = datetime.strptime(start_time, "%H:%M").time()
        req_end = datetime.strptime(end_time, "%H:%M").time()
        book_start = datetime.strptime(booking['start_time'], "%H:%M").time()
        book_end = datetime.strptime(booking['end_time'], "%H:%M").time()
        
        # Check if times overlap
        if not (req_end <= book_start or req_start >= book_end):
            conflicts.append(booking)
    
    if conflicts:
        return {
            "available": False,
            "message": "Room is not available for the requested time",
            "conflicts": conflicts
        }
    
    return {
        "available": True,
        "message": "Room is available"
    }

def book_room(user_id: str, room_id: str, date: str, start_time: str, end_time: str, purpose: str) -> Dict:
    """
    Book a meeting room
    """
    # Validate room exists
    room = get_room(room_id)
    if not room:
        return {
            "success": False,
            "message": "Room not found"
        }
    
    # Check availability
    availability = check_availability(room_id, date, start_time, end_time)
    if not availability['available']:
        return {
            "success": False,
            "message": availability['message'],
            "conflicts": availability.get('conflicts', [])
        }
    
    # Create booking
    bookings = load_bookings()
    booking_id = f"BK{str(len(bookings) + 1).zfill(3)}"
    
    new_booking = {
        "booking_id": booking_id,
        "room_id": room_id,
        "user_id": user_id,
        "date": date,
        "start_time": start_time,
        "end_time": end_time,
        "purpose": purpose,
        "status": "confirmed",
        "created_at": datetime.now().isoformat()
    }
    
    bookings.append(new_booking)
    save_bookings(bookings)
    
    return {
        "success": True,
        "message": f"Room {room['name']} booked successfully",
        "data": new_booking
    }

def cancel_booking(booking_id: str, user_id: str) -> Dict:
    """
    Cancel a room booking
    """
    bookings = load_bookings()
    
    for booking in bookings:
        if booking['booking_id'] == booking_id:
            # Check if user owns this booking
            if booking['user_id'] != user_id:
                return {
                    "success": False,
                    "message": "You can only cancel your own bookings"
                }
            
            if booking['status'] == 'cancelled':
                return {
                    "success": False,
                    "message": "Booking is already cancelled"
                }
            
            booking['status'] = 'cancelled'
            save_bookings(bookings)
            
            return {
                "success": True,
                "message": f"Booking {booking_id} cancelled successfully"
            }
    
    return {
        "success": False,
        "message": "Booking not found"
    }

def get_user_bookings(user_id: str) -> List[Dict]:
    """
    Get all bookings for a user
    """
    bookings = load_bookings()
    user_bookings = [b for b in bookings if b['user_id'] == user_id]
    user_bookings.sort(key=lambda x: (x['date'], x['start_time']), reverse=True)
    return user_bookings

def get_room_schedule(room_id: str, date: str) -> List[Dict]:
    """
    Get schedule for a specific room on a specific date
    """
    bookings = load_bookings()
    room_bookings = [
        b for b in bookings 
        if b['room_id'] == room_id and b['date'] == date and b['status'] == 'confirmed'
    ]
    room_bookings.sort(key=lambda x: x['start_time'])
    return room_bookings

