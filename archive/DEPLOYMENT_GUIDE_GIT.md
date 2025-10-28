# Git Deployment Guide for Afrihost
## Snow's Spoiled Gifts - Full E-commerce Site

This guide shows you how to deploy your Flask e-commerce site to Afrihost using Git.

---

## Current Status

✅ **Git Repository Initialized**
✅ **Initial Commit Created** (Commit: b6b4971)
✅ **All Files Staged** (141 files, 11,127 lines)
✅ **.gitignore Configured** (excludes .env, database, and sensitive files)

---

## What's NOT in Git (By Design)

These files are excluded via `.gitignore`:
- `.env` - Contains passwords and secrets
- `database/signups.db` - Your local database
- `__pycache__/` - Python cache files
- `venv/` - Virtual environment

**Important**: You'll need to recreate these on the server.

---

## Deployment Options

### Option 1: Git Push to Remote Repository (Recommended)

This is the most professional approach and allows easy updates.

#### Step 1: Create a Remote Repository

Choose one of these platforms:

**A. GitHub (Most Popular)**
1. Go to https://github.com
2. Click "New Repository"
3. Name: `snowspoiledgifts` (or any name)
4. Set to **Private** (recommended for production sites)
5. Don't initialize with README (you already have files)
6. Click "Create Repository"

**B. GitLab (Alternative)**
1. Go to https://gitlab.com
2. Click "New Project"
3. Choose "Create blank project"
4. Name: `snowspoiledgifts`
5. Set visibility to **Private**

**C. Bitbucket (Another Alternative)**
1. Go to https://bitbucket.org
2. Click "Create repository"
3. Name: `snowspoiledgifts`
4. Set to **Private**

#### Step 2: Connect Your Local Repo to Remote

After creating your remote repository, you'll see instructions. Run these commands:

```bash
# Add remote origin (replace URL with yours)
git remote add origin https://github.com/yourusername/snowspoiledgifts.git

# Or for GitLab:
# git remote add origin https://gitlab.com/yourusername/snowspoiledgifts.git

# Push your code
git branch -M main
git push -u origin main
```

If using GitHub and asked for credentials, use a Personal Access Token:
- Go to GitHub Settings → Developer Settings → Personal Access Tokens
- Generate new token with `repo` scope
- Use token as password

#### Step 3: Clone Repository on Afrihost Server

**If Afrihost provides SSH access:**

```bash
# SSH into your server
ssh username@snowspoiledgifts.co.za

# Navigate to web directory
cd ~/public_html

# Clone your repository
git clone https://github.com/yourusername/snowspoiledgifts.git .
# Note: The dot (.) clones into current directory

# Set up virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**If Afrihost doesn't provide SSH:**
- Proceed to Option 2 (FTP deployment)

---

### Option 2: Direct FTP Upload from Git Files

If SSH isn't available, deploy via FTP:

#### Step 1: Export Files from Git

In your project directory (`C:\Claude\SSG`):

```bash
# Create a clean export folder
mkdir C:\Claude\SSG-Deploy

# Copy all committed files (excludes .gitignore items)
git archive --format=zip --output=C:\Claude\SSG-Deploy\ssg-deploy.zip main

# Extract the zip
cd C:\Claude\SSG-Deploy
unzip ssg-deploy.zip
```

Or use Git Bash / Windows Explorer to copy all files EXCEPT:
- `.git/` folder
- `.env` file (you'll create this on server)
- `database/` folder
- `venv/` folder
- `__pycache__/` folders

#### Step 2: Upload via FTP

Use FileZilla or similar FTP client:

**Connection Details:**
- Host: `ftp.snowspoiledgifts.co.za` (or as provided by Afrihost)
- Username: Your FTP username
- Password: Your FTP password
- Port: 21 (FTP) or 22 (SFTP)

**Upload Structure:**
```
public_html/
├── static/
│   ├── css/
│   ├── images/
│   ├── js/
│   └── uploads/ (create this, ensure writable)
├── templates/
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── email_utils.py
│   └── forms.py
├── docs/
├── scripts/
├── app.py
├── wsgi.py
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## Server Configuration

### Step 1: Create .env File on Server

Create a new `.env` file on the server with production values:

```env
# Production Environment Configuration
SECRET_KEY=your-very-long-random-secret-key-change-this-to-something-unique
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
```

**Generate a Strong SECRET_KEY:**
```python
# On your local machine or server Python shell:
python -c "import secrets; print(secrets.token_hex(32))"
```

### Step 2: Create Database Directory

```bash
mkdir -p database
chmod 755 database
```

The database will auto-create on first run via `init_db()` in `src/database.py`.

### Step 3: Install Python Dependencies

**If using cPanel Python App Manager:**
1. Log into cPanel
2. Go to "Setup Python App"
3. Create new application
4. Point to `public_html/`
5. Set application file to `wsgi.py`
6. Install dependencies via cPanel interface

**If using SSH:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Step 4: Set File Permissions

```bash
# Application files
chmod 644 *.py
chmod 644 .env

# Executable
chmod 755 wsgi.py

# Database folder (must be writable)
chmod 755 database/

# Static files
chmod 755 static/
find static -type f -exec chmod 644 {} \;
find static -type d -exec chmod 755 {} \;

# Templates
chmod 755 templates/
chmod 644 templates/*.html
```

### Step 5: Configure Web Server

**For cPanel with Passenger:**

The `.htaccess` file should be auto-generated, but verify it exists:

```apache
# .htaccess
PassengerAppRoot /home/username/public_html
PassengerBaseURI /
PassengerPython /home/username/virtualenv/public_html/3.X/bin/python
PassengerAppLogFile /home/username/logs/passenger.log

RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteRule ^(.*)$ /wsgi.py/$1 [QSA,L]

# Force HTTPS
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
```

**For manual setup with Gunicorn:**

```bash
# Install Gunicorn
pip install gunicorn

# Run Gunicorn
gunicorn --bind 0.0.0.0:8000 --workers 2 --timeout 60 wsgi:app
```

---

## Database Setup

The application uses SQLite by default. On first run, the database will auto-initialize with these tables:

- `signups` - Email signup list
- `quote_requests` - Custom design quotes
- `cake_topper_requests` - Cake topper quotes
- `print_service_requests` - 3D print service quotes
- `cutter_categories` - Cookie/clay cutter categories
- `cutter_types` - Cutter types (Animals, Shapes, etc.)
- `cutter_items` - Individual products
- `cutter_item_photos` - Product photos

**To manually initialize:**
```python
python -c "from src.database import Database; db = Database(); db.init_db()"
```

---

## Initial Setup After Deployment

### 1. Test the Site
Visit: https://www.snowspoiledgifts.co.za

### 2. Login to Admin Panel
Visit: https://www.snowspoiledgifts.co.za/admin/login
- Username: (from .env)
- Password: (from .env)

### 3. Set Up Product Categories
Go to: `/admin/cutters/categories`

Add these categories:
- Cookie cutter
- Imprint Cookie Press Cutters

### 4. Set Up Product Types
Go to: `/admin/cutters/types`

Add these types:
- Animals
- Flora
- Shapes
- Characters
- Holiday
- Letters
- Themed - Christmas
- Themed - Birthday
- etc.

### 5. Add Products
Go to: `/admin/cutters/items/add`
- Upload photos
- Set prices
- Add descriptions
- Assign categories and types

---

## Updating Your Site After Initial Deployment

### Method 1: Git Pull (If you set up remote repo)

On the server:
```bash
cd ~/public_html
git pull origin main
source venv/bin/activate
pip install -r requirements.txt  # If dependencies changed
# Restart app (method depends on hosting setup)
```

### Method 2: FTP Upload

1. Make changes locally
2. Test locally with `python app.py`
3. Commit changes: `git add . && git commit -m "Description of changes"`
4. Upload changed files via FTP
5. Restart application if needed

---

## Enable HTTPS/SSL

1. In Afrihost cPanel, go to "SSL/TLS"
2. Use "Let's Encrypt" (free SSL certificate)
3. Install for `www.snowspoiledgifts.co.za` and `snowspoiledgifts.co.za`
4. Verify HTTPS redirect is working

---

## Monitoring and Maintenance

### Check Logs

**cPanel:**
- Go to "Error Logs" in cPanel
- Check for Python/Flask errors

**SSH:**
```bash
tail -f ~/logs/error_log
tail -f ~/logs/passenger.log  # If using Passenger
```

### Backup Database

**Option 1: Admin Panel**
- Login to `/admin/signups`
- Future feature: Export CSV

**Option 2: Download via FTP**
- Download `database/signups.db` regularly
- Store securely offline

**Option 3: SQLite Command**
```bash
sqlite3 database/signups.db ".backup backup_$(date +%Y%m%d).db"
```

### Regular Maintenance Tasks

1. **Weekly**: Check admin panel for new quotes/requests
2. **Weekly**: Backup database
3. **Monthly**: Check error logs
4. **Monthly**: Update Python dependencies if needed
5. **As needed**: Add new products

---

## Troubleshooting

### Issue: 500 Internal Server Error

**Check:**
1. Error logs (`tail -f ~/logs/error_log`)
2. Python version compatibility (needs 3.8+)
3. All dependencies installed (`pip list`)
4. `.env` file exists and is readable
5. File permissions correct

### Issue: Database Not Found

**Solution:**
```bash
mkdir -p database
chmod 755 database
python -c "from src.database import Database; Database().init_db()"
```

### Issue: Static Files (CSS/Images) Not Loading

**Check:**
1. Files uploaded to correct location
2. Permissions: `chmod -R 755 static/`
3. `.htaccess` configured correctly
4. Check browser console for 404 errors

### Issue: Admin Login Not Working

**Check:**
1. `.env` file has correct credentials
2. SECRET_KEY is set
3. Session cookies enabled
4. Clear browser cache/cookies

### Issue: Photos Not Uploading

**Check:**
1. `static/uploads/` directory exists
2. Directory is writable: `chmod 755 static/uploads/`
3. Check disk space on server
4. Check upload size limits in server config

---

## Production Checklist

Before announcing your site:

- [ ] HTTPS/SSL enabled and working
- [ ] Admin credentials changed from defaults
- [ ] Strong SECRET_KEY set
- [ ] `.env` file secured (chmod 600)
- [ ] Database backup system in place
- [ ] Email notifications working
- [ ] All product categories created
- [ ] Test products added
- [ ] Mobile responsive tested
- [ ] All forms tested (signup, quotes, etc.)
- [ ] Admin panel accessible
- [ ] Error pages working (404, 500)
- [ ] Social media links updated
- [ ] Contact information correct
- [ ] Performance tested (page load speed)
- [ ] Cross-browser tested (Chrome, Firefox, Safari, Edge)

---

## Git Commands Reference

**Check repository status:**
```bash
git status
```

**View commit history:**
```bash
git log --oneline
```

**Create new commit after changes:**
```bash
git add .
git commit -m "Description of changes"
```

**Push to remote:**
```bash
git push origin main
```

**Pull updates from remote:**
```bash
git pull origin main
```

**View remote repository:**
```bash
git remote -v
```

**Create a new branch:**
```bash
git checkout -b new-feature
```

---

## Next Steps After Deployment

1. **Add Products**: Start populating your Cookie & Clay Cutters shop
2. **Test Everything**: Quote forms, admin panel, product display
3. **Announce Launch**: Social media, email list
4. **Monitor**: Check logs and admin panel regularly
5. **Phase 2**: Implement shopping cart (see `CHECKPOINT_NEXT_PHASE.md`)

---

## Getting Help

**Afrihost Support:**
- Website: https://www.afrihost.com/support
- Email: support@afrihost.com
- Phone: Check your account details

**Questions to Ask Afrihost:**
1. "Does my hosting plan support Python Flask applications?"
2. "What is the process for deploying a Flask app?"
3. "Can I use Git on the server, or should I deploy via FTP?"
4. "What Python version is available?"
5. "How do I restart my Python application after updates?"

---

## Summary

Your Snow's Spoiled Gifts site is now ready to deploy! You have:

✅ Full-featured Flask e-commerce application
✅ Admin panel for managing products and quotes
✅ Customer-facing shop with filters and search
✅ Quote request systems
✅ Email notifications
✅ Git repository initialized and committed

**Next Action:** Choose your deployment method (Git + SSH or FTP) and follow the steps above.

Good luck! 🚀

---

**Need to reference the old deployment guide?**
See: `docs/Deployment_Guide.md`
