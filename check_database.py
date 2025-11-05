#!/usr/bin/env python3
"""
Check database schema and provide diagnostics
"""

import sqlite3
import sys
import os

def check_database(db_path='database/ssg.db'):
    """Check database schema and provide diagnostics"""
    try:
        # Check if database file exists
        if not os.path.exists(db_path):
            print(f"[ERROR] Database file does not exist: {db_path}")
            print("\nThe database file is missing. This could mean:")
            print("1. The path is wrong")
            print("2. The database hasn't been created yet")
            print("3. The app hasn't been run/initialized")
            return False

        print(f"Database file exists: {db_path}")
        print(f"File size: {os.path.getsize(db_path)} bytes\n")

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # List all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row['name'] for row in cursor.fetchall()]

        print(f"=== Database Tables ({len(tables)}) ===")
        if tables:
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                count = cursor.fetchone()['count']
                print(f"  - {table} ({count} rows)")
        else:
            print("  [WARNING] No tables found!")

        # Check for expected tables
        print("\n=== Expected Tables Check ===")
        expected_tables = [
            'cutter_categories',
            'cutter_types',
            'cutter_items',
            'cutter_item_photos',
            'cart_items',
            'users',
            'orders',
            'order_items',
            'candles_soaps_categories',
            'candles_soaps_products'
        ]

        for table in expected_tables:
            if table in tables:
                print(f"  [OK] {table}")
            else:
                print(f"  [MISSING] {table}")

        # Check cart_items schema if it exists
        if 'cart_items' in tables:
            print("\n=== cart_items Schema ===")
            cursor.execute("PRAGMA table_info(cart_items)")
            columns = cursor.fetchall()
            for col in columns:
                print(f"  {col['name']}: {col['type']}")

        # Check cutter_categories schema if it exists
        if 'cutter_categories' in tables:
            print("\n=== cutter_categories Schema ===")
            cursor.execute("PRAGMA table_info(cutter_categories)")
            columns = cursor.fetchall()
            for col in columns:
                print(f"  {col['name']}: {col['type']}")

            # Check for Custom Quotes category
            cursor.execute("SELECT * FROM cutter_categories WHERE name = 'Custom Quotes'")
            custom_quotes = cursor.fetchone()
            if custom_quotes:
                print(f"\n[FOUND] Custom Quotes category:")
                print(f"  ID: {custom_quotes['id']}")
                if 'is_public' in [col['name'] for col in columns]:
                    print(f"  is_public: {custom_quotes['is_public']}")
                else:
                    print(f"  is_public: [COLUMN MISSING]")

        conn.close()
        return True

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'database/ssg.db'
    print(f"Checking database: {db_path}\n")
    check_database(db_path)
