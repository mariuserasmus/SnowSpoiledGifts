# Admin Interface Consistency Guidelines

## Purpose
This document defines the standard patterns and conventions for all admin interfaces across product lines. **All new product lines MUST follow these guidelines** to maintain consistency and usability.

---

## Reference Implementation
**Primary Template**: Cookie & Clay Cutters admin pages
- `templates/admin-cutter-categories.html`
- `templates/admin-cutter-types.html`
- `templates/admin-cutter-items.html`

**Secondary Template**: Candles & Soaps admin pages (updated to match)
- `templates/admin-candles-soaps-categories.html`
- `templates/admin-candles-soaps-products.html`

---

## 1. Terminology Standards

### Use "Items" NOT "Products"
✅ **Correct**:
- "Manage Items"
- "Add New Item"
- "Back to Items"
- "No items found"

❌ **Incorrect**:
- "Manage Products"
- "Add Product"
- "Back to Products"
- "No products found"

### Use "Categories" Consistently
- Always plural in navigation: "Manage Categories"
- Singular in forms: "Add New Category", "Edit Category"

---

## 2. Page Structure Pattern

### Categories Management Page

```html
{% extends "base.html" %}

{% block title %}[Product Line] Categories - Admin - {{ config.SITE_NAME }}{% endblock %}

{% block content %}
<section class="admin-section">
    <div class="container-fluid">
        <!-- HEADER ROW -->
        <div class="row mb-4">
            <div class="col">
                <div class="d-flex justify-content-between align-items-center">
                    <h2><i class="fas fa-[icon]"></i> [Product Line] Categories</h2>
                    <div>
                        <a href="{{ url_for('[product_line]_items') }}" class="btn btn-outline-[color] me-2">
                            <i class="fas fa-[icon]"></i> Manage Items
                        </a>
                        <a href="{{ url_for('admin_signups') }}" class="btn btn-outline-secondary me-2">
                            <i class="fas fa-arrow-left"></i> Back to Dashboard
                        </a>
                        <a href="{{ url_for('logout') }}" class="btn btn-outline-secondary">
                            <i class="fas fa-sign-out-alt"></i> Logout
                        </a>
                    </div>
                </div>
            </div>
        </div>

        <!-- STATS ROW -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="stats-card [gradient-class]">
                    <div class="stats-icon">
                        <i class="fas fa-th-large"></i>
                    </div>
                    <div class="stats-content">
                        <h3>{{ categories|length }}</h3>
                        <p>Total Categories</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- ADD NEW CATEGORY CARD (INLINE FORM - NOT MODAL!) -->
        <div class="row mb-4">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header [bg-gradient-style]">
                        <h5 class="mb-0"><i class="fas fa-plus"></i> Add New Category</h5>
                    </div>
                    <div class="card-body">
                        <form method="POST" action="{{ url_for('[add_category_route]') }}">
                            <div class="mb-3">
                                <label class="form-label">Category Name <span class="text-danger">*</span></label>
                                <input type="text" name="name" class="form-control" required placeholder="e.g., [examples]">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Description</label>
                                <textarea name="description" class="form-control" rows="2" placeholder="Optional description"></textarea>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Display Order</label>
                                <input type="number" name="display_order" class="form-control" value="0" min="0">
                                <small class="form-text text-muted">Lower numbers appear first</small>
                            </div>
                            <button type="submit" class="btn btn-success">
                                <i class="fas fa-plus"></i> Add Category
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div>

        <!-- CATEGORIES LIST -->
        <div class="row">
            <div class="col">
                <div class="table-card">
                    <h5 class="mb-3"><i class="fas fa-list"></i> Existing Categories</h5>
                    <div class="table-responsive">
                        <table class="table table-hover">
                            <!-- Table content -->
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>
```

**CRITICAL**:
- ✅ Use **inline form** for adding new categories
- ❌ Do NOT use modals/popups that require clicking "Add Category" button
- ✅ Form must be visible immediately on page load

---

## 3. Action Buttons Pattern

### Icon-Only Style (Required)

✅ **Correct Pattern**:
```html
<!-- Edit Button -->
<a class="btn btn-link text-warning p-0 me-3"
   href="{{ url_for('edit_route', id=item.id) }}"
   title="Edit [Item/Category]"
   style="text-decoration: none; cursor: pointer;">
    <i class="fas fa-edit fa-lg"></i>
</a>

<!-- Delete Button -->
<form method="POST" action="{{ url_for('delete_route', id=item.id) }}"
      style="display: inline;"
      onsubmit="return confirm('Are you sure?');">
    <button type="submit"
            class="btn btn-link text-danger p-0"
            title="Delete [Item/Category]"
            style="text-decoration: none; cursor: pointer;">
        <i class="fas fa-trash fa-lg"></i>
    </button>
</form>

<!-- Stock/Adjustment Button (if applicable) -->
<button type="button"
        class="btn btn-link text-info p-0 me-3"
        title="Adjust Stock"
        onclick="showStockModal(...)"
        style="text-decoration: none; cursor: pointer;">
    <i class="fas fa-boxes fa-lg"></i>
</button>
```

❌ **Incorrect Pattern** (Do NOT use):
```html
<!-- NO TEXT LABELS! -->
<button class="btn btn-outline-primary">
    <i class="fas fa-edit"></i> Edit
</button>

<button class="btn btn-sm btn-outline-danger">
    <i class="fas fa-trash"></i> Delete
</button>
```

**Key Attributes**:
- `btn btn-link` (not btn-outline-*)
- `text-warning` for Edit
- `text-danger` for Delete
- `text-info` for Stock/Adjustments
- `p-0` (no padding)
- `me-3` (margin-end spacing except last button)
- `fa-lg` for larger icons
- `title` attribute for tooltips
- `style="text-decoration: none; cursor: pointer;"`

---

## 4. Color Schemes by Product Line

### Cookie & Clay Cutters
- Primary: Blue (`#2563eb`)
- Button: `btn-outline-info`
- Icon: `fa-cookie` or `fa-cube`

### Candles & Soaps
- Primary: Purple (`#9333ea`)
- Gradient: `linear-gradient(135deg, #9333ea 0%, #c084fc 100%)`
- Button: `btn-outline-purple`
- Icon: `fa-spa`

### Future Product Lines
Pick a unique color that:
1. Doesn't conflict with existing product lines
2. Has good contrast in both light and dark modes
3. Use consistent gradient pattern: `linear-gradient(135deg, [color-dark] 0%, [color-light] 100%)`

---

## 5. Navigation Integration

### Main Navigation (base.html)

#### Admin Menu
```html
<li class="nav-item dropdown">
    <a class="nav-link dropdown-toggle" href="#" id="manageItemsDropdown"
       role="button" data-bs-toggle="dropdown">
        <i class="fas fa-boxes"></i> Manage Items
    </a>
    <ul class="dropdown-menu" aria-labelledby="manageItemsDropdown">
        <li><a class="dropdown-item" href="{{ url_for('admin_cutter_items') }}">
            <i class="fas fa-cube"></i> 3D Printing
        </a></li>
        <li><a class="dropdown-item" href="{{ url_for('admin_candles_soaps_products') }}">
            <i class="fas fa-spa"></i> Candles & Soaps
        </a></li>
        <!-- ADD NEW PRODUCT LINE HERE -->
    </ul>
</li>
```

#### Customer Menu
```html
<li class="nav-item dropdown">
    <a class="nav-link dropdown-toggle" href="#" id="shopDropdown"
       role="button" data-bs-toggle="dropdown">
        <i class="fas fa-store"></i> Shop
    </a>
    <ul class="dropdown-menu" aria-labelledby="shopDropdown">
        <li><a class="dropdown-item" href="{{ url_for('printing_3d') }}">
            <i class="fas fa-cube"></i> 3D Printing
        </a></li>
        <li><a class="dropdown-item" href="{{ url_for('candles_soaps') }}">
            <i class="fas fa-spa"></i> Candles & Soaps
        </a></li>
        <!-- ADD NEW PRODUCT LINE HERE -->
    </ul>
</li>
```

**Rules**:
- Each product line gets ONE entry in dropdown
- No separate "Categories" and "Products" links
- Use product line name, not generic "Products"

---

## 6. Database Pattern

### Required Tables (Separate for Each Product Line)

```sql
-- Categories
CREATE TABLE IF NOT EXISTS [product_line]_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    display_order INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products/Items
CREATE TABLE IF NOT EXISTS [product_line]_products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    category_id INTEGER NOT NULL,
    price REAL NOT NULL,
    stock_quantity INTEGER DEFAULT 0,
    low_stock_threshold INTEGER DEFAULT 5,
    is_active INTEGER DEFAULT 1,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES [product_line]_categories(id),
    -- ADD PRODUCT-SPECIFIC FIELDS HERE
);

-- Product Photos
CREATE TABLE IF NOT EXISTS [product_line]_product_photos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    photo_path TEXT NOT NULL,
    is_main INTEGER DEFAULT 0,
    uploaded_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES [product_line]_products(id) ON DELETE CASCADE
);

-- Shopping Cart
CREATE TABLE IF NOT EXISTS [product_line]_cart_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    session_id TEXT,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (product_id) REFERENCES [product_line]_products(id)
);

-- Stock History (Audit Trail)
CREATE TABLE IF NOT EXISTS [product_line]_stock_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    change_amount INTEGER NOT NULL,
    reason TEXT,
    previous_quantity INTEGER,
    new_quantity INTEGER,
    order_id INTEGER,
    created_by TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES [product_line]_products(id),
    FOREIGN KEY (order_id) REFERENCES orders(id)
);
```

**Rules**:
- Each product line has its own table prefix
- Stock tracking is mandatory
- Audit trail (stock_history) is mandatory
- Photo support is standard

---

## 7. Form Validation & UX

### Required Fields
- Mark with `<span class="text-danger">*</span>`
- Use HTML5 `required` attribute
- Provide helpful placeholders

### Input Types
- **Text**: Name fields
- **Textarea**: Descriptions (2-4 rows)
- **Number**: Price, stock, display order
- **Select**: Categories, status (active/inactive)
- **File**: Photos (accept="image/jpeg,image/jpg,image/png,image/webp")

### Success/Error Messages
- Use Flask flash messages
- Green for success
- Red for errors
- Auto-dismiss after 5 seconds

---

## 8. CSS Styling Standards

### CRITICAL: Proper CSS Variable Usage

All admin pages MUST use CSS variables for colors to ensure proper light/dark mode support:

```css
<style>
.admin-section {
    padding: 100px 20px 60px;
    min-height: 100vh;
    background: var(--bg-color);  /* NOT a gradient with undefined variables! */
}

/* Regular cards (forms, tables, etc.) */
.card:not(.stats-card) {
    background: var(--card-bg) !important;
    color: var(--text-color) !important;
    border-radius: 15px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    border: none;
}

.card:not(.stats-card) .card-body {
    background: var(--card-bg) !important;
    color: var(--text-color) !important;
}

/* Stats cards (colored backgrounds) */
.stats-card {
    border-radius: 15px;
    padding: 25px;
    color: white !important;  /* Always white on colored backgrounds */
    display: flex;
    align-items: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    margin-bottom: 20px;
}

.stats-card * {
    color: white !important;  /* Force all children to be white */
}

/* Form labels and text */
.form-label,
label {
    color: var(--text-color) !important;
}

.table-card {
    background: var(--card-bg) !important;
    border-radius: 15px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    padding: 30px;
    margin-bottom: 30px;
    color: var(--text-color) !important;
}

/* Product-specific gradient for card headers */
.card-header {
    background: linear-gradient(135deg, [product-color-dark] 0%, [product-color-light] 100%);
    color: white;
    border-radius: 15px 15px 0 0 !important;
    padding: 15px 20px;
}

/* Dark mode is handled automatically by global style.css */
/* Do NOT add [data-bs-theme="dark"] selectors - use [data-theme="dark"] if needed */
</style>
```

### Available CSS Variables (from style.css)

**Light Mode:**
- `--card-bg: #ffffff` (white)
- `--text-color: #1f2937` (dark gray)
- `--bg-color: #ffffff` (white)
- `--muted-text: #6b7280` (gray)

**Dark Mode:**
- `--card-bg: #1e293b` (dark slate)
- `--text-color: #e2e8f0` (light gray)
- `--bg-color: #0f172a` (very dark)
- `--muted-text: #94a3b8` (light gray)

### Common Mistakes to Avoid

❌ **WRONG - Using undefined variables:**
```css
.admin-section {
    background: linear-gradient(135deg, var(--background-color) 0%, var(--accent-color) 100%);
}
```

❌ **WRONG - Hardcoded colors:**
```css
.card {
    background: white;
    color: #212529;
}
```

❌ **WRONG - Wrong dark mode selector:**
```css
[data-bs-theme="dark"] .card {
    background-color: #2b3035;
}
```

❌ **WRONG - Stats cards inherit text color:**
```css
.stats-card {
    color: var(--text-color);  /* Will be dark gray in light mode! */
}
```

✅ **CORRECT - Use proper CSS variables:**
```css
.admin-section {
    background: var(--bg-color);
}

.card:not(.stats-card) {
    background: var(--card-bg) !important;
    color: var(--text-color) !important;
}

.stats-card {
    color: white !important;  /* Always white on colored backgrounds */
}
```

## 9. Dark Mode Support

Dark mode is handled automatically by the global `style.css` file which uses `[data-theme="dark"]` selector (NOT `data-bs-theme`).

**DO NOT** add dark mode CSS in your templates. The CSS variables automatically handle light/dark mode:
- Using `var(--card-bg)` and `var(--text-color)` means your templates work in both modes automatically
- The global `style.css` (lines 1074-1094) handles dark mode overrides

Simply add this comment at the end of your `<style>` block:
```css
/* Dark mode handled by global style.css with [data-theme="dark"] */
</style>
```

---

## 10. Checklist for New Product Line

### Before Starting
- [ ] Choose unique icon from Font Awesome
- [ ] Choose unique color scheme
- [ ] Define product-specific fields needed
- [ ] Review Cookie & Clay Cutters templates

### Database Setup
- [ ] Create all 5 required tables with product line prefix
- [ ] Add database methods for CRUD operations
- [ ] Add stock management methods
- [ ] Add photo management methods
- [ ] Test all database methods

### Admin Interface
- [ ] Create categories management page with **inline form**
- [ ] Create items list page
- [ ] Create item form page (add/edit)
- [ ] Use **icon-only action buttons** everywhere
- [ ] Use "Items" terminology (not "Products")
- [ ] Add navigation links to base.html dropdowns
- [ ] Test all CRUD operations
- [ ] Verify dark mode support

### Frontend
- [ ] Create shop page for customers
- [ ] Add category filtering
- [ ] Add product detail view
- [ ] Add to cart functionality
- [ ] Update home page category card
- [ ] Change badge from "Coming Soon" to "SHOP OPEN!"

### Integration
- [ ] Update order creation to handle new cart table
- [ ] Update stock deduction on order placement
- [ ] Test complete purchase flow
- [ ] Test stock tracking and history

---

## 11. Common Mistakes to Avoid

❌ **Using Modals for Add Forms**
- Modals require extra click, hidden until button clicked
- ✅ Use inline forms visible on page load

❌ **Inconsistent Button Styles**
- Don't mix btn-outline-* with btn-link
- ✅ Always use btn-link with color classes for action buttons

❌ **Text Labels on Action Buttons**
- Takes up space, looks cluttered
- ✅ Icon-only with tooltips

❌ **Using "Products" Instead of "Items"**
- Inconsistent across pages
- ✅ Always use "Items" terminology

❌ **Separate Categories/Products Links**
- Creates navigation clutter
- ✅ Single product line entry, access categories from items page

❌ **Adding Unnecessary Dark Mode CSS**
- Adding `[data-bs-theme="dark"]` or `[data-theme="dark"]` selectors manually
- ✅ Use CSS variables - dark mode is automatic

❌ **Shared Product Tables**
- Product lines interfere with each other
- ✅ Each product line has completely separate tables

❌ **Using Undefined CSS Variables**
- `var(--background-color)` and `var(--accent-color)` don't exist
- ✅ Use `var(--bg-color)`, `var(--card-bg)`, `var(--text-color)`

❌ **Stats Cards with Variable Text Color**
- Stats cards have colored backgrounds, need white text always
- ✅ Use `.stats-card { color: white !important; }` and `.stats-card * { color: white !important; }`

❌ **Wrong Dark Mode Selector**
- Using `[data-bs-theme="dark"]` which doesn't exist on this site
- ✅ Site uses `[data-theme="dark"]`, but you should rely on CSS variables instead

---

## 12. Testing Checklist

Before considering a product line "complete":

### Admin Interface
- [ ] Add category (inline form works)
- [ ] Edit category (modal works)
- [ ] Delete category (protection if items exist)
- [ ] Add item
- [ ] Edit item
- [ ] Delete item
- [ ] Upload photo
- [ ] Set main photo
- [ ] Delete photo
- [ ] Adjust stock levels
- [ ] View stock history
- [ ] All action buttons are icon-only
- [ ] Dark mode looks good

### Customer Interface
- [ ] Browse items
- [ ] Filter by category
- [ ] View item details
- [ ] Add to cart
- [ ] View cart badge updates
- [ ] Checkout process
- [ ] Order confirmation shows items

### Integration
- [ ] Stock deducts on order
- [ ] Stock history logs correctly
- [ ] Out-of-stock items hidden/marked
- [ ] Email confirmation includes items
- [ ] Admin can see orders with items

---

## 13. CRITICAL: Unified Shopping Cart Requirement

### NEVER Create Separate Cart Systems for Different Product Lines

**CRITICAL RULE:** The application MUST use ONE unified shopping cart for ALL product types.

**WRONG - Separate Cart Tables (DO NOT DO THIS!):**
```sql
CREATE TABLE cutter_cart_items (...)           -- For Cutters
CREATE TABLE candles_soaps_cart_items (...) -- For Candles & Soaps
CREATE TABLE future_product_cart_items (...) -- For Future Product Line
```

**CORRECT - Unified Cart Table:**
```sql
CREATE TABLE cart_items (
    id INTEGER PRIMARY KEY,
    session_id TEXT,
    user_id INTEGER,
    product_type TEXT NOT NULL,  -- 'cutter', 'candles_soaps', 'future_type'
    product_id INTEGER NOT NULL,
    quantity INTEGER,
    added_date TIMESTAMP
);
```

### Why This Matters for Admins:
- **Single checkout process** - customers buy from multiple product lines in one transaction
- **Unified order management** - admin sees all items in one order, not scattered across separate systems
- **Consistent stock tracking** - all stock is tracked in one place
- **Scalable architecture** - adding new product lines is simple, doesn't break existing code
- **No code duplication** - same cart functions work for all product types

### Implementation Requirements:

**When Adding a NEW Product Line:**
1. **DO NOT** create a new cart table (e.g., `new_product_cart_items`)
2. **DO NOT** create duplicate cart route handlers
3. **DO NOT** create separate cart JavaScript functions
4. **REUSE** the existing unified cart system entirely

**The cart routes and functions remain unchanged:**
```python
# These functions handle ALL product types automatically:
@app.route('/cart/add', methods=['POST'])
def add_to_cart():
    product_type = request.json.get('product_type')  # 'cutter', 'candles_soaps', etc.
    product_id = request.json.get('product_id')
    quantity = request.json.get('quantity', 1)
    # Single function handles all product types

@app.route('/cart')
def view_cart():
    # Shows items from ALL product types in one unified cart view
```

### Database Implications for Stock Tracking:

When admin adjusts stock, the unified cart system means:
- Stock deduction applies across all orders regardless of product type
- Audit trails track all stock changes in one `stock_history` table per product line
- Order fulfillment is simpler - all items in an order are together

### Admin Checklist for New Product Line:

**DO NOT:**
- Create `[new_product]_cart_items` table
- Create `add_[new_product]_to_cart()` function
- Modify cart route handlers
- Create separate cart view templates

**DO:**
- Add new product line tables (categories, products, photos, stock history)
- Add product to the existing unified cart using `product_type` field
- Reuse all existing cart routes and functions
- Test that items from new product line work in existing cart

---

## Version History
- **v1.0** (2025-01-11): Initial documentation based on Cookie & Clay Cutters and Candles & Soaps patterns
- **v1.1** (2025-11-02): Added CRITICAL unified cart requirement section

## Questions?
If you encounter a scenario not covered in these guidelines, refer to:
1. Cookie & Clay Cutters admin templates (primary reference)
2. Candles & Soaps admin templates (secondary reference)
3. Ask before deviating from established patterns
