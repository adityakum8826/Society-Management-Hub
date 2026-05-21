import db
from core.helpers import format_datetime, get_current_shift, get_shift_timing
import pandas as pd
import streamlit as st
from datetime import datetime
from components.cards import section_header, metric_card, empty_state

# ==========================================
# CORE ENTRY POINT
# ==========================================

def render_guard_dashboard(_user: dict = None):
    # Safe user extraction
    user_id = _user.get('id') if _user else None
    user_name = _user.get('full_name', 'Security Officer') if _user else 'Security Officer'

    shift = get_current_shift()
    shift_timing = get_shift_timing(shift)

    # --- INTERCEPT LOGOUT TO SHOW HANDOVER SCREEN ---
    if st.session_state.get('initiate_handover', False):
        render_shift_handover_logout_flow(_user)
        return  # Halt rendering the rest of the dashboard

    if 'guard_active_tab' not in st.session_state:
        st.session_state.guard_active_tab = 0

    # Route sync mapping (Adjusted indices after removing Handover tab)
    current_page = str(st.session_state.get('current_page', st.query_params.get('page', 'dashboard'))).lower()
    page_to_internal_tab = {
        'dashboard': 0, 'gate_management': 1, 'visitors': 1, 'vehicles': 1,
        'parcels': 1, 'security': 2, 'patrols': 3, 'incidents': 4, 'emergency': 4,
        'account': 5, 'profile': 5
    }

    if current_page in page_to_internal_tab:
        st.session_state.guard_active_tab = page_to_internal_tab[current_page]

    # --- ADVANCED HEADER UI ---
    user_initials = ''.join([n[0] for n in user_name.split()[:2]]).upper() if user_name else "GD"

    header_col, logout_col = st.columns([6, 1])
    with header_col:
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.98) 100%); 
                        border: 1px solid rgba(99, 102, 241, 0.3); border-radius: 16px; padding: 20px 24px; 
                        margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center; 
                        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);">
                <div style="display: flex; align-items: center; gap: 18px;">
                    <div style="font-size: 40px; padding: 12px; background: rgba(99, 102, 241, 0.15); border-radius: 14px; box-shadow: inset 0 0 10px rgba(99,102,241,0.2);">🛡️</div>
                    <div>
                        <h1 style="margin: 0; font-size: 26px; color: #F8FAFC; font-weight: 800; letter-spacing: 0.5px;">Security Command Center</h1>
                        <p style="margin: 6px 0 0 0; color: #94A3B8; font-size: 15px; font-weight: 500;">
                            🟢 Officer on Duty: <span style="color:#E2E8F0;">{user_name}</span> | Shift: <span style="color:#E2E8F0;">{shift} ({shift_timing})</span>
                        </p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with logout_col:
        st.markdown("<div style='padding-top: 25px;'></div>", unsafe_allow_html=True)
        # CHANGED: Button now triggers Handover state
        if st.button("🚪 End Shift & Logout", key="guard_logout_btn", type="primary", width="stretch"):
            st.session_state.initiate_handover = True
            st.rerun()

    # --- NAVIGATION TABS (Handover Tab Removed) ---
    tabs = st.tabs([
        "🏠 Live Dashboard",
        "🏗️ Gate Management",
        "🔒 Security Logs",
        "👣 Patrols",
        "🚨 Emergency & Incidents",
        "👤 My Account"
    ])

    with tabs[0]: render_guard_home(_user)
    with tabs[1]: render_gate_management(_user)
    with tabs[2]: render_security_logs(_user)
    with tabs[3]: render_patrol_section(_user)
    with tabs[4]: render_emergency_and_incidents(_user)

    with tabs[5]: render_guard_my_account(_user)


# ==========================================
# 1. LIVE HOME / OVERVIEW (ENHANCED COMMAND CENTER)
# ==========================================
def render_guard_home(_user: dict):
    import pandas as pd
    from datetime import datetime
    import streamlit as st
    import db
    from components.cards import section_header, metric_card, empty_state

    col_title, col_refresh = st.columns([5, 1])
    with col_title:
        section_header("Live Shift Dashboard", "🏠")
    with col_refresh:
        st.markdown("<div style='padding-top: 15px;'></div>", unsafe_allow_html=True)
        if st.button("🔄 Sync Live Data", type="primary", width="stretch"):
            st.rerun()

    # --- 1. SHIFT INTELLIGENCE BRIEFING ---
    # (This calls the function we created earlier to show handover notes)
    try:
        render_shift_briefing(_user)
    except NameError:
        st.warning("⚠️ Shift Briefing module missing. Please ensure 'render_shift_briefing' is defined in this file.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- 3. FETCH LIVE DATA FOR METRICS ---
    st.markdown("### 📡 Live Operational Status")

    visitors = db.get_visitors() or []
    vehicles = db.get_vehicle_logs() or []
    parcels = db.get_parcels() or []

    # Filter Active Entities
    v_inside_list = [v for v in visitors if str(v.get('status', '')).upper() == 'INSIDE']
    veh_inside_list = [v for v in vehicles if str(v.get('status', '')).upper() == 'INSIDE']
    p_at_gate_list = [p for p in parcels if str(p.get('status', '')).upper() == 'AT_GATE']

    v_inside = len(v_inside_list)
    veh_inside = len(veh_inside_list)
    p_at_gate = len(p_at_gate_list)

    # Overstay Detection Logic (> 4 Hours) - Made safer to prevent crashes
    current_time = datetime.now()
    overstay_count = 0
    for v in v_inside_list:
        try:
            entry_t = pd.to_datetime(v.get('entry_time'), errors='coerce')
            if pd.notnull(entry_t) and (current_time - entry_t).total_seconds() > (4 * 3600):
                overstay_count += 1
        except Exception:
            pass

    # --- LIVE OPERATIONAL METRICS ---
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        metric_card("Visitors Inside", v_inside, icon="🚶", color="#3B82F6")
    with m2:
        metric_card("Vehicles Inside", veh_inside, icon="🚗", color="#10B981")
    with m3:
        metric_card("Pending Parcels", p_at_gate, icon="📦", color="#F59E0B")
    with m4:
        # Visually alert if there are overstays
        if overstay_count > 0:
            st.markdown(f"""
            <div style="background: rgba(239, 68, 68, 0.15); border: 1px solid #EF4444; padding: 15px; border-radius: 10px; text-align: center;">
                <h4 style="color:#EF4444; margin:0;">⚠️ Overstay Alerts</h4>
                <h2 style="color:#EF4444; margin:0;">{overstay_count}</h2>
            </div>
            """, unsafe_allow_html=True)
        else:
            metric_card("Overstay Alerts", 0, icon="✅", color="#10B981")

    st.markdown("---")

    # --- 4. ADVANCED DATA TABLES ---
    col_left, col_right = st.columns(2, gap="large")

    with col_left:
        st.markdown("#### 🚶 Active Visitors Inside")
        if v_inside_list:
            df_v = pd.DataFrame(v_inside_list)
            if 'entry_time' in df_v.columns:
                df_v['entry_time_dt'] = pd.to_datetime(df_v['entry_time'], errors='coerce')
                df_v = df_v.sort_values(by='entry_time_dt', ascending=False)
                df_v['Entry Time'] = df_v['entry_time_dt'].dt.strftime('%I:%M %p')
            else:
                df_v['Entry Time'] = 'N/A'

            display_cols = [c for c in ['name', 'flat_no', 'purpose', 'Entry Time'] if c in df_v.columns]
            st.dataframe(df_v[display_cols].rename(columns={'name': 'Name', 'flat_no': 'Unit', 'purpose': 'Purpose'}),
                         width="stretch", hide_index=True)
        else:
            empty_state("All Clear", "No visitors currently inside the premises.", "✅")

    with col_right:
        st.markdown("#### 🚗 Active Vehicles Inside")
        if veh_inside_list:
            df_veh = pd.DataFrame(veh_inside_list)
            if 'entry_time' in df_veh.columns:
                df_veh['entry_time_dt'] = pd.to_datetime(df_veh['entry_time'], errors='coerce')
                df_veh = df_veh.sort_values(by='entry_time_dt', ascending=False)
                df_veh['Entry Time'] = df_veh['entry_time_dt'].dt.strftime('%I:%M %p')
            else:
                df_veh['Entry Time'] = 'N/A'

            d_cols_veh = [c for c in ['vehicle_no', 'vehicle_type', 'flat_no', 'Entry Time'] if c in df_veh.columns]
            st.dataframe(df_veh[d_cols_veh].rename(
                columns={'vehicle_no': 'License Plate', 'vehicle_type': 'Type', 'flat_no': 'Unit'}),
                width="stretch", hide_index=True)
        else:
            empty_state("All Clear", "No guest vehicles currently inside.", "✅")

    st.markdown("---")
    st.markdown("#### 📦 Deliveries Pending at Gate")
    if p_at_gate_list:
        df_p = pd.DataFrame(p_at_gate_list).head(5)
        cols_p = [c for c in ['recipient_name', 'unit_number', 'courier_service'] if c in df_p.columns]
        st.dataframe(df_p[cols_p].rename(
            columns={'recipient_name': 'Recipient', 'unit_number': 'Unit', 'courier_service': 'Courier'}),
            width="stretch", hide_index=True)
    else:
        st.info("No deliveries logged or waiting today.")

import time

from components.cards import section_header
# --- HELPER FUNCTION ---
def safe_execute(query: str, params: tuple = (), commit: bool = False) -> list:
    """Safely executes DB queries. Prevents app crashes if tables are missing."""
    import db
    try:
        result = db.execute_query(query, params, commit=commit)
        return result if result else []
    except Exception as e:
        print(f"Database Execution Error: {e}")
        return []


# ==========================================
# 2. ADVANCED GATE MANAGEMENT (SMART SCAN & ACCESS LISTS)
# ==========================================
def render_gate_management(_user: dict):
    import db
    import time
    import re
    import pandas as pd
    from components.cards import section_header

    # --- BULLETPROOF DB EXECUTOR ---
    def safe_execute(query: str, params: tuple = (), commit: bool = False) -> list:
        import db
        try:
            # Explicitly force a raw connection to ensure Updates & Deletes always commit
            if hasattr(db, 'get_connection'):
                conn = db.get_connection()
                if not conn: return []
                cursor = conn.cursor(dictionary=True)
                cursor.execute(query, params)
                if commit:
                    conn.commit()
                    result = []
                else:
                    result = cursor.fetchall()
                cursor.close()
                conn.close()
                return result
            else:
                return db.execute_query(query, params)
        except Exception as e:
            print(f"Database Execution Error: {e}")
            return []

    # --- NORMALIZATION LOGIC ---
    def normalize_plate(plate_str: str) -> str:
        """Removes spaces, dashes, and special characters for a foolproof match."""
        if not plate_str:
            return ""
        return re.sub(r'[^A-Z0-9]', '', str(plate_str).upper())

    user_id = _user.get('id')
    section_header("Live Gate Operations", "🚪")
    st.info(
        "Log entries and exits below. The Vehicle scanner is equipped with Auto-Detect Intelligence for Resident Vehicles, Whitelists & Blacklists.")

    # Data Fetching
    all_visitors = db.get_visitors() or []
    all_vehicles = db.get_vehicle_logs() or []

    visitors_inside = [v for v in all_visitors if str(v.get('status', '')).upper() == 'INSIDE']
    vehicles_inside = [v for v in all_vehicles if str(v.get('status', '')).upper() == 'INSIDE']

    gate_tabs = st.tabs([
        f"👤 Visitor Logging ({len(visitors_inside)})",
        f"🚗 Vehicle Control ({len(vehicles_inside)})",
        "🛡️ Access Lists",
        "📜 Audit History"
    ])

    # --- TAB 1: VISITORS ---
    with gate_tabs[0]:
        v_col1, v_col2 = st.columns([1.5, 1], gap="large")

        with v_col1:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("### 📝 Log Visitor Entry")
            with st.form("visitor_entry_form", clear_on_submit=True):
                v_name = st.text_input("Visitor Full Name *", placeholder="e.g. John Doe")
                c1, c2 = st.columns(2)
                with c1:
                    v_flat = st.text_input("Target Unit/Flat *", placeholder="e.g. TowerA-101")
                    v_count = st.number_input("Number of Persons", min_value=1, max_value=20, value=1)
                with c2:
                    v_phone = st.text_input("Contact Number (Optional)", placeholder="10-digit number")
                    v_company = st.text_input("Company / Agency (If applicable)", placeholder="e.g. Urban Company")

                st.markdown("**Purpose of Visit * (Dot Selection)**")
                v_purpose_radio = st.radio("Select Purpose",
                                           ["Guest", "Delivery", "Service/Repair", "Interview", "Other"],
                                           horizontal=True, label_visibility="collapsed")
                v_purpose_other = st.text_input("If 'Other', please type it here:",
                                                placeholder="Type custom purpose here...")

                st.markdown("<small style='color:#94A3B8;'>* Required Fields</small>", unsafe_allow_html=True)
                if st.form_submit_button("✅ Authorize Visitor Entry", type="primary", width="stretch"):
                    safe_name = (v_name or "").strip()
                    safe_flat = (v_flat or "").strip()

                    final_purpose = (v_purpose_other or "").strip() if v_purpose_radio == "Other" else v_purpose_radio
                    if (v_company or "").strip():
                        final_purpose += f" ({v_company.strip()})"

                    if not safe_name or not safe_flat:
                        st.error("Visitor Name and Target Unit are mandatory!")
                    elif v_purpose_radio == "Other" and not (v_purpose_other or "").strip():
                        st.error("Please type the custom purpose if 'Other' is selected.")
                    else:
                        db.create_visitor(safe_name, v_phone, safe_flat, final_purpose, "", v_count, user_id)
                        db.log_action(user_id, 'VISITOR_ENTRY', 'GATE',
                                      f"{safe_name} entered to {safe_flat} for {final_purpose}")
                        st.success(f"Access granted for {safe_name}. Logged inside.")
                        time.sleep(1)
                        st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        with v_col2:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("### 🚪 Log Visitor Exit")
            with st.form("visitor_exit_form"):
                v_exit_id = st.selectbox(
                    "🔍 Search Visitor to Exit",
                    options=[v['id'] for v in visitors_inside],
                    format_func=lambda x: next(
                        (f"{v['name']} (Unit: {v.get('flat_no', 'N/A')})" for v in visitors_inside if v['id'] == x),
                        str(x))
                ) if visitors_inside else None

                if st.form_submit_button("Log Visitor Checkout", type="primary", width="stretch"):
                    if v_exit_id:
                        db.update_visitor_status(v_exit_id, 'EXITED')
                        db.log_action(user_id, 'VISITOR_EXIT', 'GATE', "Visitor departed.")
                        st.success("Visitor successfully checked out.")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.warning("No visitors currently inside.")
            st.markdown("</div>", unsafe_allow_html=True)

    # --- TAB 2: VEHICLES (SMART AUTODETECT MODULE) ---
    with gate_tabs[1]:
        veh_col1, veh_col2 = st.columns([1.5, 1], gap="large")

        with veh_col1:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("### 📝 Log Vehicle Entry")
            st.caption("🛡️ *System automatically verifies plates against Resident DB, Whitelists & Blacklists.*")

            with st.form("vehicle_entry_form", clear_on_submit=True):
                veh_no = st.text_input("License Plate / Reg No *", placeholder="e.g. DL-8C-1234").upper()
                c1, c2 = st.columns(2)
                with c1:
                    veh_flat = st.text_input("Target Unit/Flat (Leave empty if Auto-Detect works)")
                with c2:
                    veh_driver = st.text_input("Driver Name (Optional)")

                st.markdown("**Vehicle Type * (Dot Selection)**")
                veh_type_radio = st.radio("Select Type",
                                          ["Car", "Motorcycle", "Delivery Truck", "Cab/Taxi", "Other"],
                                          horizontal=True, label_visibility="collapsed")
                veh_type_other = st.text_input("If 'Other', please type it here:",
                                               placeholder="Type custom vehicle type...")

                st.markdown("<small style='color:#94A3B8;'>* Plate Number is Required</small>", unsafe_allow_html=True)
                if st.form_submit_button("✅ Scan & Authorize Entry", type="primary", width="stretch"):
                    safe_no = (veh_no or "").strip().upper()
                    safe_flat = (veh_flat or "").strip()
                    final_veh_type = (veh_type_other or "").strip() if veh_type_radio == "Other" else veh_type_radio

                    purpose_str = "Guest/Service"
                    if (veh_driver or "").strip():
                        purpose_str = f"Driver: {veh_driver.strip()}"

                    if not safe_no:
                        st.error("License Plate is mandatory for the scanner!")
                    else:
                        blacklist = db.get_blacklist() or []
                        whitelist = db.get_whitelist() or []

                        # FIXED SQL QUERY: Matched correct columns `u.unit_number` and `u.full_name` from db.py
                        res_vehicles = safe_execute("""
                                                    SELECT rv.vehicle_no,
                                                           rv.vehicle_type,
                                                           u.unit_number as flat_no,
                                                           u.full_name   as owner_name
                                                    FROM resident_vehicles rv
                                                             LEFT JOIN users u ON rv.user_id = u.id
                                                    """)

                        if not res_vehicles:
                            res_vehicles = safe_execute(
                                "SELECT vehicle_no, vehicle_type, 'Resident' as owner_name, 'N/A' as flat_no FROM resident_vehicles") or []

                        normalized_input = normalize_plate(safe_no)

                        blacklisted_veh = next(
                            (v for v in blacklist if normalize_plate(v.get('vehicle_no', '')) == normalized_input),
                            None)
                        whitelisted_veh = next(
                            (v for v in whitelist if normalize_plate(v.get('vehicle_no', '')) == normalized_input),
                            None)
                        resident_veh = next(
                            (v for v in res_vehicles if normalize_plate(v.get('vehicle_no', '')) == normalized_input),
                            None)

                        if blacklisted_veh:
                            st.error(f"🚨 ACCESS DENIED: VEHICLE `{safe_no}` IS BLACKLISTED! 🚨")
                            st.warning(f"**Reason for Ban:** {blacklisted_veh.get('reason', 'Security Risk')}")
                            db.log_action(user_id, 'BLOCKED_ENTRY', 'SECURITY',
                                          f"Blocked blacklisted vehicle {safe_no} at gate.")
                            st.toast("Security Alert Logged!", icon="🚨")
                        else:
                            if resident_veh:
                                safe_flat = resident_veh.get('flat_no') or safe_flat or "Resident"
                                owner_name = resident_veh.get('owner_name') or 'Verified Resident'
                                purpose_str = f"✅ Verified Resident ({owner_name})"
                                st.success(f"🏠 RESIDENT VEHICLE DETECTED: Auto-verified for Unit {safe_flat}.")
                                st.toast(f"Resident Vehicle {safe_no} approved.", icon="🏠")

                            elif whitelisted_veh:
                                safe_flat = whitelisted_veh.get('flat_no') or safe_flat or "Whitelisted"
                                owner_name = whitelisted_veh.get('owner_name') or 'Unknown'
                                purpose_str = f"✅ Whitelisted ({owner_name})"
                                st.success(f"🌟 VIP WHITELIST DETECTED: Auto-verified for Unit {safe_flat}.")
                                st.toast(f"Whitelisted Vehicle {safe_no} approved.", icon="🌟")

                            elif not safe_flat:
                                st.error(
                                    "❌ Guest Vehicle not found in system. Please manually enter the Target Unit/Flat.")
                                st.stop()

                            db.create_vehicle_log(safe_no, final_veh_type, purpose_str, safe_flat, 'INSIDE')
                            db.log_action(user_id, 'VEHICLE_ENTRY', 'GATE', f"Vehicle {safe_no} entered to {safe_flat}")

                            st.success(f"✅ Boom barrier opened for {safe_no}. Logged inside successfully.")
                            time.sleep(1.5)
                            st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        with veh_col2:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("### 🚪 Log Vehicle Exit")
            with st.form("vehicle_exit_form"):
                veh_exit_id = st.selectbox(
                    "🔍 Search Vehicle to Exit",
                    options=[v['id'] for v in vehicles_inside],
                    format_func=lambda x: next(
                        (f"{v['vehicle_no']} (Unit: {v.get('flat_no', 'N/A')})" for v in vehicles_inside if
                         v['id'] == x), str(x))
                ) if vehicles_inside else None

                if st.form_submit_button("Log Vehicle Departure", type="primary", width="stretch"):
                    if veh_exit_id:
                        db.update_vehicle_status(veh_exit_id, 'EXITED')
                        db.log_action(user_id, 'VEHICLE_EXIT', 'GATE', "Vehicle departed.")
                        st.success("Vehicle successfully checked out.")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.warning("No vehicles currently inside.")
            st.markdown("</div>", unsafe_allow_html=True)
    # --- TAB 3: ACCESS LISTS (FULLY ENHANCED) ---
    with gate_tabs[2]:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### 🛡️ Vehicle Access Control Lists")
        st.info("Directly manage allowed and blocked vehicles below. Instant sync with the Live Gate Scanner.")

        list_tabs = st.tabs(["🚗 Resident Vehicles (Auto-Whitelisted)", "✅ Manage Whitelist", "❌ Manage Blacklist"])

        # 1. ENHANCED RESIDENT VEHICLES TAB
        with list_tabs[0]:
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown("#### 🚗 Registered Resident Vehicles")
                st.markdown(
                    "<p style='color:#94A3B8; font-size: 14px;'>💡 Vehicles registered by residents in their Community App. These are instantly verified by the gate scanner.</p>",
                    unsafe_allow_html=True)

            # FIXED SQL QUERY for the UI display list too
            rv_data = safe_execute("""
                                   SELECT rv.vehicle_no,
                                          rv.vehicle_type,
                                          u.unit_number as flat_no,
                                          u.full_name   as owner_name,
                                          rv.created_at
                                   FROM resident_vehicles rv
                                            LEFT JOIN users u ON rv.user_id = u.id
                                   ORDER BY rv.created_at DESC
                                   """)
            if not rv_data:
                rv_data = safe_execute(
                    "SELECT vehicle_no, vehicle_type, 'Resident' as owner_name, 'N/A' as flat_no FROM resident_vehicles")

            with c2:
                count = len(rv_data) if rv_data else 0
                st.markdown(
                    f"<div style='text-align: right; background: rgba(16, 185, 129, 0.1); padding: 10px; border-radius: 10px; border: 1px solid rgba(16, 185, 129, 0.2);'><span style='font-size: 24px; font-weight: bold; color: #10B981;'>{count}</span><br><span style='color: #94A3B8; font-size: 12px; text-transform: uppercase;'>Registered Vehicles</span></div>",
                    unsafe_allow_html=True)

            if rv_data:
                search_rv = st.text_input("🔍 Search Resident Database (by Plate, Owner, or Unit)",
                                          placeholder="e.g. DL-8C or 101...")

                df_rv = pd.DataFrame(rv_data)

                if 'created_at' in df_rv.columns:
                    df_rv['created_at'] = pd.to_datetime(df_rv['created_at'], errors='coerce').dt.strftime('%b %d, %Y')

                df_rv = df_rv.rename(columns={'vehicle_no': 'License Plate', 'vehicle_type': 'Type', 'flat_no': 'Unit',
                                              'owner_name': 'Owner Name', 'created_at': 'Registered On'})
                df_rv['System Status'] = '✅ VIP Auto-Approved'

                if search_rv:
                    df_rv = df_rv[df_rv.astype(str).apply(lambda x: x.str.contains(search_rv, case=False)).any(axis=1)]

                if not df_rv.empty:
                    display_cols = [c for c in
                                    ['Registered On', 'License Plate', 'Type', 'Owner Name', 'Unit', 'System Status'] if
                                    c in df_rv.columns]
                    st.dataframe(
                        df_rv[display_cols],
                        width="stretch",
                        hide_index=True,
                        column_config={
                            "Registered On": st.column_config.TextColumn("Registered 📅", width="medium"),
                            "License Plate": st.column_config.TextColumn("License Plate 🏷️", width="medium"),
                            "Owner Name": st.column_config.TextColumn("Owner 👤", width="medium"),
                            "Unit": st.column_config.TextColumn("Unit No. 🏠", width="small"),
                            "System Status": st.column_config.TextColumn("System Status 🛡️", width="medium")
                        }
                    )
                else:
                    st.warning("No matching vehicles found for your search.")
            else:
                st.info("No resident vehicles registered in the system yet.")

        # 2. FULL WHITELIST MANAGEMENT
        with list_tabs[1]:
            w_col, w_form_col = st.columns([1.5, 1], gap="medium")
            wl = db.get_whitelist() or []

            with w_col:
                st.markdown("#### ✅ Current Whitelist")
                if wl:
                    df_wl = pd.DataFrame(wl)
                    if 'created_at' in df_wl.columns:
                        df_wl['created_at'] = pd.to_datetime(df_wl['created_at'], errors='coerce').dt.strftime(
                            '%b %d, %Y')

                    df_wl = df_wl.rename(
                        columns={'vehicle_no': 'License Plate', 'owner_name': 'Owner', 'flat_no': 'Unit',
                                 'created_at': 'Added On'})
                    display_wl_cols = [c for c in ['License Plate', 'Owner', 'Unit', 'Added On'] if c in df_wl.columns]
                    st.dataframe(df_wl[display_wl_cols], width="stretch", hide_index=True)
                else:
                    st.info("Whitelist is currently empty.")

            with w_form_col:
                st.markdown("#### ⚙️ Manage Whitelist")
                wl_action_tabs = st.tabs(["➕ Add", "✏️ Edit", "🗑️ Remove"])

                with wl_action_tabs[0]:
                    with st.form("wl_add_form", clear_on_submit=True):
                        v_no = st.text_input("Plate Number *").upper()
                        v_own = st.text_input("Owner Name")
                        v_flt = st.text_input("Unit/Flat Number")
                        if st.form_submit_button("Add to Whitelist", type="primary", width="stretch"):
                            if v_no:
                                db.add_to_whitelist(v_no, v_own, v_flt, user_id)
                                st.success(f"Vehicle {v_no} added to Whitelist.")
                                import time;
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Plate Number is required.")

                with wl_action_tabs[1]:
                    if wl:
                        # SELECTBOX OUTSIDE THE FORM
                        edit_wl_id = st.selectbox("Select Vehicle to Edit", options=[w['id'] for w in wl],
                                                  format_func=lambda x: next(
                                                      (f"{w.get('vehicle_no', '')} ({w.get('owner_name', 'Unknown')})"
                                                       for w
                                                       in wl if w['id'] == x), str(x)), key="g_wl_edit")
                        selected_w = next((w for w in wl if w['id'] == edit_wl_id), {})

                        with st.form("wl_edit_form"):
                            new_v_no = st.text_input("Plate Number *", value=selected_w.get('vehicle_no', '')).upper()
                            new_v_own = st.text_input("Owner Name", value=selected_w.get('owner_name', ''))
                            new_v_flt = st.text_input("Unit/Flat Number", value=selected_w.get('flat_no', ''))

                            if st.form_submit_button("💾 Save Changes", type="primary", width="stretch"):
                                if new_v_no:
                                    db.execute_query(
                                        "UPDATE whitelist_vehicles SET vehicle_no=%s, owner_name=%s, flat_no=%s WHERE id=%s",
                                        (new_v_no, new_v_own, new_v_flt, edit_wl_id), commit=True)
                                    db.log_action(user_id, 'UPDATE_WHITELIST', 'SECURITY',
                                                  f"Updated whitelist vehicle {new_v_no}")
                                    st.success(f"Vehicle {new_v_no} updated.")
                                    import time;
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error("Plate Number is required.")
                    else:
                        st.caption("No vehicles available to edit.")

                with wl_action_tabs[2]:
                    if wl:
                        # SELECTBOX OUTSIDE THE FORM
                        del_wl_id = st.selectbox("Select Vehicle to Remove", options=[w['id'] for w in wl],
                                                 format_func=lambda x: next(
                                                     (f"{w.get('vehicle_no', '')}" for w in wl if w['id'] == x),
                                                     str(x)), key="g_wl_del")
                        with st.form("wl_del_form"):
                            if st.form_submit_button("❌ Remove Vehicle", width="stretch"):
                                db.execute_query("DELETE FROM whitelist_vehicles WHERE id=%s", (del_wl_id,),
                                                 commit=True)
                                db.log_action(user_id, 'REMOVE_WHITELIST', 'SECURITY', "Removed whitelist vehicle")
                                st.success("Vehicle removed from Whitelist.")
                                import time;
                                time.sleep(1)
                                st.rerun()
                    else:
                        st.caption("No vehicles available to remove.")

        # 3. FULL BLACKLIST MANAGEMENT
        with list_tabs[2]:
            b_col, b_form_col = st.columns([1.5, 1], gap="medium")
            bl = db.get_blacklist() or []

            with b_col:
                st.markdown("#### ❌ Current Blacklist")
                if bl:
                    df_bl = pd.DataFrame(bl)
                    if 'created_at' in df_bl.columns:
                        df_bl['created_at'] = pd.to_datetime(df_bl['created_at'], errors='coerce').dt.strftime(
                            '%b %d, %Y')

                    df_bl = df_bl.rename(
                        columns={'vehicle_no': 'License Plate', 'reason': 'Reason for Ban', 'created_at': 'Banned On'})
                    display_bl_cols = [c for c in ['License Plate', 'Reason for Ban', 'Banned On'] if
                                       c in df_bl.columns]
                    st.dataframe(df_bl[display_bl_cols], width="stretch", hide_index=True)
                else:
                    st.info("Blacklist is currently empty.")

            with b_form_col:
                st.markdown("#### ⚙️ Manage Blacklist")
                bl_action_tabs = st.tabs(["⛔ Ban", "✏️ Edit", "🗑️ Unban"])

                with bl_action_tabs[0]:
                    with st.form("bl_add_form", clear_on_submit=True):
                        b_no = st.text_input("Plate Number *").upper()
                        b_rsn = st.text_area("Reason for Ban")
                        if st.form_submit_button("Ban Vehicle", type="primary", width="stretch"):
                            if b_no:
                                db.add_to_blacklist(b_no, b_rsn, user_id)
                                st.error(f"Vehicle {b_no} has been banned.")
                                import time;
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Plate Number is required.")

                with bl_action_tabs[1]:
                    if bl:
                        # SELECTBOX OUTSIDE THE FORM
                        edit_bl_id = st.selectbox("Select Banned Vehicle", options=[b['id'] for b in bl],
                                                  format_func=lambda x: next(
                                                      (f"{b.get('vehicle_no', '')}" for b in bl if b['id'] == x),
                                                      str(x)), key="g_bl_edit")
                        selected_b = next((b for b in bl if b['id'] == edit_bl_id), {})

                        with st.form("bl_edit_form"):
                            new_b_no = st.text_input("Plate Number *", value=selected_b.get('vehicle_no', '')).upper()
                            new_b_rsn = st.text_area("Update Reason", value=selected_b.get('reason', ''))

                            if st.form_submit_button("💾 Save Changes", type="primary", width="stretch"):
                                if new_b_no:
                                    db.execute_query(
                                        "UPDATE blacklist_vehicles SET vehicle_no=%s, reason=%s WHERE id=%s",
                                        (new_b_no, new_b_rsn, edit_bl_id), commit=True)
                                    db.log_action(user_id, 'UPDATE_BLACKLIST', 'SECURITY',
                                                  f"Updated blacklist record for {new_b_no}")
                                    st.success(f"Ban record for {new_b_no} updated.")
                                    import time;
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error("Plate Number is required.")
                    else:
                        st.caption("No vehicles available to edit.")

                with bl_action_tabs[2]:
                    if bl:
                        # SELECTBOX OUTSIDE THE FORM
                        del_bl_id = st.selectbox("Select Vehicle to Unban", options=[b['id'] for b in bl],
                                                 format_func=lambda x: next(
                                                     (f"{b.get('vehicle_no', '')}" for b in bl if b['id'] == x),
                                                     str(x)), key="g_bl_del")
                        with st.form("bl_del_form"):
                            if st.form_submit_button("🛡️ Unban Vehicle", width="stretch"):
                                db.execute_query("DELETE FROM blacklist_vehicles WHERE id=%s", (del_bl_id,),
                                                 commit=True)
                                db.log_action(user_id, 'REMOVE_BLACKLIST', 'SECURITY', "Unbanned vehicle")
                                st.success("Vehicle successfully unbanned.")
                                import time;
                                time.sleep(1)
                                st.rerun()
                    else:
                        st.caption("No vehicles available to unban.")

        st.markdown("</div>", unsafe_allow_html=True)
    # --- TAB 4: AUDIT HISTORY ---
    with gate_tabs[3]:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### 📜 Gate Operations Audit History")
        st.info("Review historical records of all entries and exits logged at the gate.")

        hist_tabs = st.tabs(["👤 Visitor History", "🚗 Vehicle History"])

        with hist_tabs[0]:
            st.markdown("#### Recent Visitor Logs")
            if all_visitors:
                df_v_hist = pd.DataFrame(all_visitors)
                if 'entry_time' in df_v_hist.columns:
                    df_v_hist['entry_time'] = pd.to_datetime(df_v_hist['entry_time'], errors='coerce').dt.strftime(
                        '%d %b %Y, %I:%M %p')
                if 'exit_time' in df_v_hist.columns:
                    df_v_hist['exit_time'] = pd.to_datetime(df_v_hist['exit_time'], errors='coerce').dt.strftime(
                        '%d %b %Y, %I:%M %p').fillna('Still Inside')

                display_cols_v = [c for c in
                                  ['name', 'phone', 'flat_no', 'purpose', 'status', 'entry_time', 'exit_time'] if
                                  c in df_v_hist.columns]
                rename_dict_v = {'name': 'Name', 'phone': 'Contact', 'flat_no': 'Unit', 'purpose': 'Purpose',
                                 'status': 'Status', 'entry_time': 'Entry Time', 'exit_time': 'Exit Time'}

                st.dataframe(df_v_hist[display_cols_v].rename(columns=rename_dict_v).head(200),
                             width="stretch", hide_index=True)
            else:
                st.caption("No visitor history records found.")

        with hist_tabs[1]:
            st.markdown("#### Recent Vehicle Logs")
            if all_vehicles:
                df_veh_hist = pd.DataFrame(all_vehicles)
                if 'entry_time' in df_veh_hist.columns:
                    df_veh_hist['entry_time'] = pd.to_datetime(df_veh_hist['entry_time'], errors='coerce').dt.strftime(
                        '%d %b %Y, %I:%M %p')
                if 'exit_time' in df_veh_hist.columns:
                    df_veh_hist['exit_time'] = pd.to_datetime(df_veh_hist['exit_time'], errors='coerce').dt.strftime(
                        '%d %b %Y, %I:%M %p').fillna('Still Inside')

                display_cols_veh = [c for c in
                                    ['vehicle_no', 'vehicle_type', 'flat_no', 'driver_name', 'status', 'entry_time',
                                     'exit_time'] if c in df_veh_hist.columns]
                rename_dict_veh = {'vehicle_no': 'License Plate', 'vehicle_type': 'Type', 'flat_no': 'Unit',
                                   'driver_name': 'Driver Info', 'status': 'Status', 'entry_time': 'Entry Time',
                                   'exit_time': 'Exit Time'}

                if 'driver_name' not in df_veh_hist.columns and 'purpose' in df_veh_hist.columns:
                    display_cols_veh = [c for c in
                                        ['vehicle_no', 'vehicle_type', 'flat_no', 'purpose', 'status', 'entry_time',
                                         'exit_time'] if c in df_veh_hist.columns]
                    rename_dict_veh['purpose'] = 'Driver / Purpose'

                st.dataframe(df_veh_hist[display_cols_veh].rename(columns=rename_dict_veh).head(200),
                             width="stretch", hide_index=True)
            else:
                st.caption("No vehicle history records found.")
# ==========================================
# 3. SECURITY LOGS & ACCESS CONTROL
# ==========================================
def render_security_logs(_user: dict):
    from components.cards import section_header
    section_header("Security Logs & Access Control", "🔒")
    st.info("View your complete shift history and security actions.")

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### 📜 Real-Time Duty Log")
    try:
        logs = db.get_audit_logs(300) or []
        my_logs = [log for log in logs if str(log.get('user_id')) == str(_user.get('id'))]

        if my_logs:
            df = pd.DataFrame(my_logs)
            if 'timestamp' in df.columns:
                from core.helpers import format_datetime
                df['timestamp'] = df['timestamp'].apply(lambda x: format_datetime(x))

            # Advanced Filtering
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                search_term = st.text_input("🔍 Search Logs", placeholder="Type action or detail...")
            with col_f2:
                if 'action' in df.columns:
                    action_filter = st.selectbox("Filter by Action Type", ["ALL"] + list(df['action'].unique()))
                else:
                    action_filter = "ALL"

            # Apply Filters
            if search_term:
                df = df[df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)]
            if action_filter != "ALL" and 'action' in df.columns:
                df = df[df['action'] == action_filter]

            display_cols = [c for c in ['timestamp', 'action', 'details'] if c in df.columns]
            st.dataframe(df[display_cols], width="stretch", hide_index=True)
        else:
            st.info("No logs generated by you yet during this shift.")
    except Exception:
        st.error("Error loading duty logs.")
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 4. PATROLS (ADVANCED SMART MODULE)
# ==========================================
def render_patrol_section(_user: dict):
    section_header("Campus Patrol Command", "👣")
    st.info("Log your checkpoint rounds and monitor real-time campus coverage.")

    # --- 1. REAL-TIME PATROL ANALYTICS ---
    # Standard mandatory checkpoints for a complete round
    standard_checkpoints = {"Main Gate", "Basement Parking", "Tower A Lobby", "Tower B Lobby", "Perimeter Fence",
                            "Clubhouse"}

    # Fetch today's patrol logs
    today_patrols = safe_execute("""
                                 SELECT location, status, notes, started_at
                                 FROM patrol_logs
                                 WHERE DATE (started_at) = CURDATE()
                                 ORDER BY started_at DESC
                                 """)

    total_cleared = len(today_patrols)

    # Calculate how many unique standard locations were checked today
    covered_locations = {str(p.get('location')) for p in today_patrols}
    coverage_count = len(covered_locations.intersection(standard_checkpoints))
    coverage_percentage = int((coverage_count / len(standard_checkpoints)) * 100) if standard_checkpoints else 100

    # Count issues reported
    issues_found = len([p for p in today_patrols if
                        'WARNING' in str(p.get('status')).upper() or 'CRITICAL' in str(p.get('status')).upper()])

    # Display Smart Metrics
    m1, m2, m3 = st.columns(3)
    with m1:
        metric_card("Checkpoints Cleared", total_cleared, icon="✅", color="#10B981")
    with m2:
        # Turn red if issues found, else blue
        color_issue = "#EF4444" if issues_found > 0 else "#3B82F6"
        metric_card("Issues Reported", issues_found, icon="⚠️", color=color_issue)
    with m3:
        # Turn orange if coverage is low
        color_cov = "#10B981" if coverage_percentage == 100 else "#F59E0B"
        metric_card("Campus Coverage", f"{coverage_percentage}%", icon="🎯", color=color_cov)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- 2. MAIN INTERFACE (FORM & LIVE FEED) ---
    col_form, col_feed = st.columns([1.2, 1], gap="large")

    with col_form:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### 📡 Log New Checkpoint")

        with st.form("patrol_log_form", clear_on_submit=True):
            st.markdown("**Select Location * (Dot Selection)**")
            loc_radio = st.radio("Location",
                                 list(standard_checkpoints) + ["Other"],
                                 horizontal=True, label_visibility="collapsed")
            loc_other = st.text_input("If 'Other', specify custom location:")

            st.markdown("**Location Status ***")
            status = st.selectbox("Current Condition", [
                "🟢 SECURE - All Clear",
                "🟡 WARNING - Minor Issue / Needs Cleanup",
                "🔴 CRITICAL - Immediate Escalation Needed"
            ], label_visibility="collapsed")

            notes = st.text_area("Observations / Notes",
                                 placeholder="E.g., Lights out in basement sector 4. Water leaking.", height=100)

            if st.form_submit_button("📍 Log Patrol Completion", type="primary", width="stretch"):
                final_loc = (loc_other or "").strip() if loc_radio == "Other" else loc_radio
                clean_status = status.split("-")[0].strip()  # Extracts just "SECURE", "WARNING", or "CRITICAL"

                if loc_radio == "Other" and not final_loc:
                    st.error("Please specify the custom location.")
                else:
                    import db
                    try:
                        # Write to database
                        db.execute_query(
                            "INSERT INTO patrol_logs (guard_id, location, notes, status, started_at) VALUES (%s, %s, %s, %s, NOW())",
                            (_user.get('id'), final_loc, (notes or "").strip(), clean_status), commit=True
                        )
                        db.log_action(_user.get('id'), 'PATROL_LOG', 'GUARD',
                                      f"Patrol cleared at {final_loc} [{clean_status}]")

                        if "CRITICAL" in clean_status:
                            st.error(f"🚨 Critical patrol alert logged at {final_loc}. Management notified.")
                        else:
                            st.success(f"✅ Secure patrol logged at {final_loc} successfully.")
                        st.rerun()
                    except Exception as e:
                        # Fallback if patrol_logs table doesn't exist yet
                        db.log_action(_user.get('id'), 'PATROL_LOG', 'GUARD', f"Patrol at {final_loc}: {clean_status}")
                        st.success(f"Patrol recorded in audit logs: {final_loc} [{clean_status}].")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_feed:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### 📋 Live Patrol Feed (Today)")

        if today_patrols:
            df_patrols = pd.DataFrame(today_patrols)

            # Format Time
            if 'started_at' in df_patrols.columns:
                df_patrols['started_at'] = pd.to_datetime(df_patrols['started_at'], errors='coerce').dt.strftime(
                    '%I:%M %p')

            # Enhance UI formatting for status
            def format_status(val):
                val_str = str(val).upper()
                if 'SECURE' in val_str or '🟢' in val_str: return "🟢 SECURE"
                if 'WARNING' in val_str or '🟡' in val_str: return "🟡 WARNING"
                if 'CRITICAL' in val_str or '🔴' in val_str: return "🔴 CRITICAL"
                return val

            df_patrols['status'] = df_patrols['status'].apply(format_status)

            # Cleanup for display
            df_patrols = df_patrols.rename(columns={
                'started_at': 'Time',
                'location': 'Checkpoint',
                'status': 'Status',
                'notes': 'Notes'
            })

            # Reorder columns
            display_cols = [c for c in ['Time', 'Checkpoint', 'Status', 'Notes'] if c in df_patrols.columns]

            st.dataframe(
                df_patrols[display_cols],
                width="stretch",
                hide_index=True,
                column_config={
                    "Time": st.column_config.TextColumn("Time ⏱️", width="small"),
                    "Checkpoint": st.column_config.TextColumn("Location 📍", width="medium"),
                    "Status": st.column_config.TextColumn("Status 🚦", width="small"),
                    "Notes": st.column_config.TextColumn("Notes 📝", width="large")
                }
            )
        else:
            empty_state("No Patrols", "No patrol rounds have been logged yet today.", "👣")
        st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# MODULE 5 & 6 (COMBINED): EMERGENCY & INCIDENT COMMAND CENTER
# ============================================================================
def render_emergency_and_incidents(_user: dict):
    if not _user:
        st.error("User session data not found.")
        return

    section_header("Emergency & Incident Command", "🚨")
    st.info(
        "Central hub for initiating emergency protocols, reporting security incidents, and managing active broadcasts.")

    # --- TAB NAVIGATION ---
    cmd_tabs = st.tabs([
        "🚨 Trigger Emergency Alert",
        "⚠️ Report Security Incident",
        "📞 Quick Dial Contacts",
        "⚙️ Manage Active Alerts & Logs"  # Upgraded Tab Title
    ])

    # ---------------------------------------------------------
    # TAB 1: EMERGENCY ACTIONS
    # ---------------------------------------------------------
    with cmd_tabs[0]:
        st.markdown("""
        <div style='background: rgba(239, 68, 68, 0.05); border: 2px solid #EF4444; border-radius: 12px; padding: 20px;'>
            <h3 style='color: #EF4444; margin-top:0;'>📢 Campus Emergency Broadcast</h3>
            <p style='color: #FCA5A5; font-size: 14px;'>⚠️ STRICTLY FOR EMERGENCY USE ONLY. False alarms will be penalized.</p>
        </div>
        <br>
        """, unsafe_allow_html=True)

        with st.form("emergency_broadcast_form", clear_on_submit=True):
            st.markdown("**Select Emergency Protocol * (Dot Selection)**")
            alert_radio = st.radio("Type", ["🔥 FIRE EVACUATION", "🚑 MEDICAL EMERGENCY", "🥷 SECURITY BREACH", "Other"],
                                   horizontal=True, label_visibility="collapsed")
            alert_other = st.text_input("If 'Other', please specify exact nature:",
                                        placeholder="e.g., Gas Leak in Tower B")

            message = st.text_area("Broadcast Instructions *",
                                   placeholder="Type specific, calm instructions here... (e.g., Evacuate Tower A immediately via stairs. Do not use elevators.)",
                                   height=100)

            if st.form_submit_button("🚨 INITIATE EMERGENCY BROADCAST (SEND TO ALL)", type="primary", width="stretch"):
                final_alert = (alert_other or "").strip() if alert_radio == "Other" else alert_radio
                safe_msg = (message or "").strip()

                if alert_radio == "Other" and not final_alert:
                    st.error("You must specify the emergency type if 'Other' is selected.")
                elif not safe_msg:
                    st.error("Broadcast instructions cannot be empty. Tell residents what to do.")
                else:
                    import db
                    # Log the emergency action
                    db.log_action(_user.get('id'), 'EMERGENCY_TRIGGERED', 'SECURITY', f"{final_alert}: {safe_msg}")

                    st.error(f"🚨 **CRITICAL SYSTEM ALERT DISPATCHED: {final_alert}** 🚨")
                    st.warning(f"Message Broadcasted: {safe_msg}")
                    st.success("✅ Push Notifications & SMS queued. Alert is now LIVE on Resident Dashboards.")
                    st.rerun()

    # ---------------------------------------------------------
    # TAB 2: INCIDENT REPORTS
    # ---------------------------------------------------------
    with cmd_tabs[1]:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### 📝 File Official Incident Report")
        st.caption("Use this form to document non-critical security events, damages, or disputes.")

        with st.form("report_incident_form", clear_on_submit=True):
            title = st.text_input("Incident Title *", placeholder="e.g. Broken Boom Barrier, Dispute at Gate")

            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Severity Level * (Dot Selection)**")
                severity = st.radio("Severity", ["Low", "Medium", "High", "Critical"], index=1, horizontal=True,
                                    label_visibility="collapsed")
            with c2:
                parties_involved = st.text_input("Parties Involved (Optional)",
                                                 placeholder="e.g. Delivery agent & Resident A-101")

            description = st.text_area("Detailed Description *",
                                       placeholder="Explain exactly what happened, when, and who was involved...",
                                       height=150)
            st.markdown("<small style='color:#94A3B8;'>* Required Fields</small>", unsafe_allow_html=True)

            if st.form_submit_button("💾 Submit Incident Report", type="primary", width="stretch"):
                safe_title = (title or "").strip()
                safe_desc = (description or "").strip()

                if not safe_title or not safe_desc:
                    st.error("Title and Description are required to file a formal report!")
                else:
                    full_desc = f"Parties Involved: {(parties_involved or 'None recorded').strip()}\n\nDetailed Report:\n{safe_desc}"
                    try:
                        import db
                        db.create_complaint(_user.get('id'), "Security Incident", safe_title, full_desc, severity)
                        db.log_action(_user.get('id'), 'INCIDENT_REPORTED', 'SECURITY',
                                      f"Reported: {safe_title} [{severity}]")
                        st.success("✅ Incident formally reported. Alert is now LIVE on Resident Dashboards.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error submitting report. Database connection issue: {e}")
        st.markdown("</div>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # TAB 3: QUICK DIAL CONTACTS
    # ---------------------------------------------------------
    with cmd_tabs[2]:
        import db
        st.markdown("### 📞 Vital Emergency Directory")
        contacts = db.get_emergency_contacts() or []

        if not contacts:
            contacts = [
                {"service_name": "🚓 Local Police Station", "phone_number": "100"},
                {"service_name": "🚒 Fire Brigade", "phone_number": "101"},
                {"service_name": "🚑 Nearest Hospital/Ambulance", "phone_number": "102"},
                {"service_name": "🏢 Estate Manager", "phone_number": "+91 98765 43210"},
                {"service_name": "⚡ Electricity Board", "phone_number": "19122"},
                {"service_name": "💧 Water Authority", "phone_number": "1916"}
            ]

        cols = st.columns(3)
        for i, c in enumerate(contacts):
            with cols[i % 3]:
                st.markdown(f"""
                <div style="background: rgba(30, 41, 59, 0.5); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 15px; margin-bottom: 15px; text-align: center; transition: all 0.3s ease;">
                    <div style="color: #94A3B8; font-size: 14px; font-weight: 600; margin-bottom: 8px;">{c.get('service_name', 'Unknown')}</div>
                    <div style="color: #EF4444; font-size: 22px; font-weight: 800; letter-spacing: 1px;">{c.get('phone_number', 'N/A')}</div>
                </div>
                """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # TAB 4: MANAGE ACTIVE ALERTS & HISTORY (Enhanced)
    # ---------------------------------------------------------
    with cmd_tabs[3]:
        st.markdown("### ⚙️ Manage Active Broadcasts")
        st.caption("Update ongoing situations or delete false alarms to clear them from Resident Dashboards.")

        # 1. Fetch ACTIVE alerts (Last 24 Hours) that allow Update/Delete
        active_logs = safe_execute("""
                                   SELECT id, timestamp, action, details
                                   FROM audit_logs
                                   WHERE module = 'SECURITY'
                                     AND action IN ('EMERGENCY_TRIGGERED'
                                       , 'INCIDENT_REPORTED')
                                     AND timestamp >= NOW() - INTERVAL 24 HOUR
                                   ORDER BY timestamp DESC
                                   """)

        if active_logs:
            for log in active_logs:
                log_id = log.get('id')
                action_type = log.get('action')
                details = log.get('details', '')

                # Format visual indicator based on type
                if action_type == 'EMERGENCY_TRIGGERED':
                    icon_status = "🚨 EMERGENCY ACTIVE"
                    color = "#EF4444"
                else:
                    icon_status = "⚠️ INCIDENT ACTIVE"
                    color = "#F59E0B"

                time_str = pd.to_datetime(log.get('timestamp')).strftime('%d %b, %I:%M %p')

                with st.expander(f"{icon_status} — Logged at {time_str}"):
                    st.markdown(f"**Current Broadcast Message:**")
                    st.info(details)

                    # Form to update or delete the specific log
                    with st.form(f"update_log_{log_id}"):
                        new_details = st.text_area("Update Situation (Residents will see this instantly):",
                                                   value=details, height=100)

                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("📝 Update Broadcast", type="primary", width="stretch"):
                                if new_details.strip():
                                    safe_execute("UPDATE audit_logs SET details = %s WHERE id = %s",
                                                 (new_details.strip(), log_id), commit=True)
                                    st.success("✅ Broadcast Updated Successfully.")
                                    st.rerun()
                                else:
                                    st.error("Details cannot be empty.")
                        with col2:
                            if st.form_submit_button("🗑️ Revoke/Delete Alert", width="stretch"):
                                safe_execute("DELETE FROM audit_logs WHERE id = %s", (log_id,), commit=True)
                                st.success("✅ Alert Revoked. It has been removed from Resident Dashboards.")
                                st.rerun()
        else:
            empty_state("No Active Alerts",
                        "There are no active emergency or incident broadcasts in the last 24 hours.", "✅")

        st.markdown("---")
        st.markdown("### 📜 Full Security Audit History")

        # 2. Fetch older history (View Only)
        all_logs = safe_execute("""
                                SELECT timestamp, action, details
                                FROM audit_logs
                                WHERE module = 'SECURITY'
                                  AND action IN ('EMERGENCY_TRIGGERED'
                                    , 'INCIDENT_REPORTED')
                                ORDER BY timestamp DESC LIMIT 50
                                """)

        if all_logs:
            df_logs = pd.DataFrame(all_logs)
            if 'timestamp' in df_logs.columns:
                df_logs['timestamp'] = pd.to_datetime(df_logs['timestamp'], errors='coerce').dt.strftime(
                    '%d %b %Y, %I:%M %p')

            df_logs = df_logs.rename(
                columns={'timestamp': 'Date & Time', 'action': 'Event Type', 'details': 'Description'})
            df_logs['Event Type'] = df_logs['Event Type'].replace(
                {'EMERGENCY_TRIGGERED': '🚨 EMERGENCY', 'INCIDENT_REPORTED': '⚠️ INCIDENT'})

            st.dataframe(
                df_logs,
                width="stretch",
                hide_index=True,
                column_config={
                    "Date & Time": st.column_config.TextColumn("Date & Time ⏱️", width="medium"),
                    "Event Type": st.column_config.TextColumn("Event Type 📌", width="small"),
                    "Description": st.column_config.TextColumn("Description 📜", width="large")
                }
            )


# ==========================================
# 7. SHIFT HANDOVER & LOGOUT FLOW
# ==========================================
def render_shift_handover_logout_flow(_user: dict):
    import db
    import pandas as pd
    from datetime import datetime
    from components.cards import metric_card

    # Use the safe execute function inside this scope
    def safe_execute(query: str, params: tuple = (), commit: bool = False) -> list:
        try:
            result = db.execute_query(query, params, commit=commit)
            return result if result else []
        except Exception as e:
            print(f"Database Execution Error: {e}")
            return []

    st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <div style="font-size: 50px;">🛑</div>
            <h1 style="color: #EF4444; margin-top: 10px;">End Shift & Secure Logout</h1>
            <p style="color: #94A3B8; font-size: 16px;">You must formally hand over your shift to the incoming officer before logging out.</p>
        </div>
    """, unsafe_allow_html=True)

    col_btn, _ = st.columns([1, 4])
    with col_btn:
        if st.button("🔙 Cancel & Return to Dashboard", width="stretch"):
            st.session_state.initiate_handover = False
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # --- 1. REAL-TIME SHIFT SUMMARY ---
    st.markdown("### 📊 Today's Gate Status Summary")

    try:
        visitors = db.get_visitors() or []
        visitors_today = len([v for v in visitors if pd.to_datetime(
            str(v.get('entry_time', datetime.today()))).date() == datetime.today().date()])
    except:
        visitors_today = 0

    try:
        vehicles = db.get_vehicle_logs() or []
        vehicles_today = len([v for v in vehicles if pd.to_datetime(
            str(v.get('entry_time', datetime.today()))).date() == datetime.today().date()])
    except:
        vehicles_today = 0

    active_alerts = len(safe_execute("""
                                     SELECT id
                                     FROM audit_logs
                                     WHERE module = 'SECURITY'
                                       AND action IN ('EMERGENCY_TRIGGERED'
                                         , 'INCIDENT_REPORTED')
                                       AND timestamp >= NOW() - INTERVAL 24 HOUR
                                     """))

    m1, m2, m3 = st.columns(3)
    with m1:
        metric_card("Visitors Today", visitors_today, icon="🚶")
    with m2:
        metric_card("Vehicles Today", vehicles_today, icon="🚗")
    with m3:
        if active_alerts > 0:
            st.markdown(f"""
            <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid #EF4444; padding: 15px; border-radius: 10px; text-align: center;">
                <h4 style="color:#EF4444; margin:0;">🚨 Active Alerts</h4>
                <h2 style="color:#EF4444; margin:0;">{active_alerts}</h2>
            </div>
            """, unsafe_allow_html=True)
        else:
            metric_card("Active Alerts", 0, icon="✅")

    # --- 2. END OF SHIFT HANDOVER FORM ---
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    # FIXED DATABASE QUERY: Using correct columns `full_name` and `contact_number` based on db.py
    all_guards = safe_execute("SELECT id, full_name as name, contact_number as phone FROM users WHERE role = 'GUARD'")
    other_guards = [g for g in all_guards if str(g.get('id')) != str(_user.get('id'))]

    with st.form("shift_handover_logout_form", clear_on_submit=False):

        c_shift, c_guard = st.columns(2)
        with c_shift:
            shift_type = st.selectbox("Shift Ending *",
                                      ["Morning (06:00 - 14:00)", "Evening (14:00 - 22:00)", "Night (22:00 - 06:00)"])

        with c_guard:
            if other_guards:
                # Safely parse real names and phone numbers
                guard_options = {f"🛡️ {g.get('name', 'Unknown')} (ID: {g.get('id')}) - {g.get('phone', 'No Phone')}": g
                                 for g in other_guards}
                selected_guard_label = st.selectbox(
                    "Incoming Guard (Search & Select) *",
                    options=list(guard_options.keys()),
                    help="Select the guard taking over the next shift."
                )
            else:
                st.error("⚠️ No other guards found in the database. Contact Admin.")
                selected_guard_label = None

        st.markdown("---")
        st.markdown("### 🔧 Equipment Verification")
        c1, c2, c3 = st.columns(3)
        with c1:
            keys_chk = st.toggle("Master Keys Present", value=True)
            radio_chk = st.toggle("Walkie-Talkie Charged", value=True)
        with c2:
            tab_chk = st.toggle("Gate Tablet Working", value=True)
            reg_chk = st.toggle("Physical Register Intact", value=True)
        with c3:
            torch_chk = st.toggle("Torch / Flashlight", value=True)
            umb_chk = st.toggle("Umbrellas / Raincoats", value=True)

        st.markdown("---")
        st.markdown("### 📝 Shift Notes")
        handover_notes = st.text_area("Pass down critical information to the next shift *",
                                      placeholder="E.g., Boom barrier motor making noise. Expecting heavy delivery at 4 PM.",
                                      height=100)

        st.markdown("<small style='color:#94A3B8;'>* Required Fields</small>", unsafe_allow_html=True)

        if st.form_submit_button("✅ Complete Handover & Secure Logout", type="primary", width="stretch"):
            safe_notes = (handover_notes or "").strip()

            if not selected_guard_label:
                st.error("You must select a valid incoming guard.")
            elif not safe_notes:
                st.error("Handover Notes are required to complete your shift!")
            else:
                incoming_guard_data = guard_options[selected_guard_label]
                inc_guard_id = incoming_guard_data.get('id')
                inc_guard_name = incoming_guard_data.get('name')

                missing_items = []
                if not keys_chk: missing_items.append("Keys")
                if not radio_chk: missing_items.append("Walkie-Talkie")
                if not tab_chk: missing_items.append("Tablet")
                if not reg_chk: missing_items.append("Register")
                if not torch_chk: missing_items.append("Torch")
                if not umb_chk: missing_items.append("Umbrella")

                equip_status = f"Missing: {', '.join(missing_items)}" if missing_items else "All Equipment Present"

                details = f"Shift: {shift_type}\nHanded over to: {inc_guard_name} (ID: {inc_guard_id})\nEquipment: {equip_status}\nNotes: {safe_notes}"

                try:
                    # 1. Log the Handover
                    db.log_action(_user.get('id'), 'SHIFT_HANDOVER', 'GUARD', details)

                    # 2. Log the actual Logout
                    db.log_action(_user.get('id'), 'LOGOUT', 'AUTH', f"Officer finished shift and logged out.")

                    # 3. Clear states & trigger system logout
                    st.session_state.initiate_handover = False
                    st.query_params["logout"] = "1"
                    st.rerun()
                except Exception as e:
                    st.error(f"Error saving handover: {e}")

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================================
# NEW MODULE: SHIFT INTELLIGENCE & HANDOVER BRIEFING
# ============================================================================
def render_shift_briefing(_user: dict):
    import pandas as pd
    import streamlit as st
    from datetime import datetime

    # Safe database execution helper
    def safe_execute(query: str, params: tuple = ()) -> list:
        import db
        try:
            result = db.execute_query(query, params)
            return result if result else []
        except Exception as e:
            print(f"DB Error in Shift Briefing: {e}")
            return []

    st.markdown("### 🕵️ Shift Intelligence Briefing")
    st.caption("Critical handover notes and equipment status from previous shifts.")

    # Fetch the last 5 handover logs with the name of the officer who wrote them
    query = """
            SELECT u.full_name as officer_name, a.timestamp, a.details
            FROM audit_logs a
                     LEFT JOIN users u ON a.user_id = u.id
            WHERE a.action = 'SHIFT_HANDOVER'
            ORDER BY a.timestamp DESC LIMIT 5 \
            """
    recent_handovers = safe_execute(query)

    if not recent_handovers:
        st.info("No recent shift handover notes found in the system.")
        return

    # --- 1. LATEST HANDOVER (PRIORITY DISPLAY) ---
    latest_log = recent_handovers[0]
    officer = latest_log.get('officer_name', 'Unknown Officer')
    timestamp = pd.to_datetime(latest_log.get('timestamp')).strftime('%d %b %Y, %I:%M %p')
    raw_details = latest_log.get('details', '')

    # Try to parse the formatted string we created in the logout flow
    # Format was: Shift: X \n Handed over to: Y \n Equipment: Z \n Notes: W
    parsed_notes = raw_details
    equip_alert = False

    if "Equipment: Missing:" in raw_details:
        equip_alert = True

    # High-visibility card for the incoming guard
    bg_color = "rgba(239, 68, 68, 0.05)" if equip_alert else "rgba(16, 185, 129, 0.05)"
    border_color = "#EF4444" if equip_alert else "#10B981"
    status_icon = "⚠️" if equip_alert else "✅"

    st.markdown(f"""
        <div style="background: {bg_color}; border-left: 4px solid {border_color}; border-radius: 8px; padding: 15px; margin-bottom: 15px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <h4 style="margin: 0; color: #E2E8F0;">{status_icon} Latest Shift Handover</h4>
                <span style="font-size: 12px; color: #94A3B8; background: rgba(255,255,255,0.1); padding: 4px 8px; border-radius: 4px;">{timestamp}</span>
            </div>
            <p style="margin: 0 0 10px 0; font-size: 14px; color: #94A3B8;">Logged by: <strong>Officer {officer}</strong></p>
            <div style="background: rgba(0,0,0,0.2); padding: 12px; border-radius: 6px; font-family: monospace; white-space: pre-wrap; color: #F1F5F9;">{raw_details}</div>
        </div>
    """, unsafe_allow_html=True)

    # --- 2. HISTORICAL HANDOVERS (EXPANDER) ---
    if len(recent_handovers) > 1:
        with st.expander("🕰️ View Previous Shift Notes (History)"):
            for log in recent_handovers[1:]:
                hist_officer = log.get('officer_name', 'Unknown')
                hist_time = pd.to_datetime(log.get('timestamp')).strftime('%d %b, %I:%M %p')
                hist_details = log.get('details', '')

                st.markdown(f"**{hist_time} | By: Officer {hist_officer}**")
                st.markdown(
                    f"<div style='font-size: 13px; color: #94A3B8; margin-bottom: 15px; border-left: 2px solid #475569; padding-left: 10px;'>{hist_details}</div>",
                    unsafe_allow_html=True)
                st.markdown("<hr style='margin: 5px 0; border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
# ==========================================
# 8. MY ACCOUNT (GUARD PROFILE)
# ==========================================
def render_guard_my_account(_user: dict = None):
    if not _user:
        st.error("User session data not found.")
        return

    user_id = _user.get('id')
    current_username = _user.get('username', 'Guard')

    # Fetch extended profile data
    try:
        profile = db.get_resident_profile(user_id) or {}
    except Exception:
        profile = {}

    section_header(f"Welcome back, {current_username}!", "🛡️")
    st.info("Manage your personal security officer account settings and extended profile details.")

    # --- TOP METRICS BAR ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("System Role", _user.get('role', 'GUARD'))
    m2.metric("Account Status", _user.get('status', 'ACTIVE'))
    m3.metric("Officer ID", user_id)
    m4.metric("Last Login", format_datetime(_user.get('last_login')) if _user.get('last_login') else "Current Session")

    st.markdown("---")

    # --- INNER TABS ---
    acc_tabs = st.tabs([
        "👤 Profile Overview",
        "✏️ Update Profile",
        "🔒 Security & Password",
        "📜 My Activity Logs"
    ])

    # --- TAB 0: PROFILE OVERVIEW ---
    with acc_tabs[0]:
        col_img, col_info = st.columns([1, 3])

        with col_img:
            # Placeholder Avatar
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #10B981, #047857); border-radius: 50%; width: 120px; height: 120px; display: flex; align-items: center; justify-content: center; font-size: 50px; margin: 10px auto; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
                👮
            </div>
            """, unsafe_allow_html=True)

        with col_info:
            st.markdown("#### Officer Information")
            c1, c2 = st.columns(2)

            with c1:
                st.markdown(f"**Full Name:** {_user.get('full_name', 'Not set')}")
                st.markdown(f"**Username:** @{_user.get('username', 'N/A')}")
                st.markdown(f"**Date of Birth:** {profile.get('dob', 'Not set')}")
                st.markdown(f"**Gender:** {profile.get('gender', 'Not set')}")
                st.markdown(
                    f"**Blood Group:** <span style='color: #EF4444; font-weight: bold;'>{profile.get('blood_group', 'Not set')}</span>",
                    unsafe_allow_html=True)

            with c2:
                st.markdown(f"**Email Address:** {_user.get('email', 'Not set')}")
                st.markdown(f"**Contact Number:** {_user.get('contact_number', 'Not set')}")
                st.markdown(f"**Emergency Contact:** 🚨 {profile.get('emergency_contact_name', 'Not set')}")
                st.markdown(f"**Emergency Phone:** {profile.get('emergency_contact_phone', 'Not set')}")
                st.markdown(
                    f"**Account Created:** {format_datetime(_user.get('created_at')) if _user.get('created_at') else 'Unknown'}")

            st.markdown("#### Biography / Notes")
            st.info(profile.get('bio', 'No bio provided yet.'))

    # --- TAB 1: UPDATE PROFILE ---
    with acc_tabs[1]:
        st.markdown("### ✏️ Edit Personal Details")

        with st.form("update_guard_profile_form", clear_on_submit=False):
            col1, col2 = st.columns(2)

            with col1:
                new_full_name = st.text_input("Full Name", value=_user.get('full_name', ''))
                new_email = st.text_input("Email Address", value=_user.get('email', ''))
                new_dob = st.text_input("Date of Birth (YYYY-MM-DD)", value=profile.get('dob', '') or '',
                                        placeholder="e.g., 1990-05-24")

                st.markdown("**Gender (Dot Selection)**")
                gender_opts = ["Male", "Female", "Other", "Prefer not to say"]
                curr_gender = profile.get('gender', 'Prefer not to say')
                new_gender_radio = st.radio("Gender", gender_opts,
                                            index=gender_opts.index(curr_gender) if curr_gender in gender_opts else 3,
                                            horizontal=True, label_visibility="collapsed")
                new_gender_other = st.text_input("If 'Other', please specify:",
                                                 value="" if curr_gender in gender_opts else curr_gender)

            with col2:
                new_contact = st.text_input("Contact Number", value=_user.get('contact_number', ''))
                new_emergency_name = st.text_input("Emergency Contact Name",
                                                   value=profile.get('emergency_contact_name', '') or '',
                                                   placeholder="e.g., Jane Doe (Wife)")
                new_emergency_phone = st.text_input("Emergency Contact Phone",
                                                    value=profile.get('emergency_contact_phone', '') or '',
                                                    placeholder="e.g., 9876543210")

                st.markdown("**Blood Group (Dot Selection)**")
                bg_opts = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"]
                curr_bg = profile.get('blood_group', 'Unknown')
                new_blood_group = st.radio("Blood Group", bg_opts,
                                           index=bg_opts.index(curr_bg) if curr_bg in bg_opts else 8, horizontal=True,
                                           label_visibility="collapsed")

                st.text_input("System Role", value=_user.get('role', 'GUARD'), disabled=True,
                              help="Role changes require Admin approval.")

            new_bio = st.text_area("Bio / About Me", value=profile.get('bio', '') or '', height=100,
                                   placeholder="Write a short biography...")

            if st.form_submit_button("💾 Save Extended Profile", type="primary"):
                final_gender = (new_gender_other or "").strip() if new_gender_radio == "Other" else new_gender_radio

                try:
                    # 1. Update Core
                    db.update_user(
                        user_id,
                        full_name=new_full_name,
                        email=new_email,
                        contact_number=new_contact
                    )

                    # 2. Update Extended
                    fam_count = profile.get('family_members', 1) or 1
                    db.update_resident_profile(
                        user_id,
                        new_dob,
                        final_gender,
                        "Security Guard",  # Default occupation
                        fam_count,
                        new_emergency_name,
                        new_emergency_phone,
                        new_blood_group,
                        new_bio
                    )

                    db.log_action(user_id, 'UPDATE_OWN_PROFILE', 'USER',
                                  f"Guard {current_username} updated their profile")
                    st.success("✅ Profile updated successfully! Changes will fully reflect on your next login.")
                except Exception as e:
                    st.error(f"Failed to update profile. Error: {str(e)}")

    # --- TAB 2: SECURITY & PASSWORD ---
    with acc_tabs[2]:
        st.markdown("### 🔒 Change Password")
        st.warning("For security reasons, changing your password will log you out of all other active sessions.")

        with st.form("guard_change_password_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                new_password = st.text_input("New Password", type="password")
            with col2:
                confirm_password = st.text_input("Confirm New Password", type="password")

            if st.form_submit_button("🔑 Update Password", type="primary"):
                if not new_password or not confirm_password:
                    st.error("Both password fields are required.")
                elif new_password != confirm_password:
                    st.error("New passwords do not match. Please try again.")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters long.")
                else:
                    try:
                        db.change_user_password(user_id, new_password)
                        db.log_action(user_id, 'CHANGE_OWN_PASSWORD', 'SECURITY',
                                      "Guard changed their personal password")
                        st.success("✅ Password updated successfully! Please use the new password on your next login.")
                    except Exception as e:
                        st.error(f"Failed to change password: {str(e)}")

    # --- TAB 3: MY ACTIVITY LOGS ---
    with acc_tabs[3]:
        st.markdown("### 📜 My Recent Activity")
        try:
            all_logs = db.get_audit_logs(1000) or []
            my_logs = [log for log in all_logs if
                       str(log.get('user_id')) == str(user_id) or log.get('username') == current_username]

            if my_logs:
                df = pd.DataFrame(my_logs[:50])
                if 'timestamp' in df.columns:
                    df['timestamp'] = df['timestamp'].apply(lambda x: format_datetime(x) if pd.notnull(x) else 'N/A')

                valid_cols = [c for c in ['timestamp', 'action', 'module', 'details'] if c in df.columns]
                st.dataframe(df[valid_cols], width="stretch", hide_index=True)
            else:
                st.info("No recent activity found for your account.")
        except Exception:
            st.error("Could not load activity logs at this time.")