"""Leave Management Module"""
import json
from typing import Dict, List, Optional
from datetime import datetime
import uuid
from .db import get_db

LEAVE_DEFAULTS = {
    "annual_leave": {"total": 20, "remaining": 20, "used": 0},
    "medical_leave": {"total": 10, "remaining": 10, "used": 0},
    "unpaid_leave": {"total": 10, "remaining": 10, "used": 0},
    "compassionate_leave": {"total": 3, "remaining": 3, "used": 0},
    "maternity_leave": {"total": 60, "remaining": 60, "used": 0},
    "paternity_leave": {"total": 7, "remaining": 7, "used": 0},
}

LEAVE_ALIASES = {
    "annual_leave": ["annual_leave", "annual"],
    "medical_leave": ["medical_leave", "sick_leave", "sick"],
    "unpaid_leave": ["unpaid_leave", "personal_leave", "personal"],
    "compassionate_leave": ["compassionate_leave", "bereavement_leave"],
    "maternity_leave": ["maternity_leave"],
    "paternity_leave": ["paternity_leave"],
}


def _to_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _normalize_leave_blob(blob, fallback_total=0, fallback_remaining=0) -> Dict:
    """
    Normalize different leave data representations to a consistent structure:
    {"total": int, "remaining": int}
    """
    if isinstance(blob, dict):
        total = blob.get("total", blob.get("entitled", blob.get("quota", blob.get("allocated", fallback_total))))
        remaining = blob.get("remaining")
        if remaining is None:
            remaining = blob.get("balance", blob.get("available", blob.get("left")))
        if remaining is None:
            used = blob.get("used", blob.get("taken", blob.get("consumed", 0)))
            remaining = _to_int(total, fallback_total) - _to_int(used, 0)

        total_int = _to_int(total, fallback_total)
        remaining_int = _to_int(remaining, fallback_remaining)
        if total_int <= 0 and remaining_int > 0:
            total_int = remaining_int
        return {
            "total": total_int,
            "remaining": max(0, remaining_int),
        }

    if isinstance(blob, str):
        trimmed = blob.strip()
        if trimmed.startswith("{"):
            try:
                parsed = json.loads(trimmed)
                return _normalize_leave_blob(parsed, fallback_total, fallback_remaining)
            except (ValueError, TypeError):
                pass

        if trimmed.replace(".", "", 1).isdigit():
            parsed_num = _to_int(trimmed, fallback_remaining)
            return {
                "total": _to_int(fallback_total, parsed_num),
                "remaining": parsed_num,
            }

    if isinstance(blob, (int, float)):
        parsed_num = _to_int(blob, fallback_remaining)
        return {
            "total": _to_int(fallback_total, parsed_num),
            "remaining": parsed_num,
        }

    remaining_int = _to_int(fallback_remaining, 0)
    total_int = _to_int(fallback_total, remaining_int)
    if total_int <= 0 and remaining_int > 0:
        total_int = remaining_int
    return {
        "total": total_int,
        "remaining": max(0, remaining_int),
    }


def _first_present(row: Dict, keys: List[str]):
    for key in keys:
        if key in row and row.get(key) is not None:
            return row.get(key)
    return None


def parse_leave_data(row: Dict, leave_type: str) -> Dict:
    """Parse leave data from JSON/JSONB, numeric, or flat schemas."""
    aliases = LEAVE_ALIASES.get(leave_type, [leave_type])
    prefix_candidates = []
    for alias in aliases:
        if alias.endswith("_leave"):
            prefix_candidates.append(alias.replace("_leave", ""))
    prefix_candidates.append(leave_type.split("_")[0])

    fallback_total_keys = []
    fallback_remaining_keys = []
    for alias in aliases:
        fallback_total_keys.append(f"{alias}_total")
        fallback_remaining_keys.append(f"{alias}_remaining")
    for prefix in prefix_candidates:
        fallback_total_keys.append(f"{prefix}_total")
        fallback_remaining_keys.append(f"{prefix}_remaining")

    raw_blob = _first_present(row, aliases)
    fallback_total = _first_present(row, fallback_total_keys)
    fallback_remaining = _first_present(row, fallback_remaining_keys)
    if fallback_total is None:
        fallback_total = raw_blob if raw_blob is not None else 0
    if fallback_remaining is None:
        fallback_remaining = raw_blob if raw_blob is not None else 0
    return _normalize_leave_blob(raw_blob, fallback_total, fallback_remaining)


def _ensure_leave_balance_row(cursor, user_id: str, year: int) -> bool:
    """Create a default leave balance row when user/year data is missing."""
    year_value = str(year)
    cursor.execute("SELECT 1 FROM leave_balances WHERE user_id = ? AND year = ?", (user_id, year_value))
    if cursor.fetchone():
        return False

    json_defaults = {k: json.dumps(v) for k, v in LEAVE_DEFAULTS.items()}
    attempts = [
        (
            """
            INSERT INTO leave_balances (
                user_id, year,
                annual_leave, medical_leave, unpaid_leave,
                compassionate_leave, maternity_leave, paternity_leave,
                carry_forward_days, carry_forward_expiry
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id, year_value,
                json_defaults["annual_leave"], json_defaults["medical_leave"], json_defaults["unpaid_leave"],
                json_defaults["compassionate_leave"], json_defaults["maternity_leave"], json_defaults["paternity_leave"],
                0, "",
            ),
        ),
        (
            """
            INSERT INTO leave_balances (
                user_id, year,
                annual_total, annual_remaining,
                medical_total, medical_remaining,
                unpaid_total, unpaid_remaining,
                compassionate_total, compassionate_remaining,
                maternity_total, maternity_remaining,
                paternity_total, paternity_remaining,
                carry_forward_days, carry_forward_expiry
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id, year_value,
                LEAVE_DEFAULTS["annual_leave"]["total"], LEAVE_DEFAULTS["annual_leave"]["remaining"],
                LEAVE_DEFAULTS["medical_leave"]["total"], LEAVE_DEFAULTS["medical_leave"]["remaining"],
                LEAVE_DEFAULTS["unpaid_leave"]["total"], LEAVE_DEFAULTS["unpaid_leave"]["remaining"],
                LEAVE_DEFAULTS["compassionate_leave"]["total"], LEAVE_DEFAULTS["compassionate_leave"]["remaining"],
                LEAVE_DEFAULTS["maternity_leave"]["total"], LEAVE_DEFAULTS["maternity_leave"]["remaining"],
                LEAVE_DEFAULTS["paternity_leave"]["total"], LEAVE_DEFAULTS["paternity_leave"]["remaining"],
                0, "",
            ),
        ),
        (
            """
            INSERT INTO leave_balances (
                user_id, year, annual_leave, medical_leave, unpaid_leave
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                user_id, year_value,
                LEAVE_DEFAULTS["annual_leave"]["remaining"],
                LEAVE_DEFAULTS["medical_leave"]["remaining"],
                LEAVE_DEFAULTS["unpaid_leave"]["remaining"],
            ),
        ),
    ]

    for query, params in attempts:
        try:
            cursor.execute(query, params)
            return True
        except Exception:
            continue
    return False


def get_leave_balance(user_id: str) -> Optional[Dict]:
    """Get leave balance for a user"""
    current_year = str(datetime.now().year)

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM leave_balances WHERE user_id = ? AND year = ?", (user_id, current_year))
        balance_row = cursor.fetchone()

        if not balance_row:
            return None

        row = dict(balance_row)
        return {
            "user_id": row.get("user_id", user_id),
            "year": row.get("year", current_year),
            "annual_leave": parse_leave_data(row, "annual_leave"),
            "medical_leave": parse_leave_data(row, "medical_leave"),
            "unpaid_leave": parse_leave_data(row, "unpaid_leave"),
            "compassionate_leave": parse_leave_data(row, "compassionate_leave"),
            "maternity_leave": parse_leave_data(row, "maternity_leave"),
            "paternity_leave": parse_leave_data(row, "paternity_leave"),
            "carry_forward_days": _to_int(row.get("carry_forward_days", 0), 0),
            "carry_forward_expiry": row.get("carry_forward_expiry", ""),
        }


def calculate_days(start_date: str, end_date: str) -> int:
    """Calculate number of days between two dates (inclusive)."""
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    return (end - start).days + 1


def apply_leave(user_id: str, leave_type: str, start_date: str, end_date: str, reason: str = "") -> Dict:
    """
    Apply for leave
    Returns: {"success": bool, "message": str, "request_id": str}
    """
    valid_types = [
        "annual_leave",
        "medical_leave",
        "unpaid_leave",
        "compassionate_leave",
        "maternity_leave",
        "paternity_leave",
    ]
    if leave_type not in valid_types:
        return {
            "success": False,
            "message": f"Invalid leave type. Must be one of: {', '.join([t.replace('_', ' ') for t in valid_types])}",
        }

    try:
        days = calculate_days(start_date, end_date)
    except Exception as e:
        return {
            "success": False,
            "message": f"Invalid date format. Please use YYYY-MM-DD format. Error: {str(e)}",
        }

    balance = get_leave_balance(user_id)
    if not balance:
        return {
            "success": False,
            "message": "Leave balance not found for user",
        }

    if balance[leave_type]["remaining"] < days:
        return {
            "success": False,
            "message": (
                f"Insufficient {leave_type.replace('_', ' ')} balance. "
                f"You have {balance[leave_type]['remaining']} days remaining, but requested {days} days."
            ),
        }

    policy_note = ""
    if leave_type == "medical_leave":
        policy_note = "\n\nPolicy Reminder: Please ensure you submit your Medical Certificate (MC) to HR upon return."
    elif leave_type == "paternity_leave" and days > 7:
        return {
            "success": False,
            "message": f"Policy Violation: Paternity leave cannot exceed 7 days consecutively. You requested {days} days.",
        }

    request_id = f"LR{str(uuid.uuid4())[:8].upper()}"
    applied_date = datetime.now().strftime("%Y-%m-%d")
    current_year = str(datetime.now().year)

    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO leave_requests (
                request_id, user_id, leave_type, start_date, end_date,
                days, reason, status, applied_date, approved_by, approved_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', ?, NULL, NULL)
            """,
            (request_id, user_id, leave_type, start_date, end_date, days, reason, applied_date),
        )

        cursor.execute("SELECT * FROM leave_balances WHERE user_id = ? AND year = ?", (user_id, current_year))
        current_row = cursor.fetchone()
        if not current_row:
            raise Exception("Leave balance row disappeared during update")

        row_dict = dict(current_row)
        raw_leave_value = row_dict.get(leave_type)

        if isinstance(raw_leave_value, dict):
            data = dict(raw_leave_value)
            parsed = _normalize_leave_blob(data)
            data["remaining"] = parsed["remaining"] - days
            data["used"] = _to_int(data.get("used"), 0) + days
            cursor.execute(
                f"UPDATE leave_balances SET {leave_type} = ? WHERE user_id = ? AND year = ?",
                (json.dumps(data), user_id, current_year),
            )
        elif isinstance(raw_leave_value, str) and raw_leave_value.strip().startswith("{"):
            data = json.loads(raw_leave_value)
            parsed = _normalize_leave_blob(data)
            data["remaining"] = parsed["remaining"] - days
            data["used"] = _to_int(data.get("used"), 0) + days
            cursor.execute(
                f"UPDATE leave_balances SET {leave_type} = ? WHERE user_id = ? AND year = ?",
                (json.dumps(data), user_id, current_year),
            )
        else:
            new_remaining = balance[leave_type]["remaining"] - days
            prefix = leave_type.split("_")[0]
            col_name = f"{prefix}_remaining"
            if col_name in row_dict:
                cursor.execute(
                    f"UPDATE leave_balances SET {col_name} = ? WHERE user_id = ? AND year = ?",
                    (new_remaining, user_id, current_year),
                )
            elif leave_type in row_dict:
                cursor.execute(
                    f"UPDATE leave_balances SET {leave_type} = ? WHERE user_id = ? AND year = ?",
                    (new_remaining, user_id, current_year),
                )
            else:
                raise Exception(f"No compatible balance column found for {leave_type}")

        conn.commit()

    return {
        "success": True,
        "message": (
            f"Leave request submitted successfully! Request ID: {request_id}. "
            f"Your request for {days} day(s) of {leave_type.replace('_', ' ')} from {start_date} to {end_date} "
            f"is pending approval.{policy_note}"
        ),
        "request_id": request_id,
        "days": days,
    }


def get_leave_requests(user_id: str) -> List[Dict]:
    """Get all leave requests for a user"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM leave_requests WHERE user_id = ?", (user_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def check_leave_balance(user_id: str) -> Dict:
    """
    Check leave balance for a user
    Returns: {"success": bool, "message": str, "balance": dict}
    """
    balance = get_leave_balance(user_id)
    if not balance:
        return {
            "success": False,
            "message": "Leave balance not found for user",
        }

    message = (
        f"Your leave balance for {balance['year']}:\n\n"
        f"Annual Leave: {balance['annual_leave']['remaining']} days remaining (out of {balance['annual_leave']['total']})\n"
        f"Medical Leave: {balance['medical_leave']['remaining']} days remaining (out of {balance['medical_leave']['total']})\n"
        f"Unpaid Leave: {balance['unpaid_leave']['remaining']} days remaining"
    )

    if balance.get("carry_forward_days", 0) > 0:
        message += (
            f"\n\nYou also have {balance['carry_forward_days']} days of Carry Forward leave "
            f"that expires on {balance['carry_forward_expiry']}."
        )

    return {
        "success": True,
        "message": message,
        "balance": balance,
    }
