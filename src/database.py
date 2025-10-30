import sqlite3
import os
from datetime import datetime
import json
import secrets
import bcrypt

class Database:
    """Handle all database operations"""

    def __init__(self, db_path):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        """Create a database connection"""
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Initialize the database with required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Create signups table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                interests TEXT,
                signup_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                unsubscribe_token TEXT UNIQUE,
                is_active INTEGER DEFAULT 1
            )
        ''')

        # Create quote requests table for 3D printing services (Custom Design)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quote_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_type TEXT NOT NULL,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT,
                preferred_contact TEXT,
                description TEXT NOT NULL,
                intended_use TEXT,
                size TEXT,
                quantity INTEGER DEFAULT 1,
                color TEXT,
                material TEXT,
                budget TEXT,
                additional_notes TEXT,
                reference_images TEXT,
                request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                status TEXT DEFAULT 'pending'
            )
        ''')

        # Create cake topper requests table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cake_topper_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT,
                event_date TEXT,
                occasion TEXT NOT NULL,
                size_preference TEXT,
                text_to_include TEXT NOT NULL,
                design_details TEXT NOT NULL,
                color_preferences TEXT,
                stand_type TEXT,
                reference_images TEXT,
                additional_notes TEXT,
                request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                status TEXT DEFAULT 'pending'
            )
        ''')

        # Create 3D print service requests table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS print_service_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                uploaded_files TEXT NOT NULL,
                material TEXT NOT NULL,
                color TEXT NOT NULL,
                layer_height TEXT,
                infill_density TEXT,
                quantity INTEGER DEFAULT 1,
                supports TEXT,
                special_instructions TEXT,
                request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                status TEXT DEFAULT 'pending'
            )
        ''')

        # Create cutter_categories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cutter_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create cutter_types table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cutter_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create cutter_items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cutter_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_number TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                dimensions TEXT,
                material TEXT,
                stock_status TEXT DEFAULT 'in_stock',
                category_id INTEGER,
                type_id INTEGER,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                FOREIGN KEY (category_id) REFERENCES cutter_categories(id),
                FOREIGN KEY (type_id) REFERENCES cutter_types(id)
            )
        ''')

        # Create cutter_item_photos table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cutter_item_photos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL,
                photo_path TEXT NOT NULL,
                is_main INTEGER DEFAULT 0,
                display_order INTEGER DEFAULT 0,
                uploaded_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (item_id) REFERENCES cutter_items(id) ON DELETE CASCADE
            )
        ''')

        # Create cart_items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cart_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                user_id INTEGER,
                item_id INTEGER NOT NULL,
                quantity INTEGER DEFAULT 1,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (item_id) REFERENCES cutter_items(id)
            )
        ''')

        # Create index for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_cutter_items_category
            ON cutter_items(category_id)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_cutter_items_type
            ON cutter_items(type_id)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_cutter_item_photos_item
            ON cutter_item_photos(item_id)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_cart_items_session
            ON cart_items(session_id)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_cart_items_user
            ON cart_items(user_id)
        ''')

        # Create users table for authentication
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                name TEXT NOT NULL,
                phone TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                email_verified INTEGER DEFAULT 0,
                shipping_address TEXT,
                shipping_city TEXT,
                shipping_state TEXT,
                shipping_postal_code TEXT,
                shipping_country TEXT DEFAULT 'South Africa'
            )
        ''')

        # Create index for faster email lookups
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_users_email
            ON users(email)
        ''')

        # Create orders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                order_number TEXT UNIQUE NOT NULL,
                status TEXT DEFAULT 'pending',
                subtotal REAL NOT NULL,
                shipping_method TEXT DEFAULT 'pickup',
                pudo_option TEXT,
                locker_location TEXT,
                shipping_cost REAL DEFAULT 0,
                total_amount REAL NOT NULL,
                shipping_address TEXT,
                shipping_city TEXT,
                shipping_state TEXT,
                shipping_postal_code TEXT,
                shipping_country TEXT,
                payment_method TEXT,
                payment_status TEXT DEFAULT 'pending',
                payment_reference TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        # Create order_items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        ''')

        # Create indexes for orders
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_orders_user
            ON orders(user_id)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_orders_number
            ON orders(order_number)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_order_items_order
            ON order_items(order_id)
        ''')

        # Run migrations for existing tables
        self._run_migrations(conn)

        conn.commit()
        conn.close()

    def _run_migrations(self, conn):
        """Run database migrations for schema updates"""
        cursor = conn.cursor()
        try:
            # Check if orders table exists and needs migration
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='orders'")
            if cursor.fetchone():
                # Check if new columns exist
                cursor.execute("PRAGMA table_info(orders)")
                columns = [col[1] for col in cursor.fetchall()]

                # Add shipping_method column if missing
                if 'shipping_method' not in columns:
                    cursor.execute("ALTER TABLE orders ADD COLUMN shipping_method TEXT DEFAULT 'pickup'")

                # Add pudo_option column if missing
                if 'pudo_option' not in columns:
                    cursor.execute("ALTER TABLE orders ADD COLUMN pudo_option TEXT")

                # Add locker_location column if missing
                if 'locker_location' not in columns:
                    cursor.execute("ALTER TABLE orders ADD COLUMN locker_location TEXT")

                # Add shipping_cost column if missing
                if 'shipping_cost' not in columns:
                    cursor.execute("ALTER TABLE orders ADD COLUMN shipping_cost REAL DEFAULT 0")

                # Add subtotal column if missing
                if 'subtotal' not in columns:
                    cursor.execute("ALTER TABLE orders ADD COLUMN subtotal REAL DEFAULT 0")
                    # Update existing orders to have subtotal = total_amount
                    cursor.execute("UPDATE orders SET subtotal = total_amount WHERE subtotal = 0 OR subtotal IS NULL")

            # Check if users table needs shipping fields
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            if cursor.fetchone():
                cursor.execute("PRAGMA table_info(users)")
                columns = [col[1] for col in cursor.fetchall()]

                if 'shipping_address' not in columns:
                    cursor.execute("ALTER TABLE users ADD COLUMN shipping_address TEXT")
                if 'shipping_city' not in columns:
                    cursor.execute("ALTER TABLE users ADD COLUMN shipping_city TEXT")
                if 'shipping_state' not in columns:
                    cursor.execute("ALTER TABLE users ADD COLUMN shipping_state TEXT")
                if 'shipping_postal_code' not in columns:
                    cursor.execute("ALTER TABLE users ADD COLUMN shipping_postal_code TEXT")
                if 'shipping_country' not in columns:
                    cursor.execute("ALTER TABLE users ADD COLUMN shipping_country TEXT DEFAULT 'South Africa'")

                # Add is_admin column if missing
                if 'is_admin' not in columns:
                    cursor.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")

            # Add invoice and quote reference fields to orders table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='orders'")
            if cursor.fetchone():
                cursor.execute("PRAGMA table_info(orders)")
                columns = [col[1] for col in cursor.fetchall()]

                # Add invoice fields
                if 'invoice_number' not in columns:
                    cursor.execute("ALTER TABLE orders ADD COLUMN invoice_number TEXT")
                if 'invoice_generated_date' not in columns:
                    cursor.execute("ALTER TABLE orders ADD COLUMN invoice_generated_date TIMESTAMP")
                if 'invoice_sent_date' not in columns:
                    cursor.execute("ALTER TABLE orders ADD COLUMN invoice_sent_date TIMESTAMP")

                # Add quote reference fields
                if 'quote_type' not in columns:
                    cursor.execute("ALTER TABLE orders ADD COLUMN quote_type TEXT")
                if 'quote_id' not in columns:
                    cursor.execute("ALTER TABLE orders ADD COLUMN quote_id INTEGER")

                # Add payment received date
                if 'payment_received_date' not in columns:
                    cursor.execute("ALTER TABLE orders ADD COLUMN payment_received_date TIMESTAMP")

            # Add order_id reference to quote tables
            for table in ['quote_requests', 'cake_topper_requests', 'print_service_requests']:
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                if cursor.fetchone():
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = [col[1] for col in cursor.fetchall()]

                    if 'order_number' not in columns:
                        cursor.execute(f"ALTER TABLE {table} ADD COLUMN order_number TEXT")
                    if 'converted_to_order_date' not in columns:
                        cursor.execute(f"ALTER TABLE {table} ADD COLUMN converted_to_order_date TIMESTAMP")

        except Exception as e:
            # Migrations are optional, don't fail if they error
            print(f"Migration warning: {str(e)}")

    def add_signup(self, name, email, interests=None, ip_address=None):
        """Add a new email signup or update interests if changed"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Convert interests list to JSON string
            interests_json = json.dumps(interests) if interests else None

            # Generate unique unsubscribe token
            unsubscribe_token = secrets.token_urlsafe(32)

            # Try to insert new signup
            cursor.execute('''
                INSERT INTO signups (name, email, interests, ip_address, unsubscribe_token, is_active)
                VALUES (?, ?, ?, ?, ?, 1)
            ''', (name, email, interests_json, ip_address, unsubscribe_token))

            conn.commit()
            conn.close()
            return True, "new_signup", unsubscribe_token

        except sqlite3.IntegrityError:
            # Email already exists, check if interests changed
            cursor.execute('''
                SELECT interests, unsubscribe_token, is_active FROM signups WHERE email = ?
            ''', (email,))

            existing = cursor.fetchone()
            if not existing:
                conn.close()
                return False, "error", None

            existing_interests = existing['interests']
            existing_token = existing['unsubscribe_token']
            is_active = existing['is_active']

            # Check if they unsubscribed previously
            if not is_active:
                conn.close()
                return False, "unsubscribed", None

            # Check if interests changed
            if existing_interests != interests_json:
                # Update interests and name
                cursor.execute('''
                    UPDATE signups
                    SET interests = ?, name = ?, ip_address = ?
                    WHERE email = ?
                ''', (interests_json, name, ip_address, email))

                conn.commit()
                conn.close()
                return True, "updated_interests", existing_token
            else:
                # No change in interests
                conn.close()
                return True, "already_registered", existing_token

        except Exception as e:
            conn.close()
            return False, "error", None

    def get_all_signups(self):
        """Get all email signups"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, name, email, interests, signup_date, ip_address, is_active
            FROM signups
            ORDER BY signup_date DESC
        ''')

        signups = cursor.fetchall()
        conn.close()

        # Convert to list of dicts
        result = []
        for signup in signups:
            result.append({
                'id': signup['id'],
                'name': signup['name'],
                'email': signup['email'],
                'interests': json.loads(signup['interests']) if signup['interests'] else [],
                'signup_date': signup['signup_date'],
                'ip_address': signup['ip_address'],
                'is_active': bool(signup['is_active'])
            })

        return result

    def get_signup_count(self):
        """Get total number of signups"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) as count FROM signups')
        count = cursor.fetchone()['count']

        conn.close()
        return count

    def export_to_csv(self):
        """Export signups to CSV format"""
        signups = self.get_all_signups()

        if not signups:
            return "name,email,interests,signup_date,ip_address\n"

        csv_content = "name,email,interests,signup_date,ip_address\n"

        for signup in signups:
            interests_str = '; '.join(signup['interests']) if signup['interests'] else ''
            csv_content += f'"{signup["name"]}","{signup["email"]}","{interests_str}","{signup["signup_date"]}","{signup["ip_address"]}"\n'

        return csv_content

    def add_quote_request(self, service_type, name, email, phone, preferred_contact,
                         description, intended_use, size, quantity, color, material,
                         budget, additional_notes, reference_images, ip_address):
        """Add a new quote request"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO quote_requests (
                    service_type, name, email, phone, preferred_contact,
                    description, intended_use, size, quantity, color, material,
                    budget, additional_notes, reference_images, ip_address
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (service_type, name, email, phone, preferred_contact,
                  description, intended_use, size, quantity, color, material,
                  budget, additional_notes, reference_images, ip_address))

            conn.commit()
            conn.close()
            return True, "Quote request submitted successfully!"

        except Exception as e:
            conn.close()
            return False, f"An error occurred: {str(e)}"

    def get_all_quote_requests(self):
        """Get all quote requests"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT *
            FROM quote_requests
            ORDER BY request_date DESC
        ''')

        requests = cursor.fetchall()
        conn.close()

        # Convert to list of dicts
        result = []
        for req in requests:
            result.append({
                'id': req['id'],
                'service_type': req['service_type'],
                'name': req['name'],
                'email': req['email'],
                'phone': req['phone'],
                'preferred_contact': req['preferred_contact'],
                'description': req['description'],
                'intended_use': req['intended_use'],
                'size': req['size'],
                'quantity': req['quantity'],
                'color': req['color'],
                'material': req['material'],
                'budget': req['budget'],
                'additional_notes': req['additional_notes'],
                'reference_images': req['reference_images'],
                'request_date': req['request_date'],
                'ip_address': req['ip_address'],
                'status': req['status']
            })

        return result

    def get_quote_request_count(self):
        """Get total number of quote requests"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) as count FROM quote_requests')
        count = cursor.fetchone()['count']

        conn.close()
        return count

    def update_quote_status(self, quote_id, status):
        """Update the status of a quote request"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                UPDATE quote_requests
                SET status = ?
                WHERE id = ?
            ''', (status, quote_id))

            conn.commit()
            conn.close()
            return True, "Status updated successfully!"

        except Exception as e:
            conn.close()
            return False, f"An error occurred: {str(e)}"

    def delete_quote_request(self, quote_id):
        """Delete a quote request"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('DELETE FROM quote_requests WHERE id = ?', (quote_id,))
            conn.commit()
            conn.close()
            return True, "Quote request deleted successfully!"

        except Exception as e:
            conn.close()
            return False, f"An error occurred: {str(e)}"

    def unsubscribe_by_token(self, token):
        """Unsubscribe a user by their unique token"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Check if token exists and is active
            cursor.execute('''
                SELECT email, name, is_active FROM signups WHERE unsubscribe_token = ?
            ''', (token,))

            result = cursor.fetchone()

            if not result:
                conn.close()
                return False, "Invalid unsubscribe link.", None

            if not result['is_active']:
                conn.close()
                return False, "already_unsubscribed", result['email']

            # Unsubscribe the user
            cursor.execute('''
                UPDATE signups
                SET is_active = 0
                WHERE unsubscribe_token = ?
            ''', (token,))

            conn.commit()
            conn.close()
            return True, "Successfully unsubscribed!", result['email']

        except Exception as e:
            conn.close()
            return False, f"An error occurred: {str(e)}", None

    def get_signup_by_token(self, token):
        """Get signup details by unsubscribe token"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT name, email, interests, is_active FROM signups WHERE unsubscribe_token = ?
            ''', (token,))

            result = cursor.fetchone()
            conn.close()

            if result:
                return {
                    'name': result['name'],
                    'email': result['email'],
                    'interests': json.loads(result['interests']) if result['interests'] else [],
                    'is_active': result['is_active']
                }
            return None

        except Exception as e:
            conn.close()
            return None

    def add_cake_topper_request(self, name, email, phone, event_date, occasion,
                               size_preference, text_to_include, design_details,
                               color_preferences, stand_type, reference_images,
                               additional_notes, ip_address):
        """Add a new cake topper quote request"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO cake_topper_requests (
                    name, email, phone, event_date, occasion, size_preference,
                    text_to_include, design_details, color_preferences, stand_type,
                    reference_images, additional_notes, ip_address
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, email, phone, event_date, occasion, size_preference,
                  text_to_include, design_details, color_preferences, stand_type,
                  reference_images, additional_notes, ip_address))

            conn.commit()
            conn.close()
            return True, "Cake topper request submitted successfully!"

        except Exception as e:
            conn.close()
            return False, f"An error occurred: {str(e)}"

    def get_all_cake_topper_requests(self):
        """Get all cake topper requests"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT *
            FROM cake_topper_requests
            ORDER BY request_date DESC
        ''')

        requests = cursor.fetchall()
        conn.close()

        # Convert to list of dicts
        result = []
        for req in requests:
            result.append({
                'id': req['id'],
                'name': req['name'],
                'email': req['email'],
                'phone': req['phone'],
                'event_date': req['event_date'],
                'occasion': req['occasion'],
                'size_preference': req['size_preference'],
                'text_to_include': req['text_to_include'],
                'design_details': req['design_details'],
                'color_preferences': req['color_preferences'],
                'stand_type': req['stand_type'],
                'reference_images': req['reference_images'],
                'additional_notes': req['additional_notes'],
                'request_date': req['request_date'],
                'ip_address': req['ip_address'],
                'status': req['status']
            })

        return result

    def update_cake_topper_status(self, request_id, status):
        """Update the status of a cake topper request"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                UPDATE cake_topper_requests
                SET status = ?
                WHERE id = ?
            ''', (status, request_id))

            conn.commit()
            conn.close()
            return True, "Status updated successfully!"

        except Exception as e:
            conn.close()
            return False, f"An error occurred: {str(e)}"

    def delete_cake_topper_request(self, request_id):
        """Delete a cake topper request"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('DELETE FROM cake_topper_requests WHERE id = ?', (request_id,))
            conn.commit()
            conn.close()
            return True, "Cake topper request deleted successfully!"

        except Exception as e:
            conn.close()
            return False, f"An error occurred: {str(e)}"

    def add_print_service_request(self, name, email, uploaded_files, material,
                                  color, layer_height, infill_density, quantity,
                                  supports, special_instructions, ip_address):
        """Add a new 3D print service request"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO print_service_requests (
                    name, email, uploaded_files, material, color, layer_height,
                    infill_density, quantity, supports, special_instructions, ip_address
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, email, uploaded_files, material, color, layer_height,
                  infill_density, quantity, supports, special_instructions, ip_address))

            conn.commit()
            conn.close()
            return True, "3D print service request submitted successfully!"

        except Exception as e:
            conn.close()
            return False, f"An error occurred: {str(e)}"

    def get_all_print_service_requests(self):
        """Get all 3D print service requests"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT *
            FROM print_service_requests
            ORDER BY request_date DESC
        ''')

        requests = cursor.fetchall()
        conn.close()

        # Convert to list of dicts
        result = []
        for req in requests:
            result.append({
                'id': req['id'],
                'name': req['name'],
                'email': req['email'],
                'uploaded_files': req['uploaded_files'],
                'material': req['material'],
                'color': req['color'],
                'layer_height': req['layer_height'],
                'infill_density': req['infill_density'],
                'quantity': req['quantity'],
                'supports': req['supports'],
                'special_instructions': req['special_instructions'],
                'request_date': req['request_date'],
                'ip_address': req['ip_address'],
                'status': req['status']
            })

        return result

    def update_print_service_status(self, request_id, status):
        """Update the status of a 3D print service request"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                UPDATE print_service_requests
                SET status = ?
                WHERE id = ?
            ''', (status, request_id))

            conn.commit()
            conn.close()
            return True, "Status updated successfully!"

        except Exception as e:
            conn.close()
            return False, f"An error occurred: {str(e)}"

    def delete_print_service_request(self, request_id):
        """Delete a 3D print service request"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('DELETE FROM print_service_requests WHERE id = ?', (request_id,))
            conn.commit()
            conn.close()
            return True, "Print service request deleted successfully!"

        except Exception as e:
            conn.close()
            return False, f"An error occurred: {str(e)}"

    # ============================================================================
    # COOKIE & CLAY CUTTERS - CATEGORIES
    # ============================================================================

    def add_cutter_category(self, name, description=None):
        """Add a new cutter category"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO cutter_categories (name, description)
                VALUES (?, ?)
            ''', (name, description))

            conn.commit()
            category_id = cursor.lastrowid
            conn.close()
            return True, "Category added successfully!", category_id

        except sqlite3.IntegrityError:
            conn.close()
            return False, "Category already exists!", None
        except Exception as e:
            conn.close()
            return False, f"An error occurred: {str(e)}", None

    def get_all_cutter_categories(self):
        """Get all cutter categories"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, name, description, created_date
            FROM cutter_categories
            ORDER BY name ASC
        ''')

        categories = cursor.fetchall()
        conn.close()

        result = []
        for cat in categories:
            result.append({
                'id': cat['id'],
                'name': cat['name'],
                'description': cat['description'],
                'created_date': cat['created_date']
            })

        return result

    def get_cutter_category(self, category_id):
        """Get a single category by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, name, description, created_date
            FROM cutter_categories
            WHERE id = ?
        ''', (category_id,))

        cat = cursor.fetchone()
        conn.close()

        if cat:
            return {
                'id': cat['id'],
                'name': cat['name'],
                'description': cat['description'],
                'created_date': cat['created_date']
            }
        return None

    def update_cutter_category(self, category_id, name, description=None):
        """Update a cutter category"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                UPDATE cutter_categories
                SET name = ?, description = ?
                WHERE id = ?
            ''', (name, description, category_id))

            conn.commit()
            conn.close()
            return True, "Category updated successfully!"

        except sqlite3.IntegrityError:
            conn.close()
            return False, "Category name already exists!"
        except Exception as e:
            conn.close()
            return False, f"An error occurred: {str(e)}"

    def delete_cutter_category(self, category_id):
        """Delete a cutter category"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Check if category is in use
            cursor.execute('''
                SELECT COUNT(*) as count FROM cutter_items WHERE category_id = ?
            ''', (category_id,))
            count = cursor.fetchone()['count']

            if count > 0:
                conn.close()
                return False, f"Cannot delete category: {count} items are using it!"

            cursor.execute('DELETE FROM cutter_categories WHERE id = ?', (category_id,))
            conn.commit()
            conn.close()
            return True, "Category deleted successfully!"

        except Exception as e:
            conn.close()
            return False, f"An error occurred: {str(e)}"

    # ============================================================================
    # COOKIE & CLAY CUTTERS - TYPES
    # ============================================================================

    def add_cutter_type(self, name, description=None):
        """Add a new cutter type"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO cutter_types (name, description)
                VALUES (?, ?)
            ''', (name, description))

            conn.commit()
            type_id = cursor.lastrowid
            conn.close()
            return True, "Type added successfully!", type_id

        except sqlite3.IntegrityError:
            conn.close()
            return False, "Type already exists!", None
        except Exception as e:
            conn.close()
            return False, f"An error occurred: {str(e)}", None

    def get_all_cutter_types(self):
        """Get all cutter types"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, name, description, created_date
            FROM cutter_types
            ORDER BY name ASC
        ''')

        types = cursor.fetchall()
        conn.close()

        result = []
        for typ in types:
            result.append({
                'id': typ['id'],
                'name': typ['name'],
                'description': typ['description'],
                'created_date': typ['created_date']
            })

        return result

    def get_cutter_type(self, type_id):
        """Get a single type by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, name, description, created_date
            FROM cutter_types
            WHERE id = ?
        ''', (type_id,))

        typ = cursor.fetchone()
        conn.close()

        if typ:
            return {
                'id': typ['id'],
                'name': typ['name'],
                'description': typ['description'],
                'created_date': typ['created_date']
            }
        return None

    def update_cutter_type(self, type_id, name, description=None):
        """Update a cutter type"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                UPDATE cutter_types
                SET name = ?, description = ?
                WHERE id = ?
            ''', (name, description, type_id))

            conn.commit()
            conn.close()
            return True, "Type updated successfully!"

        except sqlite3.IntegrityError:
            conn.close()
            return False, "Type name already exists!"
        except Exception as e:
            conn.close()
            return False, f"An error occurred: {str(e)}"

    def delete_cutter_type(self, type_id):
        """Delete a cutter type"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Check if type is in use
            cursor.execute('''
                SELECT COUNT(*) as count FROM cutter_items WHERE type_id = ?
            ''', (type_id,))
            count = cursor.fetchone()['count']

            if count > 0:
                conn.close()
                return False, f"Cannot delete type: {count} items are using it!"

            cursor.execute('DELETE FROM cutter_types WHERE id = ?', (type_id,))
            conn.commit()
            conn.close()
            return True, "Type deleted successfully!"

        except Exception as e:
            conn.close()
            return False, f"An error occurred: {str(e)}"

    # ============================================================================
    # COOKIE & CLAY CUTTERS - ITEMS
    # ============================================================================

    def generate_item_number(self, category_name):
        """Generate unique item number in format CC_<category>_NNNN"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Create a clean category prefix (remove spaces, special chars, uppercase)
        category_prefix = ''.join(c for c in category_name if c.isalnum()).upper()

        # Get the highest number for this category
        cursor.execute('''
            SELECT item_number FROM cutter_items ci
            JOIN cutter_categories cc ON ci.category_id = cc.id
            WHERE cc.name = ?
            ORDER BY ci.id DESC
            LIMIT 1
        ''', (category_name,))

        result = cursor.fetchone()
        conn.close()

        if result:
            # Extract the number and increment
            parts = result['item_number'].split('_')
            if len(parts) == 3:
                last_number = int(parts[2])
                new_number = last_number + 1
            else:
                new_number = 1
        else:
            # First item for this category
            new_number = 1

        return f'CC_{category_prefix}_{new_number:04d}'

    def add_cutter_item(self, name, description, price, dimensions, material,
                       stock_status, category_id, type_id):
        """Add a new cutter item"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Get category name for item number generation
            cursor.execute('SELECT name FROM cutter_categories WHERE id = ?', (category_id,))
            category = cursor.fetchone()

            if not category:
                conn.close()
                return False, "Invalid category!", None, None

            item_number = self.generate_item_number(category['name'])

            cursor.execute('''
                INSERT INTO cutter_items (
                    item_number, name, description, price, dimensions, material,
                    stock_status, category_id, type_id
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (item_number, name, description, price, dimensions, material,
                  stock_status, category_id, type_id))

            conn.commit()
            item_id = cursor.lastrowid
            conn.close()
            return True, "Item added successfully!", item_id, item_number

        except Exception as e:
            conn.close()
            return False, f"An error occurred: {str(e)}", None, None

    def get_all_cutter_items(self, category_id=None, type_id=None, search_term=None, active_only=True):
        """Get all cutter items with optional filters"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = '''
            SELECT
                ci.id, ci.item_number, ci.name, ci.description, ci.price,
                ci.dimensions, ci.material, ci.stock_status, ci.created_date,
                ci.updated_date, ci.is_active,
                cc.name as category_name, cc.id as category_id,
                ct.name as type_name, ct.id as type_id,
                (SELECT photo_path FROM cutter_item_photos
                 WHERE item_id = ci.id AND is_main = 1 LIMIT 1) as main_photo
            FROM cutter_items ci
            LEFT JOIN cutter_categories cc ON ci.category_id = cc.id
            LEFT JOIN cutter_types ct ON ci.type_id = ct.id
            WHERE 1=1
        '''

        params = []

        if active_only:
            query += ' AND ci.is_active = 1'

        if category_id:
            query += ' AND ci.category_id = ?'
            params.append(category_id)

        if type_id:
            query += ' AND ci.type_id = ?'
            params.append(type_id)

        if search_term:
            query += ' AND (ci.name LIKE ? OR ci.description LIKE ?)'
            params.append(f'%{search_term}%')
            params.append(f'%{search_term}%')

        query += ' ORDER BY ci.created_date DESC'

        cursor.execute(query, params)
        items = cursor.fetchall()
        conn.close()

        result = []
        for item in items:
            result.append({
                'id': item['id'],
                'item_number': item['item_number'],
                'name': item['name'],
                'description': item['description'],
                'price': item['price'],
                'dimensions': item['dimensions'],
                'material': item['material'],
                'stock_status': item['stock_status'],
                'category_id': item['category_id'],
                'category_name': item['category_name'],
                'type_id': item['type_id'],
                'type_name': item['type_name'],
                'main_photo': item['main_photo'],
                'created_date': item['created_date'],
                'updated_date': item['updated_date'],
                'is_active': bool(item['is_active'])
            })

        return result

    def get_cutter_item(self, item_id):
        """Get a single cutter item with all photos"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                ci.id, ci.item_number, ci.name, ci.description, ci.price,
                ci.dimensions, ci.material, ci.stock_status, ci.created_date,
                ci.updated_date, ci.is_active,
                cc.name as category_name, cc.id as category_id,
                ct.name as type_name, ct.id as type_id
            FROM cutter_items ci
            LEFT JOIN cutter_categories cc ON ci.category_id = cc.id
            LEFT JOIN cutter_types ct ON ci.type_id = ct.id
            WHERE ci.id = ?
        ''', (item_id,))

        item = cursor.fetchone()

        if not item:
            conn.close()
            return None

        # Get all photos for this item
        cursor.execute('''
            SELECT id, photo_path, is_main, display_order, uploaded_date
            FROM cutter_item_photos
            WHERE item_id = ?
            ORDER BY is_main DESC, display_order ASC
        ''', (item_id,))

        photos = cursor.fetchall()
        conn.close()

        photo_list = []
        for photo in photos:
            photo_list.append({
                'id': photo['id'],
                'photo_path': photo['photo_path'],
                'is_main': bool(photo['is_main']),
                'display_order': photo['display_order'],
                'uploaded_date': photo['uploaded_date']
            })

        return {
            'id': item['id'],
            'item_number': item['item_number'],
            'name': item['name'],
            'description': item['description'],
            'price': item['price'],
            'dimensions': item['dimensions'],
            'material': item['material'],
            'stock_status': item['stock_status'],
            'category_id': item['category_id'],
            'category_name': item['category_name'],
            'type_id': item['type_id'],
            'type_name': item['type_name'],
            'created_date': item['created_date'],
            'updated_date': item['updated_date'],
            'is_active': bool(item['is_active']),
            'photos': photo_list
        }

    def update_cutter_item(self, item_id, name, description, price, dimensions,
                          material, stock_status, category_id, type_id):
        """Update a cutter item"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                UPDATE cutter_items
                SET name = ?, description = ?, price = ?, dimensions = ?,
                    material = ?, stock_status = ?, category_id = ?, type_id = ?,
                    updated_date = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (name, description, price, dimensions, material, stock_status,
                  category_id, type_id, item_id))

            conn.commit()
            conn.close()
            return True, "Item updated successfully!"

        except Exception as e:
            conn.close()
            return False, f"An error occurred: {str(e)}"

    def delete_cutter_item(self, item_id):
        """Soft delete a cutter item (set is_active to 0)"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                UPDATE cutter_items
                SET is_active = 0
                WHERE id = ?
            ''', (item_id,))

            conn.commit()
            conn.close()
            return True, "Item deleted successfully!"

        except Exception as e:
            conn.close()
            return False, f"An error occurred: {str(e)}"

    def copy_cutter_item(self, item_id):
        """Create a copy of an existing item with a new item number"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Get the original item with category name
            cursor.execute('''
                SELECT ci.name, ci.description, ci.price, ci.dimensions, ci.material,
                       ci.stock_status, ci.category_id, ci.type_id, cc.name as category_name
                FROM cutter_items ci
                JOIN cutter_categories cc ON ci.category_id = cc.id
                WHERE ci.id = ?
            ''', (item_id,))

            original = cursor.fetchone()

            if not original:
                conn.close()
                return False, "Original item not found!", None

            # Generate new item number based on category
            item_number = self.generate_item_number(original['category_name'])

            # Create copy with "(Copy)" appended to name
            cursor.execute('''
                INSERT INTO cutter_items (
                    item_number, name, description, price, dimensions, material,
                    stock_status, category_id, type_id
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (item_number, f"{original['name']} (Copy)", original['description'],
                  original['price'], original['dimensions'], original['material'],
                  original['stock_status'], original['category_id'], original['type_id']))

            new_item_id = cursor.lastrowid

            # Copy photos (Note: Photos will reference the same files initially - admin can update)
            cursor.execute('''
                SELECT photo_path, is_main, display_order
                FROM cutter_item_photos
                WHERE item_id = ?
            ''', (item_id,))

            photos = cursor.fetchall()

            for photo in photos:
                cursor.execute('''
                    INSERT INTO cutter_item_photos (item_id, photo_path, is_main, display_order)
                    VALUES (?, ?, ?, ?)
                ''', (new_item_id, photo['photo_path'], photo['is_main'], photo['display_order']))

            conn.commit()
            conn.close()
            return True, "Item copied successfully!", new_item_id

        except Exception as e:
            conn.close()
            return False, f"An error occurred: {str(e)}", None

    # ============================================================================
    # COOKIE & CLAY CUTTERS - PHOTOS
    # ============================================================================

    def get_item_upload_path(self, item_id):
        """
        Get the folder path for item photos in format:
        static/uploads/cutter_items/<category>/<type>/<item_number>/

        Returns: (folder_path, category_name, type_name, item_number)
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT ci.item_number, cc.name as category_name, ct.name as type_name
            FROM cutter_items ci
            LEFT JOIN cutter_categories cc ON ci.category_id = cc.id
            LEFT JOIN cutter_types ct ON ci.type_id = ct.id
            WHERE ci.id = ?
        ''', (item_id,))

        result = cursor.fetchone()
        conn.close()

        if not result:
            return None, None, None, None

        category = result['category_name'] or 'Uncategorized'
        item_type = result['type_name'] or 'Uncategorized'
        item_number = result['item_number']

        # Clean names for folder paths (remove special chars, spaces)
        category_clean = ''.join(c if c.isalnum() else '_' for c in category)
        type_clean = ''.join(c if c.isalnum() else '_' for c in item_type)

        folder_path = os.path.join('static', 'uploads', 'cutter_items',
                                   category_clean, type_clean, item_number)

        return folder_path, category, item_type, item_number

    def add_item_photo(self, item_id, photo_path, is_main=False, display_order=0):
        """Add a photo to an item"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # If this is being set as main photo, unset any existing main photo
            if is_main:
                cursor.execute('''
                    UPDATE cutter_item_photos
                    SET is_main = 0
                    WHERE item_id = ?
                ''', (item_id,))

            cursor.execute('''
                INSERT INTO cutter_item_photos (item_id, photo_path, is_main, display_order)
                VALUES (?, ?, ?, ?)
            ''', (item_id, photo_path, is_main, display_order))

            conn.commit()
            photo_id = cursor.lastrowid
            conn.close()
            return True, "Photo added successfully!", photo_id

        except Exception as e:
            conn.close()
            return False, f"An error occurred: {str(e)}", None

    def set_main_photo(self, item_id, photo_id):
        """Set a photo as the main photo for an item"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Unset all main photos for this item
            cursor.execute('''
                UPDATE cutter_item_photos
                SET is_main = 0
                WHERE item_id = ?
            ''', (item_id,))

            # Set the new main photo
            cursor.execute('''
                UPDATE cutter_item_photos
                SET is_main = 1
                WHERE id = ? AND item_id = ?
            ''', (photo_id, item_id))

            conn.commit()
            conn.close()
            return True, "Main photo updated!"

        except Exception as e:
            conn.close()
            return False, f"An error occurred: {str(e)}"

    def delete_item_photo(self, photo_id):
        """Delete a photo"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('DELETE FROM cutter_item_photos WHERE id = ?', (photo_id,))
            conn.commit()
            conn.close()
            return True, "Photo deleted successfully!"

        except Exception as e:
            conn.close()
            return False, f"An error occurred: {str(e)}"

    def get_item_photos(self, item_id):
        """Get all photos for an item"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, photo_path, is_main, display_order, uploaded_date
            FROM cutter_item_photos
            WHERE item_id = ?
            ORDER BY is_main DESC, display_order ASC
        ''', (item_id,))

        photos = cursor.fetchall()
        conn.close()

        result = []
        for photo in photos:
            result.append({
                'id': photo['id'],
                'photo_path': photo['photo_path'],
                'is_main': bool(photo['is_main']),
                'display_order': photo['display_order'],
                'uploaded_date': photo['uploaded_date']
            })

        return result

    def get_quote_request(self, quote_id):
        """Get a single quote request by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM quote_requests WHERE id = ?', (quote_id,))
        request = cursor.fetchone()
        conn.close()
        
        return dict(request) if request else None

    def get_cake_topper_request(self, quote_id):
        """Get a single cake topper request by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM cake_topper_requests WHERE id = ?', (quote_id,))
        request = cursor.fetchone()
        conn.close()
        
        return dict(request) if request else None

    def get_print_service_request(self, quote_id):
        """Get a single print service request by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM print_service_requests WHERE id = ?', (quote_id,))
        request = cursor.fetchone()
        conn.close()

        return dict(request) if request else None

    # ============================================================================
    # SHOPPING CART
    # ============================================================================

    def add_to_cart(self, session_id, item_id, quantity=1, user_id=None):
        """Add an item to cart or update quantity if already in cart"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Check if item already in cart
            if user_id:
                cursor.execute('''
                    SELECT id, quantity FROM cart_items
                    WHERE user_id = ? AND item_id = ?
                ''', (user_id, item_id))
            else:
                cursor.execute('''
                    SELECT id, quantity FROM cart_items
                    WHERE session_id = ? AND item_id = ? AND user_id IS NULL
                ''', (session_id, item_id))

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
                    INSERT INTO cart_items (session_id, user_id, item_id, quantity)
                    VALUES (?, ?, ?, ?)
                ''', (session_id, user_id, item_id, quantity))
                message = "Added to cart!"

            conn.commit()
            conn.close()
            return True, message

        except Exception as e:
            conn.close()
            return False, f"An error occurred: {str(e)}"

    def get_cart_items(self, session_id, user_id=None):
        """Get all items in cart with product details"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            if user_id:
                cursor.execute('''
                    SELECT
                        cart.id as cart_id,
                        cart.item_id,
                        cart.quantity,
                        cart.added_date,
                        item.name,
                        item.price,
                        item.item_number,
                        item.stock_status,
                        (SELECT photo_path FROM cutter_item_photos
                         WHERE item_id = item.id AND is_main = 1 LIMIT 1) as main_photo
                    FROM cart_items cart
                    JOIN cutter_items item ON cart.item_id = item.id
                    WHERE cart.user_id = ? AND item.is_active = 1
                    ORDER BY cart.added_date DESC
                ''', (user_id,))
            else:
                cursor.execute('''
                    SELECT
                        cart.id as cart_id,
                        cart.item_id,
                        cart.quantity,
                        cart.added_date,
                        item.name,
                        item.price,
                        item.item_number,
                        item.stock_status,
                        (SELECT photo_path FROM cutter_item_photos
                         WHERE item_id = item.id AND is_main = 1 LIMIT 1) as main_photo
                    FROM cart_items cart
                    JOIN cutter_items item ON cart.item_id = item.id
                    WHERE cart.session_id = ? AND cart.user_id IS NULL AND item.is_active = 1
                    ORDER BY cart.added_date DESC
                ''', (session_id,))

            items = cursor.fetchall()
            conn.close()

            result = []
            for item in items:
                result.append({
                    'cart_id': item['cart_id'],
                    'item_id': item['item_id'],
                    'quantity': item['quantity'],
                    'name': item['name'],
                    'price': item['price'],
                    'item_number': item['item_number'],
                    'stock_status': item['stock_status'],
                    'main_photo': item['main_photo'],
                    'added_date': item['added_date'],
                    'subtotal': item['price'] * item['quantity']
                })

            return result

        except Exception as e:
            conn.close()
            return []

    def update_cart_quantity(self, cart_id, quantity):
        """Update quantity of an item in cart"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            if quantity <= 0:
                # Remove item if quantity is 0 or less
                cursor.execute('DELETE FROM cart_items WHERE id = ?', (cart_id,))
                message = "Item removed from cart!"
            else:
                cursor.execute('''
                    UPDATE cart_items
                    SET quantity = ?
                    WHERE id = ?
                ''', (quantity, cart_id))
                message = "Cart updated!"

            conn.commit()
            conn.close()
            return True, message

        except Exception as e:
            conn.close()
            return False, f"An error occurred: {str(e)}"

    def remove_from_cart(self, cart_id):
        """Remove an item from cart"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('DELETE FROM cart_items WHERE id = ?', (cart_id,))
            conn.commit()
            conn.close()
            return True, "Item removed from cart!"

        except Exception as e:
            conn.close()
            return False, f"An error occurred: {str(e)}"

    def get_cart_count(self, session_id, user_id=None):
        """Get total number of items in cart"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            if user_id:
                cursor.execute('''
                    SELECT SUM(quantity) as count FROM cart_items WHERE user_id = ?
                ''', (user_id,))
            else:
                cursor.execute('''
                    SELECT SUM(quantity) as count FROM cart_items
                    WHERE session_id = ? AND user_id IS NULL
                ''', (session_id,))

            result = cursor.fetchone()
            conn.close()

            count = result['count'] if result['count'] else 0
            return count

        except Exception as e:
            conn.close()
            return 0

    def clear_cart(self, session_id, user_id=None):
        """Clear all items from cart"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            if user_id:
                cursor.execute('DELETE FROM cart_items WHERE user_id = ?', (user_id,))
            else:
                cursor.execute('DELETE FROM cart_items WHERE session_id = ? AND user_id IS NULL', (session_id,))

            conn.commit()
            conn.close()
            return True, "Cart cleared!"

        except Exception as e:
            conn.close()
            return False, f"An error occurred: {str(e)}"

    # ============================================================================
    # USER AUTHENTICATION
    # ============================================================================

    def create_user(self, email, password, name, phone=None):
        """Create a new user with hashed password"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Hash the password using bcrypt
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            cursor.execute('''
                INSERT INTO users (email, password_hash, name, phone)
                VALUES (?, ?, ?, ?)
            ''', (email.lower(), password_hash, name, phone))

            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            return True, "User created successfully!", user_id

        except sqlite3.IntegrityError:
            conn.close()
            return False, "Email already exists!", None
        except Exception as e:
            conn.close()
            return False, f"An error occurred: {str(e)}", None

    def get_user_by_email(self, email):
        """Get user by email address"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT id, email, password_hash, name, phone, created_date, is_active, email_verified, is_admin
                FROM users
                WHERE email = ?
            ''', (email.lower(),))

            user = cursor.fetchone()
            conn.close()

            if user:
                return {
                    'id': user['id'],
                    'email': user['email'],
                    'password_hash': user['password_hash'],
                    'name': user['name'],
                    'phone': user['phone'],
                    'created_date': user['created_date'],
                    'is_active': bool(user['is_active']),
                    'email_verified': bool(user['email_verified']),
                    'is_admin': bool(user['is_admin']) if 'is_admin' in user.keys() else False
                }
            return None

        except Exception as e:
            conn.close()
            print(f"Error in get_user_by_email: {str(e)}")
            return None

    def set_user_admin(self, email, is_admin=True):
        """Set or unset admin status for a user by email"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                UPDATE users
                SET is_admin = ?
                WHERE email = ?
            ''', (1 if is_admin else 0, email.lower()))

            conn.commit()
            rows_affected = cursor.rowcount
            conn.close()
            return rows_affected > 0

        except Exception as e:
            conn.close()
            print(f"Error setting admin status: {str(e)}")
            return False

    def get_user_by_id(self, user_id):
        """Get user by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT id, email, password_hash, name, phone, created_date, is_active, email_verified, is_admin
                FROM users
                WHERE id = ?
            ''', (user_id,))

            user = cursor.fetchone()
            conn.close()

            if user:
                return {
                    'id': user['id'],
                    'email': user['email'],
                    'password_hash': user['password_hash'],
                    'name': user['name'],
                    'phone': user['phone'],
                    'created_date': user['created_date'],
                    'is_active': bool(user['is_active']),
                    'email_verified': bool(user['email_verified']),
                    'is_admin': bool(user['is_admin']) if 'is_admin' in user.keys() else False
                }
            return None

        except Exception as e:
            conn.close()
            print(f"Error in get_user_by_id: {str(e)}")
            return None

    def verify_password(self, email, password):
        """Verify user password and return user if valid"""
        user = self.get_user_by_email(email)

        if not user:
            return False, None

        if not user['is_active']:
            return False, None

        # Check password using bcrypt
        password_hash_bytes = user['password_hash'].encode('utf-8') if isinstance(user['password_hash'], str) else user['password_hash']
        if bcrypt.checkpw(password.encode('utf-8'), password_hash_bytes):
            return True, user

        return False, None

    def update_user(self, user_id, data):
        """Update user information"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Build dynamic update query based on provided data
            update_fields = []
            values = []

            if 'name' in data:
                update_fields.append('name = ?')
                values.append(data['name'])

            if 'phone' in data:
                update_fields.append('phone = ?')
                values.append(data['phone'])

            if 'email' in data:
                update_fields.append('email = ?')
                values.append(data['email'].lower())

            if not update_fields:
                conn.close()
                return False, "No fields to update!"

            # Add user_id to values
            values.append(user_id)

            query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
            cursor.execute(query, values)

            conn.commit()
            conn.close()
            return True, "User updated successfully!"

        except sqlite3.IntegrityError:
            conn.close()
            return False, "Email already exists!"
        except Exception as e:
            conn.close()
            return False, f"An error occurred: {str(e)}"

    def migrate_guest_cart_to_user(self, session_id, user_id):
        """Transfer guest cart items to logged-in user"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Get all guest cart items for this session
            cursor.execute('''
                SELECT item_id, quantity
                FROM cart_items
                WHERE session_id = ? AND user_id IS NULL
            ''', (session_id,))

            guest_items = cursor.fetchall()

            for item in guest_items:
                item_id = item['item_id']
                quantity = item['quantity']

                # Check if user already has this item in cart
                cursor.execute('''
                    SELECT id, quantity FROM cart_items
                    WHERE user_id = ? AND item_id = ?
                ''', (user_id, item_id))

                existing = cursor.fetchone()

                if existing:
                    # Merge quantities
                    new_quantity = existing['quantity'] + quantity
                    cursor.execute('''
                        UPDATE cart_items
                        SET quantity = ?
                        WHERE id = ?
                    ''', (new_quantity, existing['id']))
                else:
                    # Transfer item to user cart
                    cursor.execute('''
                        UPDATE cart_items
                        SET user_id = ?, session_id = NULL
                        WHERE session_id = ? AND item_id = ? AND user_id IS NULL
                    ''', (user_id, session_id, item_id))

            # Delete any remaining guest cart items for this session
            cursor.execute('''
                DELETE FROM cart_items
                WHERE session_id = ? AND user_id IS NULL
            ''', (session_id,))

            conn.commit()
            conn.close()
            return True, "Cart migrated successfully!"

        except Exception as e:
            conn.close()
            return False, f"An error occurred: {str(e)}"

    def create_order(self, user_id, shipping_info, payment_method='Cash on Delivery'):
        """Create a new order from user's cart"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Get cart items for user
            cursor.execute('''
                SELECT ci.item_id, ci.quantity, item.price, item.name
                FROM cart_items ci
                JOIN cutter_items item ON ci.item_id = item.id
                WHERE ci.user_id = ?
            ''', (user_id,))

            cart_items = cursor.fetchall()

            if not cart_items:
                conn.close()
                return False, "Cart is empty!", None

            # Calculate subtotal
            subtotal = sum(item['price'] * item['quantity'] for item in cart_items)

            # Determine shipping cost based on method and PUDO option
            shipping_method = shipping_info.get('method', 'pickup')
            pudo_option = shipping_info.get('pudo_option')

            # Calculate shipping cost based on PUDO option
            shipping_cost = 0
            if shipping_method == 'pudo' and pudo_option:
                pudo_rates = {
                    'locker_to_locker': 69,
                    'locker_to_kiosk': 79,
                    'locker_to_door': 109,
                    'kiosk_to_door': 119
                }
                shipping_cost = pudo_rates.get(pudo_option, 0)

            # Calculate total
            total_amount = subtotal + shipping_cost

            # Generate sequential order number: SSG-YYYYMM-001
            year_month = datetime.now().strftime('%Y%m')

            # Get the highest order number for this month to avoid duplicates
            cursor.execute('''
                SELECT order_number FROM orders
                WHERE order_number LIKE ?
                ORDER BY order_number DESC
                LIMIT 1
            ''', (f'SSG-{year_month}-%',))

            last_order = cursor.fetchone()
            if last_order:
                # Extract the sequence number from last order
                last_sequence = int(last_order['order_number'].split('-')[-1])
                order_sequence = last_sequence + 1
            else:
                order_sequence = 1

            order_number = f"SSG-{year_month}-{order_sequence:03d}"

            # Create order (use empty string for NULL values to handle old NOT NULL constraints)
            cursor.execute('''
                INSERT INTO orders (
                    user_id, order_number, subtotal, shipping_method, pudo_option,
                    locker_location, shipping_cost, total_amount,
                    shipping_address, shipping_city, shipping_state,
                    shipping_postal_code, shipping_country, payment_method
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, order_number, subtotal, shipping_method, pudo_option,
                shipping_info.get('locker_location') or '',
                shipping_cost, total_amount,
                shipping_info.get('address') or '',
                shipping_info.get('city') or '',
                shipping_info.get('state') or '',
                shipping_info.get('postal_code') or '',
                shipping_info.get('country') or 'South Africa',
                payment_method
            ))

            order_id = cursor.lastrowid

            # Create order items and check for quote references
            quote_reference = None
            for item in cart_items:
                cursor.execute('''
                    INSERT INTO order_items (order_id, product_id, quantity, price)
                    VALUES (?, ?, ?, ?)
                ''', (order_id, item['item_id'], item['quantity'], item['price']))

                # Check if this item is from a quote (item_number starts with "QUOTE-")
                cursor.execute('SELECT item_number FROM cutter_items WHERE id = ?', (item['item_id'],))
                item_data = cursor.fetchone()
                if item_data and item_data['item_number'].startswith('QUOTE-'):
                    # Parse quote reference: QUOTE-CUSTOM_DESIGN-123 or QUOTE-CAKE_TOPPER-456
                    parts = item_data['item_number'].split('-')
                    if len(parts) >= 3:
                        quote_type = parts[1].lower()
                        quote_id = int(parts[2])
                        quote_reference = {'type': quote_type, 'id': quote_id}

            # If order contains quote items, link them
            if quote_reference:
                cursor.execute('''
                    UPDATE orders
                    SET quote_type = ?, quote_id = ?
                    WHERE id = ?
                ''', (quote_reference['type'], quote_reference['id'], order_id))

                # Update quote table with order number
                table_map = {
                    'custom_design': 'quote_requests',
                    'cake_topper': 'cake_topper_requests',
                    'print_service': 'print_service_requests'
                }
                table_name = table_map.get(quote_reference['type'])
                if table_name:
                    cursor.execute(f'''
                        UPDATE {table_name}
                        SET order_number = ?
                        WHERE id = ?
                    ''', (order_number, quote_reference['id']))

            # Clear user's cart
            cursor.execute('DELETE FROM cart_items WHERE user_id = ?', (user_id,))

            conn.commit()
            conn.close()
            return True, "Order created successfully!", order_number

        except Exception as e:
            conn.close()
            return False, f"An error occurred: {str(e)}", None

    def get_order_by_number(self, order_number):
        """Get order details by order number"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM orders WHERE order_number = ?', (order_number,))
        order = cursor.fetchone()
        conn.close()

        if order:
            return dict(order)
        return None

    def get_user_orders(self, user_id):
        """Get all orders for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM orders
            WHERE user_id = ?
            ORDER BY created_date DESC
        ''', (user_id,))

        orders = cursor.fetchall()
        conn.close()

        return [dict(order) for order in orders]

    def get_all_orders(self, status_filter=None):
        """Get all orders for admin (optionally filtered by status)"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if status_filter:
            cursor.execute('''
                SELECT o.*, u.name as customer_name, u.email as customer_email
                FROM orders o
                LEFT JOIN users u ON o.user_id = u.id
                WHERE o.status = ?
                ORDER BY o.created_date DESC
            ''', (status_filter,))
        else:
            cursor.execute('''
                SELECT o.*, u.name as customer_name, u.email as customer_email
                FROM orders o
                LEFT JOIN users u ON o.user_id = u.id
                ORDER BY o.created_date DESC
            ''')

        orders = cursor.fetchall()
        conn.close()

        return [dict(order) for order in orders]

    def get_order_items(self, order_id):
        """Get all items in an order"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT oi.*, item.name,
                   (SELECT photo_path FROM cutter_item_photos
                    WHERE item_id = item.id AND is_main = 1 LIMIT 1) as image_url
            FROM order_items oi
            JOIN cutter_items item ON oi.product_id = item.id
            WHERE oi.order_id = ?
        ''', (order_id,))

        items = cursor.fetchall()
        conn.close()

        return [dict(item) for item in items]

    def update_order_status(self, order_id, status):
        """Update order status and track payment dates"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Base update
            update_fields = ['status = ?', 'updated_date = CURRENT_TIMESTAMP']
            params = [status]

            # Track payment received date when status changes to 'paid'
            if status == 'paid':
                update_fields.append('payment_received_date = CURRENT_TIMESTAMP')
                update_fields.append('payment_status = ?')
                params.append('paid')

            # Track invoice sent date when status changes to 'confirmed' or 'awaiting_payment'
            if status in ['confirmed', 'awaiting_payment']:
                # Check if invoice_sent_date is not already set
                cursor.execute('SELECT invoice_sent_date FROM orders WHERE id = ?', (order_id,))
                result = cursor.fetchone()
                if result and not result['invoice_sent_date']:
                    update_fields.append('invoice_sent_date = CURRENT_TIMESTAMP')

            params.append(order_id)

            cursor.execute(f'''
                UPDATE orders
                SET {', '.join(update_fields)}
                WHERE id = ?
            ''', params)

            conn.commit()
            conn.close()
            return True, "Order status updated!"

        except Exception as e:
            conn.close()
            return False, f"An error occurred: {str(e)}"

    def update_payment_status(self, order_number, payment_status, payment_reference=None):
        """Update payment status for an order"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            if payment_reference:
                cursor.execute('''
                    UPDATE orders
                    SET payment_status = ?, payment_reference = ?, updated_date = CURRENT_TIMESTAMP
                    WHERE order_number = ?
                ''', (payment_status, payment_reference, order_number))
            else:
                cursor.execute('''
                    UPDATE orders
                    SET payment_status = ?, updated_date = CURRENT_TIMESTAMP
                    WHERE order_number = ?
                ''', (payment_status, order_number))

            conn.commit()
            conn.close()
            return True, "Payment status updated!"

        except Exception as e:
            conn.close()
            return False, f"An error occurred: {str(e)}"

    def delete_order(self, order_number):
        """Delete an order and its associated order items"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # First get the order ID
            cursor.execute('SELECT id FROM orders WHERE order_number = ?', (order_number,))
            order = cursor.fetchone()

            if not order:
                conn.close()
                return False, "Order not found"

            order_id = order['id']

            # Delete order items first (foreign key constraint)
            cursor.execute('DELETE FROM order_items WHERE order_id = ?', (order_id,))

            # Then delete the order
            cursor.execute('DELETE FROM orders WHERE id = ?', (order_id,))

            conn.commit()
            conn.close()
            return True, f"Order {order_number} deleted successfully!"

        except Exception as e:
            conn.close()
            return False, f"An error occurred: {str(e)}"

    def convert_quote_to_sale(self, quote_type, quote_id, item_name, item_price, item_description="Custom quote item"):
        """
        Convert a quote to a sale by creating a temporary custom item and adding to customer's cart.

        Args:
            quote_type: Type of quote ('custom_design', 'cake_topper', 'print_service')
            quote_id: ID of the quote request
            item_name: Name for the custom item
            item_price: Price for the item
            item_description: Description of the item

        Returns:
            Tuple (success: bool, message: str, user_id: int or None)
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Get quote details and customer email based on quote type
            table_map = {
                'custom_design': 'quote_requests',
                'cake_topper': 'cake_topper_requests',
                'print_service': 'print_service_requests'
            }

            table_name = table_map.get(quote_type)
            if not table_name:
                conn.close()
                return False, "Invalid quote type", None

            # Get quote details
            cursor.execute(f'SELECT * FROM {table_name} WHERE id = ?', (quote_id,))
            quote = cursor.fetchone()

            if not quote:
                conn.close()
                return False, "Quote not found", None

            customer_email = quote['email']
            customer_name = quote['name']
            customer_phone = quote['phone'] if quote['phone'] else ''

            # Check if customer has a user account
            cursor.execute('SELECT id FROM users WHERE email = ?', (customer_email,))
            user = cursor.fetchone()

            if not user:
                # Auto-create user account with temporary password
                temp_password = secrets.token_urlsafe(12)  # Generate random password
                password_hash = bcrypt.hashpw(temp_password.encode('utf-8'), bcrypt.gensalt())

                cursor.execute('''
                    INSERT INTO users (email, password_hash, name, phone, is_active, email_verified)
                    VALUES (?, ?, ?, ?, 1, 0)
                ''', (customer_email, password_hash, customer_name, customer_phone))

                user_id = cursor.lastrowid
                user_created = True
                user_temp_password = temp_password
            else:
                user_id = user['id']
                user_created = False
                user_temp_password = None

            # Create a temporary custom item in cutter_items table
            # Get or create a "Custom Quotes" category
            cursor.execute("SELECT id FROM cutter_categories WHERE name = 'Custom Quotes'")
            category = cursor.fetchone()

            if not category:
                cursor.execute("INSERT INTO cutter_categories (name, description) VALUES (?, ?)",
                             ('Custom Quotes', 'Items created from custom quote requests'))
                category_id = cursor.lastrowid
            else:
                category_id = category['id']

            # Get or create a "Quote Item" type
            cursor.execute("SELECT id FROM cutter_types WHERE name = 'Quote Item'")
            cutter_type = cursor.fetchone()

            if not cutter_type:
                cursor.execute("INSERT INTO cutter_types (name, description) VALUES (?, ?)",
                             ('Quote Item', 'Custom items from quotes'))
                type_id = cursor.lastrowid
            else:
                type_id = cutter_type['id']

            # Create custom item
            cursor.execute('''
                INSERT INTO cutter_items (
                    item_number, name, description, price, stock_status,
                    category_id, type_id, created_date, is_active
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, 1)
            ''', (
                f"QUOTE-{quote_type.upper()}-{quote_id}",
                item_name,
                f"{item_description}\n\nOriginal Quote ID: {quote_id} ({quote_type.replace('_', ' ').title()})",
                item_price,
                'in_stock',
                category_id,
                type_id
            ))

            item_id = cursor.lastrowid

            # Add item to customer's cart
            cursor.execute('''
                INSERT INTO cart_items (user_id, item_id, quantity, added_date)
                VALUES (?, ?, 1, CURRENT_TIMESTAMP)
            ''', (user_id, item_id))

            # Update quote status to 'converted'
            cursor.execute(f'''
                UPDATE {table_name}
                SET status = 'converted', converted_to_order_date = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (quote_id,))

            conn.commit()
            conn.close()

            # Return success with user creation details
            result_data = {
                'user_id': user_id,
                'user_created': user_created,
                'temp_password': user_temp_password,
                'customer_email': customer_email,
                'customer_name': customer_name
            }

            if user_created:
                message = f"Account created for {customer_email} and quote added to cart!"
            else:
                message = f"Quote converted to sale and added to {customer_email}'s cart!"

            return True, message, result_data

        except Exception as e:
            conn.close()
            return False, f"An error occurred: {str(e)}", None

    def generate_invoice_number(self, order_number):
        """Generate and save invoice number for an order"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            invoice_number = f"INV-{order_number}"

            cursor.execute('''
                UPDATE orders
                SET invoice_number = ?, invoice_generated_date = CURRENT_TIMESTAMP
                WHERE order_number = ?
            ''', (invoice_number, order_number))

            conn.commit()
            conn.close()
            return True, invoice_number

        except Exception as e:
            conn.close()
            return False, f"An error occurred: {str(e)}"
