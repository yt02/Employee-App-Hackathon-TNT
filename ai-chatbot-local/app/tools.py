"""
Tool Definitions for Azure AI Agent Function Calling

This module defines all the callable tools that the Azure AI Agent can invoke.
The SDK parses function docstrings to auto-generate JSON schemas for the LLM.

Each function:
1. Wraps a module manager method
2. Has a detailed docstring with :param/:type annotations (SDK reads these)
3. Returns a JSON string (required by the SDK)
"""

import json
from azure.ai.projects.models import FunctionTool, ToolSet
from app.modules import leave_manager, room_manager, ticket_manager


# =====================================================
# LEAVE MANAGEMENT TOOLS
# =====================================================

def check_leave_balance(user_id: str) -> str:
    """
    Check the leave balance for an employee. Returns remaining annual leave,
    medical leave, and unpaid leave days for the current year.

    :param user_id: The employee ID, e.g. 'emp_001'
    :type user_id: str
    :return: JSON string with leave balance details
    :rtype: str
    """
    result = leave_manager.check_leave_balance(user_id)
    return json.dumps(result)


def apply_leave(user_id: str, leave_type: str, start_date: str, end_date: str, reason: str = "") -> str:
    """
    Apply for leave on behalf of an employee. Creates a leave request that
    will be pending approval. The leave balance must be sufficient.

    :param user_id: The employee ID, e.g. 'emp_001'
    :type user_id: str
    :param leave_type: Type of leave. Must be one of: 'annual_leave', 'medical_leave', 'unpaid_leave'
    :type leave_type: str
    :param start_date: Start date of leave in YYYY-MM-DD format, e.g. '2026-02-16'
    :type start_date: str
    :param end_date: End date of leave in YYYY-MM-DD format (inclusive), e.g. '2026-02-17'
    :type end_date: str
    :param reason: Reason for taking leave, e.g. 'Family vacation'
    :type reason: str
    :return: JSON string with success status, request ID, and confirmation message
    :rtype: str
    """
    result = leave_manager.apply_leave(user_id, leave_type, start_date, end_date, reason)
    return json.dumps(result)


# =====================================================
# MEETING ROOM TOOLS
# =====================================================

def list_available_rooms() -> str:
    """
    List all available meeting rooms with their capacity, location, and facilities.
    Use this when the user asks about meeting rooms or needs to see what rooms are available.

    :return: JSON string with list of all available meeting rooms
    :rtype: str
    """
    result = room_manager.list_available_rooms()
    return json.dumps(result)

def search_meeting_rooms(date: str, start_time: str, end_time: str, capacity: int = None, features: str = None) -> str:
    """
    Search for available meeting rooms based on their capacity, features, and availability on a specific date/time.
    Use this when the user asks for a room for a specific number of people (capacity) or with specific amenities (features).
    
    :param date: Date for the booking in YYYY-MM-DD format, e.g. '2026-02-14'
    :type date: str
    :param start_time: Start time in HH:MM format (24-hour), e.g. '14:00'
    :type start_time: str
    :param end_time: End time in HH:MM format (24-hour), e.g. '15:00'
    :type end_time: str
    :param capacity: Optional. Minimum capacity required, e.g., 4 for "find me a room for 4 people"
    :type capacity: int
    :param features: Optional. Required amenities separated by comma, e.g. "whiteboard,projector"
    :type features: str
    :return: JSON string with matching available meeting rooms
    :rtype: str
    """
    result = room_manager.search_meeting_rooms(date, start_time, end_time, capacity, features)
    return json.dumps(result)


def book_meeting_room(user_id: str, room_id: str, date: str, start_time: str, end_time: str, purpose: str = "") -> str:
    """
    Book a meeting room for a specific date and time. The room must be available
    at the requested time slot. Use list_available_rooms first if you need to
    find room IDs.

    :param user_id: The employee ID, e.g. 'emp_001'
    :type user_id: str
    :param room_id: The room ID to book, e.g. 'room_a', 'room_b', 'room_c'. You can also use the room name.
    :type room_id: str
    :param date: Date for the booking in YYYY-MM-DD format, e.g. '2026-02-14'
    :type date: str
    :param start_time: Start time in HH:MM format (24-hour), e.g. '14:00'
    :type start_time: str
    :param end_time: End time in HH:MM format (24-hour), e.g. '15:00'
    :type end_time: str
    :param purpose: Purpose of the meeting, e.g. 'Team standup'
    :type purpose: str
    :return: JSON string with booking confirmation including booking ID
    :rtype: str
    """
    result = room_manager.book_meeting_room(user_id, room_id, date, start_time, end_time, purpose)
    return json.dumps(result)


def check_room_bookings(user_id: str) -> str:
    """
    Check all active meeting room bookings for an employee. 
    Use this when the user asks "show my bookings", "what have I booked?", or similar.

    :param user_id: The employee ID, e.g. 'emp_001'
    :type user_id: str
    :return: JSON string with list of room bookings
    :rtype: str
    """
    result = room_manager.get_user_bookings(user_id)
    return json.dumps(result)


# =====================================================
# IT SUPPORT TICKET TOOLS
# =====================================================

def check_ticket_status(user_id: str) -> str:
    """
    Check the status of IT support tickets for an employee. Shows all
    open, in-progress, and recently resolved tickets.

    :param user_id: The employee ID (MUST be extracted from the '[Employee context: user_id=...]' block), e.g. 'emp_001'
    :type user_id: str
    :return: JSON string with list of tickets and their current status
    :rtype: str
    """
    result = ticket_manager.check_ticket_status(user_id)
    return json.dumps(result)


def create_ticket(user_id: str, category: str, subject: str, description: str, priority: str = "medium") -> str:
    """
    Create a new IT support ticket. The ticket will be assigned to the IT team
    for resolution.

    :param user_id: The employee ID, e.g. 'emp_001'
    :type user_id: str
    :param category: Ticket category. Must be one of: 'hardware', 'software', 'network', 'access', 'other'
    :type category: str
    :param subject: Brief subject line for the ticket, e.g. 'Laptop not charging'
    :type subject: str
    :param description: Detailed description of the issue
    :type description: str
    :param priority: Priority level. Must be one of: 'low', 'medium', 'high', 'urgent'. Default is 'medium'.
    :type priority: str
    :return: JSON string with ticket ID and confirmation
    :rtype: str
    """
    result = ticket_manager.create_ticket(user_id, category, subject, description, priority)
    return json.dumps(result)


# =====================================================
# VISITOR MANAGEMENT TOOLS
# =====================================================

def register_visitor(host_id: str, visitor_name: str, company: str, date: str, time: str, purpose: str = "", visitor_ic: str = "", visitor_email: str = "", to_date: str = "", looking_for: str = "") -> str:
    """
    Register a new guest or visitor to the office. This tool officially pre-registers 
    the guest for physical security access.

    :param host_id: The employee ID acting as the host (extract from context), e.g. 'emp_001'
    :type host_id: str
    :param visitor_name: REQUIRED. Full name of the visitor.
    :type visitor_name: str
    :param company: Name of the company the visitor represents.
    :type company: str
    :param date: REQUIRED. Arrival date in YYYY-MM-DD.
    :type date: str
    :param time: REQUIRED. Arrival time in HH:MM (24-hour format).
    :type time: str
    :param purpose: Reason for the visit.
    :type purpose: str
    :param visitor_ic: REQUIRED. IC or Passport number of the visitor.
    :type visitor_ic: str
    :param visitor_email: Contact email of the visitor.
    :type visitor_email: str
    :param to_date: End date of visit (optional, multi-day) in YYYY-MM-DD.
    :type to_date: str
    :param looking_for: REQUIRED. The specific person or department the visitor is visiting.
    :type looking_for: str
    :return: JSON string with confirmation details or error message
    :rtype: str
    """
    from app.modules import visitor_manager
    result = visitor_manager.register_visitor(
        host_id=host_id,
        visitor_name=visitor_name,
        company=company,
        date=date,
        time=time,
        purpose=purpose,
        visitor_ic=visitor_ic,
        visitor_email=visitor_email,
        to_date=to_date,
        looking_for=looking_for
    )
    return json.dumps(result)

def show_registered_visitors(user_id: str) -> str:
    """
    Retrieve a list of all visitors pre-registered by the employee.
    Use this when the user asks "show my visitors", "who is coming?", or "list my guests".

    :param user_id: The employee ID (extract from context), e.g. 'emp_001'
    :type user_id: str
    :return: JSON string with list of registered visitors
    :rtype: str
    """
    from app.modules import visitor_manager
    result = visitor_manager.get_user_visitors(user_id)
    return json.dumps(result)

# =====================================================
# SHUTTLE MANAGEMENT TOOLS
# =====================================================

def list_shuttle_routes() -> str:
    """
    List all available shuttle routes and schedules.
    
    :return: JSON string with route details
    :rtype: str
    """
    return json.dumps({
        "status": "success",
        "routes": [
            {"id": "SH001", "name": "North Route", "departure_time": "08:00", "stops": ["HQ", "Station A", "Office B"]},
            {"id": "SH002", "name": "East Route", "departure_time": "08:30", "stops": ["HQ", "Station C", "Office D"]}
        ]
    })

def book_shuttle(user_id: str, route_id: str, date: str, time: str) -> str:
    """
    Book a shuttle ride for a specific route and time.

    :param user_id: The employee ID, e.g. 'emp_001'
    :type user_id: str
    :param route_id: The ID of the shuttle route, e.g. 'SH001'
    :type route_id: str
    :param date: Date of booking in YYYY-MM-DD.
    :type date: str
    :param time: Time of departure in HH:MM format.
    :type time: str
    :return: JSON string with booking confirmation
    :rtype: str
    """
    return json.dumps({
        "status": "success",
        "message": f"Shuttle {route_id} booked successfully for {date} at {time}.",
        "booking_id": "SB" + date.replace("-", "") + "99"
    })

# =====================================================
# ORCHESTRATOR ROUTING TOOLS (Mock functions for Schema)
# =====================================================

def route_to_leave_agent(user_message: str) -> str:
    """
    Route the user's request to the Leave Management Agent.
    Use this when the user asks about leave balance, applying for leave, time off, vacations, sick days, PTO, or "MC".
    
    :param user_message: The exact original message from the user.
    :type user_message: str
    :return: JSON string confirming routing
    :rtype: str
    """
    return json.dumps({"status": "routed", "target": "leave_agent", "message": user_message})


def route_to_room_agent(user_message: str) -> str:
    """
    Route the user's request to the Meeting Room Agent.
    Use this when the user asks about meeting rooms, booking a room, or checking availability.
    
    :param user_message: The exact original message from the user.
    :type user_message: str
    :return: JSON string confirming routing
    :rtype: str
    """
    return json.dumps({"status": "routed", "target": "room_agent", "message": user_message})


def route_to_it_agent(user_message: str) -> str:
    """
    Route the user's request to the IT Support Agent.
    Use this when the user asks about technical issues, support tickets, broken hardware, or software bugs.
    
    :param user_message: The exact original message from the user.
    :type user_message: str
    :return: JSON string confirming routing
    :rtype: str
    """
    return json.dumps({"status": "routed", "target": "it_agent", "message": user_message})


def route_to_hr_agent(user_message: str) -> str:
    """
    Route the user's request to the HR Policy Agent.
    Use this when the user asks a factual question about company policy, employee handbook, benefits, or HR rules.
    
    :param user_message: The exact original message from the user.
    :type user_message: str
    :return: JSON string confirming routing
    :rtype: str
    """
    return json.dumps({"status": "routed", "target": "hr_agent", "message": user_message})


def route_to_visitor_agent(user_message: str) -> str:
    """
    Route the user's request to the Visitor Agent.
    Use this when the user wants to register a guest, manage an office visitor, or access physical security.
    
    :param user_message: The exact original message from the user.
    :type user_message: str
    :return: JSON string confirming routing
    :rtype: str
    """
    return json.dumps({"status": "routed", "target": "visitor_agent", "message": user_message})


def route_to_shuttle_agent(user_message: str) -> str:
    """
    Route the user's request to the Shuttle Agent.
    Use this when the user wants to check transport routes, book a shuttle ride, or manage commuting options.
    
    :param user_message: The exact original message from the user.
    :type user_message: str
    :return: JSON string confirming routing
    :rtype: str
    """
    return json.dumps({"status": "routed", "target": "shuttle_agent", "message": user_message})

orchestrator_functions = FunctionTool(functions=[
    route_to_leave_agent,
    route_to_room_agent,
    route_to_it_agent,
    route_to_hr_agent,
    route_to_visitor_agent,
    route_to_shuttle_agent
])
orchestrator_toolset = ToolSet()
orchestrator_toolset.add(orchestrator_functions)

# 2. Leave Agent ToolSet
leave_functions = FunctionTool(functions=[
    check_leave_balance,
    apply_leave
])
leave_toolset = ToolSet()
leave_toolset.add(leave_functions)

# 3. Room Agent ToolSet
room_functions = FunctionTool(functions=[
    list_available_rooms,
    search_meeting_rooms,
    book_meeting_room,
    check_room_bookings
])
room_toolset = ToolSet()
room_toolset.add(room_functions)

# 4. IT Agent ToolSet
it_functions = FunctionTool(functions=[
    check_ticket_status,
    create_ticket
])
it_toolset = ToolSet()
it_toolset.add(it_functions)

# 5. HR Agent ToolSet (Native RAG - Empty Toolset)
hr_toolset = ToolSet()

# 6. Visitor Agent ToolSet
visitor_functions = FunctionTool(functions=[
    register_visitor,
    show_registered_visitors
])
visitor_toolset = ToolSet()
visitor_toolset.add(visitor_functions)

# 7. Shuttle Agent ToolSet
shuttle_functions = FunctionTool(functions=[
    list_shuttle_routes,
    book_shuttle
])
shuttle_toolset = ToolSet()
shuttle_toolset.add(shuttle_functions)


# For backwards compatibility during transition, keep the old merged toolset available
user_functions = FunctionTool(
    functions=[
        check_leave_balance,
        apply_leave,
        list_available_rooms,
        search_meeting_rooms,
        book_meeting_room,
        check_room_bookings,
        check_ticket_status,
        create_ticket,
        register_visitor,
        show_registered_visitors,
        list_shuttle_routes,
        book_shuttle
    ]
)
toolset = ToolSet()
toolset.add(user_functions)
