"""
UNIFIED CART FUNCTIONS FOR database.py

Replace the old cart functions in database.py with these unified versions.
These handle both cutter_items and candles_soaps products in a single cart_items table.
"""

def add_to_cart(self, session_id, product_id, quantity=1, user_id=None, product_type='cutter_item'):
    """
    Add a product to cart (unified for all product types)

    Args:
        session_id: Session ID for guest users
        product_id: The product ID
        quantity: Quantity to add
        user_id: User ID if logged in
        product_type: 'cutter_item' or 'candles_soap'
    """
    conn = self.get_connection()
    cursor = conn.cursor()

    try:
        # Check if item already in cart
        if user_id:
            cursor.execute('''
                SELECT id, quantity FROM cart_items
                WHERE user_id = ? AND product_id = ? AND product_type = ?
            ''', (user_id, product_id, product_type))
        else:
            cursor.execute('''
                SELECT id, quantity FROM cart_items
                WHERE session_id = ? AND product_id = ? AND product_type = ? AND user_id IS NULL
            ''', (session_id, product_id, product_type))

        existing = cursor.fetchone()

        if existing:
            # Update quantity
            new_quantity = existing['quantity'] + quantity
            cursor.execute('''
                UPDATE cart_items
                SET quantity = ?
                WHERE id = ?
            ''', (new_quantity, existing['id']))
            message = "Cart updated!"
        else:
            # Add new item
            cursor.execute('''
                INSERT INTO cart_items (session_id, user_id, product_type, product_id, quantity)
                VALUES (?, ?, ?, ?, ?)
            ''', (session_id, user_id, product_type, product_id, quantity))
            message = "Added to cart!"

        conn.commit()
        conn.close()
        return True, message

    except Exception as e:
        conn.close()
        return False, f"An error occurred: {str(e)}"
