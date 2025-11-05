# PROJECT CRITICAL INFORMATION

## 🚨 READ THIS FIRST - CRITICAL CONFIGURATION

This file contains critical information that AI agents MUST check before making changes.

---

## 1. DATABASE CONFIGURATION ⚠️

**THE PRODUCTION DATABASE IS:** `database/signups.db`

**NEVER create or use:** `database/ssg.db` or any other database!

**Configured in:** `src/config.py` line 19
```python
DATABASE_PATH = os.getenv('DATABASE_PATH', 'database/signups.db')
```

**See:** `.claude/DATABASE_CONFIGURATION.md` for complete details.

### Before ANY Database Operation:
1. ✅ Check `src/config.py` for `DATABASE_PATH`
2. ✅ Verify `database/signups.db` exists and has data
3. ✅ NEVER hardcode `database/ssg.db` in scripts
4. ✅ Always print which database is being used

---

## 2. ENVIRONMENT CONFIGURATION

### Production (Afrihost cPanel):
- **Python Version:** 3.9+
- **Server:** Passenger
- **Database:** SQLite (`database/signups.db`)
- **Upload Directory:** `static/uploads/`
- **Restart Command:** `touch tmp/restart.txt`

### Key Paths:
- **App Root:** `~/ssg/`
- **Database:** `~/ssg/database/signups.db`
- **Uploads:** `~/ssg/static/uploads/`
- **Logs:** Check cPanel error logs

---

## 3. DEPLOYMENT PROCESS

### Git Workflow:
1. **Commit locally:** All changes to code
2. **Push to GitHub:** `git push origin main`
3. **Pull in cPanel:** Git Version Control → "Update From Remote"
4. **Deploy:** Click "Deploy HEAD Commit"
5. **Restart:** `touch tmp/restart.txt` (or auto-restarts)

### What Happens on Deployment:
- ✅ Code updates
- ✅ Database migrations run automatically (in `Database.__init__()`)
- ✅ App restarts via Passenger
- ❌ Environment variables NOT updated (manual .env changes needed)

---

## 4. CART SYSTEM ARCHITECTURE

### Unified Cart Schema:
**File:** `cart_items` table
- `product_type` - Either 'cutter_item' or 'candles_soap'
- `product_id` - ID of the product in respective table
- `user_id` - For logged-in users
- `session_id` - For guest users

### Migration Notes:
- Old schema used `item_id` (3D printing only)
- New schema uses `product_type` + `product_id` (supports multiple product types)
- Backward compatible - migration runs automatically

**See:** `UNIFIED_CART_MIGRATION_COMPLETE.md` for details.

---

## 5. PRODUCT LINES

### A. 3D Printing / Cookie Cutters
- **Categories:** `cutter_categories` (has `is_public` column)
- **Products:** `cutter_items`
- **Photos:** `cutter_item_photos`
- **Types:** `cutter_types`
- **Shop Page:** `/3d-printing`

### B. Candles & Soaps
- **Categories:** `candles_soaps_categories`
- **Products:** `candles_soaps_products`
- **Photos:** `candles_soaps_product_photos`
- **Stock History:** `candles_soaps_stock_history`
- **Shop Page:** `/candles-soaps`

---

## 6. QUOTE TO SALE SYSTEM

### How It Works:
1. Customer submits quote request
2. Admin reviews and converts to sale (Admin → Quotes)
3. System creates:
   - User account (if doesn't exist)
   - Cutter item in "Custom Quotes" category
   - Adds to user's cart
   - Optionally uploads photo

### Important:
- "Custom Quotes" category has `is_public=0`
- Items are HIDDEN from public shop
- Items are VISIBLE in admin carts and user's own cart
- Photo upload is optional but recommended

**See:** `fix_custom_quotes_visibility.py` for fixing visibility issues.

---

## 7. COMMON PITFALLS & SOLUTIONS

### Pitfall #1: Wrong Database
**Problem:** Using `ssg.db` instead of `signups.db`
**Solution:** Always check `src/config.py` for `DATABASE_PATH`

### Pitfall #2: Custom Quotes Showing in Shop
**Problem:** `is_public` not set to 0
**Solution:** Run `python3 fix_custom_quotes_visibility.py database/signups.db`

### Pitfall #3: Cart Schema Errors
**Problem:** "no such column: product_id"
**Solution:** Run `python3 run_migrations.py database/signups.db`

### Pitfall #4: App Not Restarting
**Problem:** Changes deployed but not showing
**Solution:** `touch ~/ssg/tmp/restart.txt`

---

## 8. KEY CONFIGURATION FILES

### `src/config.py`
- Database path
- Email settings
- Banking details (EFT)
- Site settings
- Admin credentials

### `.env` (Production)
- Secret keys
- Email passwords
- Bank account number
- API keys
- **NOT in Git** - must be configured manually in cPanel

### `app.py`
- Database initialization (line 23)
- All routes and endpoints
- Login/session management

### `src/database.py`
- Database class
- All SQL queries
- Schema initialization
- Migration logic

---

## 9. ADMIN CREDENTIALS

**Configured in:** `src/config.py`
```python
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'changeme123')
```

**Production:** Set in `.env` file (not in Git)

---

## 10. EMAIL SYSTEM

### SMTP Configuration:
- **Server:** Gmail SMTP
- **Port:** 587 (TLS)
- **Configured in:** `src/config.py`
- **Password:** Set in `.env` (production)

### Email Types:
- Order confirmations (with EFT banking details)
- Order status updates (context-aware)
- Quote converted notifications
- Admin notifications
- Bulk emails (admin tool)

---

## 11. PAYMENT METHODS

### Supported:
1. **Cash on Delivery** (default)
2. **EFT/Bank Transfer** (shows banking details)

### Banking Details:
- Configured in `src/config.py`
- Displayed in order confirmation emails
- Payment reference uses order number

---

## 12. VERSION INFORMATION

**Current Version:** 1.5.0

**Check Version:**
- Endpoint: `/version-check`
- Returns: JSON with version and git info

**Version History:**
- 1.5.0 - EFT Banking + Candles & Soaps + Unified Cart
- 1.4.0 - Admin Order Management
- Earlier versions - Basic functionality

---

## 13. FILE UPLOAD DIRECTORIES

### Structure:
```
static/uploads/
├── cutter_items/          # 3D printing product photos + quote items
│   └── [timestamp]_[filename].ext
└── candles_soaps/         # Candles & soaps product photos
    └── [category]/
        └── [product_code]/
            └── [timestamp]_[filename].ext
```

### Permissions:
- Must be writable by web server
- Set to 755 or 775
- Create directories if they don't exist

---

## 14. AGENT INSTRUCTIONS

### Before Making Database Changes:
1. Read `.claude/DATABASE_CONFIGURATION.md`
2. Verify database path in `src/config.py`
3. Check database exists and has data
4. Run diagnostics: `check_database.py`

### Before Deployment:
1. Test locally first
2. Commit with descriptive message
3. Push to GitHub
4. Document any manual steps needed
5. Remind user to restart app after deployment

### When Creating Scripts:
1. Accept database path as CLI argument
2. Default to `database/signups.db`
3. Print which database is being used
4. Include error handling
5. Provide clear output messages

---

## 15. TROUBLESHOOTING COMMANDS

### Check Database:
```bash
python3 check_database.py database/signups.db
```

### Run Migrations:
```bash
python3 run_migrations.py database/signups.db
```

### Fix Custom Quotes:
```bash
python3 fix_custom_quotes_visibility.py database/signups.db
```

### Restart App:
```bash
touch ~/ssg/tmp/restart.txt
```

### View Logs:
Check cPanel → Error Logs

---

## 🎯 GOLDEN RULES

1. **Database:** Always use `database/signups.db`
2. **Testing:** Test locally before pushing
3. **Migrations:** Auto-run, but verify with scripts
4. **Restart:** Required after deployment
5. **Documentation:** Update when making significant changes

---

**Last Updated:** 2025-01-05
**By:** Claude Code Session fixing quote-to-sale and database configuration
