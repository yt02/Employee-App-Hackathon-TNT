"""
Training Module
Handles training course viewing, enrollment, and completion tracking
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

# Get the project root directory (3 levels up from this file)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
COURSES_FILE = os.path.join(PROJECT_ROOT, 'data', 'mock_data', 'training_courses.json')
ENROLLMENTS_FILE = os.path.join(PROJECT_ROOT, 'data', 'mock_data', 'training_enrollments.json')

def load_courses() -> List[Dict]:
    """Load training courses from JSON file"""
    try:
        print(f"Loading courses from: {COURSES_FILE}")
        print(f"File exists: {os.path.exists(COURSES_FILE)}")
        with open(COURSES_FILE, 'r') as f:
            data = json.load(f)
            print(f"Loaded {len(data)} courses")
            return data
    except FileNotFoundError as e:
        print(f"File not found: {COURSES_FILE}")
        print(f"Error: {e}")
        return []
    except Exception as e:
        print(f"Error loading courses: {e}")
        return []

def load_enrollments() -> List[Dict]:
    """Load training enrollments from JSON file"""
    try:
        print(f"Loading enrollments from: {ENROLLMENTS_FILE}")
        print(f"File exists: {os.path.exists(ENROLLMENTS_FILE)}")
        with open(ENROLLMENTS_FILE, 'r') as f:
            data = json.load(f)
            print(f"Loaded {len(data)} enrollments")
            return data
    except FileNotFoundError as e:
        print(f"File not found: {ENROLLMENTS_FILE}")
        print(f"Error: {e}")
        return []
    except Exception as e:
        print(f"Error loading enrollments: {e}")
        return []

def save_enrollments(enrollments: List[Dict]):
    """Save training enrollments to JSON file"""
    with open(ENROLLMENTS_FILE, 'w') as f:
        json.dump(enrollments, f, indent=4)

def view_courses(category: Optional[str] = None, mandatory_only: bool = False) -> Dict:
    """View available training courses"""
    courses = load_courses()
    
    # Apply filters
    if category:
        courses = [c for c in courses if c['category'] == category]
    
    if mandatory_only:
        courses = [c for c in courses if c.get('mandatory', False)]
    
    return {
        "success": True,
        "data": courses
    }

def enroll_course(user_id: str, course_id: str, session_id: str) -> Dict:
    """Enroll user in a training course session"""
    courses = load_courses()
    enrollments = load_enrollments()
    
    # Find the course
    course = next((c for c in courses if c['course_id'] == course_id), None)
    if not course:
        return {"success": False, "message": "Course not found"}
    
    # Find the session
    session = next((s for s in course['schedule'] if s['session_id'] == session_id), None)
    if not session:
        return {"success": False, "message": "Session not found"}
    
    # Check if already enrolled
    existing_enrollment = next(
        (e for e in enrollments 
         if e['user_id'] == user_id 
         and e['course_id'] == course_id 
         and e['session_id'] == session_id
         and e['status'] != 'cancelled'),
        None
    )
    
    if existing_enrollment:
        return {"success": False, "message": "Already enrolled in this session"}
    
    # Check capacity
    if session['enrolled_count'] >= course['max_participants']:
        return {"success": False, "message": "Session is full"}
    
    # Create enrollment
    enrollment_id = f"ENR_{str(len(enrollments) + 1).zfill(3)}"
    
    new_enrollment = {
        "enrollment_id": enrollment_id,
        "user_id": user_id,
        "course_id": course_id,
        "session_id": session_id,
        "enrollment_date": datetime.now().isoformat(),
        "status": "enrolled",
        "completion_date": None,
        "certificate_issued": False
    }
    
    enrollments.append(new_enrollment)
    
    # Update enrolled count in session
    session['enrolled_count'] += 1
    
    save_enrollments(enrollments)
    
    # Save updated courses
    with open(COURSES_FILE, 'w') as f:
        json.dump(courses, f, indent=4)
    
    return {
        "success": True,
        "message": f"Successfully enrolled in {course['title']}",
        "data": new_enrollment
    }

def view_enrollments(user_id: str) -> Dict:
    """View user's course enrollments"""
    enrollments = load_enrollments()
    courses = load_courses()
    
    # Filter enrollments for this user
    user_enrollments = [e for e in enrollments if e['user_id'] == user_id]
    
    # Enrich with course information
    for enrollment in user_enrollments:
        course = next((c for c in courses if c['course_id'] == enrollment['course_id']), None)
        if course:
            enrollment['course_title'] = course['title']
            enrollment['course_category'] = course['category']
            enrollment['duration_hours'] = course['duration_hours']
            
            # Find session details
            session = next((s for s in course['schedule'] if s['session_id'] == enrollment['session_id']), None)
            if session:
                enrollment['session_date'] = session['date']
                enrollment['session_time'] = f"{session['start_time']} - {session['end_time']}"
                enrollment['location'] = session['location']
    
    return {
        "success": True,
        "data": user_enrollments
    }

def complete_course(enrollment_id: str, user_id: str) -> Dict:
    """Mark a course as completed"""
    enrollments = load_enrollments()
    
    for enrollment in enrollments:
        if enrollment['enrollment_id'] == enrollment_id:
            if enrollment['user_id'] != user_id:
                return {"success": False, "message": "Unauthorized"}
            
            if enrollment['status'] == 'completed':
                return {"success": False, "message": "Course already completed"}
            
            enrollment['status'] = 'completed'
            enrollment['completion_date'] = datetime.now().isoformat()
            enrollment['certificate_issued'] = True
            
            save_enrollments(enrollments)
            
            return {
                "success": True,
                "message": "Course marked as completed. Certificate issued!",
                "data": enrollment
            }
    
    return {"success": False, "message": "Enrollment not found"}

