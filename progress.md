# Snow's Spoiled Gifts - Development Progress

## Session Summary (2025-10-30 - Phase A-C: Complete Order Management & Invoice System)

### 🎯 MAJOR MILESTONE: Full E-Commerce Order Management

**Status:** Phases A, B, and C - 100% Complete ✅

#### What Was Completed

**Phase A: Enhanced Order Status Flow**
1. **Expanded Order Status System**
   - Added new statuses: `awaiting_payment`, `paid`, `processing`, `cancelled`
   - Enhanced from 4 to 8 statuses for complete order lifecycle
   - Updated admin order management UI with all statuses
   - Customer order history shows all statuses with color-coded badges

2. **Database Schema Updates**
   - Added `invoice_number`, `invoice_generated_date`, `invoice_sent_date` to orders
   - Added `quote_type`, `quote_id` to track quote origins
   - Added `payment_received_date` for tracking payments
   - Added `order_number` and `converted_to_order_date` to quote tables

3. **Email Notifications Enhanced**
   - Updated `send_order_status_update()` with all new statuses
   - Professional email templates for each status
   - Awaiting Payment, Paid, Processing, Cancelled emails added
   - Logo embedding in all emails

**Phase B: Quote-to-Order Conversion System**
1. **Conversion Workflow**
   - Created `convert_quote_to_sale()` method in database.py
   - Converts any quote type (Custom Design, Cake Topper, 3D Print) to cart item
   - Auto-creates user accounts for quote customers
   - Generates secure temporary passwords
   - Sends welcome email with login credentials

2. **Admin Interface**
   - Added "Convert to Sale" button in admin-quotes.html
   - Conversion modal with item name, price, description fields
   - Creates custom item in cutter_items table
   - Adds item to customer's cart automatically
   - Links quote to order bidirectionally

3. **User Experience**
   - Pre-populates quote forms for logged-in users
   - Sends notification email when quote converted
   - Includes temporary password for new users
   - Direct cart link for checkout

4. **Bug Fixes**
   - Fixed `sqlite3.Row .get()` error (changed to conditional expressions)
   - Fixed duplicate order number constraint (now gets last order and increments)
   - Fixed mobile navbar layout (removed SSG logo)
   - Fixed mobile cart badge positioning

**Phase C: Professional Invoice System**
1. **PDF Invoice Generation**
   - Created `src/invoice_utils.py` using ReportLab library
   - Professional invoice template with company branding
   - SSG logo embedded in invoice header
   - Organized layout with items table, totals, payment info
   - Saves PDFs to `static/invoices/`

2. **Invoice Management**
   - Auto-generates invoices when status changes to confirmed/awaiting_payment
   - Manual generation from admin panel
   - Download invoice as PDF
   - Email invoice to customer with PDF attachment
   - Regenerate invoice option
   - Invoice number format: INV-SSG-202510-001

3. **Admin Interface Updates**
   - Invoice management section in order detail page
   - Shows invoice generation status
   - Download, Email, and Regenerate buttons
   - Visual indicators for invoice state

4. **Email Integration**
   - `send_invoice_email()` function with PDF attachment
   - Professional HTML email template
   - Logo header in invoice emails
   - Customer name and order details

5. **Final Fixes**
   - Fixed invoice payment method (now shows EFT instead of Cash on Delivery)
   - Maps order status to payment status display
   - Added reportlab to requirements.txt

#### Files Created
- `src/invoice_utils.py` - PDF invoice generation with ReportLab
- `static/invoices/` - Invoice PDF storage directory

#### Files Modified
- `src/database.py` - Migrations, convert_quote_to_sale(), generate_invoice_number()
- `src/email_utils.py` - Logo embedding, invoice emails, status update emails
- `app.py` - Invoice routes, quote conversion route, auto-invoice generation
- `templates/admin-order-detail.html` - Invoice management section, Delete order
- `templates/admin-orders.html` - All status filters and badges
- `templates/admin-quotes.html` - Convert to sale modal and button
- `templates/account.html` - Customer order history with all statuses
- `templates/3d_printing.html` - Pre-populate forms for logged-in users
- `templates/base.html` - Removed SSG logo from navbar (mobile fix)
- `static/css/style.css` - Mobile cart badge positioning
- `requirements.txt` - Added reportlab>=4.0.7

#### Technical Implementation

**Order Number Generation Fix:**
```python
# Old (caused duplicates):
cursor.execute('SELECT COUNT(*) FROM orders WHERE order_number LIKE ?')

# New (prevents duplicates):
cursor.execute('''
    SELECT order_number FROM orders
    WHERE order_number LIKE ?
    ORDER BY order_number DESC
    LIMIT 1
''')
last_sequence = int(last_order['order_number'].split('-')[-1])
order_sequence = last_sequence + 1
```

**Invoice Auto-Generation:**
```python
if new_status in ['confirmed', 'awaiting_payment'] and not order.get('invoice_number'):
    success, invoice_number = db.generate_invoice_number(order_number)
    pdf_success, pdf_result = generate_invoice_pdf(order, customer, order_items, app.config)
```

**Logo Embedding in Emails:**
```python
def get_logo_embedded():
    logo_path = os.path.join('static', 'images', 'logo', 'SSG-Logo.png')
    with open(logo_path, 'rb') as f:
        logo_data = base64.b64encode(f.read()).decode()
        return f'data:image/png;base64,{logo_data}'
```

#### Git Commits
```
7cc7594 - Complete Phase A-C: Order Management, Quote-to-Order, Invoice System
1229fab - Add reportlab to requirements.txt for invoice PDF generation
```

### Current Status
**E-Commerce System: Production Ready** ✅
- ✅ Phase A: Enhanced Order Status Flow
- ✅ Phase B: Quote-to-Order Conversion
- ✅ Phase C: Invoice System
- ✅ User Authentication & Accounts
- ✅ Shopping Cart
- ✅ Checkout with Multiple Shipping Options
- ✅ Order Management
- ✅ Email Notifications

**Next Phase:**
- 💳 Payment Gateway Integration (Yoco/PayFast)
- 📦 Advanced Shipping Integration
- 📊 Analytics Dashboard
- 🎨 Enhanced Product Management

---

## Session Summary (2025-10-28 - Complete Phase 2-4: User Auth, Cart, Checkout, Orders)

### 🎯 MAJOR MILESTONE: Full E-Commerce Implementation

**Status:** Phases 2, 3, 4 - 100% Complete ✅

[Previous session summaries preserved below...]

---

## Session Summary (2025-10-26 - Cookie & Clay Cutters Admin System - CHECKPOINT)

### 🎯 MAJOR MILESTONE: Complete Admin System for Cookie & Clay Cutters

**Status:** Admin Interface 100% Complete - Ready for Frontend Integration

#### What Was Built - Database Layer
1. **Four New Database Tables Created**
   - `cutter_categories` - Stores categories (Cookie, Clay, Imprint, etc.)
   - `cutter_types` - Stores types (Animals, Flora, Shapes, Characters, Holiday, Letters)
   - `cutter_items` - Stores individual items with all metadata and unique numbering
   - `cutter_item_photos` - Stores multiple photos per item with main photo designation

2. **Complete CRUD Operations (src/database.py)**
   - **Categories:** Add, Get All, Get Single, Update, Delete (with protection)
   - **Types:** Add, Get All, Get Single, Update, Delete (with protection)
   - **Items:** Add, Get All (with filters), Get Single, Update, Delete (soft delete), **Copy Item**
   - **Photos:** Add, Get All for Item, Set Main, Delete
   - **Helpers:** `generate_item_number()`, `get_item_upload_path()`

3. **Unique Item Numbering System**
   - Format: `CC_<CATEGORY>_NNNN`
   - Examples: `CC_COOKIE_0001`, `CC_CLAY_0001`, `CC_IMPRINT_0001`
   - Auto-increments per category
   - Category name extracted and cleaned for prefix

4. **Organized File Storage Structure**
   ```
   static/uploads/cutter_items/
     Cookie/              # Category folder
       Animals/           # Type folder
         CC_COOKIE_0001/  # Item folder
           photos...
   ```

#### What Was Built - Admin Interface
1. **Category Management Page** (`admin-cutter-categories.html`)
2. **Type Management Page** (`admin-cutter-types.html`)
3. **Items List Page** (`admin-cutter-items.html`)
4. **Item Form Page** (`admin-cutter-item-form.html`)

**Status:** Admin System 100% Complete ✅

---

## Session Summary (2025-10-26 - Complete 3D Printing Quote System)

### Completed Features
**All 3D Printing Request Forms - FULLY FUNCTIONAL** ✨

1. **Cake Topper Quote Request System**
2. **3D Print Service Request System**
3. **Unified Admin Panel**
4. **Email Notification System Expansion**

**Current Status:** 3D Printing Quote System - 100% Complete

---

## Session Summary (2025-10-25 - Evening Session)

### Completed Features
**Custom Design Quote Request System - FULLY FUNCTIONAL**

1. **Backend Infrastructure**
2. **Quote Request Form**
3. **Email Notification System**
4. **Admin Panel for Quotes**
5. **Network Access Configuration**

**Status:** Custom Design Quote System - 100% Complete

---

## Session Summary (2025-10-27 - Cookie & Clay Cutters Shop Integration)

### 🎯 MAJOR MILESTONE: Shop Frontend Fully Integrated with Database

**Status:** Admin & Shop 100% Complete ✅

1. **Frontend Shop Database Integration**
2. **Product Display Updates**
3. **Product Detail Modal**
4. **Shop Functionality**
5. **Admin UI Improvements**

---

## Session Summary (2025-10-27 - Git Setup & Pre-Deployment)

### 🚀 MILESTONE: Version Control & Production Readiness

**Status:** Ready for Deployment ✅

---

## Session Summary (2025-10-28 - Fix Production Email Issue)

### 🐛 PROBLEM SOLVED: Email Not Sending from Afrihost

**Status:** Email System Fixed - Using Afrihost SMTP ✅

---

## Session Summary (2025-10-28 - Documentation Reorganization)

### 📚 COMPLETED: Documentation Cleanup & Organization

**Status:** Documentation Organized ✅

---

#### Bug Fixes & Mobile Improvements (Session Continued)
1. **Admin Session Persistence**
   - Set `session.permanent = True` in admin login
   - Added `PERMANENT_SESSION_LIFETIME` (7 days)
   - Fixed mobile admin logout issues

2. **Unified Admin Authentication**
   - Updated `@admin_required` decorator to accept database users with `is_admin` flag
   - Allows admin users to log in at `/login` instead of separate `/admin/login`
   - Created `set_admin.py` script for easy admin management
   - Set mariuserasmus69@gmail.com as admin

3. **Mobile UI Improvements**
   - Admin orders page: Dropdown filter menu on mobile instead of wrapping buttons
   - Shop product cards: Icon-only action buttons side-by-side on mobile
   - Shop filters: Collapsible section on mobile (collapsed by default)
   - Significantly improved mobile browsing experience

4. **Admin UI Polish**
   - Fixed order detail card headers (changed from cyan to blue)
   - Made email invoice button consistent (outline style)
   - Fixed quote status to include "Converted to Sale" option

#### Git Commits
```
f920b40 - Fix admin session persistence on mobile devices
5397055 - Allow admin users to access admin panel via user login
472b9d7 - Fix mobile horizontal scroll on admin orders page
3bcb0ad - Improve mobile UI: Dropdown filters, icon buttons, and collapsible filters
ba11c83 - Fix quote status display: Add 'Converted to Sale' option
0dcb81d - Fix admin order detail page styling
```

**Last Updated:** 2025-10-31
**Status:** ✅ Phase A-C Complete + Mobile Optimizations + Quote System Enhancements + Email Attachments + User Management Complete (Phase 1-3)
**Next:** Payment Gateway Integration

---

## Session Summary (2025-10-31 - User Management Phase 3: Admin Actions)

### ⚡ NEW FEATURE: Complete Admin User Management Actions

**Status:** Complete ✅

#### Features Added

**Admin Actions Available from User Detail Modal:**

1. **✏️ Edit User** - Update user profile (name, email, phone)
2. **🔑 Reset Password** - Generate random temporary password & email it to user
3. **⚡ Toggle Status** - Activate/deactivate user account (prevents login when inactive)
4. **🛡️ Toggle Admin** - Grant/revoke admin privileges
5. **🗑️ Delete User** - Permanently remove user from database (with confirmation)

#### Technical Implementation

**Database Methods (src/database.py):**
```python
def admin_reset_user_password(user_id):
    # Generates 8-character random password
    # Hashes with bcrypt, updates database
    # Returns (success, message, temp_password)

def admin_toggle_user_status(user_id):
    # Toggles is_active between True/False
    # Returns (success, message, new_status)

def admin_toggle_admin_status(user_id):
    # Toggles is_admin between True/False
    # Returns (success, message, new_status)

def admin_delete_user(user_id):
    # Deletes user from database
    # Returns (success, message)
```

**Routes (app.py):**
```python
@app.route('/admin/users/<int:user_id>/edit', methods=['POST'])
@app.route('/admin/users/<int:user_id>/reset-password', methods=['POST'])
@app.route('/admin/users/<int:user_id>/toggle-status', methods=['POST'])
@app.route('/admin/users/<int:user_id>/toggle-admin', methods=['POST'])
@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
```

**UI (templates/admin-users.html):**
- Admin Actions section in user detail modal
- Edit modal for updating user info
- Confirmation dialogs for destructive actions
- Dynamic button text (Activate/Deactivate, Grant/Revoke)

#### Feature Details

**1. Edit User**
- Opens modal with pre-filled form
- Fields: Name, Email, Phone
- Email change updates login credentials
- Warning message about email changes

**2. Reset Password**
- Generates secure 8-character temporary password
- Automatically emails user with new password
- Includes instructions to change password
- Shows temp password in flash message if email fails

**3. Toggle Status (Activate/Deactivate)**
- Active users can log in
- Inactive users cannot log in
- Button changes color/text based on current status
- Red "Deactivate" when active, Green "Activate" when inactive

**4. Toggle Admin**
- Grant admin privileges to regular users
- Revoke admin privileges from admin users
- Yellow "Grant Admin" for regular users
- Gray "Revoke Admin" for admin users

**5. Delete User**
- Permanent deletion from database
- Double confirmation required
- Warning message: "This action CANNOT be undone!"
- Success message shows deleted user's name

#### Safety Features

**Confirmations:**
- ✅ Password reset: "Reset password for [name]? A temporary password will be emailed to them."
- ✅ Delete: "Are you sure you want to DELETE [name]? This action CANNOT be undone!"

**Email Notifications:**
- ✅ Password reset emails sent automatically
- ✅ Professional branding with Snow Spoiled Gifts template
- ✅ Clear instructions for user
- ✅ Fallback if email fails (shows temp password in flash message)

**Access Control:**
- ✅ All routes protected by `@admin_required` decorator
- ✅ Only admins can access these functions

#### Files Modified
- `src/database.py` - Added 4 admin methods (lines 2136-2287)
- `app.py` - Added 5 admin routes (lines 954-1063)
- `templates/admin-users.html` - Added action buttons & edit modal (lines 257-348)

#### User Experience

**Admin Workflow:**
1. Navigate to Users page
2. Click eye icon on any user
3. View user details in modal
4. Scroll to "Admin Actions" section
5. Choose action:
   - Edit → Opens edit modal, fill form, save
   - Reset Password → Confirm, password emailed
   - Toggle Status → Instant toggle, no confirmation
   - Toggle Admin → Instant toggle, no confirmation
   - Delete → Confirm, user removed
6. Flash message confirms action
7. Page refreshes with updated data

**Password Reset Email:**
```
Subject: Your Password Has Been Reset

Your password has been reset by an administrator.

Your temporary password is: Ab12Cd34

Please log in with this temporary password and change it
immediately in your account settings.

For security reasons, we recommend using a strong password
with at least 6 characters.
```

#### Complete User Management System Summary

**Phase 1:** Users can change their own passwords ✅
**Phase 2:** Admins can view all users with statistics ✅
**Phase 3:** Admins can manage users (edit, reset, toggle, delete) ✅

**Total Features:**
- User self-service password change
- Admin user list with search & stats
- Admin edit user profile
- Admin reset user password
- Admin activate/deactivate users
- Admin grant/revoke admin privileges
- Admin delete users
- Email notifications for password resets

---

## Session Summary (2025-10-31 - User Management Phase 2: Admin User List)

### 👥 NEW FEATURE: Admin User Management Dashboard

**Status:** Complete ✅

#### Feature Added

**Admin Users Page (`/admin/users`)**
   - **What:** Comprehensive admin dashboard to view all registered users
   - **Access:** Available to admin users via navbar → Users
   - **Statistics:** Total users, active users, admins, users with orders, new users (30 days), inactive users
   - **Search:** Real-time search by name or email
   - **Details:** View full user profile with order statistics in modal

#### Technical Implementation

**Database Methods (src/database.py):**
```python
def get_all_users(self):
    """Get all users with order statistics (order count, total spent)"""
    # LEFT JOIN with orders table to include order stats

def get_user_statistics(self):
    """Get user statistics for admin dashboard"""
    # Returns statistics dictionary
```

**Route (app.py):**
```python
@app.route('/admin/users')
@admin_required
def admin_users():
    # Fetches all users and statistics, renders template
```

#### Features & Data Displayed

**User List Table Columns:**
1. ID, Name (with ADMIN badge), Email, Phone
2. Registered date, Order count, Total spent
3. Status (Active/Inactive), Actions (view details)

**Statistics Dashboard:**
- 📊 Total Users, ✅ Active, 🛡️ Admins
- 🛒 Users with Orders, ➕ New (30d), ❌ Inactive

**User Detail Modal:**
- Personal information, Account status
- Order statistics (count, total, average)
- Note: Phase 3 actions coming soon

#### Files Modified/Created
- `src/database.py` - Added `get_all_users()` and `get_user_statistics()` (lines 1920-2028)
- `app.py` - Added `/admin/users` route (lines 938-951)
- `templates/admin-users.html` - Created complete user management page
- `templates/base.html` - Added "Users" link to admin navigation (line 66)

#### What's Next (Phase 3)
Phase 3 will add admin actions: edit user, reset password, activate/deactivate, toggle admin, delete, email directly.

---

## Session Summary (2025-10-31 - User Management Phase 1: User Password Change)

### 🔐 NEW FEATURE: Users Can Change Their Own Passwords

**Status:** Complete ✅

#### Feature Added

**Self-Service Password Change**
   - **What:** Registered users can now change their own passwords from their account page
   - **Security:** Requires current password for verification before allowing change
   - **Location:** Account Page → Change Password section
   - **Validation:** Minimum 6 characters, must confirm new password

#### Technical Implementation

**Database Method (src/database.py):**
```python
def change_password(self, user_id, current_password, new_password):
    """
    Change user password after verifying current password
    - Verifies current password using bcrypt
    - Hashes new password with bcrypt
    - Updates password_hash in database
    """
```

**Form Class (src/forms.py):**
```python
class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[EqualTo('new_password')])
```

**Route (app.py):**
```python
@app.route('/change-password', methods=['POST'])
@login_required
def change_password():
    # Validates form, verifies current password, updates to new password
```

**UI (templates/account.html):**
- Added "Change Password" card with yellow/warning header for visibility
- Three fields: Current Password, New Password, Confirm New Password
- Security tip displayed below form
- Success/error flash messages on submission

#### How It Works
1. **User Navigates:** Account page → Change Password section (left column, below profile)
2. **Enter Passwords:** Current password + new password + confirmation
3. **Validation:**
   - Checks current password is correct
   - Verifies new password is at least 6 characters
   - Ensures new password matches confirmation
4. **Success:** Password updated, user notified via flash message
5. **Security:** User can continue using their account with new password immediately

#### Files Modified
- `src/database.py` - Added `change_password()` method (lines 1980-2024)
- `src/forms.py` - Added `ChangePasswordForm` class (lines 217-241)
- `app.py` - Added `change_password` route and updated account route (lines 256, 292-314)
- `templates/account.html` - Added password change card UI (lines 71-122)

#### Security Features
- ✅ Current password required (prevents unauthorized changes if someone accesses logged-in session)
- ✅ Password confirmation required (prevents typos)
- ✅ Bcrypt hashing (secure password storage)
- ✅ Minimum 6 character requirement
- ✅ Login required decorator (must be authenticated)

---

## Session Summary (2025-10-31 - Quote System: View Uploaded Images & Fix Email Recipients)

### 🐛 BUG FIXES: Quote Request Image Viewing & Email Configuration

**Status:** Complete ✅

#### Issues Resolved

1. **Quote Request Images Not Viewable**
   - **Problem:** Uploaded reference images were saved to disk but admin panel only showed filenames with no way to view/download them
   - **Location:** `static/uploads/quote_references/`, `static/uploads/cake_topper_references/`
   - **Solution:** Added clickable download/view buttons for each uploaded file in admin quotes detail modal
   - **Files Modified:** `templates/admin-quotes.html` (lines 262-276 for Custom Design, lines 312-326 for Cake Topper)

2. **Missing Email Recipient for Quote Notifications**
   - **Problem:** Quote request emails were only being sent to `mariuserasmus69@gmail.com` and `elmienerasmus@gmail.com`
   - **Missing:** `info@snowspoiledgifts.co.za` was not receiving quote notifications
   - **Solution:** Added `NOTIFICATION_RECIPIENTS` to `.env` file with all three email addresses
   - **Configuration:** `.env` line 27: `NOTIFICATION_RECIPIENTS=info@snowspoiledgifts.co.za,elmienerasmus@gmail.com,mariuserasmus69@gmail.com`

#### Technical Implementation

**Image Viewing in Admin Panel:**
```html
{% if quote.reference_images %}
<div class="mb-3">
    <h6><i class="fas fa-image"></i> Reference Images</h6>
    <p><span class="badge bg-info">{{ quote.reference_images.split(',') | length }} file(s) uploaded</span></p>
    <div class="uploaded-files-list">
        {% for filename in quote.reference_images.split(',') %}
        <div class="mb-2">
            <a href="{{ url_for('static', filename='uploads/quote_references/' + filename) }}" target="_blank" class="btn btn-sm btn-outline-primary">
                <i class="fas fa-download"></i> {{ filename }}
            </a>
        </div>
        {% endfor %}
    </div>
</div>
{% endif %}
```

**Email Configuration:**
- Email notification system uses `config['NOTIFICATION_RECIPIENTS']` from `src/email_utils.py`
- All quote types (Custom Design, Cake Topper, Print Service) now send to all three addresses
- Primary recipient shown in "To:" field, additional recipients in "Cc:" field

#### Files Modified
- `templates/admin-quotes.html` - Added download buttons for uploaded images (2 sections)
- `.env` - Added NOTIFICATION_RECIPIENTS with all three email addresses
- `src/config.py` - Already configured to read from .env (lines 52-55)

#### How It Works Now
1. **Viewing Images:** Admin can click on any filename in the quote detail modal to view/download the image in a new tab
2. **Email Distribution:** All new quote requests automatically send notification emails to:
   - info@snowspoiledgifts.co.za (Primary business email)
   - elmienerasmus@gmail.com (Primary admin)
   - mariuserasmus69@gmail.com (Secondary admin)

---

## Session Summary (2025-10-31 - Enhancement: Email Customers with File Attachments)

### ✨ NEW FEATURE: Attach Files to Customer Emails

**Status:** Complete ✅

#### Feature Added

**Email Attachments for Quote Responses**
   - **What:** Admin can now attach files (images, PDFs, documents, STL files) when emailing customers from the quotes admin panel
   - **Use Case:** Send design mockups, quotes in PDF format, reference images, STL files, or any other files to customers
   - **Location:** Admin Panel → Quotes → View Quote → Email Customer button
   - **Supported File Types:** Images (JPG, PNG, etc.), PDFs, Documents (DOC, DOCX, TXT), STL files, and more
   - **Limit:** Multiple files can be attached (max 10MB per file recommended)

#### Technical Implementation

**Frontend Changes (templates/admin-quotes.html):**
```html
<!-- Added file upload field to email modal -->
<form method="POST" enctype="multipart/form-data">
    <div class="mb-3">
        <label for="email_attachments">
            <i class="fas fa-paperclip"></i> Attach Files (optional):
        </label>
        <input type="file" class="form-control" name="email_attachments" multiple
               accept="image/*,.pdf,.doc,.docx,.txt,.stl">
    </div>
</form>
```

**Backend Changes (app.py - email_customer route):**
```python
# Handle file attachments
attachments = []
uploaded_files = request.files.getlist('email_attachments')
if uploaded_files:
    for file in uploaded_files:
        if file and file.filename:
            file_data = file.read()
            mime_type, _ = mimetypes.guess_type(file.filename)
            attachments.append({
                'filename': file.filename,
                'data': file_data,
                'mime_type': mime_type
            })

# Pass attachments to email function
send_admin_reply_to_customer(config, email, name, subject, message, attachments=attachments)
```

**Email Utility Enhancement (src/email_utils.py):**
- Updated `send_admin_reply_to_customer()` to accept optional `attachments` parameter
- Uses `MIMEMultipart('mixed')` when attachments present for proper email structure
- Automatically detects MIME types and uses appropriate handlers:
  - `MIMEImage` for image files
  - `MIMEApplication` for other file types (PDFs, documents, etc.)
- Maintains professional email branding with attachments included

#### Files Modified
- `templates/admin-quotes.html` - Added file upload field to email modal (line 428, 445-452)
- `app.py` - Updated email_customer route to handle file attachments (lines 1380-1410)
- `src/email_utils.py` - Enhanced send_admin_reply_to_customer with attachment support (lines 1016-1162)

#### How It Works
1. **Admin Panel:** Navigate to Quotes → Click eye icon on any quote → Click "Email Customer"
2. **Compose Email:** Write subject and message as usual
3. **Attach Files:** Click "Choose Files" button to select one or more files to attach
4. **Send:** Email is sent with professional Snow Spoiled Gifts branding + attachments
5. **Customer Receives:** Customer gets email with all attachments ready to download

#### Benefits
- **Send Design Mockups:** Attach preview images of custom designs for customer approval
- **Professional Quotes:** Attach PDF quotes with pricing and terms
- **Reference Material:** Send inspiration images or design references
- **3D Files:** Share STL files for customer review before printing
- **Documentation:** Attach care instructions, warranty info, or other documents

---
