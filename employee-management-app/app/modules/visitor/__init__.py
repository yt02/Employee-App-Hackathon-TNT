"""
Visitor Registration Module
Handles visitor registration, check-in, check-out, and tracking
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

# Get the project root directory (3 levels up from this file)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
DATA_FILE = os.path.join(PROJECT_ROOT, 'data', 'mock_data', 'visitors.json')

def load_visitors() -> List[Dict]:
    """Load visitors from JSON file"""
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_visitors(visitors: List[Dict]):
    """Save visitors to JSON file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(visitors, f, indent=4)

def register_visitor(
    name: str,
    company: str,
    email: str,
    phone: str,
    purpose: str,
    host_employee_id: str,
    visit_date: str,
    expected_arrival: str,
    expected_departure: str,
    notes: str = ""
) -> Dict:
    """Register a new visitor"""
    visitors = load_visitors()
    
    # Generate visitor ID
    visitor_id = f"VIS_{str(len(visitors) + 1).zfill(3)}"
    
    new_visitor = {
        "visitor_id": visitor_id,
        "name": name,
        "company": company,
        "email": email,
        "phone": phone,
        "purpose": purpose,
        "host_employee_id": host_employee_id,
        "visit_date": visit_date,
        "expected_arrival": expected_arrival,
        "expected_departure": expected_departure,
        "actual_check_in": None,
        "actual_check_out": None,
        "status": "scheduled",
        "badge_number": None,
        "created_at": datetime.now().isoformat(),
        "notes": notes
    }
    
    visitors.append(new_visitor)
    save_visitors(visitors)
    
    return {
        "success": True,
        "message": f"Visitor {name} registered successfully",
        "data": new_visitor
    }

def check_in_visitor(visitor_id: str) -> Dict:
    """Check in a visitor"""
    visitors = load_visitors()
    
    for visitor in visitors:
        if visitor['visitor_id'] == visitor_id:
            if visitor['status'] == 'checked_in':
                return {"success": False, "message": "Visitor already checked in"}
            
            if visitor['status'] == 'checked_out':
                return {"success": False, "message": "Visitor already checked out"}
            
            # Generate badge number
            badge_number = f"BADGE_{str(len([v for v in visitors if v.get('badge_number')]) + 100)}"
            
            visitor['actual_check_in'] = datetime.now().strftime("%H:%M:%S")
            visitor['status'] = 'checked_in'
            visitor['badge_number'] = badge_number
            
            save_visitors(visitors)
            
            return {
                "success": True,
                "message": f"Visitor checked in. Badge: {badge_number}",
                "data": visitor
            }
    
    return {"success": False, "message": "Visitor not found"}

def check_out_visitor(visitor_id: str) -> Dict:
    """Check out a visitor"""
    visitors = load_visitors()
    
    for visitor in visitors:
        if visitor['visitor_id'] == visitor_id:
            if visitor['status'] != 'checked_in':
                return {"success": False, "message": "Visitor not checked in"}
            
            visitor['actual_check_out'] = datetime.now().strftime("%H:%M:%S")
            visitor['status'] = 'checked_out'
            
            save_visitors(visitors)
            
            return {
                "success": True,
                "message": "Visitor checked out successfully",
                "data": visitor
            }
    
    return {"success": False, "message": "Visitor not found"}

def view_visitors(
    host_employee_id: Optional[str] = None,
    visit_date: Optional[str] = None,
    status: Optional[str] = None
) -> Dict:
    """View visitors with optional filters"""
    visitors = load_visitors()
    
    # Apply filters
    if host_employee_id:
        visitors = [v for v in visitors if v['host_employee_id'] == host_employee_id]
    
    if visit_date:
        visitors = [v for v in visitors if v['visit_date'] == visit_date]
    
    if status:
        visitors = [v for v in visitors if v['status'] == status]
    
    return {
        "success": True,
        "data": visitors
    }

