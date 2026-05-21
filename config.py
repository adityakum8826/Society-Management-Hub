import os
from pathlib import Path
from dotenv import load_dotenv  
load_dotenv()
BASE_DIR = Path(__file__).parent.absolute()

# ==========================================
# CORE SETTINGS
# ==========================================
APP_NAME = "Society Management HUB"
APP_VERSION = "8.6.0-Titanium-Live-SOC" # Version bumped to reflect Manager integration
SUPPORT_PHONE = "+91-xxxxxxxxxx"
SUPPORT_EMAIL = "support@SocietyManagementHUB.com"
MAX_UPLOAD_SIZE_MB = 50
DEMO_MODE = False

# ==========================================
# DIRECTORY STRUCTURE
# ==========================================
DATA_DIR = BASE_DIR / "data_backups"
LOGS_DIR = BASE_DIR / "logs"
ASSETS_DIR = BASE_DIR / "assets"
UPLOADS_DIR = BASE_DIR / "uploads"
BACKUP_DIR = BASE_DIR / "backups"
MODELS_DIR = BASE_DIR / "models"
EXPORTS_DIR = BASE_DIR / "exports"
CERT_DIR = BASE_DIR / "certs"
AI_CACHE_DIR = BASE_DIR / "ai_cache"
MEDIA_DIR = BASE_DIR / "media"
STATIC_DIR = BASE_DIR / "static"
TEMP_DIR = BASE_DIR / "temp"

# Auto-create directories if they don't exist
for dir_path in [DATA_DIR, LOGS_DIR, ASSETS_DIR, UPLOADS_DIR, BACKUP_DIR, MODELS_DIR, EXPORTS_DIR, CERT_DIR, AI_CACHE_DIR, MEDIA_DIR, STATIC_DIR, TEMP_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# ==========================================
# DATABASE CONFIGURATION (Cloud + Local Seamless)
# ==========================================
try:
    import streamlit as st
    # Check if we are running on Streamlit Cloud by looking for st.secrets
    if "mysql" in st.secrets:
        MYSQL_CONFIG = {
            "host": st.secrets["mysql"]["host"],
            "port": int(st.secrets["mysql"]["port"]),
            "user": st.secrets["mysql"]["user"],
            "password": st.secrets["mysql"]["password"],
            "database": st.secrets["mysql"]["database"],
            "charset": "utf8mb4",
            "pool_size": 20,
            "pool_recycle": 3600,
            "autocommit": True,
            "auth_plugin": "mysql_native_password",
            "ssl_verify_identity": True,  # Required for TiDB Serverless
            "ssl_verify_cert": True       # Required for TiDB Serverless
        }
    else:
        raise KeyError("No Streamlit secrets found, falling back to local config.")
except (ImportError, KeyError, FileNotFoundError):
    # Fallback for local testing (using your .env or local MySQL)
    MYSQL_CONFIG = {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("MYSQL_PORT", 3307)),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", "DB_PASSWORD"),
        "database": os.getenv("MYSQL_DATABASE", "Society_Management_HUB"),
        "charset": "utf8mb4",
        "pool_size": 20,
        "pool_recycle": 3600,
        "autocommit": True,
        "auth_plugin": "mysql_native_password"
    }

REDIS_CONFIG = {
    "host": os.getenv("REDIS_HOST", "localhost"),
    "port": int(os.getenv("REDIS_PORT", 6379)),
    "db": 0,
    "enabled": False
}

CACHE_CONFIG = {
    "TTL_DASHBOARD": 300,
    "TTL_USER_SESSION": 86400,
    "TTL_VISITOR_CHECK": 60,
    "TTL_COMPLAINT_STATS": 120
}

# ==========================================
# SECURITY & AUTHENTICATION
# ==========================================
PASSWORD_HASH_ALGO = "bcrypt"
BCRYPT_ROUNDS = 12
SESSION_TIMEOUT_HOURS = 24
MAX_LOGIN_ATTEMPTS = 5
PASSWORD_MIN_LENGTH = 8

SYSTEM_ROLES = ["SUPER_ADMIN", "ADMIN", "MANAGER", "RESIDENT", "GUARD"]

# ==========================================
# SOCIETY ARCHITECTURE
# ==========================================
BUILDING_ID = "Society Management HUB-001-TITANIUM"
TOTAL_BLOCKS = 5
TOTAL_FLOORS = 20
TOTAL_UNITS = 500
BLOCKS = ["A", "B", "C", "D", "E"]
UNIT_TYPES = ["1BHK", "2BHK", "3BHK", "4BHK", "Penthouse"]
FLAT_BLOCKS = ["A", "B", "C", "D", "E"]
FLAT_FLOORS = 20
FLAT_UNITS = 5

# ==========================================
# BILLING & FINANCIALS
# ==========================================
CURRENCY = "INR"
CURRENCY_SYMBOL = "₹"
MAINTENANCE_BASE_RATE = 3.50
LATE_FEE_PER_DAY = 50
GST_RATE = 18
INVOICE_DUE_DAY = 10
PAYMENT_TYPES = ["Maintenance", "Parking", "Clubhouse", "Event", "Penalty", "Other"]

# ==========================================
# HELPDESK & TICKETING
# ==========================================
COMPLAINT_CATEGORIES = [
    "Plumbing", "Electrical", "Carpentry", "Housekeeping", "Security",
    "Elevator", "Landscaping", "Pest Control", "Civil/Masonry",
    "App/IT Issue", "Neighbor Dispute", "Parking", "Water Supply",
    "Noise Complaint", "Other"
]

COMPLAINT_STATUS = {
    "Pending": {"color": "yellow", "icon": "⏸️"},
    "In Progress": {"color": "blue", "icon": "🔄"},
    "Resolved": {"color": "green", "icon": "✅"},
    "Rejected": {"color": "red", "icon": "❌"},
    "On Hold": {"color": "gray", "icon": "⏸️"},
    "Escalated": {"color": "purple", "icon": "📈"}
}

COMPLAINT_PRIORITY = {
    "Critical": {"color": "red", "sla_hours": 2, "escalation": "Manager → Admin"},
    "High": {"color": "orange", "sla_hours": 12, "escalation": "FacilityHead → Manager"},
    "Medium": {"color": "yellow", "sla_hours": 48, "escalation": "Technician → FacilityHead"},
    "Low": {"color": "green", "sla_hours": 120, "escalation": "Technician → FacilityHead"}
}

# ==========================================
# EMERGENCY & SECURITY PROTOCOLS
# ==========================================
EMERGENCY_ALERT_TYPES = ["MEDICAL", "FIRE", "SECURITY", "BREAK_IN"]

DEFAULT_EMERGENCY_CONTACTS = [
    {"service_name": "Police Control Room", "phone_number": "100", "description": "Security emergency"},
    {"service_name": "Fire Brigade", "phone_number": "101", "description": "Fire emergency"},
    {"service_name": "Ambulance Services", "phone_number": "102", "description": "Medical emergency"},
    {"service_name": "Society Admin", "phone_number": "Ext 101", "description": "Society administration"},
    {"service_name": "Electricity Dept", "phone_number": "19122", "description": "Power supply issues"},
    {"service_name": "Water Supply", "phone_number": "1916", "description": "Water supply issues"}
]

SECURITY_SOPS = [
    {"title": "Visitor Registration Protocol", "content": "All visitors must register at the gate with valid ID. Gate pass must be issued and visitor escorted to destination."},
    {"title": "Vehicle Entry Protocol", "content": "Verify vehicle against whitelist. Record entry time. Issue parking token if required."},
    {"title": "Fire Emergency Response", "content": "1. Alert all residents 2. Call fire brigade 3. Use fire extinguishers 4. Evacuate building 5. Account for all residents"},
    {"title": "Medical Emergency Response", "content": "1. Call ambulance immediately 2. Provide first aid 3. Contact resident family 4. Maintain crowd control 5. Guide ambulance"},
    {"title": "Shift Change Protocol", "content": "Complete shift handover report. Brief incoming guard on active incidents. Verify equipment and inventory."},
    {"title": "Patrol Rounds Protocol", "content": "Conduct hourly patrols of all designated areas. Check for suspicious activities. Log patrol completion."}
]

VISITOR_PURPOSES = ["Guest", "Delivery", "Service", "Official", "Family", "Event", "Interview", "Other"]
VEHICLE_TYPES = ["Car", "Bike", "Scooter", "Commercial", "Cab/Taxi", "Other"]
COURIER_SERVICES = ["Amazon", "Flipkart", "Myntra", "DTDC", "FedEx", "BlueDart", "Delhivery", "Swiggy/Zomato", "Other"]
SHIFT_TYPES = ["Morning", "Evening", "Night"]
PATROL_ZONES = ["Main Entrance", "Parking Area A", "Parking Area B", "Garden", "Block A", "Block B", "Block C"]

# ==========================================
# ENTERPRISE FEATURE FLAGS
# ==========================================
ENABLE_AI_CHATBOT = True
ENABLE_PAYMENT_GATEWAY = False
ENABLE_FACIAL_RECOGNITION = False
ENABLE_ANPR_CAMERAS = False
ENABLE_WHATSAPP_ALERTS = True
ENABLE_EMAIL_ALERTS = True
ENABLE_PUSH_NOTIFICATIONS = True
ENABLE_IVR_CALLS = False
STRICT_RBAC_ENFORCEMENT = True
MOCK_DB_FALLBACK = True
PREDICTIVE_MAINTENANCE_AI = True
BLOCKCHAIN_LEDGER_BACKUP = False
DYNAMIC_PRICING_AMENITIES = True
QR_GATE_PASS = True

# ==========================================
# UI THEME
# ==========================================
THEME = {
    "name": "TITANIUM_DARK",
    "background": "#080B10",
    "card_background": "rgba(18, 23, 33, 0.75)",
    "text_primary": "#F8FAFC",
    "text_secondary": "#94A3B8",
    "accent_primary": "#6366F1",
    "accent_secondary": "#06B6D4",
    "danger": "#E11D48",
    "success": "#10B981",
    "warning": "#F59E0B",
    "border_color": "rgba(255, 255, 255, 0.1)",
    "sidebar_background": "#0F172A"
}

# ==========================================
# DEFAULT SYSTEM USERS (Seed Data)
# ==========================================
DEFAULT_USERS = [
    {"username": "Main_Admin001", "password": "admin@123", "role": "ADMIN", "full_name": "System Administrator", "unit_number": None},
    {"username": "Mgr_001", "password": "manager@123", "role": "MANAGER", "full_name": "Society Manager", "unit_number": "Office-1"},
    {"username": "RES-1001", "password": "Test@123", "role": "RESIDENT", "full_name": "John Resident", "unit_number": "A-101"},
    {"username": "SG-101", "password": "Test@123", "role": "GUARD", "full_name": "Security Guard", "unit_number": None}
]