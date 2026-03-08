"""User Management Module - Authentication and User Information"""
import json
import os
from typing import Optional, Dict, List

DATA_DIR = "data/mock_data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
ROLES_FILE = os.path.join(DATA_DIR, "roles.json")

def load_users() -> List[Dict]:
    """Load users from JSON file"""
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def load_roles() -> List[Dict]:
    """Load roles and permissions from JSON file"""
    with open(ROLES_FILE, 'r') as f:
        return json.load(f)

def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """
    Authenticate user with username and password
    Returns user data if successful, None otherwise
    """
    users = load_users()
    
    for user in users:
        if user['username'] == username and user['password'] == password:
            # Don't return password in response
            user_data = user.copy()
            del user_data['password']
            return user_data
    
    return None

def get_user_info(user_id: str) -> Optional[Dict]:
    """
    Get user information by user_id
    Returns user data without password
    """
    users = load_users()
    
    for user in users:
        if user['user_id'] == user_id:
            user_data = user.copy()
            del user_data['password']
            return user_data
    
    return None

def get_user_permissions(user_id: str) -> List[str]:
    """
    Get list of permissions for a user based on their role
    """
    user = get_user_info(user_id)
    if not user:
        return []
    
    roles = load_roles()
    user_role = user['role']
    
    for role in roles:
        if role['role'] == user_role:
            return role['permissions']
    
    return []

def has_permission(user_id: str, permission: str) -> bool:
    """
    Check if user has a specific permission
    """
    permissions = get_user_permissions(user_id)
    
    # Admin has all permissions
    if 'all' in permissions:
        return True
    
    return permission in permissions

def get_all_users() -> List[Dict]:
    """
    Get all users (without passwords)
    """
    users = load_users()
    return [{k: v for k, v in user.items() if k != 'password'} for user in users]

