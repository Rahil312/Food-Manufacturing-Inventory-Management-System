"""main.py
Entry point for the CLI app.
Run: python main.py (from app directory) or python -m app.main (from parent directory)
"""
import sys
import os

# Add parent directory to path if running from app directory
if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

from app.auth import login
from app.menus import manufacturer_menu, supplier_menu, viewer_menu


def main():
    print('DBMS Final — CLI skeleton')
    user = None
    while not user:
        user = login()
    role = user.get('role')
    if role == 'MANUFACTURER':
        manufacturer_menu(user)
    elif role == 'SUPPLIER':
        supplier_menu(user)
    elif role == 'VIEWER':
        viewer_menu(user)
    else:
        print('Unknown role')


if __name__ == '__main__':
    main()
