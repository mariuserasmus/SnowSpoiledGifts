# Afrihost Passenger Deployment Guide
## Snow's Spoiled Gifts - Flask Application

This guide is specifically for deploying to Afrihost hosting using Passenger (Phusion Passenger).

---

## 📋 Prerequisites

- Afrihost cPanel hosting account
- Domain: www.snowspoiledgifts.co.za
- FTP/SFTP or SSH access
- Python 3.8+ support on hosting plan

---

## 📁 Files Created for Passenger

✅ **`passenger_wsgi.py`** - Passenger WSGI entry point (required)
✅ **`.htaccess`** - Apache/Passenger configuration (required)
✅ **`wsgi.py`** - Standard WSGI file (backup/alternative)

---

## 🚀 Deployment Steps

### Step 1: Upload Files via FTP/SFTP

**Connection Details:**
- Host: `ftp.snowspoiledgifts.co.za` (or provided by Afrihost)
- Username: Your FTP username
- Password: Your FTP password
- Port: 21 (FTP) or 22 (SFTP)

**Upload ALL files to `public_html/`:**

```
public_html/
├── .htaccess                    ← Passenger config
├── passenger_wsgi.py            ← Main entry point
├── wsgi.py                      ← Backup WSGI
├── app.py                       ← Flask application
├── requirements.txt             ← Python dependencies
├── .env.example                 ← Template for .env
├── src/                         ← Python modules
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── email_utils.py
│   └── forms.py
├── templates/                   ← HTML templates
├── static/                      ← CSS, JS, images
├── docs/                        ← Documentation
└── scripts/                     ← Utility scripts
```

**DO NOT upload:**
- `venv/` folder
- `__pycache__/` folders
- `.git/` folder
- `.env` file (create fresh on server)
- `database/signups.db` (will be created on server)

---

### Step 2: Create Production `.env` File on Server

Create a new file: `public_html/.env`

```env
# Production Environment Configuration
SECRET_KEY=YOUR_GENERATED_SECRET_KEY_HERE
FLASK_ENV=production
DEBUG=False

# Admin Credentials (CHANGE THESE!)
ADMIN_USERNAME=your_admin_username
ADMIN_PASSWORD=your_strong_password_here

# Database
DATABASE_PATH=database/signups.db

# Email Configuration (Gmail)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=elmienerasmus@gmail.com
MAIL_PASSWORD=your_gmail_app_password_here
MAIL_DEFAULT_SENDER=elmienerasmus@gmail.com
MAIL_CC_RECIPIENT=mariuserasmus69@gmail.com

# Site Configuration
SITE_URL=https://www.snowspoiledgifts.co.za
SITE_NAME=Snow's Spoiled Gifts
BASE_URL=https://www.snowspoiledgifts.co.za
```

**Generate a strong SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

### Step 3: Set Up Python Environment in cPanel

1. **Login to cPanel** (provided by Afrihost)

2. **Navigate to "Setup Python App"** (under Software section)

3. **Click "Create Application"**

4. **Configure Application:**
   - **Python Version:** Select 3.8, 3.9, or higher
   - **Application Root:** `/home/username/public_html`
   - **Application URL:** Leave blank (root domain)
   - **Application Startup File:** `passenger_wsgi.py`
   - **Application Entry Point:** `application`
   - **Passenger Log File:** (leave default)

5. **Click "Create"**

6. **Note the Virtual Environment Path** (will be shown, e.g., `/home/username/virtualenv/public_html/3.9`)

---

### Step 4: Update `.htaccess` with Your Details

Edit `public_html/.htaccess` and replace:

1. **Line 4:** Replace `username` with your actual cPanel username:
   ```apache
   PassengerAppRoot /home/YOUR_USERNAME/public_html
   ```

2. **Line 11:** Replace `username` and `3.9` with your details:
   ```apache
   PassengerPython /home/YOUR_USERNAME/virtualenv/public_html/3.9/bin/python3
   ```

---

### Step 5: Update `passenger_wsgi.py` with Your Details

Edit `public_html/passenger_wsgi.py` - Line 9:

Replace `3.9` with your Python version:
```python
INTERP = os.path.join(os.environ['HOME'], 'virtualenv', 'public_html', '3.9', 'bin', 'python3')
```

---

### Step 6: Install Dependencies

**In cPanel Python App interface:**

1. Go back to "Setup Python App"
2. Click on your application
3. Find the "Run pip install" section
4. Enter: `pip install -r requirements.txt`
5. Click "Run"

**OR via SSH (if available):**

```bash
source ~/virtualenv/public_html/3.9/bin/activate
cd ~/public_html
pip install -r requirements.txt
```

---

### Step 7: Create Database Directory

**Via cPanel File Manager:**
1. Navigate to `public_html/`
2. Create new folder: `database`
3. Set permissions to `755`

**OR via SSH:**
```bash
cd ~/public_html
mkdir -p database
chmod 755 database
```

The database will auto-initialize on first run.

---

### Step 8: Set File Permissions

**Via cPanel File Manager**, set these permissions:

- **Files (`.py`, `.txt`, `.md`)**: `644`
- **`.env` file**: `600` (important - most secure)
- **`passenger_wsgi.py`**: `644`
- **Directories**: `755`
- **`database/` folder**: `755`
- **`static/` folder**: `755`
- **`templates/` folder**: `755`

**OR via SSH:**
```bash
cd ~/public_html
chmod 644 *.py *.txt *.md
chmod 600 .env
chmod 755 src/ templates/ static/ database/
find static -type f -exec chmod 644 {} \;
find static -type d -exec chmod 755 {} \;
```

---

### Step 9: Restart Passenger Application

**In cPanel:**
1. Go to "Setup Python App"
2. Find your application
3. Click "Restart" button (or "Stop/Start")

**OR via SSH:**
```bash
touch ~/public_html/tmp/restart.txt
```

**OR create a restart file:**
```bash
mkdir -p ~/public_html/tmp
touch ~/public_html/tmp/restart.txt
```

---

### Step 10: Test Your Deployment

1. **Visit Homepage:**
   - https://www.snowspoiledgifts.co.za
   - Should load without errors

2. **Test 3D Printing Page:**
   - https://www.snowspoiledgifts.co.za/3d-printing
   - Products should display

3. **Test Admin Login:**
   - https://www.snowspoiledgifts.co.za/admin/login
   - Login with credentials from `.env`

4. **Check Database:**
   - Admin panel should work
   - Categories/Types/Items should be manageable

---

## 🔧 Troubleshooting

### Issue: 500 Internal Server Error

**Check Passenger logs:**
- cPanel → Setup Python App → Your App → "View Logs"
- Look for Python errors

**Common causes:**
- Wrong Python version in `.htaccess` or `passenger_wsgi.py`
- Missing dependencies: `pip install -r requirements.txt`
- `.env` file missing or incorrect
- File permission issues

**Solution:**
```bash
# Check logs
tail -f ~/logs/error_log

# Reinstall dependencies
source ~/virtualenv/public_html/3.9/bin/activate
pip install --upgrade -r requirements.txt

# Restart app
touch ~/public_html/tmp/restart.txt
```

---

### Issue: Application Not Starting

**Check:**
1. Python version matches in:
   - cPanel Python App settings
   - `.htaccess` (Line 11)
   - `passenger_wsgi.py` (Line 9)

2. Virtual environment path is correct
3. `passenger_wsgi.py` has correct path
4. Dependencies installed: `pip list`

---

### Issue: Static Files Not Loading

**Check:**
1. `static/` folder uploaded correctly
2. Permissions: folder `755`, files `644`
3. Browser cache - try hard refresh (Ctrl+F5)

**Fix:**
```bash
cd ~/public_html
chmod -R 755 static/
find static -type f -exec chmod 644 {} \;
touch tmp/restart.txt
```

---

### Issue: Database Errors

**Check:**
1. `database/` folder exists
2. Permissions: `chmod 755 database/`
3. `.env` has correct `DATABASE_PATH=database/signups.db`

**Manual initialization:**
```bash
cd ~/public_html
source ~/virtualenv/public_html/3.9/bin/activate
python3 -c "from src.database import Database; Database().init_db()"
```

---

### Issue: "Import Error" or Module Not Found

**Solution:**
```bash
source ~/virtualenv/public_html/3.9/bin/activate
cd ~/public_html
pip install -r requirements.txt --force-reinstall
touch tmp/restart.txt
```

---

## 📝 Post-Deployment Checklist

After deployment, verify:

- [ ] Homepage loads without errors
- [ ] 3D Printing page displays products
- [ ] "Add to Cart" shows toast notification
- [ ] Quote request forms work
- [ ] Admin login works
- [ ] Admin can manage categories
- [ ] Admin can manage items
- [ ] Photos upload correctly
- [ ] Email notifications work
- [ ] HTTPS/SSL is active
- [ ] Dark mode works
- [ ] Mobile responsive

---

## 🔄 Updating Your Application

After making changes locally:

1. **Commit to Git:**
   ```bash
   git add .
   git commit -m "Your changes"
   ```

2. **Upload changed files via FTP**

3. **Restart Passenger:**
   ```bash
   touch ~/public_html/tmp/restart.txt
   ```

**OR** in cPanel → Setup Python App → Restart

---

## 📊 Monitoring

**Check Logs:**
- cPanel → Setup Python App → View Logs
- `~/logs/error_log` - Apache errors
- `~/logs/passenger.log` - Passenger logs

**Performance:**
- Monitor in cPanel metrics
- Check database size: `ls -lh database/signups.db`

---

## 🆘 Getting Help from Afrihost

If you encounter issues, contact Afrihost support with:

**Questions to ask:**
1. "What Python version is available on my hosting plan?"
2. "Can you verify my Passenger configuration?"
3. "Are there any errors in my Passenger logs?"
4. "What's the correct path for my virtual environment?"
5. "Can you help restart my Python application?"

**Afrihost Support:**
- https://www.afrihost.com/support
- support@afrihost.com

---

## ✅ Success!

Once everything is working:

1. **Announce Launch** - Social media, email list
2. **Add Products** - Start populating your shop
3. **Monitor** - Check admin panel regularly
4. **Backup** - Download database weekly
5. **Plan Phase 2** - Shopping cart development

---

## 📚 Additional Resources

- **Passenger Documentation:** https://www.phusionpassenger.com/
- **Flask Documentation:** https://flask.palletsprojects.com/
- **cPanel Python:** https://docs.cpanel.net/cpanel/software/python-and-perl-modules/

---

**Your Snow's Spoiled Gifts site is ready to go live! 🚀**

Good luck with your deployment!
