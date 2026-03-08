"""FastAPI Backend for Employee Management App"""
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os

# Import modules
from app.modules.user_management import authenticate_user, get_user_info, get_user_permissions, has_permission
from app.modules.leave import get_leave_balance, apply_leave, view_history, get_all_leave_requests, approve_leave
from app.modules.meeting_rooms import list_rooms, check_availability, book_room, cancel_booking, get_user_bookings, get_room_schedule
from app.modules.calendar import view_events, create_event, update_event, delete_event
from app.modules.ticketing import create_ticket, view_tickets, update_ticket_status, assign_ticket, add_comment
from app.modules.attendance import clock_in, clock_out, view_attendance, get_attendance_summary
from app.modules.visitor import register_visitor, check_in_visitor, check_out_visitor, view_visitors
from app.modules.shuttle import view_routes, book_shuttle, cancel_shuttle_booking, view_shuttle_bookings
from app.modules.training import view_courses, enroll_course, view_enrollments, complete_course
from app.modules.wellness import view_activities, join_activity, log_wellness, view_wellness_stats

app = FastAPI(title="Employee Management System")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_path = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

# Pydantic models for request/response
class LoginRequest(BaseModel):
    username: str
    password: str

class LeaveRequest(BaseModel):
    leave_type: str
    start_date: str
    end_date: str
    reason: str

class RoomBookingRequest(BaseModel):
    room_id: str
    date: str
    start_time: str
    end_time: str
    purpose: str

class AvailabilityRequest(BaseModel):
    room_id: str
    date: str
    start_time: str
    end_time: str

class EventRequest(BaseModel):
    title: str
    description: str
    start_datetime: str
    end_datetime: str
    location: str = ""
    attendees: list = []
    event_type: str = "meeting"

class EventUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_datetime: Optional[str] = None
    end_datetime: Optional[str] = None
    location: Optional[str] = None
    attendees: Optional[list] = None
    event_type: Optional[str] = None
    status: Optional[str] = None

class TicketRequest(BaseModel):
    title: str
    description: str
    category: str
    priority: str

class TicketStatusRequest(BaseModel):
    status: str

class TicketAssignRequest(BaseModel):
    assigned_to: str

class CommentRequest(BaseModel):
    comment: str

# Phase 3 Pydantic models
class VisitorRequest(BaseModel):
    name: str
    company: str
    email: str
    phone: str
    purpose: str
    host_employee_id: str
    visit_date: str
    expected_arrival: str
    expected_departure: str
    notes: str = ""

class ShuttleBookingRequest(BaseModel):
    route_id: str
    date: str
    departure_time: str
    seats: int = 1

class TrainingEnrollmentRequest(BaseModel):
    course_id: str
    session_id: str

class WellnessLogRequest(BaseModel):
    activity_type: str
    value: float
    unit: str
    date: Optional[str] = None
    notes: str = ""

# Root endpoint - serve the UI
@app.get("/")
async def read_root():
    """Serve the employee management UI"""
    return FileResponse(os.path.join(static_path, "index.html"))

# Authentication endpoints
@app.post("/api/auth/login")
async def login(request: LoginRequest):
    """Authenticate user"""
    user = authenticate_user(request.username, request.password)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Get user permissions
    permissions = get_user_permissions(user['user_id'])
    
    return {
        "success": True,
        "message": "Login successful",
        "data": {
            "user": user,
            "permissions": permissions
        }
    }

@app.get("/api/user/{user_id}")
async def get_user(user_id: str):
    """Get user information"""
    user = get_user_info(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "success": True,
        "data": user
    }

# Leave management endpoints
@app.get("/api/leave/balance/{user_id}")
async def get_balance(user_id: str):
    """Get leave balance for user"""
    balance = get_leave_balance(user_id)
    
    if not balance:
        raise HTTPException(status_code=404, detail="Leave balance not found")
    
    return {
        "success": True,
        "data": balance
    }

@app.post("/api/leave/apply/{user_id}")
async def submit_leave(user_id: str, request: LeaveRequest):
    """Apply for leave"""
    result = apply_leave(
        user_id=user_id,
        leave_type=request.leave_type,
        start_date=request.start_date,
        end_date=request.end_date,
        reason=request.reason
    )
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['message'])
    
    return result

@app.get("/api/leave/history/{user_id}")
async def get_history(user_id: str):
    """Get leave history for user"""
    history = view_history(user_id)
    
    return {
        "success": True,
        "data": history
    }

@app.get("/api/leave/all")
async def get_all_leaves():
    """Get all leave requests (for managers)"""
    requests = get_all_leave_requests()
    
    return {
        "success": True,
        "data": requests
    }

@app.post("/api/leave/approve/{request_id}/{approver_id}")
async def approve_leave_request(request_id: str, approver_id: str):
    """Approve a leave request"""
    result = approve_leave(request_id, approver_id)
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['message'])
    
    return result

# Meeting room endpoints
@app.get("/api/rooms/list")
async def get_rooms():
    """Get list of all meeting rooms"""
    rooms = list_rooms()

    return {
        "success": True,
        "data": rooms
    }

@app.post("/api/rooms/check-availability")
async def check_room_availability(request: AvailabilityRequest):
    """Check if a room is available"""
    result = check_availability(
        room_id=request.room_id,
        date=request.date,
        start_time=request.start_time,
        end_time=request.end_time
    )

    return {
        "success": result['available'],
        "message": result['message'],
        "data": result.get('conflicts', [])
    }

@app.post("/api/rooms/book/{user_id}")
async def create_booking(user_id: str, request: RoomBookingRequest):
    """Book a meeting room"""
    result = book_room(
        user_id=user_id,
        room_id=request.room_id,
        date=request.date,
        start_time=request.start_time,
        end_time=request.end_time,
        purpose=request.purpose
    )

    if not result['success']:
        raise HTTPException(status_code=400, detail=result['message'])

    return result

@app.delete("/api/rooms/cancel/{booking_id}/{user_id}")
async def cancel_room_booking(booking_id: str, user_id: str):
    """Cancel a room booking"""
    result = cancel_booking(booking_id, user_id)

    if not result['success']:
        raise HTTPException(status_code=400, detail=result['message'])

    return result

@app.get("/api/rooms/bookings/{user_id}")
async def get_bookings(user_id: str):
    """Get all bookings for a user"""
    bookings = get_user_bookings(user_id)

    return {
        "success": True,
        "data": bookings
    }

@app.get("/api/rooms/schedule/{room_id}/{date}")
async def get_schedule(room_id: str, date: str):
    """Get schedule for a room on a specific date"""
    schedule = get_room_schedule(room_id, date)

    return {
        "success": True,
        "data": schedule
    }


# ============================================
# PHASE 2: CALENDAR, TICKETING, ATTENDANCE
# ============================================

# Calendar endpoints
@app.get("/api/calendar/events/{user_id}")
async def get_events(user_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None):
    """Get calendar events for a user"""
    events = view_events(user_id, start_date, end_date)

    return {
        "success": True,
        "data": events
    }

@app.post("/api/calendar/events/{user_id}")
async def add_event(user_id: str, request: EventRequest):
    """Create a new calendar event"""
    result = create_event(
        title=request.title,
        description=request.description,
        start_datetime=request.start_datetime,
        end_datetime=request.end_datetime,
        organizer_id=user_id,
        location=request.location,
        attendees=request.attendees,
        event_type=request.event_type
    )

    return result

@app.put("/api/calendar/events/{event_id}/{user_id}")
async def modify_event(event_id: str, user_id: str, request: EventUpdateRequest):
    """Update an existing event"""
    updates = {k: v for k, v in request.dict().items() if v is not None}
    result = update_event(event_id, user_id, updates)

    if not result['success']:
        raise HTTPException(status_code=400, detail=result['message'])

    return result

@app.delete("/api/calendar/events/{event_id}/{user_id}")
async def remove_event(event_id: str, user_id: str):
    """Delete an event"""
    result = delete_event(event_id, user_id)

    if not result['success']:
        raise HTTPException(status_code=400, detail=result['message'])

    return result

# Ticketing endpoints
@app.post("/api/tickets/create/{user_id}")
async def submit_ticket(user_id: str, request: TicketRequest):
    """Create a new support ticket"""
    result = create_ticket(
        title=request.title,
        description=request.description,
        category=request.category,
        priority=request.priority,
        created_by=user_id
    )

    return result

@app.get("/api/tickets/{user_id}")
async def get_tickets(user_id: str, filter_type: str = "my_tickets"):
    """Get tickets based on filter"""
    tickets = view_tickets(user_id, filter_type)

    return {
        "success": True,
        "data": tickets
    }

@app.put("/api/tickets/{ticket_id}/status/{user_id}")
async def change_ticket_status(ticket_id: str, user_id: str, request: TicketStatusRequest):
    """Update ticket status"""
    result = update_ticket_status(ticket_id, request.status, user_id)

    if not result['success']:
        raise HTTPException(status_code=400, detail=result['message'])

    return result

@app.put("/api/tickets/{ticket_id}/assign/{user_id}")
async def assign_ticket_to_user(ticket_id: str, user_id: str, request: TicketAssignRequest):
    """Assign ticket to a user"""
    result = assign_ticket(ticket_id, request.assigned_to, user_id)

    if not result['success']:
        raise HTTPException(status_code=400, detail=result['message'])

    return result

@app.post("/api/tickets/{ticket_id}/comment/{user_id}")
async def add_ticket_comment(ticket_id: str, user_id: str, request: CommentRequest):
    """Add a comment to a ticket"""
    result = add_comment(ticket_id, user_id, request.comment)

    if not result['success']:
        raise HTTPException(status_code=400, detail=result['message'])

    return result

# Attendance endpoints
@app.post("/api/attendance/clock-in/{user_id}")
async def user_clock_in(user_id: str):
    """Clock in for the day"""
    result = clock_in(user_id)

    if not result['success']:
        raise HTTPException(status_code=400, detail=result['message'])

    return result

@app.post("/api/attendance/clock-out/{user_id}")
async def user_clock_out(user_id: str):
    """Clock out for the day"""
    result = clock_out(user_id)

    if not result['success']:
        raise HTTPException(status_code=400, detail=result['message'])

    return result

@app.get("/api/attendance/records/{user_id}")
async def get_attendance_records(user_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None):
    """Get attendance records for a user"""
    records = view_attendance(user_id, start_date, end_date)

    return {
        "success": True,
        "data": records
    }

@app.get("/api/attendance/summary/{user_id}")
async def get_summary(user_id: str, month: Optional[int] = None, year: Optional[int] = None):
    """Get attendance summary for a user"""
    summary = get_attendance_summary(user_id, month, year)

    return {
        "success": True,
        "data": summary
    }

# ============================================
# PHASE 3: VISITOR, SHUTTLE, TRAINING, WELLNESS
# ============================================

# Visitor Registration Endpoints
@app.post("/api/visitors/register")
async def register_new_visitor(visitor: VisitorRequest):
    """Register a new visitor"""
    result = register_visitor(
        name=visitor.name,
        company=visitor.company,
        email=visitor.email,
        phone=visitor.phone,
        purpose=visitor.purpose,
        host_employee_id=visitor.host_employee_id,
        visit_date=visitor.visit_date,
        expected_arrival=visitor.expected_arrival,
        expected_departure=visitor.expected_departure,
        notes=visitor.notes
    )

    if not result['success']:
        raise HTTPException(status_code=400, detail=result['message'])

    return result

@app.post("/api/visitors/check-in/{visitor_id}")
async def check_in(visitor_id: str):
    """Check in a visitor"""
    result = check_in_visitor(visitor_id)

    if not result['success']:
        raise HTTPException(status_code=400, detail=result['message'])

    return result

@app.post("/api/visitors/check-out/{visitor_id}")
async def check_out(visitor_id: str):
    """Check out a visitor"""
    result = check_out_visitor(visitor_id)

    if not result['success']:
        raise HTTPException(status_code=400, detail=result['message'])

    return result

@app.get("/api/visitors")
async def get_visitors(
    host_employee_id: Optional[str] = None,
    visit_date: Optional[str] = None,
    status: Optional[str] = None
):
    """View visitors with optional filters"""
    result = view_visitors(host_employee_id, visit_date, status)
    return result

# Shuttle Booking Endpoints
@app.get("/api/shuttle/routes")
async def get_shuttle_routes():
    """Get all shuttle routes"""
    result = view_routes()
    return result

@app.post("/api/shuttle/book/{user_id}")
async def book_shuttle_seat(user_id: str, booking: ShuttleBookingRequest):
    """Book a shuttle"""
    result = book_shuttle(
        user_id=user_id,
        route_id=booking.route_id,
        date=booking.date,
        departure_time=booking.departure_time,
        seats=booking.seats
    )

    if not result['success']:
        raise HTTPException(status_code=400, detail=result['message'])

    return result

@app.post("/api/shuttle/cancel/{booking_id}/{user_id}")
async def cancel_shuttle(booking_id: str, user_id: str):
    """Cancel a shuttle booking"""
    result = cancel_shuttle_booking(booking_id, user_id)

    if not result['success']:
        raise HTTPException(status_code=400, detail=result['message'])

    return result

@app.get("/api/shuttle/bookings/{user_id}")
async def get_shuttle_bookings(user_id: str):
    """Get user's shuttle bookings"""
    result = view_shuttle_bookings(user_id)
    return result

# Training Endpoints
@app.get("/api/training/courses")
async def get_training_courses(category: Optional[str] = None, mandatory_only: bool = False):
    """Get all training courses"""
    result = view_courses(category, mandatory_only)
    return result

@app.post("/api/training/enroll/{user_id}")
async def enroll_in_course(user_id: str, enrollment: TrainingEnrollmentRequest):
    """Enroll in a training course"""
    result = enroll_course(user_id, enrollment.course_id, enrollment.session_id)

    if not result['success']:
        raise HTTPException(status_code=400, detail=result['message'])

    return result

@app.get("/api/training/enrollments/{user_id}")
async def get_user_enrollments(user_id: str):
    """Get user's course enrollments"""
    result = view_enrollments(user_id)
    return result

@app.post("/api/training/complete/{enrollment_id}/{user_id}")
async def complete_training(enrollment_id: str, user_id: str):
    """Mark a course as completed"""
    result = complete_course(enrollment_id, user_id)

    if not result['success']:
        raise HTTPException(status_code=400, detail=result['message'])

    return result

# Wellness Endpoints
@app.get("/api/wellness/activities")
async def get_wellness_activities(category: Optional[str] = None):
    """Get all wellness programs/activities"""
    result = view_activities(category)
    return result

@app.post("/api/wellness/join/{user_id}/{program_id}")
async def join_wellness_program(user_id: str, program_id: str):
    """Join a wellness program"""
    result = join_activity(user_id, program_id)

    if not result['success']:
        raise HTTPException(status_code=400, detail=result['message'])

    return result

@app.post("/api/wellness/log/{user_id}")
async def log_wellness_activity(user_id: str, log: WellnessLogRequest):
    """Log a wellness activity"""
    result = log_wellness(
        user_id=user_id,
        activity_type=log.activity_type,
        value=log.value,
        unit=log.unit,
        date=log.date,
        notes=log.notes
    )

    if not result['success']:
        raise HTTPException(status_code=400, detail=result['message'])

    return result

@app.get("/api/wellness/stats/{user_id}")
async def get_wellness_statistics(user_id: str, month: Optional[str] = None):
    """Get user's wellness statistics"""
    result = view_wellness_stats(user_id, month)
    return result

