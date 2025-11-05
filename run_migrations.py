#!/usr/bin/env python3
"""
Manual migration script to update database schema.
This runs all necessary migrations for the latest version.
"""

import sqlite3
import sys

def run_migrations(db_path='database/ssg.db'):
    """Run all pending database migrations"""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        print("=== Starting Database Migrations ===\n")

        # Check current schema
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row['name'] for row in cursor.fetchall()]
        print(f"Current tables: {', '.join(tables)}\n")

        # Migration 1: Add is_public to cutter_categories
        print("Migration 1: Adding is_public column to cutter_categories...")
        if 'cutter_categories' in tables:
            cursor.execute("PRAGMA table_info(cutter_categories)")
            columns = [column[1] for column in cursor.fetchall()]

            if 'is_public' not in columns:
                cursor.execute('ALTER TABLE cutter_categories ADD COLUMN is_public INTEGER DEFAULT 1')
                conn.commit()
                print("  [SUCCESS] Added is_public column")
            else:
                print("  [SKIP] is_public column already exists")
        else:
            print("  [SKIP] cutter_categories table doesn't exist")

        # Migration 2: Update cart_items for unified cart
        print("\nMigration 2: Updating cart_items table for unified cart...")
        if 'cart_items' in tables:
            cursor.execute("PRAGMA table_info(cart_items)")
            columns = [column[1] for column in cursor.fetchall()]

            changes_made = False

            if 'product_type' not in columns:
                cursor.execute('ALTER TABLE cart_items ADD COLUMN product_type TEXT DEFAULT "cutter_item"')
                print("  [SUCCESS] Added product_type column")
                changes_made = True
            else:
                print("  [SKIP] product_type column already exists")

            if 'product_id' not in columns and 'item_id' in columns:
                cursor.execute('ALTER TABLE cart_items ADD COLUMN product_id INTEGER')
                cursor.execute('UPDATE cart_items SET product_id = item_id WHERE product_id IS NULL')
                print("  [SUCCESS] Added product_id column and migrated data from item_id")
                changes_made = True
            elif 'product_id' in columns:
                print("  [SKIP] product_id column already exists")
            else:
                print("  [WARNING] Neither product_id nor item_id found")

            if changes_made:
                conn.commit()
        else:
            print("  [SKIP] cart_items table doesn't exist")

        # Migration 3: Mark Custom Quotes as non-public
        print("\nMigration 3: Marking Custom Quotes category as non-public...")
        if 'cutter_categories' in tables:
            cursor.execute("SELECT id, name, is_public FROM cutter_categories WHERE name = 'Custom Quotes'")
            category = cursor.fetchone()

            if category:
                if category['is_public'] != 0:
                    cursor.execute("UPDATE cutter_categories SET is_public = 0 WHERE id = ?", (category['id'],))
                    conn.commit()
                    print(f"  [SUCCESS] Updated 'Custom Quotes' to is_public=0")
                else:
                    print("  [SKIP] 'Custom Quotes' already marked as non-public")
            else:
                print("  [SKIP] 'Custom Quotes' category doesn't exist yet")
        else:
            print("  [SKIP] cutter_categories table doesn't exist")

        # Summary
        print("\n=== Migration Summary ===")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables_after = [row['name'] for row in cursor.fetchall()]
        print(f"Tables after migration: {len(tables_after)}")

        # Check specific tables
        if 'cutter_categories' in tables_after:
            cursor.execute("PRAGMA table_info(cutter_categories)")
            cols = [column[1] for column in cursor.fetchall()]
            print(f"\ncutter_categories columns: {', '.join(cols)}")
            print(f"  has is_public: {'YES' if 'is_public' in cols else 'NO'}")

        if 'cart_items' in tables_after:
            cursor.execute("PRAGMA table_info(cart_items)")
            cols = [column[1] for column in cursor.fetchall()]
            print(f"\ncart_items columns: {', '.join(cols)}")
            print(f"  has product_type: {'YES' if 'product_type' in cols else 'NO'}")
            print(f"  has product_id: {'YES' if 'product_id' in cols else 'NO'}")

        conn.close()
        return True

    except Exception as e:
        print(f"\n[ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'database/ssg.db'
    print(f"Database: {db_path}\n")

    success = run_migrations(db_path)

    if success:
        print("\n[SUCCESS] All migrations completed!")
        print("\nNext steps:")
        print("1. Restart your Flask application")
        print("2. Verify the 3D Printing shop page")
        print("3. Custom quote items should be hidden")
    else:
        print("\n[FAILED] Migrations failed. Check errors above.")
        sys.exit(1)
