"""
Script to reset admin password
Usage: python scripts/reset_admin_password.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.database import Database
import bcrypt

def reset_password():
    # Get database path (same as in config.py)
    db_path = os.getenv('DATABASE_PATH', 'database/signups.db')
    db = Database(db_path)

    email = "mariuserasmus69@gmail.com"
    new_password = input("Enter new password for admin: ")
    confirm_password = input("Confirm new password: ")

    if new_password != confirm_password:
        print("❌ Passwords do not match!")
        return

    if len(new_password) < 6:
        print("❌ Password must be at least 6 characters long!")
        return

    # Hash the new password
    password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

    # Update the password in database
    conn = db.get_connection()
    cursor = conn.cursor()

    try:
        # Check if user exists
        cursor.execute('SELECT id, email, is_admin FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()

        if not user:
            print(f"❌ User with email '{email}' not found!")
            conn.close()
            return

        if not user['is_admin']:
            print(f"⚠️  Warning: User '{email}' is not an admin!")

        # Update password
        cursor.execute('''
            UPDATE users
            SET password_hash = ?
            WHERE email = ?
        ''', (password_hash, email))

        conn.commit()
        conn.close()

        print(f"✅ Password successfully reset for: {email}")
        if user['is_admin']:
            print("   User is confirmed as ADMIN")

    except Exception as e:
        conn.close()
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    print("=" * 50)
    print("Admin Password Reset Utility")
    print("=" * 50)
    reset_password()
