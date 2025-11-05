# DATABASE CONFIGURATION - CRITICAL REFERENCE

## ⚠️ CRITICAL: Database File Location

**THE APPLICATION USES:** `database/signups.db`

**DO NOT CREATE OR USE:** `database/ssg.db` or any other database file!

---

## 📍 Database Path Configuration

### Location in Code:
**File:** `src/config.py` (Line 19)
```python
DATABASE_PATH = os.getenv('DATABASE_PATH', 'database/signups.db')
```

### How It's Used:
**File:** `app.py` (Line 23)
```python
db = Database(app.config['DATABASE_PATH'])
```

---

## 🚨 NEVER DO THIS:

❌ `Database('database/ssg.db')` - WRONG!
❌ `Database()` - WRONG! (Creates default path)
❌ Creating any new database files without checking config first

## ✅ ALWAYS DO THIS:

✅ Check `src/config.py` for `DATABASE_PATH` first
✅ Use the configured path from app.config
✅ For scripts, accept database path as parameter: `sys.argv[1]`
✅ Default to `'database/signups.db'` in scripts

---

## 📝 Script Best Practices

When creating database scripts, ALWAYS use this pattern:

```python
import sys

def main(db_path='database/signups.db'):  # ← Default to signups.db
    """Your function"""
    # ... your code ...

if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'database/signups.db'
    print(f"Using database: {db_path}")  # ← Always print which DB
    main(db_path)
```

---

## 🔍 How to Verify Database Path

### In Production:
```bash
# Check config
grep DATABASE_PATH ~/ssg/src/config.py

# Check what database file exists
ls -lh ~/ssg/database/*.db

# Verify which has data
python3 check_database.py database/signups.db
```

### Expected Output:
- `database/signups.db` - **CORRECT** (has data, ~176KB+)
- `database/ssg.db` - **IGNORE/DELETE** (empty, 0 bytes)

---

## 📋 Database Schema Reference

### Core Tables (Must Exist):
- `signups` - Email signups
- `quote_requests` - Custom design quotes
- `cake_topper_requests` - Cake topper quotes
- `print_service_requests` - 3D print service quotes
- `cutter_categories` - Product categories (has `is_public` column)
- `cutter_types` - Product types
- `cutter_items` - 3D printing products
- `cutter_item_photos` - Product photos
- `cart_items` - Unified cart (has `product_type`, `product_id`)
- `users` - User accounts
- `orders` - Customer orders
- `order_items` - Order line items

### Candles & Soaps Tables:
- `candles_soaps_categories`
- `candles_soaps_products`
- `candles_soaps_product_photos`
- `candles_soaps_stock_history`

---

## 🛠️ Diagnostic Commands

### Check Database Health:
```bash
python3 check_database.py database/signups.db
```

### Run Migrations:
```bash
python3 run_migrations.py database/signups.db
```

### Fix Custom Quotes Visibility:
```bash
python3 fix_custom_quotes_visibility.py database/signups.db
```

---

## 🚨 Red Flags to Watch For

If you see any of these, STOP and verify database path:

1. Error: "no such table: cutter_categories"
   → You're using the wrong database!

2. Database file is 0 bytes
   → You created a new empty database instead of using existing one!

3. Script creates `ssg.db` instead of using `signups.db`
   → Check your script's default path!

4. Tables are missing when they should exist
   → Wrong database path!

---

## 💡 Why This Matters

### What Happened (Today's Issue):
1. ❌ Scripts defaulted to `database/ssg.db`
2. ❌ Created empty database file
3. ❌ Ran migrations on wrong database
4. ❌ Wasted time debugging non-existent tables
5. ✅ Finally discovered real database is `signups.db`

### Lesson Learned:
**ALWAYS verify database path BEFORE creating any database-related code or scripts!**

---

## 📖 Historical Context

The database was originally created as `signups.db` when the site launched with just an email signup form. As features were added (products, cart, orders, etc.), new tables were added to the SAME database file.

**The name `signups.db` is legacy but it's the PRODUCTION database - DO NOT CHANGE IT!**

---

## ✅ Checklist for Database Operations

Before ANY database operation:

- [ ] Check `src/config.py` for `DATABASE_PATH`
- [ ] Verify database file exists and has data (not 0 bytes)
- [ ] Print which database path is being used
- [ ] Test on correct database first
- [ ] Confirm tables exist before running migrations

---

## 🔗 Related Files

- `src/config.py` - Database path configuration
- `src/database.py` - Database class definition
- `app.py` - Database initialization
- `check_database.py` - Diagnostic script
- `run_migrations.py` - Migration script
- `fix_custom_quotes_visibility.py` - Fix script

---

**REMEMBER: When in doubt, `database/signups.db` is the ONE TRUE DATABASE!** 🎯
