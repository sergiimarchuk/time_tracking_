import sys
import uuid
sys.path.insert(0, '/opt/dev-py/TimeTracking-dev/libs')

import psycopg2
from psycopg2.extras import RealDictCursor


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

