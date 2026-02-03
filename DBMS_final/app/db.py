"""db.py
Database helpers for the CLI app.
This is a minimal, editable helper; update the connection config before use.

Configuration is loaded from db_config.py (not tracked in git for security).
Copy db_config_template.py to db_config.py and update with your credentials.
"""
import mysql.connector
from mysql.connector import Error
import os
import sys

# Try to import database configuration
try:
    from .db_config import DB_CONFIG
except ImportError:
    # Fallback for development - look for db_config.py in current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    try:
        from db_config import DB_CONFIG
    except ImportError:
        print("ERROR: db_config.py not found!")
        print("Please copy db_config_template.py to db_config.py and update with your database credentials.")
        sys.exit(1)


def get_connection():
    """Return a new MySQL connection. Caller should close it."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Database connection error: {e}")
        raise


def run_query(sql, params=None, fetch=True):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(sql, params or ())
        if fetch:
            rows = cur.fetchall()
        else:
            rows = None
            conn.commit()
        return rows
    finally:
        cur.close()
        conn.close()


def call_proc(proc_name, params=None):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.callproc(proc_name, params or [])
        # Fetch any result sets returned
        results = []
        for res in cur.stored_results():
            results.append(res.fetchall())
        conn.commit()
        return results
    finally:
        cur.close()
        conn.close()


def test_connection(verbose=True):
    """Try to connect using DB_CONFIG and print a short report."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if verbose:
            print('Connected to MySQL server version:', conn.get_server_info())
            print('Using database:', DB_CONFIG.get('database'))
        conn.close()
        return True
    except Error as e:
        if verbose:
            print('Database connection error:', e)
        return False


if __name__ == '__main__':
    ok = test_connection()
    if not ok:
        print('\nTip: edit app/db.py and set DB_CONFIG values (host, port, user, password, database)')
    else:
        print('Connection test passed')
