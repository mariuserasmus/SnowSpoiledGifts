#!/usr/bin/env python3
"""
Script to set specific users as administrators
"""

import os
from src.database import Database

def set_admin_users():
    """Set the specified users as administrators"""
    db_path = os.getenv('DATABASE_PATH', 'database/signups.db')
    db = Database(db_path)

    admin_emails = [
        'mariuserasmus69@gmail.com',
        'elmienerasmus@gmail.com',
        'meganmerasmus@gmail.com'
    ]

    print("Setting admin users...")
    for email in admin_emails:
        result = db.set_user_admin(email, is_admin=True)
        if result:
            print(f"[OK] {email} - Admin status granted")
        else:
            print(f"[FAIL] {email} - User not found or error occurred")

    print("\nAdmin setup complete!")

if __name__ == '__main__':
    set_admin_users()
