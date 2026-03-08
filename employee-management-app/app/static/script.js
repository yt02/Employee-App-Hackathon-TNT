// Global state
let currentUser = null;
let currentPermissions = [];

// DOM Elements
const loginScreen = document.getElementById('loginScreen');
const appScreen = document.getElementById('appScreen');
const loginForm = document.getElementById('loginForm');
const loginError = document.getElementById('loginError');
const logoutBtn = document.getElementById('logoutBtn');
const userName = document.getElementById('userName');

// Tab switching
const tabBtns = document.querySelectorAll('.tab-btn');
const tabPanels = document.querySelectorAll('.tab-panel');

tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const tabName = btn.dataset.tab;
        
        // Update active tab button
        tabBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        // Update active tab panel
        tabPanels.forEach(panel => panel.classList.remove('active'));
        document.getElementById(tabName + 'Tab').classList.add('active');
        
        // Load data for the tab
        if (tabName === 'leave') {
            loadLeaveData();
        } else if (tabName === 'rooms') {
            loadRoomsData();
        }
    });
});

// Login
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            currentUser = data.data.user;
            currentPermissions = data.data.permissions;
            
            // Update UI
            userName.textContent = currentUser.name;
            loginScreen.classList.remove('active');
            appScreen.classList.add('active');
            
            // Load initial data
            loadLeaveData();
        } else {
            showError(loginError, data.detail || 'Login failed');
        }
    } catch (error) {
        showError(loginError, 'Connection error. Please try again.');
    }
});

// Logout
logoutBtn.addEventListener('click', () => {
    currentUser = null;
    currentPermissions = [];
    appScreen.classList.remove('active');
    loginScreen.classList.add('active');
    loginForm.reset();
});

// Helper functions
function showError(element, message) {
    element.textContent = message;
    element.classList.add('show');
    setTimeout(() => {
        element.classList.remove('show');
    }, 5000);
}

function showMessage(element, message, type = 'success') {
    element.textContent = message;
    element.className = `message show ${type}`;
    setTimeout(() => {
        element.classList.remove('show');
    }, 5000);
}

// Leave Management
async function loadLeaveData() {
    if (!currentUser) return;
    
    // Load leave balance
    try {
        const response = await fetch(`/api/leave/balance/${currentUser.user_id}`);
        const data = await response.json();
        
        if (data.success) {
            const balance = data.data;
            document.getElementById('alBalance').textContent = 
                `${balance.annual_leave.remaining}/${balance.annual_leave.total}`;
            document.getElementById('mlBalance').textContent = 
                `${balance.medical_leave.remaining}/${balance.medical_leave.total}`;
            document.getElementById('ulBalance').textContent = 
                `${balance.unpaid_leave.remaining}/${balance.unpaid_leave.total}`;
        }
    } catch (error) {
        console.error('Error loading leave balance:', error);
    }
    
    // Load leave history
    try {
        const response = await fetch(`/api/leave/history/${currentUser.user_id}`);
        const data = await response.json();
        
        if (data.success) {
            displayLeaveHistory(data.data);
        }
    } catch (error) {
        console.error('Error loading leave history:', error);
    }
}

function displayLeaveHistory(history) {
    const container = document.getElementById('leaveHistory');
    
    if (history.length === 0) {
        container.innerHTML = '<p>No leave history found.</p>';
        return;
    }
    
    const table = `
        <table>
            <thead>
                <tr>
                    <th>Request ID</th>
                    <th>Type</th>
                    <th>Start Date</th>
                    <th>End Date</th>
                    <th>Days</th>
                    <th>Status</th>
                    <th>Applied Date</th>
                </tr>
            </thead>
            <tbody>
                ${history.map(req => `
                    <tr>
                        <td>${req.request_id}</td>
                        <td>${req.leave_type.replace('_', ' ')}</td>
                        <td>${req.start_date}</td>
                        <td>${req.end_date}</td>
                        <td>${req.days}</td>
                        <td><span class="status-badge status-${req.status}">${req.status}</span></td>
                        <td>${req.applied_date}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    
    container.innerHTML = table;
}

// Leave application form
document.getElementById('leaveForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const leaveType = document.getElementById('leaveType').value;
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    const reason = document.getElementById('leaveReason').value;

    const messageEl = document.getElementById('leaveMessage');

    try {
        const response = await fetch(`/api/leave/apply/${currentUser.user_id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                leave_type: leaveType,
                start_date: startDate,
                end_date: endDate,
                reason: reason
            })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            showMessage(messageEl, data.message, 'success');
            e.target.reset();
            loadLeaveData(); // Refresh data
        } else {
            showMessage(messageEl, data.detail || data.message, 'error');
        }
    } catch (error) {
        showMessage(messageEl, 'Error submitting leave request', 'error');
    }
});

// Meeting Rooms Management
async function loadRoomsData() {
    if (!currentUser) return;

    // Load rooms list
    try {
        const response = await fetch('/api/rooms/list');
        const data = await response.json();

        if (data.success) {
            displayRooms(data.data);
            populateRoomSelect(data.data);
        }
    } catch (error) {
        console.error('Error loading rooms:', error);
    }

    // Load user bookings
    try {
        const response = await fetch(`/api/rooms/bookings/${currentUser.user_id}`);
        const data = await response.json();

        if (data.success) {
            displayBookings(data.data);
        }
    } catch (error) {
        console.error('Error loading bookings:', error);
    }
}

function displayRooms(rooms) {
    const container = document.getElementById('roomsList');

    const html = rooms.map(room => `
        <div class="room-card">
            <h4>${room.name}</h4>
            <div class="room-info">📍 Floor ${room.floor} | 👥 Capacity: ${room.capacity}</div>
            <div class="room-features">
                ${room.features.map(f => `<span class="feature-tag">${f}</span>`).join('')}
            </div>
        </div>
    `).join('');

    container.innerHTML = html;
}

function populateRoomSelect(rooms) {
    const select = document.getElementById('roomSelect');
    select.innerHTML = '<option value="">Choose a room...</option>';

    rooms.forEach(room => {
        const option = document.createElement('option');
        option.value = room.room_id;
        option.textContent = `${room.name} (Capacity: ${room.capacity})`;
        select.appendChild(option);
    });
}

function displayBookings(bookings) {
    const container = document.getElementById('myBookings');

    if (bookings.length === 0) {
        container.innerHTML = '<p>No bookings found.</p>';
        return;
    }

    const table = `
        <table>
            <thead>
                <tr>
                    <th>Booking ID</th>
                    <th>Room</th>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Purpose</th>
                    <th>Status</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
                ${bookings.map(booking => `
                    <tr>
                        <td>${booking.booking_id}</td>
                        <td>${booking.room_id}</td>
                        <td>${booking.date}</td>
                        <td>${booking.start_time} - ${booking.end_time}</td>
                        <td>${booking.purpose}</td>
                        <td><span class="status-badge status-${booking.status}">${booking.status}</span></td>
                        <td>
                            ${booking.status === 'confirmed' ?
                                `<button class="btn btn-secondary" onclick="cancelBooking('${booking.booking_id}')">Cancel</button>` :
                                '-'}
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;

    container.innerHTML = table;
}

// Room booking form
document.getElementById('roomBookingForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const roomId = document.getElementById('roomSelect').value;
    const date = document.getElementById('bookingDate').value;
    const startTime = document.getElementById('startTime').value;
    const endTime = document.getElementById('endTime').value;
    const purpose = document.getElementById('bookingPurpose').value;

    const messageEl = document.getElementById('roomMessage');

    try {
        const response = await fetch(`/api/rooms/book/${currentUser.user_id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                room_id: roomId,
                date: date,
                start_time: startTime,
                end_time: endTime,
                purpose: purpose
            })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            showMessage(messageEl, data.message, 'success');
            e.target.reset();
            loadRoomsData(); // Refresh data
        } else {
            showMessage(messageEl, data.detail || data.message, 'error');
        }
    } catch (error) {
        showMessage(messageEl, 'Error booking room', 'error');
    }
});

// Cancel booking
async function cancelBooking(bookingId) {
    if (!confirm('Are you sure you want to cancel this booking?')) {
        return;
    }

    try {
        const response = await fetch(`/api/rooms/cancel/${bookingId}/${currentUser.user_id}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (response.ok && data.success) {
            alert(data.message);
            loadRoomsData(); // Refresh data
        } else {
            alert(data.detail || data.message);
        }
    } catch (error) {
        alert('Error cancelling booking');
    }
}

// ============================================
// PHASE 2: CALENDAR, TICKETING, ATTENDANCE
// ============================================

// Update tab switching to include Phase 2 tabs
tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const tabName = btn.dataset.tab;

        // Update active tab button
        tabBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        // Update active tab panel
        tabPanels.forEach(panel => panel.classList.remove('active'));
        document.getElementById(tabName + 'Tab').classList.add('active');

        // Load data for the tab
        if (tabName === 'leave') {
            loadLeaveData();
        } else if (tabName === 'rooms') {
            loadRoomsData();
        } else if (tabName === 'calendar') {
            loadCalendarData();
        } else if (tabName === 'tickets') {
            loadTicketsData();
        } else if (tabName === 'attendance') {
            loadAttendanceData();
        } else if (tabName === 'visitor') {
            loadVisitorData();
        } else if (tabName === 'shuttle') {
            loadShuttleData();
        } else if (tabName === 'training') {
            loadTrainingData();
        } else if (tabName === 'wellness') {
            loadWellnessData();
        }
    });
});

// Calendar Management
async function loadCalendarData() {
    if (!currentUser) return;

    try {
        const response = await fetch(`/api/calendar/events/${currentUser.user_id}`);
        const data = await response.json();

        if (data.success) {
            displayEvents(data.data);
        }
    } catch (error) {
        console.error('Error loading calendar events:', error);
    }
}

function displayEvents(events) {
    const container = document.getElementById('myEvents');

    if (events.length === 0) {
        container.innerHTML = '<p>No events found.</p>';
        return;
    }

    const table = `
        <table>
            <thead>
                <tr>
                    <th>Title</th>
                    <th>Type</th>
                    <th>Start</th>
                    <th>End</th>
                    <th>Location</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                ${events.map(event => `
                    <tr>
                        <td>${event.title}</td>
                        <td><span class="status-badge event-${event.event_type}">${event.event_type}</span></td>
                        <td>${new Date(event.start_datetime).toLocaleString()}</td>
                        <td>${new Date(event.end_datetime).toLocaleString()}</td>
                        <td>${event.location || '-'}</td>
                        <td><span class="status-badge status-${event.status}">${event.status}</span></td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;

    container.innerHTML = table;
}

// Event form submission
document.getElementById('eventForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const title = document.getElementById('eventTitle').value;
    const description = document.getElementById('eventDescription').value;
    const startDate = document.getElementById('eventStartDate').value;
    const endDate = document.getElementById('eventEndDate').value;
    const location = document.getElementById('eventLocation').value;
    const eventType = document.getElementById('eventType').value;

    const messageEl = document.getElementById('eventMessage');

    try {
        const response = await fetch(`/api/calendar/events/${currentUser.user_id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                title: title,
                description: description,
                start_datetime: startDate,
                end_datetime: endDate,
                location: location,
                attendees: [currentUser.user_id],
                event_type: eventType
            })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            showMessage(messageEl, data.message, 'success');
            e.target.reset();
            loadCalendarData(); // Refresh data
        } else {
            showMessage(messageEl, data.detail || data.message, 'error');
        }
    } catch (error) {
        showMessage(messageEl, 'Error creating event', 'error');
    }
});

// Ticketing Management
async function loadTicketsData() {
    if (!currentUser) return;

    try {
        const response = await fetch(`/api/tickets/${currentUser.user_id}?filter_type=my_tickets`);
        const data = await response.json();

        if (data.success) {
            displayTickets(data.data);
        }
    } catch (error) {
        console.error('Error loading tickets:', error);
    }
}

function displayTickets(tickets) {
    const container = document.getElementById('myTickets');

    if (tickets.length === 0) {
        container.innerHTML = '<p>No tickets found.</p>';
        return;
    }

    const table = `
        <table>
            <thead>
                <tr>
                    <th>Ticket ID</th>
                    <th>Title</th>
                    <th>Category</th>
                    <th>Priority</th>
                    <th>Status</th>
                    <th>Created</th>
                </tr>
            </thead>
            <tbody>
                ${tickets.map(ticket => `
                    <tr>
                        <td>${ticket.ticket_id}</td>
                        <td>${ticket.title}</td>
                        <td>${ticket.category}</td>
                        <td><span class="status-badge priority-${ticket.priority}">${ticket.priority}</span></td>
                        <td><span class="status-badge status-${ticket.status.replace('_', '-')}">${ticket.status.replace('_', ' ')}</span></td>
                        <td>${new Date(ticket.created_at).toLocaleDateString()}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;

    container.innerHTML = table;
}

// Ticket form submission
document.getElementById('ticketForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const title = document.getElementById('ticketTitle').value;
    const description = document.getElementById('ticketDescription').value;
    const category = document.getElementById('ticketCategory').value;
    const priority = document.getElementById('ticketPriority').value;

    const messageEl = document.getElementById('ticketMessage');

    try {
        const response = await fetch(`/api/tickets/create/${currentUser.user_id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                title: title,
                description: description,
                category: category,
                priority: priority
            })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            showMessage(messageEl, data.message, 'success');
            e.target.reset();
            loadTicketsData(); // Refresh data
        } else {
            showMessage(messageEl, data.detail || data.message, 'error');
        }
    } catch (error) {
        showMessage(messageEl, 'Error creating ticket', 'error');
    }
});

// Attendance Management
async function loadAttendanceData() {
    if (!currentUser) return;

    // Load attendance summary
    try {
        const response = await fetch(`/api/attendance/summary/${currentUser.user_id}`);
        const data = await response.json();

        if (data.success) {
            displayAttendanceSummary(data.data);
        }
    } catch (error) {
        console.error('Error loading attendance summary:', error);
    }

    // Load attendance records
    try {
        const response = await fetch(`/api/attendance/records/${currentUser.user_id}`);
        const data = await response.json();

        if (data.success) {
            displayAttendanceRecords(data.data);
        }
    } catch (error) {
        console.error('Error loading attendance records:', error);
    }
}

function displayAttendanceSummary(summary) {
    const container = document.getElementById('attendanceSummary');

    const html = `
        <div class="summary-item">
            <div class="summary-label">Total Days</div>
            <div class="summary-value">${summary.total_days}</div>
        </div>
        <div class="summary-item">
            <div class="summary-label">Present</div>
            <div class="summary-value">${summary.present_days}</div>
        </div>
        <div class="summary-item">
            <div class="summary-label">On Leave</div>
            <div class="summary-value">${summary.on_leave_days}</div>
        </div>
        <div class="summary-item">
            <div class="summary-label">Total Hours</div>
            <div class="summary-value">${summary.total_hours}</div>
        </div>
        <div class="summary-item">
            <div class="summary-label">Avg Hours/Day</div>
            <div class="summary-value">${summary.average_hours_per_day}</div>
        </div>
    `;

    container.innerHTML = html;
}

function displayAttendanceRecords(records) {
    const container = document.getElementById('attendanceRecords');

    if (records.length === 0) {
        container.innerHTML = '<p>No attendance records found.</p>';
        return;
    }

    const table = `
        <table>
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Clock In</th>
                    <th>Clock Out</th>
                    <th>Total Hours</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                ${records.map(record => `
                    <tr>
                        <td>${record.date}</td>
                        <td>${record.clock_in || '-'}</td>
                        <td>${record.clock_out || '-'}</td>
                        <td>${record.total_hours.toFixed(2)}</td>
                        <td><span class="status-badge status-${record.status.replace('_', '-')}">${record.status.replace('_', ' ')}</span></td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;

    container.innerHTML = table;
}

// Clock in button
document.getElementById('clockInBtn').addEventListener('click', async () => {
    const messageEl = document.getElementById('clockMessage');

    try {
        const response = await fetch(`/api/attendance/clock-in/${currentUser.user_id}`, {
            method: 'POST'
        });

        const data = await response.json();

        if (response.ok && data.success) {
            showMessage(messageEl, data.message, 'success');
            loadAttendanceData(); // Refresh data
        } else {
            showMessage(messageEl, data.detail || data.message, 'error');
        }
    } catch (error) {
        showMessage(messageEl, 'Error clocking in', 'error');
    }
});

// Clock out button
document.getElementById('clockOutBtn').addEventListener('click', async () => {
    const messageEl = document.getElementById('clockMessage');

    try {
        const response = await fetch(`/api/attendance/clock-out/${currentUser.user_id}`, {
            method: 'POST'
        });

        const data = await response.json();

        if (response.ok && data.success) {
            showMessage(messageEl, data.message, 'success');
            loadAttendanceData(); // Refresh data
        } else {
            showMessage(messageEl, data.detail || data.message, 'error');
        }
    } catch (error) {
        showMessage(messageEl, 'Error clocking out', 'error');
    }
});

// ============================================
// PHASE 3: VISITOR, SHUTTLE, TRAINING, WELLNESS
// ============================================

// Visitor Management
async function loadVisitorData() {
    if (!currentUser) return;

    try {
        const response = await fetch(`/api/visitors?host_employee_id=${currentUser.user_id}`);
        const data = await response.json();

        if (data.success) {
            displayVisitors(data.data);
        } else {
            document.getElementById('visitorsList').innerHTML = '<p>Error loading visitors</p>';
        }
    } catch (error) {
        console.error('Error loading visitors:', error);
        document.getElementById('visitorsList').innerHTML = '<p>Error loading visitors. Please check if server is running.</p>';
    }
}

function displayVisitors(visitors) {
    const container = document.getElementById('visitorsList');

    if (visitors.length === 0) {
        container.innerHTML = '<p>No visitors found.</p>';
        return;
    }

    const table = `
        <table>
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Company</th>
                    <th>Purpose</th>
                    <th>Visit Date</th>
                    <th>Status</th>
                    <th>Badge</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                ${visitors.map(visitor => `
                    <tr>
                        <td>${visitor.name}</td>
                        <td>${visitor.company}</td>
                        <td>${visitor.purpose}</td>
                        <td>${visitor.visit_date}</td>
                        <td><span class="status-badge status-${visitor.status.replace('_', '-')}">${visitor.status.replace('_', ' ')}</span></td>
                        <td>${visitor.badge_number || '-'}</td>
                        <td>
                            ${visitor.status === 'scheduled' ? `<button class="btn btn-sm" onclick="checkInVisitor('${visitor.visitor_id}')">Check In</button>` : ''}
                            ${visitor.status === 'checked_in' ? `<button class="btn btn-sm" onclick="checkOutVisitor('${visitor.visitor_id}')">Check Out</button>` : ''}
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;

    container.innerHTML = table;
}

// Visitor form submission
document.getElementById('visitorForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const messageEl = document.getElementById('visitorMessage');

    try {
        const response = await fetch('/api/visitors/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: document.getElementById('visitorName').value,
                company: document.getElementById('visitorCompany').value,
                email: document.getElementById('visitorEmail').value,
                phone: document.getElementById('visitorPhone').value,
                purpose: document.getElementById('visitorPurpose').value,
                host_employee_id: currentUser.user_id,
                visit_date: document.getElementById('visitorDate').value,
                expected_arrival: document.getElementById('visitorArrival').value,
                expected_departure: document.getElementById('visitorDeparture').value,
                notes: ""
            })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            showMessage(messageEl, data.message, 'success');
            e.target.reset();
            loadVisitorData();
        } else {
            showMessage(messageEl, data.detail || data.message, 'error');
        }
    } catch (error) {
        showMessage(messageEl, 'Error registering visitor', 'error');
    }
});

async function checkInVisitor(visitorId) {
    try {
        const response = await fetch(`/api/visitors/check-in/${visitorId}`, {
            method: 'POST'
        });

        const data = await response.json();

        if (response.ok && data.success) {
            alert(data.message);
            loadVisitorData();
        } else {
            alert(data.detail || data.message);
        }
    } catch (error) {
        alert('Error checking in visitor');
    }
}

async function checkOutVisitor(visitorId) {
    try {
        const response = await fetch(`/api/visitors/check-out/${visitorId}`, {
            method: 'POST'
        });

        const data = await response.json();

        if (response.ok && data.success) {
            alert(data.message);
            loadVisitorData();
        } else {
            alert(data.detail || data.message);
        }
    } catch (error) {
        alert('Error checking out visitor');
    }
}

// Shuttle Management
let shuttleRoutes = [];

async function loadShuttleData() {
    if (!currentUser) return;

    // Load routes
    try {
        const response = await fetch('/api/shuttle/routes');
        const data = await response.json();

        if (data.success) {
            shuttleRoutes = data.data;
            populateShuttleRoutes();
        }
    } catch (error) {
        console.error('Error loading shuttle routes:', error);
    }

    // Load bookings
    try {
        const response = await fetch(`/api/shuttle/bookings/${currentUser.user_id}`);
        const data = await response.json();

        if (data.success) {
            displayShuttleBookings(data.data);
        }
    } catch (error) {
        console.error('Error loading shuttle bookings:', error);
    }
}

function populateShuttleRoutes() {
    const select = document.getElementById('shuttleRoute');
    select.innerHTML = '<option value="">Select route...</option>';

    shuttleRoutes.forEach(route => {
        const option = document.createElement('option');
        option.value = route.route_id;
        option.textContent = `${route.route_name} (${route.departure_point} → ${route.destination})`;
        select.appendChild(option);
    });
}

// Update shuttle times when route is selected
document.getElementById('shuttleRoute').addEventListener('change', (e) => {
    const routeId = e.target.value;
    const timeSelect = document.getElementById('shuttleTime');

    if (!routeId) {
        timeSelect.innerHTML = '<option value="">Select time...</option>';
        return;
    }

    const route = shuttleRoutes.find(r => r.route_id === routeId);
    if (route) {
        timeSelect.innerHTML = '<option value="">Select time...</option>';
        route.schedule.forEach(slot => {
            const option = document.createElement('option');
            option.value = slot.departure_time;
            option.textContent = `${slot.departure_time} (${slot.capacity} seats)`;
            timeSelect.appendChild(option);
        });
    }
});

function displayShuttleBookings(bookings) {
    const container = document.getElementById('shuttleBookings');

    if (bookings.length === 0) {
        container.innerHTML = '<p>No shuttle bookings found.</p>';
        return;
    }

    const table = `
        <table>
            <thead>
                <tr>
                    <th>Route</th>
                    <th>Date</th>
                    <th>Departure Time</th>
                    <th>Seats</th>
                    <th>Status</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                ${bookings.map(booking => `
                    <tr>
                        <td>${booking.route_name || booking.route_id}</td>
                        <td>${booking.date}</td>
                        <td>${booking.departure_time}</td>
                        <td>${booking.seats}</td>
                        <td><span class="status-badge status-${booking.status}">${booking.status}</span></td>
                        <td>
                            ${booking.status === 'confirmed' ? `<button class="btn btn-sm" onclick="cancelShuttleBooking('${booking.booking_id}')">Cancel</button>` : ''}
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;

    container.innerHTML = table;
}

// Shuttle form submission
document.getElementById('shuttleForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const messageEl = document.getElementById('shuttleMessage');

    try {
        const response = await fetch(`/api/shuttle/book/${currentUser.user_id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                route_id: document.getElementById('shuttleRoute').value,
                date: document.getElementById('shuttleDate').value,
                departure_time: document.getElementById('shuttleTime').value,
                seats: parseInt(document.getElementById('shuttleSeats').value)
            })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            showMessage(messageEl, data.message, 'success');
            e.target.reset();
            loadShuttleData();
        } else {
            showMessage(messageEl, data.detail || data.message, 'error');
        }
    } catch (error) {
        showMessage(messageEl, 'Error booking shuttle', 'error');
    }
});

async function cancelShuttleBooking(bookingId) {
    try {
        const response = await fetch(`/api/shuttle/cancel/${bookingId}/${currentUser.user_id}`, {
            method: 'POST'
        });

        const data = await response.json();

        if (response.ok && data.success) {
            alert(data.message);
            loadShuttleData();
        } else {
            alert(data.detail || data.message);
        }
    } catch (error) {
        alert('Error cancelling shuttle booking');
    }
}

// Training Management
async function loadTrainingData() {
    console.log('loadTrainingData called, currentUser:', currentUser);
    if (!currentUser) return;

    // Load courses
    try {
        console.log('Fetching training courses...');
        const response = await fetch('/api/training/courses');
        console.log('Training courses response:', response);
        const data = await response.json();
        console.log('Training courses data:', data);

        if (data.success) {
            displayTrainingCourses(data.data);
        } else {
            document.getElementById('trainingCourses').innerHTML = '<p>Error loading courses</p>';
        }
    } catch (error) {
        console.error('Error loading training courses:', error);
        document.getElementById('trainingCourses').innerHTML = '<p>Error loading courses. Please check if server is running.</p>';
    }

    // Load enrollments
    try {
        console.log('Fetching training enrollments...');
        const response = await fetch(`/api/training/enrollments/${currentUser.user_id}`);
        console.log('Training enrollments response:', response);
        const data = await response.json();
        console.log('Training enrollments data:', data);

        if (data.success) {
            displayTrainingEnrollments(data.data);
        } else {
            document.getElementById('trainingEnrollments').innerHTML = '<p>Error loading enrollments</p>';
        }
    } catch (error) {
        console.error('Error loading training enrollments:', error);
        document.getElementById('trainingEnrollments').innerHTML = '<p>Error loading enrollments. Please check if server is running.</p>';
    }
}

function displayTrainingCourses(courses) {
    console.log('displayTrainingCourses called with:', courses);
    const container = document.getElementById('trainingCourses');
    console.log('Container element:', container);

    if (courses.length === 0) {
        container.innerHTML = '<p>No courses available.</p>';
        return;
    }

    try {
        const table = `
            <table>
                <thead>
                    <tr>
                        <th>Course</th>
                        <th>Category</th>
                        <th>Duration</th>
                        <th>Instructor</th>
                        <th>Mandatory</th>
                        <th>Sessions</th>
                    </tr>
                </thead>
                <tbody>
                    ${courses.map(course => `
                        <tr>
                            <td><strong>${course.title}</strong><br><small>${course.description}</small></td>
                            <td>${course.category}</td>
                            <td>${course.duration_hours}h</td>
                            <td>${course.instructor}</td>
                            <td>${course.mandatory ? '✓ Yes' : 'No'}</td>
                            <td>
                                ${course.schedule.map(session => `
                                    <div style="margin-bottom: 5px;">
                                        ${session.date} ${session.start_time}<br>
                                        <small>${session.location} (${session.enrolled_count}/${course.max_participants})</small>
                                        <button class="btn btn-sm" onclick="enrollInCourse('${course.course_id}', '${session.session_id}')">Enroll</button>
                                    </div>
                                `).join('')}
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;

        console.log('Setting innerHTML...');
        container.innerHTML = table;
        console.log('Table displayed successfully');
    } catch (error) {
        console.error('Error displaying courses:', error);
        container.innerHTML = '<p>Error displaying courses</p>';
    }
}

function displayTrainingEnrollments(enrollments) {
    const container = document.getElementById('trainingEnrollments');

    if (enrollments.length === 0) {
        container.innerHTML = '<p>No enrollments found.</p>';
        return;
    }

    const table = `
        <table>
            <thead>
                <tr>
                    <th>Course</th>
                    <th>Category</th>
                    <th>Session Date</th>
                    <th>Location</th>
                    <th>Status</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                ${enrollments.map(enrollment => `
                    <tr>
                        <td>${enrollment.course_title}</td>
                        <td>${enrollment.course_category}</td>
                        <td>${enrollment.session_date || '-'}<br><small>${enrollment.session_time || ''}</small></td>
                        <td>${enrollment.location || '-'}</td>
                        <td><span class="status-badge status-${enrollment.status}">${enrollment.status}</span></td>
                        <td>
                            ${enrollment.status === 'enrolled' ? `<button class="btn btn-sm" onclick="completeCourse('${enrollment.enrollment_id}')">Mark Complete</button>` : ''}
                            ${enrollment.certificate_issued ? '🏆 Certificate' : ''}
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;

    container.innerHTML = table;
}

async function enrollInCourse(courseId, sessionId) {
    try {
        const response = await fetch(`/api/training/enroll/${currentUser.user_id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                course_id: courseId,
                session_id: sessionId
            })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            alert(data.message);
            loadTrainingData();
        } else {
            alert(data.detail || data.message);
        }
    } catch (error) {
        alert('Error enrolling in course');
    }
}

async function completeCourse(enrollmentId) {
    try {
        const response = await fetch(`/api/training/complete/${enrollmentId}/${currentUser.user_id}`, {
            method: 'POST'
        });

        const data = await response.json();

        if (response.ok && data.success) {
            alert(data.message);
            loadTrainingData();
        } else {
            alert(data.detail || data.message);
        }
    } catch (error) {
        alert('Error completing course');
    }
}

// Wellness Management
async function loadWellnessData() {
    if (!currentUser) return;

    // Load programs
    try {
        const response = await fetch('/api/wellness/activities');
        const data = await response.json();

        if (data.success) {
            displayWellnessPrograms(data.data);
        }
    } catch (error) {
        console.error('Error loading wellness programs:', error);
    }

    // Load statistics
    try {
        const response = await fetch(`/api/wellness/stats/${currentUser.user_id}`);
        const data = await response.json();

        if (data.success) {
            displayWellnessStats(data.data);
        }
    } catch (error) {
        console.error('Error loading wellness stats:', error);
    }
}

function displayWellnessPrograms(programs) {
    const container = document.getElementById('wellnessPrograms');

    if (programs.length === 0) {
        container.innerHTML = '<p>No wellness programs available.</p>';
        return;
    }

    const table = `
        <table>
            <thead>
                <tr>
                    <th>Program</th>
                    <th>Category</th>
                    <th>Schedule</th>
                    <th>Location</th>
                    <th>Participants</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                ${programs.map(program => `
                    <tr>
                        <td><strong>${program.title}</strong><br><small>${program.description}</small></td>
                        <td><span class="status-badge">${program.category}</span></td>
                        <td>
                            ${program.schedule.map(s => `${s.day} ${s.time} (${s.duration_minutes}min)`).join('<br>')}
                        </td>
                        <td>${program.location}</td>
                        <td>${program.enrolled_count}/${program.max_participants}</td>
                        <td>
                            <button class="btn btn-sm" onclick="joinWellnessProgram('${program.program_id}')">Join</button>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;

    container.innerHTML = table;
}

function displayWellnessStats(data) {
    const container = document.getElementById('wellnessStats');

    if (!data.statistics || data.statistics.length === 0) {
        container.innerHTML = '<p>No wellness data logged yet.</p>';
        return;
    }

    const html = data.statistics.map(stat => `
        <div class="summary-item">
            <div class="summary-label">${stat.activity_type}</div>
            <div class="summary-value">${stat.total} ${stat.unit}</div>
            <small>Avg: ${stat.average} ${stat.unit}</small>
        </div>
    `).join('');

    container.innerHTML = html;
}

// Wellness form submission
document.getElementById('wellnessForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const messageEl = document.getElementById('wellnessMessage');

    try {
        const response = await fetch(`/api/wellness/log/${currentUser.user_id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                activity_type: document.getElementById('wellnessType').value,
                value: parseFloat(document.getElementById('wellnessValue').value),
                unit: document.getElementById('wellnessUnit').value,
                notes: ""
            })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            showMessage(messageEl, data.message, 'success');
            e.target.reset();
            loadWellnessData();
        } else {
            showMessage(messageEl, data.detail || data.message, 'error');
        }
    } catch (error) {
        showMessage(messageEl, 'Error logging wellness activity', 'error');
    }
});

async function joinWellnessProgram(programId) {
    try {
        const response = await fetch(`/api/wellness/join/${currentUser.user_id}/${programId}`, {
            method: 'POST'
        });

        const data = await response.json();

        if (response.ok && data.success) {
            alert(data.message);
            loadWellnessData();
        } else {
            alert(data.detail || data.message);
        }
    } catch (error) {
        alert('Error joining wellness program');
    }
}
