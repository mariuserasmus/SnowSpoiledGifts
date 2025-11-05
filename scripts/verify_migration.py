import sqlite3

conn = sqlite3.connect('database/signups.db')
cursor = conn.cursor()

# Check schema
cursor.execute('PRAGMA table_info(cart_items)')
print('Cart Items Schema:')
for row in cursor.fetchall():
    print(f'  {row}')

# Check data
print('\nSample data:')
cursor.execute('SELECT * FROM cart_items LIMIT 5')
for row in cursor.fetchall():
    print(f'  {row}')

# Check counts
cursor.execute("SELECT product_type, COUNT(*) FROM cart_items GROUP BY product_type")
print('\nCounts by product type:')
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[1]}')

conn.close()
