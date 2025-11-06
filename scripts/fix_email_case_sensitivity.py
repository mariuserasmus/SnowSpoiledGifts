#!/usr/bin/env python3
"""
Database Migration Script: Fix Email Case Sensitivity Issue

This script:
1. Converts all user emails to lowercase in the database
2. Detects duplicate emails (case-insensitive duplicates)
3. Reports conflicts that need manual resolution
4. Creates a backup before making changes

Usage:
    python scripts/fix_email_case_sensitivity.py [--dry-run] [--backup]

Options:
    --dry-run    Show what would be changed without making changes
    --backup     Create a backup of the database before making changes
"""

import sys
import os
import shutil
import argparse
from datetime import datetime
from collections import defaultdict

# Add parent directory to path so we can import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database import Database


def backup_database(db_path):
    """Create a backup of the database"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{db_path}.backup_{timestamp}"

    try:
        shutil.copy2(db_path, backup_path)
        print(f"[OK] Database backed up to: {backup_path}")
        return True, backup_path
    except Exception as e:
        print(f"[ERROR] Failed to create backup: {str(e)}")
        return False, None


def analyze_email_duplicates(db):
    """Analyze the database for case-insensitive email duplicates"""
    conn = db.get_connection()
    cursor = conn.cursor()

    try:
        # Get all users
        cursor.execute('SELECT id, email, name, created_date, is_active FROM users ORDER BY created_date')
        users = cursor.fetchall()

        # Group users by lowercase email
        email_groups = defaultdict(list)
        for user in users:
            email_lower = user['email'].lower()
            email_groups[email_lower].append({
                'id': user['id'],
                'email': user['email'],
                'name': user['name'],
                'created_date': user['created_date'],
                'is_active': user['is_active']
            })

        # Find duplicates
        duplicates = {email: users_list for email, users_list in email_groups.items() if len(users_list) > 1}

        conn.close()
        return duplicates

    except Exception as e:
        conn.close()
        print(f"[ERROR] Failed to analyze duplicates: {str(e)}")
        return {}


def report_duplicates(duplicates):
    """Generate a detailed report of duplicate users"""
    if not duplicates:
        print("\n[OK] No duplicate emails found!")
        return

    print(f"\n[WARNING] Found {len(duplicates)} case-insensitive duplicate email(s):")
    print("=" * 80)

    for email_lower, users_list in duplicates.items():
        print(f"\nEmail (lowercase): {email_lower}")
        print("-" * 80)

        for i, user in enumerate(users_list, 1):
            status = "ACTIVE" if user['is_active'] else "INACTIVE"
            print(f"  {i}. User ID: {user['id']}")
            print(f"     Email: {user['email']}")
            print(f"     Name: {user['name']}")
            print(f"     Created: {user['created_date']}")
            print(f"     Status: {status}")
            print()

    print("=" * 80)
    print("\nACTION REQUIRED:")
    print("These duplicate users need manual resolution. Options:")
    print("1. Keep the oldest account and merge/delete newer ones")
    print("2. Keep the most active account and delete others")
    print("3. Contact users to determine which account to keep")
    print("\nAfter resolving duplicates, run this script again to normalize emails.")


def normalize_emails(db, dry_run=True):
    """Convert all emails to lowercase"""
    conn = db.get_connection()
    cursor = conn.cursor()

    try:
        # Get all users with non-lowercase emails
        cursor.execute('SELECT id, email FROM users')
        users = cursor.fetchall()

        updates_needed = []
        for user in users:
            email = user['email']
            email_lower = email.lower()

            if email != email_lower:
                updates_needed.append({
                    'id': user['id'],
                    'old_email': email,
                    'new_email': email_lower
                })

        if not updates_needed:
            print("\n[OK] All emails are already lowercase!")
            conn.close()
            return True

        print(f"\n[INFO] Found {len(updates_needed)} email(s) that need normalization:")
        print("-" * 80)

        for update in updates_needed:
            print(f"  User ID {update['id']}: {update['old_email']} -> {update['new_email']}")

        if dry_run:
            print("\n[DRY RUN] No changes made. Remove --dry-run to apply changes.")
            conn.close()
            return True

        # Apply updates
        print("\n[INFO] Applying updates...")
        for update in updates_needed:
            cursor.execute(
                'UPDATE users SET email = ? WHERE id = ?',
                (update['new_email'], update['id'])
            )

        conn.commit()
        print(f"[OK] Successfully normalized {len(updates_needed)} email(s)!")
        conn.close()
        return True

    except Exception as e:
        conn.rollback()
        conn.close()
        print(f"[ERROR] Failed to normalize emails: {str(e)}")
        return False


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Fix email case sensitivity in user database')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without applying them')
    parser.add_argument('--backup', action='store_true', help='Create database backup before changes')
    parser.add_argument('--db-path', default='database/signups.db', help='Path to database file')

    args = parser.parse_args()

    db_path = os.path.abspath(args.db_path)

    if not os.path.exists(db_path):
        print(f"[ERROR] Database not found: {db_path}")
        return 1

    print("=" * 80)
    print("EMAIL CASE SENSITIVITY FIX - Database Migration Script")
    print("=" * 80)
    print(f"Database: {db_path}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print("=" * 80)

    # Create database instance
    db = Database(db_path)

    # Step 1: Analyze for duplicates
    print("\nStep 1: Analyzing for duplicate emails...")
    duplicates = analyze_email_duplicates(db)

    if duplicates:
        report_duplicates(duplicates)
        print("\n[ERROR] Cannot proceed with normalization until duplicates are resolved.")
        print("[INFO] Please manually resolve the duplicate users first.")
        return 1

    # Step 2: Create backup if requested
    if args.backup and not args.dry_run:
        print("\nStep 2: Creating database backup...")
        success, backup_path = backup_database(db_path)
        if not success:
            print("[ERROR] Backup failed. Aborting to prevent data loss.")
            return 1

    # Step 3: Normalize emails
    print("\nStep 3: Normalizing email addresses to lowercase...")
    success = normalize_emails(db, dry_run=args.dry_run)

    if success and not args.dry_run:
        print("\n" + "=" * 80)
        print("[SUCCESS] Email normalization completed successfully!")
        print("=" * 80)
        print("\nNext steps:")
        print("1. Test user login with various email casings")
        print("2. Verify quote conversion works correctly")
        print("3. Monitor for any new duplicate creation attempts")
        return 0
    elif success and args.dry_run:
        print("\n" + "=" * 80)
        print("[DRY RUN COMPLETE] Run without --dry-run to apply changes")
        print("=" * 80)
        return 0
    else:
        print("\n[ERROR] Email normalization failed!")
        return 1


if __name__ == '__main__':
    sys.exit(main())
