import uuid
from datetime import datetime, date
from typing import Any, Optional, Union

import streamlit as st
import config
import db


def execute_query(query: str, params: tuple = None, commit: bool = False) -> Any:
    """Legacy wrapper for db.execute_query. Kept for backward compatibility."""
    return db.execute_query(query, params, commit=commit)


def format_currency(amount: Any) -> str:
    """Safely formats any number into a standard currency string."""
    symbol = getattr(config, 'CURRENCY_SYMBOL', '₹')
    if amount is None:
        return f"{symbol}0.00"
    try:
        return f"{symbol}{float(amount):,.2f}"
    except (ValueError, TypeError):
        return f"{symbol}0.00"


def _is_invalid_date(dt: Any) -> bool:
    """Internal helper to catch Pandas NaT and None values."""
    if dt is None:
        return True
    if str(dt).strip() in ['NaT', 'None', '']:
        return True
    return False


def format_date(dt: Any) -> str:
    if _is_invalid_date(dt):
        return 'N/A'
    if isinstance(dt, (date, datetime)):
        try:
            return dt.strftime('%d %b %Y')
        except Exception:
            return 'N/A'
    return str(dt)


def format_datetime(dt: Any) -> str:
    if _is_invalid_date(dt):
        return 'N/A'
    if isinstance(dt, datetime):
        try:
            return dt.strftime('%d %b %Y, %I:%M %p')
        except Exception:
            return 'N/A'
    return str(dt)


def format_time(dt: Any) -> str:
    if _is_invalid_date(dt):
        return 'N/A'
    if isinstance(dt, datetime):
        try:
            return dt.strftime('%I:%M %p')
        except Exception:
            return 'N/A'
    return str(dt)


def get_initials(name: Optional[str]) -> str:
    """Generates 2-letter uppercase initials from a full name."""
    if not name:
        return '??'
    parts = str(name).strip().split()
    if len(parts) >= 2:
        return f"{parts[0][0]}{parts[1][0]}".upper()
    return str(name)[:2].upper()


def get_current_shift() -> str:
    hour = datetime.now().hour
    if 6 <= hour < 14:
        return "Morning"
    elif 14 <= hour < 22:
        return "Evening"
    return "Night"


def get_shift_timing(shift_type: str) -> str:
    timings = {
        "Morning": "6:00 AM - 2:00 PM",
        "Evening": "2:00 PM - 10:00 PM",
        "Night": "10:00 PM - 6:00 AM"
    }
    return timings.get(str(shift_type), "")


def get_priority_color(priority: Optional[str]) -> str:
    if not priority: return '#94A3B8'
    colors = {
        'CRITICAL': '#E11D48',
        'EMERGENCY': '#E11D48',
        'URGENT': '#E11D48',
        'HIGH': '#F97316',
        'MEDIUM': '#EAB308',
        'LOW': '#10B981',
    }
    return colors.get(str(priority).upper(), '#94A3B8')


def get_status_color(status: Optional[str]) -> str:
    """Returns color codes for all standard DB statuses."""
    if not status: return '#94A3B8'
    colors = {
        # General & Tasks
        'PENDING': '#F59E0B',
        'IN_PROGRESS': '#8B5CF6',
        'COMPLETED': '#10B981',
        'RESOLVED': '#10B981',
        'FAILED': '#EF4444',
        'REJECTED': '#EF4444',
        'OVERDUE': '#F97316',
        'OPEN': '#3B82F6',

        # User Status
        'ACTIVE': '#10B981',
        'SUSPENDED': '#EF4444',
        'INACTIVE': '#6B7280',

        # Gate & Logistics
        'EXPECTED': '#8B5CF6',
        'INSIDE': '#3B82F6',
        'EXITED': '#10B981',
        'DENIED': '#EF4444',
        'AT_GATE': '#F59E0B',
        'DELIVERED': '#10B981',
        'VERIFIED': '#10B981'
    }
    return colors.get(str(status).upper(), '#94A3B8')


def get_role_badge_color(role: Optional[str]) -> str:
    """Returns color codes for RBAC roles."""
    if not role: return '#6B7280'
    colors = {
        'SUPER_ADMIN': '#4338CA',  # Indigo
        'ADMIN': '#8B5CF6',  # Violet
        'MANAGER': '#0EA5E9',  # Sky Blue
        'RESIDENT': '#10B981',  # Emerald
        'GUARD': '#F59E0B'  # Amber
    }
    return colors.get(str(role).upper(), '#6B7280')


def generate_invoice_number() -> str:
    return f"INV-{uuid.uuid4().hex[:12].upper()}"


def generate_transaction_id() -> str:
    return f"TXN-{uuid.uuid4().hex[:12].upper()}"


def generate_booking_id() -> str:
    return f"BKG-{uuid.uuid4().hex[:8].upper()}"


def generate_access_code() -> str:
    return uuid.uuid4().hex[:8].upper()


def validate_unit_number(unit: str) -> bool:
    if not unit: return False

    blocks = getattr(config, 'BLOCKS', [])
    floors = getattr(config, 'FLAT_FLOORS', 1)
    units_per_floor = getattr(config, 'FLAT_UNITS', 1)

    for block in blocks:
        for floor in range(1, floors + 1):
            for unit_num in range(1, units_per_floor + 1):
                if f"{block}-{floor:02d}{unit_num}" == str(unit):
                    return True
    return False


def get_unit_type_from_number(unit: Optional[str]) -> str:
    if not unit: return "Unknown"
    try:
        unit_num = int(str(unit).split('-')[-1])
        if unit_num <= 5:
            return "1BHK"
        elif unit_num <= 10:
            return "2BHK"
        elif unit_num <= 15:
            return "3BHK"
        elif unit_num <= 18:
            return "4BHK"
        else:
            return "Penthouse"
    except Exception:
        return "Unknown"


def calculate_late_fee(due_date: Union[str, date, datetime], amount: float) -> float:
    if not due_date: return 0.0

    try:
        if isinstance(due_date, str):
            due_date_obj = datetime.strptime(due_date, '%Y-%m-%d').date()
        elif isinstance(due_date, datetime):
            due_date_obj = due_date.date()
        else:
            due_date_obj = due_date

        days_overdue = (date.today() - due_date_obj).days
        fee_per_day = getattr(config, 'LATE_FEE_PER_DAY', 0.0)

        if days_overdue > 0:
            return float(days_overdue * fee_per_day)
    except Exception:
        pass

    return 0.0


def sanitize_input(text: Any) -> str:
    """Basic XSS prevention for UI rendering."""
    if not text:
        return ""
    return str(text).replace('<', '&lt;').replace('>', '&gt;')


def truncate_text(text: Any, length: int = 100) -> str:
    if not text:
        return ""
    text_str = str(text)
    if len(text_str) > length:
        return text_str[:length] + "..."
    return text_str