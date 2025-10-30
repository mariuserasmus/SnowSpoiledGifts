#!/usr/bin/env python3
"""
Script to reset user password
"""

import bcrypt
from src.database import Database

def reset_password(email, new_password):
    """Reset password for a user"""
    db = Database('database/signups.db')

    # Hash the new password
    password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Update the database
    conn = db.get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            UPDATE users
            SET password_hash = ?
            WHERE email = ?
        ''', (password_hash, email.lower()))

        conn.commit()
        rows = cursor.rowcount
        conn.close()

        if rows > 0:
            print(f"[OK] Password reset successful for {email}")
            print(f"[OK] New password: {new_password}")
            return True
        else:
            print(f"[FAIL] User not found: {email}")
            return False

    except Exception as e:
        conn.close()
        print(f"[ERROR] Failed to reset password: {str(e)}")
        return False

if __name__ == '__main__':
    email = 'mariuserasmus69@gmail.com'
    new_password = 'admin123'  # Change this to whatever you want

    print(f"Resetting password for {email}...")
    reset_password(email, new_password)
    print("\nYou can now login with:")
    print(f"  Email: {email}")
    print(f"  Password: {new_password}")
