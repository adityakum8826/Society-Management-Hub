import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple

import db

SESSION_COOKIE_NAME = "Society_Management_HUB_session"
COOKIE_MAX_AGE_DAYS = 7


def generate_session_token() -> str:
    """Generates a unique secure session token."""
    return str(uuid.uuid4())


def create_session_cookie(user_data: Dict[str, Any], remember_me: bool = False) -> Tuple[str, Dict[str, Any], int]:
    """
    Creates session data payload and calculates expiration.
    Returns: (token, session_data_dict, max_age_in_seconds)
    """
    token = generate_session_token()
    expires_days = COOKIE_MAX_AGE_DAYS if remember_me else 1

    expires_at = datetime.now() + timedelta(days=expires_days)

    session_data = {
        "token": token,
        "user_id": user_data.get("id"),
        "username": user_data.get("username"),
        "full_name": user_data.get("full_name"),
        "role": user_data.get("role"),
        "unit_number": user_data.get("unit_number"),
        "email": user_data.get("email"),
        "created_at": datetime.now().isoformat(),
        "expires_at": expires_at.isoformat()
    }

    # Return max_age in seconds
    return token, session_data, expires_days * 24 * 60 * 60


def validate_session_cookie(session_data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Validates if the provided session data dictionary is still valid (not expired).
    """
    if not session_data:
        return None

    try:
        expires_at_str = session_data.get("expires_at", "")

        # Handle both isoformat strings and actual datetime objects gracefully
        if isinstance(expires_at_str, datetime):
            expires_at = expires_at_str
        else:
            expires_at = datetime.fromisoformat(expires_at_str)

        if expires_at < datetime.now():
            return None

        return {
            "id": session_data.get("user_id"),
            "username": session_data.get("username"),
            "full_name": session_data.get("full_name"),
            "role": session_data.get("role"),
            "unit_number": session_data.get("unit_number"),
            "email": session_data.get("email")
        }
    except Exception as e:
        print(f"Session validation error: {e}")
        return None


def get_session_from_db(token: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves the persistent session from the database and fetches the associated live user data.
    """
    try:
        session = db.get_session(token)
        if session and 'user_id' in session:
            # Fetch user to ensure we have the latest details and check if they are active
            user = db.get_user_by_id(session['user_id'])

            if user and str(user.get('status', 'ACTIVE')).upper() == 'ACTIVE':
                return {
                    "token": session.get("token"),
                    "user_id": user.get("id"),
                    "username": user.get("username"),
                    "full_name": user.get("full_name"),
                    "role": user.get("role"),
                    "unit_number": user.get("unit_number"),
                    "email": user.get("email"),
                    "expires_at": session.get("expires_at")
                }
    except Exception as e:
        print(f"Error fetching session from DB: {e}")

    return None


def get_session_from_cookies() -> Optional[Dict[str, Any]]:
    """
    Attempts to retrieve and validate the session directly from the browser's cookies.
    Compatible with Streamlit 1.35+.
    """
    try:
        import streamlit as st

        # Modern Streamlit approach (1.38+)
        if hasattr(st, "context") and hasattr(st.context, "cookies"):
            token = st.context.cookies.get(SESSION_COOKIE_NAME)
            if token:
                session_data = get_session_from_db(token)
                return validate_session_cookie(session_data)

        # Fallback for slightly older Streamlit versions using headers
        elif hasattr(st, "context") and hasattr(st.context, "headers"):
            cookies = st.context.headers.get("Cookie", "")
            for cookie in cookies.split(";"):
                cookie = cookie.strip()
                if cookie.startswith(f"{SESSION_COOKIE_NAME}="):
                    token = cookie.split("=")[1]
                    session_data = get_session_from_db(token)
                    return validate_session_cookie(session_data)

    except Exception as e:
        print(f"Cookie parsing warning (safe to ignore in dev environment): {e}")

    return None