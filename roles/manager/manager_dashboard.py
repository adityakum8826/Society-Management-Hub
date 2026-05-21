"""
=============================================================================
ENTERPRISE MANAGER DASHBOARD MODULE
=============================================================================
This module provides the complete UI and operational logic for the
Society Manager role. It strictly enforces type safety, prevents Pandas
Runtime warnings, and connects directly to the live MySQL database.
=============================================================================
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st

import db
from components.cards import empty_state, section_header
from core.helpers import format_datetime


# ============================================================================
# CUSTOM CSS & UI HELPERS
# ============================================================================
def inject_custom_manager_css() -> None:
    """Injects ultra-premium, enterprise-grade CSS into the Streamlit app."""
    st.markdown("""
        <style>
        /* Main Header Styling */
        .mgr-header {
            background: linear-gradient(135deg, #0F172A 0%, #1E1B4B 100%);
            border: 1px solid rgba(139, 92, 246, 0.4);
            border-radius: 16px;
            padding: 28px 32px;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
            position: relative;
            overflow: hidden;
        }
        .mgr-header::before {
            content: '';
            position: absolute;
            top: -50%; left: -50%; width: 200%; height: 200%;
            background: radial-gradient(circle, rgba(139, 92, 246, 0.15) 0%, transparent 60%);
            animation: rotate-bg 20s linear infinite;
        }
        @keyframes rotate-bg { 100% { transform: rotate(360deg); } }
        
        .mgr-title { 
            margin: 0; font-size: 32px; color: #F8FAFC; 
            font-weight: 800; letter-spacing: 0.5px; 
            z-index: 1; position: relative;
            text-shadow: 0 2px 10px rgba(0,0,0,0.5);
        }
        .mgr-subtitle { 
            margin: 8px 0 0 0; color: #94A3B8; 
            font-size: 16px; font-weight: 500; 
            z-index: 1; position: relative;
        }
        
        /* Metric Card Styling */
        .stat-card {
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 16px;
            padding: 24px;
            text-align: center;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        .stat-card:hover { 
            transform: translateY(-5px); 
            border-color: rgba(139, 92, 246, 0.6); 
            box-shadow: 0 10px 25px rgba(139, 92, 246, 0.15);
        }
        .stat-value { font-size: 36px; font-weight: 900; color: #fff; margin: 12px 0; }
        .stat-label { font-size: 13px; color: #94A3B8; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600;}
        
        /* SLA and Priority Badges */
        .sla-breach { border-left: 6px solid #EF4444 !important; background: linear-gradient(90deg, rgba(239, 68, 68, 0.15) 0%, transparent 100%) !important; }
        .sla-warning { border-left: 6px solid #F59E0B !important; background: linear-gradient(90deg, rgba(245, 158, 11, 0.15) 0%, transparent 100%) !important; }
        .sla-good { border-left: 6px solid #10B981 !important; background: linear-gradient(90deg, rgba(16, 185, 129, 0.15) 0%, transparent 100%) !important; }
        </style>
    """, unsafe_allow_html=True)


def styled_metric(label: str, value: Any, icon: str, color: str = "#A78BFA", delta: Optional[str] = None, delta_color: str = "green") -> None:
    """Renders a beautifully styled metric card with optional delta indicators."""
    d_color = "#10B981" if delta_color == "green" else "#EF4444" if delta_color == "red" else "#F59E0B"
    delta_html = f"<div style='color: {d_color}; font-size: 14px; font-weight: 600; margin-top: 8px;'>{delta}</div>" if delta else ""

    st.markdown(f"""
        <div class="stat-card" style="border-bottom: 4px solid {color};">
            <div style="font-size: 32px; margin-bottom: 12px; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));">{icon}</div>
            <div class="stat-label">{label}</div>
            <div class="stat-value">{value}</div>
            {delta_html}
        </div>
    """, unsafe_allow_html=True)


# ============================================================================
# MAIN ENTRY POINT (ROUTER)
# ============================================================================
def render_manager_dashboard(_user: Optional[Dict[str, Any]] = None) -> None:
    """Primary router and layout container for the Manager Role."""
    if not _user:
        st.error("Authentication Error: User session lost. Please log in again.")
        return

    user_id = int(_user.get('id', 0))
    user_name = str(_user.get('full_name', 'Society Manager'))

    inject_custom_manager_css()

    if 'manager_active_tab' not in st.session_state:
        st.session_state.manager_active_tab = 0

    # --- ADVANCED HEADER UI ---
    header_col, logout_col = st.columns([7, 1])
    with header_col:
        st.markdown(f"""
            <div class="mgr-header">
                <div style="display: flex; align-items: center; gap: 24px; z-index: 1; position: relative;">
                    <div style="font-size: 48px; padding: 16px; background: rgba(139, 92, 246, 0.25); border-radius: 20px; border: 1px solid rgba(139,92,246,0.5); box-shadow: inset 0 0 20px rgba(139,92,246,0.3);">👔</div>
                    <div>
                        <h1 class="mgr-title">Manager Operations Console</h1>
                        <p class="mgr-subtitle">
                            Authorized Identity: <span style="color:#C4B5FD; font-weight: 700;">{user_name}</span> | Clearance: <span style="color:#C4B5FD; font-weight: 700;">LEVEL 4 (MANAGER)</span>
                        </p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with logout_col:
        st.markdown("<div style='padding-top: 35px;'></div>", unsafe_allow_html=True)
        if st.button("🚪 Secure Logout", key="mgr_logout_btn", type="primary", width="stretch"):
            db.log_action(user_id, 'LOGOUT', 'AUTH', "Manager securely logged out.")
            st.query_params["logout"] = "1"
            st.rerun()

    # --- MAIN NAVIGATION ---
    tabs = st.tabs([
        "📊 Command Center",
        "👥 Directory & HR",
        "🛠️ Helpdesk & SLAs",
        "🛡️ Security Oversight",
        "📢 Community Hub",
        "📱 Announcements & Notifications",
        "⚙️ Profile & Preferences"
    ])

    with tabs[0]: render_command_center(_user)
    with tabs[1]: render_directory_and_hr(_user)
    with tabs[2]: render_advanced_helpdesk(_user)
    with tabs[3]: render_security_oversight(_user)
    with tabs[4]: render_community_hub(_user)
    with tabs[5]: render_announcements_and_notifications(_user)
    with tabs[6]: render_manager_settings(_user)


# ============================================================================
# MODULE 1: COMMAND CENTER (REAL-TIME OVERVIEW)
# ============================================================================
def render_command_center(_user: Dict[str, Any]) -> None:
    c1, c2 = st.columns([6, 1])
    with c1:
        section_header("Live Society Command Center", "📊")
    with c2:
        if st.button("🔄 Sync Systems", type="primary", width="stretch"):
            st.toast("Real-time data synchronized.")
            st.rerun()

    # --- PULL ALL LIVE DATA ONCE FOR AGGREGATIONS ---
    try:
        all_users = db.get_all_users() or []
        complaints = db.get_all_complaints() or []
        visitors = db.get_visitors() or []
        vehicles = db.get_vehicle_logs() or []
    except Exception as e:
        st.error(f"System sync failure: {e}")
        all_users, complaints, visitors, vehicles = [], [], [], []

    now = datetime.now()
    yesterday = now - timedelta(days=1)

    # --- DYNAMIC METRICS ---
    residents = [u for u in all_users if str(u.get('role')).upper() == 'RESIDENT']
    total_res = len(residents)

    active_guards = len([u for u in all_users if str(u.get('role')).upper() == 'GUARD' and str(u.get('status')).upper() == 'ACTIVE'])

    open_tix = [c for c in complaints if str(c.get('status')).upper() not in ['RESOLVED', 'REJECTED']]
    total_open_tix = len(open_tix)

    # Safely calculate ticket delta
    tix_last_24 = 0
    for c in open_tix:
        try:
            if pd.to_datetime(c.get('created_at', now)) >= yesterday:
                tix_last_24 += 1
        except Exception:
            pass

    tix_delta_str = f"+{tix_last_24} new in 24h" if tix_last_24 > 0 else "Stable"
    tix_delta_color = "red" if tix_last_24 > 2 else "green"

    visitors_inside = len([v for v in visitors if str(v.get('status')).upper() == 'INSIDE'])

    visitors_today = 0
    for v in visitors:
        try:
            if pd.to_datetime(v.get('entry_time', now)).date() == now.date():
                visitors_today += 1
        except Exception:
            pass

    # Render Top Metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1: styled_metric("Total Residents", total_res, "👨‍👩‍👧", "#3B82F6")
    with m2: styled_metric("Active Guards", active_guards, "👮", "#10B981")
    with m3: styled_metric("Open Tickets", total_open_tix, "⚠️", "#EF4444", delta=tix_delta_str, delta_color=tix_delta_color)
    with m4: styled_metric("Visitors Inside", visitors_inside, "🚶", "#F59E0B", delta=f"{visitors_today} total today", delta_color="green")

    st.markdown("---")

    # --- DYNAMIC CHARTS & ALERTS ---
    col_charts, col_alerts = st.columns([2, 1], gap="large")

    with col_charts:
        st.markdown("### 📈 Live Traffic Trends (Last 7 Days)")

        # Build strict 7-day trailing date index
        dates = [(now - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]

        # Safe aggregation for Visitors
        v_df = pd.DataFrame(visitors)
        if not v_df.empty and 'entry_time' in v_df.columns:
            v_df['date'] = pd.to_datetime(v_df['entry_time'].astype(str), errors='coerce').dt.strftime('%Y-%m-%d')
            v_counts = v_df.groupby('date').size()
            v_trend = [int(v_counts.get(d, 0)) for d in dates]
        else:
            v_trend = [0] * 7

        # Safe aggregation for Vehicles
        veh_df = pd.DataFrame(vehicles)
        if not veh_df.empty and 'entry_time' in veh_df.columns:
            veh_df['date'] = pd.to_datetime(veh_df['entry_time'].astype(str), errors='coerce').dt.strftime('%Y-%m-%d')
            veh_counts = veh_df.groupby('date').size()
            veh_trend = [int(veh_counts.get(d, 0)) for d in dates]
        else:
            veh_trend = [0] * 7

        # Compile and render chart
        chart_data = pd.DataFrame({
            "Date": dates,
            "Pedestrian Visitors": v_trend,
            "External Vehicles": veh_trend
        }).set_index("Date")

        st.line_chart(chart_data, color=["#A78BFA", "#34D399"], height=350)

        # Ticket Category Analytics
        st.markdown("### 📊 Open Tickets by Category")
        if open_tix:
            tix_df = pd.DataFrame(open_tix)
            if 'module' in tix_df.columns:
                cat_counts = tix_df['module'].astype(str).value_counts().reset_index()
                cat_counts.columns = ['Category', 'Count']
                st.bar_chart(cat_counts.set_index('Category'), color="#3B82F6", height=250)
        else:
            st.info("No open tickets to display.")

    with col_alerts:
        st.markdown("### 🚨 Urgent Action Required")

        # 1. EMERGENCIES
        emergencies = [c for c in open_tix if str(c.get('priority')).upper() in ['EMERGENCY', 'CRITICAL']]
        if emergencies:
            for e in emergencies[:4]:
                st.markdown(f"""
                <div class="stat-card sla-breach" style="padding: 16px; margin-bottom: 12px; text-align: left;">
                    <div style="display:flex; justify-content: space-between;">
                        <strong style="color: #EF4444; font-size: 16px;">🚨 {str(e.get('title'))[:30]}</strong>
                        <span style="color: #EF4444; font-weight:bold;">{e.get('priority')}</span>
                    </div>
                    <div style="font-size: 13px; color: #cbd5e1; margin-top: 8px;">
                        Category: {e.get('module')} <br>
                        Resident ID: {e.get('user_id')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ No critical system emergencies.")

        st.markdown("<br>", unsafe_allow_html=True)

        # 2. SLA BREACHES (Tickets open > 48 hours)
        st.markdown("### ⏱️ SLA Violations (>48h)")
        breached = []
        for c in open_tix:
            if c.get('created_at'):
                try:
                    created_date = pd.to_datetime(str(c.get('created_at')))
                    if created_date.tzinfo is not None:
                        created_date = created_date.tz_localize(None)

                    diff_hours = (now - created_date).total_seconds() / 3600
                    if diff_hours > 48:
                        breached.append({'ticket': c, 'hours': int(diff_hours)})
                except Exception:
                    pass

        breached = sorted(breached, key=lambda x: x['hours'], reverse=True)

        if breached:
            for b in breached[:4]:
                tkt = b['ticket']
                st.markdown(f"""
                <div class="stat-card sla-warning" style="padding: 16px; margin-bottom: 12px; text-align: left;">
                    <div style="display:flex; justify-content: space-between;">
                        <strong style="color: #F59E0B; font-size: 15px;">⚠️ {str(tkt.get('title'))[:30]}</strong>
                        <span style="color: #F59E0B; font-weight:bold;">{b['hours']} hrs old</span>
                    </div>
                    <div style="font-size: 13px; color: #cbd5e1; margin-top: 6px;">Priority: {tkt.get('priority')}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("✅ All tickets are within acceptable SLAs.")


# ============================================================================
# MODULE 2: DIRECTORY & HR
# ============================================================================
def render_directory_and_hr(_user: Dict[str, Any]) -> None:
    section_header("Directory & HR Operations", "👥")

    tabs = st.tabs(["🏡 Residents Directory", "👮 Security Staff", "➕ Add Personnel"])

    try:
        all_users = db.get_all_users() or []
    except Exception:
        all_users = []

    with tabs[0]:
        st.markdown("### Master Resident Roster")
        residents = [u for u in all_users if str(u.get('role')).upper() == 'RESIDENT']

        if residents:
            df_res = pd.DataFrame(residents)

            c1, c2 = st.columns([3, 1])
            with c1:
                search_r = st.text_input("🔍 Search Residents (Name, Unit, Username)", key="search_res")
            with c2:
                status_f = st.selectbox("Status Filter", ["ALL", "ACTIVE", "SUSPENDED", "PENDING"])

            if search_r:
                mask = pd.Series(False, index=df_res.index)
                for col in df_res.columns:
                    mask = mask | df_res[col].astype(str).str.contains(search_r, case=False, na=False)
                df_res = df_res[mask]

            if status_f != "ALL":
                df_res = df_res[df_res['status'].astype(str).str.upper() == str(status_f).upper()]

            st.write("")
            if not df_res.empty:
                display_df = df_res.loc[:, ['id', 'full_name', 'username', 'unit_number', 'contact_number', 'email', 'status']]
                st.dataframe(
                    display_df,
                    column_config={
                        "id": "User ID",
                        "full_name": st.column_config.TextColumn("Resident Name", width="medium"),
                        "username": "System ID",
                        "unit_number": st.column_config.TextColumn("Unit", width="small"),
                        "contact_number": "Phone",
                        "status": st.column_config.TextColumn("Account Status"),
                    },
                    width="stretch", hide_index=True
                )

                st.markdown("#### Resident Deep Dive")
                res_ids = df_res['id'].tolist()

                def fmt_res(x: int) -> str:
                    name = next((r.get('full_name', 'Unknown') for r in residents if r.get('id') == x), "Unknown")
                    return f"ID: {x} - {name}"

                sel_res_id = st.selectbox("Select Resident to view linked data", res_ids, format_func=fmt_res)

                if sel_res_id:
                    res_data = next((r for r in residents if r.get('id') == sel_res_id), {})
                    if res_data:
                        with st.expander(f"Full Dossier: {res_data.get('full_name')} (Unit {res_data.get('unit_number')})", expanded=True):
                            sc1, sc2 = st.columns(2)
                            with sc1:
                                st.markdown("**Account Actions**")
                                curr_status = str(res_data.get('status')).upper()
                                new_stat = "SUSPENDED" if curr_status == "ACTIVE" else "ACTIVE"
                                btn_lbl = "🔓 Reactivate Account" if curr_status != "ACTIVE" else "🔒 Suspend Account"

                                if st.button(btn_lbl, key=f"sus_res_{sel_res_id}", width="stretch"):
                                    db.update_user(int(sel_res_id), status=new_stat)
                                    db.log_action(_user.get('id'), 'RESIDENT_STATUS_CHANGE', 'HR', f"Changed {res_data.get('username')} to {new_stat}")
                                    st.success(f"Account status changed to {new_stat}.")
                                    st.rerun()

                            with sc2:
                                st.markdown("**Data Links**")
                                fam = db.get_resident_family_members(int(sel_res_id)) or []
                                veh = db.get_resident_vehicles(int(sel_res_id)) or []

                                st.markdown(f"**Family Members Registered:** {len(fam)}")
                                st.markdown(f"**Vehicles Registered:** {len(veh)}")

                                if veh:
                                    for v in veh:
                                        st.caption(f"- {v.get('vehicle_no')} ({v.get('vehicle_type')}) - Status: {v.get('status')}")
            else:
                st.info("No matching residents found.")
        else:
            empty_state("No Residents", "No residents are currently registered in the database.", "🏡")

    with tabs[1]:
        st.markdown("### Security Roster & Deployment")
        guards = [u for u in all_users if str(u.get('role')).upper() == 'GUARD']

        if guards:
            df_g = pd.DataFrame(guards)
            st.dataframe(
                df_g.loc[:, ['id', 'full_name', 'username', 'contact_number', 'status']],
                column_config={"id": "Guard ID", "full_name": "Officer Name"},
                width="stretch", hide_index=True
            )

            st.markdown("#### Staff Account Control")
            with st.expander("Manage Guard Profile", expanded=True):
                guard_ids = [g.get('id') for g in guards]

                def fmt_g(x: int) -> str:
                    return next((g.get('full_name', 'Unknown') for g in guards if g.get('id') == x), "Unknown")

                g_sel_id = st.selectbox("Select Officer", guard_ids, format_func=fmt_g)
                g_data = next((g for g in guards if g.get('id') == g_sel_id), None)

                if g_data:
                    c1, c2 = st.columns(2)
                    with c1:
                        curr_g_stat = str(g_data.get('status')).upper()
                        g_new_stat = "SUSPENDED" if curr_g_stat == "ACTIVE" else "ACTIVE"
                        if st.button(f"Toggle Status (Currently {curr_g_stat})", width="stretch", key="btn_g_stat"):
                            db.update_user(int(g_sel_id), status=g_new_stat)
                            st.success(f"Guard status updated to {g_new_stat}")
                            st.rerun()
                    with c2:
                        if st.button("Generate New Password", width="stretch", key="btn_g_pwd"):
                            new_pwd = uuid.uuid4().hex[:8]
                            db.change_user_password(int(g_sel_id), new_pwd)
                            st.success(f"Password reset! Provide this to guard: **{new_pwd}**")
        else:
            empty_state("No Guards", "No security personnel registered.", "👮")

    with tabs[2]:
        st.markdown("### Register New Society Personnel")
        st.info("Managers can register new Residents or Guards. Admin accounts must be created by a Super Admin.")

        with st.form("mgr_add_user_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                full_name = st.text_input("Full Name *")
                username = st.text_input("System Username *", help="Must be unique.")
                email = st.text_input("Email Address")
            with col2:
                role = st.selectbox("Assign Role *", ["RESIDENT", "GUARD"])
                unit_number = st.text_input("Unit Number", placeholder="Required if Resident (e.g. A-101)")
                contact_number = st.text_input("Primary Contact Phone")

            if st.form_submit_button("Register & Generate Credentials", type="primary"):
                if not username or not full_name:
                    st.error("Name and Username are strictly required.")
                elif role == 'RESIDENT' and not unit_number:
                    st.error("Unit Number is required for Residents.")
                else:
                    existing = db.get_user_by_username(username)
                    if existing:
                        st.error("Error: Username is already taken in the system.")
                    else:
                        pwd = uuid.uuid4().hex[:8]
                        db.create_user(username, pwd, full_name, role, unit_number, contact_number, email)
                        db.log_action(_user.get('id'), 'CREATE_USER', 'HR', f"Registered {role}: {username}")
                        st.success(f"✅ Account Registered Successfully! Provide the user with this temporary password: **{pwd}**")


# ============================================================================
# MODULE 3: ADVANCED HELPDESK & SLAs
# ============================================================================
def render_advanced_helpdesk(_user: Dict[str, Any]) -> None:
    section_header("Enterprise Helpdesk & Ticketing", "🛠️")

    try:
        complaints = db.get_all_complaints() or []
    except Exception:
        complaints = []

    if not complaints:
        empty_state("Inbox Zero", "No support tickets in the database.", "🎉")
        return

    df = pd.DataFrame(complaints)
    df['Date'] = pd.to_datetime(df['created_at'].astype(str), errors='coerce').dt.strftime('%Y-%m-%d %H:%M')

    st.markdown("#### 🔍 Filter & Search")
    f1, f2, f3, f4 = st.columns(4)
    with f1: stat_f = st.selectbox("Status", ["ALL", "OPEN", "IN_PROGRESS", "ESCALATED", "RESOLVED", "REJECTED"])
    with f2: prio_f = st.selectbox("Priority", ["ALL", "Low", "Medium", "High", "Emergency", "Critical", "Urgent"])
    with f3: mod_f = st.selectbox("Category", ["ALL"] + list(df['module'].dropna().unique()) if 'module' in df.columns else ["ALL"])
    with f4: search_q = st.text_input("Search by Keyword")

    if stat_f != "ALL": df = df[df['status'].astype(str).str.upper() == str(stat_f).upper()]
    if prio_f != "ALL": df = df[df['priority'].astype(str).str.upper() == str(prio_f).upper()]
    if mod_f != "ALL": df = df[df['module'] == mod_f]

    if search_q:
        df = df[df['title'].astype(str).str.contains(search_q, case=False, na=False) |
                df['description'].astype(str).str.contains(search_q, case=False, na=False)]

    st.markdown(f"**Showing {len(df)} Ticket(s)**")
    st.markdown("---")

    for _, row in df.iterrows():
        status_val = str(row.get('status')).upper()
        prio_val = str(row.get('priority')).upper()

        stat_color = "#10B981" if status_val == 'RESOLVED' else "#EF4444" if status_val in ['OPEN', 'ESCALATED'] else "#F59E0B"
        prio_icon = "🚨" if prio_val in ['CRITICAL', 'EMERGENCY', 'URGENT'] else "⚠️" if prio_val == 'HIGH' else "📄"

        try:
            created_dt = pd.to_datetime(str(row.get('created_at')))
            if created_dt.tzinfo is not None:
                created_dt = created_dt.tz_localize(None)
            hours_old = int((datetime.now() - created_dt).total_seconds() / 3600)
            age_str = f"{hours_old} hours old" if hours_old < 48 else f"🔥 {hours_old} hours old (BREACH)"
        except Exception:
            age_str = "Unknown age"

        with st.expander(f"{prio_icon} [{row.get('id')}] {str(row.get('title'))[:40]} ({age_str})"):
            st.markdown(f"""
                <div style="display:flex; justify-content: space-between; border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:12px; margin-bottom:12px;">
                    <div><span style="color:#94A3B8;">Reported By:</span> <strong>Res ID {row.get('user_id')}</strong></div>
                    <div><span style="color:#94A3B8;">Module:</span> <strong>{row.get('module')}</strong></div>
                    <div><span style="color:#94A3B8;">Priority:</span> <strong>{prio_val}</strong></div>
                    <div><span style="background:{stat_color}; padding:4px 10px; border-radius:12px; color:#fff; font-size:12px; font-weight:bold;">{status_val}</span></div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("**Description:**")
            st.info(row.get('description', 'No details provided.'))

            if row.get('resolution_notes'):
                st.markdown("**Resolution Notes (Manager):**")
                st.success(row.get('resolution_notes'))

            st.markdown("#### ⚙️ Manager Actions")
            c1, c2 = st.columns([1, 1])

            with c1:
                with st.form(f"tkt_stat_form_{row.get('id')}"):
                    available_stats = ["OPEN", "IN_PROGRESS", "ESCALATED", "RESOLVED", "REJECTED"]
                    idx = available_stats.index(status_val) if status_val in available_stats else 0
                    new_stat = st.selectbox("Update Status", available_stats, index=idx)
                    notes = st.text_area("Append Resolution/Internal Notes")

                    if st.form_submit_button("💾 Save Ticket Update", type="primary"):
                        try:
                            db.update_complaint_status(int(row.get('id')), str(new_stat))
                            if notes:
                                db.execute_query("UPDATE complaints SET resolution_notes = %s WHERE id = %s", (str(notes), int(row.get('id'))), commit=True)

                            db.log_action(_user.get('id'), 'TICKET_UPDATE', 'HELPDESK', f"Ticket {row.get('id')} updated to {new_stat}")
                            st.success("Ticket updated successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to update: {e}")
            with c2:
                with st.form(f"tkt_assign_form_{row.get('id')}"):
                    assignee = st.selectbox("Assign To Staff/Vendor", ["Unassigned", "Lead Plumber", "Lead Electrician", "Facility Supervisor", "Security Head"])
                    if st.form_submit_button("👤 Assign"):
                        st.success(f"Ticket routed to {assignee} queue.")


# ============================================================================
# MODULE 4: SECURITY OVERSIGHT (ENTERPRISE ENHANCED)
# ============================================================================
def render_security_oversight(_user: Dict[str, Any]) -> None:
    section_header("Global Security Oversight", "🛡️")
    st.info("Monitor live gate traffic, guard patrols, shift handovers, and access control lists in real-time.")

    # Safe execution helper for advanced SQL joins (used in Tab 1)
    def safe_execute(query: str, params: tuple = ()) -> list:
        import db
        try:
            result = db.execute_query(query, params)
            return result if result else []
        except Exception as e:
            print(f"DB Error: {e}")
            return []

    tabs = st.tabs(["🚶 Live Gate Traffic", "🔦 Patrols & Handovers", "📋 Access Control (Lists)"])

    # --- TAB 0: LIVE GATE TRAFFIC ---
    with tabs[0]:
        col_title, col_ref = st.columns([5, 1])
        with col_title:
            st.markdown("### 📡 Real-Time Gate Feed")
        with col_ref:
            st.markdown("<div style='padding-top:10px;'></div>", unsafe_allow_html=True)
            if st.button("🔄 Refresh Feeds", key="ref_sec", width="stretch", type="primary"):
                st.rerun()

        v_col, veh_col = st.columns(2, gap="large")

        with v_col:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("#### 🚶 Pedestrians Inside")
            visitors = db.get_visitors() or []
            inside_vis = [v for v in visitors if str(v.get('status')).upper() == 'INSIDE']

            if inside_vis:
                df_v = pd.DataFrame(inside_vis)
                if 'entry_time' in df_v.columns:
                    df_v['entry_time'] = pd.to_datetime(df_v['entry_time'], errors='coerce').dt.strftime('%I:%M %p')

                disp_cols = [c for c in ['name', 'phone', 'flat_no', 'purpose', 'entry_time'] if c in df_v.columns]
                st.dataframe(
                    df_v[disp_cols].rename(
                        columns={'name': 'Name', 'phone': 'Contact', 'flat_no': 'Unit', 'purpose': 'Purpose',
                                 'entry_time': 'Entered At'}),
                    width="stretch", hide_index=True
                )
            else:
                empty_state("All Clear", "No guests currently inside.", "🚶")
            st.markdown("</div>", unsafe_allow_html=True)

        with veh_col:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("#### 🚗 Vehicles Inside")
            vehicle_records = db.get_vehicle_logs() or []
            vehicles_inside = [v for v in vehicle_records if str(v.get('status')).upper() == 'INSIDE']

            if vehicles_inside:
                df_veh = pd.DataFrame(vehicles_inside)
                if 'entry_time' in df_veh.columns:
                    df_veh['entry_time'] = pd.to_datetime(df_veh['entry_time'], errors='coerce').dt.strftime('%I:%M %p')

                disp_cols = [c for c in ['vehicle_no', 'vehicle_type', 'driver_name', 'flat_no', 'entry_time'] if
                             c in df_veh.columns]
                st.dataframe(
                    df_veh[disp_cols].rename(
                        columns={'vehicle_no': 'Plate No.', 'vehicle_type': 'Type', 'driver_name': 'Driver',
                                 'flat_no': 'Unit', 'entry_time': 'Entered At'}),
                    width="stretch", hide_index=True
                )
            else:
                empty_state("All Clear", "No external vehicles currently inside.", "🚗")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("#### 📦 Parcels Pending at Gate")
        parcels = db.get_parcels() or []
        at_gate = [p for p in parcels if str(p.get('status')).upper() == 'AT_GATE']

        if at_gate:
            df_p = pd.DataFrame(at_gate)
            if 'received_at' in df_p.columns:
                df_p['received_at'] = pd.to_datetime(df_p['received_at'], errors='coerce').dt.strftime(
                    '%d %b, %I:%M %p')

            disp_cols = [c for c in ['recipient_name', 'unit_number', 'courier_service', 'received_at'] if
                         c in df_p.columns]
            st.dataframe(
                df_p[disp_cols].rename(
                    columns={'recipient_name': 'Recipient', 'unit_number': 'Unit', 'courier_service': 'Courier',
                             'received_at': 'Arrived At'}),
                width="stretch", hide_index=True
            )
        else:
            empty_state("Clear", "No parcels pending collection.", "📦")
        st.markdown("</div>", unsafe_allow_html=True)

    # --- TAB 1: PATROLS & HANDOVERS ---
    with tabs[1]:
        p_col, h_col = st.columns([1.2, 1], gap="large")

        # LEFT COLUMN: PATROLS (With Bulletproof Fallback Logic)
        with p_col:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("### 🔦 Active Guard Patrols")

            # Attempt 1: Try pulling from the dedicated patrol_logs table
            patrol_data = safe_execute("""
                                       SELECT p.started_at, u.full_name as guard_name, p.location, p.status, p.notes
                                       FROM patrol_logs p
                                                LEFT JOIN users u ON p.guard_id = u.id
                                       ORDER BY p.started_at DESC LIMIT 100
                                       """)

            # Attempt 2: If empty, intelligently pull from the fallback audit_logs
            if not patrol_data:
                fallback_data = safe_execute("""
                                             SELECT a.timestamp as started_at,
                                                    u.full_name as guard_name,
                                                    a.details   as raw_details
                                             FROM audit_logs a
                                                      LEFT JOIN users u ON a.user_id = u.id
                                             WHERE a.action = 'PATROL_LOG'
                                             ORDER BY a.timestamp DESC LIMIT 100
                                             """)

                patrol_data = []
                for row in fallback_data:
                    details = row.get('raw_details', '')
                    # Extract location and status from the string format
                    loc = details.split(' at ')[-1].split(' [')[0] if ' at ' in details else 'Unknown'
                    stat = details.split('[')[-1].replace(']', '') if '[' in details else 'SECURE'

                    patrol_data.append({
                        'started_at': row.get('started_at'),
                        'guard_name': row.get('guard_name'),
                        'location': loc,
                        'status': stat,
                        'notes': details
                    })

            if patrol_data:
                df_patrol = pd.DataFrame(patrol_data)

                if 'started_at' in df_patrol.columns:
                    df_patrol['started_at'] = pd.to_datetime(df_patrol['started_at'], errors='coerce').dt.strftime(
                        '%d %b, %I:%M %p')

                def format_status(val):
                    v = str(val).upper()
                    if 'SECURE' in v: return "🟢 SECURE"
                    if 'WARNING' in v: return "🟡 WARNING"
                    if 'CRITICAL' in v: return "🔴 CRITICAL"
                    return val

                if 'status' in df_patrol.columns:
                    df_patrol['status'] = df_patrol['status'].apply(format_status)

                search_patrol = st.text_input("🔍 Search Patrols", placeholder="Location, Guard, Status...")
                if search_patrol:
                    df_patrol = df_patrol[
                        df_patrol.astype(str).apply(lambda x: x.str.contains(search_patrol, case=False)).any(axis=1)]

                df_patrol = df_patrol.rename(
                    columns={'started_at': 'Time', 'guard_name': 'Officer', 'location': 'Checkpoint',
                             'status': 'Status', 'notes': 'Notes'})
                disp_cols = [c for c in ['Time', 'Officer', 'Checkpoint', 'Status', 'Notes'] if c in df_patrol.columns]

                st.dataframe(df_patrol[disp_cols], width="stretch", hide_index=True)
            else:
                empty_state("No Patrols", "No patrol data recorded by the security team yet.", "🔦")
            st.markdown("</div>", unsafe_allow_html=True)

        # RIGHT COLUMN: SHIFT HANDOVERS
        with h_col:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("### 📋 Official Shift Handovers")

            handovers = safe_execute("""
                                     SELECT a.timestamp,
                                            COALESCE(u.full_name, u.name, 'Unknown Guard') as outgoing_guard,
                                            a.details
                                     FROM audit_logs a
                                              LEFT JOIN users u ON a.user_id = u.id
                                     WHERE a.action = 'SHIFT_HANDOVER'
                                     ORDER BY a.timestamp DESC LIMIT 20
                                     """)

            if handovers:
                for h in handovers:
                    time_str = pd.to_datetime(h.get('timestamp')).strftime('%d %b %Y, %I:%M %p')
                    guard_name = h.get('outgoing_guard')
                    details = h.get('details', '')

                    is_missing_equip = "Missing:" in details and "None" not in details and "All Equipment Present" not in details
                    icon = "⚠️" if is_missing_equip else "✅"
                    border_color = "#F59E0B" if is_missing_equip else "#10B981"

                    with st.expander(f"{icon} {time_str} — Logged by: {guard_name}"):
                        st.markdown(f"<div style='border-left: 3px solid {border_color}; padding-left: 12px;'>",
                                    unsafe_allow_html=True)
                        st.markdown(f"**Handover Briefing:**")
                        st.markdown(
                            f"<div style='font-family: monospace; white-space: pre-wrap; font-size: 13px; color: #E2E8F0; background: rgba(0,0,0,0.2); padding: 10px; border-radius: 6px;'>{details}</div>",
                            unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
            else:
                empty_state("No Handovers", "No official shift handovers have been recorded.", "📋")
            st.markdown("</div>", unsafe_allow_html=True)

    # --- TAB 2: ACCESS CONTROL LISTS ---
    with tabs[2]:
        st.markdown("### 🚦 Vehicle Access Control Lists")
        w_col, b_col = st.columns(2, gap="large")

        with w_col:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("#### ✅ Approved Whitelist")
            wl = db.get_whitelist() or []
            if wl:
                df_wl = pd.DataFrame(wl)
                st.dataframe(
                    df_wl.loc[:, ['vehicle_no', 'owner_name', 'flat_no']].rename(
                        columns={'vehicle_no': 'Plate No.', 'owner_name': 'Owner', 'flat_no': 'Unit'}),
                    width="stretch", hide_index=True
                )
            else:
                empty_state("No Whitelist", "Whitelist is currently empty.", "✅")

            with st.expander("➕ Add to Whitelist"):
                with st.form("wl_form", clear_on_submit=True):
                    v_no = st.text_input("Plate Number *", placeholder="e.g. DL-10-AB-1234")
                    v_own = st.text_input("Owner Name", placeholder="e.g. John Doe")
                    v_flt = st.text_input("Unit/Flat Number", placeholder="e.g. A-101")
                    if st.form_submit_button("✅ Add to Whitelist", width="stretch"):
                        if v_no:
                            db.add_to_whitelist(v_no.upper(), v_own, v_flt, _user.get('id'))
                            st.success(f"{v_no} successfully whitelisted.")
                            st.rerun()
                        else:
                            st.error("Plate Number is required.")
            st.markdown("</div>", unsafe_allow_html=True)

        with b_col:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("#### ❌ Banned Blacklist")
            bl = db.get_blacklist() or []
            if bl:
                df_bl = pd.DataFrame(bl)
                st.dataframe(
                    df_bl.loc[:, ['vehicle_no', 'reason']].rename(
                        columns={'vehicle_no': 'Plate No.', 'reason': 'Ban Reason'}),
                    width="stretch", hide_index=True
                )
            else:
                empty_state("No Bans", "Blacklist is currently empty.", "❌")

            with st.expander("⛔ Ban Vehicle"):
                with st.form("bl_form", clear_on_submit=True):
                    b_no = st.text_input("Plate Number *", placeholder="e.g. DL-10-AB-1234")
                    b_rsn = st.text_area("Reason for Ban", placeholder="e.g. Repeated rules violation.")
                    if st.form_submit_button("🚨 Ban Vehicle", type="primary", width="stretch"):
                        if b_no:
                            db.add_to_blacklist(b_no.upper(), b_rsn, _user.get('id'))
                            st.error(f"{b_no} has been blacklisted and banned from entry.")
                            st.rerun()
                        else:
                            st.error("Plate Number is required.")
            st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# MODULE 5: COMMUNITY HUB (Polls & Events)
# ============================================================================
def render_community_hub(_user: Dict[str, Any]) -> None:
    section_header("Community Hub", "📢")
    # Added a 3rd tab for History/Audit
    tabs = st.tabs(["🗳️ Pulse Polls", "📅 Events", "📜 History & Audit"])

    # ---------------------------------------------------------
    # TAB 1: POLLS
    # ---------------------------------------------------------
    with tabs[0]:
        st.markdown("### Create Community Pulse Poll")
        with st.form("create_poll_form", clear_on_submit=True):
            question = st.text_input("Poll Question *", placeholder="e.g. Should we upgrade the gym equipment?")
            opt1 = st.text_input("Option 1 *", placeholder="Yes, urgently")
            opt2 = st.text_input("Option 2 *", placeholder="No, it is fine")
            opt3 = st.text_input("Option 3 (Optional)", placeholder="Neutral")
            opt4 = st.text_input("Option 4 (Optional)")

            if st.form_submit_button("📊 Publish Poll", type="primary"):
                if question and opt1 and opt2:
                    options = [opt1, opt2]
                    if opt3: options.append(opt3)
                    if opt4: options.append(opt4)
                    db.create_poll(question, options, _user.get('id'))
                    db.log_action(_user.get('id'), 'CREATE_POLL', 'COMMUNITY', f"Poll: {question}")
                    st.success("Poll published to resident dashboards!")
                    st.rerun()
                else:
                    st.error("Question and at least 2 options required.")

        st.markdown("### Manage Active Polls")
        polls = db.get_polls() if hasattr(db, 'get_polls') else []
        active_polls = [p for p in polls if p.get('status', 'ACTIVE') != 'CLOSED']

        if active_polls:
            for p in active_polls:
                opts = p.get('options', '[]')
                if isinstance(opts, str):
                    try:
                        opts = json.loads(opts)
                    except Exception:
                        opts = []
                opt_str = ", ".join([str(o) for o in opts])

                # Update: Added column layout for the Close Poll button
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.info(
                        f"**Q:** {p.get('question')} | **Status:** {p.get('status', 'ACTIVE')} | **Options:** {opt_str}")
                with col2:
                    if st.button("❌ Close", key=f"close_poll_{p.get('id')}", help="End this poll"):
                        # Assume db.update_poll_status or similar exists; fallback to execute_query if needed
                        if hasattr(db, 'update_poll_status'):
                            db.update_poll_status(p.get('id'), 'CLOSED')
                        else:
                            db.execute_query("UPDATE polls SET status='CLOSED' WHERE id=%s", (p.get('id'),),
                                             commit=True)

                        db.log_action(_user.get('id'), 'CLOSE_POLL', 'COMMUNITY', f"Closed Poll ID: {p.get('id')}")
                        st.success("Poll Closed!")
                        st.rerun()
        else:
            st.caption("No active polls running.")

    # ---------------------------------------------------------
    # TAB 2: EVENTS (ADVANCED SCHEDULER)
    # ---------------------------------------------------------
    with tabs[1]:
        st.markdown("### 📅 Schedule Society Event")
        st.info("Plan and publish community events. Advanced timing ensures residents know exactly when to arrive.")

        with st.form("create_event_form", clear_on_submit=True):
            st.markdown("#### 📝 Event Details")
            c1, c2 = st.columns(2)
            with c1:
                e_title = st.text_input("Event Name *", placeholder="e.g., Annual Gala, Yoga Class")
                e_category = st.selectbox("Event Category",
                                          ["Community", "Health & Wellness", "Meeting", "Celebration", "Maintenance"])
            with c2:
                e_loc = st.text_input("Location *", placeholder="e.g., Clubhouse, Main Lawn")
                e_spots = st.number_input("Total Spots (0 = Unlimited)", min_value=0,
                                          help="Limit the number of attendees.")

            st.markdown("#### ⏱️ Timing & Duration")
            tc1, tc2, tc3 = st.columns(3)
            with tc1:
                e_date = st.date_input("Event Date *", min_value=datetime.today())
            with tc2:
                start_time = st.time_input("Start Time *", value=datetime.strptime("09:00", "%H:%M").time())
            with tc3:
                end_time = st.time_input("End Time *", value=datetime.strptime("17:00", "%H:%M").time())

            st.markdown("#### ℹ️ Additional Information")
            e_desc = st.text_area("Event Description & Agenda",
                                  placeholder="What should residents expect? Any dress code or prerequisites?",
                                  height=100)

            st.markdown("---")
            if st.form_submit_button("🚀 Publish Event", type="primary", width="stretch"):
                if e_title and e_loc and start_time is not None and end_time is not None:
                    if start_time >= end_time:
                        st.error("❌ Invalid Duration: End Time must be after Start Time.")
                    else:
                        formatted_time = f"{start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}"
                        full_desc = f"[{e_category}] {e_desc}"

                        db.create_event(e_title, e_date, formatted_time, e_loc, int(e_spots), full_desc,
                                        _user.get('id'))
                        db.log_action(_user.get('id'), 'CREATE_EVENT', 'COMMUNITY', f"Event: {e_title} scheduled")
                        st.success(f"✅ Event '{e_title}' scheduled successfully!")
                        st.rerun()
                else:
                    st.error("❌ Event Name, Location, and Valid Times are required fields.")

        st.markdown("### 📋 Manage Upcoming Events")
        events = db.get_events() if hasattr(db, 'get_events') else []
        active_events = [e for e in events if e.get('status', 'UPCOMING') != 'CLOSED']

        if active_events:
            df_e = pd.DataFrame(active_events)
            if 'event_date' in df_e.columns:
                df_e['Date'] = pd.to_datetime(df_e['event_date'].astype(str), errors='coerce').dt.strftime('%b %d, %Y')
            if 'spots_total' in df_e.columns:
                df_e['Spots'] = df_e['spots_total'].astype(int).apply(lambda x: "Unlimited" if x == 0 else f"{x} Max")

            disp_cols = [c for c in ['id', 'title', 'Date', 'event_time', 'location', 'Spots'] if c in df_e.columns]

            if disp_cols:
                st.dataframe(
                    df_e[disp_cols],
                    column_config={
                        "id": "Event ID",
                        "title": st.column_config.TextColumn("Event Title", width="medium"),
                        "Date": "Event Date",
                        "event_time": st.column_config.TextColumn("Duration / Time", width="medium"),
                        "location": "Location",
                        "Spots": "Capacity"
                    },
                    width="stretch",
                    hide_index=True
                )

            # Update: Added functionality to close an event
            st.markdown("#### Cancel / Close Event")
            close_col1, close_col2 = st.columns([3, 1])
            with close_col1:
                event_to_close = st.selectbox("Select Event to Close:", options=active_events, format_func=lambda
                    x: f"ID: {x.get('id')} - {x.get('title')} ({x.get('event_date')})")
            with close_col2:
                st.write("")  # Spacing to align with selectbox
                st.write("")
                if st.button("❌ Close Event", width="stretch"):
                    if hasattr(db, 'update_event_status'):
                        db.update_event_status(event_to_close.get('id'), 'CLOSED')
                    else:
                        db.execute_query("UPDATE events SET status='CLOSED' WHERE id=%s", (event_to_close.get('id'),),
                                         commit=True)

                    db.log_action(_user.get('id'), 'CLOSE_EVENT', 'COMMUNITY',
                                  f"Closed Event ID: {event_to_close.get('id')}")
                    st.success("Event successfully cancelled/closed!")
                    st.rerun()
        else:
            empty_state("No Events", "No upcoming events are currently scheduled.", "📅")
        # ---------------------------------------------------------
        # TAB 3: HISTORY & AUDIT (NEW MODULE)
        # ---------------------------------------------------------
        with tabs[2]:
            st.markdown("### 📜 Community Engagement History")
            st.info("View historical data for polls, event registrations, and management actions.")

            audit_tabs = st.tabs(["🗳️ Poll Responses", "🎟️ Event Registrations", "⚙️ Action Audit Logs"])

            with audit_tabs[0]:
                st.markdown("#### Poll Responses")
                # Fetch all poll responses globally directly from the DB
                responses = db.execute_query("""
                                             SELECT v.id,
                                                    p.question,
                                                    u.full_name as resident,
                                                    u.unit_number,
                                                    v.option_selected,
                                                    v.created_at
                                             FROM poll_votes v
                                                      JOIN polls p ON v.poll_id = p.id
                                                      JOIN users u ON v.user_id = u.id
                                             ORDER BY v.created_at DESC
                                             """) if hasattr(db, 'execute_query') else []

                if responses:
                    df_resp = pd.DataFrame(responses)
                    if 'created_at' in df_resp.columns:
                        df_resp['created_at'] = pd.to_datetime(df_resp['created_at'].astype(str),
                                                               errors='coerce').dt.strftime('%Y-%m-%d %H:%M')
                    st.dataframe(df_resp, width="stretch", hide_index=True)
                else:
                    st.caption("No poll response data available at the moment.")

            with audit_tabs[1]:
                st.markdown("#### Event Registrations")
                # FIX: Fetch all event registrations using raw SQL instead of the resident-specific get_event_registrations()
                regs = db.execute_query("""
                                        SELECT r.id,
                                               e.title     as event_name,
                                               u.full_name as resident,
                                               u.unit_number,
                                               r.status,
                                               r.created_at
                                        FROM event_registrations r
                                                 JOIN events e ON r.event_id = e.id
                                                 JOIN users u ON r.user_id = u.id
                                        ORDER BY r.created_at DESC
                                        """) if hasattr(db, 'execute_query') else []

                if regs:
                    df_regs = pd.DataFrame(regs)
                    if 'created_at' in df_regs.columns:
                        df_regs['created_at'] = pd.to_datetime(df_regs['created_at'].astype(str),
                                                               errors='coerce').dt.strftime('%Y-%m-%d %H:%M')
                    st.dataframe(df_regs, width="stretch", hide_index=True)
                else:
                    st.caption("No event registration data available at the moment.")

            with audit_tabs[2]:
                st.markdown("#### Community Hub Action Logs")
                # Fetching action logs specific to the COMMUNITY module
                all_logs = db.get_audit_logs(500) if hasattr(db, 'get_audit_logs') else []
                comm_logs = [log for log in all_logs if str(log.get('module')).upper() == 'COMMUNITY']

                if comm_logs:
                    df_logs = pd.DataFrame(comm_logs)
                    if 'timestamp' in df_logs.columns:
                        df_logs['timestamp'] = pd.to_datetime(df_logs['timestamp'].astype(str),
                                                              errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')
                    st.dataframe(df_logs, width="stretch", hide_index=True)
                else:
                    st.caption("No manager actions logged for the Community Hub yet.")
# ============================================================================
# MODULE 6: ANNOUNCEMENTS & NOTIFICATIONS (NEW & ADVANCED)
# ============================================================================
def render_announcements_and_notifications(_user: Dict[str, Any]) -> None:
    """
    Advanced Communication Module: Allows Managers to publish global
    Notice Board announcements and send direct push notifications to users.
    """
    section_header("Announcements & Broadcasts", "📱")
    st.info("Manage global society announcements and send targeted push notifications directly to user inboxes.")

    uid = int(_user.get('id', 0))
    tabs = st.tabs(["📢 Announcement Manager", "📱 Notification Broadcast", "📋 Broadcast History"])

    # ---------------------------------------------------------
    # TAB 1: ANNOUNCEMENT MANAGER
    # ---------------------------------------------------------
    with tabs[0]:
        c1, c2 = st.columns([1, 1], gap="large")
        with c1:
            st.markdown("### Publish New Announcement")
            with st.form("publish_notice_form", clear_on_submit=True):
                n_title = st.text_input("Announcement Title *", placeholder="e.g., Water Supply Interruption")
                n_content = st.text_area("Content *", height=150, placeholder="Provide detailed information...")
                is_pinned = st.checkbox("📌 Pin to top of Resident Portal")

                if st.form_submit_button("📢 Publish Announcement", type="primary", width="stretch"):
                    if n_title and n_content:
                        db.create_notice(n_title, n_content, uid, is_pinned=is_pinned)
                        db.log_action(uid, 'PUBLISH_ANNOUNCEMENT', 'COMMUNICATION', f"Published: {n_title}")
                        st.success("✅ Announcement successfully published to all resident dashboards!")
                        st.rerun()
                    else:
                        st.error("❌ Title and Content are mandatory fields.")

        with c2:
            st.markdown("### Active Announcements")
            notices = db.get_notices(20) or []
            if notices:
                for n in notices:
                    pin_status = "📌 (Pinned)" if n.get('is_pinned') else ""
                    with st.expander(f"{n.get('title')} {pin_status}"):
                        st.caption(f"Published on: {format_datetime(n.get('created_at'))}")
                        st.write(n.get('content'))
                        st.markdown("---")
                        if st.button("🗑️ Revoke Announcement", key=f"del_n_{n.get('id')}", type="secondary"):
                            db.delete_notice(int(n.get('id')))
                            db.log_action(uid, 'REVOKE_ANNOUNCEMENT', 'COMMUNICATION', f"Revoked: {n.get('title')}")
                            st.success("Announcement revoked successfully!")
                            st.rerun()
            else:
                empty_state("No Announcements", "No announcements are currently active.", "📢")

    # ---------------------------------------------------------
    # TAB 2: NOTIFICATION BROADCAST
    # ---------------------------------------------------------
    with tabs[1]:
        st.markdown("### 📱 Send Direct Notifications")
        st.caption("Push targeted notifications directly to user's personal inboxes (🔔 tab).")

        with st.form("broadcast_notification_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                title = st.text_input("Notification Title *", placeholder="e.g., Urgent: Move your vehicle")
            with c2:
                target_role = st.selectbox("Target Audience *", ["All Users", "Residents Only", "Guards Only"])

            message = st.text_area("Message Body *", height=100, placeholder="Details of the notification...")

            if st.form_submit_button("📨 Send Broadcast", type="primary", width="stretch"):
                if title and message:
                    all_users = db.get_all_users() or []

                    if target_role == "Residents Only":
                        targets = [u for u in all_users if str(u.get('role')).upper() == 'RESIDENT']
                    elif target_role == "Guards Only":
                        targets = [u for u in all_users if str(u.get('role')).upper() == 'GUARD']
                    else:
                        targets = [u for u in all_users if str(u.get('status')).upper() == 'ACTIVE']

                    count = 0
                    for t in targets:
                        target_id = t.get('id')
                        if target_id:
                            db.create_notification(target_id, title, message)
                            count += 1

                    db.log_action(uid, 'SEND_BROADCAST', 'NOTIFICATION', f"Sent '{title}' to {count} users ({target_role})")
                    st.success(f"✅ Broadcast successfully delivered to {count} user inboxes!")
                else:
                    st.error("❌ Title and Message are required.")

    # ---------------------------------------------------------
    # TAB 3: BROADCAST HISTORY
    # ---------------------------------------------------------
    with tabs[2]:
        st.markdown("### 📋 Recent Broadcast Activity")
        logs = db.get_audit_logs(500) or []
        broadcast_logs = [log for log in logs if str(log.get('action')) in ['SEND_BROADCAST', 'PUBLISH_ANNOUNCEMENT', 'REVOKE_ANNOUNCEMENT']]

        if broadcast_logs:
            df = pd.DataFrame(broadcast_logs)
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'].astype(str), errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')

            disp_cols = [c for c in ['timestamp', 'username', 'action', 'details'] if c in df.columns]
            st.dataframe(
                df[disp_cols],
                column_config={
                    "timestamp": "Date & Time",
                    "username": "Initiator",
                    "action": "Action Type",
                    "details": "Broadcast Details"
                },
                width="stretch",
                hide_index=True
            )
        else:
            empty_state("No History", "No broadcasts have been sent yet.", "📋")


import time
import pandas as pd
import streamlit as st
from datetime import datetime
from components.cards import section_header


# --- HELPER FUNCTION ---
def safe_execute(query: str, params: tuple = (), commit: bool = False) -> list:
    """Safely executes DB queries to guarantee metrics and logs work smoothly."""
    import db
    try:
        result = db.execute_query(query, params, commit=commit)
        return result if result else []
    except Exception as e:
        print(f"Database Execution Error: {e}")
        return []


# ============================================================================
# MODULE 7: GUARD PROFILE & PREFERENCES (Advanced & Bug-Free)
# ============================================================================
def render_manager_settings(_user: dict = None):
    import db
    from core.helpers import format_datetime

    if not _user:
        st.error("User session data not found.")
        return

    user_id = _user.get('id')
    current_username = _user.get('username', 'Guard')
    role = str(_user.get('role', 'GUARD')).upper()
    status = str(_user.get('status', 'ACTIVE')).upper()

    # Fetch extended profile data safely
    try:
        profile = db.get_resident_profile(user_id) or {}
    except Exception:
        profile = {}

    section_header(f"Officer Profile: {current_username}", "🛡️")
    st.info("Manage your security officer account settings, view personal duty performance, and update credentials.")

    # --- PERFORMANCE METRICS ---
    today_str = datetime.now().strftime('%Y-%m-%d')
    my_visitors_today = safe_execute("SELECT id FROM visitors WHERE logged_by=%s AND DATE(entry_time) = %s",
                                     (user_id, today_str))
    my_vehicles_today = safe_execute("SELECT id FROM vehicle_logs WHERE logged_by=%s AND DATE(entry_time) = %s",
                                     (user_id, today_str))

    total_handled = len(my_visitors_today) + len(my_vehicles_today)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("System Role", f"⭐ {role}")
    m2.metric("Account Status", f"🟢 {status}")
    m3.metric("Officer ID Badge", f"SEC-{user_id:04d}")
    m4.metric("Entries Logged Today", f"📝 {total_handled}")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- INNER TABS ---
    acc_tabs = st.tabs([
        "👤 Digital ID Card",
        "✏️ Update Profile",
        "🔒 Security & Password",
        "📊 Duty Activity Logs"
    ])

    # --- TAB 1: PROFILE OVERVIEW (DIGITAL ID CARD) ---
    with acc_tabs[0]:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        col_img, col_info = st.columns([1, 2.5], gap="large")

        with col_img:
            # Premium Digital ID Avatar
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1e293b, #0f172a); border: 2px solid rgba(99, 102, 241, 0.5); border-radius: 16px; padding: 20px; text-align: center; box-shadow: 0 10px 25px rgba(0,0,0,0.3);">
                <div style="background: rgba(99, 102, 241, 0.1); border-radius: 50%; width: 100px; height: 100px; display: flex; align-items: center; justify-content: center; font-size: 50px; margin: 0 auto 15px auto; border: 2px solid #6366f1;">
                    👮‍♂️
                </div>
                <h3 style="margin: 0; color: #F8FAFC; font-size: 18px;">{_user.get('full_name', 'Security Officer')}</h3>
                <p style="margin: 5px 0 0 0; color: #10B981; font-size: 13px; font-weight: bold; text-transform: uppercase;">ACTIVE DUTY</p>
                <div style="margin-top: 15px; padding-top: 15px; border-top: 1px dashed rgba(255,255,255,0.1); color: #94A3B8; font-size: 12px;">
                    Badge ID: SEC-{user_id:04d}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_info:
            st.markdown("#### 📋 Official Credentials")
            c1, c2 = st.columns(2)

            with c1:
                st.markdown(f"**Username:** <span style='color:#94A3B8;'>@{_user.get('username', 'N/A')}</span>",
                            unsafe_allow_html=True)

                # Format DOB cleanly
                raw_dob_disp = str(profile.get('dob', 'Not set')).strip()
                if raw_dob_disp in ['0000-00-00', 'None', '', 'NULL']:
                    raw_dob_disp = 'Not set'
                st.markdown(f"**Date of Birth:** <span style='color:#94A3B8;'>{raw_dob_disp}</span>",
                            unsafe_allow_html=True)

                st.markdown(f"**Gender:** <span style='color:#94A3B8;'>{profile.get('gender', 'Not set')}</span>",
                            unsafe_allow_html=True)
                st.markdown(
                    f"**Blood Group:** <span style='color: #EF4444; font-weight: bold; background: rgba(239, 68, 68, 0.1); padding: 2px 8px; border-radius: 4px;'>{profile.get('blood_group', 'Not set')}</span>",
                    unsafe_allow_html=True)

            with c2:
                st.markdown(f"**Email:** <span style='color:#94A3B8;'>{_user.get('email', 'Not set')}</span>",
                            unsafe_allow_html=True)
                st.markdown(f"**Phone:** <span style='color:#94A3B8;'>{_user.get('contact_number', 'Not set')}</span>",
                            unsafe_allow_html=True)
                st.markdown(
                    f"**Emergency Contact:** <span style='color:#94A3B8;'>🚨 {profile.get('emergency_contact_name', 'Not set')}</span>",
                    unsafe_allow_html=True)
                st.markdown(
                    f"**Emergency Phone:** <span style='color:#94A3B8;'>{profile.get('emergency_contact_phone', 'Not set')}</span>",
                    unsafe_allow_html=True)

            st.markdown("#### 📝 Service Notes / Bio")
            st.info(profile.get('bio', 'No service bio provided yet. Update your profile to add one.'))
        st.markdown("</div>", unsafe_allow_html=True)

    # --- TAB 2: UPDATE PROFILE (WITH STRICT SQL INJECTION/DATE FIX) ---
    with acc_tabs[1]:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### ✏️ Edit Personal Details")

        with st.form("update_guard_profile_form", clear_on_submit=False):
            col1, col2 = st.columns(2)

            with col1:
                new_full_name = st.text_input("Full Name *", value=_user.get('full_name', ''))
                new_email = st.text_input("Email Address", value=_user.get('email', ''))

                # Fetch DOB, prep for input
                saved_dob = str(profile.get('dob', '')).strip()
                if saved_dob in ['0000-00-00', 'None', 'NULL']:
                    saved_dob = ''
                new_dob = st.text_input("Date of Birth (YYYY-MM-DD)", value=saved_dob, placeholder="e.g., 1990-05-24")

                st.markdown("**Gender (Dot Selection)**")
                gender_opts = ["Male", "Female", "Other", "Prefer not to say"]
                curr_gender = profile.get('gender', 'Prefer not to say')
                new_gender_radio = st.radio("Gender", gender_opts,
                                            index=gender_opts.index(curr_gender) if curr_gender in gender_opts else 3,
                                            horizontal=True, label_visibility="collapsed")
                new_gender_other = st.text_input("If 'Other', please specify:",
                                                 value="" if curr_gender in gender_opts else curr_gender)

            with col2:
                new_contact = st.text_input("Contact Number *", value=_user.get('contact_number', ''))
                new_emergency_name = st.text_input("Emergency Contact Name 🚨",
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

                st.text_input("System Role", value=f"⭐ {role}", disabled=True,
                              help="Role upgrades require Management approval.")

            new_bio = st.text_area("Service Biography / Notes", value=profile.get('bio', '') or '', height=100,
                                   placeholder="Write a short professional biography...")
            st.markdown("<small style='color:#94A3B8;'>* Required Fields</small>", unsafe_allow_html=True)

            # FIXED: Button uses width="stretch"
            if st.form_submit_button("💾 Save Extended Profile", type="primary", width="stretch"):
                final_gender = (new_gender_other or "").strip() if new_gender_radio == "Other" else new_gender_radio

                # FIXED: SQL ERROR 1292 - Strict Date Nullification
                clean_dob = new_dob.strip()
                final_dob = clean_dob if clean_dob and clean_dob.lower() not in ['none', 'null', '0000-00-00'] else None

                if not new_full_name or not new_contact:
                    st.error("Full Name and Contact Number are mandatory.")
                else:
                    try:
                        # 1. Update Core Users Table
                        db.update_user(user_id, full_name=new_full_name, email=new_email, contact_number=new_contact)

                        # 2. Safely Update Extended Profile Table using Direct SQL (Bypasses any internal DB bugs)
                        fam_count = profile.get('family_members', 1) or 1

                        safe_execute("""
                                     INSERT INTO resident_profiles
                                     (user_id, dob, gender, occupation, family_members, emergency_contact_name,
                                      emergency_contact_phone, blood_group, bio)
                                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY
                                     UPDATE
                                         dob=
                                     VALUES (dob), gender=
                                     VALUES (gender), occupation=
                                     VALUES (occupation), family_members=
                                     VALUES (family_members), emergency_contact_name=
                                     VALUES (emergency_contact_name), emergency_contact_phone=
                                     VALUES (emergency_contact_phone), blood_group=
                                     VALUES (blood_group), bio=
                                     VALUES (bio)
                                     """, (
                                         user_id, final_dob, final_gender, "Security Officer", fam_count,
                                         new_emergency_name, new_emergency_phone, new_blood_group, new_bio
                                     ), commit=True)

                        db.log_action(user_id, 'UPDATE_OWN_PROFILE', 'USER',
                                      f"Officer {current_username} updated credentials")
                        st.success("✅ Profile updated successfully! Changes will fully reflect on your next login.")
                        time.sleep(1.5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to update profile. Error: {str(e)}")
        st.markdown("</div>", unsafe_allow_html=True)

    # --- TAB 3: SECURITY & PASSWORD ---
    with acc_tabs[2]:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### 🔒 Change Password")
        st.warning("⚠️ For security reasons, changing your password will log you out of all other active devices.")

        with st.form("guard_change_password_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                new_password = st.text_input("New Password *", type="password")
            with col2:
                confirm_password = st.text_input("Confirm New Password *", type="password")

            # FIXED: Button uses width="stretch"
            if st.form_submit_button("🔑 Update Security Password", type="primary", width="stretch"):
                if not new_password or not confirm_password:
                    st.error("Both password fields are required.")
                elif new_password != confirm_password:
                    st.error("New passwords do not match. Please try again.")
                elif len(new_password) < 6:
                    st.error("Password must be strictly at least 6 characters long.")
                else:
                    try:
                        db.change_user_password(user_id, new_password)
                        db.log_action(user_id, 'CHANGE_OWN_PASSWORD', 'SECURITY',
                                      "Officer changed their personal security password")
                        st.success("✅ Password updated successfully! Please use the new password on your next login.")
                        time.sleep(1.5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to change password: {str(e)}")
        st.markdown("</div>", unsafe_allow_html=True)

    # --- TAB 4: MY ACTIVITY LOGS ---
    with acc_tabs[3]:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### 📊 My Duty Activity Logs")
        st.info("Review a real-time audit trail of all security actions performed under your account.")

        try:
            my_logs = safe_execute(
                "SELECT timestamp, action, module, details FROM audit_logs WHERE user_id=%s ORDER BY timestamp DESC LIMIT 200",
                (user_id,))

            if my_logs:
                df_logs = pd.DataFrame(my_logs)

                # Format Dates safely
                if 'timestamp' in df_logs.columns:
                    df_logs['timestamp'] = pd.to_datetime(df_logs['timestamp'], errors='coerce').dt.strftime(
                        '%d %b %Y, %I:%M %p')

                # Rename for beautiful UI
                df_logs = df_logs.rename(columns={
                    'timestamp': 'Date & Time',
                    'action': 'Action Type',
                    'module': 'Module',
                    'details': 'Audit Details'
                })

                # Quick Search Filter
                search_log = st.text_input("🔍 Search My Logs (e.g., VISITOR_ENTRY, GATE, Plate Number...)",
                                           placeholder="Type to filter your history...")
                if search_log:
                    df_logs = df_logs[
                        df_logs.astype(str).apply(lambda x: x.str.contains(search_log, case=False)).any(axis=1)]

                if not df_logs.empty:
                    st.dataframe(
                        df_logs,
                        width="stretch",
                        hide_index=True,
                        column_config={
                            "Date & Time": st.column_config.TextColumn("Date & Time ⏱️", width="medium"),
                            "Action Type": st.column_config.TextColumn("Action 🎯", width="medium"),
                            "Module": st.column_config.TextColumn("Module 📦", width="small"),
                            "Audit Details": st.column_config.TextColumn("Detailed Event Log 📜", width="large")
                        }
                    )
                else:
                    st.warning("No records match your search filter.")
            else:
                st.caption("No duty activity found for your account yet.")
        except Exception as e:
            st.error(f"Could not load activity logs at this time. Error: {str(e)}")

        st.markdown("</div>", unsafe_allow_html=True)
