"""db.py
Database helpers for the CLI app.
This version uses environment variables for security.
Copy db_config_template.py to db_config.py and update with your values.
"""
import mysql.connector
from mysql.connector import Error
import os

# Try to import from local config file, fall back to environment variables
try:
    from .db_config import DB_CONFIG
except ImportError:
    # Fall back to environment variables or defaults
    DB_CONFIG = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', '052726'),  # Keep current password as default
        'database': os.getenv('DB_NAME', 'dbms_project')
    }


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
