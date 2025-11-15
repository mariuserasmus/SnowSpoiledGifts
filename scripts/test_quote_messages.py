"""
Test script for the quote messaging system.

This script tests all the new database methods to ensure they work correctly.

Author: SQLite Database Specialist
Date: 2025-11-14
"""

import sys
import os

# Add parent directory to path to import Database
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.database import Database

def test_quote_messaging_system():
    """Test all quote messaging functionality"""

    # Initialize database
    db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'signups.db')
    db = Database(db_path)

    print("=" * 70)
    print("TESTING QUOTE MESSAGING SYSTEM")
    print("=" * 70)

    # Test 1: Get existing quotes to test with
    print("\n[TEST 1] Finding existing quotes...")
    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, service_type, name FROM quote_requests LIMIT 1")
    custom_quote = cursor.fetchone()

    cursor.execute("SELECT id, occasion, name FROM cake_topper_requests LIMIT 1")
    cake_quote = cursor.fetchone()

    cursor.execute("SELECT id, name FROM print_service_requests LIMIT 1")
    print_quote = cursor.fetchone()

    conn.close()

    if not custom_quote and not cake_quote and not print_quote:
        print("  [WARNING] No quotes found in database. Creating test quote...")
        # Create a test quote
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO quote_requests (service_type, name, email, description, quantity)
            VALUES (?, ?, ?, ?, ?)
        ''', ('custom_design', 'Test User', 'test@example.com', 'Test description', 1))
        test_quote_id = cursor.lastrowid
        conn.commit()
        conn.close()
        custom_quote = {'id': test_quote_id, 'service_type': 'custom_design', 'name': 'Test User'}
        print(f"  [OK] Created test quote with ID: {test_quote_id}")

    # Test 2: Add a simple admin message
    print("\n[TEST 2] Adding admin message...")
    if custom_quote:
        success, msg, msg_id = db.add_quote_message(
            quote_type='quote_requests',
            quote_id=custom_quote['id'],
            message_text='Hello! We received your quote request and are reviewing it.',
            sender='admin',
            message_type='admin_message'
        )
        print(f"  Result: {success}")
        print(f"  Message: {msg}")
        print(f"  Message ID: {msg_id}")

    # Test 3: Add a quote message with pricing
    print("\n[TEST 3] Adding quote message with pricing...")
    if custom_quote:
        success, msg, msg_id = db.add_quote_message(
            quote_type='quote_requests',
            quote_id=custom_quote['id'],
            message_text='Based on your requirements, here is our quote. Let me know if you have questions!',
            sender='admin',
            quoted_price_per_item=150.00,
            quoted_total=150.00,
            message_type='quote_sent'
        )
        print(f"  Result: {success}")
        print(f"  Message: {msg}")
        print(f"  Message ID: {msg_id}")

    # Test 4: Retrieve all messages for the quote
    print("\n[TEST 4] Retrieving all messages...")
    if custom_quote:
        messages = db.get_quote_messages('quote_requests', custom_quote['id'])
        print(f"  Found {len(messages)} message(s)")
        for i, msg in enumerate(messages, 1):
            print(f"\n  Message {i}:")
            print(f"    ID: {msg['id']}")
            print(f"    Sender: {msg['sender']}")
            print(f"    Type: {msg['message_type']}")
            print(f"    Text: {msg['message_text'][:50]}...")
            if msg['quoted_price_per_item']:
                print(f"    Price per item: R{msg['quoted_price_per_item']:.2f}")
            if msg['quoted_total']:
                print(f"    Total: R{msg['quoted_total']:.2f}")
            print(f"    Created: {msg['created_at']}")

    # Test 5: Update quote pricing directly
    print("\n[TEST 5] Updating quote pricing...")
    if custom_quote:
        success, msg = db.update_quote_pricing(
            quote_type='quote_requests',
            quote_id=custom_quote['id'],
            price_per_item=175.00,
            total=175.00
        )
        print(f"  Result: {success}")
        print(f"  Message: {msg}")

    # Test 6: Verify pricing was updated in quote table
    print("\n[TEST 6] Verifying quote table pricing...")
    if custom_quote:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT quoted_price_per_item, quoted_total, quoted_date
            FROM quote_requests WHERE id = ?
        ''', (custom_quote['id'],))
        quote_data = cursor.fetchone()
        conn.close()

        if quote_data:
            print(f"  Price per item: R{quote_data['quoted_price_per_item']:.2f}")
            print(f"  Total: R{quote_data['quoted_total']:.2f}")
            print(f"  Quoted date: {quote_data['quoted_date']}")

    # Test 7: Test invalid quote type
    print("\n[TEST 7] Testing error handling (invalid quote type)...")
    success, msg, msg_id = db.add_quote_message(
        quote_type='invalid_type',
        quote_id=1,
        message_text='This should fail',
        sender='admin'
    )
    print(f"  Result: {success} (should be False)")
    print(f"  Message: {msg}")

    # Test 8: Test with cake topper quote (if exists)
    if cake_quote:
        print("\n[TEST 8] Testing with cake topper quote...")
        success, msg, msg_id = db.add_quote_message(
            quote_type='cake_topper_requests',
            quote_id=cake_quote['id'],
            message_text='Your cake topper design looks great! Here is the pricing.',
            sender='admin',
            quoted_price_per_item=85.00,
            quoted_total=85.00,
            message_type='quote_sent'
        )
        print(f"  Result: {success}")
        print(f"  Message ID: {msg_id}")

        messages = db.get_quote_messages('cake_topper_requests', cake_quote['id'])
        print(f"  Retrieved {len(messages)} message(s)")

    # Test 9: Test with print service quote (if exists)
    if print_quote:
        print("\n[TEST 9] Testing with print service quote...")
        success, msg, msg_id = db.add_quote_message(
            quote_type='print_service_requests',
            quote_id=print_quote['id'],
            message_text='Your files have been reviewed. Quote attached.',
            sender='admin',
            quoted_total=45.50,
            attached_image='quote_mockup.png',
            message_type='quote_sent'
        )
        print(f"  Result: {success}")
        print(f"  Message ID: {msg_id}")

        messages = db.get_quote_messages('print_service_requests', print_quote['id'])
        print(f"  Retrieved {len(messages)} message(s)")

    print("\n" + "=" * 70)
    print("ALL TESTS COMPLETED")
    print("=" * 70)

if __name__ == '__main__':
    try:
        test_quote_messaging_system()
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
