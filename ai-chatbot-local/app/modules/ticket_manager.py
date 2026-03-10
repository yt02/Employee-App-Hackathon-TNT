"""IT Support Ticket Management Module"""
import json
import os
from typing import Dict, List
from datetime import datetime
import uuid
from .db import get_db

def create_ticket(user_id: str, category: str, subject: str, description: str, priority: str = "medium") -> Dict:
    """
    Create an IT support ticket
    Returns: {"success": bool, "message": str, "ticket_id": str}
    """
    # Validate category
    valid_categories = ["hardware", "software", "network", "access", "other"]
    if category.lower() not in valid_categories:
        category = "other"
    
    # Validate priority
    valid_priorities = ["low", "medium", "high", "urgent"]
    if priority.lower() not in valid_priorities:
        priority = "medium"
    
    # Create ticket
    ticket_id = f"TKT{str(uuid.uuid4())[:8].upper()}"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tickets (
                ticket_id, user_id, category, subject, description, priority, 
                status, created_at, updated_at, assigned_to, resolved_at
            ) VALUES (?, ?, ?, ?, ?, ?, 'open', ?, ?, NULL, NULL)
        """, (ticket_id, user_id, category.lower(), subject, description, priority.lower(), now, now))
        
        conn.commit()
    
    return {
        "success": True,
        "message": f"IT support ticket created successfully! Ticket ID: {ticket_id}. Your {priority} priority {category} issue has been submitted. Our IT team will respond shortly.",
        "ticket_id": ticket_id
    }

def get_user_tickets(user_id: str) -> List[Dict]:
    """Get all tickets for a user"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tickets WHERE user_id = ?", (user_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def check_ticket_status(user_id: str, ticket_id: str = None) -> Dict:
    """
    Check status of user's tickets
    Returns: {"success": bool, "message": str, "tickets": list}
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        if ticket_id:
            cursor.execute("SELECT * FROM tickets WHERE user_id = ? AND ticket_id = ?", (user_id, ticket_id))
            ticket_row = cursor.fetchone()
            
            if not ticket_row:
                return {
                    "success": False,
                    "message": f"Ticket {ticket_id} not found"
                }
            
            ticket = dict(ticket_row)
            
            # Pre-format as ticket-list block to force UI rendering
            json_str = json.dumps([ticket], indent=2)
            message = f"Here is the status for your ticket:\n\n```ticket-list\n{json_str}\n```\n"

            return {
                "success": True,
                "message": message,
                "tickets": [ticket]
            }
        
        # List all tickets
        cursor.execute("SELECT * FROM tickets WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
        rows = cursor.fetchall()
        tickets = [dict(row) for row in rows]
        
    if not tickets:
        return {
            "success": False,
            "message": "You have no open support tickets."
        }
        
    recent_tickets = tickets[:5]
    json_str = json.dumps(recent_tickets, indent=2)
    message = f"You have {len(tickets)} support ticket(s). Here are your most recent ones:\n\n```ticket-list\n{json_str}\n```\n"
    
    return {
        "success": True,
        "message": message,
        "tickets": tickets
    }

