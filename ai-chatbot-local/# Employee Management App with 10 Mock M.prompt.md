# Employee Management App with 10 Mock Modules

**TL;DR:** Add a multi-functional employee app with **10 mock modules** where all data, users, and processes are simulated. Use JSON files for mock data storage, hardcoded user authentication, and a hybrid UI (chat interface + dedicated module panels). The router classifies user intent and dispatches to the appropriate mock module or document Q&A.

## Steps

### 1. Create Module Architecture & Mock Data Structure
   - Create `app/modules/` directory with 10 subdirectories:
     - user_management
     - leave
     - calendar
     - meeting_rooms
     - ticketing
     - visitor_registration
     - shuttle
     - training
     - wellness
     - attendance
   
   - Create `data/mock_data/` with JSON files:
     - users.json
     - roles.json
     - leave_balances.json
     - calendar_events.json
     - rooms.json
     - tickets.json
     - visitors.json
     - shuttles.json
     - training_programs.json
     - fitness_classes.json
     - attendance_records.json
   
   - Define mock data schema for each module (users with roles, permissions, pre-populated data)

### 2. Build Intent Router & Request Dispatcher
   - Add intent classification function (keyword-based) to detect module from query
     - "apply leave" → leave
     - "book room" → meeting_rooms
     - "submit ticket" → ticketing
     - etc.
   - Modify `app/chat.py` to check intent and route to module handler vs. RAG retrieval
   - Create `app/intent_classifier.py` with keyword mapping to modules

### 3. Implement 10 Mock Module Handlers
   
   **User/Role Management:**
   - `authenticate_user()` - mock login validation
   - `get_user_permissions()` - check user roles
   - `get_user_info()` - return user details
   
   **Leave:**
   - `get_leave_balance()` - retrieve AL, MC, etc. by user
   - `apply_leave()` - submit leave request, update JSON
   - `view_history()` - show past leave records
   
   **Calendar:**
   - `get_calendar()` - return user's calendar events
   - `add_event()` - create new event
   - `check_availability()` - show free time slots
   
   **Meeting Rooms:**
   - `list_rooms()` - show all rooms with capacity, features
   - `check_availability()` - show booked slots by date/time
   - `book_room()` - create booking, prevent double-booking
   - `cancel_booking()` - remove reservation
   
   **Ticketing:**
   - `submit_ticket()` - create support request with auto-routing
   - `view_ticket_status()` - check ticket progress
   - `list_tickets()` - show all user's tickets
   
   **Visitor Registration:**
   - `register_visitor()` - add external visitor with time bounds
   - `view_visitors()` - list registered visitors
   
   **Shuttle Booking:**
   - `book_shuttle()` - reserve a ride
   - `view_timetable()` - show routes and schedules
   - `cancel_booking()` - remove reservation
   - `track_status()` - show booking status
   
   **Training:**
   - `view_programs()` - list available training courses
   - `enroll()` - register for training
   - `view_records()` - show personal training history
   
   **Wellness:**
   - `view_classes()` - list fitness classes and schedules
   - `signup_class()` - register for class
   - `view_trainer_list()` - show trainers
   
   **Attendance:**
   - `checkin()` - log attendance (mock clock-in/out)
   - `view_history()` - show past attendance records

### 4. Create Unified API Endpoints in `app/main.py`
   - Keep existing GET `/` and POST `/chat` endpoints
   - Add `/api/auth/login` (mock authentication)
   - Add `/api/{module}/{action}` dynamic routing for all module operations
   - All endpoints return standardized JSON response format:
     ```json
     {
       "success": true/false,
       "message": "...",
       "data": {...}
     }
     ```

### 5. Update Frontend UI
   - Modify `app/static/index.html`:
     - Add login section (username/password form)
     - Add module navigation tabs (Leave, Rooms, Tickets, Calendar, Attendance, Shuttle, Training, Wellness, Visitor, Chat)
     - Create separate panels/sections for each module with module-specific forms
     - Keep chat interface for document Q&A and general queries
   
   - Update `app/static/script.js`:
     - Handle module form submissions and routing
     - Implement tab switching logic
     - Display module-specific responses vs. chat responses
     - Maintain session state (logged-in user, current module)

### 6. Update `app/requirements.txt`
   - Add any new dependencies (likely minimal—just JSON I/O, already covered)

## Further Refinements & Design Decisions

### 1. Mock User Accounts
   Create 3-5 pre-defined users with different roles:
   - `emp_001` (Employee) - can apply leave, book rooms, access training
   - `hr_manager_001` (HR Manager) - can view/approve leave, manage training
   - `facility_mgr_001` (Facility Manager) - can manage rooms, visitor registration
   - `admin_001` (Admin) - full access to all modules

### 2. Data Persistence Strategy
   - **Option A:** JSON files (data lost on app restart, simple, suitable for demo)
   - **Option B:** In-memory with file sync (faster, data persists, good for testing)
   - **Recommendation:** Start with JSON files for simplicity

### 3. Navigation/UX
   - **Option A:** Module tabs in header + dedicated form sections below
   - **Option B:** Unified chat interface with [LEAVE], [BOOKING], [TICKET] command buttons
   - **Option C:** Sidebar navigation menu with module panels
   - **Recommendation:** Tabs in header (cleaner, more scalable)

### 4. Mock Data Initialization
   - Pre-populate JSON files with sample data on app startup
   - Generate mock leave balances, meeting rooms, events per user
   - Create sample tickets, visitor records, shuttle routes in data files

### 5. Permission/Role-Based Actions
   - Check user role before allowing certain actions (e.g., only HR can approve leave)
   - Return "Permission Denied" errors for unauthorized actions
   - Track which user performs each action (for audit trail simulation)

### 6. Workflow Examples (End-to-End Demo Scenarios)
   - **Scenario 1:** Employee logs in → applies for tomorrow's AL → leaves balance updates
   - **Scenario 2:** Employee books meeting room → calendar integration → confirmation message
   - **Scenario 3:** Employee submits IT ticket → auto-routed to IT department → status updates
   - **Scenario 4:** Facility manager registers visitor → time-bound access → visitor record created

## Implementation Priority

1. **Phase 1 (Core):** User authentication, Leave system, Meeting room booking
2. **Phase 2 (Standard):** Calendar, Ticketing, Attendance
3. **Phase 3 (Enhanced):** Visitor registration, Shuttle booking, Training, Wellness
