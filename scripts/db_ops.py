import sys
import uuid
sys.path.insert(0, '/opt/dev-py/TimeTracking-dev/libs')

import psycopg2
from psycopg2.extras import RealDictCursor

# Update these values with your actual DB credentials
DB_CONFIG = {
    'dbname': 'mydatabase',
    'user': 'myuser',
    'password': 'mypassword',
    'host': 'localhost',
    'port': 55432,
}

def get_db_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    with conn.cursor() as cur:
        cur.execute("SET search_path TO auto_time_tracker;")
    return conn

def _validate_uuid(uid):
    return str(uid)

def get_user_id_by_uid(uid):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SET search_path TO auto_time_tracker;")
            cur.execute("SELECT id FROM users WHERE ldap_entry_uuid = %s", (uid,))
            result = cur.fetchone()
            return result[0] if result else None

def get_user_id_by_int_id(user_id):
    # user_id is an integer like 3, 5, 42
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SET search_path TO auto_time_tracker;")
            cur.execute("SELECT id FROM users WHERE id = %s", (user_id,))
            result = cur.fetchone()
            return result[0] if result else None

def create_user_if_not_exists(uid, vor_name, nach_name, email="no-email@example.com", contact_info=None):
    uid_str = _validate_uuid(uid)
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE ldap_entry_uuid = %s", (uid_str,))
            existing = cur.fetchone()
            if not existing:
                cur.execute("""
                    INSERT INTO users (ldap_entry_uuid, vor_name, nach_name, email, additional_contact_info)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """, (uid_str, vor_name, nach_name, email, contact_info))
                return cur.fetchone()[0]
            return existing[0]

def insert_vehicle(user_id, plate_number, extra_info):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO vehicles (user_id, plate_number, extra_info)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (user_id, plate_number, extra_info))
            return cur.fetchone()[0]

def insert_vehicle_file(vehicle_id, file_type, file_path):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO vehicle_files (vehicle_id, file_type, file_path)
                VALUES (%s, %s, %s)
            """, (vehicle_id, file_type, file_path))

def get_user_files_by_uid(uid):
    uid_str = _validate_uuid(uid)
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT 
                    vf.id,
                    v.plate_number,
                    vf.file_type,
                    vf.file_path,
                    vf.uploaded_at
                FROM 
                    vehicle_files vf
                JOIN 
                    vehicles v ON vf.vehicle_id = v.id
                JOIN 
                    users u ON v.user_id = u.id
                WHERE 
                    u.ldap_entry_uuid = %s
                ORDER BY 
                    vf.uploaded_at DESC
            """, (uid_str,))
            return cur.fetchall()
