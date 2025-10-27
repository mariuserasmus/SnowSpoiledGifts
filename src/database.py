import sqlite3
import os
from datetime import datetime
import json
import secrets

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

        conn.commit()
        conn.close()

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
