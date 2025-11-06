"""
Fix Hybrid Cart Schema
=======================

This script fixes a cart_items table that has BOTH old and new columns:
- Old: item_id (NOT NULL)
- New: product_type, product_id

The migration will:
1. Backup the database
2. Remove the NOT NULL constraint from item_id (rebuild table)
3. Migrate any data from item_id to product_id
4. Remove the item_id column entirely

This completes the unified cart migration properly.
"""

import sqlite3
import os
from datetime import datetime
import shutil

# Get database path relative to script location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATABASE_PATH = os.path.join(PROJECT_ROOT, 'database', 'signups.db')

def backup_database():
    """Create a backup of the database before migration"""
    backup_path = DATABASE_PATH.replace('.db', f'_backup_hybrid_fix_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
    print(f"Creating backup at: {backup_path}")
    shutil.copy2(DATABASE_PATH, backup_path)
    print(f"Backup created successfully: {backup_path}")
    return backup_path

def fix_hybrid_cart_schema():
    """Fix the hybrid cart schema"""

    print("\n" + "="*60)
    print("HYBRID CART SCHEMA FIX")
    print("="*60 + "\n")

    # Create backup first
    backup_path = backup_database()

    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        print("\n[STEP 1] Analyzing current schema...")
        cursor.execute('PRAGMA table_info(cart_items)')
        columns = {col[1]: col for col in cursor.fetchall()}

        print(f"  Current columns: {', '.join(columns.keys())}")

        if 'item_id' not in columns:
            print("\n  ✓ item_id column doesn't exist - schema is already clean!")
            conn.close()
            return

        if 'product_id' not in columns or 'product_type' not in columns:
            print("\n  ✗ Missing unified schema columns (product_id/product_type)")
            print("    Please run migrate_unified_cart.py first")
            conn.close()
            return

        print("  ✓ Found hybrid schema - has both item_id and product_id/product_type")

        # Check for data that needs migration
        print("\n[STEP 2] Checking for data to migrate...")
        cursor.execute('''
            SELECT COUNT(*) as count
            FROM cart_items
            WHERE item_id IS NOT NULL AND product_id IS NULL
        ''')
        unmigrated_count = cursor.fetchone()['count']
        print(f"  Found {unmigrated_count} rows with item_id but no product_id")

        # Migrate data from item_id to product_id if needed
        if unmigrated_count > 0:
            print("\n[STEP 3] Migrating data from item_id to product_id...")
            cursor.execute('''
                UPDATE cart_items
                SET product_id = item_id,
                    product_type = 'cutter_item'
                WHERE item_id IS NOT NULL AND product_id IS NULL
            ''')
            print(f"  ✓ Migrated {cursor.rowcount} rows")

        # Recreate table without item_id column
        print("\n[STEP 4] Recreating table without item_id column...")

        # Get all current data
        cursor.execute('SELECT * FROM cart_items')
        all_data = cursor.fetchall()
        print(f"  Found {len(all_data)} total cart items")

        # Drop old table
        cursor.execute('DROP TABLE cart_items')
        print("  ✓ Dropped old cart_items table")

        # Create new table without item_id
        cursor.execute('''
            CREATE TABLE cart_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                user_id INTEGER,
                product_type TEXT NOT NULL DEFAULT 'cutter_item',
                product_id INTEGER NOT NULL,
                quantity INTEGER DEFAULT 1,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        print("  ✓ Created new cart_items table")

        # Recreate indexes
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
        print("  ✓ Created indexes")

        # Insert data back (only unified schema columns)
        print("\n[STEP 5] Restoring cart data...")
        for row in all_data:
            # Use product_id if available, otherwise use item_id
            final_product_id = row['product_id'] if row['product_id'] else row['item_id']
            final_product_type = row['product_type'] if row['product_type'] else 'cutter_item'

            cursor.execute('''
                INSERT INTO cart_items
                (id, session_id, user_id, product_type, product_id, quantity, added_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['id'],
                row['session_id'],
                row['user_id'],
                final_product_type,
                final_product_id,
                row['quantity'],
                row['added_date']
            ))

        print(f"  ✓ Restored {len(all_data)} cart items")

        # Verify
        print("\n[STEP 6] Verifying new schema...")
        cursor.execute('PRAGMA table_info(cart_items)')
        new_columns = [col[1] for col in cursor.fetchall()]
        print(f"  New columns: {', '.join(new_columns)}")

        if 'item_id' in new_columns:
            raise Exception("ERROR: item_id column still exists after migration!")

        if 'product_id' not in new_columns or 'product_type' not in new_columns:
            raise Exception("ERROR: product_id or product_type missing after migration!")

        cursor.execute('SELECT COUNT(*) as count FROM cart_items')
        final_count = cursor.fetchone()['count']
        print(f"  ✓ Final cart item count: {final_count}")

        # Commit all changes
        conn.commit()

        print("\n" + "="*60)
        print("MIGRATION COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"\nBackup saved at: {backup_path}")
        print("\nCart schema is now fully migrated to unified schema.")
        print("The item_id column has been removed.")

    except Exception as e:
        conn.rollback()
        print(f"\n\n✗ ERROR during migration: {str(e)}")
        print(f"\nDatabase has been rolled back. Your backup is at: {backup_path}")
        import traceback
        traceback.print_exc()

    finally:
        conn.close()

if __name__ == '__main__':
    print("\nWARNING: This script will modify your database structure.")
    print("A backup will be created automatically before any changes.")
    print(f"\nDatabase: {DATABASE_PATH}")
    print("\nPROCEEDING WITH HYBRID SCHEMA FIX...\n")

    fix_hybrid_cart_schema()
