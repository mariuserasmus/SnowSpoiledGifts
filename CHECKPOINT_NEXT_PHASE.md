# 🎯 NEXT PHASE: E-COMMERCE FEATURES

**Date:** October 27, 2025
**Current Status:** Admin & Shop Complete - Ready for Cart & Checkout

---

## 🛒 PHASE 1: Shopping Cart (NEXT UP)
**Priority:** HIGH
**Complexity:** Medium
**Estimated Time:** 4-6 hours

### Features to Implement:
- [ ] Add to Cart button on product cards
- [ ] Add to Cart from product detail modal
- [ ] Cart storage (Flask session for guests, database for members)
- [ ] Cart icon in navbar with item count badge
- [ ] Cart page (`/cart`) showing all cart items
- [ ] Update quantity (increase/decrease buttons)
- [ ] Remove items from cart
- [ ] Cart subtotal calculation
- [ ] Tax calculation (if applicable)
- [ ] "Continue Shopping" button
- [ ] "Proceed to Checkout" button
- [ ] Empty cart message when no items

### Database Schema:
```sql
CREATE TABLE cart_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,  -- For guest users
    user_id INTEGER,  -- For logged-in users (NULL for guests)
    item_id INTEGER NOT NULL,
    quantity INTEGER DEFAULT 1,
    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (item_id) REFERENCES cutter_items(id)
);
```

### Files to Modify:
- `app.py` - Add cart routes (`/cart`, `/cart/add`, `/cart/update`, `/cart/remove`)
- `src/database.py` - Add cart methods
- `templates/3d_printing.html` - Add "Add to Cart" buttons
- `templates/cart.html` - NEW - Create cart page
- `templates/base.html` - Add cart icon to navbar

---

## 👤 PHASE 2: User Authentication & Accounts
**Priority:** HIGH
**Complexity:** Medium-High
**Estimated Time:** 6-8 hours

### 2A: Guest Checkout
- [ ] Guest checkout flow (no account required)
- [ ] Form to collect: name, email, phone, shipping address
- [ ] Store guest orders with email as identifier
- [ ] Send order confirmation email

### 2B: Member Registration
- [ ] Registration page (`/register`)
- [ ] Email/password form
- [ ] Password hashing with bcrypt
- [ ] Email validation (unique check)
- [ ] Password strength requirements
- [ ] Terms & conditions acceptance
- [ ] Welcome email on registration

### 2C: Member Login/Logout
- [ ] Login page (`/login`)
- [ ] Session management
- [ ] "Remember me" checkbox
- [ ] Logout functionality
- [ ] Protected routes (@login_required decorator)

### 2D: Member Dashboard
- [ ] Member dashboard (`/account`)
- [ ] View/edit profile
- [ ] Order history
- [ ] Saved addresses
- [ ] Change password

### 2E: Password Reset
- [ ] Forgot password page
- [ ] Generate reset token
- [ ] Send reset email with link
- [ ] Reset password page
- [ ] Token expiration (24 hours)

### Database Schema:
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    first_name TEXT,
    last_name TEXT,
    phone TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active INTEGER DEFAULT 1
);

CREATE TABLE user_addresses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    address_type TEXT DEFAULT 'shipping',  -- 'shipping' or 'billing'
    address_line1 TEXT NOT NULL,
    address_line2 TEXT,
    city TEXT NOT NULL,
    state_province TEXT,
    postal_code TEXT NOT NULL,
    country TEXT DEFAULT 'South Africa',
    is_default INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE password_reset_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token TEXT UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## 💳 PHASE 3: Checkout & Payment
**Priority:** HIGH
**Complexity:** High
**Estimated Time:** 8-10 hours

### 3A: Checkout Flow
- [ ] Checkout page (`/checkout`)
- [ ] Step 1: Shipping information
- [ ] Step 2: Billing information (with "Same as shipping" option)
- [ ] Step 3: Review order
- [ ] Order summary sidebar (items, subtotal, shipping, tax, total)
- [ ] Validate all fields before payment
- [ ] Store order in "pending" status before payment

### 3B: Shipping
- [ ] Calculate shipping costs (flat rate, free over R500, etc.)
- [ ] Multiple shipping methods (standard, express)
- [ ] Shipping address validation

### 3C: Payment Integration
- [ ] **PayFast** integration (recommended for South Africa)
  - Merchant ID setup
  - Generate payment signature
  - Redirect to PayFast
  - Handle payment return (success/cancel)
  - Handle IPN (Instant Payment Notification)
- [ ] Alternative: PayPal or Stripe (international)

### 3D: Order Confirmation
- [ ] Order confirmation page (`/order/confirmation/<order_number>`)
- [ ] Display order details
- [ ] Send confirmation email to customer
- [ ] Send notification email to admin
- [ ] Clear cart after successful order

### Database Schema:
```sql
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_number TEXT UNIQUE NOT NULL,  -- Format: ORD-20251027-0001
    user_id INTEGER,  -- NULL for guest orders
    guest_email TEXT,  -- For guest orders
    subtotal REAL NOT NULL,
    shipping_cost REAL DEFAULT 0,
    tax REAL DEFAULT 0,
    total REAL NOT NULL,
    status TEXT DEFAULT 'pending',  -- pending, paid, processing, shipped, delivered, cancelled
    payment_method TEXT,  -- payfast, paypal, stripe, etc.
    payment_status TEXT DEFAULT 'pending',  -- pending, paid, failed, refunded
    notes TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    paid_date TIMESTAMP,
    shipped_date TIMESTAMP
);

CREATE TABLE order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    item_name TEXT NOT NULL,  -- Store name at purchase time
    quantity INTEGER NOT NULL,
    price_at_purchase REAL NOT NULL,  -- Store price at purchase time
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (item_id) REFERENCES cutter_items(id)
);

CREATE TABLE order_addresses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL UNIQUE,
    shipping_name TEXT NOT NULL,
    shipping_address_line1 TEXT NOT NULL,
    shipping_address_line2 TEXT,
    shipping_city TEXT NOT NULL,
    shipping_postal_code TEXT NOT NULL,
    shipping_phone TEXT,
    billing_name TEXT NOT NULL,
    billing_address_line1 TEXT NOT NULL,
    billing_address_line2 TEXT,
    billing_city TEXT NOT NULL,
    billing_postal_code TEXT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id)
);

CREATE TABLE payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    payment_gateway TEXT,  -- payfast, paypal, stripe
    transaction_id TEXT,  -- Gateway transaction ID
    amount REAL NOT NULL,
    status TEXT,  -- success, failed, pending, refunded
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    response_data TEXT,  -- Store gateway response as JSON
    FOREIGN KEY (order_id) REFERENCES orders(id)
);
```

---

## 📦 PHASE 4: Order Management (Admin)
**Priority:** MEDIUM
**Complexity:** Medium
**Estimated Time:** 4-6 hours

### Features:
- [ ] Admin orders page (`/admin/orders`)
- [ ] List all orders (table view)
- [ ] Filter by status (All, Pending, Paid, Processing, Shipped, Delivered)
- [ ] Filter by date range
- [ ] Search by order number, customer email, name
- [ ] Order detail view (`/admin/orders/<order_id>`)
- [ ] Update order status dropdown
- [ ] Mark as paid/unpaid
- [ ] Add tracking number
- [ ] View customer details
- [ ] View ordered items
- [ ] Add admin notes
- [ ] Generate invoice PDF
- [ ] Generate packing slip PDF
- [ ] Refund order (update payment status)
- [ ] Email customer when status changes

---

## 📧 PHASE 5: Email Notifications
**Priority:** MEDIUM
**Complexity:** Low
**Estimated Time:** 2-3 hours

### Email Templates Needed:
- [ ] Order confirmation (to customer)
- [ ] Order received (to admin)
- [ ] Order shipped (to customer)
- [ ] Password reset
- [ ] Welcome email (new member)
- [ ] Order cancelled (to customer)

### Setup:
- [ ] Configure Flask-Mail
- [ ] HTML email templates
- [ ] Plain text fallbacks
- [ ] Test emails in development

---

## 🚀 PHASE 6: Future Enhancements

### Product Features
- [ ] Wishlist functionality
- [ ] Product reviews & ratings (star rating + text)
- [ ] Related products recommendations
- [ ] Product quick view (modal)
- [ ] Recently viewed products
- [ ] Compare products side-by-side

### Inventory Management
- [ ] Stock level tracking
- [ ] Low stock alerts (email admin)
- [ ] Out of stock display
- [ ] Backorder handling
- [ ] Restock notifications

### Marketing & Sales
- [ ] Discount codes / coupon system
- [ ] Percentage or fixed amount discounts
- [ ] Minimum order for discount
- [ ] Expiry dates for coupons
- [ ] Loyalty points system
- [ ] Free shipping thresholds

### Customer Experience
- [ ] Social media sharing buttons
- [ ] Email product to friend
- [ ] Save cart for later
- [ ] Guest order tracking (by order number + email)
- [ ] Live chat / customer service
- [ ] FAQ section

### Admin Analytics
- [ ] Sales dashboard
- [ ] Revenue reports
- [ ] Top selling products
- [ ] Customer analytics
- [ ] Export orders to CSV
- [ ] Inventory reports
- [ ] Sales by category/type

---

## 📋 TECHNICAL NOTES

### Dependencies Needed:
```bash
pip install flask-login  # For user session management
pip install bcrypt  # For password hashing
pip install flask-mail  # For sending emails
pip install reportlab  # For PDF generation (invoices)
```

### Security Considerations:
- HTTPS in production (SSL certificate)
- CSRF protection for forms
- Rate limiting on login attempts
- Secure session cookies
- Input validation & sanitization
- SQL injection prevention (already using parameterized queries)
- XSS prevention (Jinja2 auto-escapes)

### Payment Gateway Setup:
- PayFast merchant account required
- Test mode available for development
- Sandbox credentials for testing
- IPN (Instant Payment Notification) endpoint needed
- Signature generation for security

---

## 📝 RECOMMENDED IMPLEMENTATION ORDER

1. **Start with Cart** (Phase 1) - Allows customers to add items
2. **Then Authentication** (Phase 2) - Guest + Member flows
3. **Then Checkout** (Phase 3) - Complete purchase flow
4. **Then Order Admin** (Phase 4) - Manage orders
5. **Then Emails** (Phase 5) - Improve communication
6. **Then Enhancements** (Phase 6) - As needed

---

**Total Estimated Time: 24-33 hours of development**

Ready to start with Shopping Cart! 🛒
