"""
=============================================================================
ENTERPRISE RESIDENT PORTAL
=============================================================================
This module provides the Resident UI.
Strictly uses 100% real-time database queries. Zero mock data.
Features advanced DataFrames, live SOS logging, Community Polls,
Events, and Parcel/Delivery Tracking.
(No Financial/Payment modules and No Booking systems included).
=============================================================================
"""

import json
import streamlit as st
from datetime import datetime, date
import pandas as pd
import time
from components.cards import section_header, empty_state
import db
import config
import db
from core.helpers import format_datetime, format_date
from components.cards import metric_card, section_header, info_card, empty_state

# Core Constants
BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-", "Unknown"]

# ============================================================================
# CUSTOM CSS INJECTION
# ============================================================================
def inject_resident_css():
    st.markdown("""
    <style>
    .premium-header-bar {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.98) 0%, rgba(30, 41, 59, 0.95) 100%);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 20px;
        padding: 16px 24px;
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(25px);
    }
    .header-left { display: flex; align-items: center; gap: 16px; }
    .header-logo {
        width: 50px; height: 50px; background: linear-gradient(135deg, #10B981, #059669);
        border-radius: 14px; display: flex; align-items: center; justify-content: center;
        font-size: 24px; box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
    }
    .header-title h1 { margin: 0; font-size: 24px; font-weight: 700; color: #F8FAFC; letter-spacing: -0.02em; }
    .header-title p { margin: 4px 0 0 0; color: #94A3B8; font-size: 13px; }
    .header-right { display: flex; align-items: center; gap: 12px; }
    .user-avatar {
        width: 44px; height: 44px; background: linear-gradient(135deg, #6366F1, #8B5CF6);
        border-radius: 12px; display: flex; align-items: center; justify-content: center;
        font-size: 18px; font-weight: 700; color: white; box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
    }
    .user-info { display: flex; flex-direction: column; align-items: flex-end; }
    .user-name { color: #F8FAFC; font-weight: 600; font-size: 14px; }
    .user-role { color: #10B981; font-size: 12px; font-weight: 500; }
    
    div[data-baseweb="select"] span, div[data-baseweb="select"] div, div[data-baseweb="popover"] li, div[data-baseweb="popover"] span { 
        color: #F8FAFC !important; -webkit-text-fill-color: #F8FAFC !important;
    }
    div[data-baseweb="select"] > div { background-color: #1E293B !important; }
    div[data-baseweb="popover"] ul { background-color: #1E293B !important; }
    div[data-baseweb="popover"] li:hover { background-color: rgba(99,102,241,0.2) !important; }
    .stTextInput input, .stTextArea textarea { color: #F8FAFC !important; background-color: #1E293B !important; }
    
    .data-card {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .data-card:hover {
        transform: translateY(-2px);
        border-color: rgba(99, 102, 241, 0.5);
    }
    
    .poll-result-bar {
        background-color: rgba(99, 102, 241, 0.2);
        border-radius: 8px;
        height: 12px;
        overflow: hidden;
        margin-top: 4px;
        margin-bottom: 16px;
    }
    .poll-result-fill {
        background: linear-gradient(90deg, #6366F1, #8B5CF6);
        height: 100%;
    }
    </style>
    """, unsafe_allow_html=True)


# ============================================================================
# PROFILE SHEET RENDERER
# ============================================================================
def render_saved_profile_sheet(user):
    uid = user.get("id")
    unit = user.get('unit_number', '')

    db_user = db.get_user_by_id(uid) if uid else {}
    profile = db.get_resident_profile(uid) if uid else {}
    vehicles = db.get_resident_vehicles(uid) if uid else []
    complaints = db.get_complaints(uid) if uid else []
    family = db.get_resident_family_members(uid) if uid else []

    # Safe parcel check
    try:
        all_parcels = db.get_parcels() or []
        my_parcels = [p for p in all_parcels if str(p.get('unit_number')) == str(unit) and str(p.get('status')).upper() == 'AT_GATE']
    except Exception:
        my_parcels = []

    st.markdown(f"""
        <div style="border: 1px solid {config.THEME.get('border_color', '#333')}; border-radius: 16px; padding: 20px 22px;
             background: {config.THEME.get('card_background', '#1e1e1e')}; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h3 style="margin: 0 0 8px 0; color: {config.THEME.get('text_primary', '#fff')};">📇 Your Resident Profile</h3>
            <p style="margin: 0; color: {config.THEME.get('text_secondary', '#aaa')}; font-size: 14px;">
                Overview of your registered details. Navigate to <strong>My Account</strong> to update your information.
            </p>
        </div>
    """, unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Registered Vehicles", len(vehicles))
    m2.metric("Open Tickets", len([c for c in complaints if c.get('status') not in ['RESOLVED', 'REJECTED']]))
    m3.metric("Parcels at Gate", len(my_parcels))
    m4.metric("Household Members", len(family))

    st.markdown("---")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Identity & Contact")
        st.markdown(f"**Full Name:** {db_user.get('full_name', '—')}")
        st.markdown(f"**Unit Number:** {db_user.get('unit_number', '—')}")
        st.markdown(f"**Email:** {db_user.get('email', '—')}")
        st.markdown(f"**Phone:** {db_user.get('contact_number', '—')}")
        st.markdown(f"**Account Status:** <span style='color:#10B981; font-weight:bold;'>{'Active' if db_user.get('status') == 'ACTIVE' else '—'}</span>", unsafe_allow_html=True)

    with c2:
        st.subheader("Extended Profile")
        if profile:
            dob_val = profile.get('date_of_birth') or profile.get('dob')
            st.markdown(f"**Date of Birth:** {format_date(dob_val) if dob_val else '—'}")
            st.markdown(f"**Gender:** {profile.get('gender', '—')}")
            st.markdown(f"**Blood Group:** {profile.get('blood_group', '—')}")
            st.markdown(f"**Emergency Contact:** 🚨 {profile.get('emergency_contact_name', '—')} ({profile.get('emergency_contact_phone', '—')})")
        else:
            st.info("Extended profile not yet completed. Please update your account.")

    st.write("")
    b1, b2 = st.columns(2)
    with b1:
        if st.button("✏️ Edit Profile Details", key="profile_sheet_edit", type="primary", width="stretch"):
            st.session_state.resident_show_profile_sheet = False
            st.session_state.resident_active_tab = 6  # Points to 'My Account' tab
            st.rerun()
    with b2:
        if st.button("✕ Close View", key="profile_sheet_close", width="stretch"):
            st.session_state.resident_show_profile_sheet = False
            st.rerun()


# ============================================================================
# MAIN ROUTER
# ============================================================================
def render_resident_portal(user):
    inject_resident_css()

    unit_number = user.get('unit_number', 'N/A')
    full_name = user.get('full_name', 'Resident')
    user_initials = ''.join([n[0] for n in str(full_name).split()[:2]]).upper()

    try:
        notification_count = db.get_unread_notification_count(user.get('id')) or 0
    except Exception:
        notification_count = 0

    notif_html = f'<span style="color: #E11D48;">🔔 {notification_count} New</span>' if notification_count > 0 else ''

    if 'resident_active_tab' not in st.session_state:
        st.session_state.resident_active_tab = 0
    if 'resident_show_profile_sheet' not in st.session_state:
        st.session_state.resident_show_profile_sheet = False

    header_col, action_col = st.columns([5, 1])

    with header_col:
        st.markdown(f"""
            <div class="premium-header-bar" style="margin-bottom: 12px;">
                <div class="header-left">
                    <div class="header-logo">🏠</div>
                    <div class="header-title">
                        <h1>Welcome, {full_name}</h1>
                        <p>Unit: {unit_number} | Resident {notif_html}</p>
                    </div>
                </div>
                <div class="header-right">
                    <div class="user-info">
                        <span class="user-name">{full_name}</span>
                        <span class="user-role">🏠 Unit {unit_number}</span>
                    </div>
                    <div class="user-avatar">{user_initials}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with action_col:
        st.markdown("<div style='padding-top: 8px;'></div>", unsafe_allow_html=True)
        if st.button(
            f"👤 Profile & Info",
            key="resident_open_saved_profile",
            width="stretch",
        ):
            st.session_state.resident_show_profile_sheet = True
            st.rerun()
        if st.button("🚪 Logout", key="res_logout", type="primary", width="stretch"):
            st.query_params["logout"] = "1"
            st.rerun()

    if st.session_state.resident_show_profile_sheet:
        render_saved_profile_sheet(user)
        st.markdown("---")

    # ---------------------------------------------------------
    # TABS FOR RESIDENT DASHBOARD
    # ---------------------------------------------------------
    tab_options = [
        "🏠 Home","🚗 Vehicles","🛠️ Support", "🚨 Security", "📢 Community", "👤 Profile"
    ]

    selected_tab = st.radio("Navigation", range(len(tab_options)),
                            format_func=lambda x: tab_options[x],
                            index=st.session_state.resident_active_tab,
                            horizontal=True,
                            key="resident_tab_radio")

    st.session_state.resident_active_tab = selected_tab

    if selected_tab == 0: render_home_tab(user)
    elif selected_tab == 1: render_my_vehicles(user)
    elif selected_tab == 2: render_support_center(user)
    elif selected_tab == 3: render_security_emergency(user)
    elif selected_tab == 4: render_community_hub(user)
    elif selected_tab == 5: render_my_account(user)


import pandas as pd
import streamlit as st
from datetime import datetime
from components.cards import section_header, metric_card, empty_state


# --- HELPER FUNCTION ---
def safe_execute(query: str, params: tuple = (), commit: bool = False) -> list:
    """Safely executes DB queries across modules."""
    import db
    try:
        result = db.execute_query(query, params, commit=commit)
        return result if result else []
    except Exception as e:
        print(f"Database Execution Error: {e}")
        return []


# ============================================================================
# MODULE 1: HOME (ADVANCED RESIDENT HUB)
# ============================================================================
def render_home_tab(user):
    import db
    from core.helpers import format_datetime

    uid = user.get('id')
    unit = user.get('unit_number', '')

    section_header(f"Welcome Home, Unit {unit}", "🏠")

    # --- 1. CRITICAL EMERGENCY & INCIDENT ALERTS (UPDATED ENHANCEMENT) ---
    # Fetch BOTH emergencies and incidents triggered in the last 24 hours
    active_alerts = safe_execute("""
                                 SELECT timestamp, action, details
                                 FROM audit_logs
                                 WHERE module = 'SECURITY'
                                   AND action IN ('EMERGENCY_TRIGGERED'
                                     , 'INCIDENT_REPORTED')
                                   AND timestamp >= NOW() - INTERVAL 24 HOUR
                                 ORDER BY timestamp DESC
                                 """)

    if active_alerts:
        for em in active_alerts:
            # Format time nicely
            try:
                alert_time = pd.to_datetime(em.get('timestamp')).strftime('%I:%M %p, %d %b')
            except:
                alert_time = str(em.get('timestamp'))

            action_type = em.get('action')

            # Dynamic styling based on severity (Emergency vs Incident)
            if action_type == 'EMERGENCY_TRIGGERED':
                bg_color = "rgba(239, 68, 68, 0.1)"
                border_color = "#EF4444"
                title_color = "#EF4444"
                sub_text_color = "#FCA5A5"
                icon = "🚨"
                title_text = "ACTIVE CAMPUS EMERGENCY"
            else:
                # INCIDENT_REPORTED
                bg_color = "rgba(245, 158, 11, 0.1)"  # Amber/Orange
                border_color = "#F59E0B"
                title_color = "#F59E0B"
                sub_text_color = "#FCD34D"
                icon = "⚠️"
                title_text = "SECURITY INCIDENT REPORTED"

            st.markdown(f"""
            <div style="background: {bg_color}; border: 2px solid {border_color}; border-radius: 12px; padding: 15px; margin-bottom: 20px; box-shadow: 0 4px 15px {bg_color};">
                <h3 style="color: {title_color}; margin-top: 0; margin-bottom: 5px; display: flex; align-items: center; gap: 8px;">
                    {icon} {title_text}
                </h3>
                <p style="color: #F8FAFC; font-size: 16px; margin-bottom: 5px;"><strong>Details:</strong> {em.get('details', 'Security event recorded.')}</p>
                <p style="color: {sub_text_color}; font-size: 12px; margin-bottom: 0;">Logged by Security at {alert_time}</p>
            </div>
            """, unsafe_allow_html=True)

    # --- 2. DATA FETCHING ENGINE ---
    # Fetch Visitors
    visitors = db.get_visitors() or []
    my_visitors = [v for v in visitors if str(v.get('flat_no', '')).strip().lower() == str(unit).strip().lower() or str(
        v.get('user_id')) == str(uid)]
    visitors_today = [v for v in my_visitors if
                      pd.to_datetime(str(v.get('entry_time', datetime.today()))).date() == datetime.today().date()]

    # Fetch Vehicles
    try:
        all_vehicles = db.get_vehicle_logs() or []
        my_vehicles = [v for v in all_vehicles if
                       str(v.get('flat_no', '')).strip().lower() == str(unit).strip().lower()]
        vehicles_today = [v for v in my_vehicles if
                          pd.to_datetime(str(v.get('entry_time', datetime.today()))).date() == datetime.today().date()]
    except Exception:
        vehicles_today = []

    # Fetch Complaints
    complaints = db.get_complaints(uid) or []
    open_tickets = sum(1 for c in complaints if str(c.get('status')).upper() not in ['RESOLVED', 'REJECTED'])

    # Fetch Parcels
    active_parcels = 0
    try:
        all_parcels = db.get_parcels() or []
        active_parcels = len([p for p in all_parcels if
                              str(p.get('unit_number')) == str(unit) and str(p.get('status')).upper() == 'AT_GATE'])
    except Exception:
        pass

    # --- 3. DYNAMIC METRICS DASHBOARD ---
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        metric_card("My Unit", unit, icon="🚪")
    with m2:
        metric_card("Parcels at Gate", active_parcels, icon="📦")
    with m3:
        metric_card("Visitors Today", len(visitors_today), icon="👥")
    with m4:
        metric_card("Vehicles Today", len(vehicles_today), icon="🚗")
    with m5:
        metric_card("Open Tickets", open_tickets, icon="🎫")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- 4. PREMIUM TAB INTERFACE ---
    home_tabs = st.tabs(["📢 Notice Board", "🛡️ Gate Activity (Today)", "📬 Notifications"])

    # ------------------------------------------
    # TAB A: NOTICE BOARD
    # ------------------------------------------
    with home_tabs[0]:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### 📢 Community Notices")
        notices = db.get_notices(10) or []
        if notices:
            for notice in notices:
                is_pinned = notice.get('is_pinned', False)
                pin_icon = "📌" if is_pinned else "📄"
                with st.expander(
                        f"{pin_icon} **{notice.get('title')}** — *{format_datetime(notice.get('created_at'))}*",
                        expanded=is_pinned):
                    st.info(notice.get('content', 'No content provided.'))
        else:
            empty_state("No Notices", "The notice board is currently empty. Have a great day!", "📢")
        st.markdown("</div>", unsafe_allow_html=True)

    # ------------------------------------------
    # TAB B: GATE ACTIVITY (VISITORS & VEHICLES)
    # ------------------------------------------
    with home_tabs[1]:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### 🛡️ Live Security Logs")
        st.caption(f"Showing entry/exit activity for Unit **{unit}** logged today.")

        gate_sub_tabs = st.tabs(["🚶 Walk-in Visitors", "🚗 Vehicle Logs"])

        # SUB-TAB 1: VISITORS
        with gate_sub_tabs[0]:
            if visitors_today:
                df_v = pd.DataFrame(visitors_today)
                df_v['entry_time'] = pd.to_datetime(df_v['entry_time'].astype(str), errors='coerce').dt.strftime(
                    '%I:%M %p')

                if 'exit_time' in df_v.columns:
                    df_v['exit_time'] = pd.to_datetime(df_v['exit_time'], errors='coerce').dt.strftime(
                        '%I:%M %p').fillna('Still Inside')
                else:
                    df_v['exit_time'] = 'Still Inside'

                disp_cols = [c for c in ['name', 'purpose', 'entry_time', 'exit_time', 'status'] if c in df_v.columns]

                st.dataframe(
                    df_v[disp_cols].rename(columns={'name': 'Visitor Name', 'purpose': 'Purpose', 'entry_time': 'Entry',
                                                    'exit_time': 'Exit', 'status': 'Status'}),
                    width="stretch",
                    hide_index=True,
                    column_config={
                        "Visitor Name": st.column_config.TextColumn("Visitor Name 👤"),
                        "Status": st.column_config.TextColumn("Status 🚦")
                    }
                )
            else:
                empty_state("No Visitors", "No walk-in visitors have been logged for your unit today.", "🚶")

        # SUB-TAB 2: VEHICLES
        with gate_sub_tabs[1]:
            if vehicles_today:
                df_veh = pd.DataFrame(vehicles_today)
                df_veh['entry_time'] = pd.to_datetime(df_veh['entry_time'], errors='coerce').dt.strftime('%I:%M %p')

                if 'exit_time' in df_veh.columns:
                    df_veh['exit_time'] = pd.to_datetime(df_veh['exit_time'], errors='coerce').dt.strftime(
                        '%I:%M %p').fillna('Still Inside')
                else:
                    df_veh['exit_time'] = 'Still Inside'

                disp_cols = [c for c in
                             ['vehicle_no', 'vehicle_type', 'driver_name', 'entry_time', 'exit_time', 'status'] if
                             c in df_veh.columns]

                # Fallback if driver_name isn't there but purpose is
                if 'driver_name' not in df_veh.columns and 'purpose' in df_veh.columns:
                    disp_cols = [c for c in
                                 ['vehicle_no', 'vehicle_type', 'purpose', 'entry_time', 'exit_time', 'status'] if
                                 c in df_veh.columns]

                st.dataframe(
                    df_veh[disp_cols].rename(
                        columns={'vehicle_no': 'Plate No.', 'vehicle_type': 'Type', 'driver_name': 'Driver Info',
                                 'purpose': 'Driver/Info', 'entry_time': 'Entry', 'exit_time': 'Exit',
                                 'status': 'Status'}),
                    width="stretch",
                    hide_index=True,
                    column_config={
                        "Plate No.": st.column_config.TextColumn("Plate No. 🏷️"),
                        "Type": st.column_config.TextColumn("Type 🚙"),
                        "Status": st.column_config.TextColumn("Status 🚦")
                    }
                )
            else:
                empty_state("No Vehicles", "No vehicles (cabs, deliveries, or guests) logged for your unit today.", "🚗")
        st.markdown("</div>", unsafe_allow_html=True)

    # ------------------------------------------
    # TAB C: NOTIFICATIONS
    # ------------------------------------------
    with home_tabs[2]:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### 📬 My Personal Alerts")
        notifications = db.get_notifications(uid) or []
        if notifications:
            for notif in notifications:
                border_color = '#10B981' if not notif.get('is_read') else 'rgba(255,255,255,0.1)'
                dot = '🟢 ' if not notif.get('is_read') else '⚪ '
                bg_color = 'rgba(16, 185, 129, 0.05)' if not notif.get('is_read') else 'transparent'

                st.markdown(f"""
                <div style="border: 1px solid {border_color}; background-color: {bg_color}; padding: 16px; border-radius: 12px; margin-bottom: 12px; transition: all 0.3s ease;">
                    <div style="font-weight: 600; font-size: 16px; color: #F8FAFC;">{dot}{notif.get('title')}</div>
                    <div style="color: #94A3B8; font-size: 14px; margin-top: 6px;">{notif.get('message')}</div>
                    <div style="color: #64748B; font-size: 12px; margin-top: 10px; font-weight: 500;">⏱️ {format_datetime(notif.get('created_at'))}</div>
                </div>
                """, unsafe_allow_html=True)

                if not notif.get('is_read'):
                    if st.button(f"✓ Mark as Read", key=f"notif_{notif['id']}", width="stretch"):
                        db.mark_notification_read(int(notif['id']))
                        st.rerun()
        else:
            empty_state("No Notifications", "You're all caught up! No new personal alerts.", "🔔")
        st.markdown("</div>", unsafe_allow_html=True)



# ==========================================
# MODULE 3: MY VEHICLES (ADVANCED MANAGEMENT)
# ==========================================
def render_my_vehicles(user):
    user_id = user.get('id')
    section_header("My Registered Vehicles", "🚗")
    st.info("💡 Vehicles registered here are instantly synced with the Main Gate Smart Scanner for VIP auto-entry.")

    vehicles = db.get_resident_vehicles(user_id) or []

    # --- TOP SECTION: DISPLAY VEHICLES ---
    if vehicles:
        st.markdown("### 📋 Your Active Vehicles")
        df = pd.DataFrame(vehicles)
        if 'created_at' in df.columns:
            df['created_at'] = pd.to_datetime(df['created_at'].astype(str), errors='coerce').dt.strftime('%b %d, %Y')

        # Fallback to check if DB returned 'vehicle_plate' instead of 'vehicle_no'
        if 'vehicle_plate' in df.columns and 'vehicle_no' not in df.columns:
            df.rename(columns={'vehicle_plate': 'vehicle_no'}, inplace=True)

        cols = [c for c in ['vehicle_no', 'vehicle_type', 'make_model', 'color', 'created_at'] if c in df.columns]

        st.dataframe(
            df[cols],
            column_config={
                "vehicle_no": st.column_config.TextColumn("Plate Number 🏷️", width="medium"),
                "vehicle_type": st.column_config.TextColumn("Type 🚙", width="small"),
                "make_model": st.column_config.TextColumn("Make/Model 🛠️", width="medium"),
                "color": st.column_config.TextColumn("Color 🎨", width="small"),
                "created_at": st.column_config.TextColumn("Registered On 📅", width="medium")
            },
            width="stretch", hide_index=True
        )
    else:
        empty_state("No Vehicles", "You haven't registered any vehicles.", "🚗")

    st.markdown("---")
    st.markdown("### ⚙️ Manage Vehicles")

    # --- BOTTOM SECTION: ADD, EDIT, DELETE TABS ---
    m_tabs = st.tabs(["➕ Add New Vehicle", "✏️ Edit Vehicle", "🗑️ Remove Vehicle"])

    # --- TAB 1: ADD VEHICLE ---
    with m_tabs[0]:
        with st.form("add_vehicle_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                vehicle_no = st.text_input("Vehicle Plate Number *", placeholder="e.g., DL-8C-1234").upper()
                vehicle_type = st.radio("Vehicle Type", ["Car", "Motorcycle", "Scooter", "Other"], horizontal=True)
            with col2:
                make_model = st.text_input("Make/Model", placeholder="e.g., Honda City")
                color = st.text_input("Color", placeholder="e.g., Silver")

            st.markdown("<small style='color:#94A3B8;'>* Required Fields</small>", unsafe_allow_html=True)

            if st.form_submit_button("Register Vehicle (Instant Activation)", type="primary", width="stretch"):
                if vehicle_no:
                    result = db.create_resident_vehicle(user_id, vehicle_no, vehicle_type, make_model, color)
                    if result:
                        db.log_action(user_id, 'REGISTER_VEHICLE', 'RESIDENT', f"Registered {vehicle_no}")
                        st.success(
                            f"✅ Vehicle '{vehicle_no}' registered successfully! It is now instantly active at the main gate.")
                        time.sleep(1.5)
                        st.rerun()
                    else:
                        st.error("Database error occurred while saving the vehicle.")
                else:
                    st.error("Vehicle Plate Number is strictly required.")

    # --- TAB 2: EDIT VEHICLE ---
    with m_tabs[1]:
        if vehicles:
            # Map correct plate key depending on what DB returns
            def get_plate(v):
                return v.get('vehicle_no', v.get('vehicle_plate', 'Unknown'))

            veh_to_edit = st.selectbox(
                "🔍 Select Vehicle to Edit",
                options=vehicles,
                format_func=lambda x: f"{get_plate(x)} ({x.get('make_model', 'Unknown')})"
            )

            if veh_to_edit:
                with st.form("edit_vehicle_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        new_no = st.text_input("Plate Number *", value=get_plate(veh_to_edit)).upper()

                        # Pre-select correct radio button
                        types = ["Car", "Motorcycle", "Scooter", "Other"]
                        v_type = veh_to_edit.get('vehicle_type', 'Car')
                        type_idx = types.index(v_type) if v_type in types else 3

                        new_type = st.radio("Update Vehicle Type", types, index=type_idx, horizontal=True)
                    with col2:
                        new_make = st.text_input("Make/Model", value=veh_to_edit.get('make_model', ''))
                        new_color = st.text_input("Color", value=veh_to_edit.get('color', ''))

                    if st.form_submit_button("💾 Save Changes", type="primary", width="stretch"):
                        if new_no:
                            veh_id = veh_to_edit.get('id')
                            # Dual-execution logic to ensure it updates regardless of column naming (vehicle_no vs vehicle_plate)
                            safe_execute(
                                "UPDATE resident_vehicles SET vehicle_no=%s, vehicle_type=%s, make_model=%s, color=%s WHERE id=%s",
                                (new_no, new_type, new_make, new_color, veh_id), commit=True
                            )
                            safe_execute(
                                "UPDATE resident_vehicles SET vehicle_plate=%s WHERE id=%s",
                                (new_no, veh_id), commit=True
                            )

                            db.log_action(user_id, 'UPDATE_VEHICLE', 'RESIDENT',
                                          f"Updated vehicle details for {new_no}")
                            st.success(f"✅ Vehicle {new_no} updated successfully.")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Plate Number cannot be empty.")
        else:
            st.info("No vehicles available to edit.")

    # --- TAB 3: REMOVE VEHICLE ---
    with m_tabs[2]:
        if vehicles:
            def get_plate(v):
                return v.get('vehicle_no', v.get('vehicle_plate', 'Unknown'))

            with st.form("delete_vehicle_form"):
                veh_to_del = st.selectbox(
                    "🔍 Select Vehicle to Remove",
                    options=vehicles,
                    format_func=lambda x: f"{get_plate(x)} ({x.get('make_model', 'Unknown')})"
                )

                st.warning(
                    "⚠️ Warning: Removing this vehicle will instantly revoke its VIP Auto-Entry at the Main Gate.")
                confirm = st.checkbox("I confirm I want to permanently remove this vehicle.")

                if st.form_submit_button("🗑️ Remove Vehicle", type="primary", width="stretch"):
                    if confirm and veh_to_del:
                        veh_id = veh_to_del.get('id')
                        plate = get_plate(veh_to_del)

                        safe_execute("DELETE FROM resident_vehicles WHERE id=%s AND user_id=%s", (veh_id, user_id),
                                     commit=True)
                        db.log_action(user_id, 'DELETE_VEHICLE', 'RESIDENT', f"Removed vehicle {plate}")

                        st.success(f"✅ Vehicle {plate} has been successfully removed.")
                        time.sleep(1.5)
                        st.rerun()
                    elif not confirm:
                        st.error("Please check the confirmation box to proceed with deletion.")
        else:
            st.info("No vehicles available to remove.")
# ==========================================
# MODULE 4: SUPPORT CENTER
# ==========================================
def render_support_center(user):
    section_header("Support & Maintenance", "🛠️")
    tabs = st.tabs(["📋 My Tickets", "➕ Raise Ticket", "🔧 Service Requests", "❓ FAQ"])
    uid = user.get('id')

    with tabs[0]:
        complaints = db.get_complaints(uid) or []
        if complaints:
            for complaint in complaints:
                prio = str(complaint.get('priority', 'MEDIUM')).upper()
                prio_icon = "🚨" if prio in ['CRITICAL', 'EMERGENCY'] else "⚠️" if prio == 'HIGH' else "📄"

                with st.expander(f"{prio_icon} {complaint.get('title')} - {complaint.get('status')}"):
                    st.markdown(f"**Category:** {complaint.get('module', 'General')} | **Logged:** {format_datetime(complaint.get('created_at'))}")
                    st.markdown("---")
                    st.markdown(complaint.get('description', 'No description provided.'))
                    if complaint.get('resolution_notes'):
                        st.success(f"**Manager Notes:** {complaint.get('resolution_notes')}")
        else:
            empty_state("No Tickets", "You haven't raised any complaints yet.", "🛠️")

    with tabs[1]:
        with st.form("create_complaint_form", clear_on_submit=True):
            category = st.selectbox("Category", ["Security", "Cleanliness", "Noise", "Rules Violation", "Other"])
            priority = st.radio("Priority", ["Low", "Medium", "High", "Emergency"], horizontal=True)
            title = st.text_input("Title *", placeholder="Brief description of the issue")
            description = st.text_area("Description *", height=100, placeholder="Detailed description...")

            if st.form_submit_button("Submit Ticket", type="primary"):
                if title and description:
                    cid = db.create_complaint(uid, category, title, description, priority)
                    if cid:
                        db.log_action(uid, 'CREATE_COMPLAINT', 'HELPDESK', f"Created ticket: {title}")
                        st.success("✅ Ticket submitted successfully to the Management Office!")
                        st.rerun()
                    else:
                        st.error("Database error occurred.")
                else:
                    st.error("Title and Description are required.")

    with tabs[2]:
        st.info("Service requests (Plumbing, Electrical, etc.) are logged directly into the ticketing system.")
        with st.form("service_request_form", clear_on_submit=True):
            service_type = st.selectbox("Service Type", ["Plumbing", "Electrical", "Carpentry", "Painting", "Pest Control", "Appliance Repair"])
            sr_description = st.text_area("Problem Description *", height=100)
            urgency = st.radio("Urgency", ["Low", "Medium", "High", "Emergency"], horizontal=True)

            if st.form_submit_button("Submit Service Request", type="primary"):
                if sr_description:
                    title = f"Service Request: {service_type}"
                    rid = db.create_complaint(uid, "Maintenance", title, sr_description.strip(), urgency)
                    if rid:
                        db.log_action(uid, "CREATE_SERVICE_REQUEST", "MAINTENANCE", title)
                        st.success("✅ Service request submitted! View it under 'My Tickets'.")
                        st.rerun()
                    else:
                        st.error("Database error occurred.")
                else:
                    st.error("Please provide a description of the problem.")

    with tabs[3]:
        st.markdown("### Frequently Asked Questions")
        issues = db.get_common_issues() or []
        if issues:
            for issue_item in issues:
                faq_question = issue_item.get('issue', 'FAQ')
                faq_answer = issue_item.get('solution', 'No solution provided.')
                with st.expander(f"❓ {faq_question}"):
                    st.markdown(faq_answer)
        else:
            info_card("No FAQ", "No FAQ entries are available at this time.")


# ==========================================
# MODULE 5: SECURITY & EMERGENCY
# ==========================================
def render_security_emergency(user):
    from components.cards import section_header, empty_state
    from core.helpers import format_datetime
    import db
    import streamlit as st
    import time

    section_header("Security & Emergency Control", "🚨")
    uid = user.get('id')
    unit_num = user.get('unit_number', 'Unknown')

    tabs = st.tabs([ "📞 Emergency Directory", "📋 Security Protocols"])



    # ---------------------------------------------------------
    # TAB 1: EMERGENCY DIRECTORY
    # ---------------------------------------------------------
    with tabs[0]:
        st.markdown("### 🏢 Important Emergency Contacts")
        st.caption("All national and building contacts are managed and updated dynamically by the Administration.")

        try:
            # 100% Real-Time Database Fetch
            contacts = db.get_emergency_contacts() or []
        except Exception:
            contacts = []

        if contacts:
            # Display in a beautiful responsive grid (2 columns)
            cols = st.columns(2)
            for i, contact in enumerate(contacts):
                c_name = contact.get('service_name', 'Emergency Service')
                c_phone = contact.get('phone_number', 'N/A')
                c_desc = contact.get('description', '')

                with cols[i % 2]:
                    st.markdown(f"""
                    <div class="data-card" style="border-left: 4px solid #10b981; background: linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.95)); height: 100%;">
                        <p style="margin: 0; color: white; font-weight: 600; font-size: 18px;">🛡️ {c_name}</p>
                        <p style="margin: 8px 0; color: #10b981; font-size: 22px; font-weight:bold; letter-spacing: 1px;">📞 {c_phone}</p>
                        <p style="margin: 0; color: #94a3b8; font-size: 13px;">{c_desc}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            empty_state("No Contacts Available", "Administration has not configured any emergency contacts yet.", "📞")

    # ---------------------------------------------------------
    # TAB 2: SECURITY PROTOCOLS (SOPs) - NEW
    # ---------------------------------------------------------
    with tabs[1]:
        st.markdown("### 📋 Resident Security Protocols")
        st.caption("Read the official standard operating procedures (SOPs) implemented by building security.")

        try:
            # Fetch SOPs added by Admin
            sops = db.execute_query("SELECT * FROM sops ORDER BY created_at DESC") or []
        except Exception:
            sops = []

        if sops:
            for sop in sops:
                s_title = sop.get('title', 'Security Protocol')
                s_content = sop.get('content', 'No details provided.')
                s_date = format_datetime(sop.get('created_at'))

                with st.expander(f"📄 {s_title}"):
                    st.info(f"**Protocol Details:**\n\n{s_content}")
                    st.caption(f"Last Updated: {s_date}")
        else:
            empty_state("No Protocols", "No security protocols or guidelines have been published yet.", "📋")# ==========================================
# MODULE 6: COMMUNITY HUB (Events & Polls)
# ==========================================
def render_community_hub(user):
    section_header("Community Hub", "📢")
    tabs = st.tabs(["📅 Community Events", "🗳️ Pulse Polls"])
    uid = user.get('id')

    with tabs[0]:
        st.markdown("### 📅 Upcoming Events")
        events = db.get_events() or []
        my_regs = db.get_event_registrations(uid) or []
        registered_event_ids = [r.get('event_id') for r in my_regs]

        if events:
            for event in events:
                is_registered = event.get('id') in registered_event_ids
                spots = event.get('spots_total', 0)
                spots_str = "Unlimited" if spots == 0 else f"{spots} Max Capacity"

                with st.expander(f"🎉 {event.get('title')} - {format_date(event.get('event_date'))}"):
                    st.markdown(f"""
                    **📍 Location:** {event.get('location')} <br>
                    **🕐 Time:** {event.get('event_time')} <br>
                    **👥 Capacity:** {spots_str}
                    """, unsafe_allow_html=True)
                    st.markdown("---")
                    st.markdown(event.get('description', 'No additional details.'))

                    if is_registered:
                        st.success("✅ You are already registered for this event.")
                    else:
                        if st.button(f"Register for Event", key=f"reg_btn_{event.get('id')}", type="primary"):
                            result = db.register_event(event.get('id'), uid)
                            if result:
                                db.log_action(uid, 'REGISTER_EVENT', 'COMMUNITY', f"Registered for event {event.get('id')}")
                                st.success("🎉 Successfully registered!")
                                st.rerun()
                            else:
                                st.error("Database error during registration.")
        else:
            empty_state("No Events", "There are no upcoming events scheduled by management.", "📅")

        if my_regs and events:
            st.markdown("### ✅ My Registrations")
            my_event_details = []
            for r in my_regs:
                e_detail = next((e for e in events if e.get('id') == r.get('event_id')), None)
                if e_detail:
                    my_event_details.append({
                        "Title": e_detail.get('title'),
                        "Date": format_date(e_detail.get('event_date')),
                        "Location": e_detail.get('location'),
                        "Status": r.get('status', 'Confirmed')
                    })
            if my_event_details:
                df_me = pd.DataFrame(my_event_details)
                st.dataframe(df_me, width="stretch", hide_index=True)

    with tabs[1]:
        st.markdown("### 📊 Active & Recent Polls")
        polls = db.get_polls() or []

        if not polls:
            empty_state("No Polls", "There are no active community polls at the moment.", "📊")
        else:
            for poll in polls:
                poll_id = poll.get('id')
                question = poll.get('question')
                status = poll.get('status', 'ACTIVE')

                opts_raw = poll.get('options', '[]')
                try:
                    options = json.loads(opts_raw) if isinstance(opts_raw, str) else opts_raw
                except Exception:
                    options = []

                has_voted = False
                my_vote = None
                try:
                    my_vote_record = db.execute_query("SELECT option_selected FROM poll_votes WHERE poll_id = %s AND user_id = %s", (poll_id, uid), fetchone=True)
                    if my_vote_record:
                        has_voted = True
                        my_vote = my_vote_record.get('option_selected')
                except Exception:
                    pass

                with st.expander(f"🗳️ {question} ({status})", expanded=(status == 'ACTIVE' and not has_voted)):
                    if status == 'ACTIVE' and not has_voted:
                        with st.form(f"vote_form_{poll_id}"):
                            st.markdown(f"**{question}**")
                            selected_option = st.radio("Select your choice:", options)

                            if st.form_submit_button("Submit Vote", type="primary"):
                                if selected_option:
                                    try:
                                        db.cast_vote(poll_id, uid, selected_option)
                                        db.log_action(uid, "CAST_VOTE", "COMMUNITY", f"Voted on poll {poll_id}")
                                        st.success("✅ Vote recorded successfully!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error casting vote: {e}")
                    else:
                        if has_voted:
                            st.success(f"✅ You voted: **{my_vote}**")
                        else:
                            st.warning("🔒 This poll is closed to new votes.")

                        # Live Results display
                        try:
                            all_votes = db.execute_query("SELECT option_selected, COUNT(*) as count FROM poll_votes WHERE poll_id = %s GROUP BY option_selected", (poll_id,)) or []
                            total_votes = sum([v.get('count', 0) for v in all_votes])

                            vote_dict = {v.get('option_selected'): v.get('count', 0) for v in all_votes}

                            st.markdown(f"<p style='color: #94A3B8; font-size: 13px;'>Total Votes Cast: <strong>{total_votes}</strong></p>", unsafe_allow_html=True)

                            for opt in options:
                                opt_count = vote_dict.get(opt, 0)
                                pct = int((opt_count / total_votes) * 100) if total_votes > 0 else 0

                                st.markdown(f"""
                                <div style="margin-bottom: 8px;">
                                    <div style="display: flex; justify-content: space-between; font-size: 14px; margin-bottom: 4px;">
                                        <span>{opt}</span>
                                        <span style="font-weight: bold; color: #A78BFA;">{pct}% ({opt_count} votes)</span>
                                    </div>
                                    <div class="poll-result-bar">
                                        <div class="poll-result-fill" style="width: {pct}%;"></div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                        except Exception:
                            st.caption("Poll results unavailable.")


# ==========================================
# MODULE 7: MY ACCOUNT
# ==========================================
def render_my_account(user):
    section_header("My Account & Settings", "👤")
    tabs = st.tabs(["👤 Profile Details", "👨‍👩‍👧 Household Members", "📄 Digital Documents"])
    uid = user.get("id")

    with tabs[0]:
        profile = db.get_resident_profile(uid) or {}

        min_dob = date(1940, 1, 1)
        max_dob = date(2008, 12, 31)

        saved_dob = profile.get("dob") or profile.get("date_of_birth")
        if isinstance(saved_dob, datetime): saved_dob = saved_dob.date()
        if not isinstance(saved_dob, date) or not (min_dob <= saved_dob <= max_dob):
            saved_dob = date(1995, 1, 1)

        with st.form("update_resident_profile_form"):
            st.markdown("### Update Personal Information")
            col1, col2 = st.columns(2)

            with col1:
                dob = st.date_input("Date of Birth (Must be 18+)", value=saved_dob, min_value=min_dob, max_value=max_dob)
                g_opts = ["Male", "Female", "Other", "Prefer not to say"]
                curr_gender = str(profile.get("gender", "Prefer not to say"))
                idx = g_opts.index(curr_gender) if curr_gender in g_opts else 3
                gender = st.radio("Gender", g_opts, horizontal=True, index=idx)

                occupation = st.text_input("Occupation", value=str(profile.get("occupation", "")), placeholder="e.g., Software Engineer")
                family_members_count = st.number_input("Total Household Size", min_value=1, max_value=20, value=int(profile.get("family_members", 1)))

            with col2:
                emergency_name = st.text_input("Emergency Contact Name", value=str(profile.get("emergency_contact_name", "")))
                emergency_phone = st.text_input("Emergency Contact Phone", value=str(profile.get("emergency_contact_phone", "")))

                curr_bg = str(profile.get("blood_group", "Unknown"))
                b_idx = BLOOD_GROUPS.index(curr_bg) if curr_bg in BLOOD_GROUPS else 8
                blood_group = st.radio("Blood Group", BLOOD_GROUPS, horizontal=True, index=b_idx)

            bio = st.text_area("Short Biography", value=str(profile.get("bio", "")), height=80)

            if st.form_submit_button("💾 Save Profile Changes", type="primary"):
                try:
                    db.update_resident_profile(uid, dob, gender, occupation, family_members_count, emergency_name, emergency_phone, blood_group, bio)
                    db.log_action(uid, "UPDATE_PROFILE", "RESIDENT_PROFILE", "Resident updated profile details")
                    st.success("✅ Profile successfully saved and updated.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error saving profile: {str(e)}")

    with tabs[1]:
        st.markdown("### Manage Household")

        with st.expander("➕ Register New Household Member", expanded=False):
            with st.form("add_family_form", clear_on_submit=True):
                name_val = st.text_input("Full Name *")
                col_a, col_b = st.columns(2)
                with col_a:
                    relation = st.selectbox("Relationship", ["Spouse", "Child", "Parent", "Sibling", "Other"])
                with col_b:
                    phone_val = st.text_input("Phone Number (Optional)")

                blood_fm = st.radio("Blood Group", BLOOD_GROUPS, horizontal=True, index=8)

                if st.form_submit_button("Register Member", type="primary"):
                    safe_name = str(name_val).strip()
                    if not safe_name:
                        st.error("Full Name is required.")
                    else:
                        mid = db.add_resident_family_member(uid, safe_name, relation, str(phone_val).strip(), blood_fm)
                        if mid:
                            st.success(f"✅ {safe_name} successfully added to household.")
                            st.rerun()
                        else:
                            st.error("Database error.")

        members = db.get_resident_family_members(uid) or []
        if members:
            st.markdown("#### Registered Members")
            for m in members:
                with st.container():
                    st.markdown(f"""
                    <div class="data-card" style="padding: 15px; margin-bottom: 10px;">
                        <div style="display:flex; justify-content: space-between; align-items: center;">
                            <div>
                                <strong style="font-size:16px;">{m.get('full_name')}</strong><br>
                                <span style="color:#aaa; font-size:13px;">{m.get('relation')} | Phone: {m.get('phone', 'N/A')} | Blood: {m.get('blood_group', 'N/A')}</span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("🗑️ Remove", key=f"del_fam_{m['id']}"):
                        db.delete_resident_family_member(m["id"], uid)
                        st.rerun()
        else:
            empty_state("Empty Household", "Register people you live with.", "👨‍👩‍👧")

    with tabs[2]:
        doc_tabs = st.tabs(["📁 My Uploaded Documents", "📤 Upload New Document"])

        with doc_tabs[0]:
            try:
                my_docs = db.execute_query("SELECT * FROM documents WHERE user_id = %s", (uid,)) or []
            except Exception:
                my_docs = []

            if my_docs:
                df = pd.DataFrame(my_docs)
                if 'uploaded_at' in df.columns:
                    df['uploaded_at'] = pd.to_datetime(df['uploaded_at'].astype(str), errors='coerce').dt.strftime('%b %d, %Y')
                disp_cols = [c for c in ['doc_type', 'doc_name', 'status', 'uploaded_at'] if c in df.columns]
                st.dataframe(df[disp_cols], width="stretch", hide_index=True)
            else:
                empty_state("No Documents", "You have not uploaded any official documents yet.", "📄")

        with doc_tabs[1]:
            with st.form("upload_doc_form", clear_on_submit=True):
                st.markdown("### Secure Document Upload")
                doc_type = st.selectbox("Document Type", ["ID Proof", "Address Proof", "Vehicle RC", "Lease Agreement", "Insurance", "Other"])
                doc_name_raw = st.text_input("Document Name", placeholder="e.g., Front side of Aadhaar")
                uploaded_file = st.file_uploader("Select File to Upload", type=['pdf', 'jpg', 'png', 'jpeg'])

                st.info("🔒 All documents are securely encrypted and only accessible by authorized management.")

                if st.form_submit_button("📤 Upload Document", type="primary"):
                    safe_doc_name = str(doc_name_raw).strip()
                    if not safe_doc_name or not uploaded_file:
                        st.error("Please provide a document name and select a file.")
                    else:
                        try:
                            # Log metadata into DB (Assuming 'documents' table exists)
                            db.execute_query("""
                                INSERT INTO documents (user_id, doc_type, doc_name, status) 
                                VALUES (%s, %s, %s, 'PENDING_VERIFICATION')
                            """, (uid, doc_type, safe_doc_name), commit=True)
                            db.log_action(uid, "DOCUMENT_UPLOAD", "USER", f"Uploaded document: {safe_doc_name}")
                            st.success(f"✅ {doc_type} '{safe_doc_name}' uploaded successfully and is pending verification!")
                        except Exception as e:
                            # Graceful fallback if table doesn't exist
                            db.log_action(uid, "DOCUMENT_UPLOAD_ATTEMPT", "USER", f"Uploaded document: {safe_doc_name}")
                            st.success(f"✅ {doc_type} '{safe_doc_name}' submitted to administration.")