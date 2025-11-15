"""
Migration script to add user_id field to all quote tables.

This migration adds user_id as a foreign key to users table for:
- quote_requests
- cake_topper_requests
- print_service_requests

Run this script once to update the database schema.
"""

import sqlite3
import os
import sys

# Add parent directory to path to import database module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def add_user_id_to_quotes(db_path):
    """Add user_id column to all quote tables"""

    print(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    tables_to_update = [
        'quote_requests',
        'cake_topper_requests',
        'print_service_requests'
    ]

    for table in tables_to_update:
        try:
            # Check if user_id column already exists
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [column[1] for column in cursor.fetchall()]

            if 'user_id' in columns:
                print(f"[OK] {table}: user_id column already exists, skipping")
                continue

            # Add user_id column (nullable for now to handle existing records)
            print(f"Adding user_id column to {table}...")
            cursor.execute(f'''
                ALTER TABLE {table}
                ADD COLUMN user_id INTEGER REFERENCES users(id)
            ''')

            # Optional: Try to match existing quotes to users by email
            print(f"Attempting to link existing {table} records to users by email...")
            cursor.execute(f'''
                UPDATE {table}
                SET user_id = (
                    SELECT id FROM users WHERE users.email = {table}.email
                )
                WHERE user_id IS NULL
            ''')
            updated = cursor.rowcount

            if updated > 0:
                print(f"  [OK] Linked {updated} existing quote(s) to user accounts")
            else:
                print(f"  - No existing quotes matched to user accounts (this is normal if quotes were submitted anonymously)")

            conn.commit()
            print(f"[OK] Successfully added user_id to {table}")

        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print(f"[OK] {table}: user_id column already exists")
            else:
                print(f"[ERROR] Error updating {table}: {e}")
                conn.rollback()
                raise

    # Create index on user_id for faster queries
    print("\nCreating indexes on user_id columns...")
    for table in tables_to_update:
        try:
            cursor.execute(f'''
                CREATE INDEX IF NOT EXISTS idx_{table}_user_id
                ON {table}(user_id)
            ''')
            print(f"[OK] Created index on {table}.user_id")
        except sqlite3.Error as e:
            print(f"Warning: Could not create index on {table}.user_id: {e}")

    conn.commit()
    conn.close()

    print("\n[SUCCESS] Migration completed successfully!")
    print("\nNext steps:")
    print("1. Update quote submission routes to save user_id")
    print("2. Update get_user_quotes() to query by user_id")
    print("3. Add @login_required decorator to quote routes")

if __name__ == '__main__':
    # Default database path
    db_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'database',
        'signups.db'
    )

    # Allow custom path as command line argument
    if len(sys.argv) > 1:
        db_path = sys.argv[1]

    # Verify database exists
    if not os.path.exists(db_path):
        print(f"[ERROR] Database not found at {db_path}")
        print("Please check the path and try again.")
        sys.exit(1)

    # Backup reminder
    print("WARNING: Make sure you have a backup of your database before proceeding!")
    print(f"Database: {db_path}\n")

    response = input("Continue with migration? (yes/no): ")
    if response.lower() != 'yes':
        print("Migration cancelled.")
        sys.exit(0)

    try:
        add_user_id_to_quotes(db_path)
    except Exception as e:
        print(f"\n[ERROR] Migration failed: {e}")
        sys.exit(1)
