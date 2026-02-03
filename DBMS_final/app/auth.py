"""auth.py
Simple authentication helpers. This is an app-level auth (not DB privileges).
Change to use secure password hashing in production (bcrypt, argon2).
"""
from getpass import getpass
from app.db import run_query


def login():
    """Simple login - checks username and password from user_account table"""
    print('\n' + '='*60)
    print('LOGIN')
    print('='*60)
    
    username = input('Username: ').strip()
    password = getpass('Password: ')
    
    # Query user account
    rows = run_query(
        'SELECT user_id, username, role, manufacturer_id, supplier_id, password_hash, first_name, last_name FROM user_account WHERE username = %s', 
        (username,)
    )
    
    if not rows:
        print('❌ User not found')
        return None
    
    user = rows[0]
    stored_password = user.get('password_hash', '')
    
    # Simple password check
    # In production, use bcrypt.checkpw() or similar
    # For demo, accept: actual password, 'password123', or any password if hash starts with 'HASH_'
    if (password == stored_password or 
        password == 'password123' or 
        stored_password.startswith('HASH_')):
        
        print(f"✅ Logged in as {username} ({user['role']})")
        if user['first_name']:
            print(f"   Welcome, {user['first_name']} {user['last_name']}!")
        return user
    else:
        print('❌ Invalid credentials')
        return None
