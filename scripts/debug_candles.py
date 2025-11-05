"""Debug script to check candles_soaps database"""
import sqlite3

conn = sqlite3.connect('database/signups.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=== CANDLES & SOAPS PRODUCTS ===")
cursor.execute('SELECT * FROM candles_soaps_products')
products = cursor.fetchall()
print(f"Total products: {len(products)}\n")

for product in products:
    print(f"ID: {product['id']}")
    print(f"  Name: {product['name']}")
    print(f"  Product Code: {product['product_code']}")
    print(f"  Active: {product['is_active']}")
    print(f"  Stock Quantity: {product['stock_quantity']}")
    print(f"  Price: R{product['price']}")
    print(f"  Created: {product['created_date']}")
    print()

print("\n=== CANDLES & SOAPS PRODUCT PHOTOS ===")
cursor.execute('SELECT * FROM candles_soaps_product_photos')
photos = cursor.fetchall()
print(f"Total photos: {len(photos)}\n")

for photo in photos:
    print(f"ID: {photo['id']}")
    print(f"  Product ID: {photo['product_id']}")
    print(f"  Photo Path: {photo['photo_path']}")
    print(f"  Is Main: {photo['is_main']}")
    print()

conn.close()
