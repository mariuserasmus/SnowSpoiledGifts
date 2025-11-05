# Shop Interface Consistency Guidelines

## Purpose
This document defines the standard patterns and conventions for all shop pages across product lines. **All new shop pages MUST follow these guidelines** to maintain consistency, usability, and accessibility.

---

## Reference Implementation
**Primary Template**: 3D Printing shop page
- `templates/3d_printing.html`

**Template Features**:
- Multi-section product catalog with category navigation
- Product filtering and search functionality
- Product grid with cards and image carousels
- Add to cart with AJAX and toast notifications
- Product detail modals with specifications
- Dark mode support with CSS variables

---

## 1. Page Structure Standards

### Overall Layout

✅ **Correct Pattern**:
```html
{% extends "base.html" %}

{% block title %}[Product Category] - {{ config.SITE_NAME }}{% endblock %}

{% block content %}
<!-- 1. Category Header Bar -->
<section class="category-header">
    <div class="container">
        <h1 class="category-title">[Product Category Name]</h1>
        <p class="category-description">[Engaging description]</p>
    </div>
</section>

<!-- 2. Sub-Products Navigation (if applicable) -->
<section class="sub-products-section">
    <!-- Navigation cards to different product types -->
</section>

<!-- 3. Product Details Section -->
<section class="sub-product-details">
    <!-- Product grids, filters, modals -->
</section>

<!-- 4. Modals -->
<!-- Product detail modal, custom request modals, etc. -->

<!-- 5. Toast Notifications -->
<div class="toast-container"></div>

{% endblock %}
```

**Key Sections**:
1. **Category Header** - Eye-catching intro with gradient background
2. **Navigation Cards** - Sub-categories or product types (if needed)
3. **Product Details** - Main content area with filters and product grid
4. **Modals** - Product details, custom requests
5. **Toasts** - User feedback notifications

---

## 2. CSS Variable Usage

### Required CSS Variables (from global style.css)

**Light Mode**:
- `--card-bg: #ffffff` (white)
- `--text-color: #1f2937` (dark gray)
- `--bg-color: #ffffff` (white)
- `--muted-text: #6b7280` (gray)
- `--light-color: #f9fafb` (light gray)
- `--shadow-sm: 0 1px 2px rgba(0,0,0,0.05)`
- `--shadow-md: 0 4px 6px rgba(0,0,0,0.1)`

**Dark Mode**:
- `--card-bg: #1e293b` (dark slate)
- `--text-color: #e2e8f0` (light gray)
- `--bg-color: #0f172a` (very dark)
- `--muted-text: #94a3b8` (light gray)
- `--light-color: #1e293b` (dark slate)
- Shadows adjust automatically

### CSS Variable Usage Examples

✅ **Correct - Using CSS Variables**:
```css
.category-header {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
    color: white;
}

.sub-product-card {
    background: var(--card-bg);
    box-shadow: var(--shadow-sm);
    transition: all 0.3s ease;
}

.product-info {
    color: var(--text-color);
}

.product-specs {
    color: var(--muted-text);
}

.product-filters-card {
    background: var(--card-bg);
    box-shadow: var(--shadow-sm);
}

.sub-products-section {
    background: var(--light-color);
}
```

❌ **Incorrect - Hardcoded Colors**:
```css
/* WRONG - doesn't respect dark mode */
.product-card {
    background: white;
    color: #1f2937;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}
```

❌ **Incorrect - Undefined Variables**:
```css
/* WRONG - these variables don't exist */
.category-header {
    background: linear-gradient(135deg, var(--primary-color) 0%, var(--accent-color) 100%);
}
```

---

## 3. Category Header Pattern

### Structure

```html
<section class="category-header">
    <div class="container">
        <h1 class="category-title">[Category Name]</h1>
        <p class="category-description">[Engaging description text]</p>
    </div>
</section>
```

### Styling

```css
.category-header {
    background: linear-gradient(135deg, [color-dark] 0%, [color-light] 100%);
    color: white;
    padding: 40px 0 20px;
    margin-top: 76px; /* Fixed navbar height */
}

.category-title {
    font-size: 1.75rem;
    font-weight: 700;
    margin-bottom: 0.25rem;
}

.category-description {
    font-size: 0.95rem;
    opacity: 0.9;
    margin: 0;
}

@media (max-width: 768px) {
    .category-title {
        font-size: 1.5rem;
    }

    .category-header {
        padding: 60px 0 30px;
    }
}
```

**Key Points**:
- Always use a gradient background (not solid color)
- White text on colored background
- Adjust margin-top for fixed navbar (typically 76px)
- Set opacity for description text (0.9)
- Responsive font sizes

---

## 4. Product Card Pattern

### HTML Structure

```html
<div class="col-6 col-md-4 col-lg-3" data-category="{{ item.category_id }}" data-type="{{ item.type_id }}">
    <div class="shop-product-card"
         data-item-id="{{ item.id }}"
         data-name="{{ item.name|e }}"
         data-description="{{ item.description|e }}"
         data-price="R{{ "%.2f"|format(item.price) }}"
         data-dimensions="{{ item.dimensions|e }}"
         data-category="{{ item.category_name|e }}"
         data-category-desc="{{ item.category_description|e }}"
         data-type="{{ item.type_name|e }}"
         data-material="{{ item.material|e }}"
         data-stock="{{ item.stock_status|e }}"
         data-photos='{{ item.photo_urls|tojson }}'
         onclick="openProductDetailFromCard(this, event);"
         style="cursor: pointer;">

        <!-- Product Image -->
        <div class="product-image">
            {% if item.main_photo_url %}
            <img src="{{ item.main_photo_url }}" alt="{{ item.name }}" loading="lazy">
            {% else %}
            <img src="https://images.unsplash.com/photo-1551754655-cd27e38d2076?w=400&h=400&fit=crop&q=80" alt="{{ item.name }}">
            {% endif %}

            <!-- Badges -->
            <span class="badge bg-primary product-badge">{{ item.category_name }}</span>

            {% if item.is_new %}
            <span class="badge bg-success new-badge">NEW</span>
            {% endif %}
        </div>

        <!-- Product Info -->
        <div class="product-info">
            <h5>{{ item.name }}</h5>
            <p class="text-muted small mb-2">{{ item.description }}</p>

            <p class="product-specs">
                <small><i class="fas fa-ruler"></i> {{ item.dimensions }}</small><br>
                <small><i class="fas fa-tag"></i> {{ item.category_name }}, {{ item.type_name }}</small>
            </p>

            <div class="product-price">R{{ "%.2f"|format(item.price) }}</div>

            <!-- Action Buttons -->
            <div class="product-actions">
                <button class="btn btn-primary btn-sm add-to-cart-btn"
                        data-item-id="{{ item.id }}"
                        onclick="event.stopPropagation(); addToCart({{ item.id }}, '{{ item.name }}')">
                    <i class="fas fa-shopping-cart"></i> <span class="btn-text">Add to Cart</span>
                </button>
                <button class="btn btn-outline-secondary btn-sm"
                        onclick="event.stopPropagation(); openCustomizeModal('{{ item.name }}')">
                    <i class="fas fa-pencil-alt"></i> <span class="btn-text">Customize This</span>
                </button>
            </div>
        </div>
    </div>
</div>
```

### CSS Styling

```css
.shop-product-card {
    background: var(--card-bg);
    border-radius: 12px;
    overflow: hidden;
    transition: all 0.3s ease;
    box-shadow: 0 0 8px rgba(37, 99, 235, 0.2), var(--shadow-sm);
    height: 100%;
    display: flex;
    flex-direction: column;
    border: 1px solid #2563eb;
}

.shop-product-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.15);
}

.product-image {
    position: relative;
    width: 100%;
    padding-top: 100%; /* 1:1 aspect ratio */
    overflow: hidden;
}

.product-image img {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.product-badge {
    position: absolute;
    top: 10px;
    right: 10px;
    z-index: 10;
}

.product-info {
    padding: 1rem;
    flex-grow: 1;
    display: flex;
    flex-direction: column;
}

.product-specs {
    font-size: 0.75rem;
    color: var(--muted-text);
    margin-bottom: 0.5rem;
}

.product-price {
    font-size: 1.5rem;
    font-weight: 700;
    color: #2563eb;
    margin-bottom: 1rem;
}

.product-actions {
    margin-top: auto;
    display: flex;
    gap: 0.5rem;
}

/* Desktop: Full width buttons with text */
@media (min-width: 768px) {
    .product-actions {
        flex-direction: column;
    }

    .product-actions .btn {
        width: 100%;
    }
}

/* Mobile: Icon-only buttons side by side */
@media (max-width: 767.98px) {
    .product-actions {
        flex-direction: row;
        justify-content: space-between;
    }

    .product-actions .btn {
        flex: 1;
        padding: 0.5rem;
    }

    .product-actions .btn-text {
        display: none;
    }

    .product-actions .btn i {
        font-size: 1.1rem;
    }
}
```

**Key Features**:
- 1:1 aspect ratio for images
- Flex layout to push actions to bottom
- Category badge in top-right
- NEW badge for recent items
- Hover effect with lift animation
- Mobile-responsive action buttons

---

## 5. Filtering & Search Pattern

### HTML Structure

```html
<div class="row mb-4">
    <div class="col-12">
        <!-- Mobile: Collapsible Filter Button -->
        <button class="btn btn-outline-primary w-100 mb-3 d-md-none"
                type="button"
                data-bs-toggle="collapse"
                data-bs-target="#filterCollapse"
                aria-expanded="false"
                aria-controls="filterCollapse">
            <i class="fas fa-filter"></i> Show Filters & Search
        </button>

        <!-- Filter Section (Collapsible on mobile, always visible on desktop) -->
        <div class="collapse d-md-block" id="filterCollapse">
            <div class="product-filters-card">
                <div class="row g-3 align-items-end">
                    <!-- Category Filter -->
                    <div class="col-md-3">
                        <label class="form-label"><strong>Category</strong></label>
                        <select class="form-select" id="filterCategory">
                            <option value="">All Categories</option>
                            {% for category in categories %}
                            <option value="{{ category.id }}">{{ category.name }}</option>
                            {% endfor %}
                        </select>
                    </div>

                    <!-- Type Filter -->
                    <div class="col-md-3">
                        <label class="form-label"><strong>Type</strong></label>
                        <select class="form-select" id="filterType">
                            <option value="">All Types</option>
                            {% for type in types %}
                            <option value="{{ type.id }}">{{ type.name }}</option>
                            {% endfor %}
                        </select>
                    </div>

                    <!-- Search Box -->
                    <div class="col-md-4">
                        <label class="form-label"><strong>Search</strong></label>
                        <div class="input-group">
                            <input type="text" class="form-control" id="searchBox"
                                   placeholder="Search by name or description...">
                            <button class="btn btn-outline-secondary"><i class="fas fa-search"></i></button>
                        </div>
                    </div>

                    <!-- Sort By -->
                    <div class="col-md-2">
                        <label class="form-label"><strong>Sort By</strong></label>
                        <select class="form-select" id="sortBy">
                            <option>Newest First</option>
                            <option>Price: Low to High</option>
                            <option>Price: High to Low</option>
                            <option>Name: A-Z</option>
                            <option>Most Popular</option>
                        </select>
                    </div>
                </div>

                <!-- Product Count -->
                <div class="row mt-3">
                    <div class="col-12">
                        <p class="mb-0 text-muted"><strong>Showing <span class="product-count">0</span> products</strong></p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
```

### CSS Styling

```css
.product-filters-card {
    background: var(--card-bg);
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: var(--shadow-sm);
}

.product-filters-card .form-label {
    font-weight: 600;
    color: var(--text-color);
}

.product-filters-card .form-select,
.product-filters-card .form-control {
    background: var(--bg-color);
    color: var(--text-color);
    border-color: rgba(229, 231, 235, 0.3);
}

.product-filters-card .form-select:focus,
.product-filters-card .form-control:focus {
    background: var(--bg-color);
    color: var(--text-color);
    border-color: #2563eb;
}
```

### JavaScript Functionality

```javascript
// Attach filter and sort event listeners
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('filterCategory').addEventListener('change', filterAndSortProducts);
    document.getElementById('filterType').addEventListener('change', filterAndSortProducts);
    document.getElementById('searchBox').addEventListener('input', filterAndSortProducts);
    document.getElementById('sortBy').addEventListener('change', filterAndSortProducts);
});

// Client-side filtering and sorting
function filterAndSortProducts() {
    const categoryFilter = document.getElementById('filterCategory').value;
    const typeFilter = document.getElementById('filterType').value;
    const searchTerm = document.getElementById('searchBox').value.toLowerCase();
    const sortBy = document.getElementById('sortBy').value;

    const productGrid = document.getElementById('productGrid');
    const productCards = Array.from(document.querySelectorAll('#productGrid > div[data-category]'));
    let visibleCards = [];

    // Filter products
    productCards.forEach(card => {
        const cardCategory = card.getAttribute('data-category');
        const cardType = card.getAttribute('data-type');
        const cardElement = card.querySelector('.shop-product-card');
        const name = cardElement.getAttribute('data-name').toLowerCase();
        const description = cardElement.getAttribute('data-description').toLowerCase();

        const categoryMatch = !categoryFilter || cardCategory === categoryFilter;
        const typeMatch = !typeFilter || cardType === typeFilter;
        const searchMatch = !searchTerm || name.includes(searchTerm) || description.includes(searchTerm);

        if (categoryMatch && typeMatch && searchMatch) {
            card.style.display = '';
            visibleCards.push(card);
        } else {
            card.style.display = 'none';
        }
    });

    // Sort visible products
    if (sortBy && visibleCards.length > 0) {
        visibleCards.sort((a, b) => {
            const aCard = a.querySelector('.shop-product-card');
            const bCard = b.querySelector('.shop-product-card');

            switch(sortBy) {
                case 'Price: Low to High':
                    const aPrice = parseFloat(aCard.getAttribute('data-price').replace('R', ''));
                    const bPrice = parseFloat(bCard.getAttribute('data-price').replace('R', ''));
                    return aPrice - bPrice;

                case 'Price: High to Low':
                    const aPriceH = parseFloat(aCard.getAttribute('data-price').replace('R', ''));
                    const bPriceH = parseFloat(bCard.getAttribute('data-price').replace('R', ''));
                    return bPriceH - aPriceH;

                case 'Name: A-Z':
                    const aName = aCard.getAttribute('data-name').toLowerCase();
                    const bName = bCard.getAttribute('data-name').toLowerCase();
                    return aName.localeCompare(bName);

                default:
                    return 0;
            }
        });

        visibleCards.forEach(card => {
            productGrid.appendChild(card);
        });
    }

    // Update product count
    document.querySelector('.product-count').textContent = visibleCards.length;
}
```

**Key Features**:
- Category, Type, Search, and Sort filters
- Collapsible on mobile, always visible on desktop
- Real-time filtering and sorting
- Product count display
- Search by name or description

---

## 6. Product Detail Modal Pattern

### HTML Structure

```html
<div class="modal fade" id="productDetailModal" tabindex="-1">
    <div class="modal-dialog modal-xl">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="productModalTitle">Product Name</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <div class="row">
                    <!-- Image Carousel Section -->
                    <div class="col-md-6 mb-4 mb-md-0">
                        <div id="productImageCarousel" class="carousel slide" data-bs-ride="false">
                            <div class="carousel-indicators" id="carouselIndicators">
                                <!-- Dynamically populated -->
                            </div>
                            <div class="carousel-inner" id="carouselImages">
                                <!-- Dynamically populated -->
                            </div>
                            <button class="carousel-control-prev" type="button" data-bs-target="#productImageCarousel" data-bs-slide="prev">
                                <span class="carousel-control-prev-icon" aria-hidden="true"></span>
                                <span class="visually-hidden">Previous</span>
                            </button>
                            <button class="carousel-control-next" type="button" data-bs-target="#productImageCarousel" data-bs-slide="next">
                                <span class="carousel-control-next-icon" aria-hidden="true"></span>
                                <span class="visually-hidden">Next</span>
                            </button>
                        </div>

                        <!-- Category Description -->
                        <div class="alert alert-info mt-3" id="modalCategoryDescription" style="display: none;">
                            <i class="fas fa-info-circle"></i> <span id="modalCategoryDescriptionText"></span>
                        </div>
                    </div>

                    <!-- Product Details Section -->
                    <div class="col-md-6">
                        <div class="product-detail-info">
                            <h3 id="modalProductName">Product Name</h3>
                            <p class="text-muted" id="modalProductDescription">Product description</p>

                            <div class="product-price-large mb-3" id="modalProductPrice">R45.00</div>

                            <!-- Specifications -->
                            <div class="product-specifications mb-4">
                                <h6 class="fw-bold">Specifications:</h6>
                                <ul class="list-unstyled">
                                    <li><i class="fas fa-ruler text-primary"></i> <strong>Dimensions:</strong> <span id="modalProductDimensions">8cm × 7cm × 2cm</span></li>
                                    <li><i class="fas fa-tag text-primary"></i> <strong>Category:</strong> <span id="modalProductCategory">Cookie</span></li>
                                    <li><i class="fas fa-shapes text-primary"></i> <strong>Type:</strong> <span id="modalProductType">Animal</span></li>
                                    <li><i class="fas fa-cube text-primary"></i> <strong>Material:</strong> <span id="modalProductMaterial">Food-safe PLA</span></li>
                                    <li><i class="fas fa-box text-primary"></i> <strong>Stock:</strong> <span id="modalProductStock" class="badge bg-success">In Stock</span></li>
                                </ul>
                            </div>

                            <!-- Quantity Selector -->
                            <div class="quantity-selector mb-4">
                                <label class="form-label fw-bold">Quantity:</label>
                                <div class="input-group" style="max-width: 200px;">
                                    <button class="btn btn-outline-secondary" type="button" onclick="decreaseQuantity()">
                                        <i class="fas fa-minus"></i>
                                    </button>
                                    <input type="number" class="form-control text-center" id="productQuantity" value="1" min="1" max="999">
                                    <button class="btn btn-outline-secondary" type="button" onclick="increaseQuantity()">
                                        <i class="fas fa-plus"></i>
                                    </button>
                                </div>
                            </div>

                            <!-- Action Buttons -->
                            <div class="product-actions-modal">
                                <button class="btn btn-primary btn-lg w-100 mb-2" id="modalAddToCartBtn" onclick="addToCartFromModal()">
                                    <i class="fas fa-shopping-cart"></i> Add to Cart
                                </button>
                                <button class="btn btn-outline-secondary btn-lg w-100" onclick="openCustomizeModalFromProduct()">
                                    <i class="fas fa-pencil-alt"></i> Customize This Product
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
```

### CSS Styling

```css
#productImageCarousel .carousel-inner {
    border-radius: 12px;
    overflow: hidden;
}

#productImageCarousel .carousel-item img {
    width: 100%;
    height: 500px;
    object-fit: cover;
}

#productImageCarousel .carousel-control-prev,
#productImageCarousel .carousel-control-next {
    background: rgba(0, 0, 0, 0.3);
    width: 50px;
    height: 50px;
    border-radius: 50%;
    top: 50%;
    transform: translateY(-50%);
}

.product-price-large {
    font-size: 2.5rem;
    font-weight: 700;
    color: #2563eb;
}

.product-specifications li {
    padding: 0.5rem 0;
    border-bottom: 1px solid rgba(229, 231, 235, 0.3);
}

.product-specifications li:last-child {
    border-bottom: none;
}

.modal-content {
    background: var(--card-bg);
    color: var(--text-color);
}

.modal-header {
    border-bottom-color: rgba(229, 231, 235, 0.3);
}

.modal-footer {
    border-top-color: rgba(229, 231, 235, 0.3);
}
```

### JavaScript Functions

```javascript
// Open product detail modal
function openProductDetailFromCard(cardElement, event) {
    const itemId = cardElement.getAttribute('data-item-id');
    const name = cardElement.getAttribute('data-name');
    const description = cardElement.getAttribute('data-description');
    const price = cardElement.getAttribute('data-price');
    const dimensions = cardElement.getAttribute('data-dimensions');
    const category = cardElement.getAttribute('data-category');
    const categoryDescription = cardElement.getAttribute('data-category-desc');
    const type = cardElement.getAttribute('data-type');
    const material = cardElement.getAttribute('data-material');
    const stock = cardElement.getAttribute('data-stock');
    const photosJson = cardElement.getAttribute('data-photos');

    // Store item ID for cart
    document.getElementById('productDetailModal').setAttribute('data-current-item-id', itemId);

    let images = [];
    try {
        images = JSON.parse(photosJson) || [];
    } catch (e) {
        images = ['https://images.unsplash.com/photo-1551754655-cd27e38d2076?w=800&h=800&fit=crop&q=80'];
    }

    // Populate modal with product data
    document.getElementById('productModalTitle').textContent = name;
    document.getElementById('modalProductName').textContent = name;
    document.getElementById('modalProductDescription').textContent = description;
    document.getElementById('modalProductPrice').textContent = price;
    document.getElementById('modalProductDimensions').textContent = dimensions;
    document.getElementById('modalProductCategory').textContent = category;
    document.getElementById('modalProductType').textContent = type;
    document.getElementById('modalProductMaterial').textContent = material;

    // Stock badge
    const stockBadge = document.getElementById('modalProductStock');
    stockBadge.textContent = stock;
    stockBadge.className = 'badge';
    if (stock === 'In Stock') {
        stockBadge.classList.add('bg-success');
    } else if (stock === 'Made to Order') {
        stockBadge.classList.add('bg-warning');
    } else {
        stockBadge.classList.add('bg-secondary');
    }

    // Populate carousel
    const carouselIndicators = document.getElementById('carouselIndicators');
    const carouselImages = document.getElementById('carouselImages');
    carouselIndicators.innerHTML = '';
    carouselImages.innerHTML = '';

    images.forEach((imageUrl, index) => {
        const indicator = document.createElement('button');
        indicator.type = 'button';
        indicator.setAttribute('data-bs-target', '#productImageCarousel');
        indicator.setAttribute('data-bs-slide-to', index.toString());
        if (index === 0) {
            indicator.classList.add('active');
            indicator.setAttribute('aria-current', 'true');
        }
        carouselIndicators.appendChild(indicator);

        const carouselItem = document.createElement('div');
        carouselItem.classList.add('carousel-item');
        if (index === 0) {
            carouselItem.classList.add('active');
        }

        const img = document.createElement('img');
        img.src = imageUrl;
        img.classList.add('d-block', 'w-100');
        img.alt = `${name} - Image ${index + 1}`;

        carouselItem.appendChild(img);
        carouselImages.appendChild(carouselItem);
    });

    // Reset quantity
    document.getElementById('productQuantity').value = 1;

    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('productDetailModal'));
    modal.show();
}

// Quantity controls
function increaseQuantity() {
    const input = document.getElementById('productQuantity');
    const currentValue = parseInt(input.value) || 1;
    const maxValue = parseInt(input.max) || 999;
    if (currentValue < maxValue) {
        input.value = currentValue + 1;
    }
}

function decreaseQuantity() {
    const input = document.getElementById('productQuantity');
    const currentValue = parseInt(input.value) || 1;
    const minValue = parseInt(input.min) || 1;
    if (currentValue > minValue) {
        input.value = currentValue - 1;
    }
}
```

**Key Features**:
- Image carousel with indicators and controls
- Product specifications list
- Stock status badge
- Quantity selector with +/- buttons
- Large price display
- Add to cart button
- Customize product button

---

## 7. Mobile Responsiveness Pattern

### Grid Breakpoints

✅ **Correct - Responsive Grid**:
```html
<!-- 2 columns on mobile, 3 on tablet, 4 on desktop -->
<div class="row g-4" id="productGrid">
    <div class="col-6 col-md-4 col-lg-3">
        <!-- Product card -->
    </div>
</div>
```

### Collapsible Filters

✅ **Correct - Mobile Collapsible**:
```html
<!-- Show button only on mobile -->
<button class="btn btn-outline-primary w-100 mb-3 d-md-none"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#filterCollapse">
    <i class="fas fa-filter"></i> Show Filters & Search
</button>

<!-- Hide on mobile, show on desktop -->
<div class="collapse d-md-block" id="filterCollapse">
    <!-- Filters -->
</div>
```

### Icon-Only Buttons on Mobile

✅ **Correct - Responsive Button Text**:
```css
/* Desktop: Full width buttons with text */
@media (min-width: 768px) {
    .product-actions {
        flex-direction: column;
    }

    .product-actions .btn {
        width: 100%;
    }
}

/* Mobile: Icon-only buttons side by side */
@media (max-width: 767.98px) {
    .product-actions {
        flex-direction: row;
        justify-content: space-between;
    }

    .product-actions .btn {
        flex: 1;
        padding: 0.5rem;
    }

    .product-actions .btn-text {
        display: none; /* Hide text labels */
    }

    .product-actions .btn i {
        font-size: 1.1rem;
    }
}
```

**Key Points**:
- Use Bootstrap's grid system (col-6, col-md-4, col-lg-3)
- Collapse filters on mobile
- Hide button text labels on mobile
- Stack buttons vertically on desktop
- Adjust font sizes and spacing for screens

---

## 8. Add to Cart Functionality

### HTML Button Structure

```html
<button class="btn btn-primary btn-sm add-to-cart-btn"
        data-item-id="{{ item.id }}"
        onclick="event.stopPropagation(); addToCart({{ item.id }}, '{{ item.name }}')">
    <i class="fas fa-shopping-cart"></i> <span class="btn-text">Add to Cart</span>
</button>
```

### JavaScript Function

```javascript
function addToCart(itemId, itemName) {
    // Show loading state
    const button = document.querySelector(`button[data-item-id="${itemId}"]`);
    const originalText = button.innerHTML;
    button.disabled = true;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adding...';

    // Send AJAX request
    fetch('/cart/add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            item_id: itemId,
            quantity: 1
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Show success message
            showToast(`${itemName} added to cart!`, 'success');

            // Update cart badge
            updateCartBadge(data.cart_count);

            // Show success state
            button.innerHTML = '<i class="fas fa-check"></i> Added!';
            button.classList.remove('btn-primary');
            button.classList.add('btn-success');

            // Reset after 2 seconds
            setTimeout(() => {
                button.innerHTML = originalText;
                button.classList.remove('btn-success');
                button.classList.add('btn-primary');
                button.disabled = false;
            }, 2000);
        } else {
            showToast(data.message || 'Failed to add to cart', 'error');
            button.innerHTML = originalText;
            button.disabled = false;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('An error occurred. Please try again.', 'error');
        button.innerHTML = originalText;
        button.disabled = false;
    });
}

function addToCartFromModal() {
    const modal = document.getElementById('productDetailModal');
    const itemId = modal.getAttribute('data-current-item-id');
    const quantity = parseInt(document.getElementById('productQuantity').value) || 1;

    const button = document.getElementById('modalAddToCartBtn');
    const originalText = button.innerHTML;
    button.disabled = true;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adding...';

    fetch('/cart/add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            item_id: itemId,
            quantity: quantity
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(`Added ${quantity} item(s) to cart!`, 'success');
            updateCartBadge(data.cart_count);

            button.innerHTML = '<i class="fas fa-check"></i> Added!';
            button.classList.remove('btn-primary');
            button.classList.add('btn-success');

            document.getElementById('productQuantity').value = 1;

            setTimeout(() => {
                button.innerHTML = originalText;
                button.classList.remove('btn-success');
                button.classList.add('btn-primary');
                button.disabled = false;
            }, 2000);
        } else {
            showToast(data.message || 'Failed to add to cart', 'error');
            button.innerHTML = originalText;
            button.disabled = false;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('An error occurred. Please try again.', 'error');
        button.innerHTML = originalText;
        button.disabled = false;
    });
}
```

**Key Features**:
- Loading state with spinner
- Success state with checkmark
- Toast notification
- Cart badge update
- Error handling
- Prevents double-click issues

---

## 9. Toast Notification Pattern

### HTML Structure

```html
<div class="toast-container position-fixed top-0 end-0 p-3" style="z-index: 11000;">
    <!-- Toasts dynamically created here -->
</div>
```

### JavaScript Function

```javascript
function showToast(message, type = 'info') {
    // Create container if needed
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.style.cssText = 'position: fixed; top: 80px; right: 20px; z-index: 9999;';
        document.body.appendChild(toastContainer);
    }

    // Create toast element
    const toast = document.createElement('div');
    const alertClass = type === 'success' ? 'success' : type === 'error' ? 'danger' : 'info';
    toast.className = `alert alert-${alertClass} alert-dismissible fade show`;
    toast.style.cssText = 'min-width: 250px; margin-bottom: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);';
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    toastContainer.appendChild(toast);

    // Auto-dismiss after 3 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 150);
    }, 3000);
}
```

### Usage Examples

```javascript
// Success message
showToast('Item added to cart!', 'success');

// Error message
showToast('Failed to add item', 'error');

// Info message
showToast('Coming soon!', 'info');
```

**Key Features**:
- Auto-dismisses after 3 seconds
- Closeable with X button
- Top-right positioning
- Color-coded by type
- Smooth fade animations

---

## 10. Common CSS Classes Reference

### Layout Classes
- `.category-header` - Page header with gradient
- `.sub-products-section` - Navigation cards section
- `.sub-product-details` - Main content area
- `.product-detail-content` - Individual product sections (hidden/shown)

### Card Classes
- `.shop-product-card` - Product grid card
- `.sub-product-card` - Navigation card
- `.product-filters-card` - Filter/search card
- `.request-form-card` - Form container
- `.custom-request-callout` - Callout box

### Component Classes
- `.product-image` - Image container (1:1 aspect)
- `.product-info` - Product details section
- `.product-specs` - Specifications text
- `.product-price` - Price display
- `.product-actions` - Button group
- `.product-badge` - Category/NEW badge
- `.product-detail-info` - Modal details

### Filter Classes
- `.product-filters-card` - Filter container
- `#filterCategory` - Category select
- `#filterType` - Type select
- `#searchBox` - Search input
- `#sortBy` - Sort select

### Modal Classes
- `#productDetailModal` - Product detail modal
- `#productImageCarousel` - Image carousel
- `.carousel-indicators` - Carousel dots
- `.carousel-item` - Individual slide

### Button Classes
- `.btn-primary` - Primary (blue) button
- `.btn-success` - Success (green) button
- `.btn-danger` - Danger (red) button
- `.btn-outline-secondary` - Secondary outline button
- `.add-to-cart-btn` - Add to cart button
- `.btn-text` - Hidden on mobile

---

## 11. Required JavaScript Functions

### Essential Functions

```javascript
// Filtering and sorting
function filterAndSortProducts()

// Product detail modal
function openProductDetailFromCard(cardElement, event)
function openProductDetail(event, name, description, price, ...)

// Add to cart
function addToCart(itemId, itemName)
function addToCartFromModal()

// Quantity controls
function increaseQuantity()
function decreaseQuantity()

// Notifications
function showToast(message, type)
function showComingSoonToast()

// Customize modal
function openCustomizeModal(productName)
function openCustomizeModalFromProduct()

// Cart badge update
function updateCartBadge(count)
```

### Function Signatures

✅ **Correct Pattern**:
```javascript
// Filter with all parameters captured
function filterAndSortProducts() {
    const categoryFilter = document.getElementById('filterCategory').value;
    const typeFilter = document.getElementById('filterType').value;
    const searchTerm = document.getElementById('searchBox').value.toLowerCase();
    const sortBy = document.getElementById('sortBy').value;
    // ... filtering logic
}

// Add to cart with AJAX
function addToCart(itemId, itemName) {
    fetch('/cart/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ item_id: itemId, quantity: 1 })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(data.message, 'success');
            updateCartBadge(data.cart_count);
        }
    })
    .catch(error => showToast('Error', 'error'));
}

// Show toast with auto-dismiss
function showToast(message, type = 'info') {
    // Create and append toast element
    // Auto-dismiss after 3 seconds
}
```

---

## 12. Accessibility Standards

### Alt Text for Images

✅ **Correct**:
```html
<img src="{{ item.main_photo_url }}" alt="{{ item.name }}" loading="lazy">
<img src="{{ image }}" class="d-block w-100" alt="Product Image {{ index + 1 }}">
```

❌ **Incorrect**:
```html
<img src="{{ item.main_photo_url }}" alt="image">
<img src="{{ image }}" class="d-block w-100">
```

### ARIA Labels

✅ **Correct**:
```html
<!-- Carousel controls -->
<button class="carousel-control-prev" aria-label="Previous slide">
    <span class="visually-hidden">Previous</span>
</button>

<!-- Collapse toggle -->
<button data-bs-toggle="collapse" aria-expanded="false" aria-controls="filterCollapse">
    <i class="fas fa-filter"></i> Show Filters
</button>

<!-- Carousel indicators -->
<button data-bs-slide-to="0" aria-label="Slide 1"></button>
```

❌ **Incorrect**:
```html
<button class="carousel-control-prev">
    <!-- No label -->
</button>
```

### Keyboard Navigation

✅ **Correct Pattern**:
```html
<!-- Form controls are naturally keyboard accessible -->
<select class="form-select" id="filterCategory">
    <option value="">All Categories</option>
</select>

<input type="text" class="form-control" id="searchBox">

<!-- Quantity control with keyboard support -->
<div class="quantity-selector">
    <button onclick="decreaseQuantity()">−</button>
    <input type="number" id="productQuantity" min="1" max="999">
    <button onclick="increaseQuantity()">+</button>
</div>
```

### Color Contrast

- Text on white background: Dark gray (1f2937)
- Text on dark background: Light gray (e2e8f0)
- Button colors meet WCAG AA standards
- Links are distinguishable without color alone

### Form Labels

✅ **Correct**:
```html
<label for="filterCategory" class="form-label">Category</label>
<select id="filterCategory" class="form-select">
    <!-- Options -->
</select>
```

❌ **Incorrect**:
```html
<select class="form-select">
    <option>All Categories</option>
</select>
```

### Loading and Feedback States

✅ **Correct**:
```javascript
// Show loading spinner during request
button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adding...';
button.disabled = true;

// Show success/error with toast
showToast('Item added!', 'success');
```

---

## 13. Checklist for New Shop Pages

### Before Starting
- [ ] Review 3D Printing template (reference implementation)
- [ ] Define category structure
- [ ] Choose product attributes (dimensions, material, etc.)
- [ ] Plan filtering options
- [ ] Define color scheme and gradients

### Database Setup
- [ ] Create categories table
- [ ] Create products table
- [ ] Create product photos table
- [ ] Create shopping cart table
- [ ] Test CRUD operations
- [ ] Add sample data

### Page Structure
- [ ] Category header section with gradient
- [ ] Sub-products navigation (if needed)
- [ ] Product filters and search
- [ ] Product grid (col-6 col-md-4 col-lg-3)
- [ ] Product detail modal
- [ ] Custom request modal (if applicable)
- [ ] Toast container

### CSS Styling
- [ ] Use CSS variables for colors
- [ ] Responsive grid layout
- [ ] Hover effects on cards
- [ ] Mobile-responsive filters
- [ ] Icon-only buttons on mobile
- [ ] Dark mode support
- [ ] Proper shadows and borders

### JavaScript Functions
- [ ] Filter products by category
- [ ] Filter products by type
- [ ] Search by name/description
- [ ] Sort by price, name, date
- [ ] Open product detail modal
- [ ] Add to cart with AJAX
- [ ] Show toast notifications
- [ ] Update cart badge
- [ ] Quantity controls

### Accessibility
- [ ] Alt text on all images
- [ ] ARIA labels on buttons
- [ ] Keyboard navigation support
- [ ] Form labels associated
- [ ] Color contrast verified
- [ ] Carousel navigation works

### Testing
- [ ] Test all filters work
- [ ] Test search functionality
- [ ] Test sorting options
- [ ] Test add to cart
- [ ] Test product detail modal
- [ ] Test on mobile (responsive)
- [ ] Test dark mode
- [ ] Test keyboard navigation
- [ ] Test on different browsers
- [ ] Verify accessibility

### Integration
- [ ] Add navigation links to base.html
- [ ] Update cart routes
- [ ] Test checkout flow
- [ ] Verify stock management
- [ ] Test order confirmation

---

## 14. Common Patterns to Reuse

### Product Data Attributes

```html
<!-- Store all data on card for modal functionality -->
<div class="shop-product-card"
     data-item-id="{{ item.id }}"
     data-name="{{ item.name|e }}"
     data-description="{{ item.description|e }}"
     data-price="R{{ "%.2f"|format(item.price) }}"
     data-dimensions="{{ item.dimensions|e }}"
     data-category="{{ item.category_name|e }}"
     data-category-desc="{{ item.category_description|e }}"
     data-type="{{ item.type_name|e }}"
     data-material="{{ item.material|e }}"
     data-stock="{{ item.stock_status|e }}"
     data-photos='{{ item.photo_urls|tojson }}'>
```

### Event Handling

```html
<!-- Stop propagation to prevent multiple handlers -->
<button onclick="event.stopPropagation(); addToCart({{ item.id }}, '{{ item.name }}')">
    <i class="fas fa-shopping-cart"></i> Add to Cart
</button>

<!-- Card click opens modal -->
<div class="shop-product-card" onclick="openProductDetailFromCard(this, event);">
```

### Dynamic Content Population

```javascript
// Clear and rebuild carousel
carouselIndicators.innerHTML = '';
carouselImages.innerHTML = '';

images.forEach((imageUrl, index) => {
    // Create indicator button
    const indicator = document.createElement('button');
    // Add to indicators
    carouselIndicators.appendChild(indicator);

    // Create carousel item
    const carouselItem = document.createElement('div');
    // Add to images
    carouselImages.appendChild(carouselItem);
});
```

---

## 15. Version History
- **v1.0** (2025-01-11): Initial documentation based on 3D Printing shop page pattern

## 16. CRITICAL: Unified Shopping Cart Requirement

### NEVER Create Separate Cart Systems

**RULE:** The application MUST use ONE unified shopping cart for ALL product types.

**WRONG - Separate Cart Tables:**
```sql
CREATE TABLE cart_items (...)           -- For Product Type A
CREATE TABLE product_b_cart_items (...) -- For Product Type B
CREATE TABLE product_c_cart_items (...) -- For Product Type C
```

**CORRECT - Unified Cart Table:**
```sql
CREATE TABLE cart_items (
    id INTEGER PRIMARY KEY,
    session_id TEXT,
    user_id INTEGER,
    product_type TEXT NOT NULL,  -- 'cutter', 'candles_soaps', 'new_type'
    product_id INTEGER NOT NULL,
    quantity INTEGER,
    added_date TIMESTAMP
);
```

### Benefits of Unified Cart:
- Single source of truth for all products
- Simpler code (one set of cart functions)
- Better user experience (all items in one shopping cart)
- Easier, unified checkout process
- Scalable for new product types
- Consistent cart behavior across all product lines

### Implementation Pattern:
When adding a NEW product line:
1. **DO NOT** create a new cart table (e.g., `candles_cart_items`, `new_product_cart_items`)
2. **DO NOT** duplicate cart functions for each product type
3. **USE** the existing `cart_items` table with a `product_type` field
4. **REUSE** all cart functions: `add_to_cart()`, `get_cart_items()`, `remove_from_cart()`, etc.

### Example Cart Function:
```python
def add_to_cart(product_type, product_id, quantity=1):
    """Add item to unified cart regardless of product type"""
    cursor = get_db().cursor()
    cursor.execute('''
        INSERT INTO cart_items (session_id, product_type, product_id, quantity, added_date)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
    ''', (session.get('session_id'), product_type, product_id, quantity))
    get_db().commit()
```

### Getting Cart Count:
```python
def get_cart_count():
    """Gets total items across ALL product types"""
    cursor = get_db().cursor()
    cursor.execute('SELECT SUM(quantity) FROM cart_items WHERE session_id = ?',
                   (session.get('session_id'),))
    result = cursor.fetchone()
    return result[0] or 0
```

### Getting All Cart Items:
```python
def get_cart_items():
    """Returns cart items from ALL product types"""
    cursor = get_db().cursor()
    cursor.execute('''
        SELECT id, product_type, product_id, quantity, added_date
        FROM cart_items
        WHERE session_id = ?
        ORDER BY added_date DESC
    ''', (session.get('session_id'),))
    return cursor.fetchall()
```

### Product Details Lookup:
```python
def get_product_details(product_type, product_id):
    """Get product info based on type"""
    cursor = get_db().cursor()

    if product_type == 'cutter':
        cursor.execute('SELECT * FROM cutter_items WHERE id = ?', (product_id,))
    elif product_type == 'candles_soaps':
        cursor.execute('SELECT * FROM candles_soaps_products WHERE id = ?', (product_id,))
    elif product_type == 'new_type':
        cursor.execute('SELECT * FROM new_type_products WHERE id = ?', (product_id,))

    return cursor.fetchone()
```

---

## Questions?
If you encounter a scenario not covered in these guidelines, refer to:
1. 3D Printing shop template (`templates/3d_printing.html`) - primary reference
2. Review CSS variable usage in `static/style.css`
3. Check Bootstrap utilities documentation for responsive classes
4. Ask before deviating from established patterns
