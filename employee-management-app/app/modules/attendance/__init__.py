"""
Attendance Module - Clock in/out and attendance tracking
"""
import json
import os
from datetime import datetime, date
from typing import List, Dict, Optional
import uuid

# Path to attendance data
DATA_DIR = os.path.join(os.path.dirname(__file__), '../../../data/mock_data')
ATTENDANCE_FILE = os.path.join(DATA_DIR, 'attendance_records.json')


def load_attendance() -> List[Dict]:
    """Load attendance records from JSON file"""
    try:
        with open(ATTENDANCE_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_attendance(records: List[Dict]):
    """Save attendance records to JSON file"""
    with open(ATTENDANCE_FILE, 'w') as f:
        json.dump(records, f, indent=4)


def clock_in(user_id: str) -> Dict:
    """
    Clock in for the day
    
    Args:
        user_id: User ID
    
    Returns:
        Result dictionary with success status
    """
    records = load_attendance()
    today = date.today().isoformat()
    current_time = datetime.now().strftime("%H:%M:%S")
    
    # Check if already clocked in today
    for record in records:
        if record['user_id'] == user_id and record['date'] == today:
            if record['clock_in']:
                return {
                    "success": False,
                    "message": f"Already clocked in at {record['clock_in']}"
                }
    
    # Create new attendance record
    record_id = f"ATT_{str(uuid.uuid4())[:8].upper()}"
    
    new_record = {
        "record_id": record_id,
        "user_id": user_id,
        "date": today,
        "clock_in": current_time,
        "clock_out": None,
        "total_hours": 0,
        "status": "present",
        "notes": ""
    }
    
    records.append(new_record)
    save_attendance(records)
    
    return {
        "success": True,
        "message": f"Clocked in at {current_time}",
        "data": new_record
    }


def clock_out(user_id: str) -> Dict:
    """
    Clock out for the day
    
    Args:
        user_id: User ID
    
    Returns:
        Result dictionary with success status
    """
    records = load_attendance()
    today = date.today().isoformat()
    current_time = datetime.now().strftime("%H:%M:%S")
    
    # Find today's record
    for record in records:
        if record['user_id'] == user_id and record['date'] == today:
            if not record['clock_in']:
                return {
                    "success": False,
                    "message": "No clock-in record found for today"
                }
            
            if record['clock_out']:
                return {
                    "success": False,
                    "message": f"Already clocked out at {record['clock_out']}"
                }
            
            # Calculate total hours
            clock_in_time = datetime.strptime(record['clock_in'], "%H:%M:%S")
            clock_out_time = datetime.strptime(current_time, "%H:%M:%S")
            duration = clock_out_time - clock_in_time
            total_hours = round(duration.total_seconds() / 3600, 2)
            
            record['clock_out'] = current_time
            record['total_hours'] = total_hours
            
            save_attendance(records)
            
            return {
                "success": True,
                "message": f"Clocked out at {current_time}. Total hours: {total_hours}",
                "data": record
            }
    
    return {
        "success": False,
        "message": "No clock-in record found for today. Please clock in first."
    }


def view_attendance(user_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict]:
    """
    View attendance records for a user
    
    Args:
        user_id: User ID
        start_date: Optional start date filter (YYYY-MM-DD)
        end_date: Optional end date filter (YYYY-MM-DD)
    
    Returns:
        List of attendance records
    """
    records = load_attendance()
    user_records = []
    
    for record in records:
        if record['user_id'] == user_id:
            # Apply date filters if provided
            if start_date and record['date'] < start_date:
                continue
            if end_date and record['date'] > end_date:
                continue
            
            user_records.append(record)
    
    # Sort by date (newest first)
    user_records.sort(key=lambda x: x['date'], reverse=True)
    
    return user_records


def get_attendance_summary(user_id: str, month: Optional[int] = None, year: Optional[int] = None) -> Dict:
    """
    Get attendance summary for a user
    
    Args:
        user_id: User ID
        month: Optional month filter (1-12)
        year: Optional year filter
    
    Returns:
        Summary dictionary with statistics
    """
    records = load_attendance()
    
    # Use current month/year if not provided
    if not month:
        month = datetime.now().month
    if not year:
        year = datetime.now().year
    
    # Filter records for the specified month/year
    month_records = []
    for record in records:
        if record['user_id'] == user_id:
            record_date = datetime.fromisoformat(record['date'])
            if record_date.month == month and record_date.year == year:
                month_records.append(record)
    
    # Calculate statistics
    total_days = len(month_records)
    present_days = len([r for r in month_records if r['status'] == 'present'])
    on_leave_days = len([r for r in month_records if r['status'] == 'on_leave'])
    total_hours = sum(r['total_hours'] for r in month_records)
    avg_hours = round(total_hours / present_days, 2) if present_days > 0 else 0
    
    return {
        "user_id": user_id,
        "month": month,
        "year": year,
        "total_days": total_days,
        "present_days": present_days,
        "on_leave_days": on_leave_days,
        "total_hours": round(total_hours, 2),
        "average_hours_per_day": avg_hours
    }

