"""
Authentication module - compatibility layer
Uses the AuthService from security.auth_service for secure password handling
"""
from security.auth_service import AuthService
from database import get_user_by_username, add_user


def generate_salt():
    """Generate a random salt (handled by AuthService)"""
    import os
    return os.urandom(16).hex()


def hash_password(password, salt=None):
    """Hash a password using PBKDF2 with SHA256"""
    auth_service = AuthService()
    # This uses the internal _hash_password method
    return auth_service._hash_password(password)


def register_user(username, password, role="user"):
    """Register a new user with authentication"""
    auth_service = AuthService()
    return auth_service.register_user(username, password)


def verify_login(username, password):
    """Verify user login credentials"""
    auth_service = AuthService()
    if auth_service.authenticate(username, password):
        return get_user_by_username(username) or {"username": username}
    return None
