# 🛡️ Pre-Deployment Safety Checklist

**CRITICAL:** Complete this checklist BEFORE deploying to production to ensure nothing breaks.

---

## ✅ Email Configuration (CRITICAL)

Since your production SMTP is already configured, verify these settings match in your **production `.env` file**:

### Required Variables (Must Match Live SMTP Settings)

```env
# Email - MUST match your current live SMTP settings
MAIL_SERVER=<your-current-live-smtp-server>
MAIL_PORT=<your-current-live-smtp-port>
MAIL_USE_TLS=<True or False based on your setup>
MAIL_USE_SSL=<True or False based on your setup>
MAIL_USERNAME=<your-current-live-email-username>
MAIL_PASSWORD=<your-current-live-email-password>
MAIL_DEFAULT_SENDER=<info@snowspoiledgifts.co.za or current sender>
ADMIN_EMAIL=<email-where-order-notifications-go>
```

### ⚠️ Common Issues to Avoid:

**Issue 1: Different MAIL_USERNAME format**
- Some servers use full email: `info@snowspoiledgifts.co.za`
- Some servers use just username: `info`
- **Action:** Use whatever format is working in your current live setup

**Issue 2: TLS vs SSL**
- Port 587 typically uses `MAIL_USE_TLS=True` and `MAIL_USE_SSL=False`
- Port 465 typically uses `MAIL_USE_SSL=True` and `MAIL_USE_TLS=False`
- **Action:** Match what's currently working on live

**Issue 3: MAIL_DEFAULT_SENDER vs MAIL_USERNAME**
- `MAIL_USERNAME` = credentials to authenticate with SMTP server
- `MAIL_DEFAULT_SENDER` = "From" address shown to recipients
- These CAN be different (e.g., authenticate with one email, send from another)
- **Action:** If unsure, set both to the same email address

---

## 🔍 Database Safety

### Migration Check ✅

The new Phase 4 features added these database changes:
- `users` table: Added `is_admin` column (INTEGER DEFAULT 0)

**Migration is AUTOMATIC** - runs on first app startup. No manual SQL needed.

### Backup Strategy (IMPORTANT!)

**BEFORE deploying, backup your live database:**

```bash
# On live server, create backup BEFORE deployment
cp database/signups.db database/signups.db.backup_$(date +%Y%m%d_%H%M%S)
```

**Rollback Plan:**
If anything breaks, restore the backup:
```bash
# Stop the app
sudo systemctl stop ssg

# Restore backup
cp database/signups.db.backup_YYYYMMDD_HHMMSS database/signups.db

# Restart app with old code
sudo systemctl start ssg
```

---

## 🧪 Test Before Going Live

### Test in DEV First (DO THIS NOW!)

```bash
# 1. Start your DEV app
cd c:\Claude\SSG
python app.py

# 2. Test as Admin User
# Login: http://localhost:5000/login
# Email: mariuserasmus69@gmail.com
# Check that you see "Orders | Manage Items | Quotes | Signups" in navbar

# 3. Test Orders Dashboard
# Navigate to: http://localhost:5000/admin/orders
# Should see orders list (or empty if no orders)

# 4. Test Order Status Update (if you have orders)
# Click "View" on an order
# Change status to "Confirmed"
# Check "Send email notification"
# Submit and verify email is sent

# 5. Test as Regular User
# Logout or use incognito mode
# Login as non-admin user
# Verify you see normal navbar (Cart | Home | etc.)
# Verify you DON'T see admin links
```

### Expected Behavior:
- ✅ Admin users see admin navbar
- ✅ Regular users see customer navbar
- ✅ Orders dashboard loads without errors
- ✅ Email notifications send successfully (check inbox)
- ✅ No console errors in browser

---

## 📋 Deployment Steps (Safe Approach)

### Step 1: Backup Live Database

```bash
# SSH into live server
ssh user@yourserver.com

# Navigate to app directory
cd /var/www/ssg  # or wherever your app is

# Create backup with timestamp
cp database/signups.db database/signups.db.backup_$(date +%Y%m%d_%H%M%S)

# Verify backup exists
ls -lh database/*.backup*
```

### Step 2: Update Code

```bash
# Pull latest code
git pull origin main

# Or if using manual upload:
# Upload files via FTP/SFTP, being careful to:
# - NOT overwrite .env (your production settings)
# - NOT overwrite database/signups.db
```

### Step 3: Update Dependencies (if needed)

```bash
# Activate virtual environment
source venv/bin/activate

# Update dependencies
pip install -r requirements.txt
```

### Step 4: Verify .env Configuration

```bash
# Check that production .env has all required variables
cat .env | grep -E "MAIL_|ADMIN_EMAIL"

# Should show:
# MAIL_SERVER=...
# MAIL_PORT=...
# MAIL_USE_TLS=...
# MAIL_USERNAME=...
# MAIL_PASSWORD=...
# MAIL_DEFAULT_SENDER=...
# ADMIN_EMAIL=...
```

### Step 5: Restart Application

```bash
# If using systemd
sudo systemctl restart ssg

# If using Gunicorn directly
pkill gunicorn
gunicorn --workers 3 --bind 127.0.0.1:8000 app:app &

# If using screen/tmux, restart the process
```

### Step 6: Check Logs Immediately

```bash
# Watch logs for errors
sudo journalctl -u ssg -f

# Or if using Gunicorn directly
tail -f logs/gunicorn.log  # adjust path as needed

# Look for:
# ✅ "Running on http://..." (app started)
# ✅ No Python errors
# ❌ Any error messages (fix immediately)
```

### Step 7: Test Production Site

**Test Checklist:**

1. **Homepage Loads:**
   ```
   Visit: https://snowspoiledgifts.co.za
   Expected: Site loads normally
   ```

2. **Existing Features Work:**
   - [ ] Can browse cookie cutters
   - [ ] Can add items to cart
   - [ ] Can view cart
   - [ ] Can login as existing user
   - [ ] Can access account page

3. **New Admin Features:**
   - [ ] Login as admin (mariuserasmus69@gmail.com)
   - [ ] See admin navbar (Orders | Manage Items | etc.)
   - [ ] Can access `/admin/orders`
   - [ ] Orders dashboard loads
   - [ ] Can view order details
   - [ ] Can update order status

4. **Email Functionality:**
   - [ ] Place test order (as customer)
   - [ ] Verify confirmation email received
   - [ ] Update order status (as admin)
   - [ ] Verify status update email received

---

## 🚨 Rollback Plan (If Anything Breaks)

### Quick Rollback (Restore Previous Version)

```bash
# Stop the app
sudo systemctl stop ssg

# Restore previous code
git reset --hard HEAD~1  # Go back one commit

# Restore database backup
cp database/signups.db.backup_YYYYMMDD_HHMMSS database/signups.db

# Restart app
sudo systemctl start ssg

# Verify site works
curl https://snowspoiledgifts.co.za
```

### Partial Rollback (Keep Database, Revert Code)

If database migration succeeded but code has issues:

```bash
# Stop app
sudo systemctl stop ssg

# Revert code only
git reset --hard HEAD~1

# Keep database (already has is_admin column, which is fine)

# Restart app
sudo systemctl start ssg
```

---

## 🔒 Security Check

### File Permissions (Critical for .env)

```bash
# Secure .env file
chmod 600 .env
chown www-data:www-data .env  # or your web server user

# Verify
ls -la .env
# Should show: -rw------- (only owner can read/write)
```

### Environment Variables Check

```bash
# Ensure SECRET_KEY is set to a random string (not the dev default)
grep SECRET_KEY .env

# Should NOT be: dev-secret-key-change-in-production
# Should be: random-string-at-least-32-characters
```

### HTTPS Check

```bash
# Verify SSL certificate is valid
curl -I https://snowspoiledgifts.co.za | grep "200 OK"

# Should return: HTTP/2 200 OK (or HTTP/1.1 200 OK)
```

---

## ✅ Final Checklist Before Deployment

**Complete these in order:**

- [ ] **Tested all new admin features in DEV** (most important!)
- [ ] **Backed up live database** (with timestamp)
- [ ] **Verified production .env has MAIL_PASSWORD set**
- [ ] **Verified MAIL_USERNAME format matches live setup**
- [ ] **Verified MAIL_PORT and TLS/SSL settings match live setup**
- [ ] **Read through rollback plan** (know how to undo)
- [ ] **Have access to server logs** (know where to look for errors)
- [ ] **Off-hours deployment** (low traffic time, if possible)
- [ ] **Someone available to help** (or at least test with you)

---

## 🎯 Safe Deployment Strategy

**Recommended Approach:**

1. **Friday afternoon or weekend** - Lower traffic, more time to fix issues
2. **Test in DEV thoroughly** - Catch issues before production
3. **Backup everything** - Database, .env, code
4. **Deploy incrementally:**
   - First: Just update code, restart, test
   - Then: Test admin features
   - Finally: Test email functionality
5. **Monitor for 30 minutes** after deployment
6. **Have rollback plan ready** to execute in 2 minutes if needed

---

## 📞 If Something Goes Wrong

### Step 1: Check Logs
```bash
sudo journalctl -u ssg -n 100
```

### Step 2: Common Issues & Fixes

**Issue: "500 Internal Server Error"**
```bash
# Check Python errors in logs
sudo journalctl -u ssg | grep -i error

# Common cause: Missing module
pip install -r requirements.txt
sudo systemctl restart ssg
```

**Issue: "Email not sending"**
```bash
# Test SMTP directly
python -c "import smtplib; s=smtplib.SMTP('your-smtp-server', 587); s.starttls(); s.login('your-user', 'your-pass'); print('OK')"

# Check .env
cat .env | grep MAIL_
```

**Issue: "Admin features not visible"**
```bash
# Check if is_admin column exists
sqlite3 database/signups.db "PRAGMA table_info(users);" | grep is_admin

# If missing, manually add:
sqlite3 database/signups.db "ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0;"

# Re-run admin setup
python set_admins.py
```

### Step 3: Rollback if Needed

If issues persist after 15 minutes of troubleshooting:
```bash
# Execute rollback plan (see above)
# Get site back to working state
# Debug offline
```

---

## 💡 Post-Deployment Monitoring

**Monitor for first 24 hours:**

1. **Check logs daily:**
   ```bash
   sudo journalctl -u ssg --since "1 hour ago" | grep -i error
   ```

2. **Test critical paths:**
   - Customer registration ✓
   - Checkout process ✓
   - Admin order management ✓
   - Email delivery ✓

3. **Watch for email issues:**
   - Check spam folder for test emails
   - Verify all notifications arrive
   - Monitor SMTP errors in logs

---

## ✅ Success Criteria

**Deployment is successful when:**

- [x] Site loads normally for customers
- [x] Existing features work (cart, checkout, etc.)
- [x] Admin users can access `/admin/orders`
- [x] Orders dashboard displays correctly
- [x] Order status updates work
- [x] Email notifications send successfully
- [x] No errors in logs for 1 hour after deployment

---

**You're ready to deploy safely! 🚀**

**Key Reminder:** The biggest risk is email configuration mismatch. Double-check that your production `.env` exactly matches your current working live SMTP settings.

---

*Last Updated: 2025-10-30*
