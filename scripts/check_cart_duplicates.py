"""Check for duplicate items in cart"""
import sqlite3

conn = sqlite3.connect('database/signups.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=== CHECKING FOR DUPLICATE CART ITEMS ===\n")

# Get all cart items
cursor.execute('''
    SELECT * FROM cart_items
    ORDER BY user_id, session_id, product_type, product_id
''')
items = cursor.fetchall()

print(f"Total cart items: {len(items)}\n")

# Group by user/session and product
from collections import defaultdict
by_user_product = defaultdict(list)

for item in items:
    key = f"user:{item['user_id']}_session:{item['session_id']}_type:{item['product_type']}_product:{item['product_id']}"
    by_user_product[key].append(dict(item))

# Check for duplicates
duplicates_found = False
for key, items_list in by_user_product.items():
    if len(items_list) > 1:
        duplicates_found = True
        print(f"⚠️  DUPLICATE FOUND: {key}")
        for item in items_list:
            print(f"    ID: {item['id']}, Quantity: {item['quantity']}, Added: {item['added_date']}")
        print()

if not duplicates_found:
    print("✓ No duplicates found")

# Show current cart state
print("\n=== CURRENT CART CONTENTS ===\n")
for item in items:
    print(f"ID: {item['id']}")
    print(f"  User: {item['user_id']}, Session: {item['session_id']}")
    print(f"  Type: {item['product_type']}, Product: {item['product_id']}")
    print(f"  Quantity: {item['quantity']}")
    print(f"  Added: {item['added_date']}")
    print()

conn.close()
