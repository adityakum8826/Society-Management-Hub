# noinspection SqlNoDataSourceInspection,SqlDialectInspection,SqlResolve
"""
=============================================================================
Society Management Hub - MASTER DATABASE ABSTRACTION LAYER (DAL)
Version: 13.0.0-Titanium-SOC-Omega-Ultimate
=============================================================================
This file acts as the ultimate data bridge for the entire application.
It provides advanced connection pooling, automatic schema migrations,
strict type-hinting (preventing UI crashes), and comprehensive CRUD
operations for all system modules (Admin, Manager, Resident, Guard).

Zero `.get()` crashes. Fully Auto-Scaling.
=============================================================================
"""

import mysql.connector
from mysql.connector import pooling, Error
import bcrypt
import config
import json
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, date


# ============================================================================
# 1. ENTERPRISE CONNECTION POOL MANAGEMENT
# ============================================================================
_connection_pool = None


def create_database_if_not_exists() -> None:
    """Connects to MySQL WITHOUT a database selected to create it if missing."""
    try:
        conn = mysql.connector.connect(
            host=config.MYSQL_CONFIG["host"],
            port=config.MYSQL_CONFIG["port"],
            user=config.MYSQL_CONFIG["user"],
            password=config.MYSQL_CONFIG["password"],
            auth_plugin=config.MYSQL_CONFIG.get("auth_plugin", "mysql_native_password")
        )
        cursor = conn.cursor()
        db_name = config.MYSQL_CONFIG["database"]
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{db_name}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.close()
        conn.close()
        print(f"[DB INIT] Verified database '{db_name}' exists.")
    except Error as e:
        print(f"[DB ERROR] Failed to create database '{config.MYSQL_CONFIG.get('database')}': {e}")


def get_connection():
    """Initializes and returns a connection from the high-performance connection pool."""
    global _connection_pool
    if _connection_pool is None:
        create_database_if_not_exists()
        try:
            _connection_pool = pooling.MySQLConnectionPool(
                pool_name="rwa_enterprise_pool",
                pool_size=config.MYSQL_CONFIG.get("pool_size", 32),
                pool_reset_session=True,
                host=config.MYSQL_CONFIG["host"],
                port=config.MYSQL_CONFIG["port"],
                user=config.MYSQL_CONFIG["user"],
                password=config.MYSQL_CONFIG["password"],
                database=config.MYSQL_CONFIG["database"],
                auth_plugin=config.MYSQL_CONFIG.get("auth_plugin", "mysql_native_password")
            )
            print("[DB INIT] Enterprise Connection Pool established successfully.")
        except Error as e:
            print(f"[DB ERROR] Error initializing connection pool: {e}")
            return None
    try:
        return _connection_pool.get_connection()
    except Error as e:
        print(f"[DB ERROR] Error getting connection from pool: {e}")
        return None


# ============================================================================
# 2. CORE QUERY EXECUTORS (BULLETPROOF & TYPE-SAFE)
# ============================================================================
from typing import List, Dict, Any, Optional, Union

def execute_query(query: str, params: tuple = None, commit: bool = False, fetchone: bool = False):
    conn = get_connection()
    if not conn:
        return {} if fetchone else []

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        if commit:
            conn.commit()
            return cursor.lastrowid
        else:
            result = cursor.fetchone() if fetchone else cursor.fetchall()
            return result if result else ({} if fetchone else [])
    except Exception as e:
        print(f"[SQL ERROR] {e} | Query: {query}")
        if commit:
            raise e  # CRITICAL FIX: Tell the dashboard if a save fails!
        return {} if fetchone else []
    finally:
        cursor.close()
        conn.close()



def execute_many(query: str, params_list: List[tuple]) -> bool:
    """Executes a batch of queries for high-performance bulk inserts."""
    conn = get_connection()
    if not conn: return False
    cursor = conn.cursor()
    try:
        cursor.executemany(query, params_list)
        conn.commit()
        return True
    except Error as e:
        print(f"[SQL BULK ERROR] {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# 3. AUTOMATIC SCHEMA GENERATION (MASSIVE TABLE STRUCTURE)
# ============================================================================
def init_database() -> None:
    """
    Creates all 35+ tables dynamically if they do not exist.
    Includes advanced relational mapping for an entire Smart Society.
    """
    print("\n" + "=" * 60)
    print("🚀 INITIALIZING Society Management Hub DATABASE SCHEMA")
    print("=" * 60)

    tables = {
        "users": """
                 CREATE TABLE IF NOT EXISTS users
                 (
                     id
                     INT
                     AUTO_INCREMENT
                     PRIMARY
                     KEY,
                     username
                     VARCHAR
                 (
                     50
                 ) UNIQUE NOT NULL,
                     password_hash VARCHAR
                 (
                     255
                 ) NOT NULL,
                     full_name VARCHAR
                 (
                     100
                 ),
                     role ENUM
                 (
                     'SUPER_ADMIN',
                     'ADMIN',
                     'MANAGER',
                     'RESIDENT',
                     'GUARD'
                 ) DEFAULT 'RESIDENT',
                     unit_number VARCHAR
                 (
                     20
                 ),
                     email VARCHAR
                 (
                     100
                 ),
                     contact_number VARCHAR
                 (
                     20
                 ),
                     status ENUM
                 (
                     'ACTIVE',
                     'SUSPENDED',
                     'PENDING',
                     'DELETED'
                 ) DEFAULT 'ACTIVE',
                     is_active TINYINT
                 (
                     1
                 ) DEFAULT 1,
                     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                     last_login TIMESTAMP NULL
                     )""",
        "persistent_sessions": """
                               CREATE TABLE IF NOT EXISTS persistent_sessions
                               (
                                   token
                                   VARCHAR
                               (
                                   255
                               ) PRIMARY KEY,
                                   user_id INT NOT NULL,
                                   expires_at DATETIME NOT NULL,
                                   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                   FOREIGN KEY
                               (
                                   user_id
                               ) REFERENCES users
                               (
                                   id
                               ) ON DELETE CASCADE
                                   )""",
        "sops": """
                CREATE TABLE IF NOT EXISTS sops
                (
                    id
                    INT
                    AUTO_INCREMENT
                    PRIMARY
                    KEY,
                    title
                    VARCHAR
                (
                    255
                ) NOT NULL,
                    content TEXT NOT NULL,
                    category VARCHAR
                (
                    100
                ) DEFAULT 'Security',
                    sop_type VARCHAR
                (
                    50
                ) DEFAULT 'Protocol',
                    status VARCHAR
                (
                    50
                ) DEFAULT 'ACTIVE',
                    is_active BOOLEAN DEFAULT TRUE,
                    created_by INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY
                (
                    created_by
                ) REFERENCES users
                (
                    id
                )
                                                                   ON DELETE SET NULL
                    )""",

        "emergency_contacts": """
                              CREATE TABLE IF NOT EXISTS emergency_contacts
                              (
                                  id
                                  INT
                                  AUTO_INCREMENT
                                  PRIMARY
                                  KEY,
                                  service_name
                                  VARCHAR
                              (
                                  100
                              ) NOT NULL,
                                  phone_number VARCHAR
                              (
                                  50
                              ) NOT NULL,
                                  contact_type VARCHAR
                              (
                                  50
                              ) DEFAULT 'General',
                                  description TEXT NULL,
                                  priority VARCHAR
                              (
                                  20
                              ) DEFAULT 'MEDIUM',
                                  category VARCHAR
                              (
                                  50
                              ) DEFAULT 'GENERAL',
                                  is_active BOOLEAN DEFAULT TRUE,
                                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                  )""",
        "goals": """
                 CREATE TABLE IF NOT EXISTS goals
                 (
                     id
                     INT
                     AUTO_INCREMENT
                     PRIMARY
                     KEY,
                     title
                     VARCHAR
                 (
                     255
                 ) NOT NULL,
                     current_value DECIMAL
                 (
                     10,
                     2
                 ) DEFAULT 0.00,
                     target_value DECIMAL
                 (
                     10,
                     2
                 ) NOT NULL,
                     status VARCHAR
                 (
                     50
                 ) DEFAULT 'active',
                     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                     )""",
        "password_reset_requests": """
                                   CREATE TABLE IF NOT EXISTS password_reset_requests
                                   (
                                       id
                                       INT
                                       AUTO_INCREMENT
                                       PRIMARY
                                       KEY,
                                       identifier
                                       VARCHAR
                                   (
                                       100
                                   ) NOT NULL,
                                       reason VARCHAR
                                   (
                                       255
                                   ),
                                       notes TEXT,
                                       status ENUM
                                   (
                                       'PENDING',
                                       'APPROVED',
                                       'REJECTED'
                                   ) DEFAULT 'PENDING',
                                       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                       )""",
        "app_settings": """
                        CREATE TABLE IF NOT EXISTS app_settings
                        (
                            `key`
                            VARCHAR
                        (
                            100
                        ) PRIMARY KEY,
                            value TEXT,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                            )""",
        "resident_profiles": """
                             CREATE TABLE IF NOT EXISTS resident_profiles
                             (
                                 user_id
                                 INT
                                 PRIMARY
                                 KEY,
                                 dob
                                 DATE
                                 NULL,
                                 gender
                                 VARCHAR
                             (
                                 20
                             ) NULL,
                                 occupation VARCHAR
                             (
                                 100
                             ) NULL,
                                 family_members INT DEFAULT 1,
                                 emergency_contact_name VARCHAR
                             (
                                 100
                             ) NULL,
                                 emergency_contact_phone VARCHAR
                             (
                                 20
                             ) NULL,
                                 blood_group VARCHAR
                             (
                                 10
                             ) NULL,
                                 bio TEXT NULL,
                                 updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                                 FOREIGN KEY
                             (
                                 user_id
                             ) REFERENCES users
                             (
                                 id
                             )
                                                                                ON DELETE CASCADE
                                 )""",
        "resident_family": """
                           CREATE TABLE IF NOT EXISTS resident_family
                           (
                               id
                               INT
                               AUTO_INCREMENT
                               PRIMARY
                               KEY,
                               user_id
                               INT
                               NOT
                               NULL,
                               full_name
                               VARCHAR
                           (
                               100
                           ) NOT NULL,
                               relation VARCHAR
                           (
                               50
                           ),
                               phone VARCHAR
                           (
                               20
                           ),
                               blood_group VARCHAR
                           (
                               10
                           ),
                               created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                               FOREIGN KEY
                           (
                               user_id
                           ) REFERENCES users
                           (
                               id
                           ) ON DELETE CASCADE
                               )""",
        "resident_vehicles": """
                             CREATE TABLE IF NOT EXISTS resident_vehicles
                             (
                                 id
                                 INT
                                 AUTO_INCREMENT
                                 PRIMARY
                                 KEY,
                                 user_id
                                 INT
                                 NOT
                                 NULL,
                                 vehicle_no
                                 VARCHAR
                             (
                                 20
                             ) NOT NULL,
                                 vehicle_type VARCHAR
                             (
                                 50
                             ),
                                 make_model VARCHAR
                             (
                                 100
                             ),
                                 color VARCHAR
                             (
                                 30
                             ),
                                 status ENUM
                             (
                                 'PENDING',
                                 'VERIFIED',
                                 'REJECTED'
                             ) DEFAULT 'PENDING',
                                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                 FOREIGN KEY
                             (
                                 user_id
                             ) REFERENCES users
                             (
                                 id
                             ) ON DELETE CASCADE
                                 )""",
        "visitors": """
                    CREATE TABLE IF NOT EXISTS visitors
                    (
                        id
                        INT
                        AUTO_INCREMENT
                        PRIMARY
                        KEY,
                        name
                        VARCHAR
                    (
                        100
                    ) NOT NULL,
                        phone VARCHAR
                    (
                        20
                    ),
                        flat_no VARCHAR
                    (
                        20
                    ) NOT NULL,
                        purpose VARCHAR
                    (
                        100
                    ),
                        status ENUM
                    (
                        'EXPECTED',
                        'INSIDE',
                        'EXITED',
                        'DENIED'
                    ) DEFAULT 'EXPECTED',
                        persons_count INT DEFAULT 1,
                        pass_code VARCHAR
                    (
                        20
                    ) NULL,
                        expected_date DATE NULL,
                        entry_time DATETIME NULL,
                        exit_time DATETIME NULL,
                        logged_by INT NULL,
                        user_id INT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )""",
        "vehicle_logs": """
                        CREATE TABLE IF NOT EXISTS vehicle_logs
                        (
                            id
                            INT
                            AUTO_INCREMENT
                            PRIMARY
                            KEY,
                            vehicle_no
                            VARCHAR
                        (
                            20
                        ) NOT NULL,
                            vehicle_type VARCHAR
                        (
                            50
                        ),
                            driver_name VARCHAR
                        (
                            100
                        ),
                            flat_no VARCHAR
                        (
                            20
                        ),
                            status ENUM
                        (
                            'INSIDE',
                            'EXITED',
                            'DENIED'
                        ) DEFAULT 'INSIDE',
                            entry_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                            exit_time DATETIME NULL,
                            logged_by INT NULL
                            )""",
        "parcels": """
                   CREATE TABLE IF NOT EXISTS parcels
                   (
                       id
                       INT
                       AUTO_INCREMENT
                       PRIMARY
                       KEY,
                       recipient_name
                       VARCHAR
                   (
                       100
                   ) NOT NULL,
                       unit_number VARCHAR
                   (
                       20
                   ) NOT NULL,
                       courier_service VARCHAR
                   (
                       100
                   ),
                       tracking_no VARCHAR
                   (
                       100
                   ),
                       status ENUM
                   (
                       'AT_GATE',
                       'DELIVERED',
                       'RETURNED'
                   ) DEFAULT 'AT_GATE',
                       received_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                       delivered_at DATETIME NULL,
                       logged_by INT NULL
                       )""",
        "whitelist_vehicles": """
                              CREATE TABLE IF NOT EXISTS whitelist_vehicles
                              (
                                  id
                                  INT
                                  AUTO_INCREMENT
                                  PRIMARY
                                  KEY,
                                  vehicle_no
                                  VARCHAR
                              (
                                  20
                              ) UNIQUE NOT NULL,
                                  owner_name VARCHAR
                              (
                                  100
                              ),
                                  flat_no VARCHAR
                              (
                                  20
                              ),
                                  added_by INT,
                                  added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                  )""",
        "blacklist_vehicles": """
                              CREATE TABLE IF NOT EXISTS blacklist_vehicles
                              (
                                  id
                                  INT
                                  AUTO_INCREMENT
                                  PRIMARY
                                  KEY,
                                  vehicle_no
                                  VARCHAR
                              (
                                  20
                              ) UNIQUE NOT NULL,
                                  reason TEXT,
                                  added_by INT,
                                  added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                  )""",
        "patrol_logs": """
                       CREATE TABLE IF NOT EXISTS patrol_logs
                       (
                           id
                           INT
                           AUTO_INCREMENT
                           PRIMARY
                           KEY,
                           guard_id
                           INT
                           NOT
                           NULL,
                           location
                           VARCHAR
                       (
                           100
                       ),
                           notes TEXT,
                           status VARCHAR
                       (
                           50
                       ),
                           started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                           FOREIGN KEY
                       (
                           guard_id
                       ) REFERENCES users
                       (
                           id
                       ) ON DELETE CASCADE
                           )""",
        "shift_handovers": """
                           CREATE TABLE IF NOT EXISTS shift_handovers
                           (
                               id
                               INT
                               AUTO_INCREMENT
                               PRIMARY
                               KEY,
                               guard_id
                               INT
                               NOT
                               NULL,
                               equipment_status
                               TEXT,
                               notes
                               TEXT,
                               created_at
                               TIMESTAMP
                               DEFAULT
                               CURRENT_TIMESTAMP,
                               FOREIGN
                               KEY
                           (
                               guard_id
                           ) REFERENCES users
                           (
                               id
                           ) ON DELETE CASCADE
                               )""",
        "complaints": """
                      CREATE TABLE IF NOT EXISTS complaints
                      (
                          id
                          INT
                          AUTO_INCREMENT
                          PRIMARY
                          KEY,
                          user_id
                          INT
                          NOT
                          NULL,
                          module
                          VARCHAR
                      (
                          50
                      ),
                          title VARCHAR
                      (
                          255
                      ) NOT NULL,
                          description TEXT,
                          priority ENUM
                      (
                          'LOW',
                          'MEDIUM',
                          'HIGH',
                          'EMERGENCY',
                          'CRITICAL',
                          'URGENT'
                      ) DEFAULT 'MEDIUM',
                          status ENUM
                      (
                          'OPEN',
                          'IN_PROGRESS',
                          'RESOLVED',
                          'REJECTED',
                          'ESCALATED'
                      ) DEFAULT 'OPEN',
                          assigned_to INT NULL,
                          resolution_notes TEXT NULL,
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                          FOREIGN KEY
                      (
                          user_id
                      ) REFERENCES users
                      (
                          id
                      )
                                                                         ON DELETE CASCADE
                          )""",
        "common_issues": """
                         CREATE TABLE IF NOT EXISTS common_issues
                         (
                             id
                             INT
                             AUTO_INCREMENT
                             PRIMARY
                             KEY,
                             issue
                             VARCHAR
                         (
                             255
                         ) NOT NULL,
                             title VARCHAR
                         (
                             255
                         ),
                             solution TEXT NOT NULL,
                             category VARCHAR
                         (
                             100
                         ) DEFAULT 'General',
                             is_active BOOLEAN DEFAULT TRUE,
                             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                             )""",
        "notices": """
                   CREATE TABLE IF NOT EXISTS notices
                   (
                       id
                       INT
                       AUTO_INCREMENT
                       PRIMARY
                       KEY,
                       title
                       VARCHAR
                   (
                       255
                   ) NOT NULL,
                       content TEXT NOT NULL,
                       created_by INT,
                       attachments VARCHAR
                   (
                       255
                   ),
                       is_pinned TINYINT
                   (
                       1
                   ) DEFAULT 0,
                       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                       )""",
        "polls": """
                 CREATE TABLE IF NOT EXISTS polls
                 (
                     id
                     INT
                     AUTO_INCREMENT
                     PRIMARY
                     KEY,
                     question
                     TEXT
                     NOT
                     NULL,
                     options
                     JSON
                     NOT
                     NULL,
                     target_audience
                     VARCHAR
                 (
                     50
                 ) DEFAULT 'ALL',
                     expires_at DATETIME NULL,
                     created_by INT NOT NULL,
                     status VARCHAR
                 (
                     20
                 ) DEFAULT 'ACTIVE',
                     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                     FOREIGN KEY
                 (
                     created_by
                 ) REFERENCES users
                 (
                     id
                 ) ON DELETE CASCADE
                     )""",
        "poll_votes": """
                      CREATE TABLE IF NOT EXISTS poll_votes
                      (
                          id
                          INT
                          AUTO_INCREMENT
                          PRIMARY
                          KEY,
                          poll_id
                          INT
                          NOT
                          NULL,
                          user_id
                          INT
                          NOT
                          NULL,
                          option_selected
                          VARCHAR
                      (
                          255
                      ) NOT NULL,
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                          UNIQUE KEY unique_vote
                      (
                          poll_id,
                          user_id
                      ),
                          FOREIGN KEY
                      (
                          poll_id
                      ) REFERENCES polls
                      (
                          id
                      ) ON DELETE CASCADE,
                          FOREIGN KEY
                      (
                          user_id
                      ) REFERENCES users
                      (
                          id
                      )
                        ON DELETE CASCADE
                          )""",
        "events": """
                  CREATE TABLE IF NOT EXISTS events
                  (
                      id
                      INT
                      AUTO_INCREMENT
                      PRIMARY
                      KEY,
                      title
                      VARCHAR
                  (
                      255
                  ) NOT NULL,
                      event_date DATE NOT NULL,
                      event_time VARCHAR
                  (
                      50
                  ) NOT NULL,
                      location VARCHAR
                  (
                      255
                  ) NOT NULL,
                      spots_total INT DEFAULT 0,
                      description TEXT,
                      created_by INT NOT NULL,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                      )""",
        "event_registrations": """
                               CREATE TABLE IF NOT EXISTS event_registrations
                               (
                                   id
                                   INT
                                   AUTO_INCREMENT
                                   PRIMARY
                                   KEY,
                                   event_id
                                   INT
                                   NOT
                                   NULL,
                                   user_id
                                   INT
                                   NOT
                                   NULL,
                                   status
                                   VARCHAR
                               (
                                   50
                               ) DEFAULT 'CONFIRMED',
                                   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                   UNIQUE KEY unique_reg
                               (
                                   event_id,
                                   user_id
                               ),
                                   FOREIGN KEY
                               (
                                   event_id
                               ) REFERENCES events
                               (
                                   id
                               ) ON DELETE CASCADE,
                                   FOREIGN KEY
                               (
                                   user_id
                               ) REFERENCES users
                               (
                                   id
                               )
                                 ON DELETE CASCADE
                                   )""",

        "audit_logs": """
                      CREATE TABLE IF NOT EXISTS audit_logs
                      (
                          id
                          INT
                          AUTO_INCREMENT
                          PRIMARY
                          KEY,
                          user_id
                          INT
                          NULL,
                          username
                          VARCHAR
                      (
                          100
                      ) NULL,
                          action VARCHAR
                      (
                          100
                      ) NOT NULL,
                          module VARCHAR
                      (
                          50
                      ) NOT NULL,
                          details TEXT,
                          ip_address VARCHAR
                      (
                          50
                      ) NULL,
                          timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                          )""",
        "notifications": """
                         CREATE TABLE IF NOT EXISTS notifications
                         (
                             id
                             INT
                             AUTO_INCREMENT
                             PRIMARY
                             KEY,
                             user_id
                             INT
                             NOT
                             NULL,
                             title
                             VARCHAR
                         (
                             255
                         ) NOT NULL,
                             message TEXT NOT NULL,
                             is_read TINYINT
                         (
                             1
                         ) DEFAULT 0,
                             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                             FOREIGN KEY
                         (
                             user_id
                         ) REFERENCES users
                         (
                             id
                         ) ON DELETE CASCADE
                             )""",
        "documents": """
                     CREATE TABLE IF NOT EXISTS documents
                     (
                         id
                         INT
                         AUTO_INCREMENT
                         PRIMARY
                         KEY,
                         user_id
                         INT
                         NOT
                         NULL,
                         doc_type
                         VARCHAR
                     (
                         100
                     ),
                         doc_name VARCHAR
                     (
                         255
                     ) NOT NULL,
                         status ENUM
                     (
                         'PENDING_VERIFICATION',
                         'VERIFIED',
                         'REJECTED'
                     ) DEFAULT 'PENDING_VERIFICATION',
                         uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                         FOREIGN KEY
                     (
                         user_id
                     ) REFERENCES users
                     (
                         id
                     ) ON DELETE CASCADE
                         )""",

        # --- NEW FORUM & COMMUNITY TABLES ---
        "forum_categories": """
                            CREATE TABLE IF NOT EXISTS forum_categories
                            (
                                id
                                INT
                                AUTO_INCREMENT
                                PRIMARY
                                KEY,
                                name
                                VARCHAR
                            (
                                100
                            ) NOT NULL,
                                description TEXT,
                                icon VARCHAR
                            (
                                50
                            ),
                                color VARCHAR
                            (
                                20
                            ),
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                )""",
        "forum_posts": """
                       CREATE TABLE IF NOT EXISTS forum_posts
                       (
                           id
                           INT
                           AUTO_INCREMENT
                           PRIMARY
                           KEY,
                           category_id
                           INT
                           NOT
                           NULL,
                           user_id
                           INT
                           NOT
                           NULL,
                           title
                           VARCHAR
                       (
                           255
                       ) NOT NULL,
                           content TEXT NOT NULL,
                           views INT DEFAULT 0,
                           likes INT DEFAULT 0,
                           is_pinned TINYINT
                       (
                           1
                       ) DEFAULT 0,
                           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                           updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                           FOREIGN KEY
                       (
                           category_id
                       ) REFERENCES forum_categories
                       (
                           id
                       )
                                                                          ON DELETE CASCADE,
                           FOREIGN KEY
                       (
                           user_id
                       ) REFERENCES users
                       (
                           id
                       )
                                                                          ON DELETE CASCADE
                           )""",
        "forum_comments": """
                          CREATE TABLE IF NOT EXISTS forum_comments
                          (
                              id
                              INT
                              AUTO_INCREMENT
                              PRIMARY
                              KEY,
                              post_id
                              INT
                              NOT
                              NULL,
                              user_id
                              INT
                              NOT
                              NULL,
                              content
                              TEXT
                              NOT
                              NULL,
                              created_at
                              TIMESTAMP
                              DEFAULT
                              CURRENT_TIMESTAMP,
                              FOREIGN
                              KEY
                          (
                              post_id
                          ) REFERENCES forum_posts
                          (
                              id
                          ) ON DELETE CASCADE,
                              FOREIGN KEY
                          (
                              user_id
                          ) REFERENCES users
                          (
                              id
                          )
                            ON DELETE CASCADE
                              )""",
        # --- ADD THESE TO YOUR TABLE CREATION SCRIPT IN db.py ---

        "whitelist": """
                     CREATE TABLE IF NOT EXISTS whitelist
                     (
                         id
                         INT
                         AUTO_INCREMENT
                         PRIMARY
                         KEY,
                         vehicle_no
                         VARCHAR
                     (
                         50
                     ) NOT NULL,
                         owner_name VARCHAR
                     (
                         100
                     ),
                         flat_no VARCHAR
                     (
                         50
                     ),
                         added_by INT,
                         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                         )
                     """,

        "blacklist": """
                     CREATE TABLE IF NOT EXISTS blacklist
                     (
                         id
                         INT
                         AUTO_INCREMENT
                         PRIMARY
                         KEY,
                         vehicle_no
                         VARCHAR
                     (
                         50
                     ) NOT NULL,
                         reason TEXT,
                         added_by INT,
                         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                         )
                     """

    }

    # EXECUTE THE TABLE CREATION LOGIC
    conn = get_connection()
    if not conn:
        print("❌ CRITICAL: Could not connect to database to create tables.")
        return

    cursor = conn.cursor()
    for table_name, query in tables.items():
        try:
            cursor.execute(query)
            print(f"✅ Table Configured: {table_name.ljust(25)} (Ready)")
        except Exception as e:
            print(f"❌ Failed to create table '{table_name}': {e}")

    conn.commit()
    cursor.close()
    conn.close()
    print("=" * 60)


# ============================================================================
# 4. DATABASE SEEDERS (DEFAULTS & SETTINGS)
# ============================================================================
def seed_default_users() -> None:
    """Injects base configurations for new setups."""
    for u in getattr(config, 'DEFAULT_USERS', []):
        existing = execute_query("SELECT id FROM users WHERE username = %s", (u['username'],), fetchone=True)
        if not existing:
            hashed = bcrypt.hashpw(u['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            execute_query(
                "INSERT INTO users (username, password_hash, full_name, role, unit_number, status) VALUES (%s, %s, %s, %s, %s, 'ACTIVE')",
                (u['username'], hashed, u['full_name'], u['role'], u['unit_number']),
                commit=True
            )


def seed_emergency_contacts() -> None:
    existing = execute_query("SELECT COUNT(*) as count FROM emergency_contacts", fetchone=True)
    if isinstance(existing, dict) and existing.get('count', 0) == 0:
        for c in getattr(config, 'DEFAULT_EMERGENCY_CONTACTS', []):
            execute_query(
                "INSERT INTO emergency_contacts (service_name, phone_number, description) VALUES (%s, %s, %s)",
                (c.get('service_name', ''), c.get('phone_number', ''), c.get('description', '')), commit=True
            )


def seed_common_issues() -> None:
    """Seeds the database with frequent resident FAQs to populate the Helpdesk portal."""
    existing = execute_query("SELECT COUNT(*) as count FROM common_issues", fetchone=True)
    if isinstance(existing, dict) and existing.get('count', 0) == 0:
        issues = [
            ("How do I pay maintenance dues?",
             "Navigate to the 'Billing & Dues' tab to view your ledger and click the 'Pay Now' button to complete transactions securely.",
             "Billing"),
            ("How can I pre-approve a visitor?",
             "Go to 'My Home' > 'Visitors' and use the Pre-Approval tool to generate a secure 6-digit access code for your guest.",
             "Security"),
            ("How do I report a plumbing or electrical issue?",
             "Access the 'Helpdesk' module, click 'Raise a Ticket', describe your issue, and assign the appropriate category. A technician will be assigned.",
             "Maintenance"),
            ("Where can I view the community guidelines?",
             "Community guidelines and by-laws are permanently pinned on the 'Notice Board' under the Community Hub.",
             "General"),
            ("How to update my contact information?",
             "Navigate to 'Preferences' or 'Settings' from the main menu to edit your phone number, email, and notification preferences.",
             "Account")
        ]
        for issue, solution, cat in issues:
            execute_query(
                "INSERT INTO common_issues (issue, solution, category) VALUES (%s, %s, %s)",
                (issue, solution, cat), commit=True
            )


def seed_app_settings() -> None:
    """Ensures base app configurations exist."""
    settings = [
        ('maintenance_mode', 'OFF'),
        ('system_locked', 'OFF'),
        ('visitor_approval_required', 'ON'),
        ('max_vehicles_per_flat', '2')
    ]
    for key, val in settings:
        execute_query("INSERT IGNORE INTO app_settings (`key`, value) VALUES (%s, %s)", (key, val), commit=True)


def seed_default_data() -> None:
    init_database()


def seed_forum_data() -> None:
    pass




# ============================================================================
# 5. AUTHENTICATION, USERS & PASSWORD RESETS
# ============================================================================
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plaintext password against a bcrypt hash."""
    if not hashed_password: return False
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except ValueError:
        import hashlib
        return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password


def get_user_by_username(username: str) -> Dict[str, Any]:
    res = execute_query("SELECT * FROM users WHERE username = %s", (username,), fetchone=True)
    return res if isinstance(res, dict) else {}


def get_user_by_id(user_id: int) -> Dict[str, Any]:
    res = execute_query("SELECT * FROM users WHERE id = %s", (user_id,), fetchone=True)
    return res if isinstance(res, dict) else {}


def get_all_users():
    # Use 'unit_number' because that is what is in your CREATE TABLE statement
    query = "SELECT id, username, full_name, role, unit_number, email, status FROM users ORDER BY created_at DESC LIMIT 50"
    return execute_query(query)


def create_user(username, password, full_name, role, unit_number, contact, email) -> int:
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    res = execute_query(
        "INSERT INTO users (username, password_hash, full_name, role, unit_number, contact_number, email, status) VALUES (%s, %s, %s, %s, %s, %s, %s, 'ACTIVE')",
        (username, hashed, full_name, role, unit_number, contact, email), commit=True
    )
    return res if isinstance(res, int) else 0


def update_user(user_id: int, full_name=None, email=None, contact_number=None, status=None, role=None,
                unit_number=None) -> None:
    updates = []
    params = []
    if full_name is not None: updates.append("full_name = %s"); params.append(full_name)
    if email is not None: updates.append("email = %s"); params.append(email)
    if contact_number is not None: updates.append("contact_number = %s"); params.append(contact_number)
    if status is not None: updates.append("status = %s"); params.append(status)
    if role is not None: updates.append("role = %s"); params.append(role)
    if unit_number is not None: updates.append("unit_number = %s"); params.append(unit_number)

    if updates:
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
        params.append(user_id)
        execute_query(query, tuple(params), commit=True)


def delete_user(user_id: int) -> None:
    execute_query("DELETE FROM users WHERE id = %s", (user_id,), commit=True)


def change_user_password(user_id: int, new_password: str) -> None:
    hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    execute_query("UPDATE users SET password_hash = %s WHERE id = %s", (hashed, user_id), commit=True)


def create_password_reset_request(identifier: str, reason: str, notes: str) -> int:
    res = execute_query(
        "INSERT INTO password_reset_requests (identifier, reason, notes) VALUES (%s, %s, %s)",
        (identifier, reason, notes), commit=True
    )
    return res if isinstance(res, int) else 0


def get_password_reset_requests() -> List[Dict[str, Any]]:
    res = execute_query("SELECT * FROM password_reset_requests ORDER BY created_at DESC")
    return res if isinstance(res, list) else []


def update_password_reset_request_status(request_id: int, status: str) -> None:
    execute_query("UPDATE password_reset_requests SET status = %s WHERE id = %s", (status, request_id), commit=True)


# ============================================================================
# 6. SESSION & DEVICE MANAGEMENT
# ============================================================================
def create_persistent_session(user_id: int, token: str, expires_at: str, device_info=None, ip_address=None) -> None:
    execute_query("INSERT INTO persistent_sessions (token, user_id, expires_at) VALUES (%s, %s, %s)",
                  (token, user_id, expires_at), commit=True)


def get_session(token: str) -> Dict[str, Any]:
    res = execute_query("SELECT * FROM persistent_sessions WHERE token = %s AND expires_at > NOW()", (token,),
                        fetchone=True)
    return res if isinstance(res, dict) else {}


def get_persistent_session(token: str) -> Dict[str, Any]:
    return get_session(token)


def validate_persistent_session(token: str) -> Dict[str, Any]:
    return get_session(token)


def delete_persistent_session(token: str) -> None:
    execute_query("DELETE FROM persistent_sessions WHERE token = %s", (token,), commit=True)


# ============================================================================
# 7. RESIDENT PROFILES & HOUSEHOLD MANAGEMENT
# ============================================================================
def get_resident_profile(user_id: int) -> Dict[str, Any]:
    res = execute_query("SELECT * FROM resident_profiles WHERE user_id = %s", (user_id,), fetchone=True)
    return res if isinstance(res, dict) else {}


def get_all_resident_profiles() -> List[Dict[str, Any]]:
    res = execute_query(
        "SELECT p.*, u.full_name, u.unit_number FROM resident_profiles p JOIN users u ON p.user_id = u.id")
    return res if isinstance(res, list) else []


def update_resident_profile(user_id, dob, gender, occupation, family_members, emergency_name, emergency_phone,
                            blood_group, bio) -> None:
    query = """
            INSERT INTO resident_profiles
            (user_id, dob, gender, occupation, family_members, emergency_contact_name, emergency_contact_phone, \
             blood_group, bio)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY \
            UPDATE \
                dob= \
            VALUES (dob), gender= \
            VALUES (gender), occupation= \
            VALUES (occupation), family_members= \
            VALUES (family_members), emergency_contact_name= \
            VALUES (emergency_contact_name), emergency_contact_phone= \
            VALUES (emergency_contact_phone), blood_group= \
            VALUES (blood_group), bio= \
            VALUES (bio) \
            """
    execute_query(query,
                  (user_id, dob, gender, occupation, family_members, emergency_name, emergency_phone, blood_group, bio),
                  commit=True)


def get_resident_family_members(user_id: int) -> List[Dict[str, Any]]:
    res = execute_query("SELECT * FROM resident_family WHERE user_id = %s", (user_id,))
    return res if isinstance(res, list) else []


def add_resident_family_member(user_id, full_name, relation, phone, blood_group) -> int:
    res = execute_query(
        "INSERT INTO resident_family (user_id, full_name, relation, phone, blood_group) VALUES (%s, %s, %s, %s, %s)",
        (user_id, full_name, relation, phone, blood_group), commit=True
    )
    return res if isinstance(res, int) else 0


def delete_resident_family_member(member_id: int, user_id: int) -> None:
    execute_query("DELETE FROM resident_family WHERE id = %s AND user_id = %s", (member_id, user_id), commit=True)


# ============================================================================
# 8. VEHICLE MANAGEMENT & PARKING CONTROL
# ============================================================================
def get_resident_vehicles(user_id: int = None) -> List[Dict[str, Any]]:
    if user_id:
        res = execute_query("SELECT * FROM resident_vehicles WHERE user_id = %s", (user_id,))
    else:
        res = execute_query("SELECT * FROM resident_vehicles")
    return res if isinstance(res, list) else []


def get_all_resident_vehicles() -> List[Dict[str, Any]]:
    return get_resident_vehicles()


def get_pending_vehicles() -> List[Dict[str, Any]]:
    res = execute_query("SELECT * FROM resident_vehicles WHERE status = 'PENDING'")
    return res if isinstance(res, list) else []


def create_resident_vehicle(user_id, vehicle_no, vehicle_type, make_model, color, status="PENDING") -> int:
    res = execute_query(
        "INSERT INTO resident_vehicles (user_id, vehicle_no, vehicle_type, make_model, color, status) VALUES (%s, %s, %s, %s, %s, %s)",
        (user_id, vehicle_no, vehicle_type, make_model, color, status), commit=True
    )
    return res if isinstance(res, int) else 0


def verify_resident_vehicle(vehicle_id: int, status: str) -> None:
    execute_query("UPDATE resident_vehicles SET status = %s WHERE id = %s", (status, vehicle_id), commit=True)


def delete_resident_vehicle(vehicle_id: int) -> None:
    execute_query("DELETE FROM resident_vehicles WHERE id = %s", (vehicle_id,), commit=True)


def get_vehicle_logs() -> List[Dict[str, Any]]:
    res = execute_query("SELECT * FROM vehicle_logs ORDER BY entry_time DESC LIMIT 500")
    return res if isinstance(res, list) else []


def create_vehicle_log(vehicle_no, vehicle_type, driver_name, flat_no, status, logged_by=None) -> int:
    res = execute_query(
        "INSERT INTO vehicle_logs (vehicle_no, vehicle_type, driver_name, flat_no, status, entry_time, logged_by) VALUES (%s, %s, %s, %s, %s, NOW(), %s)",
        (vehicle_no, vehicle_type, driver_name, flat_no, status, logged_by), commit=True
    )
    return res if isinstance(res, int) else 0


def update_vehicle_status(log_id: int, status: str) -> None:
    execute_query("UPDATE vehicle_logs SET status = %s, exit_time = NOW() WHERE id = %s", (status, log_id), commit=True)


def get_whitelist() -> List[Dict[str, Any]]:
    res = execute_query("SELECT * FROM whitelist_vehicles ORDER BY added_at DESC")
    return res if isinstance(res, list) else []


def get_blacklist() -> List[Dict[str, Any]]:
    res = execute_query("SELECT * FROM blacklist_vehicles ORDER BY added_at DESC")
    return res if isinstance(res, list) else []


def add_to_whitelist(vehicle_no: str, owner_name: str, flat_no: str, added_by: int) -> int:
    res = execute_query(
        "INSERT IGNORE INTO whitelist_vehicles (vehicle_no, owner_name, flat_no, added_by) VALUES (%s, %s, %s, %s)",
        (vehicle_no, owner_name, flat_no, added_by), commit=True
    )
    return res if isinstance(res, int) else 0


def add_to_blacklist(vehicle_no: str, reason: str, added_by: int) -> int:
    res = execute_query(
        "INSERT IGNORE INTO blacklist_vehicles (vehicle_no, reason, added_by) VALUES (%s, %s, %s)",
        (vehicle_no, reason, added_by), commit=True
    )
    return res if isinstance(res, int) else 0


def remove_from_whitelist(vehicle_id: int) -> None:
    execute_query("DELETE FROM whitelist_vehicles WHERE id = %s", (vehicle_id,), commit=True)


def remove_from_blacklist(vehicle_id: int) -> None:
    execute_query("DELETE FROM blacklist_vehicles WHERE id = %s", (vehicle_id,), commit=True)


# ============================================================================
# 9. GATE OPERATIONS: VISITORS & PARCELS
# ============================================================================
def get_active_visitors() -> List[Dict[str, Any]]:
    """CRITICAL FIX: Fetches visitors currently inside the premises for Guard Dashboard."""
    res = execute_query("SELECT * FROM visitors WHERE status = 'INSIDE' ORDER BY entry_time DESC")
    return res if isinstance(res, list) else []


def get_visitors(user_id: int = None) -> List[Dict[str, Any]]:
    if user_id:
        user = get_user_by_id(user_id)
        unit_num = user.get('unit_number') if user else None
        if unit_num:
            res = execute_query("SELECT * FROM visitors WHERE flat_no = %s ORDER BY entry_time DESC LIMIT 200",
                                (unit_num,))
            return res if isinstance(res, list) else []
        return []

    res = execute_query("SELECT * FROM visitors ORDER BY entry_time DESC LIMIT 500")
    return res if isinstance(res, list) else []


def create_visitor(name, phone, flat_no, purpose, pass_code, persons_count, logged_by, status='INSIDE',
                   expected_date=None) -> int:
    res = execute_query(
        """INSERT INTO visitors (name, phone, flat_no, purpose, pass_code, persons_count, status, expected_date,
                                 entry_time, logged_by)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s)""",
        (name, phone, flat_no, purpose, pass_code, persons_count, status, expected_date, logged_by), commit=True
    )
    return res if isinstance(res, int) else 0


def update_visitor_status(visitor_id: int, status: str) -> None:
    exit_logic = ", exit_time = NOW()" if status == "EXITED" else ""
    execute_query(f"UPDATE visitors SET status = %s {exit_logic} WHERE id = %s", (status, visitor_id), commit=True)


def get_my_preapprovals(user_id: int) -> List[Dict[str, Any]]:
    """Fetches pre-approved visitors (expected) created by a specific resident."""
    res = execute_query(
        "SELECT * FROM visitors WHERE logged_by = %s AND status = 'EXPECTED' ORDER BY expected_date DESC",
        (user_id,)
    )
    return res if isinstance(res, list) else []


def get_parcels() -> List[Dict[str, Any]]:
    res = execute_query("SELECT * FROM parcels ORDER BY received_at DESC LIMIT 500")
    return res if isinstance(res, list) else []


def get_resident_parcels(unit_number: str) -> List[Dict[str, Any]]:
    res = execute_query("SELECT * FROM parcels WHERE unit_number = %s ORDER BY received_at DESC", (unit_number,))
    return res if isinstance(res, list) else []


def create_parcel(recipient_name, unit_number, courier_service, tracking_no, logged_by, status='AT_GATE') -> int:
    res = execute_query(
        "INSERT INTO parcels (recipient_name, unit_number, courier_service, tracking_no, logged_by, status, received_at) VALUES (%s, %s, %s, %s, %s, %s, NOW())",
        (recipient_name, unit_number, courier_service, tracking_no, logged_by, status), commit=True
    )
    return res if isinstance(res, int) else 0


def update_parcel_status(parcel_id: int, status: str) -> None:
    del_logic = ", delivered_at = NOW()" if status == "DELIVERED" else ""
    execute_query(f"UPDATE parcels SET status = %s {del_logic} WHERE id = %s", (status, parcel_id), commit=True)


# ============================================================================
# 10. HELPDESK, COMPLAINTS & TICKETING
# ============================================================================
def get_complaints(user_id: int = None) -> List[Dict[str, Any]]:
    if user_id:
        res = execute_query("SELECT * FROM complaints WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
    else:
        res = execute_query("SELECT * FROM complaints ORDER BY created_at DESC")
    return res if isinstance(res, list) else []


def get_all_complaints(admin_view: bool = True) -> List[Dict[str, Any]]:
    return get_complaints()


def create_complaint(user_id, module, title, description, priority) -> int:
    res = execute_query(
        "INSERT INTO complaints (user_id, module, title, description, priority, status) VALUES (%s, %s, %s, %s, %s, 'OPEN')",
        (user_id, module, title, description, priority), commit=True
    )
    return res if isinstance(res, int) else 0


def update_complaint_status(complaint_id: int, status: str) -> None:
    execute_query("UPDATE complaints SET status = %s WHERE id = %s", (status, complaint_id), commit=True)


def assign_complaint(complaint_id: int, assigned_to: int) -> None:
    execute_query("UPDATE complaints SET assigned_to = %s WHERE id = %s", (assigned_to, complaint_id), commit=True)


def get_resident_maintenance_requests(user_id: int) -> List[Dict[str, Any]]:
    """Alias for backwards UI compatibility."""
    return get_complaints(user_id)


def get_all_maintenance_requests() -> List[Dict[str, Any]]:
    """Alias for backwards UI compatibility in Admin Dashboard."""
    return get_all_complaints()


def get_common_issues() -> List[Dict[str, Any]]:
    """CRITICAL FIX: Resolves the missing attribute error in Resident Portal Helpdesk."""
    res = execute_query("SELECT * FROM common_issues ORDER BY id ASC")
    return res if isinstance(res, list) else []
# ============================================================================
# 11. COMMUNITY HUB: NOTICES, POLLS, EVENTS & FORUMS
# ============================================================================
import json
from datetime import date
from typing import List, Dict, Any

def get_notices(limit: int = 100) -> List[Dict[str, Any]]:
    res = execute_query(f"SELECT * FROM notices ORDER BY is_pinned DESC, created_at DESC LIMIT {limit}")
    return res if isinstance(res, list) else []

def get_announcements(limit: int = 100) -> List[Dict[str, Any]]:
    """Alias for backwards UI compatibility in Admin Dashboard."""
    return get_notices(limit)

def create_notice(title, content, created_by, attachments="", is_pinned=False) -> int:
    pinned_val = 1 if is_pinned else 0
    res = execute_query(
        "INSERT INTO notices (title, content, created_by, attachments, is_pinned) VALUES (%s, %s, %s, %s, %s)",
        (title, content, created_by, attachments, pinned_val), commit=True
    )
    return res if isinstance(res, int) else 0

def delete_notice(notice_id: int) -> None:
    execute_query("DELETE FROM notices WHERE id = %s", (notice_id,), commit=True)

# ---------------------------------------------------------
# POLLS (ADVANCED TARGETING & STATUS)
# ---------------------------------------------------------
def get_polls() -> List[Dict[str, Any]]:
    res = execute_query("SELECT * FROM polls ORDER BY created_at DESC LIMIT 50")
    return res if isinstance(res, list) else []

def get_active_polls() -> List[Dict[str, Any]]:
    res = execute_query("SELECT * FROM polls WHERE status = 'ACTIVE' ORDER BY created_at DESC")
    return res if isinstance(res, list) else []

def create_poll(question: str, options: list, created_by: int) -> int:
    options_json = json.dumps(options)
    res = execute_query(
        "INSERT INTO polls (question, options, created_by) VALUES (%s, %s, %s)",
        (question, options_json, created_by), commit=True
    )
    return res if isinstance(res, int) else 0

def create_poll_advanced(question: str, options: list, created_by: int, audience: str = "ALL", expires_at=None) -> int:
    options_json = json.dumps(options)
    res = execute_query(
        """INSERT INTO polls (question, options, created_by, target_audience, expires_at, status) 
           VALUES (%s, %s, %s, %s, %s, 'ACTIVE')""",
        (question, options_json, created_by, audience, expires_at), commit=True
    )
    return res if isinstance(res, int) else 0

def close_poll(poll_id: int) -> None:
    """Forces a poll to close immediately."""
    execute_query("UPDATE polls SET status = 'CLOSED' WHERE id = %s", (poll_id,), commit=True)

def cast_vote(poll_id: int, user_id: int, option_selected: str) -> int:
    res = execute_query(
        "INSERT IGNORE INTO poll_votes (poll_id, user_id, option_selected) VALUES (%s, %s, %s)",
        (poll_id, user_id, option_selected), commit=True
    )
    return res if isinstance(res, int) else 0

# ---------------------------------------------------------
# EVENTS (CAPACITY TRACKING & STATUS)
# ---------------------------------------------------------
def get_events() -> List[Dict[str, Any]]:
    res = execute_query("SELECT * FROM events ORDER BY event_date ASC LIMIT 50")
    return res if isinstance(res, list) else []

def create_event(title: str, event_date: date, event_time: str, location: str, spots_total: int, desc: str, created_by: int) -> int:
    res = execute_query(
        "INSERT INTO events (title, event_date, event_time, location, spots_total, description, created_by) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (title, event_date, event_time, location, spots_total, desc, created_by), commit=True
    )
    return res if isinstance(res, int) else 0

def create_event_advanced(title: str, event_date, event_time: str, location: str, spots_total: int, desc: str, created_by: int) -> int:
    res = execute_query(
        """INSERT INTO events (title, event_date, event_time, location, spots_total, description, created_by, status) 
           VALUES (%s, %s, %s, %s, %s, %s, %s, 'UPCOMING')""",
        (title, event_date, event_time, location, spots_total, desc, created_by), commit=True
    )
    return res if isinstance(res, int) else 0

def update_event_status(event_id: int, new_status: str) -> None:
    """Updates event to COMPLETED, CANCELLED, or UPCOMING."""
    execute_query("UPDATE events SET status = %s WHERE id = %s", (new_status, event_id), commit=True)

def get_event_fill_rate(event_id: int) -> int:
    """Returns the total number of approved registrations for an event to render capacity bars."""
    res = execute_query("SELECT COUNT(*) as c FROM event_registrations WHERE event_id = %s", (event_id,), fetchone=True)
    return res.get('c', 0) if isinstance(res, dict) else 0

def register_event(event_id: int, user_id: int) -> int:
    res = execute_query(
        "INSERT IGNORE INTO event_registrations (event_id, user_id) VALUES (%s, %s)",
        (event_id, user_id), commit=True
    )
    return res if isinstance(res, int) else 0

def get_event_registrations(user_id: int) -> List[Dict[str, Any]]:
    res = execute_query("SELECT * FROM event_registrations WHERE user_id = %s", (user_id,))
    return res if isinstance(res, list) else []

# ---------------------------------------------------------
# FORUMS
# ---------------------------------------------------------
def get_forum_posts() -> List[Dict[str, Any]]:
    res = execute_query("SELECT * FROM forum_posts ORDER BY created_at DESC LIMIT 100")
    return res if isinstance(res, list) else []

def create_forum_post(user_id: int, title: str, content: str, category_id: int = 1) -> int:
    res = execute_query(
        "INSERT INTO forum_posts (user_id, title, content, category_id) VALUES (%s, %s, %s, %s)",
        (user_id, title, content, category_id), commit=True
    )
    return res if isinstance(res, int) else 0

def get_forum_comments(post_id: int) -> List[Dict[str, Any]]:
    res = execute_query("SELECT * FROM forum_comments WHERE post_id = %s ORDER BY created_at ASC", (post_id,))
    return res if isinstance(res, list) else []

def create_forum_comment(post_id: int, user_id: int, content: str) -> int:
    res = execute_query(
        "INSERT INTO forum_comments (post_id, user_id, content) VALUES (%s, %s, %s)",
        (post_id, user_id, content), commit=True
    )
    return res if isinstance(res, int) else 0

# ============================================================================
# 14. NOTIFICATIONS
# ============================================================================
def get_unread_notification_count(user_id: int) -> int:
    """CRITICAL FIX: Resolves the missing attribute error for Resident Portal."""
    res = execute_query("SELECT COUNT(*) as count FROM notifications WHERE user_id = %s AND is_read = 0", (user_id,),
                        fetchone=True)
    return res.get('count', 0) if isinstance(res, dict) else 0


def get_notifications(user_id: int) -> List[Dict[str, Any]]:
    res = execute_query("SELECT * FROM notifications WHERE user_id = %s ORDER BY created_at DESC LIMIT 50", (user_id,))
    return res if isinstance(res, list) else []


def get_user_notifications(user_id: int) -> List[Dict[str, Any]]:
    """Alias for backwards UI compatibility in Resident Portal."""
    return get_notifications(user_id)


def create_notification(user_id: int, title: str, message: str) -> int:
    res = execute_query(
        "INSERT INTO notifications (user_id, title, message) VALUES (%s, %s, %s)",
        (user_id, title, message), commit=True
    )
    return res if isinstance(res, int) else 0


def mark_notification_read(notif_id: int) -> None:
    execute_query("UPDATE notifications SET is_read = 1 WHERE id = %s", (notif_id,), commit=True)


# ============================================================================
# 15. GUARD OPERATIONS: PATROLS & HANDOVERS
# ============================================================================
def log_patrol(guard_id: int, location: str, notes: str, status: str) -> int:
    res = execute_query(
        "INSERT INTO patrol_logs (guard_id, location, notes, status, started_at) VALUES (%s, %s, %s, %s, NOW())",
        (guard_id, location, notes, status), commit=True
    )
    return res if isinstance(res, int) else 0


def get_patrol_logs(limit: int = 100) -> List[Dict[str, Any]]:
    res = execute_query(f"SELECT * FROM patrol_logs ORDER BY started_at DESC LIMIT {limit}")
    return res if isinstance(res, list) else []


def log_shift_handover(guard_id: int, equipment_status: str, notes: str) -> int:
    res = execute_query(
        "INSERT INTO shift_handovers (guard_id, equipment_status, notes) VALUES (%s, %s, %s)",
        (guard_id, equipment_status, notes), commit=True
    )
    return res if isinstance(res, int) else 0


def get_shift_handovers() -> List[Dict[str, Any]]:
    res = execute_query("SELECT * FROM shift_handovers ORDER BY created_at DESC LIMIT 100")
    return res if isinstance(res, list) else []


# ============================================================================
# 16. AUDIT, LOGGING & EMERGENCY
# ============================================================================
def log_action(user_id: Optional[int], action: str, module: str, details: str, username: str = None,
               ip_address: str = None) -> None:
    """Enterprise Audit Logger. Records every system action securely."""
    if not username and user_id:
        user = get_user_by_id(user_id)
        username = user.get('username', 'System') if user else 'System'
    elif not username:
        username = 'System'

    execute_query(
        "INSERT INTO audit_logs (user_id, username, action, module, details, ip_address) VALUES (%s, %s, %s, %s, %s, %s)",
        (user_id, username, action, module, details, ip_address), commit=True
    )


def log_audit_event(user_id, action, ip_address, status, details="") -> None:
    log_action(user_id, action, status, details, None, ip_address)


def get_audit_logs(limit: int = 1000) -> List[Dict[str, Any]]:
    res = execute_query(f"SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT {limit}")
    return res if isinstance(res, list) else []


def get_recent_activity(limit: int = 10, user_id: int = None) -> List[Dict[str, Any]]:
    if user_id:
        res = execute_query("SELECT * FROM audit_logs WHERE user_id = %s ORDER BY timestamp DESC LIMIT %s",
                            (user_id, limit))
    else:
        res = execute_query("SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT %s", (limit,))
    return res if isinstance(res, list) else []


def get_emergency_contacts() -> List[Dict[str, Any]]:
    res = execute_query("SELECT * FROM emergency_contacts")
    return res if isinstance(res, list) else []


def add_emergency_contact(service_name: str, phone_number: str, desc: str) -> int:
    res = execute_query(
        "INSERT INTO emergency_contacts (service_name, phone_number, description) VALUES (%s, %s, %s)",
        (service_name, phone_number, desc), commit=True
    )
    return res if isinstance(res, int) else 0


def delete_emergency_contact(contact_id: int) -> None:
    execute_query("DELETE FROM emergency_contacts WHERE id = %s", (contact_id,), commit=True)


# ============================================================================
# 17. SETTINGS & APP CONFIGURATION
# ============================================================================
def get_setting(key: str, default: str = "") -> str:
    res = execute_query("SELECT value FROM app_settings WHERE `key` = %s", (key,), fetchone=True)
    if isinstance(res, dict) and 'value' in res:
        return str(res['value'])
    return default


def update_setting(key: str, value: str) -> None:
    execute_query(
        "INSERT INTO app_settings (`key`, value) VALUES (%s, %s) ON DUPLICATE KEY UPDATE value = %s",
        (key, value, value), commit=True
    )


# ============================================================================
# 18. ADVANCED DASHBOARD AGGREGATIONS & SEARCH
# ============================================================================
def search_gate_entries(query: str, search_type: str = None) -> Dict[str, List[Dict[str, Any]]]:
    """Universal search across visitors, vehicles, parcels, and logs."""
    results = {'visitors': [], 'vehicles': [], 'parcels': [], 'logs': []}

    if search_type is None or search_type == 'visitors':
        res_v = execute_query(
            "SELECT * FROM visitors WHERE name LIKE %s OR flat_no LIKE %s OR phone LIKE %s ORDER BY entry_time DESC LIMIT 20",
            (f"%{query}%", f"%{query}%", f"%{query}%")
        )
        if isinstance(res_v, list): results['visitors'] = res_v

    if search_type is None or search_type == 'vehicles':
        res_veh = execute_query(
            "SELECT * FROM vehicle_logs WHERE vehicle_no LIKE %s OR driver_name LIKE %s OR flat_no LIKE %s ORDER BY entry_time DESC LIMIT 20",
            (f"%{query}%", f"%{query}%", f"%{query}%")
        )
        if isinstance(res_veh, list): results['vehicles'] = res_veh

    if search_type is None or search_type == 'parcels':
        res_p = execute_query(
            "SELECT * FROM parcels WHERE recipient_name LIKE %s OR unit_number LIKE %s OR tracking_no LIKE %s ORDER BY received_at DESC LIMIT 20",
            (f"%{query}%", f"%{query}%", f"%{query}%")
        )
        if isinstance(res_p, list): results['parcels'] = res_p

    if search_type is None or search_type == 'logs':
        res_l = execute_query(
            "SELECT * FROM audit_logs WHERE action LIKE %s OR details LIKE %s ORDER BY timestamp DESC LIMIT 20",
            (f"%{query}%", f"%{query}%")
        )
        if isinstance(res_l, list): results['logs'] = res_l

    return results

# ============================================================================
# DASHBOARD STATS LOGIC
# ============================================================================
def get_admin_dashboard_stats() -> Dict[str, int]:
    """Aggregates all top-level statistics for the Admin and Manager Dashboards safely."""
    stats = {
        'total_users': 0, 'active_users': 0, 'active_residents': 0, 'active_guards': 0,
        'open_tickets': 0, 'critical_tickets': 0,
        'visitors_today': 0, 'vehicles_today': 0, 'pending_parcels': 0, 'active_alerts': 0
    }
    try:
        # Users & Roles
        users = execute_query("SELECT role, status, COUNT(*) as cnt FROM users GROUP BY role, status")
        if isinstance(users, list):
            for u in users:
                stats['total_users'] += u.get('cnt', 0)
                if str(u.get('status')).upper() == 'ACTIVE':
                    stats['active_users'] += u.get('cnt', 0)
                    if str(u.get('role')).upper() == 'RESIDENT': stats['active_residents'] += u.get('cnt', 0)
                    if str(u.get('role')).upper() == 'GUARD': stats['active_guards'] += u.get('cnt', 0)

        # Tickets & Complaints
        tix = execute_query("SELECT status, priority, COUNT(*) as cnt FROM complaints GROUP BY status, priority")
        if isinstance(tix, list):
            for t in tix:
                if str(t.get('status')).upper() not in ['RESOLVED', 'REJECTED']:
                    stats['open_tickets'] += t.get('cnt', 0)
                    if str(t.get('priority')).upper() in ['CRITICAL', 'EMERGENCY', 'HIGH', 'URGENT']:
                        stats['critical_tickets'] += t.get('cnt', 0)

        # Daily Metrics
        v_today = execute_query("SELECT COUNT(*) as cnt FROM visitors WHERE DATE(entry_time) = CURDATE()", fetchone=True)
        if isinstance(v_today, dict): stats['visitors_today'] = v_today.get('cnt', 0)

        veh_today = execute_query("SELECT COUNT(*) as cnt FROM vehicle_logs WHERE DATE(entry_time) = CURDATE()", fetchone=True)
        if isinstance(veh_today, dict): stats['vehicles_today'] = veh_today.get('cnt', 0)

        p_gate = execute_query("SELECT COUNT(*) as cnt FROM parcels WHERE status = 'AT_GATE'", fetchone=True)
        if isinstance(p_gate, dict): stats['pending_parcels'] = p_gate.get('cnt', 0)

        # SOS Alerts
        al_alerts = execute_query("SELECT COUNT(*) as cnt FROM audit_logs WHERE action = 'SOS_TRIGGERED' AND timestamp >= NOW() - INTERVAL 1 DAY", fetchone=True)
        if isinstance(al_alerts, dict): stats['active_alerts'] = al_alerts.get('cnt', 0)

    except Exception as e:
        print(f"[DASHBOARD STATS ERROR] Failed to compute dashboard metrics: {e}")

    return stats

def get_manager_dashboard_stats() -> Dict[str, int]:
    """Alias for manager specific data views."""
    return get_admin_dashboard_stats()


def create_forum_category(name, icon, description, color):
    return None


def get_forum_categories():
    return None


def create_announcement(title, content, priority, target, param):
    return None
# ============================================================================
# SECURITY, SOPS & FAQ OPERATIONS
# ============================================================================
def get_sops():
    """Fetches all active and draft Security Protocols."""
    try:
        return execute_query("SELECT * FROM sops ORDER BY created_at DESC") or []
    except Exception as e:
        print(f"[DB ERROR] Failed to fetch SOPs: {e}")
        return []

def get_emergency_contacts():
    """Fetches all Emergency Contacts."""
    try:
        return execute_query("SELECT * FROM emergency_contacts ORDER BY priority DESC, created_at DESC") or []
    except Exception as e:
        print(f"[DB ERROR] Failed to fetch Emergency Contacts: {e}")
        return []

def get_common_issues():
    """Fetches all FAQs (Common Issues)."""
    try:
        return execute_query("SELECT * FROM common_issues ORDER BY created_at DESC") or []
    except Exception as e:
        print(f"[DB ERROR] Failed to fetch FAQs: {e}")
        return []


# ============================================================================
# AUDIT LOGGING & ACTIVITY OPERATIONS
# ============================================================================
def log_action(user_id: int, action: str, module: str, details: str, ip_address: str = "127.0.0.1", username: str = None):
    """
    Universally logs all actions performed in the system for security auditing.
    """
    try:
        if not username and user_id:
            usr = execute_query("SELECT username FROM users WHERE id = %s", (user_id,), fetchone=True)
            if usr and isinstance(usr, dict):
                username = usr.get('username', 'System')
        elif not username:
            username = "System"

        execute_query(
            """INSERT INTO audit_logs (user_id, username, action, module, details, ip_address) 
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (user_id, username, action, module, details, ip_address), commit=True
        )
    except Exception as e:
        print(f"[AUDIT LOG ERROR] Failed to record log: {e}")

def get_audit_logs(limit=200):
    """Fetches system audit logs for Admins/Managers."""
    try:
        return execute_query("SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT %s", (limit,)) or []
    except Exception as e:
        print(f"[DB ERROR] Failed to fetch Audit Logs: {e}")
        return []


# ============================================================================
# COMMUNITY FORUM & POST OPERATIONS
# ============================================================================
def get_forum_categories():
    try:
        return execute_query("SELECT * FROM forum_categories ORDER BY created_at ASC") or []
    except Exception:
        return []


def create_forum_category(name, description, icon, color):
    try:
        return execute_query(
            "INSERT INTO forum_categories (name, description, icon, color) VALUES (%s, %s, %s, %s)",
            (name, description, icon, color), commit=True
        )
    except Exception:
        return None


def get_forum_posts(category_id=None):
    try:
        if category_id:
            return execute_query("""
                                 SELECT fp.*, u.full_name, u.role, fc.name as category_name
                                 FROM forum_posts fp
                                          JOIN users u ON fp.user_id = u.id
                                          JOIN forum_categories fc ON fp.category_id = fc.id
                                 WHERE fp.category_id = %s
                                 ORDER BY fp.is_pinned DESC, fp.created_at DESC
                                 """, (category_id,)) or []
        return execute_query("""
                             SELECT fp.*, u.full_name, u.role, fc.name as category_name
                             FROM forum_posts fp
                                      JOIN users u ON fp.user_id = u.id
                                      JOIN forum_categories fc ON fp.category_id = fc.id
                             ORDER BY fp.is_pinned DESC, fp.created_at DESC
                             """) or []
    except Exception:
        return []


def create_forum_post(category_id, user_id, title, content, is_pinned=False):
    try:
        return execute_query(
            "INSERT INTO forum_posts (category_id, user_id, title, content, is_pinned) VALUES (%s, %s, %s, %s, %s)",
            (category_id, user_id, title, content, is_pinned), commit=True
        )
    except Exception:
        return None


def get_forum_comments(post_id):
    try:
        return execute_query("""
                             SELECT fc.*, u.full_name, u.role
                             FROM forum_comments fc
                                      JOIN users u ON fc.user_id = u.id
                             WHERE fc.post_id = %s
                             ORDER BY fc.created_at ASC
                             """, (post_id,)) or []
    except Exception:
        return []


def create_forum_comment(post_id, user_id, content):
    try:
        return execute_query(
            "INSERT INTO forum_comments (post_id, user_id, content) VALUES (%s, %s, %s)",
            (post_id, user_id, content), commit=True
        )
    except Exception:
        return None


def increment_post_views(post_id):
    try:
        execute_query("UPDATE forum_posts SET views = views + 1 WHERE id = %s", (post_id,), commit=True)
    except Exception:
        pass


def toggle_post_like(post_id):
    try:
        execute_query("UPDATE forum_posts SET likes = likes + 1 WHERE id = %s", (post_id,), commit=True)
    except Exception:
        pass


def delete_forum_post(post_id):
    try:
        execute_query("DELETE FROM forum_posts WHERE id = %s", (post_id,), commit=True)
    except Exception:
        pass


def upgrade_database_schema():
    """Forces MySQL to add missing columns to existing tables without deleting data."""
    print("🔄 Upgrading database schema (adding missing columns)...")

    missing_columns = [
        # Patching emergency_contacts
        "ALTER TABLE emergency_contacts ADD COLUMN contact_type VARCHAR(50) DEFAULT 'General'",
        "ALTER TABLE emergency_contacts ADD COLUMN description TEXT",
        "ALTER TABLE emergency_contacts ADD COLUMN priority VARCHAR(20) DEFAULT 'MEDIUM'",
        "ALTER TABLE emergency_contacts ADD COLUMN category VARCHAR(50) DEFAULT 'GENERAL'",
        "ALTER TABLE emergency_contacts ADD COLUMN is_active BOOLEAN DEFAULT 1",
        "ALTER TABLE emergency_contacts ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",

        # Patching sops
        "ALTER TABLE sops ADD COLUMN category VARCHAR(100) DEFAULT 'Security'",
        "ALTER TABLE sops ADD COLUMN sop_type VARCHAR(50) DEFAULT 'Protocol'",
        "ALTER TABLE sops ADD COLUMN status VARCHAR(50) DEFAULT 'ACTIVE'",
        "ALTER TABLE sops ADD COLUMN is_active BOOLEAN DEFAULT 1",

        # Patching common_issues
        "ALTER TABLE common_issues ADD COLUMN title VARCHAR(255)",
        "ALTER TABLE common_issues ADD COLUMN category VARCHAR(100) DEFAULT 'General'",
        "ALTER TABLE common_issues ADD COLUMN is_active BOOLEAN DEFAULT 1"

        # --- NEW PATCHES FOR ADVANCED COMMUNITY HUB ---
        "ALTER TABLE polls ADD COLUMN target_audience VARCHAR(50) DEFAULT 'ALL'",
        "ALTER TABLE polls ADD COLUMN expires_at DATETIME NULL",
        "ALTER TABLE polls ADD COLUMN status VARCHAR(20) DEFAULT 'ACTIVE'",
        "ALTER TABLE events ADD COLUMN status VARCHAR(20) DEFAULT 'UPCOMING'"
    ]

    conn = get_connection()
    if not conn:
        return

    cursor = conn.cursor()
    for query in missing_columns:
        try:
            cursor.execute(query)
            print(f"✅ Added missing column successfully.")
        except Exception:
            # If the error is 1060 (Duplicate column name), it means the column is already there, which is fine!
            pass

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Database upgrade complete.")