"""
Migration script to add quote messaging system to Snow Spoiled Gifts database.

This script:
1. Creates the quote_messages table for storing admin-customer communications
2. Adds pricing fields to all quote tables (quote_requests, cake_topper_requests, print_service_requests)
3. Can be run multiple times safely (idempotent)

Author: SQLite Database Specialist
Date: 2025-11-14
"""

import sqlite3
import os
from datetime import datetime

def get_db_path():
    """Get the database path relative to this script"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, '..', 'database', 'signups.db')
    return os.path.normpath(db_path)

def table_exists(cursor, table_name):
    """Check if a table exists in the database"""
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name=?
    """, (table_name,))
    return cursor.fetchone() is not None

def column_exists(cursor, table_name, column_name):
    """Check if a column exists in a table"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [col[1] for col in cursor.fetchall()]
    return column_name in columns

def create_quote_messages_table(cursor):
    """Create the quote_messages table if it doesn't exist"""
    if table_exists(cursor, 'quote_messages'):
        print("  [SKIP] quote_messages table already exists")
        return False

    cursor.execute('''
        CREATE TABLE quote_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quote_type TEXT NOT NULL,
            quote_id INTEGER NOT NULL,
            message_text TEXT NOT NULL,
            sender TEXT NOT NULL DEFAULT 'admin',
            quoted_price_per_item REAL,
            quoted_total REAL,
            attached_image TEXT,
            message_type TEXT DEFAULT 'admin_message',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (quote_id) REFERENCES quote_requests(id)
        )
    ''')

    # Create indexes for efficient queries
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_quote_messages_quote
        ON quote_messages(quote_type, quote_id)
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_quote_messages_created
        ON quote_messages(created_at)
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_quote_messages_type
        ON quote_messages(message_type)
    ''')

    print("  [OK] Created quote_messages table with indexes")
    return True

def add_pricing_columns_to_quote_table(cursor, table_name):
    """Add pricing columns to a quote table"""
    columns_added = []

    # Check and add quoted_price_per_item
    if not column_exists(cursor, table_name, 'quoted_price_per_item'):
        cursor.execute(f'''
            ALTER TABLE {table_name}
            ADD COLUMN quoted_price_per_item REAL
        ''')
        columns_added.append('quoted_price_per_item')

    # Check and add quoted_total
    if not column_exists(cursor, table_name, 'quoted_total'):
        cursor.execute(f'''
            ALTER TABLE {table_name}
            ADD COLUMN quoted_total REAL
        ''')
        columns_added.append('quoted_total')

    # Check and add quoted_date
    if not column_exists(cursor, table_name, 'quoted_date'):
        cursor.execute(f'''
            ALTER TABLE {table_name}
            ADD COLUMN quoted_date TIMESTAMP
        ''')
        columns_added.append('quoted_date')

    if columns_added:
        print(f"  [OK] Added columns to {table_name}: {', '.join(columns_added)}")
        return True
    else:
        print(f"  [SKIP] All pricing columns already exist in {table_name}")
        return False

def run_migration():
    """Execute the migration"""
    db_path = get_db_path()

    if not os.path.exists(db_path):
        print(f"ERROR: Database not found at {db_path}")
        return False

    print(f"Running migration on: {db_path}")
    print(f"Migration started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Step 1: Create quote_messages table
        print("\n[1/4] Creating quote_messages table...")
        create_quote_messages_table(cursor)

        # Step 2: Add pricing columns to quote_requests
        print("\n[2/4] Adding pricing columns to quote_requests...")
        add_pricing_columns_to_quote_table(cursor, 'quote_requests')

        # Step 3: Add pricing columns to cake_topper_requests
        print("\n[3/4] Adding pricing columns to cake_topper_requests...")
        add_pricing_columns_to_quote_table(cursor, 'cake_topper_requests')

        # Step 4: Add pricing columns to print_service_requests
        print("\n[4/4] Adding pricing columns to print_service_requests...")
        add_pricing_columns_to_quote_table(cursor, 'print_service_requests')

        # Commit all changes
        conn.commit()

        print("\n" + "=" * 60)
        print("MIGRATION COMPLETED SUCCESSFULLY")
        print("=" * 60)

        # Verify the changes
        print("\n[VERIFICATION]")
        if table_exists(cursor, 'quote_messages'):
            cursor.execute("SELECT COUNT(*) FROM quote_messages")
            count = cursor.fetchone()[0]
            print(f"  quote_messages table: {count} messages")

        for table in ['quote_requests', 'cake_topper_requests', 'print_service_requests']:
            has_price = column_exists(cursor, table, 'quoted_price_per_item')
            has_total = column_exists(cursor, table, 'quoted_total')
            has_date = column_exists(cursor, table, 'quoted_date')
            status = "OK" if (has_price and has_total and has_date) else "MISSING COLUMNS"
            print(f"  {table}: {status}")

        return True

    except Exception as e:
        conn.rollback()
        print(f"\nERROR: Migration failed: {str(e)}")
        return False

    finally:
        conn.close()
        print(f"\nMigration ended at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    success = run_migration()
    exit(0 if success else 1)
