#!/usr/bin/env python3
"""
 Admin Tools
Version: 8.6.0-Titanium-Live-SOC

Run from terminal: python admin_tools.py
"""

import os
import sys
import bcrypt
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import db
import config


class colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def clear_screen():
    try:
        if os.system('cls' if os.name == 'nt' else 'clear') != 0:
            print("\n" * 50)
    except:
        print("\n" * 50)


def print_header():
    clear_screen()
    print(f"{colors.HEADER}{colors.BOLD}")
    print("=" * 60)
    print("     Society Management HUB - ENTERPRISE CLI")
    print("     Version: " + getattr(config, 'APP_VERSION', '8.6.0'))
    print("=" * 60)
    print(f"{colors.ENDC}")


def get_input(prompt):
    print(f"{colors.CYAN}>> {prompt}: {colors.ENDC}", end="", flush=True)
    try:
        return input().strip()
    except Exception:
        return ""


def get_password(prompt="Password"):
    print(f"{colors.CYAN}>> {prompt}: {colors.ENDC}", end="", flush=True)
    try:
        return input().strip()
    except Exception:
        return ""


def press_enter():
    print(f"\n{colors.YELLOW}Press Enter to continue...{colors.ENDC}", end="", flush=True)
    try:
        input()
    except Exception:
        pass


# ==========================================
# SYSTEM & MAINTENANCE
# ==========================================

def system_info():
    print_header()
    print(f"\n{colors.CYAN}--- System Information ---{colors.ENDC}\n")
    print(f"  Application: {getattr(config, 'APP_NAME', 'Society Management HUB')}")
    print(f"  Version: {getattr(config, 'APP_VERSION', '8.6.0')}")
    print(f"  Database Host: {config.MYSQL_CONFIG['host']}")
    print(f"  Database Name: {config.MYSQL_CONFIG['database']}")

    try:
        result = db.execute_query("SELECT COUNT(*) as cnt FROM users")
        user_count = result[0]['cnt'] if result else 0
        print(f"  Total Users: {user_count}")
    except:
        print(f"  Total Users: {colors.RED}Database Error{colors.ENDC}")

    press_enter()


def maintenance_mode():
    print_header()
    print(f"\n{colors.CYAN}--- Maintenance Mode ---{colors.ENDC}\n")

    # Ensure settings table exists for this feature
    db.execute_query("""
                     CREATE TABLE IF NOT EXISTS app_settings
                     (
                         `key`
                         VARCHAR
                     (
                         50
                     ) PRIMARY KEY,
                         value VARCHAR
                     (
                         255
                     )
                         )
                     """, commit=True)

    try:
        result = db.execute_query("SELECT value FROM app_settings WHERE `key` = 'maintenance_mode'")
        current_status = result[0]['value'] if result else 'OFF'
    except Exception:
        current_status = 'OFF'

    print(f"Current Status: {colors.GREEN if current_status == 'ON' else colors.RED}{current_status}{colors.ENDC}")
    print(f"\n{colors.YELLOW}1.{colors.ENDC} Turn ON Maintenance Mode")
    print(f"{colors.YELLOW}2.{colors.ENDC} Turn OFF Maintenance Mode")
    print(f"{colors.YELLOW}3.{colors.ENDC} Back to Main Menu")

    choice = get_input("\nSelect option")
    if choice == '1':
        db.execute_query(
            "INSERT INTO app_settings (`key`, value) VALUES ('maintenance_mode', 'ON') ON DUPLICATE KEY UPDATE value = 'ON'",
            commit=True)
        print(f"\n{colors.GREEN}Maintenance mode turned ON!{colors.ENDC}")
    elif choice == '2':
        db.execute_query(
            "INSERT INTO app_settings (`key`, value) VALUES ('maintenance_mode', 'OFF') ON DUPLICATE KEY UPDATE value = 'OFF'",
            commit=True)
        print(f"\n{colors.GREEN}Maintenance mode turned OFF!{colors.ENDC}")
    press_enter()


# ==========================================
# USER MANAGEMENT
# ==========================================

def user_management():
    while True:
        print_header()
        print(f"\n{colors.CYAN}--- User Management ---{colors.ENDC}\n")
        print(f"{colors.YELLOW}1.{colors.ENDC} List All Users")
        print(f"{colors.YELLOW}2.{colors.ENDC} Search User")
        print(f"{colors.YELLOW}3.{colors.ENDC} Create New User")
        print(f"{colors.YELLOW}4.{colors.ENDC} Update User Password")
        print(f"{colors.YELLOW}5.{colors.ENDC} Update User Details")
        print(f"{colors.YELLOW}6.{colors.ENDC} Activate/Suspend User")
        print(f"{colors.YELLOW}7.{colors.ENDC} Delete User")
        print(f"{colors.YELLOW}8.{colors.ENDC} Back to Main Menu")

        choice = get_input("\nSelect option")
        if choice == '1':
            list_users()
        elif choice == '2':
            search_user()
        elif choice == '3':
            create_user()
        elif choice == '4':
            update_password()
        elif choice == '5':
            update_user_details()
        elif choice == '6':
            toggle_user_status()
        elif choice == '7':
            delete_user()
        elif choice == '8':
            break
        else:
            print(f"\n{colors.RED}Invalid option!{colors.ENDC}")
            press_enter()


def list_users():
    print_header()
    print(f"\n{colors.CYAN}--- All Users ---{colors.ENDC}\n")

    # Corrected: Changed House_number to unit_number in the SQL query
    users = db.execute_query(
        "SELECT id, username, full_name, role, unit_number, email, status FROM users ORDER BY created_at DESC LIMIT 50")

    if users and isinstance(users, list):
        # Updated header to say 'Unit' instead of 'House' for consistency
        print(f"{colors.BOLD}{'Username':<15} {'Name':<20} {'Role':<15} {'Unit':<8} {'Status':<10}{colors.ENDC}")
        print("-" * 70)
        for u in users:
            stat_color = colors.GREEN if u.get('status') == 'ACTIVE' else colors.RED

            # Corrected: Use u.get('unit_number') to fetch the correct database value
            unit_val = str(u.get('unit_number', 'N/A'))

            print(
                f"{u['username']:<15} "
                f"{str(u['full_name'])[:18]:<20} "
                f"{u['role']:<15} "
                f"{unit_val:<8} "
                f"{stat_color}{u['status']}{colors.ENDC}"
            )
    else:
        print(f"\n{colors.YELLOW}No users found or Database Table is missing!{colors.ENDC}")

    press_enter()

def search_user():
    print_header()
    print(f"\n{colors.CYAN}--- Search User ---{colors.ENDC}\n")
    search = get_input("Enter username, name, or email")
    if not search: return
    users = db.execute_query(
        "SELECT * FROM users WHERE username LIKE %s OR full_name LIKE %s OR email LIKE %s",
        (f'%{search}%', f'%{search}%', f'%{search}%')
    )
    if users:
        for u in users:
            print(f"\n{colors.GREEN}--- User Found ---{colors.ENDC}")
            print(
                f"  ID: {u['id']}\n  Username: {u['username']}\n  Name: {u['full_name']}\n  Role: {u['role']}\n  Email: {u.get('email', 'N/A')}\n  House: {u.get('House_number', 'N/A')}\n  Status: {u['status']}")
    else:
        print(f"\n{colors.YELLOW}No user found!{colors.ENDC}")
    press_enter()


def create_user():
    print_header()
    print(f"\n{colors.CYAN}--- Create New User ---{colors.ENDC}\n")
    username = get_input("Username")
    if not username: return

    if db.execute_query("SELECT id FROM users WHERE username = %s", (username,)):
        print(f"\n{colors.RED}Username already exists!{colors.ENDC}")
        press_enter()
        return

    full_name = get_input("Full Name")
    email = get_input("Email (Optional)")
    contact = get_input("Contact Number (Optional)")
    role = get_input("Role (SUPER_ADMIN/ADMIN/MANAGER/RESIDENT/GUARD)").upper()

    if role not in getattr(config, 'SYSTEM_ROLES', ['ADMIN', 'MANAGER', 'RESIDENT', 'GUARD']):
        role = 'RESIDENT'

    # Fixed: Changed House to unit and prompt to Unit Number
    unit = get_input("Unit Number") if role == 'RESIDENT' else None
    password = get_password("Password")

    if len(password) < 6:
        print(f"\n{colors.RED}Password must be at least 6 characters!{colors.ENDC}")
        press_enter()
        return

    try:
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        # Fixed: Changed House_number to unit_number in the query string
        db.execute_query(
            """INSERT INTO users (username, password_hash, full_name, role, unit_number, contact_number, email, status)
               VALUES (%s, %s, %s, %s, %s, %s, %s, 'ACTIVE')""",
            (username, hashed_pw, full_name, role, unit, contact, email),
            commit=True
        )
        print(f"\n{colors.GREEN}✅ User '{username}' created successfully!{colors.ENDC}")
    except Exception as e:
        print(f"\n{colors.RED}❌ Database Error: {e}{colors.ENDC}")

    press_enter()
# ==========================================
# MANAGER CREATOR
# ==========================================
def create_manager():
    print_header()
    print(f"\n{colors.CYAN}--- 👔 Create New Manager ID ---{colors.ENDC}\n")
    username = get_input("Choose Manager Username")
    if not username: return

    if db.execute_query("SELECT id FROM users WHERE username = %s", (username,)):
        print(f"\n{colors.RED}❌ Username exists!{colors.ENDC}");
        press_enter();
        return

    full_name = get_input("Full Name")
    password = get_password("Choose Password")
    if len(password) < 6:
        print(f"\n{colors.RED}❌ Password too short!{colors.ENDC}");
        press_enter();
        return

    try:
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        db.execute_query(
            """INSERT INTO users (username, password_hash, full_name, role, status) 
               VALUES (%s, %s, %s, 'MANAGER', 'ACTIVE')""",
            (username, hashed_pw, full_name),
            commit=True
        )
        print(f"\n{colors.GREEN}✅ SUCCESS! Society Manager account created and activated.{colors.ENDC}")
    except Exception as e:
        print(f"\n{colors.RED}❌ Error: {e}{colors.ENDC}")
    press_enter()

def update_password():
    print_header()
    print(f"\n{colors.CYAN}--- Update User Password ---{colors.ENDC}\n")
    username = get_input("Username")
    user = db.execute_query("SELECT id FROM users WHERE username = %s", (username,))
    if not user:
        print(f"\n{colors.RED}User not found!{colors.ENDC}")
        press_enter()
        return

    new_pwd = get_password("New Password")
    if len(new_pwd) < 6:
        print(f"\n{colors.RED}Password must be at least 6 characters!{colors.ENDC}")
        press_enter()
        return

    try:
        hashed = bcrypt.hashpw(new_pwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        db.execute_query("UPDATE users SET password_hash = %s WHERE id = %s", (hashed, user[0]['id']), commit=True)
        print(f"\n{colors.GREEN}✅ Password updated successfully!{colors.ENDC}")
    except Exception as e:
        print(f"\n{colors.RED}❌ Database Error: {e}{colors.ENDC}")

    press_enter()
def update_user_details():
    print_header()
    print(f"\n{colors.CYAN}--- Update User Details ---{colors.ENDC}\n")
    username = get_input("Username")

    users = db.execute_query("SELECT * FROM users WHERE username = %s", (username,))
    if not users:
        print(f"\n{colors.RED}User not found!{colors.ENDC}")
        press_enter()
        return

    user = users[0]

    print(f"{colors.YELLOW}Leave blank to keep current value{colors.ENDC}")
    full_name = get_input(f"New Name [{user['full_name']}]")
    role = get_input(f"New Role [{user['role']}]").upper()
    # Fixed: Changed House_number to unit_number
    unit = get_input(f"New Unit Number [{user.get('unit_number', '')}]")
    email = get_input(f"New Email [{user.get('email', '')}]")

    updates = []
    params = []
    if full_name: updates.append("full_name = %s"); params.append(full_name)
    if role and role in config.SYSTEM_ROLES: updates.append("role = %s"); params.append(role)
    # Fixed: Changed House_number to unit_number
    if unit: updates.append("unit_number = %s"); params.append(unit)
    if email: updates.append("email = %s"); params.append(email)

    if updates:
        try:
            params.append(user['id'])
            db.execute_query(f"UPDATE users SET {', '.join(updates)} WHERE id = %s", tuple(params), commit=True)
            print(f"\n{colors.GREEN}✅ User updated successfully!{colors.ENDC}")
        except Exception as e:
            print(f"\n{colors.RED}❌ Database Error: {e}{colors.ENDC}")
    else:
        print(f"\n{colors.YELLOW}No changes made.{colors.ENDC}")

    press_enter()

def toggle_user_status():
    print_header()
    print(f"\n{colors.CYAN}--- Activate/Suspend User ---{colors.ENDC}\n")
    username = get_input("Username")
    users = db.execute_query("SELECT id, status FROM users WHERE username = %s", (username,))
    if not users:
        print(f"\n{colors.RED}User not found!{colors.ENDC}")
        press_enter()
        return

    user = users[0]
    print(f"Current Status: {colors.YELLOW}{user['status']}{colors.ENDC}")
    choice = get_input("Type '1' to set ACTIVE, '0' to set SUSPENDED")

    if choice in ['1', '0']:
        try:
            stat_str = 'ACTIVE' if choice == '1' else 'SUSPENDED'
            db.execute_query("UPDATE users SET status = %s WHERE id = %s", (stat_str, user['id']), commit=True)
            print(f"\n{colors.GREEN}✅ Status updated to {stat_str}!{colors.ENDC}")
        except Exception as e:
            print(f"\n{colors.RED}❌ Database Error: {e}{colors.ENDC}")

    press_enter()


def delete_user():
    print_header()
    print(f"\n{colors.RED}--- Delete User ---{colors.ENDC}\n")
    username = get_input("Username to delete")

    users = db.execute_query("SELECT id, username FROM users WHERE username = %s", (username,))
    if not users:
        print(f"\n{colors.RED}User not found!{colors.ENDC}")
        press_enter()
        return

    user = users[0]
    confirm = get_input(f"Type 'DELETE' to permanently remove {username}")

    if confirm == 'DELETE':
        try:
            db.execute_query("DELETE FROM users WHERE id = %s", (user['id'],), commit=True)
            print(f"\n{colors.GREEN}✅ User permanently deleted from database!{colors.ENDC}")
        except Exception as e:
            print(f"\n{colors.YELLOW}⚠️ Hard delete blocked due to attached records.{colors.ENDC}")
            print(f"{colors.CYAN}Performing a Soft Delete instead...{colors.ENDC}")
            try:
                db.execute_query("UPDATE users SET status = 'SUSPENDED' WHERE id = %s", (user['id'],), commit=True)
                print(f"\n{colors.GREEN}✅ User Soft-Deleted! (Account suspended){colors.ENDC}")
            except Exception as soft_e:
                print(f"\n{colors.RED}❌ Database Error: {soft_e}{colors.ENDC}")

    press_enter()


# ==========================================
# SUPER ADMIN CREATOR
# ==========================================

def create_super_admin():
    print_header()
    print(f"\n{colors.CYAN}--- 👑 Create New Super Admin ---{colors.ENDC}\n")
    username = get_input("Choose Admin Username")
    if not username: return

    if db.execute_query("SELECT id FROM users WHERE username = %s", (username,)):
        print(f"\n{colors.RED}❌ Username exists!{colors.ENDC}");
        press_enter();
        return

    full_name = get_input("Full Name")
    password = get_password("Choose Password")
    if len(password) < 6:
        print(f"\n{colors.RED}❌ Password too short!{colors.ENDC}");
        press_enter();
        return

    try:
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        db.execute_query(
            """INSERT INTO users (username, password_hash, full_name, role, status)
               VALUES (%s, %s, %s, 'SUPER_ADMIN', 'ACTIVE')""",
            (username, hashed_pw, full_name),
            commit=True
        )
        print(f"\n{colors.GREEN}✅ SUCCESS! Super Admin created and activated.{colors.ENDC}")
    except Exception as e:
        print(f"\n{colors.RED}❌ Error: {e}{colors.ENDC}")
    press_enter()


# ==========================================
# DATABASE MANAGEMENT
# ==========================================

def database_management():
    while True:
        print_header()
        print(f"\n{colors.CYAN}--- Database Management ---{colors.ENDC}\n")
        print(f"{colors.YELLOW}1.{colors.ENDC} Show Database Stats")
        print(f"{colors.YELLOW}2.{colors.ENDC} Show Table List")
        print(f"{colors.YELLOW}3.{colors.ENDC} Show Table Row Counts")
        print(f"{colors.YELLOW}4.{colors.ENDC} Execute Custom Query")
        print(f"{colors.YELLOW}5.{colors.ENDC} Clear/Reset specific table")
        print(f"{colors.YELLOW}6.{colors.ENDC} Seed Default Data")
        print(f"{colors.YELLOW}7.{colors.ENDC} Back to Main Menu")

        choice = get_input("\nSelect option")
        if choice == '1':
            data_statistics()
        elif choice == '2':
            show_tables()
        elif choice == '3':
            show_table_counts()
        elif choice == '4':
            custom_query()
        elif choice == '5':
            clear_table_data()
        elif choice == '6':
            seed_data()
        elif choice == '7':
            break


def show_tables():
    print_header()
    print(f"\n{colors.CYAN}--- Database Tables ---{colors.ENDC}\n")
    try:
        tables = db.execute_query("SHOW TABLES")
        for i, t in enumerate(tables):
            print(f"  {i + 1}. {list(t.values())[0]}")
    except Exception as e:
        print(f"{colors.RED}Error: {e}{colors.ENDC}")
    press_enter()


def show_table_counts():
    print_header()
    print(f"\n{colors.CYAN}--- Table Row Counts ---{colors.ENDC}\n")
    try:
        tables = db.execute_query("SHOW TABLES")
        for t in tables:
            t_name = list(t.values())[0]
            cnt = db.execute_query(f"SELECT COUNT(*) as c FROM {t_name}")
            print(f"{t_name:<25} : {cnt[0]['c']} rows")
    except Exception as e:
        print(f"{colors.RED}Error: {e}{colors.ENDC}")
    press_enter()


def custom_query():
    print_header()
    print(f"\n{colors.CYAN}--- Execute Custom Query ---{colors.ENDC}\n")
    print(f"{colors.RED}WARNING: Raw SQL Execution!{colors.ENDC}")
    query = get_input("SQL Query")
    if not query: return
    try:
        if query.strip().upper().startswith("SELECT"):
            res = db.execute_query(query)
            for r in res[:10]: print(r)
            if len(res) > 10: print(f"... and {len(res) - 10} more")
        else:
            db.execute_query(query, commit=True)
            print(f"{colors.GREEN}Query executed!{colors.ENDC}")
    except Exception as e:
        print(f"{colors.RED}Error: {e}{colors.ENDC}")
    press_enter()


def clear_table_data():
    print_header()
    t_name = get_input("Table name to clear")
    if get_input(f"Type 'YES' to truncate {t_name}") == 'YES':
        try:
            db.execute_query(f"TRUNCATE TABLE {t_name}", commit=True)
            print(f"{colors.GREEN}Table cleared!{colors.ENDC}")
        except Exception as e:
            print(f"{colors.RED}Error: {e}{colors.ENDC}")
    press_enter()


def seed_data():
    print_header()
    if get_input("Type 'SEED' to populate default data") == 'SEED':
        try:
            db.seed_default_users()
            db.seed_emergency_contacts()
            print(f"{colors.GREEN}Seeding Complete!{colors.ENDC}")
        except Exception as e:
            print(f"{colors.RED}Error: {e}{colors.ENDC}")
    press_enter()


# ==========================================
# DATA RESET MENU
# ==========================================

def data_reset_menu():
    while True:
        print_header()
        print(f"\n{colors.RED}{colors.BOLD}--- ⚠️ DATA RESET & CLEAR ---{colors.ENDC}\n")
        print(f"{colors.YELLOW}1.{colors.ENDC} 🔴 CLEAR ALL TRANSACTIONAL DATA (Keep Users)")
        print(f"{colors.YELLOW}2.{colors.ENDC} 🔄 Reset App to Fresh State (Wipe & Seed)")
        print(f"{colors.YELLOW}3.{colors.ENDC} 🔙 Back to Main Menu")
        choice = get_input("\nSelect option")
        if choice == '1':
            clear_all_data()
        elif choice == '2':
            reset_app()
        elif choice == '3':
            break


def clear_all_data():
    print_header()
    print(f"{colors.RED}This deletes everything EXCEPT user accounts!{colors.ENDC}")
    if get_input("Type 'DELETE ALL' to confirm") == 'DELETE ALL':
        tables = [
            'visitors', 'vehicle_logs', 'complaints', 'parcels',
            'audit_logs', 'notices', 'patrol_logs'
        ]
        for t in tables:
            try:
                db.execute_query(f"DELETE FROM {t}", commit=True)
            except:
                pass
        print(f"{colors.GREEN}All transactional data cleared!{colors.ENDC}")
    press_enter()


def reset_app():
    print_header()
    print(f"{colors.RED}This wipes data AND re-seeds defaults!{colors.ENDC}")
    if get_input("Type 'RESET APP' to confirm") == 'RESET APP':
        clear_all_data()
        seed_data()
        print(f"{colors.GREEN}App reset to fresh state!{colors.ENDC}")
    press_enter()


def data_statistics():
    print_header()
    print(f"\n{colors.CYAN}--- Data Statistics ---{colors.ENDC}\n")
    tables = {
        'Users': 'users',
        'Resident Profiles': 'resident_profiles',
        'Resident Vehicles': 'resident_vehicles',
        'Visitors': 'visitors',
        'Vehicle Logs': 'vehicle_logs',
        'Complaints': 'complaints',
        'Parcels': 'parcels',
        'Notices': 'notices',
        'Audit Logs': 'audit_logs'
    }
    print(f"{colors.BOLD}{'Table':<25} {'Records':<10}{colors.ENDC}")
    print("-" * 35)
    for name, table_name in tables.items():
        try:
            cnt = db.execute_query(f"SELECT COUNT(*) as cnt FROM {table_name}")
            print(f"{name:<25} {cnt[0]['cnt']:<10}")
        except:
            print(f"{name:<25} {'0 (Missing)':<10}")
    press_enter()

# ==========================================
# MAIN ROUTINE
# ==========================================

def main():
    try:
        db.init_database()
    except Exception as e:
        print(f"{colors.RED}Database initialization error: {e}{colors.ENDC}")
        return

    while True:
        print_header()
        print(f"\n{colors.GREEN}Welcome to Admin Tools{colors.ENDC}\n")
        print(f"{colors.YELLOW}1.{colors.ENDC} System Information")
        print(f"{colors.YELLOW}2.{colors.ENDC} User Management")
        print(f"{colors.YELLOW}3.{colors.ENDC} Maintenance Mode")
        print(f"{colors.YELLOW}4.{colors.ENDC} Database Management")
        print(f"{colors.YELLOW}5.{colors.ENDC} 👑 Create Super Admin ID")
        print(f"{colors.YELLOW}6.{colors.ENDC} 👔 Create Manager ID")
        print(f"{colors.YELLOW}7.{colors.ENDC} 📊 Data Statistics")
        print(f"{colors.YELLOW}8.{colors.ENDC} ⚠️ Data Reset & Clear")
        print(f"{colors.YELLOW}9.{colors.ENDC} Exit")

        choice = get_input("\nSelect option")
        if choice == '1': system_info()
        elif choice == '2': user_management()
        elif choice == '3': maintenance_mode()
        elif choice == '4': database_management()
        elif choice == '5': create_super_admin()
        elif choice == '6': create_manager()  # <-- New Manager routing
        elif choice == '7': data_statistics()
        elif choice == '8': data_reset_menu()
        elif choice == '9':
            print(f"\n{colors.GREEN}Goodbye!{colors.ENDC}\n")
            break
        else:
            print(f"\n{colors.RED}Invalid option!{colors.ENDC}")
            press_enter()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{colors.YELLOW}Program interrupted by user. Exiting...{colors.ENDC}")
        sys.exit(0)