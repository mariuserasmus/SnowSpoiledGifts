from flask import Flask, render_template, request, redirect, url_for, flash, session, Response
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from functools import wraps
from src.config import Config
from src.database import Database
from src.forms import EmailSignupForm, RegistrationForm, LoginForm, EditProfileForm, CheckoutForm
from src.email_utils import send_quote_notification, send_customer_confirmation, send_signup_confirmation, send_cake_topper_notification, send_print_service_notification, send_admin_reply_to_customer, send_order_confirmation
from version_check import get_version_info
from datetime import datetime
import os
import random

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Configure session settings
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['PERMANENT_SESSION_LIFETIME'] = 86400 * 30  # 30 days

# Initialize database
db = Database(app.config['DATABASE_PATH'])

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'


# User class for Flask-Login
class User(UserMixin):
    def __init__(self, user_dict):
        self.id = user_dict['id']
        self.email = user_dict['email']
        self.name = user_dict['name']
        self.phone = user_dict.get('phone')
        self._is_active = user_dict.get('is_active', True)
        self.is_admin = user_dict.get('is_admin', False)
        self.created_date = user_dict.get('created_date')

    @property
    def is_active(self):
        """Override UserMixin's is_active property"""
        return self._is_active


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    user_dict = db.get_user_by_id(int(user_id))
    if user_dict:
        return User(user_dict)
    return None


def get_session_id():
    """Get or create a session ID for cart tracking"""
    if 'cart_session_id' not in session:
        session['cart_session_id'] = os.urandom(24).hex()
        session.permanent = True
    return session['cart_session_id']


def admin_required(f):
    """Decorator to require admin login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    """Main landing page"""
    form = EmailSignupForm()

    # Get stats for homepage counters
    total_products = len(db.get_all_cutter_items(active_only=True))
    total_customers = db.get_signup_count()  # Using email signups as customer count for now

    # Calculate new products this month (created in last 30 days)
    from datetime import datetime, timedelta
    thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    all_products = db.get_all_cutter_items(active_only=True)
    new_products = len([p for p in all_products if p['created_date'] and p['created_date'] >= thirty_days_ago])

    return render_template('index.html',
                          form=form,
                          config=app.config,
                          total_products=total_products,
                          total_customers=total_customers,
                          new_products=new_products)


@app.route('/signup', methods=['POST'])
def signup():
    """Handle email signup"""
    form = EmailSignupForm()

    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        interests = form.interests.data
        ip_address = request.remote_addr

        success, message_type, unsubscribe_token = db.add_signup(name, email, interests, ip_address)

        if success:
            # Prepare signup data for email
            signup_data = {
                'name': name,
                'email': email,
                'interests': interests,
                'unsubscribe_token': unsubscribe_token
            }

            # Send confirmation email to customer (non-blocking - don't fail if email fails)
            email_success, email_message = send_signup_confirmation(app.config, signup_data)
            if not email_success:
                print(f"Signup confirmation email failed: {email_message}")

            # Display appropriate message based on signup type
            if message_type == "new_signup":
                flash("Successfully signed up! Check your email for confirmation.", 'success')
            elif message_type == "updated_interests":
                flash("Your interests have been updated! Check your email for confirmation.", 'success')
            elif message_type == "already_registered":
                flash("You're already registered with these interests!", 'info')

            return redirect(url_for('thank_you'))
        else:
            # Handle error cases
            if message_type == "unsubscribed":
                flash("This email was previously unsubscribed. Please contact us if you'd like to re-subscribe.", 'error')
            else:
                flash("An error occurred. Please try again later.", 'error')
            return redirect(url_for('index'))
    else:
        # Form validation failed
        for field, errors in form.errors.items():
            for error in errors:
                flash(error, 'error')
        return redirect(url_for('index'))


@app.route('/thank-you')
def thank_you():
    """Thank you page after signup"""
    return render_template('thank-you.html', config=app.config)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    # Redirect if already logged in
    if current_user.is_authenticated:
        flash('You are already logged in!', 'info')
        return redirect(url_for('index'))

    form = RegistrationForm()

    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        phone = form.phone.data if form.phone.data else None
        password = form.password.data

        # Create user
        success, message, user_id = db.create_user(email, password, name, phone)

        if success:
            # Get the newly created user
            user_dict = db.get_user_by_id(user_id)
            if user_dict:
                user = User(user_dict)
                login_user(user)

                # Migrate guest cart to user if exists
                session_id = get_session_id()
                db.migrate_guest_cart_to_user(session_id, user_id)

                flash(f'Registration successful! Welcome to {app.config["SITE_NAME"]}!', 'success')
                return redirect(url_for('index'))
            else:
                flash('An error occurred after registration. Please try logging in.', 'error')
                return redirect(url_for('login'))
        else:
            flash(message, 'error')
            return render_template('register.html', form=form, config=app.config)

    return render_template('register.html', form=form, config=app.config)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    # Redirect if already logged in
    if current_user.is_authenticated:
        flash('You are already logged in!', 'info')
        return redirect(url_for('index'))

    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        # Verify credentials
        is_valid, user_dict = db.verify_password(email, password)

        if is_valid and user_dict:
            user = User(user_dict)
            login_user(user)

            # Migrate guest cart to user if exists
            session_id = get_session_id()
            db.migrate_guest_cart_to_user(session_id, user_dict['id'])

            flash(f'Welcome back, {user.name}!', 'success')

            # Redirect to next page if specified, otherwise to home
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password. Please try again.', 'error')
            return render_template('login.html', form=form, config=app.config)

    return render_template('login.html', form=form, config=app.config)


@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('index'))


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    """User account dashboard"""
    form = EditProfileForm()

    if form.validate_on_submit():
        # Update user profile
        update_data = {
            'name': form.name.data,
            'email': form.email.data,
            'phone': form.phone.data if form.phone.data else None
        }

        success, message = db.update_user(current_user.id, update_data)

        if success:
            flash('Profile updated successfully!', 'success')
            # Refresh current user data
            user_dict = db.get_user_by_id(current_user.id)
            if user_dict:
                current_user.name = user_dict['name']
                current_user.email = user_dict['email']
                current_user.phone = user_dict.get('phone')
            return redirect(url_for('account'))
        else:
            flash(message, 'error')

    # Pre-populate form with current user data
    if request.method == 'GET':
        form.name.data = current_user.name
        form.email.data = current_user.email
        form.phone.data = current_user.phone

    # Get order history
    orders = db.get_user_orders(current_user.id)

    return render_template('account.html', form=form, orders=orders, config=app.config)


@app.route('/unsubscribe', methods=['GET', 'POST'])
def unsubscribe():
    """Handle unsubscribe requests"""
    token = request.args.get('token')

    if not token:
        flash('Invalid unsubscribe link.', 'error')
        return redirect(url_for('index'))

    # Get signup details to show on confirmation page
    signup_details = db.get_signup_by_token(token)

    if not signup_details:
        flash('Invalid unsubscribe link.', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Process unsubscribe
        success, message, email = db.unsubscribe_by_token(token)

        if success:
            flash('You have been successfully unsubscribed. We\'re sorry to see you go!', 'success')
            return render_template('unsubscribe-confirmed.html', config=app.config, email=email)
        else:
            if message == "already_unsubscribed":
                flash('This email has already been unsubscribed.', 'info')
            else:
                flash(message, 'error')
            return redirect(url_for('index'))

    # Show confirmation page (GET request)
    return render_template('unsubscribe.html', config=app.config, signup=signup_details, token=token)


def get_carousel_images(subproduct_folder, max_images=15):
    """
    Load images from a gallery folder and return up to max_images in random order.
    Falls back to placeholder images if folder is empty.

    Args:
        subproduct_folder: Name of subfolder (e.g., 'CustomDesign', 'CakeToppers', 'PrintService')
        max_images: Maximum number of images to return (default: 15)

    Returns:
        List of image URLs in random order (limited to max_images)
    """
    # Define the folder path
    gallery_path = os.path.join('static', 'images', 'gallery', '3DPrinting', subproduct_folder)

    # Supported image extensions
    supported_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp')

    images = []

    # Check if folder exists and has images
    if os.path.exists(gallery_path):
        # Get all image files from the folder
        for filename in os.listdir(gallery_path):
            if filename.lower().endswith(supported_extensions):
                # Create URL path for the image
                image_url = f"/static/images/gallery/3DPrinting/{subproduct_folder}/{filename}"
                images.append(image_url)

    # If no images found, use fallback placeholder images based on subproduct
    if not images:
        fallback_images = {
            'CustomDesign': [
                'https://images.unsplash.com/photo-1683818051102-dd1199d163b9?w=800&h=600&fit=crop&q=80',
                'https://images.unsplash.com/photo-1614624532983-4ce03382d63d?w=800&h=600&fit=crop&q=80',
                'https://images.unsplash.com/photo-1581092160562-40aa08e78837?w=800&h=600&fit=crop&q=80',
                'https://images.unsplash.com/photo-1612815154858-60aa4c59eaa6?w=800&h=600&fit=crop&q=80'
            ],
            'CakeToppers': [
                'https://images.unsplash.com/photo-1604531825889-88dc0c7e37db?w=800&h=600&fit=crop&q=80',
                'https://images.unsplash.com/photo-1558636508-e0db3814bd1d?w=800&h=600&fit=crop&q=80',
                'https://images.unsplash.com/photo-1621303837174-89787a7d4729?w=800&h=600&fit=crop&q=80',
                'https://images.unsplash.com/photo-1586985289688-ca3cf47d3e6e?w=800&h=600&fit=crop&q=80'
            ],
            'PrintService': [
                'https://images.unsplash.com/photo-1740625940423-a59a65c753c0?w=800&h=600&fit=crop&q=80',
                'https://images.unsplash.com/photo-1581092918056-0c4c3acd3789?w=800&h=600&fit=crop&q=80',
                'https://images.unsplash.com/photo-1633167606207-d840b5070fc2?w=800&h=600&fit=crop&q=80',
                'https://images.unsplash.com/photo-1614624532983-4ce03382d63d?w=800&h=600&fit=crop&q=80'
            ]
        }
        images = fallback_images.get(subproduct_folder, [])

    # Randomize the order of images
    random.shuffle(images)

    # Limit to max_images
    return images[:max_images]


@app.route('/3d-printing')
def printing_3d():
    """3D Printing category page with dynamic carousel images"""
    from datetime import datetime, timedelta

    # Load images for each subproduct carousel
    carousel_images = {
        'custom_design': get_carousel_images('CustomDesign'),
        'cake_toppers': get_carousel_images('CakeToppers'),
        'print_service': get_carousel_images('PrintService')
    }

    # Fetch all cutter items from database
    items = db.get_all_cutter_items()

    # Add is_new flag, photo URLs, and main photo URL to each item
    for item in items:
        # Calculate is_new flag (items created within last 30 days)
        try:
            created = datetime.strptime(item['created_date'], '%Y-%m-%d %H:%M:%S')
            days_old = (datetime.now() - created).days
            item['is_new'] = days_old <= 30
        except:
            item['is_new'] = False

        # Get all photos for this item
        photos = db.get_item_photos(item['id'])

        # Build photo URLs list
        # Note: photo_path already contains the full path like "static/uploads/cutter_items/..."
        if photos:
            item['photo_urls'] = [f"/{photo['photo_path'].replace(os.sep, '/')}" for photo in photos]
            # Set main photo URL
            main_photo = next((photo for photo in photos if photo['is_main']), photos[0] if photos else None)
            item['main_photo_url'] = f"/{main_photo['photo_path'].replace(os.sep, '/')}" if main_photo else None
        else:
            item['photo_urls'] = []
            item['main_photo_url'] = None

    # Get categories and types for filters
    categories = db.get_all_cutter_categories()
    types = db.get_all_cutter_types()

    # Create category description lookup
    category_descriptions = {cat['id']: cat.get('description', '') for cat in categories}

    # Add category description to each item
    for item in items:
        item['category_description'] = category_descriptions.get(item['category_id'], '')

    return render_template('3d_printing.html',
                         config=app.config,
                         carousel_images=carousel_images,
                         items=items,
                         categories=categories,
                         types=types)


@app.route('/quote-request', methods=['POST'])
def quote_request():
    """Handle quote request submissions from 3D printing services"""
    # Get form data
    service_type = request.form.get('service_type')
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone', '')
    preferred_contact = request.form.get('preferred_contact', 'Email')
    description = request.form.get('description')
    intended_use = request.form.get('intended_use', '')
    size = request.form.get('size', '')
    quantity = request.form.get('quantity', 1)
    color = request.form.get('color', '')
    material = request.form.get('material', '')
    budget = request.form.get('budget', '')
    additional_notes = request.form.get('additional_notes', '')
    ip_address = request.remote_addr

    # Handle file uploads (store filenames for now)
    uploaded_files = request.files.getlist('reference_images')
    file_names = []
    if uploaded_files:
        # Create uploads directory if it doesn't exist
        upload_folder = os.path.join('static', 'uploads', 'quote_references')
        os.makedirs(upload_folder, exist_ok=True)

        for file in uploaded_files:
            if file and file.filename:
                # Create a unique filename
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{file.filename}"
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                file_names.append(filename)

    reference_images = ','.join(file_names) if file_names else ''

    # Validate required fields
    if not all([service_type, name, email, description]):
        flash('Please fill in all required fields.', 'error')
        return redirect(url_for('printing_3d') + '#custom-design')

    # Add to database
    success, message = db.add_quote_request(
        service_type, name, email, phone, preferred_contact,
        description, intended_use, size, quantity, color, material,
        budget, additional_notes, reference_images, ip_address
    )

    if success:
        # Send email notification to admin
        quote_data = {
            'service_type': service_type,
            'name': name,
            'email': email,
            'phone': phone,
            'preferred_contact': preferred_contact,
            'description': description,
            'intended_use': intended_use,
            'size': size,
            'quantity': quantity,
            'color': color,
            'material': material,
            'budget': budget,
            'additional_notes': additional_notes,
            'reference_images': reference_images,
            'ip_address': ip_address
        }

        # Send email notification to admin (non-blocking - don't fail if email fails)
        email_success, email_message = send_quote_notification(app.config, quote_data)
        if not email_success:
            print(f"Admin email notification failed: {email_message}")

        # Send confirmation email to customer
        customer_email_success, customer_email_message = send_customer_confirmation(app.config, quote_data)
        if not customer_email_success:
            print(f"Customer confirmation email failed: {customer_email_message}")

        flash('Your quote request has been submitted successfully! We\'ll get back to you within 24-48 hours.', 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('printing_3d') + '#custom-design')


@app.route('/cake-topper-request', methods=['POST'])
def cake_topper_request():
    """Handle cake topper quote request submissions"""
    # Get form data
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone', '')
    event_date = request.form.get('event_date', '')
    occasion = request.form.get('occasion')
    size_preference = request.form.get('size_preference', '')
    text_to_include = request.form.get('text_to_include')
    design_details = request.form.get('design_details')
    color_preferences = request.form.get('color_preferences', '')
    stand_type = request.form.get('stand_type', '')
    additional_notes = request.form.get('additional_notes', '')
    ip_address = request.remote_addr

    # Handle file uploads
    uploaded_files = request.files.getlist('reference_images')
    file_names = []
    if uploaded_files:
        upload_folder = os.path.join('static', 'uploads', 'cake_topper_references')
        os.makedirs(upload_folder, exist_ok=True)

        for file in uploaded_files:
            if file and file.filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{file.filename}"
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                file_names.append(filename)

    reference_images = ','.join(file_names) if file_names else ''

    # Validate required fields
    if not all([name, email, occasion, text_to_include, design_details]):
        flash('Please fill in all required fields.', 'error')
        return redirect(url_for('printing_3d') + '#cake-toppers')

    # Add to database
    success, message = db.add_cake_topper_request(
        name, email, phone, event_date, occasion, size_preference,
        text_to_include, design_details, color_preferences, stand_type,
        reference_images, additional_notes, ip_address
    )

    if success:
        # Send email notification to admin
        cake_topper_data = {
            'name': name,
            'email': email,
            'phone': phone,
            'event_date': event_date,
            'occasion': occasion,
            'size_preference': size_preference,
            'text_to_include': text_to_include,
            'design_details': design_details,
            'color_preferences': color_preferences,
            'stand_type': stand_type,
            'reference_images': reference_images,
            'additional_notes': additional_notes,
            'ip_address': ip_address
        }

        # Send email notification to admin (non-blocking)
        email_success, email_message = send_cake_topper_notification(app.config, cake_topper_data)
        if not email_success:
            print(f"Admin email notification failed: {email_message}")

        flash('Your cake topper request has been submitted successfully! We\'ll send you a quote within 24-48 hours.', 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('printing_3d') + '#cake-toppers')


@app.route('/print-service-request', methods=['POST'])
def print_service_request():
    """Handle 3D print service request submissions"""
    # Get form data
    name = request.form.get('name')
    email = request.form.get('email')
    material = request.form.get('material')
    color = request.form.get('color')
    layer_height = request.form.get('layer_height', '0.2mm (Standard - Balanced)')
    infill_density = request.form.get('infill_density', '20% (Standard - Most items)')
    quantity = request.form.get('quantity', 1)
    supports = request.form.get('supports', 'Automatic (Recommended)')
    special_instructions = request.form.get('special_instructions', '')
    ip_address = request.remote_addr

    # Handle 3D file uploads
    uploaded_files = request.files.getlist('print_files')
    file_names = []
    if uploaded_files:
        upload_folder = os.path.join('static', 'uploads', 'print_files')
        os.makedirs(upload_folder, exist_ok=True)

        for file in uploaded_files:
            if file and file.filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{file.filename}"
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                file_names.append(filename)

    uploaded_files_str = ','.join(file_names) if file_names else ''

    # Validate required fields
    if not all([name, email, material, color]) or not file_names:
        flash('Please fill in all required fields and upload at least one 3D file.', 'error')
        return redirect(url_for('printing_3d') + '#print-service')

    # Add to database
    success, message = db.add_print_service_request(
        name, email, uploaded_files_str, material, color, layer_height,
        infill_density, quantity, supports, special_instructions, ip_address
    )

    if success:
        # Send email notification to admin
        print_service_data = {
            'name': name,
            'email': email,
            'uploaded_files': uploaded_files_str,
            'material': material,
            'color': color,
            'layer_height': layer_height,
            'infill_density': infill_density,
            'quantity': quantity,
            'supports': supports,
            'special_instructions': special_instructions,
            'ip_address': ip_address
        }

        # Send email notification to admin (non-blocking)
        email_success, email_message = send_print_service_notification(app.config, print_service_data)
        if not email_success:
            print(f"Admin email notification failed: {email_message}")

        flash('Your 3D print service request has been submitted successfully! You\'ll receive a confirmation email with quote and payment instructions.', 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('printing_3d') + '#print-service')


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if (username == app.config['ADMIN_USERNAME'] and
            password == app.config['ADMIN_PASSWORD']):
            session['admin_logged_in'] = True
            flash('Successfully logged in!', 'success')
            return redirect(url_for('admin_signups'))
        else:
            flash('Invalid credentials!', 'error')

    return render_template('admin-login.html', config=app.config)


@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    flash('Successfully logged out!', 'success')
    return redirect(url_for('index'))


@app.route('/admin/signups')
@admin_required
def admin_signups():
    """Admin page to view signups"""
    signups = db.get_all_signups()
    total_count = db.get_signup_count()

    return render_template('admin-signups.html',
                          signups=signups,
                          total_count=total_count,
                          config=app.config)


@app.route('/admin/orders')
@admin_required
def admin_orders():
    """Admin page to view and manage orders"""
    status_filter = request.args.get('status', None)
    orders = db.get_all_orders(status_filter)

    return render_template('admin-orders.html',
                          orders=orders,
                          status_filter=status_filter,
                          config=app.config)


@app.route('/admin/orders/<order_number>')
@admin_required
def admin_order_detail(order_number):
    """Admin page to view order details"""
    order = db.get_order_by_number(order_number)

    if not order:
        flash('Order not found.', 'error')
        return redirect(url_for('admin_orders'))

    # Get customer info
    customer = db.get_user_by_id(order['user_id'])

    order_items = db.get_order_items(order['id'])

    return render_template('admin-order-detail.html',
                          order=order,
                          customer=customer,
                          order_items=order_items,
                          config=app.config)


@app.route('/admin/orders/<order_number>/update-status', methods=['POST'])
@admin_required
def admin_update_order_status(order_number):
    """Update order status"""
    new_status = request.form.get('status')
    send_email = request.form.get('send_email') == 'on'

    order = db.get_order_by_number(order_number)
    if not order:
        flash('Order not found.', 'error')
        return redirect(url_for('admin_orders'))

    # Update the status
    db.update_order_status(order['id'], new_status)

    # Send status update email if requested
    if send_email:
        from src.email_utils import send_order_status_update
        user = db.get_user_by_id(order['user_id'])
        if user:
            send_order_status_update(app.config, user['email'], order_number, new_status, user['name'])

    flash(f'Order {order_number} status updated to {new_status}.', 'success')
    return redirect(url_for('admin_order_detail', order_number=order_number))


@app.route('/admin/orders/<order_number>/delete', methods=['POST'])
@admin_required
def admin_delete_order(order_number):
    """Delete an order"""
    success, message = db.delete_order(order_number)

    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('admin_orders'))


@app.route('/admin/quotes')
@admin_required
def admin_quotes():
    """Admin page to view all quote requests (Custom Design, Cake Topper, Print Service)"""
    # Get all three types of requests
    custom_design_quotes = db.get_all_quote_requests()
    cake_topper_quotes = db.get_all_cake_topper_requests()
    print_service_quotes = db.get_all_print_service_requests()

    # Add type identifier to each quote
    for quote in custom_design_quotes:
        quote['request_type'] = 'Custom Design'
    for quote in cake_topper_quotes:
        quote['request_type'] = 'Cake Topper'
    for quote in print_service_quotes:
        quote['request_type'] = 'Print Service'

    # Combine all quotes
    all_quotes = custom_design_quotes + cake_topper_quotes + print_service_quotes

    # Sort by request_date (most recent first)
    all_quotes.sort(key=lambda x: x['request_date'], reverse=True)

    total_count = len(all_quotes)

    return render_template('admin-quotes.html',
                          quotes=all_quotes,
                          total_count=total_count,
                          config=app.config)


@app.route('/admin/quotes/update-status/<string:request_type>/<int:quote_id>', methods=['POST'])
@admin_required
def update_quote_status(request_type, quote_id):
    """Update quote request status for any type"""
    status = request.form.get('status')

    # Call the appropriate update method based on request type
    if request_type == 'custom_design':
        success, message = db.update_quote_status(quote_id, status)
    elif request_type == 'cake_topper':
        success, message = db.update_cake_topper_status(quote_id, status)
    elif request_type == 'print_service':
        success, message = db.update_print_service_status(quote_id, status)
    else:
        success = False
        message = "Invalid request type"

    if success:
        flash(f'Status updated to {status}!', 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('admin_quotes'))


@app.route('/admin/quotes/delete/<string:request_type>/<int:quote_id>', methods=['POST'])
@admin_required
def delete_quote_request(request_type, quote_id):
    """Delete quote request for any type"""
    # Call the appropriate delete method based on request type
    if request_type == 'custom_design':
        success, message = db.delete_quote_request(quote_id)
    elif request_type == 'cake_topper':
        success, message = db.delete_cake_topper_request(quote_id)
    elif request_type == 'print_service':
        success, message = db.delete_print_service_request(quote_id)
    else:
        success = False
        message = "Invalid request type"

    if success:
        flash('Quote request deleted successfully!', 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('admin_quotes'))


@app.route('/admin/export-csv')
@admin_required
def export_csv():
    """Export signups to CSV"""
    csv_content = db.export_to_csv()

    return Response(
        csv_content,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=signups.csv'}
    )


# ============================================================================
# COOKIE & CLAY CUTTERS - ADMIN ROUTES
# ============================================================================

# Categories Management
@app.route('/admin/cutters/categories')
@admin_required
def admin_cutter_categories():
    """Admin page to manage cutter categories"""
    categories = db.get_all_cutter_categories()
    return render_template('admin-cutter-categories.html',
                          categories=categories,
                          config=app.config)


@app.route('/admin/cutters/categories/add', methods=['POST'])
@admin_required
def admin_add_cutter_category():
    """Add a new cutter category"""
    name = request.form.get('name')
    description = request.form.get('description')

    success, message, category_id = db.add_cutter_category(name, description)

    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('admin_cutter_categories'))


@app.route('/admin/cutters/categories/edit/<int:category_id>', methods=['POST'])
@admin_required
def admin_edit_cutter_category(category_id):
    """Edit a cutter category"""
    name = request.form.get('name')
    description = request.form.get('description')

    success, message = db.update_cutter_category(category_id, name, description)

    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('admin_cutter_categories'))


@app.route('/admin/cutters/categories/delete/<int:category_id>', methods=['POST'])
@admin_required
def admin_delete_cutter_category(category_id):
    """Delete a cutter category"""
    success, message = db.delete_cutter_category(category_id)

    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('admin_cutter_categories'))


# Types Management
@app.route('/admin/cutters/types')
@admin_required
def admin_cutter_types():
    """Admin page to manage cutter types"""
    types = db.get_all_cutter_types()
    return render_template('admin-cutter-types.html',
                          types=types,
                          config=app.config)


@app.route('/admin/cutters/types/add', methods=['POST'])
@admin_required
def admin_add_cutter_type():
    """Add a new cutter type"""
    name = request.form.get('name')
    description = request.form.get('description')

    success, message, type_id = db.add_cutter_type(name, description)

    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('admin_cutter_types'))


@app.route('/admin/cutters/types/edit/<int:type_id>', methods=['POST'])
@admin_required
def admin_edit_cutter_type(type_id):
    """Edit a cutter type"""
    name = request.form.get('name')
    description = request.form.get('description')

    success, message = db.update_cutter_type(type_id, name, description)

    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('admin_cutter_types'))


@app.route('/admin/cutters/types/delete/<int:type_id>', methods=['POST'])
@admin_required
def admin_delete_cutter_type(type_id):
    """Delete a cutter type"""
    success, message = db.delete_cutter_type(type_id)

    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('admin_cutter_types'))


# Items Management
@app.route('/admin/cutters/items')
@admin_required
def admin_cutter_items():
    """Admin page to manage cutter items"""
    # Get filter parameters
    category_id = request.args.get('category_id', type=int)
    type_id = request.args.get('type_id', type=int)
    search_term = request.args.get('search')

    items = db.get_all_cutter_items(
        category_id=category_id,
        type_id=type_id,
        search_term=search_term,
        active_only=True
    )

    categories = db.get_all_cutter_categories()
    types = db.get_all_cutter_types()

    return render_template('admin-cutter-items.html',
                          items=items,
                          categories=categories,
                          types=types,
                          config=app.config)


@app.route('/admin/cutters/items/add', methods=['GET', 'POST'])
@admin_required
def admin_add_cutter_item_page():
    """Show form to add a new cutter item or handle form submission"""
    categories = db.get_all_cutter_categories()
    types = db.get_all_cutter_types()

    if request.method == 'POST':
        # Handle form submission
        name = request.form.get('name')
        description = request.form.get('description')
        price = float(request.form.get('price'))
        dimensions = request.form.get('dimensions')
        material = request.form.get('material')
        stock_status = request.form.get('stock_status')
        category_id = int(request.form.get('category_id'))
        type_id = int(request.form.get('type_id'))

        success, message, item_id, item_number = db.add_cutter_item(
            name, description, price, dimensions, material,
            stock_status, category_id, type_id
        )

        if success:
            # Handle photo uploads
            uploaded_files = request.files.getlist('photos')
            if uploaded_files and uploaded_files[0].filename:
                folder_path, _, _, _ = db.get_item_upload_path(item_id)
                os.makedirs(folder_path, exist_ok=True)

                for idx, file in enumerate(uploaded_files):
                    if file and file.filename:
                        # Create unique filename
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        filename = f"{timestamp}_{idx}_{file.filename}"
                        file_path = os.path.join(folder_path, filename)
                        file.save(file_path)

                        # Add to database (first photo is main)
                        is_main = (idx == 0)
                        db.add_item_photo(item_id, file_path, is_main=is_main, display_order=idx)

            flash(f'{message} Item #{item_number} created!', 'success')
            return redirect(url_for('admin_cutter_items'))
        else:
            flash(message, 'error')
            return render_template('admin-cutter-item-form.html',
                                  item=None,
                                  categories=categories,
                                  types=types,
                                  config=app.config)

    # GET request - show form
    return render_template('admin-cutter-item-form.html',
                          item=None,
                          categories=categories,
                          types=types,
                          config=app.config)


@app.route('/admin/cutters/items/edit/<int:item_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_cutter_item_page(item_id):
    """Show form to edit a cutter item or handle form submission"""
    item = db.get_cutter_item(item_id)

    if not item:
        flash('Item not found!', 'error')
        return redirect(url_for('admin_cutter_items'))

    categories = db.get_all_cutter_categories()
    types = db.get_all_cutter_types()

    if request.method == 'POST':
        # Handle form submission
        name = request.form.get('name')
        description = request.form.get('description')
        price = float(request.form.get('price'))
        dimensions = request.form.get('dimensions')
        material = request.form.get('material')
        stock_status = request.form.get('stock_status')
        category_id = int(request.form.get('category_id'))
        type_id = int(request.form.get('type_id'))

        success, message = db.update_cutter_item(
            item_id, name, description, price, dimensions,
            material, stock_status, category_id, type_id
        )

        if success:
            # Handle new photo uploads
            uploaded_files = request.files.getlist('photos')
            if uploaded_files and uploaded_files[0].filename:
                folder_path, _, _, _ = db.get_item_upload_path(item_id)
                os.makedirs(folder_path, exist_ok=True)

                # Get current photo count for display order
                existing_photos = db.get_item_photos(item_id)
                current_count = len(existing_photos)

                for idx, file in enumerate(uploaded_files):
                    if file and file.filename:
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        filename = f"{timestamp}_{idx}_{file.filename}"
                        file_path = os.path.join(folder_path, filename)
                        file.save(file_path)

                        # If this is the first photo overall, make it main
                        is_main = (current_count == 0 and idx == 0)
                        db.add_item_photo(item_id, file_path, is_main=is_main, display_order=current_count + idx)

            flash(message, 'success')
        else:
            flash(message, 'error')

        # Reload item to show updated data
        item = db.get_cutter_item(item_id)

    # GET request or after POST - show form
    return render_template('admin-cutter-item-form.html',
                          item=item,
                          categories=categories,
                          types=types,
                          config=app.config)


@app.route('/admin/cutters/items/copy/<int:item_id>', methods=['POST'])
@admin_required
def admin_copy_cutter_item(item_id):
    """Copy a cutter item"""
    success, message, new_item_id = db.copy_cutter_item(item_id)

    if success:
        flash(message, 'success')
        return redirect(url_for('admin_edit_cutter_item_page', item_id=new_item_id))
    else:
        flash(message, 'error')
        return redirect(url_for('admin_cutter_items'))


@app.route('/admin/cutters/items/delete/<int:item_id>', methods=['POST'])
@admin_required
def admin_delete_cutter_item(item_id):
    """Delete (deactivate) a cutter item"""
    success, message = db.delete_cutter_item(item_id)

    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('admin_cutter_items'))


# Photo Management
@app.route('/admin/cutters/photos/set-main/<int:item_id>/<int:photo_id>', methods=['POST'])
@admin_required
def admin_set_main_photo(item_id, photo_id):
    """Set a photo as the main photo for an item"""
    success, message = db.set_main_photo(item_id, photo_id)

    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('admin_edit_cutter_item_page', item_id=item_id))


@app.route('/admin/cutters/photos/delete/<int:photo_id>', methods=['POST'])
@admin_required
def admin_delete_photo(photo_id):
    """Delete a photo"""
    # Get the item_id before deleting (for redirect)
    # This is a bit hacky but works for now
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT item_id FROM cutter_item_photos WHERE id = ?', (photo_id,))
    result = cursor.fetchone()
    item_id = result['item_id'] if result else None
    conn.close()

    success, message = db.delete_item_photo(photo_id)

    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    if item_id:
        return redirect(url_for('admin_edit_cutter_item_page', item_id=item_id))
    else:
        return redirect(url_for('admin_cutter_items'))


@app.route('/version-check')
def version_check():
    """Check which version of the code is currently deployed"""
    import json
    version_info = get_version_info()
    return Response(
        json.dumps(version_info, indent=2),
        mimetype='application/json'
    )


@app.route('/admin/quotes/email/<string:request_type>/<int:quote_id>', methods=['POST'])
@admin_required
def email_customer(request_type, quote_id):
    """Send email to customer from admin panel"""
    subject = request.form.get('email_subject')
    message = request.form.get('email_message')

    # Get quote details based on request type
    if request_type == 'custom_design':
        quote_details = db.get_quote_request(quote_id)
    elif request_type == 'cake_topper':
        quote_details = db.get_cake_topper_request(quote_id)
    elif request_type == 'print_service':
        quote_details = db.get_print_service_request(quote_id)
    else:
        flash('Invalid request type', 'error')
        return redirect(url_for('admin_quotes'))

    if not quote_details:
        flash('Quote not found', 'error')
        return redirect(url_for('admin_quotes'))

    # Send email
    success, result_message = send_admin_reply_to_customer(
        app.config,
        quote_details['email'],
        quote_details['name'],
        subject,
        message
    )

    if success:
        flash(f'Email sent successfully to {quote_details["email"]}!', 'success')
    else:
        flash(f'Failed to send email: {result_message}', 'error')

    return redirect(url_for('admin_quotes'))


# ============================================================================
# SHOPPING CART ROUTES
# ============================================================================

@app.route('/cart/add', methods=['POST'])
def cart_add():
    """Add an item to the shopping cart"""
    from flask import jsonify

    try:
        data = request.get_json()
        item_id = data.get('item_id')
        quantity = data.get('quantity', 1)

        if not item_id:
            return jsonify({'success': False, 'message': 'Item ID required'}), 400

        # Get or create session ID
        session_id = get_session_id()

        # Use Flask-Login's current_user
        user_id = current_user.id if current_user.is_authenticated else None
        success, message = db.add_to_cart(session_id, item_id, quantity, user_id)

        if success:
            # Get updated cart count
            cart_count = db.get_cart_count(session_id, user_id)
            return jsonify({
                'success': True,
                'message': message,
                'cart_count': cart_count
            })
        else:
            return jsonify({'success': False, 'message': message}), 500

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/cart')
def cart():
    """Display shopping cart page"""
    session_id = get_session_id()
    user_id = current_user.id if current_user.is_authenticated else None

    # Get cart items
    cart_items = db.get_cart_items(session_id, user_id)

    # Calculate totals
    subtotal = sum(item['subtotal'] for item in cart_items)

    return render_template('cart.html',
                          cart_items=cart_items,
                          subtotal=subtotal,
                          config=app.config)


@app.route('/cart/update', methods=['POST'])
def cart_update():
    """Update quantity of item in cart"""
    from flask import jsonify

    try:
        data = request.get_json()
        cart_id = data.get('cart_id')
        quantity = data.get('quantity')

        if not cart_id or quantity is None:
            return jsonify({'success': False, 'message': 'Cart ID and quantity required'}), 400

        success, message = db.update_cart_quantity(cart_id, quantity)

        if success:
            # Get updated cart info
            session_id = get_session_id()
            user_id = current_user.id if current_user.is_authenticated else None
            cart_count = db.get_cart_count(session_id, user_id)
            cart_items = db.get_cart_items(session_id, user_id)
            subtotal = sum(item['subtotal'] for item in cart_items)

            return jsonify({
                'success': True,
                'message': message,
                'cart_count': cart_count,
                'subtotal': subtotal
            })
        else:
            return jsonify({'success': False, 'message': message}), 500

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/cart/remove', methods=['POST'])
def cart_remove():
    """Remove an item from cart"""
    from flask import jsonify

    try:
        data = request.get_json()
        cart_id = data.get('cart_id')

        if not cart_id:
            return jsonify({'success': False, 'message': 'Cart ID required'}), 400

        success, message = db.remove_from_cart(cart_id)

        if success:
            # Get updated cart info
            session_id = get_session_id()
            user_id = current_user.id if current_user.is_authenticated else None
            cart_count = db.get_cart_count(session_id, user_id)
            cart_items = db.get_cart_items(session_id, user_id)
            subtotal = sum(item['subtotal'] for item in cart_items)

            return jsonify({
                'success': True,
                'message': message,
                'cart_count': cart_count,
                'subtotal': subtotal
            })
        else:
            return jsonify({'success': False, 'message': message}), 500

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/cart/count')
def cart_count():
    """Get current cart count (for AJAX updates)"""
    from flask import jsonify

    session_id = get_session_id()
    user_id = current_user.id if current_user.is_authenticated else None
    count = db.get_cart_count(session_id, user_id)

    return jsonify({'count': count})


@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Checkout page with shipping address"""
    form = CheckoutForm()

    # Pre-fill form with user data if available
    if request.method == 'GET' and current_user.is_authenticated:
        user = db.get_user_by_id(current_user.id)
        if user:
            form.name.data = user.get('name', '')
            form.phone.data = user.get('phone', '')
            form.address.data = user.get('shipping_address', '')
            form.city.data = user.get('shipping_city', '')
            form.state.data = user.get('shipping_state', '')
            form.postal_code.data = user.get('shipping_postal_code', '')
            form.country.data = user.get('shipping_country', 'South Africa')

    if form.validate_on_submit():
        # Validate PUDO options
        if form.shipping_method.data == 'pudo':
            if not form.pudo_option.data:
                flash('Please select a PUDO delivery option!', 'danger')
                return render_template('checkout.html',
                                      form=form,
                                      cart_items=db.get_cart_items(get_session_id(), current_user.id),
                                      subtotal=sum(item['subtotal'] for item in db.get_cart_items(get_session_id(), current_user.id)),
                                      config=app.config)

            # Check if address or locker location is required
            if form.pudo_option.data in ['locker_to_door', 'kiosk_to_door']:
                # to-Door options require full address
                if not form.address.data or not form.city.data or not form.state.data or not form.postal_code.data:
                    flash('Please provide a complete delivery address for door delivery!', 'danger')
                    return render_template('checkout.html',
                                          form=form,
                                          cart_items=db.get_cart_items(get_session_id(), current_user.id),
                                          subtotal=sum(item['subtotal'] for item in db.get_cart_items(get_session_id(), current_user.id)),
                                          config=app.config)
            else:
                # Locker/Kiosk options require locker location
                if not form.locker_location.data:
                    flash('Please provide your PUDO Locker/Kiosk location!', 'danger')
                    return render_template('checkout.html',
                                          form=form,
                                          cart_items=db.get_cart_items(get_session_id(), current_user.id),
                                          subtotal=sum(item['subtotal'] for item in db.get_cart_items(get_session_id(), current_user.id)),
                                          config=app.config)

        # Prepare shipping info
        is_door_delivery = (form.shipping_method.data == 'pudo' and
                           form.pudo_option.data in ['locker_to_door', 'kiosk_to_door'])

        shipping_info = {
            'method': form.shipping_method.data,
            'pudo_option': form.pudo_option.data if form.shipping_method.data == 'pudo' else None,
            'locker_location': form.locker_location.data if form.shipping_method.data == 'pudo' else None,
            'address': form.address.data if is_door_delivery else None,
            'city': form.city.data if is_door_delivery else None,
            'state': form.state.data if is_door_delivery else None,
            'postal_code': form.postal_code.data if is_door_delivery else None,
            'country': form.country.data if is_door_delivery else 'South Africa'
        }

        # Update user's info for future use
        user_update = {
            'name': form.name.data,
            'phone': form.phone.data
        }

        if is_door_delivery:
            user_update.update({
                'shipping_address': form.address.data,
                'shipping_city': form.city.data,
                'shipping_state': form.state.data,
                'shipping_postal_code': form.postal_code.data,
                'shipping_country': form.country.data
            })

        db.update_user(current_user.id, user_update)

        # Create order
        success, message, order_number = db.create_order(current_user.id, shipping_info)

        if success:
            # Get order details for email
            order = db.get_order_by_number(order_number)

            # Send order confirmation emails
            try:
                send_order_confirmation(
                    app.config,
                    order,
                    current_user.email,
                    current_user.name
                )
            except Exception as e:
                print(f"Failed to send order confirmation email: {str(e)}")
                # Don't fail the order if email fails

            flash(f'Order {order_number} created successfully!', 'success')
            return redirect(url_for('order_confirmation', order_number=order_number))
        else:
            flash(message, 'danger')
            return redirect(url_for('cart'))

    # Get cart items for display
    session_id = get_session_id()
    cart_items = db.get_cart_items(session_id, current_user.id)
    subtotal = sum(item['subtotal'] for item in cart_items)

    # Check if cart is empty
    if not cart_items:
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('printing_3d'))

    return render_template('checkout.html',
                          form=form,
                          cart_items=cart_items,
                          subtotal=subtotal,
                          config=app.config)


@app.route('/order/<order_number>')
@login_required
def order_confirmation(order_number):
    """Order confirmation page"""
    order = db.get_order_by_number(order_number)

    if not order or order['user_id'] != current_user.id:
        flash('Order not found!', 'danger')
        return redirect(url_for('index'))

    order_items = db.get_order_items(order['id'])

    return render_template('order_confirmation.html',
                          order=order,
                          order_items=order_items,
                          config=app.config)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
