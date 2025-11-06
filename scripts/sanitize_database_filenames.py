"""
Sanitize Database Filenames
============================

This script updates all file references in the database to use sanitized filenames
(spaces replaced with underscores, special characters removed).

This is needed when files have been manually renamed on disk but database still
has the old filenames with spaces/special characters.

Affected tables:
- quote_requests.reference_images
- cake_topper_requests.reference_images
- print_service_requests.uploaded_files
"""

import sqlite3
import os
import re
from datetime import datetime
import shutil

# Get database path relative to script location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATABASE_PATH = os.path.join(PROJECT_ROOT, 'database', 'signups.db')


def sanitize_filename(filename):
    """
    Sanitize filename to match the sanitize_filename() function in app.py
    """
    if not filename:
        return filename

    # Split filename and extension
    name, ext = os.path.splitext(filename)

    # Replace spaces with underscores
    name = name.replace(' ', '_')

    # Remove or replace other problematic characters
    # Keep only alphanumeric, underscores, hyphens, and periods
    name = re.sub(r'[^\w\-.]', '_', name)

    # Remove consecutive underscores
    name = re.sub(r'_+', '_', name)

    # Remove leading/trailing underscores
    name = name.strip('_')

    return name + ext


def backup_database():
    """Create a backup of the database before migration"""
    backup_path = DATABASE_PATH.replace('.db', f'_backup_filename_sanitize_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
    print(f"Creating backup at: {backup_path}")
    shutil.copy2(DATABASE_PATH, backup_path)
    print(f"Backup created successfully: {backup_path}")
    return backup_path


def sanitize_database_filenames():
    """Sanitize all filenames in the database"""

    print("\n" + "="*60)
    print("DATABASE FILENAME SANITIZATION SCRIPT")
    print("="*60 + "\n")

    # Create backup first
    backup_path = backup_database()

    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    total_updates = 0

    try:
        # Define tables and columns that contain filenames
        tables_to_update = [
            ('quote_requests', 'reference_images'),
            ('cake_topper_requests', 'reference_images'),
            ('print_service_requests', 'uploaded_files')
        ]

        for table_name, column_name in tables_to_update:
            print(f"\n[Processing {table_name}.{column_name}]")

            # Check if table exists
            cursor.execute('''
                SELECT name FROM sqlite_master
                WHERE type='table' AND name=?
            ''', (table_name,))

            if not cursor.fetchone():
                print(f"  ⊘ Table '{table_name}' doesn't exist, skipping...")
                continue

            # Check if column exists
            cursor.execute(f'PRAGMA table_info({table_name})')
            columns = [col[1] for col in cursor.fetchall()]

            if column_name not in columns:
                print(f"  ⊘ Column '{column_name}' doesn't exist in {table_name}, skipping...")
                continue

            # Get all rows with filenames
            cursor.execute(f'''
                SELECT id, {column_name}
                FROM {table_name}
                WHERE {column_name} IS NOT NULL AND {column_name} != ""
            ''')

            rows = cursor.fetchall()
            print(f"  Found {len(rows)} rows with filenames")

            updates_in_table = 0

            for row in rows:
                original_filenames = row[column_name]

                if not original_filenames:
                    continue

                # Filenames are comma-separated
                filenames = [f.strip() for f in original_filenames.split(',')]
                sanitized_filenames = [sanitize_filename(f) for f in filenames]

                # Check if any changes were made
                if filenames != sanitized_filenames:
                    new_value = ','.join(sanitized_filenames)

                    # Show what's being changed
                    print(f"\n  ID {row['id']}:")
                    print(f"    Before: {original_filenames}")
                    print(f"    After:  {new_value}")

                    # Update the database
                    cursor.execute(f'''
                        UPDATE {table_name}
                        SET {column_name} = ?
                        WHERE id = ?
                    ''', (new_value, row['id']))

                    updates_in_table += 1
                    total_updates += 1

            if updates_in_table > 0:
                print(f"\n  ✓ Updated {updates_in_table} rows in {table_name}")
            else:
                print(f"  ✓ No updates needed in {table_name}")

        # Commit all changes
        conn.commit()

        print("\n" + "="*60)
        if total_updates > 0:
            print(f"✓ SANITIZATION COMPLETED - {total_updates} ROWS UPDATED")
        else:
            print("✓ NO UPDATES NEEDED - ALL FILENAMES ALREADY CLEAN")
        print("="*60)
        print(f"\nBackup saved at: {backup_path}")

        if total_updates > 0:
            print("\nDatabase has been updated with sanitized filenames.")
            print("Filenames now match the sanitize_filename() function in app.py")
            print("\nNote: If you manually renamed files, make sure they match")
            print("the sanitized names shown above.")

    except Exception as e:
        conn.rollback()
        print(f"\n\n✗ ERROR during sanitization: {str(e)}")
        print(f"\nDatabase has been rolled back. Your backup is at: {backup_path}")
        import traceback
        traceback.print_exc()

    finally:
        conn.close()


if __name__ == '__main__':
    print("\nWARNING: This script will modify filename references in your database.")
    print("A backup will be created automatically before any changes.")
    print(f"\nDatabase: {DATABASE_PATH}")
    print("\nPROCEEDING WITH FILENAME SANITIZATION...\n")

    sanitize_database_filenames()
