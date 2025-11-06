#!/usr/bin/env python3
"""
Duplicate User Management Script

This script helps identify and resolve duplicate user accounts created
due to the email case sensitivity bug.

Features:
1. List all duplicate users (case-insensitive email matching)
2. Show detailed information about each duplicate
3. Merge duplicate accounts (orders, carts, quotes)
4. Delete duplicate accounts after merging

Usage:
    python scripts/manage_duplicate_users.py --list
    python scripts/manage_duplicate_users.py --merge <keep_id> <delete_id> [--dry-run]
    python scripts/manage_duplicate_users.py --email <email>

Options:
    --list              List all duplicate email accounts
    --email <email>     Show details for specific email
    --merge <keep> <delete>  Merge delete_id into keep_id, then delete
    --dry-run           Show what would happen without making changes
"""

import sys
import os
import argparse
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database import Database


def list_duplicates(db):
    """List all users with duplicate emails (case-insensitive)"""
    conn = db.get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            SELECT id, email, name, created_date, is_active, is_admin
            FROM users
            ORDER BY created_date
        ''')
        users = cursor.fetchall()

        # Group by lowercase email
        email_groups = defaultdict(list)
        for user in users:
            email_lower = user['email'].lower()
            email_groups[email_lower].append(dict(user))

        # Find duplicates
        duplicates = {email: users for email, users in email_groups.items() if len(users) > 1}

        conn.close()
        return duplicates

    except Exception as e:
        conn.close()
        print(f"[ERROR] {str(e)}")
        return {}


def get_user_details(db, user_id):
    """Get detailed information about a user including their data"""
    conn = db.get_connection()
    cursor = conn.cursor()

    try:
        # Get user info
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()

        if not user:
            conn.close()
            return None

        # Get order count
        cursor.execute('SELECT COUNT(*) as count FROM orders WHERE user_id = ?', (user_id,))
        order_count = cursor.fetchone()['count']

        # Get cart item count
        cursor.execute('SELECT COUNT(*) as count FROM cart_items WHERE user_id = ?', (user_id,))
        cart_count = cursor.fetchone()['count']

        # Get candles/soaps cart count
        cursor.execute('SELECT COUNT(*) as count FROM candles_soaps_cart WHERE user_id = ?', (user_id,))
        cs_cart_count = cursor.fetchone()['count']

        # Get quote counts
        cursor.execute('SELECT COUNT(*) as count FROM quote_requests WHERE email = ?', (user['email'],))
        quote_count = cursor.fetchone()['count']

        cursor.execute('SELECT COUNT(*) as count FROM cake_topper_requests WHERE email = ?', (user['email'],))
        cake_count = cursor.fetchone()['count']

        cursor.execute('SELECT COUNT(*) as count FROM print_service_requests WHERE email = ?', (user['email'],))
        print_count = cursor.fetchone()['count']

        conn.close()

        return {
            'user': dict(user),
            'orders': order_count,
            'cart_items': cart_count,
            'cs_cart_items': cs_cart_count,
            'quotes': quote_count + cake_count + print_count
        }

    except Exception as e:
        conn.close()
        print(f"[ERROR] {str(e)}")
        return None


def show_email_details(db, email):
    """Show details for all users with a specific email"""
    conn = db.get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            'SELECT id FROM users WHERE LOWER(email) = LOWER(?)',
            (email,)
        )
        users = cursor.fetchall()
        conn.close()

        if not users:
            print(f"[INFO] No users found with email: {email}")
            return

        print(f"\nFound {len(users)} user(s) with email: {email}")
        print("=" * 80)

        for user in users:
            details = get_user_details(db, user['id'])
            if details:
                print_user_details(details)
                print("-" * 80)

    except Exception as e:
        conn.close()
        print(f"[ERROR] {str(e)}")


def print_user_details(details):
    """Pretty print user details"""
    user = details['user']
    print(f"\nUser ID: {user['id']}")
    print(f"Email: {user['email']}")
    print(f"Name: {user['name']}")
    print(f"Phone: {user.get('phone', 'N/A')}")
    print(f"Created: {user['created_date']}")
    print(f"Active: {'Yes' if user['is_active'] else 'No'}")
    print(f"Admin: {'Yes' if user.get('is_admin', 0) else 'No'}")
    print(f"Verified: {'Yes' if user.get('email_verified', 0) else 'No'}")
    print(f"\nData:")
    print(f"  Orders: {details['orders']}")
    print(f"  Cart Items: {details['cart_items']}")
    print(f"  C&S Cart Items: {details['cs_cart_items']}")
    print(f"  Quotes: {details['quotes']}")


def merge_users(db, keep_id, delete_id, dry_run=True):
    """Merge delete_id into keep_id and optionally delete the duplicate"""
    conn = db.get_connection()
    cursor = conn.cursor()

    try:
        # Verify both users exist
        cursor.execute('SELECT id, email FROM users WHERE id IN (?, ?)', (keep_id, delete_id))
        users = cursor.fetchall()

        if len(users) != 2:
            print("[ERROR] One or both user IDs not found")
            conn.close()
            return False

        keep_user = next(u for u in users if u['id'] == keep_id)
        delete_user = next(u for u in users if u['id'] == delete_id)

        if keep_user['email'].lower() != delete_user['email'].lower():
            print(f"[ERROR] Users have different emails:")
            print(f"  Keep ({keep_id}): {keep_user['email']}")
            print(f"  Delete ({delete_id}): {delete_user['email']}")
            conn.close()
            return False

        print(f"\n{'[DRY RUN] ' if dry_run else ''}Merging user {delete_id} into {keep_id}")
        print("=" * 80)

        # Get details
        keep_details = get_user_details(db, keep_id)
        delete_details = get_user_details(db, delete_id)

        print("\nKEEP this account:")
        print_user_details(keep_details)

        print("\nDELETE this account:")
        print_user_details(delete_details)

        if dry_run:
            print("\n[DRY RUN] Would perform these operations:")
        else:
            print("\nPerforming merge operations:")

        operations = []

        # Migrate orders
        cursor.execute('SELECT COUNT(*) as count FROM orders WHERE user_id = ?', (delete_id,))
        order_count = cursor.fetchone()['count']
        if order_count > 0:
            operations.append(f"Migrate {order_count} order(s)")
            if not dry_run:
                cursor.execute('UPDATE orders SET user_id = ? WHERE user_id = ?', (keep_id, delete_id))

        # Migrate cart items
        cursor.execute('SELECT COUNT(*) as count FROM cart_items WHERE user_id = ?', (delete_id,))
        cart_count = cursor.fetchone()['count']
        if cart_count > 0:
            operations.append(f"Migrate {cart_count} cart item(s)")
            if not dry_run:
                # Delete duplicates first, then migrate
                cursor.execute('''
                    DELETE FROM cart_items
                    WHERE user_id = ?
                    AND item_id IN (
                        SELECT item_id FROM cart_items WHERE user_id = ?
                    )
                ''', (delete_id, keep_id))
                cursor.execute('UPDATE cart_items SET user_id = ? WHERE user_id = ?', (keep_id, delete_id))

        # Migrate candles/soaps cart
        cursor.execute('SELECT COUNT(*) as count FROM candles_soaps_cart WHERE user_id = ?', (delete_id,))
        cs_cart_count = cursor.fetchone()['count']
        if cs_cart_count > 0:
            operations.append(f"Migrate {cs_cart_count} C&S cart item(s)")
            if not dry_run:
                cursor.execute('''
                    DELETE FROM candles_soaps_cart
                    WHERE user_id = ?
                    AND item_id IN (
                        SELECT item_id FROM candles_soaps_cart WHERE user_id = ?
                    )
                ''', (delete_id, keep_id))
                cursor.execute('UPDATE candles_soaps_cart SET user_id = ? WHERE user_id = ?', (keep_id, delete_id))

        # Delete the duplicate user
        operations.append(f"Delete user account {delete_id}")
        if not dry_run:
            cursor.execute('DELETE FROM users WHERE id = ?', (delete_id,))

        for op in operations:
            print(f"  - {op}")

        if not dry_run:
            conn.commit()
            print("\n[SUCCESS] Merge completed successfully!")
        else:
            print("\n[DRY RUN] No changes made. Remove --dry-run to apply.")

        conn.close()
        return True

    except Exception as e:
        conn.rollback()
        conn.close()
        print(f"[ERROR] Merge failed: {str(e)}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Manage duplicate user accounts')
    parser.add_argument('--list', action='store_true', help='List all duplicates')
    parser.add_argument('--email', type=str, help='Show details for email')
    parser.add_argument('--merge', nargs=2, type=int, metavar=('KEEP_ID', 'DELETE_ID'),
                       help='Merge DELETE_ID into KEEP_ID')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without applying')
    parser.add_argument('--db-path', default='database/signups.db', help='Database path')

    args = parser.parse_args()

    db_path = os.path.abspath(args.db_path)
    if not os.path.exists(db_path):
        print(f"[ERROR] Database not found: {db_path}")
        return 1

    db = Database(db_path)

    if args.list:
        duplicates = list_duplicates(db)
        if not duplicates:
            print("[OK] No duplicate emails found!")
            return 0

        print(f"\nFound {len(duplicates)} duplicate email(s):")
        print("=" * 80)

        for email, users in duplicates.items():
            print(f"\nEmail: {email}")
            print(f"Accounts: {len(users)}")
            for user in users:
                details = get_user_details(db, user['id'])
                if details:
                    print_user_details(details)
            print("-" * 80)

    elif args.email:
        show_email_details(db, args.email)

    elif args.merge:
        keep_id, delete_id = args.merge
        success = merge_users(db, keep_id, delete_id, dry_run=args.dry_run)
        return 0 if success else 1

    else:
        parser.print_help()
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
