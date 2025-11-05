# app.py Update Instructions - Unified Cart System

## Quick Reference: Function Call Changes

### 1. Add to Cart - Cutter Items

**Find all occurrences of:**
```python
db.add_to_cart(session_id, item_id, quantity, user_id)
```

**Replace with:**
```python
db.add_to_cart(session_id, item_id, 'cutter_item', quantity, user_id)
```

**Example Route:**
```python
@app.route('/add_to_cart/<int:item_id>', methods=['POST'])
def add_to_cart_route(item_id):
    quantity = int(request.form.get('quantity', 1))
    session_id = session.get('session_id')
    user_id = session.get('user_id')

    # ADD 'cutter_item' as the third parameter
    success, message = db.add_to_cart(session_id, item_id, 'cutter_item', quantity, user_id)

    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(request.referrer or url_for('shop'))
```

---

### 2. Add to Cart - Candles & Soaps

**Find:**
```python
db.add_to_candles_soaps_cart(session_id, product_id, quantity, user_id)
```

**Replace with:**
```python
db.add_to_cart(session_id, product_id, 'candles_soap', quantity, user_id)
```

**Example Route:**
```python
@app.route('/candles-soaps/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_candles_soaps_cart_route(product_id):
    quantity = int(request.form.get('quantity', 1))
    session_id = session.get('session_id')
    user_id = session.get('user_id')

    # USE unified function with 'candles_soap' type
    success, message = db.add_to_cart(session_id, product_id, 'candles_soap', quantity, user_id)

    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(request.referrer or url_for('candles_soaps'))
```

---

### 3. View Cart - Get All Items

**Find:**
```python
cutter_items = db.get_cart_items(session_id, user_id)
candles_items = db.get_candles_soaps_cart_items(session_id, user_id)
all_items = cutter_items + candles_items
```

**Replace with:**
```python
all_items = db.get_cart_items(session_id, user_id)
```

**Example Route:**
```python
@app.route('/cart')
def view_cart():
    session_id = session.get('session_id')
    user_id = session.get('user_id')

    # Single call gets ALL cart items (both cutter and candles/soaps)
    all_items = db.get_cart_items(session_id, user_id)

    # Calculate total
    cart_total = sum(item.get('subtotal', 0) for item in all_items)

    return render_template('cart.html',
                         cart_items=all_items,
                         cart_total=cart_total)
```

**If you need to separate by product type for display:**
```python
@app.route('/cart')
def view_cart():
    session_id = session.get('session_id')
    user_id = session.get('user_id')

    # Get all items
    all_items = db.get_cart_items(session_id, user_id)

    # Optional: Separate by type for different display sections
    cutter_items = [item for item in all_items if item['product_type'] == 'cutter_item']
    candles_items = [item for item in all_items if item['product_type'] == 'candles_soap']

    return render_template('cart.html',
                         all_items=all_items,
                         cutter_items=cutter_items,
                         candles_items=candles_items)
```

---

### 4. Cart Count - Context Processor

**Find:**
```python
@app.context_processor
def inject_cart_count():
    session_id = session.get('session_id')
    user_id = session.get('user_id')

    cutter_count = db.get_cart_count(session_id, user_id)
    candles_count = db.get_candles_soaps_cart_count(session_id, user_id)

    return {'cart_count': cutter_count + candles_count}
```

**Replace with:**
```python
@app.context_processor
def inject_cart_count():
    session_id = session.get('session_id')
    user_id = session.get('user_id')

    # Single call returns total count for all product types
    total_count = db.get_cart_count(session_id, user_id)

    return {'cart_count': total_count}
```

**If you need separate counts for badges:**
```python
@app.context_processor
def inject_cart_count():
    session_id = session.get('session_id')
    user_id = session.get('user_id')

    # Get counts by product type
    cutter_count = db.get_cart_count(session_id, user_id, product_type='cutter_item')
    candles_count = db.get_cart_count(session_id, user_id, product_type='candles_soap')
    total_count = cutter_count + candles_count

    return {
        'cart_count': total_count,
        'cutter_cart_count': cutter_count,
        'candles_cart_count': candles_count
    }
```

---

### 5. Update Cart Quantity

**Find:**
```python
# Separate handling by product type
if product_type == 'cutter':
    db.update_cart_quantity(cart_id, quantity)
else:
    db.update_candles_soaps_cart_quantity(cart_id, quantity)
```

**Replace with:**
```python
# One function handles all types
db.update_cart_quantity(cart_id, quantity)
```

**Example Route:**
```python
@app.route('/update_cart/<int:cart_id>', methods=['POST'])
def update_cart(cart_id):
    quantity = int(request.form.get('quantity', 1))

    # Works for all product types
    success, message = db.update_cart_quantity(cart_id, quantity)

    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('view_cart'))
```

---

### 6. Remove from Cart

**Find:**
```python
# Separate functions
if product_type == 'cutter':
    db.remove_from_cart(cart_id)
else:
    db.remove_from_candles_soaps_cart(cart_id)
```

**Replace with:**
```python
# One function handles all types
db.remove_from_cart(cart_id)
```

**Example Route:**
```python
@app.route('/remove_from_cart/<int:cart_id>', methods=['POST'])
def remove_from_cart(cart_id):
    # Works for all product types
    success, message = db.remove_from_cart(cart_id)

    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('view_cart'))
```

---

### 7. Clear Cart

**Find:**
```python
# Clear both carts separately
db.clear_cart(session_id, user_id)
db.clear_candles_soaps_cart(session_id, user_id)
```

**Replace with:**
```python
# Single call clears all product types
db.clear_cart(session_id, user_id)
```

**Example Route:**
```python
@app.route('/clear_cart', methods=['POST'])
def clear_cart():
    session_id = session.get('session_id')
    user_id = session.get('user_id')

    # Clears all items (both cutter and candles/soaps)
    success, message = db.clear_cart(session_id, user_id)

    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('view_cart'))
```

**If you want to clear only specific product type:**
```python
@app.route('/clear_cart/<product_type>', methods=['POST'])
def clear_cart_by_type(product_type):
    session_id = session.get('session_id')
    user_id = session.get('user_id')

    # Clear only cutter items or only candles/soaps items
    success, message = db.clear_cart(session_id, user_id, product_type=product_type)

    return redirect(url_for('view_cart'))
```

---

### 8. Login - Cart Migration

**Find:**
```python
@app.route('/login', methods=['POST'])
def login():
    # ... authentication logic ...

    if user:
        session['user_id'] = user['id']
        session_id = session.get('session_id')

        # Migrate both carts separately
        db.migrate_guest_cart_to_user(session_id, user['id'])
        db.migrate_guest_candles_soaps_cart_to_user(session_id, user['id'])
```

**Replace with:**
```python
@app.route('/login', methods=['POST'])
def login():
    # ... authentication logic ...

    if user:
        session['user_id'] = user['id']
        session_id = session.get('session_id')

        # Single call migrates all product types
        db.migrate_guest_cart_to_user(session_id, user['id'])
```

**Full Example:**
```python
@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    user = db.verify_user(email, password)

    if user:
        session['user_id'] = user['id']
        session['user_email'] = user['email']
        session['is_admin'] = user['is_admin']

        # Migrate guest cart to user (all product types)
        session_id = session.get('session_id')
        if session_id:
            db.migrate_guest_cart_to_user(session_id, user['id'])

        flash('Login successful!', 'success')
        return redirect(url_for('index'))
    else:
        flash('Invalid email or password', 'error')
        return redirect(url_for('login'))
```

---

### 9. Checkout - Mixed Cart Processing

**Example of handling mixed cart at checkout:**

```python
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    session_id = session.get('session_id')
    user_id = session.get('user_id')

    if not user_id:
        flash('Please login to checkout', 'warning')
        return redirect(url_for('login'))

    # Get all cart items (both types)
    cart_items = db.get_cart_items(session_id, user_id)

    if not cart_items:
        flash('Your cart is empty', 'warning')
        return redirect(url_for('shop'))

    # Calculate total
    cart_total = sum(item.get('subtotal', 0) for item in cart_items)

    if request.method == 'POST':
        # Process order
        shipping_method = request.form.get('shipping_method')
        shipping_address = request.form.get('shipping_address')

        # Create order
        order_id = db.create_order(
            user_id=user_id,
            total_amount=cart_total,
            shipping_method=shipping_method,
            shipping_address=shipping_address
        )

        if order_id:
            # Add all cart items to order (handles both product types)
            for item in cart_items:
                db.add_order_item(
                    order_id=order_id,
                    product_id=item['product_id'],
                    product_type=item['product_type'],
                    quantity=item['quantity'],
                    price=item['price']
                )

            # Clear cart after successful order
            db.clear_cart(session_id, user_id)

            flash('Order placed successfully!', 'success')
            return redirect(url_for('order_confirmation', order_id=order_id))
        else:
            flash('Error creating order', 'error')

    return render_template('checkout.html',
                         cart_items=cart_items,
                         cart_total=cart_total)
```

---

## Search & Replace Guide

Use your editor's search and replace feature:

### Pattern 1: Add to Cart (Cutters)
**Search for:** `db.add_to_cart(session_id, item_id,`
**Replace with:** `db.add_to_cart(session_id, item_id, 'cutter_item',`

### Pattern 2: Add to Cart (Candles/Soaps)
**Search for:** `db.add_to_candles_soaps_cart(`
**Replace with:** `db.add_to_cart(` (then manually add 'candles_soap' parameter)

### Pattern 3: Get Cart Items (Candles/Soaps)
**Search for:** `db.get_candles_soaps_cart_items(`
**Replace with:** `db.get_cart_items(` (works as drop-in replacement)

### Pattern 4: Cart Count (Candles/Soaps)
**Search for:** `db.get_candles_soaps_cart_count(`
**Replace with:** `db.get_cart_count(`

### Pattern 5: Update Quantity (Candles/Soaps)
**Search for:** `db.update_candles_soaps_cart_quantity(`
**Replace with:** `db.update_cart_quantity(`

### Pattern 6: Remove from Cart (Candles/Soaps)
**Search for:** `db.remove_from_candles_soaps_cart(`
**Replace with:** `db.remove_from_cart(`

### Pattern 7: Clear Cart (Candles/Soaps)
**Search for:** `db.clear_candles_soaps_cart(`
**Replace with:** `db.clear_cart(`

### Pattern 8: Migrate Cart (Candles/Soaps)
**Search for:** `db.migrate_guest_candles_soaps_cart_to_user(`
**Replace with:** `db.migrate_guest_cart_to_user(` (or delete if already called for cutters)

---

## Testing Your Changes

After updating app.py, test these scenarios:

### Basic Cart Operations
1. Add cutter item to cart
2. Add candles/soap item to cart
3. View cart (should show both)
4. Update quantities
5. Remove items
6. Clear cart

### User Flow
1. As guest: Add items, register, verify cart persists
2. As guest: Add items, login, verify carts merge
3. As logged-in user: Add items, logout, login, verify cart persists

### Checkout
1. Checkout with only cutter items
2. Checkout with only candles/soaps items
3. Checkout with mixed cart (both types)
4. Verify order items are created correctly
5. Verify stock is updated correctly

---

## Common Pitfalls

### 1. Missing product_type Parameter
**Wrong:**
```python
db.add_to_cart(session_id, item_id, quantity, user_id)
```
**Right:**
```python
db.add_to_cart(session_id, item_id, 'cutter_item', quantity, user_id)
```

### 2. Calling Two Functions to Get Cart Items
**Wrong:**
```python
cutter_items = db.get_cart_items(session_id, user_id)
candles_items = db.get_candles_soaps_cart_items(session_id, user_id)
```
**Right:**
```python
all_items = db.get_cart_items(session_id, user_id)
```

### 3. Adding Cart Counts Separately
**Wrong:**
```python
count = db.get_cart_count(session_id, user_id) + db.get_candles_soaps_cart_count(session_id, user_id)
```
**Right:**
```python
count = db.get_cart_count(session_id, user_id)
```

### 4. Migrating Carts Twice
**Wrong:**
```python
db.migrate_guest_cart_to_user(session_id, user_id)
db.migrate_guest_candles_soaps_cart_to_user(session_id, user_id)
```
**Right:**
```python
db.migrate_guest_cart_to_user(session_id, user_id)  # Handles all types
```

---

## Files Modified

After completing the updates:

- `c:\Claude\SSG\app.py` - Updated cart routes
- `c:\Claude\SSG\src\database.py` - Updated cart functions
- `c:\Claude\SSG\database\signups.db` - Migrated cart tables

## Backup Reminder

Before making changes to app.py:
```bash
cp app.py app.py.backup
```

If something goes wrong:
```bash
cp app.py.backup app.py
```

---

## Need Help?

- Review the full migration guide: `UNIFIED_CART_MIGRATION_GUIDE.md`
- Check the new function signatures: `unified_cart_functions.py`
- Test with small changes first
- Verify each route works before moving to the next

Good luck with the migration!
