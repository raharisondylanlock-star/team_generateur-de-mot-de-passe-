"""
Database module for user management
Wrapper around AuthService for compatibility
"""
import json
from pathlib import Path
# Lazy import to avoid circular import when security.auth_service imports database.*
# from security.auth_service import AuthService


# Initialize the auth service
_auth_service = None


def _get_auth_service():
    global _auth_service
    if _auth_service is None:
        from security.auth_service import AuthService
        _auth_service = AuthService()
    return _auth_service

_storage_path = Path(__file__).resolve().parent / "database" / "users.json"


def _load_users_db():
    """Load users database"""
    if not _storage_path.exists():
        return {}
    try:
        return json.loads(_storage_path.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        return {}


def get_user_by_username(username):
    """Get user by username"""
    username = username.strip()
    users = _load_users_db()
    
    if username not in users:
        return None
    
    return {
        'username': username,
        'password_hash': users[username]
    }


def add_user(username, password_hash, salt=None, role="user"):
    """Add a new user"""
    username = username.strip()
    
    users = _load_users_db()
    if username in users:
        return False
    
    # Store the full hash (salt:digest) as provided
    users[username] = password_hash
    
    try:
        _storage_path.write_text(json.dumps(users, indent=2, ensure_ascii=False), encoding='utf-8')
        return True
    except Exception as e:
        print(f"Error adding user: {e}")
        return False


def user_exists(username):
    """Check if user exists"""
    username = username.strip()
    users = _load_users_db()
    return username in users


def verify_password(username, password):
    """Verify user password"""
    return _get_auth_service().authenticate(username, password)



def change_user_password(username, old_password, new_password):
    """Change user password"""
    return _get_auth_service().change_password(username, old_password, new_password)

