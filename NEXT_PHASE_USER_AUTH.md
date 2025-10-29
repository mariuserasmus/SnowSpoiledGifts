# NEXT PHASE: User Authentication

**Status:** Ready to start
**Estimated Time:** 6-8 hours
**Priority:** High (needed before checkout)

---

## Current State (Shopping Cart - Phase 1 Complete)

✅ Shopping cart fully functional
✅ Guest users can add items (session-based)
✅ Cart badge in navbar
✅ Full cart page with quantity controls
✅ Database has `user_id` field ready in `cart_items` table

---

## Phase 2: User Authentication - Implementation Plan

### Checkpoint 2A: Database & Core Auth (45-60 min)
- [ ] Create `users` table in database
  - id, email, password_hash, name, phone, created_date
  - is_active, email_verified
- [ ] Install `bcrypt` for password hashing
- [ ] Add user management methods to `database.py`:
  - `create_user(email, password, name, phone)`
  - `get_user_by_email(email)`
  - `get_user_by_id(user_id)`
  - `verify_password(email, password)`
  - `update_user(user_id, data)`
- [ ] Create registration form in `src/forms.py`
- [ ] Create `/register` route
- [ ] Create `register.html` template
- [ ] **TEST:** Register new user, verify in database

### Checkpoint 2B: Login/Logout (30-45 min)
- [ ] Install `flask-login` extension
- [ ] Configure UserLoader in `app.py`
- [ ] Create login form
- [ ] Create `/login` route
- [ ] Create `/logout` route
- [ ] Create `login.html` template
- [ ] Add login/logout links to navbar
- [ ] Update navbar to show username when logged in
- [ ] **TEST:** Login, logout, verify sessions work

### Checkpoint 2C: Member Dashboard (45-60 min)
- [ ] Create `/account` route (login required)
- [ ] Create `account.html` template showing:
  - User profile information
  - Edit profile form
  - Order history (placeholder for now)
- [ ] Add "My Account" dropdown in navbar
- [ ] Migrate guest cart to user cart on login
  - Transfer cart_items from session_id to user_id
- [ ] **TEST:** Login, view dashboard, add items to cart

### Checkpoint 2D: Integration with Existing System (30-45 min)
- [ ] Update cart routes to check for logged-in user
- [ ] Update `get_cart_items()` calls to use user_id when available
- [ ] Add decorator for login-required routes
- [ ] Test guest → member cart migration
- [ ] **TEST:** Full flow - guest cart → register → cart preserved

### Checkpoint 2E: Password Reset (Optional - 45-60 min)
*Can defer this if needed*
- [ ] Create password reset token system
- [ ] Create `/forgot-password` route
- [ ] Create `/reset-password/<token>` route
- [ ] Send reset email
- [ ] Create forgot/reset password templates
- [ ] **TEST:** Request reset, verify email, reset password

---

## Files to Create/Modify

### New Files:
- `templates/register.html`
- `templates/login.html`
- `templates/account.html`
- `templates/forgot_password.html` (optional)
- `templates/reset_password.html` (optional)

### Modify:
- `src/database.py` - Add users table + methods
- `app.py` - Add auth routes + flask-login setup
- `src/forms.py` - Add registration/login forms
- `templates/base.html` - Update navbar with login/account links
- `requirements.txt` - Add bcrypt, flask-login

---

## Dependencies to Install

```bash
pip install flask-login bcrypt
```

Or add to requirements.txt:
```
flask-login>=0.6.3
bcrypt>=4.1.2
```

---

## Key Design Decisions

1. **Email as Username:** Use email for login (simpler UX)
2. **Session-based Auth:** Use flask-login (not JWT)
3. **Cart Migration:** Automatically transfer guest cart on login
4. **Optional Fields:** Phone number optional during registration
5. **Email Verification:** Skip for MVP (add later if needed)

---

## Testing Checklist

After Phase 2 completion:
- [ ] Register new user
- [ ] Login with correct password
- [ ] Login with wrong password (should fail)
- [ ] Logout
- [ ] Add items as guest → register → verify cart preserved
- [ ] Add items as guest → login existing → verify cart merged
- [ ] View account dashboard
- [ ] Edit profile information
- [ ] Access protected routes without login (should redirect)

---

## Success Criteria

Phase 2 is complete when:
1. Users can register and login
2. Guest carts transfer to user accounts on login
3. "My Account" page shows user info
4. Navbar shows logged-in state
5. Cart properly associates with user_id
6. All tests pass

---

## After Phase 2: What's Next?

**Phase 3: Checkout & Orders**
- Shipping address form
- Payment integration (PayFast/PayPal)
- Create orders table
- Order confirmation emails
- Order history in account

**Phase 4: Admin Order Management**
- View all orders
- Update order status
- Mark as shipped
- Send tracking info

---

**Start Date:** [To be determined]
**Completion Target:** Same day (6-8 hours)

---

📌 **Quick Start Command:**
When starting Phase 2, say: "Let's start Phase 2: User Authentication. Begin with Checkpoint 2A."
