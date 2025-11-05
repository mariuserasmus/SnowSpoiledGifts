# Claude Code Instructions for Snow Spoiled Gifts Project

## 🚨 READ FIRST - EVERY SESSION

Before making ANY changes to this project, you MUST:

1. ✅ Read `.claude/PROJECT_CRITICAL_INFO.md`
2. ✅ Read `.claude/DATABASE_CONFIGURATION.md`
3. ✅ Verify database path in `src/config.py` (should be `database/signups.db`)

## 🗄️ DATABASE - CRITICAL

**THE ONLY DATABASE:** `database/signups.db`

**NEVER use:** `database/ssg.db`, `ssg.db`, or any other database file!

**Why this matters:** In a previous session, an AI agent incorrectly used `ssg.db` instead of `signups.db`, creating an empty database and wasting hours debugging. This MUST NOT happen again.

### Before Any Database Operation:

```python
# ❌ WRONG - Hardcoded wrong path
db = Database('database/ssg.db')

# ❌ WRONG - No path specified
db = Database()

# ✅ CORRECT - Use configured path
db = Database(app.config['DATABASE_PATH'])

# ✅ CORRECT - For scripts
db_path = sys.argv[1] if len(sys.argv) > 1 else 'database/signups.db'
print(f"Using database: {db_path}")  # Always announce which DB
```

## 📋 Key Project Facts

- **Production Database:** `database/signups.db` (170KB+, has data)
- **Version:** 1.5.0
- **Python:** 3.9+
- **Framework:** Flask with SQLite
- **Hosting:** Afrihost cPanel with Passenger
- **Deployment:** Git pull → Deploy → Restart (`touch tmp/restart.txt`)

## 🛒 Cart System

**Unified Cart Architecture:**
- Table: `cart_items`
- Fields: `product_type` ('cutter_item' or 'candles_soap'), `product_id`
- Supports: 3D printing items AND candles/soaps in same cart
- Legacy: Old `item_id` field still exists for backward compatibility

## 📦 Product Lines

1. **3D Printing / Cookie Cutters**
   - Categories: `cutter_categories` (has `is_public` column!)
   - Products: `cutter_items`
   - Shop: `/3d-printing`

2. **Candles & Soaps**
   - Categories: `candles_soaps_categories`
   - Products: `candles_soaps_products`
   - Shop: `/candles-soaps`

## 🎯 Quote to Sale System

- Converts quote requests to cart items
- Creates items in "Custom Quotes" category
- **IMPORTANT:** "Custom Quotes" has `is_public=0` (hidden from shop)
- Items visible in: Admin carts, customer's own cart
- Items hidden from: Public shop pages
- Supports optional photo upload

## 🔧 Common Tasks

### Check Database Health:
```bash
python3 check_database.py database/signups.db
```

### Run Migrations:
```bash
python3 run_migrations.py database/signups.db
```

### Restart Production App:
```bash
touch ~/ssg/tmp/restart.txt
```

## ⚠️ Common Pitfalls

### 1. Wrong Database Path
**Symptom:** "no such table: cutter_categories"
**Cause:** Using `ssg.db` instead of `signups.db`
**Fix:** Check `src/config.py` line 19

### 2. Database Not Updating
**Symptom:** Changes not reflected
**Cause:** App not restarted after deployment
**Fix:** `touch tmp/restart.txt`

### 3. Custom Quotes Showing in Shop
**Symptom:** Quote items visible on `/3d-printing`
**Cause:** `is_public` not set to 0
**Fix:** `python3 fix_custom_quotes_visibility.py database/signups.db`

## 📝 Script Writing Guidelines

When creating database scripts:

```python
#!/usr/bin/env python3
import sys

def main(db_path='database/signups.db'):  # ← Correct default
    print(f"Using database: {db_path}")    # ← Always print
    # ... your code ...

if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'database/signups.db'
    main(db_path)
```

## 🚀 Deployment Checklist

Before deployment:
- [ ] Test locally with `database/signups.db`
- [ ] Verify no hardcoded `ssg.db` references
- [ ] Check migrations will run correctly
- [ ] Document any manual steps
- [ ] Remind user to restart app

After deployment:
- [ ] Verify version: `/version-check`
- [ ] Check database: `check_database.py`
- [ ] Test key functionality
- [ ] Verify app restarted

## 📚 Additional Documentation

Full details available in:
- `.claude/PROJECT_CRITICAL_INFO.md` - Complete project reference
- `.claude/DATABASE_CONFIGURATION.md` - Database deep dive
- `README.md` - Project overview
- `UNIFIED_CART_MIGRATION_COMPLETE.md` - Cart architecture

## 🎓 Lessons Learned

**Database Path Confusion (2025-01-05):**
- Agent used wrong database path (`ssg.db` vs `signups.db`)
- Created empty database file instead of using existing one
- Spent significant time debugging "table doesn't exist" errors
- Root cause: No documentation about database path configuration
- Solution: Created this comprehensive documentation

**Prevention:** Always check database path FIRST, before any database operations.

---

**Remember:** When in doubt, `database/signups.db` is the one true database! 🎯
