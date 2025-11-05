#!/usr/bin/env python3
"""
Script to manually fix Custom Quotes visibility issue.
This ensures the "Custom Quotes" category is marked as non-public.
"""

import sqlite3
import sys

def fix_custom_quotes_visibility(db_path='database/ssg.db'):
    """Mark Custom Quotes category as non-public"""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        print("Checking Custom Quotes category...")

        # Check if Custom Quotes category exists
        cursor.execute("SELECT id, name, is_public FROM cutter_categories WHERE name = 'Custom Quotes'")
        category = cursor.fetchone()

        if category:
            print(f"Found category: {category['name']} (ID: {category['id']})")
            print(f"Current is_public value: {category['is_public']}")

            if category['is_public'] != 0:
                # Update to non-public
                cursor.execute("UPDATE cutter_categories SET is_public = 0 WHERE id = ?", (category['id'],))
                conn.commit()
                print(f"[SUCCESS] Updated 'Custom Quotes' category to is_public=0")

                # Show items in this category
                cursor.execute("""
                    SELECT id, item_number, name
                    FROM cutter_items
                    WHERE category_id = ? AND is_active = 1
                """, (category['id'],))
                items = cursor.fetchall()

                if items:
                    print(f"\nItems in Custom Quotes category (will now be hidden from shop):")
                    for item in items:
                        print(f"  - {item['item_number']}: {item['name']}")
                else:
                    print("\nNo items in Custom Quotes category.")
            else:
                print("[OK] Category is already marked as non-public (is_public=0)")
        else:
            print("[WARNING] 'Custom Quotes' category not found in database")
            print("This is normal if no quotes have been converted yet.")

        conn.close()
        return True

    except Exception as e:
        print(f"[ERROR] {e}")
        return False

if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'database/ssg.db'
    print(f"Database: {db_path}\n")

    success = fix_custom_quotes_visibility(db_path)

    if success:
        print("\n[SUCCESS] Fix completed successfully!")
        print("\nNext steps:")
        print("1. Refresh your 3D Printing shop page")
        print("2. The Custom Quotes items should now be hidden")
        print("3. They will still appear in admin carts and user carts")
    else:
        print("\n[FAILED] Fix failed. Please check the error message above.")
        sys.exit(1)
