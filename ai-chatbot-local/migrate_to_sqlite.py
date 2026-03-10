import os
import json
import sqlite3


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data", "mock_data")
DB_PATH = os.path.join(BASE_DIR, "data", "database.db")

def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def migrate():
    print(f"Migrating JSON data to {DB_PATH}...")
    
    # Remove existing db if rewriting
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            username TEXT,
            password TEXT,
            name TEXT,
            email TEXT,
            role TEXT,
            department TEXT,
            manager_id TEXT
        )
    """)
    users = load_json("users.json")
    for user in users:
        cursor.execute("""
            INSERT INTO users (user_id, username, password, name, email, role, department, manager_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user["user_id"], user["username"], user["password"], user["name"], user["email"], user["role"], user.get("department"), user.get("manager_id")))
    
    # 2. Leave Balances
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leave_balances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            year INTEGER,
            annual_total INTEGER,
            annual_remaining INTEGER,
            medical_total INTEGER,
            medical_remaining INTEGER,
            unpaid_total INTEGER,
            unpaid_remaining INTEGER,
            compassionate_total INTEGER,
            compassionate_remaining INTEGER,
            maternity_total INTEGER,
            maternity_remaining INTEGER,
            paternity_total INTEGER,
            paternity_remaining INTEGER,
            carry_forward_days INTEGER,
            carry_forward_expiry TEXT
        )
    """)
    leave_balances = load_json("leave_balances.json")
    for bal in leave_balances:
        cursor.execute("""
            INSERT INTO leave_balances (
                user_id, year, 
                annual_total, annual_remaining, 
                medical_total, medical_remaining, 
                unpaid_total, unpaid_remaining,
                compassionate_total, compassionate_remaining,
                maternity_total, maternity_remaining,
                paternity_total, paternity_remaining,
                carry_forward_days, carry_forward_expiry
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            bal["user_id"], bal["year"],
            bal.get("annual_leave", {}).get("total", 0), bal.get("annual_leave", {}).get("remaining", 0),
            bal.get("medical_leave", {}).get("total", 0), bal.get("medical_leave", {}).get("remaining", 0),
            bal.get("unpaid_leave", {}).get("total", 0), bal.get("unpaid_leave", {}).get("remaining", 0),
            bal.get("compassionate_leave", {}).get("total", 0), bal.get("compassionate_leave", {}).get("remaining", 0),
            bal.get("maternity_leave", {}).get("total", 0), bal.get("maternity_leave", {}).get("remaining", 0),
            bal.get("paternity_leave", {}).get("total", 0), bal.get("paternity_leave", {}).get("remaining", 0),
            bal.get("carry_forward_days", 0), bal.get("carry_forward_expiry", "")
        ))

    # 3. Leave Requests
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leave_requests (
            request_id TEXT PRIMARY KEY,
            user_id TEXT,
            leave_type TEXT,
            start_date TEXT,
            end_date TEXT,
            days INTEGER,
            reason TEXT,
            status TEXT,
            applied_date TEXT,
            approved_by TEXT,
            approved_date TEXT
        )
    """)
    leave_requests = load_json("leave_requests.json")
    for req in leave_requests:
        cursor.execute("""
            INSERT INTO leave_requests (
                request_id, user_id, leave_type, start_date, end_date, 
                days, reason, status, applied_date, approved_by, approved_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            req["request_id"], req["user_id"], req["leave_type"], req["start_date"], req["end_date"],
            req["days"], req.get("reason"), req["status"], req.get("applied_date"), req.get("approved_by"), req.get("approved_date")
        ))

    # 4. Rooms
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            room_id TEXT PRIMARY KEY,
            name TEXT,
            capacity INTEGER,
            location TEXT,
            features_json TEXT
        )
    """)
    rooms = load_json("rooms.json")
    for room in rooms:
        features = room.get("features", room.get("facilities", []))
        cursor.execute("""
            INSERT INTO rooms (room_id, name, capacity, location, features_json)
            VALUES (?, ?, ?, ?, ?)
        """, (
            room["room_id"], room["name"], room["capacity"], 
            room.get("location", f"Floor {room.get('floor', 'Unknown')}"), 
            json.dumps(features)
        ))

    # 5. Room Bookings
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS room_bookings (
            booking_id TEXT PRIMARY KEY,
            room_id TEXT,
            user_id TEXT,
            date TEXT,
            start_time TEXT,
            end_time TEXT,
            purpose TEXT,
            status TEXT,
            created_at TEXT
        )
    """)
    room_bookings = load_json("room_bookings.json")
    for bk in room_bookings:
        cursor.execute("""
            INSERT INTO room_bookings (
                booking_id, room_id, user_id, date, start_time, end_time, purpose, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            bk["booking_id"], bk["room_id"], bk["user_id"], bk["date"], 
            bk["start_time"], bk["end_time"], bk.get("purpose"), bk["status"], bk.get("created_at")
        ))

    # 7. Training Courses
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS training_courses (
            course_id TEXT PRIMARY KEY,
            title TEXT,
            description TEXT,
            category TEXT,
            instructor TEXT,
            duration_hours INTEGER,
            max_participants INTEGER,
            status TEXT,
            mandatory BOOLEAN,
            schedule_json TEXT
        )
    """)
    training_courses = load_json("training_courses.json")
    for course in training_courses:
        cursor.execute("""
            INSERT INTO training_courses (
                course_id, title, description, category, instructor, 
                duration_hours, max_participants, status, mandatory, schedule_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            course["course_id"], course["title"], course["description"], 
            course["category"], course["instructor"], course["duration_hours"], 
            course["max_participants"], course["status"], course["mandatory"],
            json.dumps(course.get("schedule", []))
        ))

    # 8. Wellness Programs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wellness_programs (
            program_id TEXT PRIMARY KEY,
            title TEXT,
            description TEXT,
            category TEXT,
            location TEXT,
            instructor TEXT,
            max_participants INTEGER,
            status TEXT,
            schedule_json TEXT
        )
    """)
    wellness_programs = load_json("wellness_programs.json")
    for program in wellness_programs:
        cursor.execute("""
            INSERT INTO wellness_programs (
                program_id, title, description, category, location, 
                instructor, max_participants, status, schedule_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            program["program_id"], program["title"], program["description"], 
            program["category"], program["location"], program["instructor"], 
            program["max_participants"], program["status"],
            json.dumps(program.get("schedule", []))
        ))

    # 9. Training Enrollments
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS training_enrollments (
            enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            course_id TEXT,
            status TEXT,
            enrolled_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (course_id) REFERENCES training_courses(course_id)
        )
    """)

    # 10. Wellness Registrations
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wellness_registrations (
            registration_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            program_id TEXT,
            status TEXT,
            registered_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (program_id) REFERENCES wellness_programs(program_id)
        )
    """)

    # 11. Visitors
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS visitors (
            visitor_id INTEGER PRIMARY KEY AUTOINCREMENT,
            host_id TEXT,
            visitor_name TEXT,
            visitor_ic TEXT,
            company TEXT,
            date TEXT,
            time TEXT,
            purpose TEXT,
            visitor_email TEXT,
            looking_for TEXT,
            to_date TEXT,
            status TEXT DEFAULT 'pre-registered',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (host_id) REFERENCES users(user_id)
        )
    """)

    conn.commit()
    conn.close()
    print("Migration completed successfully!")

if __name__ == "__main__":
    migrate()
