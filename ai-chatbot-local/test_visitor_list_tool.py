"""Test Visitor List Tool"""
import json
from app import tools

def test_visitor_list():
    print("Testing show_registered_visitors tool...")
    # This should return the visitor we registered in the previous test
    result_json = tools.show_registered_visitors("emp_001")
    result = json.loads(result_json)
    
    print(f"Result: {json.dumps(result, indent=2)}")
    
    if isinstance(result, list):
        print(f"PASS: Tool returned a list with {len(result)} visitors.")
    else:
        print("FAIL: Tool did not return a list.")

if __name__ == "__main__":
    test_visitor_list()
