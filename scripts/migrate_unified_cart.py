"""
Database Migration Script: Unified Cart System
===============================================

This script migrates from two separate cart tables to a single unified cart_items table.

BEFORE:
- cart_items (for cutter products)
- candles_soaps_cart_items (for candles & soaps)

AFTER:
- cart_items (unified - handles all product types)

The unified table includes:
- product_type field: 'cutter_item' or 'candles_soap'
- product_id field: references the actual product in respective table
"""

import sqlite3
import os
from datetime import datetime

# Get database path relative to script location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATABASE_PATH = os.path.join(PROJECT_ROOT, 'database', 'signups.db')

def backup_database():
    """Create a backup of the database before migration"""
    backup_path = DATABASE_PATH.replace('.db', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')

    print(f"Creating backup at: {backup_path}")

    # Copy the database file
    import shutil
    shutil.copy2(DATABASE_PATH, backup_path)

    print(f"Backup created successfully: {backup_path}")
    return backup_path

def get_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def check_table_exists(cursor, table_name):
    """Check if a table exists"""
    cursor.execute('''
        SELECT name FROM sqlite_master
        WHERE type='table' AND name=?
    ''', (table_name,))
    return cursor.fetchone() is not None

def get_table_columns(cursor, table_name):
    """Get list of column names for a table"""
    cursor.execute(f'PRAGMA table_info({table_name})')
    return [col[1] for col in cursor.fetchall()]

def migrate_to_unified_cart():
    """Main migration function"""

    print("\n" + "="*60)
    print("UNIFIED CART MIGRATION SCRIPT")
    print("="*60 + "\n")

    # Create backup first
    backup_path = backup_database()

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Step 1: Check current state
        print("\n[STEP 1] Analyzing current database structure...")

        has_cart_items = check_table_exists(cursor, 'cart_items')
        has_candles_soaps_cart = check_table_exists(cursor, 'candles_soaps_cart_items')

        print(f"  - cart_items table exists: {has_cart_items}")
        print(f"  - candles_soaps_cart_items table exists: {has_candles_soaps_cart}")

        if not has_cart_items and not has_candles_soaps_cart:
            print("\n  WARNING: No cart tables found. Nothing to migrate.")
            return

        # Step 2: Check if migration already done
        if has_cart_items:
            columns = get_table_columns(cursor, 'cart_items')
            if 'product_type' in columns and 'product_id' in columns:
                print("\n  INFO: Unified cart schema already exists!")
                print("  The database appears to be already migrated.")
                print("\n  Skipping migration - already completed.")
                conn.close()
                return

        # Step 3: Rename old cart_items to cart_items_old
        print("\n[STEP 2] Preserving existing cart_items table...")

        if has_cart_items:
            # Check if there's data in the old cart
            cursor.execute('SELECT COUNT(*) as count FROM cart_items')
            old_cart_count = cursor.fetchone()['count']
            print(f"  - Found {old_cart_count} items in existing cart_items table")

            # Drop the old backup table if it exists
            cursor.execute('DROP TABLE IF EXISTS cart_items_old')

            # Rename existing cart_items to cart_items_old
            cursor.execute('ALTER TABLE cart_items RENAME TO cart_items_old')
            print("  - Renamed cart_items to cart_items_old")

        # Step 4: Create new unified cart_items table
        print("\n[STEP 3] Creating unified cart_items table...")

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cart_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                user_id INTEGER,
                product_type TEXT NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER DEFAULT 1,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        print("  - Created unified cart_items table with product_type and product_id fields")

        # Step 5: Create indexes for performance
        print("\n[STEP 4] Creating indexes...")

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_cart_items_user_id
            ON cart_items(user_id)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_cart_items_session_id
            ON cart_items(session_id)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_cart_items_product_type
            ON cart_items(product_type)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_cart_items_lookup
            ON cart_items(user_id, product_type, product_id)
        ''')

        print("  - Created indexes for user_id, session_id, product_type, and composite lookup")

        # Step 6: Migrate data from cart_items_old (cutter items)
        print("\n[STEP 5] Migrating data from old cart_items...")

        if has_cart_items:
            cursor.execute('''
                INSERT INTO cart_items (session_id, user_id, product_type, product_id, quantity, added_date)
                SELECT
                    session_id,
                    user_id,
                    'cutter_item' as product_type,
                    item_id as product_id,
                    quantity,
                    added_date
                FROM cart_items_old
            ''')

            migrated_cutter_count = cursor.rowcount
            print(f"  - Migrated {migrated_cutter_count} cutter items with product_type='cutter_item'")
        else:
            print("  - No old cart_items table to migrate")

        # Step 7: Migrate data from candles_soaps_cart_items
        print("\n[STEP 6] Migrating data from candles_soaps_cart_items...")

        if has_candles_soaps_cart:
            cursor.execute('SELECT COUNT(*) as count FROM candles_soaps_cart_items')
            candles_count = cursor.fetchone()['count']
            print(f"  - Found {candles_count} items in candles_soaps_cart_items")

            cursor.execute('''
                INSERT INTO cart_items (session_id, user_id, product_type, product_id, quantity, added_date)
                SELECT
                    session_id,
                    user_id,
                    'candles_soap' as product_type,
                    product_id,
                    quantity,
                    added_date
                FROM candles_soaps_cart_items
            ''')

            migrated_candles_count = cursor.rowcount
            print(f"  - Migrated {migrated_candles_count} candles/soaps items with product_type='candles_soap'")
        else:
            print("  - No candles_soaps_cart_items table found")

        # Step 8: Verify migration
        print("\n[STEP 7] Verifying migration...")

        cursor.execute('SELECT COUNT(*) as total FROM cart_items')
        total_unified = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) as cutter_count FROM cart_items WHERE product_type='cutter_item'")
        cutter_unified = cursor.fetchone()['cutter_count']

        cursor.execute("SELECT COUNT(*) as candles_count FROM cart_items WHERE product_type='candles_soap'")
        candles_unified = cursor.fetchone()['candles_count']

        print(f"  - Total items in unified cart: {total_unified}")
        print(f"  - Cutter items: {cutter_unified}")
        print(f"  - Candles/Soaps items: {candles_unified}")

        # Step 9: Drop old tables
        print("\n[STEP 8] Cleaning up old tables...")

        cursor.execute('DROP TABLE IF EXISTS cart_items_old')
        cursor.execute('DROP TABLE IF EXISTS candles_soaps_cart_items')
        print("  - Dropped cart_items_old")
        print("  - Dropped candles_soaps_cart_items")

        # Commit all changes
        conn.commit()

        print("\n" + "="*60)
        print("MIGRATION COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"\nBackup saved at: {backup_path}")
        print("\nNext steps:")
        print("1. Update database.py with new unified cart functions")
        print("2. Update app.py to use the new unified cart functions")
        print("3. Test thoroughly before deploying to production")

    except Exception as e:
        conn.rollback()
        print(f"\n\nERROR during migration: {str(e)}")
        print(f"\nDatabase has been rolled back. Your backup is at: {backup_path}")
        import traceback
        traceback.print_exc()

    finally:
        conn.close()

if __name__ == '__main__':
    # Auto-execute migration
    print("\nWARNING: This script will modify your database structure.")
    print("A backup will be created automatically before any changes.")
    print(f"\nDatabase: {DATABASE_PATH}")
    print("\nPROCEEDING WITH MIGRATION...\n")

    migrate_to_unified_cart()
