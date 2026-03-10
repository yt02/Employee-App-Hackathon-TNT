"""Visitor Management Module"""
import json
from typing import Dict, List, Optional
from datetime import date, datetime, time
from .db import get_db

def register_visitor(
    host_id: str,
    visitor_name: str,
    company: str,
    date: str,
    time: str,
    purpose: str = "",
    visitor_ic: str = "",
    visitor_email: str = "",
    to_date: str = "",
    looking_for: str = ""
) -> Dict:
    """
    Register a new visitor in the system.
    """
    if not visitor_name or not visitor_ic or not looking_for:
        return {
            "success": False,
            "message": "Missing required fields. Please provide visitor name, IC/Passport, and the person/department they are looking for."
        }

    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO visitors (
                host_id, visitor_name, visitor_ic, company, 
                date, time, purpose, visitor_email, looking_for, to_date, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            host_id, visitor_name, visitor_ic, company,
            date, time, purpose, visitor_email, looking_for, to_date or date, 'pre-registered'
        ))
        
        conn.commit()
    
    return {
        "success": True,
        "message": f"Visitor {visitor_name} has been pre-registered successfully for {date} at {time}.",
        "details": {
            "visitor_name": visitor_name,
            "date": date,
            "time": time,
            "host_id": host_id,
            "looking_for": looking_for
        }
    }

def get_user_visitors(user_id: str) -> List[Dict]:
    """Get all pre-registered visitors for a host"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM visitors WHERE host_id = ? ORDER BY created_at DESC", (user_id,))
        rows = cursor.fetchall()
        results = []
        for row in rows:
            item = dict(row)
            for key, value in item.items():
                if isinstance(value, (datetime, date, time)):
                    item[key] = value.isoformat()
            results.append(item)
        return results
