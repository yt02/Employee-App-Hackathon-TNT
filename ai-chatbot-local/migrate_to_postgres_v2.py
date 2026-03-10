import os
import sys
import json
import psycopg2
from urllib.parse import urlparse, uses_netloc
from psycopg2.extras import RealDictCursor

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data", "mock_data")
DATABASE_URL = os.environ.get("DATABASE_URL")

def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def migrate():
    print(f"Starting migration... Python version: {sys.version}")
    if not DATABASE_URL:
        print("DATABASE_URL environment variable is not set.")
        return

    print(f"Connecting to Postgres... (URL length: {len(DATABASE_URL)})")
    
    try:
        uses_netloc.append("postgres")
        url = urlparse(DATABASE_URL)
        print(f"Parsed URL: scheme={url.scheme}, host={url.hostname}, port={url.port}")
    except Exception as e:
        print(f"Error parsing DATABASE_URL: {e}")
        return
    
    conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
    conn.autocommit = True
    cursor = conn.cursor()
    print("Direct connection established.")

    def create_table_with_optional_fks(table_name, with_fk_sql, without_fk_sql):
        """
        Legacy databases may not have unique constraints on referenced columns.
        If FK creation fails (pgcode 42830), create the table without FKs so migration can continue.
        """
        try:
            cursor.execute(with_fk_sql)
        except psycopg2.Error as e:
            if e.pgcode == "42830":  # invalid_foreign_key
                print(f"Warning: could not create {table_name} with foreign keys: {e}")
                print(f"Creating {table_name} without foreign keys.")
                cursor.execute(without_fk_sql)
            else:
                raise

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

    # Legacy environments may have users table created without a unique index/PK on user_id.
    # Try to enforce uniqueness for data integrity, but continue even if this cannot be applied.
    try:
        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_users_user_id_unique
            ON users (user_id)
        """)
    except Exception as e:
        print(f"Warning: could not ensure unique index on users.user_id: {e}")
        print("Continuing with existence-check inserts for users.")

    users = load_json("users.json")
    for user in users:
        cursor.execute("""
            INSERT INTO users (user_id, username, password, name, email, role, department, manager_id)
            SELECT %s, %s, %s, %s, %s, %s, %s, %s
            WHERE NOT EXISTS (
                SELECT 1 FROM users WHERE user_id = %s
            )
        """, (
            user["user_id"],
            user["username"],
            user["password"],
            user["name"],
            user["email"],
            user["role"],
            user.get("department"),
            user.get("manager_id"),
            user["user_id"]
        ))
    
    # 2. Leave Balances
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leave_balances (
            id SERIAL PRIMARY KEY,
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
    
    # ... Rest of tables ...
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

    try:
        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_training_courses_course_id_unique
            ON training_courses (course_id)
        """)
    except Exception as e:
        print(f"Warning: could not ensure unique index on training_courses.course_id: {e}")

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

    try:
        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_wellness_programs_program_id_unique
            ON wellness_programs (program_id)
        """)
    except Exception as e:
        print(f"Warning: could not ensure unique index on wellness_programs.program_id: {e}")

    # 9. Training Enrollments
    create_table_with_optional_fks(
        "training_enrollments",
        """
        CREATE TABLE IF NOT EXISTS training_enrollments (
            enrollment_id SERIAL PRIMARY KEY,
            user_id TEXT REFERENCES users(user_id),
            course_id TEXT REFERENCES training_courses(course_id),
            status TEXT DEFAULT 'enrolled',
            enrolled_at TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS training_enrollments (
            enrollment_id SERIAL PRIMARY KEY,
            user_id TEXT,
            course_id TEXT,
            status TEXT DEFAULT 'enrolled',
            enrolled_at TEXT
        )
        """
    )

    # 10. Wellness Registrations
    create_table_with_optional_fks(
        "wellness_registrations",
        """
        CREATE TABLE IF NOT EXISTS wellness_registrations (
            registration_id SERIAL PRIMARY KEY,
            user_id TEXT REFERENCES users(user_id),
            program_id TEXT REFERENCES wellness_programs(program_id),
            status TEXT DEFAULT 'registered',
            registered_at TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS wellness_registrations (
            registration_id SERIAL PRIMARY KEY,
            user_id TEXT,
            program_id TEXT,
            status TEXT DEFAULT 'registered',
            registered_at TEXT
        )
        """
    )

    # 11. Visitors (CREATE TABLE ONLY, NO DATA)
    create_table_with_optional_fks(
        "visitors",
        """
        CREATE TABLE IF NOT EXISTS visitors (
            visitor_id SERIAL PRIMARY KEY,
            host_id TEXT REFERENCES users(user_id),
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS visitors (
            visitor_id SERIAL PRIMARY KEY,
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    print("Created 'visitors' table if it didn't exist.")

    # SAFE DATA POPULATION (Restoring initial data if tables are empty)
    def populate_if_empty(table_name, json_file, insert_sql):
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        if count == 0:
            print(f"Populating {table_name} from {json_file}...")
            data = load_json(json_file)
            for item in data:
                try:
                    if table_name == "leave_balances":
                        # Special handling for leave balances to map JSON to flat columns
                        cursor.execute(insert_sql, (
                            item["user_id"], item["year"],
                            item.get("annual_leave", {}).get("total", 0), item.get("annual_leave", {}).get("remaining", 0),
                            item.get("medical_leave", {}).get("total", 0), item.get("medical_leave", {}).get("remaining", 0),
                            item.get("unpaid_leave", {}).get("total", 0), item.get("unpaid_leave", {}).get("remaining", 0),
                            item.get("compassionate_leave", {}).get("total", 0), item.get("compassionate_leave", {}).get("remaining", 0),
                            item.get("maternity_leave", {}).get("total", 0), item.get("maternity_leave", {}).get("remaining", 0),
                            item.get("paternity_leave", {}).get("total", 0), item.get("paternity_leave", {}).get("remaining", 0),
                            item.get("carry_forward_days", 0), item.get("carry_forward_expiry", "")
                        ))
                    elif table_name == "rooms":
                        features = item.get("features", item.get("facilities", []))
                        cursor.execute(insert_sql, (
                            item["room_id"], item["name"], item["capacity"], 
                            item.get("location", f"Floor {item.get('floor', 'Unknown')}"), 
                            json.dumps(features)
                        ))
                    elif table_name == "training_courses":
                        cursor.execute(insert_sql, (
                            item["course_id"], item["title"], item["description"], 
                            item["category"], item["instructor"], item["duration_hours"], 
                            item["max_participants"], item["status"], item["mandatory"],
                            json.dumps(item.get("schedule", []))
                        ))
                    elif table_name == "wellness_programs":
                        cursor.execute(insert_sql, (
                            item["program_id"], item["title"], item["description"], 
                            item["category"], item["location"], item["instructor"], 
                            item["max_participants"], item["status"],
                            json.dumps(item.get("schedule", []))
                        ))
                    else:
                        # Fallback for simple tables
                        vals = tuple(item.values())
                        cursor.execute(insert_sql, vals)
                except Exception as e:
                    print(f"Warning: Failed to insert item into {table_name}: {e}")
        else:
            print(f"Table {table_name} already has {count} rows, skipping initial population.")

    # Apply population for each table
    populate_if_empty("leave_balances", "leave_balances.json", """
        INSERT INTO leave_balances (
            user_id, year, 
            annual_total, annual_remaining, 
            medical_total, medical_remaining, 
            unpaid_total, unpaid_remaining,
            compassionate_total, compassionate_remaining,
            maternity_total, maternity_remaining,
            paternity_total, paternity_remaining,
            carry_forward_days, carry_forward_expiry
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """)

    populate_if_empty("rooms", "rooms.json", """
        INSERT INTO rooms (room_id, name, capacity, location, features_json)
        VALUES (%s, %s, %s, %s, %s)
    """)

    populate_if_empty("training_courses", "training_courses.json", """
        INSERT INTO training_courses (
            course_id, title, description, category, instructor, 
            duration_hours, max_participants, status, mandatory, schedule_json
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """)

    populate_if_empty("wellness_programs", "wellness_programs.json", """
        INSERT INTO wellness_programs (
            program_id, title, description, category, location, 
            instructor, max_participants, status, schedule_json
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """)

    print("Postgres Migration and population logic finished!")
    conn.close()

if __name__ == "__main__":
    migrate()
