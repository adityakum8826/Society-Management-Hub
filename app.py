"""
=============================================================================
Society Management HUB - ENTERPRISE ENTRY POINT
=============================================================================
UI: Original Dark Glassmorphism Design
Logic: Advanced Session Management, Maintenance Checks, & Secure Routing
=============================================================================
"""

import streamlit as st
import uuid
from datetime import datetime, timedelta
import time

import db
from core import auth
from roles.admin.admin_dashboard import render_admin_dashboard
from roles.manager.manager_dashboard import render_manager_dashboard
from roles.resident.resident_portal import render_resident_portal
from roles.guard.guard_dashboard import render_guard_dashboard


# ─────────────────────────────────────────────
#  CSS — dark glassmorphism, inspired by image 1
# ─────────────────────────────────────────────
def get_login_page_styles():
    return """
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

/* ── Full-page dark gradient background ── */
[data-testid="stAppViewContainer"] {
    background: radial-gradient(ellipse at 20% 50%, #1a1033 0%, #0a0a0f 40%, #0d0d1a 100%);
    min-height: 100vh;
    font-family: 'DM Sans', sans-serif;
}

/* hide default streamlit chrome */
[data-testid="stHeader"],
footer,
#MainMenu { display: none !important; }

/* ── Coloured blob accents (pure CSS) ── */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    top: -120px; left: -120px;
    width: 520px; height: 520px;
    background: radial-gradient(circle, rgba(120,60,220,.45) 0%, transparent 70%);
    filter: blur(60px);
    pointer-events: none; z-index: 0;
}
[data-testid="stAppViewContainer"]::after {
    content: '';
    position: fixed;
    bottom: -80px; right: -80px;
    width: 480px; height: 480px;
    background: radial-gradient(circle, rgba(255,100,60,.30) 0%, transparent 70%);
    filter: blur(70px);
    pointer-events: none; z-index: 0;
}

/* ── Top-left brand mark ── */
.brand-bar {
    position: fixed;
    top: 0; left: 0; right: 0;
    padding: 16px 28px;
    display: flex;
    align-items: center;
    gap: 10px;
    z-index: 100;
    background: rgba(255,255,255,.03);
    backdrop-filter: blur(8px);
    border-bottom: 1px solid rgba(255,255,255,.06);
}
.brand-bar .brand-icon { font-size: 22px; }
.brand-bar .brand-name {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 17px;
    color: #fff;
    letter-spacing: .5px;
}
.brand-bar .brand-sub {
    font-size: 11px;
    color: rgba(255,255,255,.35);
    margin-left: 4px;
    font-weight: 400;
}

/* ── Card wrapper ── */
div[data-testid="stTabs"] {
    background: rgba(255,255,255,.055);
    backdrop-filter: blur(28px) saturate(160%);
    -webkit-backdrop-filter: blur(28px) saturate(160%);
    border: 1px solid rgba(255,255,255,.12);
    border-radius: 22px;
    padding: 40px 36px 36px;
    max-width: 520px;
    margin: 88px auto 0;
    box-shadow:
        0 8px 40px rgba(0,0,0,.55),
        inset 0 1px 0 rgba(255,255,255,.10);
    position: relative;
    z-index: 10;
}

/* ── Tab toggle (Sign in / Sign up style) ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,.07) !important;
    border-radius: 50px !important;
    padding: 4px !important;
    gap: 0 !important;
    border: 1px solid rgba(255,255,255,.10) !important;
    width: fit-content !important;
    margin: 0 auto 28px !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: rgba(255,255,255,.5) !important;
    border-radius: 50px !important;
    padding: 8px 22px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    border: none !important;
    transition: all .25s ease !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(255,255,255,.15) !important;
    color: #fff !important;
    box-shadow: 0 2px 12px rgba(0,0,0,.3) !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }
.stTabs [data-baseweb="tab-border"]    { display: none !important; }

/* ── Section heading ── */
.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 24px;
    font-weight: 700;
    color: #fff;
    margin: 0 0 6px;
}
.section-sub {
    font-size: 13px;
    color: rgba(255,255,255,.4);
    margin: 0 0 24px;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background: rgba(255,255,255,.07) !important;
    border: 1px solid rgba(255,255,255,.12) !important;
    border-radius: 12px !important;
    color: #fff !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    padding: 12px 16px !important;
    transition: border .2s ease, box-shadow .2s ease !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: rgba(180,130,255,.5) !important;
    box-shadow: 0 0 0 3px rgba(150,80,255,.15) !important;
    outline: none !important;
}
.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder {
    color: rgba(255,255,255,.25) !important;
}
label { color: rgba(255,255,255,.7) !important; font-size: 13px !important; }

/* ── Primary button ── */
.stButton > button[kind="primary"],
.stFormSubmitButton > button[kind="primary"] {
    background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%) !important;
    border: none !important;
    border-radius: 12px !important;
    color: #fff !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 14px 0 !important;
    width: 100% !important;
    transition: transform .15s ease, box-shadow .15s ease !important;
    box-shadow: 0 4px 20px rgba(124,58,237,.45) !important;
    cursor: pointer !important;
}
.stButton > button[kind="primary"]:hover,
.stFormSubmitButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 28px rgba(124,58,237,.6) !important;
}

/* ── Checkbox ── */
.stCheckbox > label { color: rgba(255,255,255,.55) !important; font-size: 13px !important; }

/* ── Radio ── */
.stRadio > div { gap: 8px !important; }
.stRadio > div > label {
    background: rgba(255,255,255,.06) !important;
    border: 1px solid rgba(255,255,255,.10) !important;
    border-radius: 10px !important;
    padding: 8px 18px !important;
    color: rgba(255,255,255,.6) !important;
    font-size: 13px !important;
    cursor: pointer !important;
    transition: all .2s !important;
}

# /* ── Divider with "OR SIGN IN WITH" ── */
# .or-divider {
#     display: flex;
#     align-items: center;
#     gap: 12px;
#     margin: 22px 0 18px;
#     color: rgba(255,255,255,.3);
#     font-size: 11px;
#     letter-spacing: 1.5px;
#     text-transform: uppercase;
# }
# .or-divider::before,
# .or-divider::after {
#     content: '';
#     flex: 1;
#     height: 1px;
#     background: rgba(255,255,255,.1);
# }
# 
# /* ── Social buttons ── */
# .social-row { display: flex; gap: 12px; margin-bottom: 20px; }
# .social-btn {
#     flex: 1;
#     background: rgba(255,255,255,.07);
#     border: 1px solid rgba(255,255,255,.12);
#     border-radius: 12px;
#     padding: 13px;
#     cursor: pointer;
#     text-align: center;
#     font-size: 20px;
#     transition: background .2s ease, transform .15s ease;
#     color: #fff;
# }
# .social-btn:hover {
#     background: rgba(255,255,255,.13);
#     transform: translateY(-1px);
# }

/* ── Terms footnote ── */
.terms-note {
    text-align: center;
    font-size: 11px;
    color: rgba(255,255,255,.25);
    margin-top: 16px;
}
.terms-note a { color: rgba(200,160,255,.6); text-decoration: none; }

/* ── Badges ── */
.badge-row { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 20px; }
.badge {
    background: rgba(255,255,255,.07);
    border: 1px solid rgba(255,255,255,.12);
    border-radius: 50px;
    padding: 4px 12px;
    font-size: 11px;
    color: rgba(255,255,255,.5);
    letter-spacing: .3px;
}

/* success / error override */
.stAlert { border-radius: 10px !important; }

/* scrollbar */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,.12); border-radius: 4px; }
</style>
"""


# ─────────────────────────────────────────────
#  ADVANCED STATE & LOGIC HELPERS
# ─────────────────────────────────────────────
def init_session_state():
    """Initializes strictly needed global states to prevent resets."""
    defaults = {
        'user': None,
        'session_token': None,
        'logged_in': False,
        'session_data': None,
        'db_initialized': False
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def normalize_user_dict(user: dict) -> dict:
    """Ensures uniformity across the user dictionary structure."""
    if not user or not isinstance(user, dict):
        return {}
    if user.get('id') is None and user.get('user_id') is not None:
        user['id'] = user['user_id']
    user['role'] = str(user.get('role', 'RESIDENT')).upper()
    return user


def check_maintenance_mode(user_role: str) -> bool:
    """Returns True if the system is under maintenance and user is not an Admin."""
    try:
        is_maintenance = db.get_setting("maintenance_mode", "OFF") == "ON"
        if is_maintenance and user_role not in ["ADMIN", "SUPER_ADMIN"]:
            return True
    except Exception:
        pass
    return False


# ─────────────────────────────────────────────
#  MAIN UI RENDER FUNCTION
# ─────────────────────────────────────────────
def render_login_page():
    st.markdown(get_login_page_styles(), unsafe_allow_html=True)

    # ── Brand bar (top-left) ──────────────────────────
    st.markdown("""
    <div class="brand-bar">
        <span class="brand-icon">🏙️</span>
        <span class="brand-name">Society Management HUB</span>
        <span class="brand-sub">Society Portal</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Glass card wrapper ───────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["🔐  Sign In", "📝  Sign Up", "🔑  Forgot Password"])

    # ════════════════════════════════════════
    #  TAB 1 — SIGN IN
    # ════════════════════════════════════════
    with tab1:
        st.markdown('<p class="section-title">Welcome back</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-sub">Sign in to your Dashboard</p>', unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter username")
            password = st.text_input("Security Key", type="password", placeholder="Enter password")

            submit = st.form_submit_button("🚀  Sign In to Portal", type="primary", width="stretch")

            if submit:
                if not username or not password:
                    st.warning("❌ Please fill in both fields.")
                else:
                    # Authenticate via core auth layer
                    user = auth.login_user(username, password)

                    if user:
                        # 1. Advanced Status & Security Check
                        user_role = str(user.get("role", "")).upper()
                        user_status = str(user.get('status', 'ACTIVE')).upper()

                        if user_status not in ['ACTIVE', 'APPROVED']:
                            st.error("❌ Access Denied: Your account is suspended or pending approval.")
                        elif check_maintenance_mode(user_role):
                            st.error("🚧 System Under Maintenance: Only administrators can log in right now.")
                        else:
                            # 2. Secure Token Setup
                            token = str(uuid.uuid4())
                            expires_at = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')

                            # Log session to database if supported
                            try:
                                db.create_persistent_session(user.get('id'), token, expires_at)
                                db.log_action(user.get('id'), 'LOGIN', 'AUTH', "User authenticated.")
                            except Exception:
                                pass  # Graceful fallback if methods don't exist yet

                            # 3. Apply Local State
                            st.session_state.session_token = token
                            st.session_state.user = normalize_user_dict(user)
                            st.session_state.session_data = st.session_state.user
                            st.session_state.logged_in = True

                            st.query_params["session"] = token
                            st.success(f"✅  Welcome back, {user.get('full_name', username)}!")
                            time.sleep(0.5)
                            st.rerun()
                    else:
                        st.error("❌  Invalid username or password!")



    # ════════════════════════════════════════
    #  TAB 2 — SIGN UP
    # ════════════════════════════════════════
    with tab2:
        st.markdown('<p class="section-title">Create an account</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-sub">Join the Society Management HUB</p>', unsafe_allow_html=True)

        role = st.radio("Select your role", ["🏠  Resident", "🚔  Security Guard"], horizontal=True)
        user_role = "RESIDENT" if "Resident" in role else "GUARD"

        if user_role == "RESIDENT":
            with st.form("register_resident_form"):
                c1, c2 = st.columns(2)
                with c1:
                    first_name = st.text_input("First Name", placeholder="John")
                with c2:
                    last_name = st.text_input("Last Name", placeholder="Doe")
                full_name = f"{first_name} {last_name}".strip()

                username = st.text_input("Username", placeholder="Choose a unique username")
                email = st.text_input("Email", placeholder="you@example.com")

                c3, c4 = st.columns(2)
                with c3:
                    unit_number = st.text_input("Flat / Unit No.", placeholder="A-101")
                with c4:
                    contact = st.text_input("Phone", placeholder="+91 XXXXXXXXXX")

                password = st.text_input("Password", type="password", placeholder="Min 6 characters")
                confirm = st.text_input("Confirm Password", type="password")
                terms = st.checkbox("I agree to the Terms & Conditions")

                submit = st.form_submit_button("✅  Create Account", type="primary", width="stretch")

                if submit:
                    if not all([first_name, username, email, unit_number, password, confirm]):
                        st.error("Please fill in all required fields!")
                    elif password != confirm:
                        st.error("Passwords do not match!")
                    elif len(password) < 6:
                        st.error("Password must be at least 6 characters!")
                    elif not terms:
                        st.error("Please accept the Terms & Conditions!")
                    else:
                        if db.create_user(username, password, full_name, user_role, unit_number, contact, email):
                            st.success("🎉  Account created successfully! Please sign in.")
                        else:
                            st.error("❌  Failed to create account. Username may already exist.")

        else:  # GUARD
            with st.form("register_guard_form"):
                c1, c2 = st.columns(2)
                with c1:
                    full_name = st.text_input("Full Name", placeholder="Guard Name")
                with c2:
                    guard_id = st.text_input("Guard ID", placeholder="SG-001")

                email = st.text_input("Email", placeholder="guard@SMH.com")
                gate = st.text_input("Assigned Gate / Zone", placeholder="Main Gate, Block A")

                c3, c4 = st.columns(2)
                with c3:
                    contact = st.text_input("Phone", placeholder="+91 XXXXXXXXXX")
                with c4:
                    emp_id = st.text_input("Employee ID (optional)", placeholder="EMP-001")

                password = st.text_input("Password", type="password", placeholder="Min 6 characters")
                confirm = st.text_input("Confirm Password", type="password")
                terms = st.checkbox("I agree to the Terms & Conditions")

                submit = st.form_submit_button("✅  Register as Guard", type="primary", width="stretch")

                if submit:
                    if not all([full_name, guard_id, email, gate, password, confirm]):
                        st.error("Please fill in all required fields!")
                    elif password != confirm:
                        st.error("Passwords do not match!")
                    elif len(password) < 6:
                        st.error("Password must be at least 6 characters!")
                    elif not terms:
                        st.error("Please accept the Terms & Conditions!")
                    else:
                        if db.create_user(guard_id, password, full_name, user_role, None, contact, email):
                            st.success("🎉  Guard registered successfully! Please sign in.")
                        else:
                            st.error("❌  Failed to register guard. Guard ID may already exist.")


    # ════════════════════════════════════════
    #  TAB 3 — FORGOT PASSWORD
    # ════════════════════════════════════════
    with tab3:
        st.markdown('<p class="section-title">Reset your password</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-sub">Submit a request and our admin will assist you</p>', unsafe_allow_html=True)

        with st.form("forgot_password_form"):
            email_or_user = st.text_input("Username or Email", placeholder="Enter your username or email")
            reason = st.selectbox(
                "Reason for request",
                ["Forgot my password", "Account locked", "Suspected unauthorized access",
                 "Want to change password", "Other"]
            )
            notes = st.text_area("Additional Notes", placeholder="Any details that may help the admin...")

            submit = st.form_submit_button("📬  Submit Reset Request", type="primary", width="stretch")

            if submit:
                if not email_or_user:
                    st.warning("Please provide your username or email.")
                else:
                    try:
                        if hasattr(db, 'create_password_reset_request'):
                            db.create_password_reset_request(email_or_user, reason, notes)
                        st.success("✅  Request submitted! Admin will review and get back to you.")
                    except Exception as e:
                        st.error(f"Failed to submit: {e}")


# ─────────────────────────────────────────────
#  ROUTER & LIFECYCLE MANAGEMENT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    # 1. Page Config (Set to WIDE so Dashboards aren't squished)
    # The max-width CSS logic keeps the login screen perfectly centered regardless!
    st.set_page_config(
        page_title="Society Management HUB",
        page_icon="🏙️",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    init_session_state()

    # Init Database
    if not st.session_state.db_initialized:
        try:
            if hasattr(db, 'init_database'):
                db.init_database()
                db.upgrade_database_schema()
            st.session_state.db_initialized = True
        except Exception:
            pass

    # 2. Logout Handler
    if "logout" in st.query_params:
        if st.session_state.get('session_token'):
            try:
                db.delete_persistent_session(st.session_state.session_token)
            except Exception:
                pass
        for k in ["logged_in", "user", "session_token", "session_data"]:
            st.session_state.pop(k, None)
        st.query_params.clear()
        st.rerun()

    # 3. Session Restoration & Validation
    if not st.session_state.logged_in:
        token = st.query_params.get('session') or st.session_state.get('session_token')
        if token:
            try:
                session = db.get_session(token)
                if session:
                    user = db.get_user_by_id(session['user_id'])
                    if user and str(user.get('status', 'ACTIVE')).upper() in ['ACTIVE', 'APPROVED']:
                        if check_maintenance_mode(str(user.get('role')).upper()):
                            st.warning("🚧 System Under Maintenance. Try again later.")
                            st.query_params.clear()
                        else:
                            st.session_state.user = normalize_user_dict(user)
                            st.session_state.session_token = token
                            st.session_state.logged_in = True
                            st.session_state.session_data = st.session_state.user
                            st.query_params['session'] = token
                    else:
                        db.delete_persistent_session(token)
                        st.query_params.clear()
            except Exception:
                pass  # If db.get_session isn't implemented, fallback normally

    # 4. Global Maintenance Mode Enforcer
    if st.session_state.logged_in:
        role = str(st.session_state.user.get('role', 'RESIDENT')).upper()
        if check_maintenance_mode(role):
            st.error("🚨 Maintenance Mode Activated. You have been securely logged out.")
            st.session_state.clear()
            st.query_params.clear()
            time.sleep(1)
            st.rerun()

    # 5. Routing Engine
    if not st.session_state.logged_in:
        render_login_page()
    else:
        # Route to respective dashboard using session data
        user_data = st.session_state.session_data
        role = user_data.get("role", "").upper()

        if role in ["SUPER_ADMIN", "ADMIN"]:
            render_admin_dashboard(user_data)
        elif role == "MANAGER":
            render_manager_dashboard(user_data)
        elif role == "RESIDENT":
            render_resident_portal(user_data)
        elif role == "GUARD":
            render_guard_dashboard(user_data)
        else:
            st.error("❌ Access Denied: Unknown role configuration.")
            if st.button("Logout", type="primary"):
                st.query_params["logout"] = "1"
                st.rerun()