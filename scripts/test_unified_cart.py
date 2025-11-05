#!/usr/bin/env python3
"""
Test script for unified cart system
"""

import sys
sys.path.insert(0, 'src')

from database import Database

# Initialize database
db = Database('database/signups.db')

print("="*60)
print("TESTING UNIFIED CART SYSTEM")
print("="*60)

# Test session
test_session = "test_session_12345"
test_user_id = 3  # Existing user

print("\n[TEST 1] Get current cart items...")
items = db.get_cart_items(test_session, user_id=test_user_id)
print(f"  Found {len(items)} items in cart")
for item in items:
    print(f"  - {item['name']} (Type: {item['product_type']}, Qty: {item['quantity']})")

print("\n[TEST 2] Get cart count...")
count = db.get_cart_count(test_session, user_id=test_user_id)
print(f"  Total items in cart: {count}")

print("\n[TEST 3] Test backward-compatible candles/soaps functions...")
candles_count = db.get_candles_soaps_cart_count(test_session, user_id=test_user_id)
print(f"  Candles/Soaps cart count: {candles_count}")

candles_items = db.get_candles_soaps_cart_items(test_session, user_id=test_user_id)
print(f"  Candles/Soaps items: {len(candles_items)}")
for item in candles_items:
    print(f"  - {item['name']} (Qty: {item['quantity']})")

print("\n[TEST 4] Add a cutter item to cart...")
success, msg = db.add_to_cart(test_session, product_id=1, quantity=2, user_id=test_user_id, product_type='cutter_item')
print(f"  Result: {msg} (Success: {success})")

print("\n[TEST 5] Add a candles/soaps item to cart...")
success, msg = db.add_to_cart(test_session, product_id=3, quantity=1, user_id=test_user_id, product_type='candles_soap')
print(f"  Result: {msg} (Success: {success})")

print("\n[TEST 6] Get updated cart...")
items = db.get_cart_items(test_session, user_id=test_user_id)
print(f"  Found {len(items)} items in cart")
for item in items:
    print(f"  - {item['name']} (Type: {item['product_type']}, Qty: {item['quantity']}, Subtotal: R{item['subtotal']:.2f})")

print("\n[TEST 7] Calculate cart total...")
total = sum(item['subtotal'] for item in items)
print(f"  Cart Total: R{total:.2f}")

print("\n" + "="*60)
print("ALL TESTS COMPLETED!")
print("="*60)
