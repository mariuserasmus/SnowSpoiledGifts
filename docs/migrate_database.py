#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database migration script to add unsubscribe functionality to existing signups table.

This script adds the following columns to the signups table:
- unsubscribe_token (TEXT UNIQUE) - Secure token for unsubscribe links
- is_active (INTEGER DEFAULT 1) - Subscription status (1 = active, 0 = unsubscribed)

It will also generate unique unsubscribe tokens for all existing signups.
"""

import sqlite3
import secrets
import os
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Database path
DATABASE_PATH = os.getenv('DATABASE_PATH', 'database/signups.db')

def migrate_database():
    """Run database migration to add new columns"""

    print(f"Starting database migration for: {DATABASE_PATH}")

    # Check if database exists
    if not os.path.exists(DATABASE_PATH):
        print(f"Error: Database file not found at {DATABASE_PATH}")
        return False

    try:
        # Connect to database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Check if columns already exist
        cursor.execute("PRAGMA table_info(signups)")
        columns = [column[1] for column in cursor.fetchall()]

        print(f"Current columns: {columns}")

        # Add unsubscribe_token column if it doesn't exist
        if 'unsubscribe_token' not in columns:
            print("Adding 'unsubscribe_token' column...")
            cursor.execute('''
                ALTER TABLE signups
                ADD COLUMN unsubscribe_token TEXT
            ''')
            print("✓ 'unsubscribe_token' column added")
        else:
            print("✓ 'unsubscribe_token' column already exists")

        # Add is_active column if it doesn't exist
        if 'is_active' not in columns:
            print("Adding 'is_active' column...")
            cursor.execute('''
                ALTER TABLE signups
                ADD COLUMN is_active INTEGER DEFAULT 1
            ''')
            print("✓ 'is_active' column added")
        else:
            print("✓ 'is_active' column already exists")

        # Generate unique tokens for existing signups that don't have them
        cursor.execute('''
            SELECT id, unsubscribe_token FROM signups
            WHERE unsubscribe_token IS NULL OR unsubscribe_token = ''
        ''')

        signups_without_tokens = cursor.fetchall()

        if signups_without_tokens:
            print(f"\nGenerating unique tokens for {len(signups_without_tokens)} existing signups...")

            for signup_id, _ in signups_without_tokens:
                # Generate unique token
                token = secrets.token_urlsafe(32)

                # Make sure token is unique
                while True:
                    cursor.execute('SELECT id FROM signups WHERE unsubscribe_token = ?', (token,))
                    if cursor.fetchone() is None:
                        break
                    token = secrets.token_urlsafe(32)

                # Update signup with token
                cursor.execute('''
                    UPDATE signups
                    SET unsubscribe_token = ?
                    WHERE id = ?
                ''', (token, signup_id))

                print(f"  ✓ Generated token for signup ID {signup_id}")
        else:
            print("\n✓ All signups already have unsubscribe tokens")

        # Set is_active to 1 for all existing signups if NULL
        cursor.execute('''
            UPDATE signups
            SET is_active = 1
            WHERE is_active IS NULL
        ''')

        rows_updated = cursor.rowcount
        if rows_updated > 0:
            print(f"✓ Set {rows_updated} existing signups to active status")

        # Commit changes
        conn.commit()

        # Verify the migration
        cursor.execute("PRAGMA table_info(signups)")
        new_columns = [column[1] for column in cursor.fetchall()]

        print(f"\n✓ Migration complete!")
        print(f"✓ New columns: {new_columns}")

        # Show summary
        cursor.execute('SELECT COUNT(*) FROM signups')
        total_signups = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM signups WHERE is_active = 1')
        active_signups = cursor.fetchone()[0]

        print(f"\n📊 Database Summary:")
        print(f"   Total signups: {total_signups}")
        print(f"   Active signups: {active_signups}")
        print(f"   Unsubscribed: {total_signups - active_signups}")

        conn.close()
        return True

    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        return False

if __name__ == '__main__':
    print("=" * 70)
    print("Database Migration Script - Adding Unsubscribe Functionality")
    print("=" * 70)
    print()

    success = migrate_database()

    print()
    print("=" * 70)
    if success:
        print("✓ Migration completed successfully!")
        print("You can now start the application.")
    else:
        print("❌ Migration failed. Please check the errors above.")
    print("=" * 70)
