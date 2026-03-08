"""
Shuttle Booking Module
Handles shuttle route viewing and booking management
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

# Get the project root directory (3 levels up from this file)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
ROUTES_FILE = os.path.join(PROJECT_ROOT, 'data', 'mock_data', 'shuttle_routes.json')
BOOKINGS_FILE = os.path.join(PROJECT_ROOT, 'data', 'mock_data', 'shuttle_bookings.json')

def load_routes() -> List[Dict]:
    """Load shuttle routes from JSON file"""
    try:
        with open(ROUTES_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def load_bookings() -> List[Dict]:
    """Load shuttle bookings from JSON file"""
    try:
        with open(BOOKINGS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_bookings(bookings: List[Dict]):
    """Save shuttle bookings to JSON file"""
    with open(BOOKINGS_FILE, 'w') as f:
        json.dump(bookings, f, indent=4)

def view_routes() -> Dict:
    """Get all available shuttle routes"""
    routes = load_routes()
    
    return {
        "success": True,
        "data": routes
    }

def book_shuttle(
    user_id: str,
    route_id: str,
    date: str,
    departure_time: str,
    seats: int = 1
) -> Dict:
    """Book a shuttle"""
    routes = load_routes()
    bookings = load_bookings()
    
    # Find the route
    route = next((r for r in routes if r['route_id'] == route_id), None)
    if not route:
        return {"success": False, "message": "Route not found"}
    
    # Find the schedule slot
    schedule_slot = next((s for s in route['schedule'] if s['departure_time'] == departure_time), None)
    if not schedule_slot:
        return {"success": False, "message": "Invalid departure time"}
    
    # Check capacity
    existing_bookings = [
        b for b in bookings 
        if b['route_id'] == route_id 
        and b['date'] == date 
        and b['departure_time'] == departure_time
        and b['status'] == 'confirmed'
    ]
    
    total_booked_seats = sum(b['seats'] for b in existing_bookings)
    
    if total_booked_seats + seats > schedule_slot['capacity']:
        return {
            "success": False,
            "message": f"Not enough seats available. Only {schedule_slot['capacity'] - total_booked_seats} seats left"
        }
    
    # Create booking
    booking_id = f"SHT_{str(len(bookings) + 1).zfill(3)}"
    
    new_booking = {
        "booking_id": booking_id,
        "user_id": user_id,
        "route_id": route_id,
        "date": date,
        "departure_time": departure_time,
        "seats": seats,
        "status": "confirmed",
        "created_at": datetime.now().isoformat()
    }
    
    bookings.append(new_booking)
    save_bookings(bookings)
    
    return {
        "success": True,
        "message": "Shuttle booked successfully",
        "data": new_booking
    }

def cancel_shuttle_booking(booking_id: str, user_id: str) -> Dict:
    """Cancel a shuttle booking"""
    bookings = load_bookings()
    
    for booking in bookings:
        if booking['booking_id'] == booking_id:
            if booking['user_id'] != user_id:
                return {"success": False, "message": "Unauthorized to cancel this booking"}
            
            if booking['status'] == 'cancelled':
                return {"success": False, "message": "Booking already cancelled"}
            
            booking['status'] = 'cancelled'
            save_bookings(bookings)
            
            return {
                "success": True,
                "message": "Shuttle booking cancelled successfully",
                "data": booking
            }
    
    return {"success": False, "message": "Booking not found"}

def view_shuttle_bookings(user_id: str) -> Dict:
    """View user's shuttle bookings"""
    bookings = load_bookings()
    routes = load_routes()
    
    # Filter bookings for this user
    user_bookings = [b for b in bookings if b['user_id'] == user_id]
    
    # Enrich with route information
    for booking in user_bookings:
        route = next((r for r in routes if r['route_id'] == booking['route_id']), None)
        if route:
            booking['route_name'] = route['route_name']
            booking['departure_point'] = route['departure_point']
            booking['destination'] = route['destination']
    
    return {
        "success": True,
        "data": user_bookings
    }

