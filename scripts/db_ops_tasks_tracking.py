import sys
from datetime import datetime
sys.path.insert(0, '/opt/dev-py/TimeTracking-dev/libs')

from scripts.db_connection import get_db_connection  # Assumes this returns psycopg2 connection

def insert_task(user_id, task_name, start_time, end_time, extra_data=None):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO tasks (user_id, task_name, start_time, end_time, extra_data)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, task_name, start_time, end_time, extra_data))

def get_tasks_for_user_on_date(user_id, date_obj):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, task_name, start_time, end_time, extra_data
                FROM tasks
                WHERE user_id = %s AND DATE(start_time) = %s
                ORDER BY start_time
            """, (user_id, date_obj))
            rows = cur.fetchall()

            return [
                (
                    r[0],
                    r[1],
                    r[2],  # already datetime
                    r[3],
                    r[4]
                ) for r in rows
            ]

