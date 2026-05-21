import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

import db


def login_user(username: str, password: str, remember_me: bool = False, ip_address: str = "Unknown") -> Optional[
    Dict[str, Any]]:
    """
    Validates credentials using bcrypt via the database layer and creates an audit log.
    """
    user = db.get_user_by_username(username)

    if user and db.verify_password(password, user.get('password_hash', '')):
        # Check if user is actually active before allowing login
        if str(user.get('status', 'ACTIVE')).upper() != 'ACTIVE':
            db.log_action(user.get('id'), 'LOGIN_FAILED', 'AUTH',
                          f"Inactive/Suspended account attempt from {ip_address}", username)
            return None

        db.log_action(user.get('id'), 'LOGIN_SUCCESS', 'AUTH', f"User logged in securely from {ip_address}", username)
        return user

    # Failed credentials
    db.log_action(None, 'LOGIN_FAILED', 'AUTH', f"Invalid credentials attempt from {ip_address}", username)
    return None


def create_persistent_session(user_id: int, remember_me: bool = False) -> str:
    """
    Generates a secure token and stores it in the database.
    """
    token = str(uuid.uuid4())
    days = 30 if remember_me else 1
    expires_at = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')

    db.create_persistent_session(user_id, token, expires_at)
    return token


def validate_session(token: str) -> Optional[Dict[str, Any]]:
    """
    Checks if a session token is valid and returns the associated active user.
    """
    session = db.get_session(token)
    if session and 'user_id' in session:
        user = db.get_user_by_id(session['user_id'])
        if user and str(user.get('status', '')).upper() == 'ACTIVE':
            return user
    return None


def logout_user(user_id: int, ip_address: str = "Unknown") -> None:
    """
    Logs the logout event.
    """
    if user_id:
        db.log_action(user_id, 'LOGOUT_SUCCESS', 'AUTH', f"User logged out from {ip_address}")


def check_permission(user_role: str, permission: str) -> bool:
    """
    Enterprise Role-Based Access Control (RBAC) permission checking.
    """
    user_role = str(user_role).upper()

    permissions = {
        'SUPER_ADMIN': ['*'],  # Has everything implicitly
        'ADMIN': [
            'dashboard_view', 'user_manage', 'user_create', 'user_update', 'user_delete',
            'complaint_manage', 'complaint_assign', 'complaint_escalate', 'finance_view',
            'finance_edit', 'finance_delete', 'invoice_generate', 'payment_verify',
            'payment_waive', 'notice_broadcast', 'notice_pin', 'notice_delete',
            'visitor_view', 'visitor_manage', 'visitor_blacklist', 'iot_control',
            'iot_view', 'iot_configure', 'reports_generate', 'reports_export',
            'amenity_manage', 'amenity_configure', 'settings_manage', 'backup_create', 'audit_view'
        ],
        'MANAGER': [
            'dashboard_view', 'user_manage', 'user_create', 'user_update',
            'complaint_manage', 'complaint_assign', 'finance_view',
            'invoice_generate', 'payment_verify', 'notice_broadcast', 'notice_pin',
            'visitor_view', 'visitor_manage', 'iot_view', 'reports_generate',

        ],
        'RESIDENT': [
            'dashboard_view', 'complaint_lodge', 'complaint_view_own', 'finance_view_own',
            'payment_make', 'notice_view', 'visitor_pre_approve', 'amenity_book', 'poll_vote', 'chat_access'
        ],
        'GUARD': [
            'dashboard_view', 'visitor_entry', 'visitor_exit', 'vehicle_log', 'panic_alert_trigger',
            'expected_visitor_view', 'fast_track_entry', 'parcel_log'
        ]
    }

    if user_role == 'SUPER_ADMIN':
        return True

    return permission in permissions.get(user_role, [])


def is_admin(user: dict) -> bool:
    """Check if the user has Admin or Super Admin privileges."""
    return user and str(user.get('role', '')).upper() in ['ADMIN', 'SUPER_ADMIN']


def is_manager_or_admin(user: dict) -> bool:
    """Check if the user has at least Manager level privileges."""
    return user and str(user.get('role', '')).upper() in ['ADMIN', 'SUPER_ADMIN', 'MANAGER']