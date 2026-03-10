"""Test Visitor Persistence"""
import os
import json
from app.modules import visitor_manager

def test_registration():
    print("Testing Visitor Registration...")
    result = visitor_manager.register_visitor(
        host_id="emp_001",
        visitor_name="Test Visitor",
        visitor_ic="990101-10-1234",
        company="Test Corp",
        date="2026-03-10",
        time="14:00",
        purpose="Meeting",
        looking_for="HR Department"
    )
    print(f"Result: {json.dumps(result, indent=2)}")
    
    if result["success"]:
        print("Fetching visitors for emp_001...")
        visitors = visitor_manager.get_user_visitors("emp_001")
        print(f"Found {len(visitors)} visitors.")
        for v in visitors:
            print(f"- {v['visitor_name']} ({v['date']} {v['time']})")

if __name__ == "__main__":
    # Ensure we use local SQLite if DATABASE_URL is not set for this test
    test_registration()
