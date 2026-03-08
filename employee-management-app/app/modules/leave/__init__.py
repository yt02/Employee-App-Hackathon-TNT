"""Leave Management Module - Leave Balance, Applications, and History"""
import json
import os
from typing import Optional, Dict, List
from datetime import datetime, timedelta

DATA_DIR = "data/mock_data"
LEAVE_BALANCES_FILE = os.path.join(DATA_DIR, "leave_balances.json")
LEAVE_REQUESTS_FILE = os.path.join(DATA_DIR, "leave_requests.json")

def load_leave_balances() -> List[Dict]:
    """Load leave balances from JSON file"""
    with open(LEAVE_BALANCES_FILE, 'r') as f:
        return json.load(f)

def save_leave_balances(balances: List[Dict]):
    """Save leave balances to JSON file"""
    with open(LEAVE_BALANCES_FILE, 'w') as f:
        json.dump(balances, f, indent=2)

def load_leave_requests() -> List[Dict]:
    """Load leave requests from JSON file"""
    with open(LEAVE_REQUESTS_FILE, 'r') as f:
        return json.load(f)

def save_leave_requests(requests: List[Dict]):
    """Save leave requests to JSON file"""
    with open(LEAVE_REQUESTS_FILE, 'w') as f:
        json.dump(requests, f, indent=2)

def get_leave_balance(user_id: str, year: int = 2026) -> Optional[Dict]:
    """
    Get leave balance for a user
    """
    balances = load_leave_balances()
    
    for balance in balances:
        if balance['user_id'] == user_id and balance['year'] == year:
            return balance
    
    return None

def calculate_days(start_date: str, end_date: str) -> int:
    """
    Calculate number of days between two dates (inclusive)
    """
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    return (end - start).days + 1

def apply_leave(user_id: str, leave_type: str, start_date: str, end_date: str, reason: str) -> Dict:
    """
    Apply for leave
    Returns success status and message
    """
    # Validate leave type
    valid_types = ["annual_leave", "medical_leave", "unpaid_leave"]
    if leave_type not in valid_types:
        return {
            "success": False,
            "message": f"Invalid leave type. Must be one of: {', '.join(valid_types)}"
        }
    
    # Calculate days
    days = calculate_days(start_date, end_date)
    
    # Check balance
    balance = get_leave_balance(user_id)
    if not balance:
        return {
            "success": False,
            "message": "Leave balance not found for user"
        }
    
    if balance[leave_type]['remaining'] < days:
        return {
            "success": False,
            "message": f"Insufficient {leave_type.replace('_', ' ')} balance. You have {balance[leave_type]['remaining']} days remaining."
        }
    
    # Create leave request
    requests = load_leave_requests()
    request_id = f"LR{str(len(requests) + 1).zfill(3)}"
    
    new_request = {
        "request_id": request_id,
        "user_id": user_id,
        "leave_type": leave_type,
        "start_date": start_date,
        "end_date": end_date,
        "days": days,
        "reason": reason,
        "status": "pending",
        "applied_date": datetime.now().strftime("%Y-%m-%d"),
        "approved_by": None,
        "approved_date": None
    }
    
    requests.append(new_request)
    save_leave_requests(requests)
    
    # Update balance (deduct from remaining)
    balances = load_leave_balances()
    for bal in balances:
        if bal['user_id'] == user_id and bal['year'] == 2026:
            bal[leave_type]['used'] += days
            bal[leave_type]['remaining'] -= days
            break
    save_leave_balances(balances)
    
    return {
        "success": True,
        "message": f"Leave request {request_id} submitted successfully",
        "data": new_request
    }

def view_history(user_id: str) -> List[Dict]:
    """
    View leave history for a user
    """
    requests = load_leave_requests()
    user_requests = [req for req in requests if req['user_id'] == user_id]
    
    # Sort by applied date (most recent first)
    user_requests.sort(key=lambda x: x['applied_date'], reverse=True)
    
    return user_requests

def get_all_leave_requests() -> List[Dict]:
    """
    Get all leave requests (for managers/HR)
    """
    requests = load_leave_requests()
    requests.sort(key=lambda x: x['applied_date'], reverse=True)
    return requests

def approve_leave(request_id: str, approver_id: str) -> Dict:
    """
    Approve a leave request
    """
    requests = load_leave_requests()
    
    for req in requests:
        if req['request_id'] == request_id:
            if req['status'] != 'pending':
                return {
                    "success": False,
                    "message": f"Leave request is already {req['status']}"
                }
            
            req['status'] = 'approved'
            req['approved_by'] = approver_id
            req['approved_date'] = datetime.now().strftime("%Y-%m-%d")
            save_leave_requests(requests)
            
            return {
                "success": True,
                "message": f"Leave request {request_id} approved",
                "data": req
            }
    
    return {
        "success": False,
        "message": "Leave request not found"
    }

