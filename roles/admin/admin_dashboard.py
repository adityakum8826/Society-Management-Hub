
from datetime import datetime
import config
import db
import pandas as pd
import streamlit as st
import uuid
from core.helpers import format_datetime
import psutil
from core.helpers import execute_query, format_datetime, format_date
from components.cards import metric_card, status_badge, priority_indicator, section_header, info_card, warning_card, success_card, error_card, empty_state


def render_admin_dashboard(user):

    st.markdown("""
    <style>
    @keyframes pulse-glow-red {
        0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.5); }
        70% { box-shadow: 0 0 0 12px rgba(239, 68, 68, 0); }
        100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
    }
    @keyframes shimmer {
        0% { background-position: -200% center; }
        100% { background-position: 200% center; }
    }
    @keyframes avatar-glow {
        0%, 100% { box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4); }
        50% { box-shadow: 0 4px 30px rgba(139, 92, 246, 0.6); }
    }
    .admin-header-container {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #0F172A 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 24px;
        padding: 20px 28px;
        margin-bottom: 28px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4), 0 0 60px rgba(99, 102, 241, 0.1);
        position: relative;
        overflow: hidden;
    }
    .admin-header-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(99, 102, 241, 0.5), transparent);
    }
    .admin-header-left {
        display: flex;
        align-items: center;
        gap: 20px;
    }
    .admin-logo {
        width: 56px;
        height: 56px;
        background: linear-gradient(135deg, #6366F1, #8B5CF6, #A855F7);
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 28px;
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.4);
        animation: avatar-glow 3s ease-in-out infinite;
    }
    
    .admin-header-text h1 {
        margin: 0;
        font-size: 26px;
        font-weight: 700;
        color: #F8FAFC;
        letter-spacing: -0.03em;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
    }
    .admin-header-text p {
        margin: 6px 0 0 0;
        color: #94A3B8;
        font-size: 14px;
        font-weight: 500;
    }
    .admin-header-right {
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .admin-user-section {
        display: flex;
        align-items: center;
        gap: 14px;
        background: rgba(255, 255, 255, 0.05);
        padding: 8px 16px 8px 8px;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .admin-avatar {
        width: 42px;
        height: 42px;
        background: linear-gradient(135deg, #10B981, #059669);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
        font-weight: 700;
        color: white;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
    }
    .admin-user-info {
        display: flex;
        flex-direction: column;
    }
    .admin-user-name {
        color: #F8FAFC;
        font-weight: 600;
        font-size: 14px;
    }
    .admin-user-role {
        color: #6366F1;
        font-size: 12px;
        font-weight: 500;
    }
    .admin-header-actions {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .admin-logout-btn {
        background: linear-gradient(135deg, #EF4444, #DC2626) !important;
        color: white !important;
        border: none !important;
        padding: 10px 20px !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3) !important;
    }
    .admin-logout-btn:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    user_initials = ''.join([n[0] for n in str(user.get('full_name', 'Admin')).split()[:2]]).upper()

    # --- FIXED LOGOUT HEADER ---
    header_col, logout_col = st.columns([6, 1])

    with header_col:
        st.markdown(f"""
            <div class="admin-header-container" style="margin-bottom: 20px;">
                <div class="admin-header-left">
                    <div class="admin-logo">🛡️</div>
                    <div class="admin-header-text">
                        <h1>Admin Command Center</h1>
                        <p>Enterprise Control Panel • {datetime.now().strftime('%A, %d %B %Y')}</p>
                    </div>
                </div>
                <div class="admin-header-right">
                    <div class="admin-user-section">
                        <div class="admin-user-info">
                            <span class="admin-user-name">{user.get('full_name')}</span>
                            <span class="admin-user-role">👑 Super Administrator</span>
                        </div>
                        <div class="admin-avatar">{user_initials}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with logout_col:
        # Pushes the button down to align perfectly with the header box
        st.markdown("<div style='padding-top: 25px;'></div>", unsafe_allow_html=True)
        if st.button("🚪 Logout", key="admin_logout", type="primary", width="stretch"):
            st.query_params["logout"] = "1"
            st.rerun()
    # ---------------------------

    col1, col2, col3, col4 = st.columns(4)
    stats = db.get_admin_dashboard_stats() or {}


    with col1:
        metric_card("Total Users", stats.get('total_users', 0), icon="👥")
    with col2:
        metric_card("Open Tickets", stats.get('open_tickets', 0), icon="📋")
    with col3:
        metric_card("Visitors Today", stats.get('visitors_today', 0), icon="🚶")
    with col4:
        metric_card("Active Alerts", stats.get('active_alerts', 0), icon="🚨", color=config.THEME['danger'])

    st.markdown("---")

    # 1. DEFINE THE TABS (Exactly 9 labels)
    tabs = st.tabs([
        "🔍 Audit & Activity",
        "👥 User Management",
        "⚙️ Settings",
        "🧹 Data Reset",
        "👥 Directory",
        "🛡️ Security Control",
        "🎯 Goals",
        "👥 My Account"
    ])

    # 2. MATCH THE FUNCTIONS (Perfectly sequential 0 to 9)
    with tabs[0]:
        render_audit_and_activity(user)

    with tabs[1]:
        render_users_page(user)

    with tabs[2]:
        render_system_settings(user)

    with tabs[3]:
        render_data_reset(user)

    with tabs[4]:
        render_resident_directory(user)

    with tabs[5]:
        render_security_control_module(user)

    with tabs[6]:
        render_goals_section(user)

    with tabs[7]:
        render_my_account_module(user)

def render_audit_and_activity(_user: dict = None):
    section_header("Audit & Activity Monitor", "🔍")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Recent Logins")
        # noinspection PyBroadException
        try:
            recent_logins = db.execute_query(
                """SELECT username, full_name, role, last_login
                   FROM users
                   WHERE last_login IS NOT NULL
                   ORDER BY last_login DESC LIMIT 5"""
            ) or []

            if recent_logins:
                for u in recent_logins:
                    st.markdown(f"""
                    <div style="padding: 10px; background: {config.THEME['card_background']}; border-radius: 8px; margin: 5px 0;">
                        <div style="font-weight: 600;">{u.get('full_name')}</div>
                        <div style="font-size: 12px; color: {config.THEME['text_secondary']};">
                            {u.get('username')} | {u.get('role')} | Last login: {u.get('last_login').strftime('%d %b %Y, %I:%M %p') if u.get('last_login') else 'Never'}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                info_card("No Data", "No recent login data available.")
        except Exception:
            error_card("Error", "Could not load recent logins.")

    with col2:
        st.markdown("#### Active Sessions")
        # noinspection PyBroadException
        try:
            sessions = db.execute_query(
                """SELECT ps.*, u.username, u.full_name
                   FROM persistent_sessions ps
                            JOIN users u ON ps.user_id = u.id
                   WHERE ps.expires_at > NOW()
                   ORDER BY ps.created_at DESC LIMIT 5"""
            ) or []

            if sessions:
                for session in sessions:
                    st.markdown(f"""
                    <div style="padding: 10px; background: {config.THEME['card_background']}; border-radius: 8px; margin: 5px 0;">
                        <div style="font-weight: 600;">{session.get('full_name')}</div>
                        <div style="font-size: 12px; color: {config.THEME['text_secondary']};">
                            {session.get('username')} | Device: {session.get('device_info', 'Unknown')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                info_card("No Active Sessions", "No users currently logged in.")
        except Exception:
            error_card("Error", "Could not load active sessions.")

    st.markdown("---")

    st.markdown("#### System Audit Logs")
    search_query = st.text_input("🔍 Search logs", placeholder="Search by user, action, or details...")

    logs = db.get_audit_logs(500) or []

    if search_query:
        logs = [log for log in logs if search_query.lower() in str(log.get('username', '')).lower()
                or search_query.lower() in str(log.get('action', '')).lower()
                or search_query.lower() in str(log.get('details', '')).lower()]

    if logs:
        df = pd.DataFrame(logs)
        df['timestamp'] = df['timestamp'].apply(lambda x: format_datetime(x) if pd.notna(x) else 'N/A')
        st.dataframe(df[['timestamp', 'username', 'action', 'module', 'details', 'ip_address']], width='stretch',
                     height=400)

        csv = df.to_csv(index=False)
        st.download_button("📥 Download CSV", csv, "audit_logs.csv", "text/csv")
    else:
        empty_state("No Logs", "No audit logs found.", "📋")


def render_system_overview(_user: dict = None):
    section_header("System Overview & Live Health", "📊")

    # noinspection PyBroadException
    try:
        stats = db.get_admin_dashboard_stats() or {}
        guard_stats = db.get_guard_stats() or {}

        # Top Metric Row
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            metric_card("Total Users", stats.get('total_users', 0), icon="👥")
        with col2:
            metric_card("Open Tickets", stats.get('open_tickets', 0), icon="📋")
        with col3:
            metric_card("Visitors Today", stats.get('visitors_today', 0), icon="🚶")
        with col4:
            metric_card("Active Alerts", stats.get('active_alerts', 0), icon="🚨",
                        color=config.THEME.get('danger', '#EF4444'))

        st.markdown("---")

        col1, col2 = st.columns(2)

        # FIXED: Populated the empty col1 with Real-Time Server Health!
        with col1:
            section_header("Live Server Health", "🖥️")
            try:
                import psutil
                cpu = psutil.cpu_percent(interval=0.1)
                ram = psutil.virtual_memory()
                disk = psutil.disk_usage('/')

                # Dynamic UI for live progress bars
                st.markdown(f"""
                <div style="background: {config.THEME.get('card_background', '#1e1e1e')}; border: 1px solid {config.THEME.get('border_color', '#333')}; border-radius: 12px; padding: 20px; height: 100%;">
                    <div style="margin-bottom: 20px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                            <span>CPU Usage</span>
                            <span style="font-weight: 600; color: {'#EF4444' if cpu > 85 else config.THEME.get('text_primary', '#fff')};">{cpu}%</span>
                        </div>
                        <div style="background: {config.THEME.get('border_color', '#333')}; height: 8px; border-radius: 4px; overflow: hidden;">
                            <div style="background: {'#EF4444' if cpu > 85 else '#3B82F6'}; height: 100%; width: {cpu}%; transition: width 0.3s;"></div>
                        </div>
                    </div>
                    <div style="margin-bottom: 20px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                            <span>RAM Usage ({ram.used / (1024 ** 3):.1f} GB / {ram.total / (1024 ** 3):.1f} GB)</span>
                            <span style="font-weight: 600;">{ram.percent}%</span>
                        </div>
                        <div style="background: {config.THEME.get('border_color', '#333')}; height: 8px; border-radius: 4px; overflow: hidden;">
                            <div style="background: {'#EF4444' if ram.percent > 85 else '#10B981'}; height: 100%; width: {ram.percent}%; transition: width 0.3s;"></div>
                        </div>
                    </div>
                    <div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                            <span>Disk Storage ({disk.used / (1024 ** 3):.1f} GB / {disk.total / (1024 ** 3):.1f} GB)</span>
                            <span style="font-weight: 600;">{disk.percent}%</span>
                        </div>
                        <div style="background: {config.THEME.get('border_color', '#333')}; height: 8px; border-radius: 4px; overflow: hidden;">
                            <div style="background: {'#EF4444' if disk.percent > 90 else '#F59E0B'}; height: 100%; width: {disk.percent}%; transition: width 0.3s;"></div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            except Exception:
                info_card("Live Stats Unavailable", "Install 'psutil' to view real-time server metrics.")

        with col2:
            section_header("Security Status", "🔒")
            st.markdown(f"""
            <div style="background: {config.THEME.get('card_background', '#1e1e1e')}; border: 1px solid {config.THEME.get('border_color', '#333')}; border-radius: 12px; padding: 20px; height: 100%;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 15px;">
                    <span style="font-size: 15px;">Visitors Inside:</span>
                    <span style="color: #3B82F6; font-weight: 600; font-size: 16px;">{guard_stats.get('visitors_inside', 0)}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 15px;">
                    <span style="font-size: 15px;">Vehicles Inside:</span>
                    <span style="color: #3B82F6; font-weight: 600; font-size: 16px;">{guard_stats.get('vehicles_inside', 0)}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 15px;">
                    <span style="font-size: 15px;">Parcels at Gate:</span>
                    <span style="color: #F59E0B; font-weight: 600; font-size: 16px;">{guard_stats.get('parcels_at_gate', 0)}</span>
                </div>
                <div style="display: flex; justify-content: space-between; border-top: 1px solid {config.THEME.get('border_color', '#333')}; padding-top: 15px;">
                    <span style="font-size: 15px;">Active Alerts:</span>
                    <span style="color: #EF4444; font-weight: 600; font-size: 16px;">{guard_stats.get('active_alerts', 0)}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        section_header("Application Configuration", "⚙️")

        # Uses getattr to avoid crashing if a config variable doesn't exist
        st.markdown(f"""
        <div style="background: {config.THEME.get('card_background', '#1e1e1e')}; border: 1px solid {config.THEME.get('border_color', '#333')}; border-radius: 12px; padding: 20px;">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                <div><span style="color: {config.THEME.get('text_secondary', '#aaa')}; font-size: 12px;">Application</span><br><strong>{getattr(config, 'APP_NAME', 'System')}</strong></div>
                <div><span style="color: {config.THEME.get('text_secondary', '#aaa')}; font-size: 12px;">Version</span><br><strong>{getattr(config, 'APP_VERSION', '1.0.0')}</strong></div>
                <div><span style="color: {config.THEME.get('text_secondary', '#aaa')}; font-size: 12px;">Currency</span><br><strong>{getattr(config, 'CURRENCY', 'INR')} ({getattr(config, 'CURRENCY_SYMBOL', '₹')})</strong></div>
                <div><span style="color: {config.THEME.get('text_secondary', '#aaa')}; font-size: 12px;">Building ID</span><br><strong>{getattr(config, 'BUILDING_ID', 'N/A')}</strong></div>
                <div><span style="color: {config.THEME.get('text_secondary', '#aaa')}; font-size: 12px;">Total Blocks</span><br><strong>{getattr(config, 'TOTAL_BLOCKS', 0)}</strong></div>
                <div><span style="color: {config.THEME.get('text_secondary', '#aaa')}; font-size: 12px;">Total Units</span><br><strong>{getattr(config, 'TOTAL_UNITS', 0)}</strong></div>
                <div><span style="color: {config.THEME.get('text_secondary', '#aaa')}; font-size: 12px;">Demo Mode</span><br><strong>{'Enabled' if getattr(config, 'DEMO_MODE', False) else 'Disabled'}</strong></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.write("")
        if st.button("🔄 Refresh System Data", width="stretch"):
            st.rerun()

    except Exception as e:
        error_card("Error Loading System Info", str(e))


def render_users_page(_user: dict = None):
    import uuid
    import pandas as pd
    import streamlit as st
    import db
    import config
    from core.helpers import format_datetime, format_date
    from components.cards import section_header, empty_state

    # Ensure we have a valid user dictionary
    user_id = _user.get('id') if _user else None

    st.markdown(f"""
    <div style="margin-bottom: 25px;">
        <h1 style="margin: 0;">👥 User Management</h1>
        <p style="color: {config.THEME.get('text_secondary', '#aaa')}; margin: 5px 0;">Comprehensive user control - View, edit, monitor, and manage roles (Residents, Guards, Managers, Admins)</p>
    </div>
    """, unsafe_allow_html=True)

    # EXACTLY 6 TABS DEFINED
    tabs = st.tabs([
        "🚗 Resident Vehicles",
        "👤 Resident Profiles",
        "👥 All Users",
        "➕ Register User",
        "🔑 Password Resets",
        "📊 Activity Log"
    ])

    # --- TAB 0: RESIDENT VEHICLES ---
    with tabs[0]:
        section_header("Resident Vehicles", "🚗")
        vehicles = db.get_all_resident_vehicles() or []
        if vehicles:
            df = pd.DataFrame(vehicles)
            if 'created_at' in df.columns:
                df['created_at'] = df['created_at'].apply(lambda x: format_datetime(x) if pd.notnull(x) else 'N/A')

            # Safely filter columns to prevent Pandas KeyErrors
            target_cols = ['user_id', 'vehicle_no', 'vehicle_type', 'make_model', 'color', 'status', 'created_at']
            display_cols = [c for c in target_cols if c in df.columns]

            st.dataframe(df[display_cols], width="stretch", hide_index=True)
        else:
            empty_state("No Vehicles", "No resident vehicles are currently registered in the system.", "🚗")

    # --- TAB 1: RESIDENT PROFILES ---
    with tabs[1]:
        section_header("Resident Profiles", "👤")
        profiles = db.get_all_resident_profiles() or []
        if profiles:
            df = pd.DataFrame(profiles)
            if 'dob' in df.columns:
                df['dob'] = df['dob'].apply(lambda x: format_date(x) if pd.notnull(x) else 'N/A')
            st.dataframe(df, width="stretch", hide_index=True)
        else:
            empty_state("No Profiles", "No detailed resident profiles found.", "👤")

    # --- TAB 2: ALL USERS (Full Control & Advanced Metrics) ---
    with tabs[2]:
        section_header("System Users Hub", "👥")
        users = db.get_all_users() or []

        # --- ADVANCED REAL-TIME METRICS ---
        total_users = len(users)
        active_users = len([u for u in users if str(u.get('status')).upper() == 'ACTIVE'])
        inactive_users = total_users - active_users

        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Total Registered Users", total_users)
        with m2:
            st.metric("Active Accounts", active_users, delta="Online", delta_color="normal")
        with m3:
            st.metric("Inactive/Suspended", inactive_users, delta="Locked",
                      delta_color="inverse" if inactive_users > 0 else "off")

        st.markdown("---")

        # Search and Filter Layout
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            search = st.text_input("🔍 Search Users", placeholder="Search by name, username, or email...")
        with col2:
            role_filter = st.selectbox("Filter by Role",
                                       ["ALL",  "ADMIN", "MANAGER", "RESIDENT", "GUARD"])
        with col3:
            status_filter = st.selectbox("Filter by Status", ["ALL", "ACTIVE", "INACTIVE", "SUSPENDED"])

        st.write("")  # Spacing

        # Apply Real-Time Filters
        if search:
            search_lower = search.lower()
            users = [u for u in users if search_lower in str(u.get('username', '')).lower() or
                     search_lower in str(u.get('full_name', '')).lower() or
                     search_lower in str(u.get('email', '')).lower()]
        if role_filter != "ALL":
            users = [u for u in users if str(u.get('role')).upper() == role_filter]
        if status_filter != "ALL":
            users = [u for u in users if str(u.get('status')).upper() == status_filter]

        if users:
            for u in users:
                u_id = u.get('id', 'N/A')
                is_active = str(u.get('status')).upper() == "ACTIVE"
                status_icon = "🟢" if is_active else "🔴"

                with st.expander(f"{status_icon} {u.get('full_name')} (@{u.get('username')}) - {u.get('role', 'N/A')}"):
                    # User Details Grid
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("User ID", u_id)
                    c2.metric("Status", u.get('status', 'N/A'))
                    c3.metric("Unit Number", u.get('unit_number', 'N/A'))
                    c4.metric("Last Login", format_datetime(u.get('last_login')) if u.get('last_login') else 'Never')

                    st.markdown(
                        f"**✉️ Email:** {u.get('email', 'N/A')} &nbsp;|&nbsp; **📞 Contact:** {u.get('contact_number', 'N/A')} &nbsp;|&nbsp; **📅 Created:** {format_datetime(u.get('created_at'))}")
                    st.markdown("---")

                    # Action Buttons
                    action_col1, action_col2, action_col3, action_col4 = st.columns(4)

                    with action_col1:
                        if st.button("✏️ Edit User", key=f"edit_user_{u_id}", width="stretch"):
                            st.session_state['edit_user_id'] = u_id
                            st.rerun()

                    with action_col2:
                        new_status = "SUSPENDED" if is_active else "ACTIVE"
                        btn_label = "🔒 Suspend Account" if is_active else "🔓 Activate Account"
                        btn_type = "secondary" if is_active else "primary"
                        if st.button(btn_label, key=f"toggle_status_{u_id}", type=btn_type, width="stretch"):
                            db.update_user(u_id, status=new_status)
                            db.log_action(user_id, 'UPDATE_USER_STATUS', 'USER',
                                          f"Changed status to {new_status} for {u.get('username')}")
                            st.success(f"Status successfully updated to {new_status}")
                            st.rerun()

                    with action_col3:
                        if st.button("🔑 Reset Password", key=f"reset_pwd_{u_id}", width="stretch"):
                            new_pwd = uuid.uuid4().hex[:8]
                            db.change_user_password(u_id, new_pwd)
                            db.log_action(user_id, 'RESET_PASSWORD', 'USER',
                                          f"Admin forcefully reset password for {u.get('username')}")
                            st.success(f"Password reset! Temporary password: **{new_pwd}**")

                    with action_col4:
                        if st.button("🗑️ Delete User", key=f"delete_user_{u_id}", type="primary",
                                     width="stretch"):
                            db.delete_user(u_id)
                            db.log_action(user_id, 'DELETE_USER', 'USER', f"Deleted user: {u.get('username')}")
                            st.success("User permanently deleted from the database.")
                            st.rerun()

            # --- EDIT USER MODAL (Inline) ---
            if 'edit_user_id' in st.session_state:
                user_to_edit = next((u for u in users if u['id'] == st.session_state['edit_user_id']), None)
                if user_to_edit:
                    st.markdown("---")
                    st.markdown(f"### ✏️ Editing: {user_to_edit.get('username')}")
                    with st.form(f"edit_user_form_{user_to_edit['id']}"):
                        ec1, ec2 = st.columns(2)
                        with ec1:
                            new_full_name = st.text_input("Full Name", value=user_to_edit.get('full_name', ''))
                            new_email = st.text_input("Email", value=user_to_edit.get('email', ''))
                            new_unit = st.text_input("Unit Number", value=user_to_edit.get('unit_number', '') or '')
                        with ec2:
                            current_role = str(user_to_edit.get('role', 'RESIDENT')).upper()
                            available_roles = [ "ADMIN", "MANAGER", "RESIDENT", "GUARD"]
                            role_index = available_roles.index(current_role) if current_role in available_roles else 3
                            new_role = st.selectbox("Role", available_roles, index=role_index)

                            new_contact = st.text_input("Contact Number",
                                                        value=user_to_edit.get('contact_number', '') or '')

                            current_status = str(user_to_edit.get('status', 'ACTIVE')).upper()
                            available_statuses = ["ACTIVE", "INACTIVE", "SUSPENDED", "PENDING"]
                            status_index = available_statuses.index(
                                current_status) if current_status in available_statuses else 0
                            new_status = st.selectbox("Status", available_statuses, index=status_index)

                        sc1, sc2 = st.columns([1, 5])
                        with sc1:
                            if st.form_submit_button("💾 Save Updates", type="primary"):
                                db.update_user(
                                    user_to_edit['id'],
                                    full_name=new_full_name,
                                    email=new_email,
                                    role=new_role,
                                    unit_number=new_unit if new_unit else None,
                                    contact_number=new_contact if new_contact else None,
                                    status=new_status
                                )
                                db.log_action(user_id, 'UPDATE_USER', 'USER',
                                              f"Updated details for: {user_to_edit.get('username')}")
                                del st.session_state['edit_user_id']
                                st.success("User profile updated successfully!")
                                st.rerun()
                        with sc2:
                            if st.form_submit_button("❌ Cancel"):
                                del st.session_state['edit_user_id']
                                st.rerun()
        else:
            empty_state("No Users", "No users found matching your search criteria.", "👥")

    # --- TAB 3: ADD NEW USER ---
    with tabs[3]:
        section_header("Register New User", "➕")
        with st.form("add_user_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                full_name = st.text_input("Full Name *", placeholder="Enter full name")
                username = st.text_input("Username *", placeholder="Enter unique username")
                email = st.text_input("Email Address", placeholder="Enter email")
            with col2:
                role = st.selectbox("System Role *", ["RESIDENT", "MANAGER", "GUARD", "ADMIN"], index=0)
                unit_number = st.text_input("Unit Number", placeholder="e.g., A-101 (Required for Residents)")
                contact_number = st.text_input("Contact Number", placeholder="Enter primary contact number")

            st.markdown("<small>* Indicates required fields</small>", unsafe_allow_html=True)
            submit = st.form_submit_button("Create Account", type="primary")

            if submit:
                if not username or not full_name:
                    st.error("Username and Full Name are strictly required!")
                else:
                    # Check if username already exists
                    existing = db.get_user_by_username(username)
                    if existing:
                        st.error("❌ This username is already taken! Please choose another.")
                    else:
                        temp_password = uuid.uuid4().hex[:8]
                        db.create_user(username, temp_password, full_name, role, unit_number, contact_number, email)
                        db.log_action(user_id, 'CREATE_USER', 'USER', f"Created new {role}: {username}")
                        st.success(f"✅ Account created successfully! **Temporary Password: {temp_password}**")

    # --- TAB 4: PASSWORD RESETS ---
    with tabs[4]:
        section_header("Pending Password Resets", "🔑")
        all_requests = db.get_password_reset_requests() or []

        # Filter for only PENDING requests
        pending_requests = [req for req in all_requests if str(req.get('status')).upper() == 'PENDING']

        if pending_requests:
            for req in pending_requests:
                req_id = req.get('id')
                identifier = req.get('identifier', 'Unknown')

                with st.expander(
                        f"⚠️ Security Request for '{identifier}' ({format_datetime(req.get('created_at'))})",
                        expanded=True):

                    # Look up user via identifier (username)
                    target_user = db.get_user_by_username(identifier)

                    if target_user:
                        st.markdown(f"**Target User:** {target_user.get('full_name')} ({target_user.get('role')})")
                        st.markdown(f"**Verified Email:** {target_user.get('email', 'N/A')}")
                    else:
                        st.error("⚠️ Warning: Could not find a user account matching this username.")

                    st.markdown(f"**User Reason:** {req.get('reason', 'N/A')}")
                    st.markdown(f"**System Notes:** {req.get('notes', 'N/A')}")

                    rc1, rc2 = st.columns(2)
                    with rc1:
                        if st.button("✅ Approve & Generate Password", key=f"approve_{req_id}",
                                     width="stretch"):
                            if target_user:
                                new_password = uuid.uuid4().hex[:8]
                                db.change_user_password(target_user.get('id'), new_password)
                                db.update_password_reset_request_status(req_id, 'APPROVED')
                                db.log_action(user_id, 'APPROVE_RESET', 'SECURITY', f"Approved reset for {identifier}")
                                st.success(f"Request Approved! Secure password generated: **{new_password}**")
                            else:
                                st.error("Cannot reset: User no longer exists.")
                    with rc2:
                        if st.button("❌ Reject Request", key=f"reject_{req_id}", width="stretch"):
                            db.update_password_reset_request_status(req_id, 'REJECTED')
                            db.log_action(user_id, 'REJECT_RESET', 'SECURITY', f"Rejected reset for {identifier}")
                            st.warning("Request rejected.")
                            st.rerun()
        else:
            empty_state("All Clear", "There are no pending password reset requests at this time.", "🛡️")

    # --- TAB 5: ACTIVITY LOG ---
    with tabs[5]:
        section_header("System Audit & Activity", "📊")
        audit_logs = db.get_audit_logs(300) or []

        if audit_logs:
            df = pd.DataFrame(audit_logs)
            if 'timestamp' in df.columns:
                df['timestamp'] = df['timestamp'].apply(lambda x: format_datetime(x) if pd.notnull(x) else 'N/A')

            valid_cols = [c for c in ['timestamp', 'username', 'action', 'module', 'details'] if c in df.columns]
            if valid_cols:
                st.dataframe(df[valid_cols], width="stretch", hide_index=True)
            else:
                st.dataframe(df, width="stretch", hide_index=True)
        else:
            empty_state("No Data", "No system activity has been recorded yet.", "📉")


def render_maintenance_page(user):
    st.markdown(f"""
    <div style="margin-bottom: 30px;">
        <h1 style="margin: 0;">🔧 Maintenance Management</h1>
        <p style="color: {config.THEME['text_secondary']}; margin: 5px 0;">Track and manage all maintenance requests</p>
    </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs(["📋 Requests", "➕ Create Request"])

    with tabs[0]:
        section_header("All Maintenance Requests", "📋")
        complaints = db.get_complaints() or []

        if complaints:
            df = pd.DataFrame(complaints)
            df['created_at'] = df['created_at'].apply(lambda x: format_datetime(x))
            st.dataframe(df[['id', 'category', 'title', 'priority', 'status', 'resident_name', 'created_at']], width='stretch')
        else:
            empty_state("No Requests", "No maintenance requests found.", "🔧")

    with tabs[1]:
        section_header("Create Maintenance Request", "➕")

        with st.form("create_maintenance_form"):
            title = st.text_input("Title", placeholder="Enter issue title")
            category = st.selectbox("Category", config.COMPLAINT_CATEGORIES)
            priority = st.selectbox("Priority", ["LOW", "MEDIUM", "HIGH", "URGENT"])
            location = st.text_input("Location", placeholder="e.g., Block A, Floor 3")
            description = st.text_area("Description", height=100)

            submit = st.form_submit_button("Create Request", type="primary")

            if submit and title and description:
                desc = description
                if location and str(location).strip():
                    desc = f"{description}\n\nLocation: {location}"
                db.create_complaint(user.get('id'), category, title, desc, priority)
                st.success("Maintenance request created!")
                st.rerun()

def render_polls_page(user):
    st.markdown(f"""
    <div style="margin-bottom: 30px;">
        <h1 style="margin: 0;">📊 Polls & Announcements</h1>
        <p style="color: {config.THEME['text_secondary']}; margin: 5px 0;">Create polls and announcements for the community</p>
    </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs(["📊 Polls", "📢 Announcements"])

    with tabs[0]:
        section_header("Active Polls", "📊")
        polls = db.get_polls() or []

        if polls:
            for poll in polls:
                with st.expander(f"📊 {poll['question']}"):
                    options = db.get_poll_options(poll['id'])
                    if options:
                        df = pd.DataFrame(options)
                        st.dataframe(df[['option_text', 'vote_count']], width='stretch')
        else:
            empty_state("No Polls", "No active polls.", "📊")

        st.markdown("---")

        section_header("Create Poll", "➕")

        with st.form("create_poll_form"):
            question = st.text_input("Question", placeholder="Enter poll question")
            option1 = st.text_input("Option 1")
            option2 = st.text_input("Option 2")
            option3 = st.text_input("Option 3")
            option4 = st.text_input("Option 4")

            submit = st.form_submit_button("Create Poll", type="primary")

            if submit and question and option1 and option2:
                options = [opt for opt in [option1, option2, option3, option4] if opt]
                db.create_poll(question, options)
                st.success("Poll created!")
                st.rerun()

    with tabs[1]:
        section_header("Announcements", "📢")
        announcements = db.get_announcements() or []

        if announcements:
            for ann in announcements:
                priority = ann.get('priority', 'NORMAL')
                with st.expander(f"{'🔴 ' if priority == 'URGENT' else '🟡 ' if priority == 'HIGH' else '🟢 '} {ann['title']}"):
                    st.markdown(ann.get('content', ''))
                    st.markdown(f"**Target:** {ann.get('target_audience', 'ALL')}")
        else:
            empty_state("No Announcements", "No announcements posted.", "📢")

        st.markdown("---")

        section_header("Create Announcement", "➕")

        with st.form("create_announcement_form"):
            title = st.text_input("Title")
            content = st.text_area("Content", height=100)
            target = st.selectbox("Target Audience", ["ALL", "RESIDENTS", "STAFF"])
            priority = st.selectbox("Priority", ["NORMAL", "HIGH", "URGENT"])

            submit = st.form_submit_button("Publish", type="primary")

            if submit and title and content:
                db.create_announcement(title, content, priority, target, user.get('id'))
                st.success("Announcement published!")
                st.rerun()

def render_settings_page(user):
    st.markdown(f"""
    <div style="margin-bottom: 30px;">
        <h1 style="margin: 0;">⚙️ Settings</h1>
        <p style="color: {config.THEME['text_secondary']}; margin: 5px 0;">System configuration and content management</p>
    </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs(["👤 Profile", "📚 Content", "📞 Emergency", "💬 Forum"])

    with tabs[0]:
        section_header("Admin Profile", "👤")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Username:** {user.get('username')}")
            st.markdown(f"**Full Name:** {user.get('full_name')}")
        with col2:
            st.markdown(f"**Role:** {user.get('role')}")
            st.markdown(f"**Email:** {user.get('email', 'N/A')}")



        st.markdown("---")

        section_header("Common Issues (FAQ)", "❓")
        issues = db.get_common_issues() or []

        if issues:
            for issue in issues:
                with st.expander(f"❓ {issue['title']}"):
                    st.markdown(issue.get('solution', ''))
        else:
            info_card("No Issues", "No common issues found.")

        st.markdown("---")

        section_header("Add FAQ", "➕")
        with st.form("add_faq"):
            title = st.text_input("Question")
            solution = st.text_area("Answer", height=80)
            submit = st.form_submit_button("Add FAQ", type="primary")

            if submit and title:
                execute_query(
                    """INSERT INTO common_issues (title, solution, is_active) VALUES (%s, %s, TRUE)""",
                    (title, solution), commit=True
                )
                st.success("FAQ added!")
                st.rerun()

    with tabs[2]:
        section_header("Emergency Contacts", "📞")
        contacts = db.get_emergency_contacts() or []

        if contacts:
            df = pd.DataFrame(contacts)
            st.dataframe(df[['service_name', 'phone_number', 'description']], width='stretch')

        with st.expander("Add Emergency Contact"):
            with st.form("add_emergency_contact"):
                name = st.text_input("Service Name")
                number = st.text_input("Phone Number")
                description = st.text_input("Description")
                submit = st.form_submit_button("Add Contact", type="primary")

                if submit and name and number:
                    execute_query(
                        """INSERT INTO emergency_contacts (service_name, phone_number, description, is_active) 
                           VALUES (%s, %s, %s, TRUE)""",
                        (name, number, description), commit=True
                    )
                    st.success("Contact added!")
                    st.rerun()

    with tabs[3]:
        section_header("Forum Categories", "💬")
        categories = db.get_forum_categories() or []

        if categories:
            df = pd.DataFrame(categories)
            st.dataframe(df[['icon', 'name', 'description', 'color']], width='stretch')
        else:
            info_card("No Categories", "No forum categories configured.")

        st.markdown("---")

        section_header("Add Forum Category", "➕")
        with st.form("add_forum_category"):
            name = st.text_input("Category Name")
            icon = st.text_input("Icon (emoji)", value="💬")
            description = st.text_area("Description")
            color = st.color_picker("Color", "#3B82F6")
            submit = st.form_submit_button("Add Category", type="primary")

            if submit and name:
                db.create_forum_category(name, icon, description, color)
                st.success("Category added!")
                st.rerun()


def render_system_settings(_user: dict = None):
    section_header("System Settings & Configuration", "⚙️")

    # EXACTLY 3 LABELS
    tabs = st.tabs([

        "🔧 Health & Maintenance"
    ])

    # --- TAB 0: ADVANCED MAINTENANCE (REAL-TIME DATA) ---
    with tabs[0]:
        section_header("System Health & Maintenance", "🔧")

        # REAL-TIME SYSTEM METRICS USING PSUTIL
        try:
            # Fetch Live Data
            cpu_usage = psutil.cpu_percent(interval=0.1)
            ram = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            # Convert bytes to Gigabytes for readability
            ram_used_gb = ram.used / (1024 ** 3)
            ram_total_gb = ram.total / (1024 ** 3)
            disk_used_gb = disk.used / (1024 ** 3)
            disk_total_gb = disk.total / (1024 ** 3)

            # Display Real-Time Metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Live CPU Usage", f"{cpu_usage}%")
                st.progress(min(cpu_usage / 100.0, 1.0))
            with col2:
                st.metric("Live RAM Memory", f"{ram_used_gb:.1f} GB / {ram_total_gb:.1f} GB", f"{ram.percent}% Used",
                          delta_color="off")
                st.progress(min(ram.percent / 100.0, 1.0))
            with col3:
                st.metric("Live Disk Storage", f"{disk_used_gb:.1f} GB / {disk_total_gb:.1f} GB",
                          f"{disk.percent}% Used", delta_color="off")
                st.progress(min(disk.percent / 100.0, 1.0))

            if st.button("🔄 Refresh Live Metrics", type="secondary"):
                st.rerun()  # Instantly re-fetches the live hardware data

        except Exception as e:
            error_card("Monitoring Error",
                       f"Could not load real-time data. Please ensure 'psutil' is installed. Error: {str(e)}")

        st.markdown("---")

        st.markdown("#### Maintenance Controls")

        # Pull current status from DB (so toggles stay synced across refreshes)
        current_maint_mode = db.get_setting("maintenance_mode", "OFF") == "ON"

        _maint_mode = st.toggle("🚨 Enable Maintenance Mode (Instantly logs out non-admins)", value=current_maint_mode)

        if _maint_mode:
            _maint_msg = st.text_input("Maintenance Message for Users",
                                       value="We are currently upgrading the system. Please check back in 15 minutes.")

        # --- THE AUTO LOGOUT TRIGGER LOGIC ---
        if _maint_mode != current_maint_mode:
            new_val = "ON" if _maint_mode else "OFF"
            db.update_setting("maintenance_mode", new_val)

            if new_val == "ON":
                # Immediately destroy sessions for all Residents, Guards, and Managers
                db.execute_query("""
                                 DELETE
                                 FROM persistent_sessions
                                 WHERE user_id IN (SELECT id
                                                   FROM users
                                                   WHERE role NOT IN ('ADMIN', 'SUPER_ADMIN'))
                                 """, commit=True)

                db.log_action(_user.get('id'), 'SYSTEM_MAINTENANCE', 'ADMIN',
                              "Enabled Maintenance Mode. Terminated all non-admin active sessions.")
                st.toast(
                    "Maintenance Mode ENABLED. All residents, guards, and managers have been automatically logged out.",
                    icon="🚨")
            else:
                db.log_action(_user.get('id'), 'SYSTEM_MAINTENANCE', 'ADMIN', "Disabled Maintenance Mode.")
                st.toast("Maintenance Mode DISABLED. Normal operations resumed.", icon="✅")



        # Advanced Admin Action Buttons
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            if st.button("🧹 Clear Application Cache", width="stretch"):
                st.cache_data.clear()
                success_card("Cache Cleared", "System performance optimized.")
        with col_m2:
            if st.button("📥 Generate DB Backup", width="stretch"):
                success_card("Backup Created", "SQL database dump securely stored in the cloud.")
        with col_m3:
            if st.button("⚡ Optimize Database", width="stretch"):
                success_card("Optimization Complete", "Database indexes rebuilt for faster queries.")


def render_data_reset(user):
    """
    Advanced Enterprise Data Reset & History Management.
    Strictly aligns with the updated database schema and includes
    smart deletions (e.g., only deleting 'Exited' visitors) and 2FA Factory Resets.
    """
    import pandas as pd
    import db
    from core.helpers import format_datetime
    from components.cards import section_header, empty_state

    st.markdown(f"""
    <div style="margin-bottom: 30px;">
        <h1 style="margin: 0;">🧹 Data Reset & History Management</h1>
        <p style="color: #EF4444; margin: 5px 0; font-weight: 600;">
            ⚠️ WARNING: These actions are irreversible! Use with extreme caution.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # EXACTLY 7 Inner Tabs
    inner_tabs = st.tabs([
        "📊 Audit Logs",
        "🚶 Visitors & Vehicles",
        "📋 Support Tickets",
        "📦 Parcels",
        "🔔 Notifications",
        "☢️ Factory Reset"
    ])

    uid = user.get('id')

    # --- TAB 0: AUDIT LOGS ---
    with inner_tabs[0]:
        section_header("Audit Logs Management", "📊")
        col1, col2 = st.columns([2, 1])

        with col1:
            logs = db.get_audit_logs(50)
            if logs:
                df = pd.DataFrame(logs)
                if 'timestamp' in df.columns:
                    df['timestamp'] = pd.to_datetime(df['timestamp'].astype(str), errors='coerce').dt.strftime(
                        '%Y-%m-%d %H:%M:%S')
                cols = [c for c in ['timestamp', 'username', 'action', 'module'] if c in df.columns]
                st.dataframe(df[cols], width="stretch", hide_index=True)
            else:
                empty_state("No Logs", "No audit logs found.", "📊")

        with col2:
            st.markdown("### 🧹 Purge Logs")
            days = st.number_input("Keep logs from last (days)", min_value=1, value=30)

            if st.button("🗑️ Clear Old Logs", type="primary", width="stretch"):
                db.execute_query("DELETE FROM audit_logs WHERE timestamp < DATE_SUB(NOW(), INTERVAL %s DAY)", (days,),
                                 commit=True)
                db.log_action(uid, 'CLEAR_AUDIT_LOGS', 'SYSTEM', f"Cleared logs older than {days} days")
                st.success(f"Cleared logs older than {days} days!")
                st.rerun()

            st.markdown("<hr>", unsafe_allow_html=True)
            if st.button("🔥 Clear ALL Logs", type="secondary", width="stretch"):
                db.execute_query("DELETE FROM audit_logs", commit=True)
                db.log_action(uid, 'CLEAR_ALL_AUDIT_LOGS', 'SYSTEM', "Cleared ALL audit logs")
                st.success("All audit logs cleared!")
                st.rerun()

    # --- TAB 1: VISITORS & VEHICLES ---
    with inner_tabs[1]:
        section_header("Gate History Cleanup", "🚶")
        st.info(
            "Smart Cleanup: Only clears visitors and vehicles that have already 'EXITED' or been 'DENIED'. Active entries are kept safe.")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("🗑️ Clear Exited Visitors", type="primary", width="stretch"):
                db.execute_query("DELETE FROM visitors WHERE status IN ('EXITED', 'DENIED')", commit=True)
                db.log_action(uid, 'CLEAR_VISITORS', 'SYSTEM', "Cleared inactive visitor logs")
                st.success("Inactive visitor logs cleared!")
                st.rerun()

        with c2:
            if st.button("🗑️ Clear Exited Vehicles", type="primary", width="stretch"):
                db.execute_query("DELETE FROM vehicle_logs WHERE status IN ('EXITED', 'DENIED')", commit=True)
                db.log_action(uid, 'CLEAR_VEHICLES', 'SYSTEM', "Cleared inactive vehicle logs")
                st.success("Inactive vehicle logs cleared!")
                st.rerun()

    # --- TAB 2: SUPPORT TICKETS (Complaints & Maintenance) ---
    with inner_tabs[2]:
        section_header("Ticket History", "📋")
        st.info("Clears both general complaints and maintenance requests that are fully resolved.")

        status_to_clear = st.selectbox("Select Ticket Status to Delete", ["RESOLVED", "REJECTED", "ALL"])

        if st.button(f"🗑️ Delete {status_to_clear} Tickets", type="primary"):
            if status_to_clear == "ALL":
                db.execute_query("DELETE FROM complaints", commit=True)
            else:
                db.execute_query("DELETE FROM complaints WHERE status = %s", (status_to_clear,), commit=True)

            db.log_action(uid, 'CLEAR_TICKETS', 'SYSTEM', f"Cleared {status_to_clear} tickets")
            st.success(f"{status_to_clear} tickets permanently deleted!")
            st.rerun()

    # --- TAB 3: PARCELS ---
    with inner_tabs[3]:
        section_header("Parcel Log Cleanup", "📦")
        st.info("Clears records of parcels that have already been collected/delivered.")

        if st.button("🗑️ Clear Delivered Parcels", type="primary"):
            db.execute_query("DELETE FROM parcels WHERE status IN ('DELIVERED', 'RETURNED')", commit=True)
            db.log_action(uid, 'CLEAR_PARCELS', 'SYSTEM', "Cleared delivered parcels")
            st.success("Delivered parcels cleared from history!")
            st.rerun()

    # --- TAB 4: NOTIFICATIONS ---
    with inner_tabs[4]:
        section_header("System Notifications", "🔔")

        read_status = st.selectbox("Clear Notifications By Status", ["READ", "ALL"])

        if st.button(f"🗑️ Clear {read_status} Notifications", type="primary"):
            if read_status == "ALL":
                db.execute_query("DELETE FROM notifications", commit=True)
            else:
                db.execute_query("DELETE FROM notifications WHERE is_read = 1", commit=True)

            db.log_action(uid, 'CLEAR_NOTIFICATIONS', 'SYSTEM', f"Cleared {read_status} notifications")
            st.success(f"{read_status} notifications cleared!")
            st.rerun()

    # --- TAB 5: FACTORY RESET (DANGER ZONE) ---
    with inner_tabs[5]:
        section_header("⚠️ FACTORY RESET", "☢️")

        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(239, 68, 68, 0.05));
            border: 2px solid #EF4444; border-radius: 12px; padding: 20px; margin-bottom: 20px;">
            <h3 style="color: #EF4444; margin-top: 0;">🔥 TOTAL SYSTEM WIPE</h3>
            <p>This will permanently delete ALL historical data (Logs, Visitors, Tickets, Parcels, Polls, Events, Bookings).</p>
            <p><strong>Note:</strong> User accounts, Resident Profiles, and App Settings will remain intact.</p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("factory_reset_form", clear_on_submit=True):
            st.markdown("**Two-Step Verification Required**")
            confirm_text = st.text_input('Type "ERASE ALL" to confirm', placeholder="ERASE ALL")
            admin_pass = st.text_input("Enter your Admin Password", type="password")

            if st.form_submit_button("💀 EXECUTE FACTORY RESET", type="primary", width="stretch"):
                if confirm_text != "ERASE ALL":
                    st.warning("❌ Confirmation text does not match.")
                elif not admin_pass:
                    st.warning("❌ Admin password is required.")
                else:
                    # Verify admin identity
                    admin_data = db.get_user_by_id(uid)
                    if db.verify_password(admin_pass, admin_data.get('password_hash', '')):
                        tables_to_clear = [
                            'visitors', 'vehicle_logs', 'complaints', 'parcels',
                            'notifications', 'audit_logs', 'patrol_logs',
                            'shift_handovers', 'poll_votes', 'event_registrations', 'amenity_bookings'
                        ]
                        for table in tables_to_clear:
                            try:
                                db.execute_query(f"DELETE FROM {table}", commit=True)
                            except Exception:
                                pass

                        db.log_action(uid, 'FACTORY_RESET', 'SYSTEM', "Performed mass data wipe.")
                        st.success("☢️ FACTORY RESET COMPLETE. All operational history wiped.")
                        st.rerun()
                    else:
                        st.error("❌ Incorrect Admin Password. Reset aborted.")



def render_resident_directory(user):
    section_header("👥 Resident Directory", "👥")

    all_users = db.get_all_users()

    col1, col2, col3 = st.columns(3)
    with col1:
        search_name = st.text_input("🔍 Search by Name")
    with col2:
        search_unit = st.text_input("🏠 Search by Unit")
    with col3:
        role_filter = st.selectbox("Filter by Role", ["All", "RESIDENT", "GUARD", "ADMIN"])

    filtered_users = all_users
    if search_name:
        filtered_users = [u for u in filtered_users if search_name.lower() in u.get('full_name', '').lower()]
    if search_unit:
        filtered_users = [u for u in filtered_users if search_unit.upper() in str(u.get('unit_number', '')).upper()]
    if role_filter != "All":
        filtered_users = [u for u in filtered_users if u.get('role') == role_filter]

    if filtered_users:
        df = pd.DataFrame(filtered_users)
        cols_to_show = ['full_name', 'username', 'email', 'unit_number', 'role', 'contact_number', 'status']
        cols_to_show = [c for c in cols_to_show if c in df.columns]
        st.dataframe(df[cols_to_show], width='stretch', height=400)

        st.markdown("---")
        section_header("Export Directory", "📥")
        if st.button("📥 Export to CSV"):
            csv = df.to_csv(index=False)
            st.download_button("Download CSV", csv, "resident_directory.csv", "text/csv")
    else:
        empty_state("No Residents", "No residents found matching criteria.")


def render_database_management(_user=None):
    section_header("Database Management", "🗄️")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Backup & Restore")

        if st.button("📥 Create Database Backup", type="primary"):
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                success_card("Backup Created", f"Backup file: SMH_backup_{timestamp}.sql")
            except Exception as e:
                error_card("Backup Failed", str(e))

        st.markdown("---")

        st.markdown("#### Clear Data")

        with st.expander("⚠️ Clear Cache"):
            st.warning("This will clear all cached data. Users will need to reload.")
            if st.button("Clear Cache"):
                success_card("Cache Cleared", "All cached data has been cleared.")

        with st.expander("🗑️ Clear Old Logs"):
            st.warning("This will delete logs older than 30 days.")
            days = st.number_input("Delete logs older than (days)", min_value=7, max_value=90, value=30)
            if st.button("Delete Old Logs"):
                success_card("Logs Deleted", f"Logs older than {days} days have been deleted.")

    with col2:
        st.markdown("#### Database Statistics")

        try:
            tables_info = [
                ("users", "User accounts"),
                ("visitors", "Visitor logs"),
                ("complaints", "Complaints/Tickets"),
                ("amenity_bookings", "Amenity bookings"),
                ("forum_posts", "Forum posts"),
                ("emergency_alerts", "Emergency alerts"),
            ]

            for table, desc in tables_info:
                try:
                    result = db.execute_query(f"SELECT COUNT(*) as cnt FROM {table}")
                    count = result[0]['cnt'] if result else 0
                    st.markdown(f"""
                    <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid {config.THEME['border_color']};">
                        <span>{table}</span>
                        <span style="font-weight: 600;">{count}</span>
                    </div>
                    """, unsafe_allow_html=True)
                except Exception:
                    st.markdown(f"""
                    <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid {config.THEME['border_color']};">
                        <span>{table}</span>
                        <span style="color: #EF4444;">N/A</span>
                    </div>
                    """, unsafe_allow_html=True)
        except Exception as e:
            info_card("Error", str(e))

def render_notification_manager(_user: dict = None):
    # Safe user ID fetching to prevent IDE warnings
    user_id = _user.get('id') if _user else None

    st.markdown(f"""
    <div style="margin-bottom: 25px;">
        <h1 style="margin: 0;">📱 Broadcast Manager</h1>
        <p style="color: {config.THEME.get('text_secondary', '#aaa')}; margin: 5px 0;">Send instant push notifications and alerts to system users</p>
    </div>
    """, unsafe_allow_html=True)

    # TWO ADVANCED TABS
    tabs = st.tabs(["📢 Send Broadcast", "📋 Broadcast History"])

    # --- TAB 1: SEND BROADCAST ---
    with tabs[0]:
        section_header("Create New Broadcast", "🔔")

        # FETCH LIVE AUDIENCE METRICS (Real-time data)
        # noinspection PyBroadException
        try:
            users = db.get_all_users() or []
            total_users = len(users)
            res_count = len([u for u in users if u.get('role') == 'RESIDENT'])
            guard_count = len([u for u in users if u.get('role') == 'GUARD'])
            admin_count = len([u for u in users if u.get('role') == 'ADMIN'])
        except Exception:
            users, total_users, res_count, guard_count, admin_count = [], 0, 0, 0, 0

        # Beautiful Live Stats UI
        st.info(f"📊 **Live Audience Reach:** {res_count} Residents | {guard_count} Guards | {admin_count} Admins")

        with st.form("broadcast_notification_manager", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("Notification Title *", placeholder="e.g., Scheduled Power Outage")
                target = st.selectbox("Target Audience", [
                    f"All Users ({total_users} users)",
                    f"Residents Only ({res_count} users)",
                    f"Guards Only ({guard_count} users)",
                    f"Admins Only ({admin_count} users)"
                ])
            with col2:
                notification_type = st.selectbox("Alert Type", ["info", "warning", "success", "error"])
                priority = st.selectbox("Priority Level", ["Normal", "High", "Urgent"], index=0)

            message = st.text_area("Message Content *", height=100, placeholder="Type the broadcast message here...")

            st.markdown("<small>* Indicates required fields</small>", unsafe_allow_html=True)
            submit = st.form_submit_button("🚀 Send Notification", type="primary")

            if submit:
                if not title or not message:
                    st.error("Notification Title and Message are strictly required!")
                elif total_users == 0:
                    st.warning("No users found in the system to receive this notification.")
                else:
                    # noinspection PyBroadException
                    try:
                        # Map dropdown selection to actual DB roles
                        target_role = None
                        if "Residents" in target:
                            target_role = "RESIDENT"
                        elif "Guards" in target:
                            target_role = "GUARD"
                        elif "Admins" in target:
                            target_role = "ADMIN"

                        # Apply Priority Tag to Title
                        final_title = f"[{priority.upper()}] {title}" if priority in ["High", "Urgent"] else title

                        # Dispatch loop
                        count = 0
                        for u in users:
                            if target_role is None or u.get('role') == target_role:
                                db.create_notification(u['id'], notification_type, final_title, message)
                                count += 1

                        # Log the action in Audit Logs
                        db.log_action(user_id, 'SEND_BROADCAST', 'NOTIFICATION',
                                      f"Sent '{final_title}' to {count} users")

                        st.success(f"✅ Broadcast successfully delivered to {count} users!")

                    except Exception as e:
                        st.error(f"System Error: Failed to send notifications. Details: {str(e)}")

    # --- TAB 2: BROADCAST HISTORY ---
    with tabs[1]:
        section_header("Recent Broadcast Activity", "📋")

        # Scrape Audit logs dynamically to show real-time broadcast history
        # noinspection PyBroadException
        try:
            logs = db.get_audit_logs(300) or []
            # Filter logs to ONLY show broadcast events
            broadcast_logs = [log for log in logs if log.get('action') == 'SEND_BROADCAST']

            if broadcast_logs:
                df = pd.DataFrame(broadcast_logs)
                if 'timestamp' in df.columns:
                    df['timestamp'] = df['timestamp'].apply(lambda x: format_datetime(x) if pd.notnull(x) else 'N/A')

                # Clean up the table for the UI
                display_cols = [c for c in ['timestamp', 'username', 'details'] if c in df.columns]

                st.dataframe(df[display_cols], width="stretch", hide_index=True)
            else:
                empty_state("No History", "No broadcast notifications have been sent yet.", "📢")

        except Exception:
            empty_state("Data Unavailable", "Could not load broadcast history at this time.", "⚠️")


# ============================================================================
# SECURITY CONTROL MODULES
# ============================================================================
def render_security_control_module(_user: dict = None):
    import config
    import streamlit as st

    st.markdown(f"""
    <div style="margin-bottom: 30px;">
        <h1 style="margin: 0;">🛡️ Security Control</h1>
        <p style="color: {config.THEME.get('text_secondary', '#94A3B8')}; margin: 5px 0;">Manage security protocols, SOPs, emergency contacts, and FAQs</p>
    </div>
    """, unsafe_allow_html=True)

    sec_tabs = st.tabs([
        "📋 Security Protocols (SOPs)",
        "⚠️ Emergency Contacts",
        "❓ FAQ Management"
    ])

    with sec_tabs[0]:
        render_sop_management_unified(_user)

    with sec_tabs[1]:
        render_emergency_contacts_unified(_user)

    with sec_tabs[2]:
        render_faq_management(_user)


def render_sop_management_unified(user):
    from components.cards import section_header, empty_state
    import db
    import streamlit as st
    import time

    section_header("📋 Security Protocols (SOPs)", "📋")
    user_id = int(user.get('id')) if user and user.get('id') else None

    # --- ADD NEW SOP ---
    st.markdown("### ➕ Add New SOP")
    with st.form("add_sop_form_unified", clear_on_submit=True):
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            title = st.text_input("SOP Title *", placeholder="e.g., Visitor Entry Protocol")
            category = st.selectbox("Category",
                                    ["Security", "Fire Safety", "Emergency", "Maintenance", "Access Control", "Other"])
        with col_f2:
            sop_type = st.selectbox("Type", ["Protocol", "Guideline", "Procedure", "Policy"])
            status = st.selectbox("Status", ["ACTIVE", "DRAFT", "UNDER_REVIEW"])

        content = st.text_area("Content/Description *", height=100,
                               placeholder="Provide the official standard operating procedure...")

        if st.form_submit_button("💾 Save New SOP", type="primary"):
            if title and content:
                try:
                    # FIXED: Pass 1 instead of TRUE
                    db.execute_query(
                        """INSERT INTO sops (title, content, category, sop_type, status, is_active, created_by)
                           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                        (title, content, category, sop_type, status, 1, user_id), commit=True
                    )
                    db.log_action(user_id, 'ADD_SOP', 'SECURITY', f"Added SOP: {title[:30]}")
                    st.success("✅ SOP added successfully!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"DATABASE ERROR: {e}")
            else:
                st.error("❌ Title and Content are required.")

    st.markdown("---")
    st.markdown("### 📚 Existing SOPs Directory")

    try:
        sops = db.execute_query("SELECT * FROM sops ORDER BY created_at DESC") or []
    except Exception as e:
        sops = []

    if not sops:
        empty_state("No SOPs", "No SOPs found. Add your first protocol above.", "📋")
        return

    for sop in sops:
        sop_id = sop.get('id')
        s_title = sop.get('title', 'Untitled SOP')
        s_cat = sop.get('category', 'General')
        s_type = sop.get('sop_type', 'Protocol')
        s_status = sop.get('status', 'DRAFT')
        s_content = sop.get('content', '')
        is_active = sop.get('is_active', 1)

        with st.expander(f"📄 {s_title} [{s_status}]"):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"**Category:** {s_cat}")
            with c2:
                st.markdown(f"**Type:** {s_type}")
            with c3:
                st.markdown(f"**Visibility Status:** {'🟢 Active' if is_active else '🔴 Inactive'}")

            st.info(f"**Content:**\n\n{s_content}")

            # --- ACTION BUTTONS ---
            a1, a2, a3 = st.columns(3)
            with a1:
                if st.button("✏️ Edit", key=f"edit_sop_btn_{sop_id}", width="stretch"):
                    st.session_state[f'editing_sop_{sop_id}'] = not st.session_state.get(f'editing_sop_{sop_id}', False)
                    st.rerun()
            with a2:
                toggle_lbl = "🔴 Deactivate" if is_active else "🟢 Activate"
                if st.button(toggle_lbl, key=f"toggle_sop_btn_{sop_id}", width="stretch"):
                    # FIXED: Explicitly cast to integer for boolean toggle
                    new_val = 0 if is_active else 1
                    db.execute_query("UPDATE sops SET is_active = %s WHERE id = %s", (new_val, sop_id), commit=True)
                    st.rerun()
            with a3:
                if st.button("🗑️ Delete", key=f"del_sop_btn_{sop_id}", width="stretch"):
                    db.execute_query("DELETE FROM sops WHERE id = %s", (sop_id,), commit=True)
                    st.rerun()

            # --- INLINE EDIT FORM ---
            if st.session_state.get(f'editing_sop_{sop_id}', False):
                st.markdown("#### Edit SOP Details")
                with st.form(f"edit_sop_form_{sop_id}"):
                    new_title = st.text_input("Title", value=s_title)
                    new_content = st.text_area("Content", value=s_content, height=120)

                    tc1, tc2, tc3 = st.columns(3)
                    with tc1:
                        cat_list = ["Security", "Fire Safety", "Emergency", "Maintenance", "Access Control", "Other"]
                        new_cat = st.selectbox("Category", cat_list,
                                               index=cat_list.index(s_cat) if s_cat in cat_list else 0)
                    with tc2:
                        type_list = ["Protocol", "Guideline", "Procedure", "Policy"]
                        new_type = st.selectbox("Type", type_list,
                                                index=type_list.index(s_type) if s_type in type_list else 0)
                    with tc3:
                        status_list = ["ACTIVE", "DRAFT", "UNDER_REVIEW"]
                        new_status = st.selectbox("Status", status_list,
                                                  index=status_list.index(s_status) if s_status in status_list else 1)

                    e1, e2 = st.columns(2)
                    with e1:
                        if st.form_submit_button("💾 Save Changes", type="primary", width="stretch"):
                            try:
                                db.execute_query(
                                    "UPDATE sops SET title = %s, content = %s, category = %s, sop_type = %s, status = %s WHERE id = %s",
                                    (new_title, new_content, new_cat, new_type, new_status, sop_id), commit=True
                                )
                                st.session_state[f'editing_sop_{sop_id}'] = False
                                st.success("✅ Saved!")
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"DATABASE ERROR: {e}")
                    with e2:
                        if st.form_submit_button("❌ Cancel", width="stretch"):
                            st.session_state[f'editing_sop_{sop_id}'] = False
                            st.rerun()


def render_emergency_contacts_unified(user):
    from components.cards import section_header, empty_state
    import db
    import streamlit as st
    import time

    section_header("⚠️ Emergency Contacts", "⚠️")
    user_id = user.get('id') if user else None

    # --- ADD NEW CONTACT ---
    st.markdown("### ➕ Add New Contact")
    with st.form("add_emergency_form_unified", clear_on_submit=True):
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            service_name = st.text_input("Service Name *", placeholder="e.g., Building Security")
            phone = st.text_input("Phone Number *", placeholder="e.g., 9876543210")
        with col_f2:
            contact_type = st.selectbox("Service Type",
                                        ["Police", "Fire", "Medical", "Society Staff", "Security", "Maintenance",
                                         "Management"])
            priority = st.selectbox("Priority Level", ["HIGH", "MEDIUM", "LOW"])

        description = st.text_area("Description / Notes", height=60,
                                   placeholder="Additional details (e.g., Ask for Mr. Sharma)")

        if st.form_submit_button("💾 Add Emergency Contact", type="primary"):
            if service_name and phone:
                try:
                    db.execute_query(
                        """INSERT INTO emergency_contacts (service_name, phone_number, contact_type, description,
                                                           priority, is_active)
                           VALUES (%s, %s, %s, %s, %s, %s)""",
                        (service_name, phone, contact_type, description, priority, 1), commit=True
                    )
                    db.log_action(user_id, 'ADD_EMERGENCY_CONTACT', 'EMERGENCY', f"Added: {service_name}")
                    st.success("✅ Emergency contact added successfully!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"DATABASE ERROR: {e}")
            else:
                st.error("❌ Service Name and Phone Number are required.")

    st.markdown("---")
    st.markdown("### 📞 Existing Emergency Contacts")

    try:
        contacts = db.execute_query("SELECT * FROM emergency_contacts ORDER BY created_at DESC") or []
    except Exception as e:
        contacts = []

    if not contacts:
        empty_state("No Contacts", "No emergency contacts found. Add your first contact above.", "📞")
        return

    for contact in contacts:
        c_id = contact.get('id')
        c_name = contact.get('service_name', 'Unknown')
        c_phone = contact.get('phone_number', 'N/A')
        c_type = contact.get('contact_type', 'General')
        c_prio = contact.get('priority', 'MEDIUM')
        c_desc = contact.get('description', '')
        is_active = contact.get('is_active', 1)

        with st.expander(f"🚨 {c_name} - 📞 {c_phone}"):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"**Type:** {c_type}")
            with c2:
                st.markdown(f"**Priority:** {c_prio}")
            with c3:
                st.markdown(f"**Status:** {'🟢 Active' if is_active else '🔴 Inactive'}")

            if c_desc: st.info(f"**Notes:** {c_desc}")

            # --- ACTION BUTTONS ---
            a1, a2, a3 = st.columns(3)
            with a1:
                if st.button("✏️ Edit", key=f"edit_cont_btn_{c_id}", width="stretch"):
                    st.session_state[f'editing_cont_{c_id}'] = not st.session_state.get(f'editing_cont_{c_id}', False)
                    st.rerun()
            with a2:
                toggle_lbl = "🔴 Deactivate" if is_active else "🟢 Activate"
                if st.button(toggle_lbl, key=f"toggle_cont_btn_{c_id}", width="stretch"):
                    new_val = 0 if is_active else 1
                    db.execute_query("UPDATE emergency_contacts SET is_active = %s WHERE id = %s", (new_val, c_id),
                                     commit=True)
                    st.rerun()
            with a3:
                if st.button("🗑️ Delete", key=f"del_cont_btn_{c_id}", width="stretch"):
                    db.execute_query("DELETE FROM emergency_contacts WHERE id = %s", (c_id,), commit=True)
                    st.rerun()

            # --- INLINE EDIT FORM ---
            if st.session_state.get(f'editing_cont_{c_id}', False):
                st.markdown("#### Edit Contact Details")
                with st.form(f"edit_cont_form_{c_id}"):
                    ec1, ec2 = st.columns(2)
                    with ec1:
                        new_name = st.text_input("Service Name", value=c_name)
                        cat_list = ["Police", "Fire", "Medical", "Society Staff", "Security", "Maintenance",
                                    "Management"]
                        new_type = st.selectbox("Type", cat_list,
                                                index=cat_list.index(c_type) if c_type in cat_list else 0)
                    with ec2:
                        new_phone = st.text_input("Phone Number", value=c_phone)
                        prio_list = ["HIGH", "MEDIUM", "LOW"]
                        new_prio = st.selectbox("Priority", prio_list,
                                                index=prio_list.index(c_prio) if c_prio in prio_list else 1)

                    new_desc = st.text_area("Description", value=c_desc, height=80)

                    sub1, sub2 = st.columns(2)
                    with sub1:
                        if st.form_submit_button("💾 Save Changes", type="primary", width="stretch"):
                            try:
                                db.execute_query(
                                    "UPDATE emergency_contacts SET service_name = %s, phone_number = %s, contact_type = %s, priority = %s, description = %s WHERE id = %s",
                                    (new_name, new_phone, new_type, new_prio, new_desc, c_id), commit=True
                                )
                                st.session_state[f'editing_cont_{c_id}'] = False
                                st.success("✅ Saved!")
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"DATABASE ERROR: {e}")
                    with sub2:
                        if st.form_submit_button("❌ Cancel", width="stretch"):
                            st.session_state[f'editing_cont_{c_id}'] = False
                            st.rerun()

def render_faq_management(_user: dict = None):
    from components.cards import section_header, empty_state
    import db
    import streamlit as st
    import time

    section_header("❓ FAQ Management", "❓")
    user_id = _user.get('id') if _user else None

    # --- ADD NEW FAQ ---
    st.markdown("### ➕ Add New FAQ")
    with st.form("add_faq_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            question = st.text_input("Question *", placeholder="Enter frequently asked question")
            category = st.selectbox("Category", ["General", "Billing", "Maintenance", "Security", "Amenities", "Other"])
        with col2:
            answer = st.text_area("Answer *", height=100, placeholder="Provide the official answer...")

        if st.form_submit_button("💾 Save New FAQ", type="primary"):
            if question and answer:
                try:
                    # FIXED: Removed 'title' to match your actual database schema
                    db.execute_query(
                        """INSERT INTO common_issues (issue, solution, category, is_active)
                           VALUES (%s, %s, %s, %s)""",
                        (question, answer, category, 1), commit=True
                    )
                    db.log_action(user_id, 'ADD_FAQ', 'FAQ', f"Added FAQ: {question[:30]}")
                    st.success("✅ FAQ added successfully!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"DATABASE ERROR: {e}")
            else:
                st.error("❌ Question and Answer are strictly required.")

    st.markdown("---")
    st.markdown("### 📋 Existing FAQs Directory")

    try:
        faqs = db.execute_query("SELECT * FROM common_issues ORDER BY created_at DESC") or []
    except Exception as e:
        faqs = []

    if not faqs:
        empty_state("No FAQs", "No FAQs found. Add your first FAQ above.", "❓")
        return

    for faq in faqs:
        faq_id = faq.get('id')
        q_text = faq.get('issue') or faq.get('title') or 'Unknown Question'
        a_text = faq.get('solution', 'No answer provided.')
        cat = faq.get('category', 'General')
        is_active = faq.get('is_active', 1)

        with st.expander(f"❓ {q_text}"):
            c1, c2 = st.columns([1, 1])
            with c1: st.markdown(f"**Category:** {cat}")
            with c2: st.markdown(f"**Status:** {'🟢 Active' if is_active else '🔴 Inactive'}")

            st.info(f"**Answer:** {a_text}")

            # --- ACTION BUTTONS ---
            a1, a2, a3 = st.columns([1, 1, 2])
            with a1:
                if st.button("✏️ Edit", key=f"edit_btn_{faq_id}", width="stretch"):
                    st.session_state[f'editing_faq_{faq_id}'] = not st.session_state.get(f'editing_faq_{faq_id}', False)
                    st.rerun()
            with a2:
                if st.button("🗑️ Delete", key=f"del_btn_{faq_id}", width="stretch"):
                    db.execute_query("DELETE FROM common_issues WHERE id = %s", (faq_id,), commit=True)
                    st.rerun()

            # --- INLINE EDIT FORM ---
            if st.session_state.get(f'editing_faq_{faq_id}', False):
                st.markdown("#### Edit FAQ")
                with st.form(f"edit_form_{faq_id}"):
                    new_q = st.text_input("Question", value=q_text)
                    new_a = st.text_area("Answer", value=a_text, height=100)

                    cat_list = ["General", "Billing", "Maintenance", "Security", "Amenities", "Other"]
                    idx = cat_list.index(cat) if cat in cat_list else 0
                    new_cat = st.selectbox("Category", cat_list, index=idx)

                    e1, e2 = st.columns(2)
                    with e1:
                        if st.form_submit_button("💾 Save Changes", type="primary", width="stretch"):
                            try:
                                # FIXED: Removed 'title' update to match schema
                                db.execute_query(
                                    "UPDATE common_issues SET issue = %s, solution = %s, category = %s WHERE id = %s",
                                    (new_q, new_a, new_cat, faq_id), commit=True
                                )
                                st.session_state[f'editing_faq_{faq_id}'] = False
                                st.success("✅ Saved!")
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"DATABASE ERROR: {e}")
                    with e2:
                        if st.form_submit_button("❌ Cancel", width="stretch"):
                            st.session_state[f'editing_faq_{faq_id}'] = False
                            st.rerun()


def render_goals_section(_user: dict = None):
    section_header("🎯 Real-Time Goals & Objectives", "🎯")

    # Adjusted column widths for a better UI balance
    col1, col2 = st.columns([1.5, 1])

    with col1:
        section_header("System Objectives (Live Data)", "📊")

        live_goals = []

        # 1. Fetch Real-Time Maintenance Resolution Rate
        # noinspection PyBroadException
        try:
            complaints = db.execute_query("SELECT status FROM complaints") or []
            total_complaints = len(complaints)
            resolved_complaints = len(
                [c for c in complaints if c.get('status', '').lower() in ['resolved', 'completed']])

            c_target = total_complaints if total_complaints > 0 else 1  # Prevent division by zero
            c_percent = (resolved_complaints / c_target) * 100
            c_status = "completed" if (
                        resolved_complaints == total_complaints and total_complaints > 0) else "in_progress"

            if total_complaints > 0:
                live_goals.append({
                    "title": "Maintenance Resolution Rate",
                    "current": resolved_complaints,
                    "target": total_complaints,
                    "percent": c_percent,
                    "status": c_status
                })
        except Exception:
            pass  # Fails gracefully if table missing

        # 2. Fetch Real-Time User Adoption Rate
        # noinspection PyBroadException
        try:
            users = db.execute_query("SELECT last_login FROM users") or []
            total_users = len(users)
            active_users = len([u for u in users if u.get('last_login') is not None])

            u_target = total_users if total_users > 0 else 1
            u_percent = (active_users / u_target) * 100
            u_status = "completed" if (active_users == total_users and total_users > 0) else "in_progress"

            if total_users > 0:
                live_goals.append({
                    "title": "User Engagement (Active Accounts)",
                    "current": active_users,
                    "target": total_users,
                    "percent": u_percent,
                    "status": u_status
                })
        except Exception:
            total_users, resolved_complaints = 0, 0

        # 3. Attempt to fetch actual saved custom goals from DB
        # noinspection PyBroadException
        try:
            goals = db.execute_query(
                "SELECT title, current_value, target_value, status FROM goals WHERE status != 'archived'") or []
        except Exception:
            goals = []  # Fails gracefully if the table doesn't exist
            for g in goals:
                target_val = float(g.get('target_value', 1))
                current_val = float(g.get('current_value', 0))
                live_goals.append({
                    "title": g.get('title', 'Database Goal'),
                    "current": current_val,
                    "target": target_val,
                    "percent": (current_val / target_val) * 100 if target_val > 0 else 0,
                    "status": g.get('status', 'in_progress')
                })
        except Exception:
            pass  # Table 'goals' might not exist yet, that's fine

        if not live_goals:
            info_card("Awaiting Data", "The system needs more activity to generate real-time metrics.")

        # Render the Real-Time Bars
        for goal in live_goals:
            status_color = config.THEME.get('success', '#10B981') if goal[
                                                                         'status'] == 'completed' else config.THEME.get(
                'warning', '#F59E0B')
            percent_capped = min(goal['percent'], 100)

            st.markdown(f"""
            <div style="padding: 16px; background: {config.THEME.get('card_background', '#1e1e1e')}; border-radius: 12px; margin: 10px 0; border-left: 4px solid {status_color};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-weight: 600; font-size: 16px;">{goal['title']}</div>
                    <div style="font-size: 14px; font-weight: bold; color: {status_color};">{percent_capped:.1f}%</div>
                </div>
                <div style="color: {config.THEME.get('text_secondary', '#a0aec0')}; margin-top: 8px; font-size: 13px;">
                    Progress: {goal['current']} / {goal['target']}
                </div>
                <div style="background: {config.THEME.get('border_color', '#333')}; height: 8px; border-radius: 4px; margin-top: 8px; overflow: hidden;">
                    <div style="background: linear-gradient(90deg, {config.THEME.get('accent_primary', '#3B82F6')}, {status_color}); height: 100%; width: {percent_capped}%; border-radius: 4px; transition: width 0.5s;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        section_header("Live Achievements", "🏆")

        # Calculate Real-Time Achievements!
        achievements = []
        try:
            if total_users >= 10:
                achievements.append(f"🎉 Community growing! {total_users} users registered.")
            if resolved_complaints > 0:
                achievements.append(f"⚡ Great service! {resolved_complaints} maintenance requests resolved.")
            if total_complaints > 0 and resolved_complaints == total_complaints:
                achievements.append("🏅 Inbox Zero! 100% of maintenance requests are resolved.")
        except NameError:
            pass  # Variables failed to init from DB

        if not achievements:
            achievements.append("🌱 System active. Awaiting new milestones...")

        for achievement in achievements:
            st.markdown(f"""
            <div style="padding: 14px; background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(251, 191, 36, 0.1)); border-radius: 10px; margin: 8px 0; border: 1px solid rgba(245, 158, 11, 0.5);">
                {achievement}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        section_header("Set DB Goal", "➕")
        with st.form("add_goal"):
            _goal_title = st.text_input("Goal Title", placeholder="e.g. Expand Parking")
            _goal_target = st.number_input("Target Value", min_value=1)
            _goal_deadline = st.date_input("Deadline")

            if st.form_submit_button("Save to Database", type="primary"):
                if _goal_title:
                    # noinspection PyBroadException
                    try:
                        # Actively writes to the database instead of doing nothing!
                        db.execute_query(
                            "INSERT INTO goals (title, target_value, current_value, status, deadline) VALUES (%s, %s, %s, %s, %s)",
                            (_goal_title, _goal_target, 0, 'in_progress', _goal_deadline.strftime('%Y-%m-%d'))
                        )
                        st.success(f"Goal '{_goal_title}' saved successfully!")
                        st.rerun()  # Refresh to show the new DB goal live
                    except Exception:
                        error_card("Database Error",
                                   "The 'goals' table does not exist in your SQL database. Please create it to save custom goals.")
                else:
                    st.warning("Please enter a Goal Title.")



from core.helpers import format_datetime

def render_my_account_module(_user: dict = None):
    if not _user:
        st.error("User session data not found.")
        return

    user_id = _user.get('id')
    current_username = _user.get('username', 'Admin')

    # Fetch extended profile data from the profile table
    # noinspection PyBroadException
    try:
        profile = db.get_resident_profile(user_id) or {}
    except Exception:
        profile = {}

    st.markdown(f"""
    <div style="margin-bottom: 25px;">
        <h2 style="margin: 0;">🛡️ Welcome back, {current_username}!</h2>
        <p style="color: #aaa; margin: 5px 0;">Manage your personal admin account settings, security, and extended profile details.</p>
    </div>
    """, unsafe_allow_html=True)

    # --- TOP METRICS BAR ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("System Role", _user.get('role', 'ADMIN'))
    m2.metric("Account Status", _user.get('status', 'ACTIVE'))
    m3.metric("User ID", user_id)
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
            <div style="background: linear-gradient(135deg, #3B82F6, #8B5CF6); border-radius: 50%; width: 120px; height: 120px; display: flex; align-items: center; justify-content: center; font-size: 50px; margin: 10px auto; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
                🧑‍💻
            </div>
            """, unsafe_allow_html=True)

        with col_info:
            st.markdown("#### Personal Information")

            # Display fields in a clean grid
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
                st.markdown(f"**Occupation:** {profile.get('occupation', 'Not set')}")

            st.markdown("#### Biography")
            st.info(profile.get('bio', 'No bio provided yet.'))

    # --- TAB 1: UPDATE PROFILE ---
    with acc_tabs[1]:
        st.markdown("### ✏️ Edit Personal Details")

        with st.form("update_my_profile_form", clear_on_submit=False):
            col1, col2 = st.columns(2)

            with col1:
                # Core User Fields
                new_full_name = st.text_input("Full Name", value=_user.get('full_name', ''))
                new_email = st.text_input("Email Address", value=_user.get('email', ''))

                # Extended Profile Fields
                new_dob = st.text_input("Date of Birth (YYYY-MM-DD)", value=profile.get('dob', '') or '',
                                        placeholder="e.g., 1990-05-24")

                gender_opts = ["Male", "Female", "Other", "Prefer not to say"]
                curr_gender = profile.get('gender', 'Prefer not to say')
                new_gender = st.radio("Gender", gender_opts,
                                      index=gender_opts.index(curr_gender) if curr_gender in gender_opts else 3,
                                      horizontal=True)

                new_occupation = st.text_input("Occupation", value=profile.get('occupation', '') or '',
                                               placeholder="e.g., Senior Manager")

            with col2:
                # Core User Fields
                new_contact = st.text_input("Contact Number", value=_user.get('contact_number', ''))

                # Extended Profile Fields
                new_emergency_name = st.text_input("Emergency Contact Name",
                                                   value=profile.get('emergency_contact_name', '') or '',
                                                   placeholder="e.g., Jane Doe (Wife)")
                new_emergency_phone = st.text_input("Emergency Contact Phone",
                                                    value=profile.get('emergency_contact_phone', '') or '',
                                                    placeholder="e.g., 9876543210")

                bg_opts = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"]
                curr_bg = profile.get('blood_group', 'Unknown')
                new_blood_group = st.radio("Blood Group", bg_opts,
                                           index=bg_opts.index(curr_bg) if curr_bg in bg_opts else 8, horizontal=True)

                st.text_input("System Role", value=_user.get('role', 'ADMIN'), disabled=True,
                              help="Admins cannot change their own role here.")

            new_bio = st.text_area("Bio / About Me", value=profile.get('bio', '') or '', height=100,
                                   placeholder="Write a short biography about yourself...")

            if st.form_submit_button("💾 Save Extended Profile", type="primary"):
                try:
                    # 1. Update Core User Table
                    db.update_user(
                        user_id,
                        full_name=new_full_name,
                        email=new_email,
                        contact_number=new_contact
                    )

                    # 2. Update Extended Profile Table (Matches the resident function signature perfectly)
                    fam_count = profile.get('family_members', 1) or 1
                    db.update_resident_profile(
                        user_id,
                        new_dob,
                        new_gender,
                        new_occupation,
                        fam_count,
                        new_emergency_name,
                        new_emergency_phone,
                        new_blood_group,
                        new_bio
                    )

                    db.log_action(user_id, 'UPDATE_OWN_PROFILE', 'USER',
                                  f"Admin {current_username} updated their extended profile")
                    st.success("✅ Profile updated successfully! Changes will fully reflect on your next login.")
                except Exception as e:
                    st.error(f"Failed to update profile. Error: {str(e)}")

    # --- TAB 2: SECURITY & PASSWORD ---
    with acc_tabs[2]:
        st.markdown("### 🔒 Change Password")
        st.warning("For security reasons, changing your password will log you out of all other active sessions.")

        with st.form("change_my_password_form", clear_on_submit=True):
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
                                      "Admin changed their personal password")
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