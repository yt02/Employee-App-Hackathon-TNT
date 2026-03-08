"""
Calendar Module - Manage events, meetings, deadlines, and tasks
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import uuid

# Path to calendar events data
DATA_DIR = os.path.join(os.path.dirname(__file__), '../../../data/mock_data')
EVENTS_FILE = os.path.join(DATA_DIR, 'calendar_events.json')


def load_events() -> List[Dict]:
    """Load calendar events from JSON file"""
    try:
        with open(EVENTS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_events(events: List[Dict]):
    """Save calendar events to JSON file"""
    with open(EVENTS_FILE, 'w') as f:
        json.dump(events, f, indent=4)


def view_events(user_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict]:
    """
    View calendar events for a user
    
    Args:
        user_id: User ID
        start_date: Optional start date filter (YYYY-MM-DD)
        end_date: Optional end date filter (YYYY-MM-DD)
    
    Returns:
        List of events where user is organizer or attendee
    """
    events = load_events()
    user_events = []
    
    for event in events:
        # Check if user is organizer or attendee
        if event['organizer_id'] == user_id or user_id in event['attendees']:
            # Apply date filters if provided
            if start_date or end_date:
                event_date = event['start_datetime'].split('T')[0]
                
                if start_date and event_date < start_date:
                    continue
                if end_date and event_date > end_date:
                    continue
            
            user_events.append(event)
    
    # Sort by start datetime
    user_events.sort(key=lambda x: x['start_datetime'])
    
    return user_events


def create_event(
    title: str,
    description: str,
    start_datetime: str,
    end_datetime: str,
    organizer_id: str,
    location: str = "",
    attendees: List[str] = None,
    event_type: str = "meeting"
) -> Dict:
    """
    Create a new calendar event
    
    Args:
        title: Event title
        description: Event description
        start_datetime: Start datetime (ISO format)
        end_datetime: End datetime (ISO format)
        organizer_id: User ID of organizer
        location: Event location
        attendees: List of attendee user IDs
        event_type: Type of event (meeting, deadline, task)
    
    Returns:
        Result dictionary with success status and event data
    """
    events = load_events()
    
    # Generate event ID
    event_id = f"EVT_{str(uuid.uuid4())[:8].upper()}"
    
    # Create event object
    new_event = {
        "event_id": event_id,
        "title": title,
        "description": description,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "location": location,
        "organizer_id": organizer_id,
        "attendees": attendees or [organizer_id],
        "event_type": event_type,
        "status": "confirmed",
        "created_at": datetime.now().isoformat()
    }
    
    events.append(new_event)
    save_events(events)
    
    return {
        "success": True,
        "message": "Event created successfully",
        "data": new_event
    }


def update_event(event_id: str, user_id: str, updates: Dict) -> Dict:
    """
    Update an existing event
    
    Args:
        event_id: Event ID to update
        user_id: User ID making the update (must be organizer)
        updates: Dictionary of fields to update
    
    Returns:
        Result dictionary with success status
    """
    events = load_events()
    
    for event in events:
        if event['event_id'] == event_id:
            # Check if user is the organizer
            if event['organizer_id'] != user_id:
                return {
                    "success": False,
                    "message": "Only the organizer can update this event"
                }
            
            # Update allowed fields
            allowed_fields = ['title', 'description', 'start_datetime', 'end_datetime', 
                            'location', 'attendees', 'event_type', 'status']
            
            for field, value in updates.items():
                if field in allowed_fields:
                    event[field] = value
            
            save_events(events)
            
            return {
                "success": True,
                "message": "Event updated successfully",
                "data": event
            }
    
    return {
        "success": False,
        "message": "Event not found"
    }


def delete_event(event_id: str, user_id: str) -> Dict:
    """
    Delete an event
    
    Args:
        event_id: Event ID to delete
        user_id: User ID making the deletion (must be organizer)
    
    Returns:
        Result dictionary with success status
    """
    events = load_events()
    
    for i, event in enumerate(events):
        if event['event_id'] == event_id:
            # Check if user is the organizer
            if event['organizer_id'] != user_id:
                return {
                    "success": False,
                    "message": "Only the organizer can delete this event"
                }
            
            events.pop(i)
            save_events(events)
            
            return {
                "success": True,
                "message": "Event deleted successfully"
            }
    
    return {
        "success": False,
        "message": "Event not found"
    }

