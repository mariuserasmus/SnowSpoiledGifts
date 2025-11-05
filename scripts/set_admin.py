#!/usr/bin/env python3
"""
Script to set a user as admin by email address.
Usage: python set_admin.py
"""

from src.database import Database

def set_admin(email):
    """Set a user as admin"""
    db = Database('database/signups.db')
    conn = db.get_connection()
    cursor = conn.cursor()

    # Check if user exists
    cursor.execute('SELECT id, name, email, is_admin FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()

    if not user:
        print(f"[X] User with email '{email}' not found!")
        conn.close()
        return False

    # Update user to admin
    cursor.execute('UPDATE users SET is_admin = 1 WHERE email = ?', (email,))
    conn.commit()
    conn.close()

    print(f"[OK] User '{user['name']}' ({email}) is now an admin!")
    return True

if __name__ == '__main__':
    print("=== Set User as Admin ===\n")

    # List of admin emails
    admin_emails = [
        'mariuserasmus69@gmail.com',
        'elmienerasmus@gmail.com'
    ]

    for email in admin_emails:
        set_admin(email)
