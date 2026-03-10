from app.tools import toolset, user_functions
from azure.ai.projects.models import RequiredFunctionToolCall

print("Functions dictionary:", user_functions._functions)

# Use dummy object
class DummyFunction:
    name = "check_leave_balance"
    arguments = '{"user_id": "emp_001"}'

class DummyAction:
    function = DummyFunction()
    id = "call_123"

action = DummyAction()

try:
    print("Executing check_leave_balance...")
    result = toolset.execute(action)
    print("Result:", result)
except Exception as e:
    import traceback
    traceback.print_exc()


