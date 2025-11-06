from flask import Flask, render_template, request, redirect, url_for, flash, session, Response, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from functools import wraps
from src.config import Config
from src.database import Database
from src.forms import EmailSignupForm, RegistrationForm, LoginForm, EditProfileForm, CheckoutForm, ChangePasswordForm
from src.email_utils import send_quote_notification, send_customer_confirmation, send_signup_confirmation, send_cake_topper_notification, send_print_service_notification, send_admin_reply_to_customer, send_order_confirmation
from scripts.version_check import get_version_info
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import random
import re

# Configuration for file uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Utility function to sanitize filenames
def sanitize_filename(filename):
    """
    Sanitize filename to remove problematic characters that might cause issues
    with web servers or file systems.
    - Replaces spaces with underscores
    - Removes or replaces special characters
    - Preserves file extension
    """
    if not filename:
        return filename

    # Split filename and extension
    name, ext = os.path.splitext(filename)

    # Replace spaces with underscores
    name = name.replace(' ', '_')

    # Remove or replace other problematic characters
    # Keep only alphanumeric, underscores, hyphens, and periods
    name = re.sub(r'[^\w\-.]', '_', name)

    # Remove consecutive underscores
    name = re.sub(r'_+', '_', name)

    # Remove leading/trailing underscores
    name = name.strip('_')

    return name + ext

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
    """Decorator to require admin access (either old admin login or user with is_admin flag)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if logged in via old admin system OR via user system with admin flag
        if session.get('admin_logged_in'):
            return f(*args, **kwargs)
        elif current_user.is_authenticated and current_user.is_admin:
            return f(*args, **kwargs)
        else:
            flash('You need admin privileges to access this page.', 'error')
            return redirect(url_for('login'))
    return decorated_function


@app.route('/')
def index():
    """Main landing page"""
    form = EmailSignupForm()

    # Get stats for homepage counters (only public products, not custom quotes)
    total_products = len(db.get_all_cutter_items(active_only=True, public_categories_only=True))
    total_customers = db.get_signup_count()  # Using email signups as customer count for now

    # Calculate new products this month (created in last 30 days)
    from datetime import datetime, timedelta
    thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    all_products = db.get_all_cutter_items(active_only=True, public_categories_only=True)
    new_products = len([p for p in all_products if p['created_date'] and p['created_date'] >= thirty_days_ago])

    return render_template('index.html',
                          form=form,
                          config=app.config,
                          total_products=total_products,
                          total_customers=total_customers,
                          new_products=new_products)


@app.route('/privacy-policy')
def privacy_policy():
    """Privacy Policy page"""
    from datetime import datetime
    last_updated = datetime.now().strftime('%B %d, %Y')
    return render_template('privacy-policy.html',
                          config=app.config,
                          last_updated=last_updated)


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

                # Migrate guest carts to user if exists
                session_id = get_session_id()
                db.migrate_guest_cart_to_user(session_id, user_id)
                db.migrate_guest_candles_soaps_cart_to_user(session_id, user_id)

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

            # Migrate guest carts to user if exists
            session_id = get_session_id()
            db.migrate_guest_cart_to_user(session_id, user_dict['id'])
            db.migrate_guest_candles_soaps_cart_to_user(session_id, user_dict['id'])

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
    password_form = ChangePasswordForm()

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

    return render_template('account.html', form=form, password_form=password_form, config=app.config)


@app.route('/orders-quotes')
@login_required
def orders_quotes():
    """User orders and quotes tracking page"""
    # Get user's orders
    orders = db.get_user_orders(current_user.id)

    # Get user's quotes
    quotes = db.get_user_quotes(current_user.email)

    return render_template('orders_quotes.html', orders=orders, quotes=quotes, config=app.config)


@app.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Handle password change request"""
    form = ChangePasswordForm()

    if form.validate_on_submit():
        success, message = db.change_password(
            current_user.id,
            form.current_password.data,
            form.new_password.data
        )

        if success:
            flash(message, 'success')
        else:
            flash(message, 'error')
    else:
        # Show validation errors
        for field, errors in form.errors.items():
            for error in errors:
                flash(error, 'error')

    return redirect(url_for('account'))


@app.route('/quote/delete/<int:quote_id>', methods=['POST'])
@login_required
def delete_quote(quote_id):
    """Delete a quote request (user can only delete their own quotes)"""
    try:
        # Get the quote to verify ownership
        quote = db.get_quote_request(quote_id)

        if not quote:
            return jsonify({'success': False, 'message': 'Quote not found'}), 404

        # Verify the quote belongs to the current user
        if quote['email'] != current_user.email:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403

        # Delete the quote
        success, message = db.delete_quote_request(quote_id)

        return jsonify({'success': success, 'message': message})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/quote/upload-photos', methods=['POST'])
@login_required
def upload_quote_photos():
    """Upload photos for a quote request"""
    try:
        quote_id = request.form.get('quote_id')
        if not quote_id:
            return jsonify({'success': False, 'message': 'Quote ID is required'}), 400

        # Get the quote to verify ownership
        quote = db.get_quote_request(int(quote_id))

        if not quote:
            return jsonify({'success': False, 'message': 'Quote not found'}), 404

        # Verify the quote belongs to the current user
        if quote['email'] != current_user.email:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403

        # Get uploaded files
        if 'photos' not in request.files:
            return jsonify({'success': False, 'message': 'No photos uploaded'}), 400

        files = request.files.getlist('photos')

        if len(files) == 0:
            return jsonify({'success': False, 'message': 'No photos selected'}), 400

        if len(files) > 5:
            return jsonify({'success': False, 'message': 'Maximum 5 photos allowed'}), 400

        # Save photos
        upload_folder = os.path.join('static', 'uploads', 'quote_photos')
        os.makedirs(upload_folder, exist_ok=True)

        saved_files = []
        for file in files:
            if file and allowed_file(file.filename):
                # Generate unique filename
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                original_filename = secure_filename(file.filename)
                filename = f"{timestamp}_{quote_id}_{original_filename}"
                filepath = os.path.join(upload_folder, filename)

                # Save file
                file.save(filepath)
                saved_files.append(filename)

        # Update quote with new image paths
        existing_images = quote.get('reference_images', '')
        if existing_images:
            all_images = existing_images + ',' + ','.join(saved_files)
        else:
            all_images = ','.join(saved_files)

        # Update the quote in database
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE quote_requests
            SET reference_images = ?
            WHERE id = ?
        ''', (all_images, quote_id))
        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': f'{len(saved_files)} photo(s) uploaded successfully'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


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

    # Fetch all cutter items from database (only from public categories to exclude custom quotes)
    items = db.get_all_cutter_items(public_categories_only=True)

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

    # Get categories and types for filters (only public categories)
    categories = db.get_all_cutter_categories(public_only=True)
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
    email = request.form.get('email', '').lower().strip()
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
                # Sanitize the original filename to remove problematic characters
                sanitized_name = sanitize_filename(file.filename)
                # Create a unique filename with timestamp
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{sanitized_name}"
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
    email = request.form.get('email', '').lower().strip()
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
                # Sanitize the original filename to remove problematic characters
                sanitized_name = sanitize_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{sanitized_name}"
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
    email = request.form.get('email', '').lower().strip()
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
                # Sanitize the original filename to remove problematic characters
                sanitized_name = sanitize_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{sanitized_name}"
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
            session.permanent = True  # Make session persistent across browser sessions
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


@app.route('/admin/signups/bulk-email-stats')
@admin_required
def get_bulk_email_stats_route():
    """API endpoint to get count of recipients for bulk email"""
    interest_filter = request.args.get('interest', 'all')

    if interest_filter == 'all':
        interest_filter = None

    # Get signups for the filter and count them
    signups = db.get_signups_by_interest(interest_filter)
    count = len(signups) if signups else 0

    return jsonify({
        'success': True,
        'count': count
    })


@app.route('/admin/signups/send-bulk-email', methods=['POST'])
@admin_required
def send_bulk_email_route():
    """Send bulk email to signups filtered by interest"""
    from src.email_utils import send_bulk_email

    interest_filter = request.form.get('interest_filter', 'all')
    subject = request.form.get('subject', '').strip()
    message = request.form.get('message', '').strip()

    # Validate inputs
    if not subject or not message:
        flash('Subject and message are required.', 'error')
        return redirect(url_for('admin_signups'))

    # Get recipients
    if interest_filter == 'all':
        interest_filter = None

    signups = db.get_signups_by_interest(interest_filter)

    if not signups:
        flash('No active subscribers found for the selected filter.', 'warning')
        return redirect(url_for('admin_signups'))

    # Format recipients as list of tuples (email, name, unsubscribe_token)
    recipients = [(s['email'], s['name'], s['unsubscribe_token']) for s in signups]

    # Send bulk email
    success_count, failed_count, result_message = send_bulk_email(
        app.config,
        recipients,
        subject,
        message,
        interest_filter=interest_filter,
        include_logo=True
    )

    # Show results
    if success_count > 0:
        flash(f'Successfully sent {success_count} email(s)!', 'success')

    if failed_count > 0:
        flash(f'Failed to send {failed_count} email(s). Check logs for details.', 'error')

    return redirect(url_for('admin_signups'))


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

    # Auto-generate invoice when status changes to confirmed or awaiting_payment
    if new_status in ['confirmed', 'awaiting_payment'] and not order.get('invoice_number'):
        from src.invoice_utils import generate_invoice_pdf

        # Generate invoice number
        success, invoice_number = db.generate_invoice_number(order_number)
        if success:
            order['invoice_number'] = invoice_number

            # Get customer and items for PDF generation
            customer = db.get_user_by_id(order['user_id'])
            order_items = db.get_order_items(order['id'])

            # Generate PDF
            pdf_success, pdf_result = generate_invoice_pdf(order, customer, order_items, app.config)
            if pdf_success:
                flash(f'Invoice {invoice_number} auto-generated!', 'info')

    # Send status update email if requested
    if send_email:
        from src.email_utils import send_order_status_update
        user = db.get_user_by_id(order['user_id'])
        if user:
            # Pass shipping method for context-aware messaging
            send_order_status_update(app.config, user['email'], order_number, new_status, user['name'], order.get('shipping_method'))

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


@app.route('/admin/orders/<order_number>/generate-invoice', methods=['POST'])
@admin_required
def admin_generate_invoice(order_number):
    """Generate PDF invoice for an order"""
    from src.invoice_utils import generate_invoice_pdf

    # Get order details
    order = db.get_order_by_number(order_number)
    if not order:
        flash('Order not found.', 'error')
        return redirect(url_for('admin_orders'))

    # Get customer and items
    customer = db.get_user_by_id(order['user_id'])
    order_items = db.get_order_items(order['id'])

    # Generate invoice number if not exists
    if not order.get('invoice_number'):
        success, invoice_number = db.generate_invoice_number(order_number)
        if not success:
            flash(f'Failed to generate invoice number: {invoice_number}', 'error')
            return redirect(url_for('admin_order_detail', order_number=order_number))
        order['invoice_number'] = invoice_number

    # Generate PDF
    success, result = generate_invoice_pdf(order, customer, order_items, app.config)

    if success:
        flash(f'Invoice {order["invoice_number"]} generated successfully!', 'success')
    else:
        flash(f'Failed to generate invoice: {result}', 'error')

    return redirect(url_for('admin_order_detail', order_number=order_number))


@app.route('/admin/orders/<order_number>/download-invoice')
@admin_required
def admin_download_invoice(order_number):
    """Download invoice PDF"""
    from flask import send_file
    from src.invoice_utils import get_invoice_path, invoice_exists

    # Get order to check invoice number
    order = db.get_order_by_number(order_number)
    if not order or not order.get('invoice_number'):
        flash('Invoice not found. Please generate it first.', 'error')
        return redirect(url_for('admin_order_detail', order_number=order_number))

    invoice_path = get_invoice_path(order['invoice_number'])

    if not invoice_exists(order['invoice_number']):
        flash('Invoice PDF not found. Please generate it again.', 'error')
        return redirect(url_for('admin_order_detail', order_number=order_number))

    return send_file(invoice_path, as_attachment=True, download_name=f"{order['invoice_number']}.pdf")


@app.route('/admin/orders/<order_number>/send-invoice-email', methods=['POST'])
@admin_required
def admin_send_invoice_email(order_number):
    """Send invoice PDF via email to customer"""
    from src.email_utils import send_invoice_email
    from src.invoice_utils import get_invoice_path

    # Get order details
    order = db.get_order_by_number(order_number)
    if not order:
        flash('Order not found.', 'error')
        return redirect(url_for('admin_orders'))

    if not order.get('invoice_number'):
        flash('Invoice not generated yet. Please generate it first.', 'error')
        return redirect(url_for('admin_order_detail', order_number=order_number))

    # Get customer details
    customer = db.get_user_by_id(order['user_id'])
    if not customer:
        flash('Customer not found.', 'error')
        return redirect(url_for('admin_order_detail', order_number=order_number))

    # Get invoice path
    invoice_path = get_invoice_path(order['invoice_number'])

    # Send email
    success, message = send_invoice_email(
        app.config,
        customer['email'],
        customer['name'],
        order_number,
        order['invoice_number'],
        invoice_path
    )

    if success:
        flash(f'Invoice emailed to {customer["email"]}!', 'success')
    else:
        flash(f'Failed to send invoice email: {message}', 'error')

    return redirect(url_for('admin_order_detail', order_number=order_number))


@app.route('/admin/users')
@admin_required
def admin_users():
    """Admin page to view and manage all registered users"""
    # Get all users with order statistics
    users = db.get_all_users()

    # Get user statistics
    stats = db.get_user_statistics()

    return render_template('admin-users.html',
                          users=users,
                          stats=stats,
                          config=app.config)


@app.route('/admin/users/<int:user_id>/edit', methods=['POST'])
@admin_required
def admin_edit_user(user_id):
    """Admin function to edit user details"""
    name = request.form.get('name')
    email = request.form.get('email', '').lower().strip()
    phone = request.form.get('phone')

    if not name or not email:
        flash('Name and email are required!', 'error')
        return redirect(url_for('admin_users'))

    update_data = {
        'name': name,
        'email': email,
        'phone': phone if phone else None
    }

    success, message = db.update_user(user_id, update_data)

    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('admin_users'))


@app.route('/admin/users/<int:user_id>/reset-password', methods=['POST'])
@admin_required
def admin_reset_password(user_id):
    """Admin function to reset user password"""
    success, message, temp_password = db.admin_reset_user_password(user_id)

    if success:
        # Get user details for email
        user = db.get_user_by_id(user_id)
        if user:
            # Send email with temporary password
            try:
                from src.email_utils import send_admin_reply_to_customer
                email_success, email_message = send_admin_reply_to_customer(
                    app.config,
                    user['email'],
                    user['name'],
                    'Your Password Has Been Reset',
                    f"""Your password has been reset by an administrator.

Your temporary password is: {temp_password}

Please log in with this temporary password and change it immediately in your account settings.

For security reasons, we recommend using a strong password with at least 6 characters.
"""
                )

                if email_success:
                    flash(f'{message} Temporary password sent to {user["email"]}', 'success')
                else:
                    flash(f'{message} Temporary password: {temp_password} (Email failed to send)', 'warning')
            except Exception as e:
                flash(f'{message} Temporary password: {temp_password} (Unable to send email)', 'warning')
        else:
            flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('admin_users'))


@app.route('/admin/users/<int:user_id>/toggle-status', methods=['POST'])
@admin_required
def admin_toggle_status(user_id):
    """Admin function to toggle user active status"""
    success, message, new_status = db.admin_toggle_user_status(user_id)

    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('admin_users'))


@app.route('/admin/users/<int:user_id>/toggle-admin', methods=['POST'])
@admin_required
def admin_toggle_admin(user_id):
    """Admin function to toggle user admin privileges"""
    success, message, new_status = db.admin_toggle_admin_status(user_id)

    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('admin_users'))


@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    """Admin function to delete a user"""
    success, message = db.admin_delete_user(user_id)

    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('admin_users'))


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
                        # Sanitize and create unique filename
                        sanitized_name = sanitize_filename(file.filename)
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        filename = f"{timestamp}_{idx}_{sanitized_name}"
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
                        # Sanitize and create unique filename
                        sanitized_name = sanitize_filename(file.filename)
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        filename = f"{timestamp}_{idx}_{sanitized_name}"
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


# ========================================
# CANDLES & SOAPS ADMIN ROUTES
# ========================================

# Category Management
@app.route('/admin/candles-soaps/categories')
@admin_required
def admin_candles_soaps_categories():
    """Admin page to manage candles & soaps categories"""
    categories = db.get_all_candles_soaps_categories(active_only=False)

    # Add product count to each category
    for category in categories:
        products = db.get_all_candles_soaps_products(category_id=category['id'], active_only=False)
        category['product_count'] = len(products)

    return render_template('admin-candles-soaps-categories.html',
                         categories=categories,
                         config=app.config)


@app.route('/admin/candles-soaps/categories/add', methods=['POST'])
@admin_required
def admin_add_candles_soaps_category():
    """Add a new candles & soaps category"""
    name = request.form.get('name')
    description = request.form.get('description')
    display_order = request.form.get('display_order', 0)

    if not name:
        flash('Category name is required.', 'error')
        return redirect(url_for('admin_candles_soaps_categories'))

    success, message, category_id = db.add_candles_soaps_category(name, description, display_order)

    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('admin_candles_soaps_categories'))


@app.route('/admin/candles-soaps/categories/<int:category_id>/edit', methods=['POST'])
@admin_required
def admin_edit_candles_soaps_category(category_id):
    """Edit a candles & soaps category"""
    name = request.form.get('name')
    description = request.form.get('description')
    display_order = request.form.get('display_order', 0)
    is_active = request.form.get('is_active', 1)

    if not name:
        flash('Category name is required.', 'error')
        return redirect(url_for('admin_candles_soaps_categories'))

    success, message = db.update_candles_soaps_category(category_id, name, description, display_order, is_active)

    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('admin_candles_soaps_categories'))


@app.route('/admin/candles-soaps/categories/<int:category_id>/delete', methods=['POST'])
@admin_required
def admin_delete_candles_soaps_category(category_id):
    """Delete a candles & soaps category"""
    success, message = db.delete_candles_soaps_category(category_id)

    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('admin_candles_soaps_categories'))


# Product Management
@app.route('/admin/candles-soaps/products')
@admin_required
def admin_candles_soaps_products():
    """Admin page to manage candles & soaps products"""
    # Get filter parameters
    category_id = request.args.get('category_id')
    stock_status = request.args.get('stock_status')
    search = request.args.get('search', '')

    # Get all products (only active by default)
    products = db.get_all_candles_soaps_products(
        category_id=int(category_id) if category_id else None,
        active_only=True
    )

    # Apply search filter
    if search:
        search_lower = search.lower()
        products = [p for p in products if
                   search_lower in p['name'].lower() or
                   search_lower in (p['product_code'] or '').lower()]

    # Apply stock status filter
    if stock_status:
        if stock_status == 'in_stock':
            products = [p for p in products if p['stock_quantity'] > p['low_stock_threshold']]
        elif stock_status == 'low_stock':
            products = [p for p in products if 0 < p['stock_quantity'] <= p['low_stock_threshold']]
        elif stock_status == 'out_of_stock':
            products = [p for p in products if p['stock_quantity'] == 0]

    # Get low stock products for stats
    low_stock_products = db.get_low_stock_candles_soaps_products()

    # Get categories for filter dropdown
    categories = db.get_all_candles_soaps_categories(active_only=False)

    return render_template('admin-candles-soaps-products.html',
                         products=products,
                         low_stock_products=low_stock_products,
                         categories=categories,
                         config=app.config)


@app.route('/admin/candles-soaps/products/add')
@admin_required
def admin_add_candles_soaps_product():
    """Show form to add a new candles & soaps product"""
    categories = db.get_all_candles_soaps_categories(active_only=True)
    return render_template('admin-candles-soaps-product-form.html',
                         product=None,
                         categories=categories,
                         photos=[],
                         config=app.config)


@app.route('/admin/candles-soaps/products/create', methods=['POST'])
@admin_required
def admin_create_candles_soaps_product():
    """Create a new candles & soaps product"""
    product_data = {
        'name': request.form.get('name'),
        'description': request.form.get('description'),
        'category_id': request.form.get('category_id'),
        'price': request.form.get('price'),
        'stock_quantity': request.form.get('stock_quantity', 0),
        'low_stock_threshold': request.form.get('low_stock_threshold', 5),
        'weight_grams': request.form.get('weight_grams') or None,
        'dimensions': request.form.get('dimensions') or None,
        'scent': request.form.get('scent') or None,
        'color': request.form.get('color') or None,
        'burn_time_hours': request.form.get('burn_time_hours') or None,
        'ingredients': request.form.get('ingredients') or None,
        'is_active': request.form.get('is_active', 1)
    }

    # Validate required fields
    if not product_data['name'] or not product_data['category_id'] or not product_data['price']:
        flash('Name, category, and price are required.', 'error')
        return redirect(url_for('admin_add_candles_soaps_product'))

    success, message, product_id = db.add_candles_soaps_product(product_data)

    if success:

        # Handle photo uploads
        uploaded_files = request.files.getlist('photos')
        if uploaded_files and uploaded_files[0].filename:
            # Get upload path for candles & soaps products
            folder_path = os.path.join('static', 'uploads', 'candles_soaps', str(product_id))
            os.makedirs(folder_path, exist_ok=True)

            for idx, file in enumerate(uploaded_files):
                if file and file.filename:
                    # Create unique filename with sanitized extension
                    sanitized_name = sanitize_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    ext = os.path.splitext(sanitized_name)[1]
                    filename = f"{timestamp}_{idx}{ext}"
                    file_path = os.path.join(folder_path, filename)
                    file.save(file_path)

                    # Add to database (first photo is main)
                    is_main = (idx == 0)
                    photo_success, photo_message, photo_id = db.add_candles_soaps_product_photo(product_id, file_path, is_main=is_main)
                    if not photo_success:
                        flash(f"Warning: {photo_message}", 'warning')

        flash(message, 'success')
        return redirect(url_for('admin_candles_soaps_products'))
    else:
        flash(message, 'error')
        return redirect(url_for('admin_add_candles_soaps_product'))


@app.route('/admin/candles-soaps/products/<int:product_id>/edit')
@admin_required
def admin_edit_candles_soaps_product(product_id):
    """Show form to edit a candles & soaps product"""
    product = db.get_candles_soaps_product(product_id)

    if not product:
        flash('Product not found.', 'error')
        return redirect(url_for('admin_candles_soaps_products'))

    categories = db.get_all_candles_soaps_categories(active_only=False)
    photos = db.get_candles_soaps_product_photos(product_id)

    return render_template('admin-candles-soaps-product-form.html',
                         product=product,
                         categories=categories,
                         photos=photos,
                         config=app.config)


@app.route('/admin/candles-soaps/products/<int:product_id>/update', methods=['POST'])
@admin_required
def admin_update_candles_soaps_product(product_id):
    """Update a candles & soaps product"""
    product_data = {
        'name': request.form.get('name'),
        'description': request.form.get('description'),
        'category_id': request.form.get('category_id'),
        'price': request.form.get('price'),
        'stock_quantity': request.form.get('stock_quantity', 0),
        'low_stock_threshold': request.form.get('low_stock_threshold', 5),
        'weight_grams': request.form.get('weight_grams') or None,
        'dimensions': request.form.get('dimensions') or None,
        'scent': request.form.get('scent') or None,
        'color': request.form.get('color') or None,
        'burn_time_hours': request.form.get('burn_time_hours') or None,
        'ingredients': request.form.get('ingredients') or None,
        'is_active': request.form.get('is_active', 1)
    }

    # Validate required fields
    if not product_data['name'] or not product_data['category_id'] or not product_data['price']:
        flash('Name, category, and price are required.', 'error')
        return redirect(url_for('admin_edit_candles_soaps_product', product_id=product_id))

    success, message = db.update_candles_soaps_product(product_id, product_data)

    if success:
        # Handle new photo uploads
        uploaded_files = request.files.getlist('photos')
        if uploaded_files and uploaded_files[0].filename:
            # Get upload path for candles & soaps products
            folder_path = os.path.join('static', 'uploads', 'candles_soaps', str(product_id))
            os.makedirs(folder_path, exist_ok=True)

            # Get current photo count to determine if we need to set first uploaded as main
            existing_photos = db.get_candles_soaps_product_photos(product_id)
            has_main = any(photo['is_main'] for photo in existing_photos)

            for idx, file in enumerate(uploaded_files):
                if file and file.filename:
                    # Create unique filename with sanitized extension
                    sanitized_name = sanitize_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    ext = os.path.splitext(sanitized_name)[1]
                    filename = f"{timestamp}_{idx}{ext}"
                    file_path = os.path.join(folder_path, filename)
                    file.save(file_path)

                    # Set first photo as main if there are no existing photos with main flag
                    is_main = (idx == 0 and not has_main)
                    db.add_candles_soaps_product_photo(product_id, file_path, is_main=is_main)

        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('admin_edit_candles_soaps_product', product_id=product_id))


@app.route('/admin/candles-soaps/products/<int:product_id>/delete', methods=['POST'])
@admin_required
def admin_delete_candles_soaps_product(product_id):
    """Delete a candles & soaps product"""
    success, message = db.delete_candles_soaps_product(product_id)

    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('admin_candles_soaps_products'))


# Stock Management
@app.route('/admin/candles-soaps/products/<int:product_id>/stock/adjust', methods=['POST'])
@admin_required
def admin_adjust_candles_soaps_stock(product_id):
    """Adjust stock for a candles & soaps product"""
    change_amount = request.form.get('change_amount')
    reason = request.form.get('reason')

    if not change_amount or not reason:
        flash('Change amount and reason are required.', 'error')
        return redirect(url_for('admin_candles_soaps_products'))

    try:
        change_amount = int(change_amount)
    except ValueError:
        flash('Invalid change amount.', 'error')
        return redirect(url_for('admin_candles_soaps_products'))

    # Get current user ID if available
    created_by = current_user.id if current_user.is_authenticated else None

    success, message = db.update_candles_soaps_stock(
        product_id,
        change_amount,
        reason,
        order_id=None,
        created_by=created_by
    )

    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('admin_candles_soaps_products'))


# Photo Management
@app.route('/admin/candles-soaps/products/<int:product_id>/photos/upload', methods=['POST'])
@admin_required
def admin_upload_candles_soaps_photo(product_id):
    """Upload a photo for a candles & soaps product"""
    from werkzeug.utils import secure_filename

    # Check if photo was uploaded
    if 'photo' not in request.files:
        flash('No photo uploaded.', 'error')
        return redirect(url_for('admin_edit_candles_soaps_product', product_id=product_id))

    photo = request.files['photo']

    if photo.filename == '':
        flash('No photo selected.', 'error')
        return redirect(url_for('admin_edit_candles_soaps_product', product_id=product_id))

    # Check file extension
    allowed_extensions = {'jpg', 'jpeg', 'png', 'webp'}
    if '.' not in photo.filename or photo.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        flash('Invalid file type. Allowed: JPG, PNG, WebP', 'error')
        return redirect(url_for('admin_edit_candles_soaps_product', product_id=product_id))

    # Get product details for folder structure
    product = db.get_candles_soaps_product(product_id)
    if not product:
        flash('Product not found.', 'error')
        return redirect(url_for('admin_candles_soaps_products'))

    # Get category name for folder
    category = db.get_candles_soaps_category(product['category_id'])
    category_name = secure_filename(category['name']) if category else 'uncategorized'

    # Create folder structure: static/uploads/candles_soaps/CATEGORY_NAME/PRODUCT_CODE/
    upload_folder = os.path.join('static', 'uploads', 'candles_soaps', category_name, product['product_code'])
    os.makedirs(upload_folder, exist_ok=True)

    # Generate unique filename with sanitization
    sanitized_name = sanitize_filename(photo.filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_filename = f"{timestamp}_{sanitized_name}"

    # Save file
    file_path = os.path.join(upload_folder, unique_filename)
    photo.save(file_path)

    # Add to database
    is_main = request.form.get('is_main') == '1'
    success, message = db.add_candles_soaps_product_photo(product_id, file_path, is_main=is_main)

    if success:
        flash('Photo uploaded successfully!', 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('admin_edit_candles_soaps_product', product_id=product_id))


@app.route('/admin/candles-soaps/products/<int:product_id>/photos/<int:photo_id>/set-main', methods=['POST'])
@admin_required
def admin_set_main_candles_soaps_photo(product_id, photo_id):
    """Set a photo as the main photo for a candles & soaps product"""
    success, message = db.set_candles_soaps_main_photo(product_id, photo_id)

    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('admin_edit_candles_soaps_product', product_id=product_id))


@app.route('/admin/candles-soaps/products/<int:product_id>/photos/<int:photo_id>/delete', methods=['POST'])
@admin_required
def admin_delete_candles_soaps_photo(product_id, photo_id):
    """Delete a photo for a candles & soaps product"""
    success, message = db.delete_candles_soaps_product_photo(photo_id)

    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('admin_edit_candles_soaps_product', product_id=product_id))


# ========================================
# END CANDLES & SOAPS ADMIN ROUTES
# ========================================


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

    # Handle file attachments
    attachments = []
    uploaded_files = request.files.getlist('email_attachments')
    if uploaded_files:
        for file in uploaded_files:
            if file and file.filename:
                # Sanitize filename before attaching to email
                sanitized_name = sanitize_filename(file.filename)
                # Read file into memory
                file_data = file.read()

                # Get MIME type based on file extension
                import mimetypes
                mime_type, _ = mimetypes.guess_type(sanitized_name)
                if not mime_type:
                    mime_type = 'application/octet-stream'

                attachments.append({
                    'filename': sanitized_name,
                    'data': file_data,
                    'mime_type': mime_type
                })

    # Send email
    success, result_message = send_admin_reply_to_customer(
        app.config,
        quote_details['email'],
        quote_details['name'],
        subject,
        message,
        attachments=attachments
    )

    if success:
        flash(f'Email sent successfully to {quote_details["email"]}!', 'success')
    else:
        flash(f'Failed to send email: {result_message}', 'error')

    return redirect(url_for('admin_quotes'))


@app.route('/admin/quotes/convert-to-sale/<string:request_type>/<int:quote_id>', methods=['POST'])
@admin_required
def convert_quote_to_sale(request_type, quote_id):
    """Convert a quote to a sale by adding to customer's cart"""
    from werkzeug.utils import secure_filename

    item_name = request.form.get('item_name')
    item_price = request.form.get('item_price')
    item_description = request.form.get('item_description', 'Custom quote item')

    if not item_name or not item_price:
        flash('Item name and price are required!', 'error')
        return redirect(url_for('admin_quotes'))

    try:
        item_price = float(item_price)
    except ValueError:
        flash('Invalid price format!', 'error')
        return redirect(url_for('admin_quotes'))

    # Convert quote to sale
    success, message, result_data = db.convert_quote_to_sale(
        request_type,
        quote_id,
        item_name,
        item_price,
        item_description
    )

    if success:
        # Handle photo upload if provided
        if 'item_photo' in request.files:
            photo = request.files['item_photo']

            if photo and photo.filename:
                # Get the item_id from result_data
                item_id = result_data.get('item_id')

                if item_id:
                    # Sanitize the filename
                    sanitized_name = sanitize_filename(photo.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"{timestamp}_{sanitized_name}"

                    # Create upload directory if it doesn't exist
                    upload_dir = os.path.join('static', 'uploads', 'cutter_items')
                    os.makedirs(upload_dir, exist_ok=True)

                    # Save the file
                    file_path = os.path.join(upload_dir, filename)
                    photo.save(file_path)

                    # Add photo to database (as main photo)
                    photo_success, photo_message, photo_id = db.add_item_photo(item_id, file_path, is_main=True)

                    if not photo_success:
                        flash(f'Item created but photo upload failed: {photo_message}', 'warning')

        flash(message, 'success')

        # Send email notification to customer
        from src.email_utils import send_quote_converted_notification
        if result_data:
            email_success, email_msg = send_quote_converted_notification(
                app.config,
                result_data['customer_email'],
                result_data['customer_name'],
                item_name,
                item_price,
                result_data.get('user_created', False),
                result_data.get('temp_password')
            )

            if not email_success:
                print(f"Failed to send quote conversion email: {email_msg}")

    else:
        flash(message, 'error')

    return redirect(url_for('admin_quotes'))


# ============================================================================
# ADMIN CART TRACKING ROUTES
# ============================================================================

@app.route('/admin/carts')
@admin_required
def admin_carts():
    """View all active carts (registered users and guests)"""
    carts = db.get_all_active_carts()

    # Calculate some statistics
    total_carts = len(carts)
    registered_carts = len([c for c in carts if c['cart_type'] == 'registered'])
    guest_carts = len([c for c in carts if c['cart_type'] == 'guest'])
    total_value = sum(c['cart_total'] for c in carts)

    return render_template('admin-carts.html',
                          carts=carts,
                          total_carts=total_carts,
                          registered_carts=registered_carts,
                          guest_carts=guest_carts,
                          total_value=total_value,
                          config=app.config)


@app.route('/admin/carts/view')
@admin_required
def admin_view_cart():
    """View detailed cart items for a specific user or guest"""
    user_id = request.args.get('user_id', type=int)
    session_id = request.args.get('session_id')

    if not user_id and not session_id:
        flash('Invalid cart reference!', 'error')
        return redirect(url_for('admin_carts'))

    # Get cart details
    cart_items = db.get_cart_details_for_admin(user_id=user_id, session_id=session_id)

    if not cart_items:
        flash('Cart is empty or not found!', 'warning')
        return redirect(url_for('admin_carts'))

    # Get user info if registered user
    user_info = None
    if user_id:
        user_info = db.get_user_by_id(user_id)

    # Calculate total
    cart_total = sum(item['subtotal'] for item in cart_items)

    return render_template('admin-cart-detail.html',
                          cart_items=cart_items,
                          cart_total=cart_total,
                          user_info=user_info,
                          user_id=user_id,
                          session_id=session_id,
                          config=app.config)


@app.route('/admin/carts/clear', methods=['POST'])
@admin_required
def admin_clear_cart():
    """Clear a specific user's or guest's cart"""
    user_id = request.form.get('user_id', type=int)
    session_id = request.form.get('session_id')

    if not user_id and not session_id:
        flash('Invalid cart reference!', 'error')
        return redirect(url_for('admin_carts'))

    success, message = db.admin_clear_cart(user_id=user_id, session_id=session_id)

    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('admin_carts'))


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

    # Get cart items (unified - includes all product types)
    cart_items = db.get_cart_items(session_id, user_id)

    # Add cart_type for backward compatibility with templates
    for item in cart_items:
        if 'product_type' in item:
            item['cart_type'] = item['product_type']
        else:
            item['cart_type'] = 'cutter'  # Default for old items

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
        cart_type = data.get('cart_type', 'cutter')  # Default to cutter for backward compatibility

        if not cart_id:
            return jsonify({'success': False, 'message': 'Cart ID required'}), 400

        # Remove item from the appropriate cart
        if cart_type == 'candles_soap':
            success, message = db.remove_from_candles_soaps_cart(cart_id)
        else:
            success, message = db.remove_from_cart(cart_id)

        if success:
            # Get updated cart info from unified cart
            session_id = get_session_id()
            user_id = current_user.id if current_user.is_authenticated else None

            # Get count from unified cart (all product types)
            cart_count = db.get_cart_count(session_id, user_id)

            # Get all items from unified cart
            all_items = db.get_cart_items(session_id, user_id)
            subtotal = sum(item['subtotal'] for item in all_items)

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

    # Get count from unified cart (all product types)
    total_count = db.get_cart_count(session_id, user_id)

    return jsonify({'count': total_count})


@app.route('/admin/counts')
@admin_required
def admin_counts():
    """Get admin notification counts (for badge updates)"""
    from flask import jsonify

    # Get counts for admin badges
    active_orders_count = db.get_active_orders_count()
    active_quotes_count = db.get_active_quotes_count()
    total_carts_count = db.get_total_carts_count()

    return jsonify({
        'orders': active_orders_count,
        'quotes': active_quotes_count,
        'carts': total_carts_count
    })


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

        # Get payment method from form
        payment_method = form.payment_method.data if form.payment_method.data else 'cash_on_delivery'

        # Create order
        success, message, order_number = db.create_order(current_user.id, shipping_info, payment_method)

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


# ============================================================================
# CANDLES & SOAPS SHOP ROUTES
# ============================================================================

@app.route('/candles-soaps')
def candles_soaps():
    """Candles & Soaps shop page"""
    from datetime import datetime, timedelta

    # Get filter parameter
    category_id = request.args.get('category', type=int)

    # Get all active products (show all, including out of stock)
    products = db.get_all_candles_soaps_products(
        category_id=category_id,
        in_stock_only=False,
        active_only=True
    )

    # Add photo URLs, main photo URL, and is_new flag to each product
    for product in products:
        # Calculate is_new flag (products created within last 30 days)
        try:
            created = datetime.strptime(product['created_date'], '%Y-%m-%d %H:%M:%S')
            days_old = (datetime.now() - created).days
            product['is_new'] = days_old <= 30
        except:
            product['is_new'] = False

        # Get all photos for this product
        photos = db.get_candles_soaps_product_photos(product['id'])

        # Build photo URLs list
        if photos:
            product['photo_urls'] = [f"/{photo['photo_path'].replace(os.sep, '/')}" for photo in photos]
            # Set main photo URL
            main_photo = next((photo for photo in photos if photo['is_main']), photos[0] if photos else None)
            product['main_photo_url'] = f"/{main_photo['photo_path'].replace(os.sep, '/')}" if main_photo else None
        else:
            product['photo_urls'] = []
            product['main_photo_url'] = None

    # Get all active categories for filter buttons
    categories = db.get_all_candles_soaps_categories(active_only=True)

    # Create category description lookup and add to products
    category_descriptions = {cat['id']: cat.get('description', '') for cat in categories}
    for product in products:
        product['category_description'] = category_descriptions.get(product['category_id'], '')

    return render_template('candles_soaps.html',
                         config=app.config,
                         products=products,
                         categories=categories)


@app.route('/candles-soaps/cart/add', methods=['POST'])
def candles_soaps_cart_add():
    """Add a candles/soaps product to cart"""
    from flask import jsonify

    try:
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)

        if not product_id:
            return jsonify({'success': False, 'message': 'Product ID required'}), 400

        # Get or create session ID
        session_id = get_session_id()

        # Use Flask-Login's current_user
        user_id = current_user.id if current_user.is_authenticated else None

        # Check if product exists and has stock
        product = db.get_candles_soaps_product(product_id)
        if not product:
            return jsonify({'success': False, 'message': 'Product not found'}), 404

        if product['stock_quantity'] == 0:
            return jsonify({'success': False, 'message': 'Product is out of stock'}), 400

        if product['stock_quantity'] < quantity:
            return jsonify({'success': False, 'message': f'Only {product["stock_quantity"]} items available'}), 400

        # Add to candles_soaps cart
        success, message = db.add_to_candles_soaps_cart(session_id, product_id, quantity, user_id)

        if success:
            # Get updated cart count (unified across all product types)
            total_cart_count = db.get_cart_count(session_id, user_id)

            return jsonify({
                'success': True,
                'message': message,
                'cart_count': total_cart_count
            })
        else:
            return jsonify({'success': False, 'message': message}), 500

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
