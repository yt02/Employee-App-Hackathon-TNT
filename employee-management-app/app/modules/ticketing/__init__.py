"""
Ticketing Module - IT support, facilities, and general request tickets
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import uuid

# Path to tickets data
DATA_DIR = os.path.join(os.path.dirname(__file__), '../../../data/mock_data')
TICKETS_FILE = os.path.join(DATA_DIR, 'tickets.json')


def load_tickets() -> List[Dict]:
    """Load tickets from JSON file"""
    try:
        with open(TICKETS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_tickets(tickets: List[Dict]):
    """Save tickets to JSON file"""
    with open(TICKETS_FILE, 'w') as f:
        json.dump(tickets, f, indent=4)


def create_ticket(
    title: str,
    description: str,
    category: str,
    priority: str,
    created_by: str
) -> Dict:
    """
    Create a new support ticket
    
    Args:
        title: Ticket title
        description: Detailed description
        category: Category (IT Support, Hardware Request, Facilities, etc.)
        priority: Priority level (low, medium, high, urgent)
        created_by: User ID of ticket creator
    
    Returns:
        Result dictionary with success status and ticket data
    """
    tickets = load_tickets()
    
    # Generate ticket ID
    ticket_id = f"TKT_{str(uuid.uuid4())[:8].upper()}"
    
    # Create ticket object
    new_ticket = {
        "ticket_id": ticket_id,
        "title": title,
        "description": description,
        "category": category,
        "priority": priority,
        "status": "pending",
        "created_by": created_by,
        "assigned_to": None,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "resolved_at": None,
        "comments": []
    }
    
    tickets.append(new_ticket)
    save_tickets(tickets)
    
    return {
        "success": True,
        "message": "Ticket created successfully",
        "data": new_ticket
    }


def view_tickets(user_id: str, filter_type: str = "my_tickets") -> List[Dict]:
    """
    View tickets based on filter
    
    Args:
        user_id: User ID
        filter_type: Filter type (my_tickets, assigned_to_me, all)
    
    Returns:
        List of tickets
    """
    tickets = load_tickets()
    
    if filter_type == "my_tickets":
        # Tickets created by the user
        return [t for t in tickets if t['created_by'] == user_id]
    elif filter_type == "assigned_to_me":
        # Tickets assigned to the user
        return [t for t in tickets if t['assigned_to'] == user_id]
    elif filter_type == "all":
        # All tickets (for admins/managers)
        return tickets
    else:
        return []


def update_ticket_status(ticket_id: str, status: str, user_id: str) -> Dict:
    """
    Update ticket status
    
    Args:
        ticket_id: Ticket ID
        status: New status (pending, in_progress, resolved, closed)
        user_id: User ID making the update
    
    Returns:
        Result dictionary with success status
    """
    tickets = load_tickets()
    
    for ticket in tickets:
        if ticket['ticket_id'] == ticket_id:
            ticket['status'] = status
            ticket['updated_at'] = datetime.now().isoformat()
            
            if status == "resolved":
                ticket['resolved_at'] = datetime.now().isoformat()
            
            save_tickets(tickets)
            
            return {
                "success": True,
                "message": f"Ticket status updated to {status}",
                "data": ticket
            }
    
    return {
        "success": False,
        "message": "Ticket not found"
    }


def assign_ticket(ticket_id: str, assigned_to: str, assigner_id: str) -> Dict:
    """
    Assign ticket to a user
    
    Args:
        ticket_id: Ticket ID
        assigned_to: User ID to assign ticket to
        assigner_id: User ID making the assignment
    
    Returns:
        Result dictionary with success status
    """
    tickets = load_tickets()
    
    for ticket in tickets:
        if ticket['ticket_id'] == ticket_id:
            ticket['assigned_to'] = assigned_to
            ticket['status'] = "in_progress"
            ticket['updated_at'] = datetime.now().isoformat()
            
            save_tickets(tickets)
            
            return {
                "success": True,
                "message": "Ticket assigned successfully",
                "data": ticket
            }
    
    return {
        "success": False,
        "message": "Ticket not found"
    }


def add_comment(ticket_id: str, user_id: str, comment: str) -> Dict:
    """
    Add a comment to a ticket
    
    Args:
        ticket_id: Ticket ID
        user_id: User ID adding the comment
        comment: Comment text
    
    Returns:
        Result dictionary with success status
    """
    tickets = load_tickets()
    
    for ticket in tickets:
        if ticket['ticket_id'] == ticket_id:
            comment_id = f"CMT_{str(uuid.uuid4())[:8].upper()}"
            
            new_comment = {
                "comment_id": comment_id,
                "user_id": user_id,
                "comment": comment,
                "created_at": datetime.now().isoformat()
            }
            
            ticket['comments'].append(new_comment)
            ticket['updated_at'] = datetime.now().isoformat()
            
            save_tickets(tickets)
            
            return {
                "success": True,
                "message": "Comment added successfully",
                "data": new_comment
            }
    
    return {
        "success": False,
        "message": "Ticket not found"
    }

