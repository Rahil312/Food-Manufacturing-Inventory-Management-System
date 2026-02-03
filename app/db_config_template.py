"""db_config_template.py
Database configuration template.
Copy this file to db_config.py and update with your actual values.
DO NOT commit db_config.py to version control.
"""

# ----- Edit these values to match your MySQL server -----
DB_CONFIG = {
    'host': 'localhost',        # e.g. 'localhost' or '127.0.0.1' or remote host
    'port': 3306,               # MySQL default port
    'user': 'root',             # database user
    'password': 'YOUR_PASSWORD_HERE',  # <-- REPLACE with your DB password
    'database': 'dbms_project'  # database name - using dbms_project consistently
}
# ------------------------------------------------------