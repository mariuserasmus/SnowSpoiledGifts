"""Test script to verify add to cart functionality"""
import requests
import json

# Test the candles & soaps cart endpoint
url = 'http://localhost:5000/candles-soaps/cart/add'
headers = {'Content-Type': 'application/json'}
data = {'product_id': 3, 'quantity': 1}  # Flower Ladies

print("Testing Candles & Soaps Add to Cart...")
print(f"URL: {url}")
print(f"Data: {data}")
print()

try:
    response = requests.post(url, headers=headers, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

    if response.status_code == 200:
        json_response = response.json()
        print(f"\nParsed Response:")
        print(f"  Success: {json_response.get('success')}")
        print(f"  Message: {json_response.get('message')}")
        print(f"  Cart Count: {json_response.get('cart_count')}")
    else:
        print(f"\nError: {response.status_code}")

except Exception as e:
    print(f"Error: {e}")
