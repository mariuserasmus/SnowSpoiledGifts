# Deployment Guide - Afrihost Hosting

This guide will help you deploy your Snow's Spoiled Gifts "Coming Soon" website to Afrihost.

## Prerequisites

- Afrihost hosting account
- Domain: www.snowspoiledgifts.co.za (already owned)
- FTP/SFTP credentials from Afrihost
- Python support on your hosting plan

## Step 1: Verify Afrihost Python Support

Contact Afrihost support or check your hosting control panel to confirm:

1. **Python Version**: Ensure Python 3.8+ is available
2. **Database Support**: Confirm MySQL or PostgreSQL availability (SQLite should work if file permissions allow)
3. **WSGI Support**: Check if they support WSGI (mod_wsgi, uWSGI, or Gunicorn)
4. **Control Panel**: cPanel, Plesk, or custom panel

## Step 2: Prepare Your Application for Production

### Update Configuration

1. **Edit `.env` file** (create from `.env.example`):

```bash
# Production settings
SECRET_KEY=your-very-long-random-secret-key-here-change-this
FLASK_ENV=production
DEBUG=False

# Strong admin credentials
ADMIN_USERNAME=your_admin_username
ADMIN_PASSWORD=your_strong_password_here

# Database
DATABASE_PATH=database/signups.db

# Email Configuration (Gmail)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=elmienerasmus@gmail.com
MAIL_PASSWORD=your-gmail-app-password-here
MAIL_DEFAULT_SENDER=elmienerasmus@gmail.com
MAIL_CC_RECIPIENT=mariuserasmus69@gmail.com

# Site Configuration
SITE_URL=https://www.snowspoiledgifts.co.za
SITE_NAME=Snow's Spoiled Gifts
BASE_URL=https://www.snowspoiledgifts.co.za
```

**Important:**
- Generate SECRET_KEY: `python -c "import secrets; print(secrets.token_hex(32))"`
- Get Gmail App Password from: https://myaccount.google.com/apppasswords

2. **Verify `src/config.py`** (Optional - Already configured):

The file `src/config.py` already exists and has sensible defaults. It reads from `.env` automatically.

If you want to customize site information, edit `src/config.py` (lines 21-35):

```python
# Site settings
SITE_NAME = "Snow Spoiled Gifts"
SITE_URL = "www.snowspoiledgifts.co.za"
CONTACT_EMAIL = "elmienerasmus@gmail.com"
CONTACT_PHONE = "+71 4711 779"

# Social Media Links
SOCIAL_MEDIA = {
    'facebook': 'https://facebook.com/snowspoiledgifts',
    'instagram': 'https://www.instagram.com/sn0w_sp0ild_g1fts',
    'whatsapp': 'https://wa.me/27714711779',
}
```

**Note:** These are already set correctly. You only need to update if you want to change contact info or social links.

3. **Review `requirements.txt`** (already exists):

```
Flask==3.0.0
Flask-WTF==1.2.1
WTForms==3.1.1
email-validator==2.1.0
python-dotenv==1.0.0
gunicorn==21.2.0  # Add this for production
```

## Step 3: Create WSGI Entry Point

Create `wsgi.py` in your project root:

```python
from app import app

if __name__ == "__main__":
    app.run()
```

## Step 4: Deployment Methods

### Method A: Using cPanel (Most Common)

If Afrihost uses cPanel:

#### 1. Upload Files via FTP/SFTP

Using FileZilla or similar:
- Host: ftp.snowspoiledgifts.co.za (or provided by Afrihost)
- Username: Your FTP username
- Password: Your FTP password
- Port: 21 (FTP) or 22 (SFTP)

Upload these folders/files:
```
public_html/
├── static/
├── templates/
├── database/  (create this folder, ensure writable)
├── app.py
├── config.py
├── database.py
├── forms.py
├── wsgi.py
├── requirements.txt
└── .env
```

**Important**: Do NOT upload:
- `venv/` folder
- `__pycache__/` folders
- `.git/` folder
- `*.pyc` files

#### 2. Set Up Python App in cPanel

1. Log into cPanel
2. Find "Setup Python App" or "Python Selector"
3. Click "Create Application"
4. Configure:
   - **Python Version**: 3.8 or higher
   - **Application Root**: `/home/username/public_html`
   - **Application URL**: `snowspoiledgifts.co.za`
   - **Application Startup File**: `wsgi.py`
   - **Application Entry Point**: `app`

5. Add environment variables in cPanel:
   - Click "Environment Variables"
   - Add each variable from your `.env` file

6. Install dependencies:
   - In cPanel Python App interface, there's usually a terminal or command section
   - Run: `pip install -r requirements.txt`

#### 3. Configure .htaccess (Auto-generated, but verify)

cPanel usually creates this, but ensure it exists in your public_html:

```apache
PassengerAppRoot /home/username/public_html
PassengerBaseURI /
PassengerPython /home/username/virtualenv/public_html/3.X/bin/python
PassengerAppLogFile /home/username/logs/passenger.log

RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteRule ^(.*)$ /wsgi.py/$1 [QSA,L]
```

### Method B: Manual Setup (Advanced)

If you have SSH access:

#### 1. SSH into your server

```bash
ssh username@snowspoiledgifts.co.za
```

#### 2. Navigate to your web directory

```bash
cd ~/public_html
# or wherever your web root is
```

#### 3. Upload files

Use `scp` from your local machine:

```bash
scp -r /path/to/local/SSG/* username@snowspoiledgifts.co.za:~/public_html/
```

#### 4. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 5. Set up Gunicorn (if no WSGI module available)

Create `gunicorn_config.py`:

```python
bind = "127.0.0.1:8000"
workers = 2
threads = 2
timeout = 60
```

Start Gunicorn:

```bash
gunicorn --config gunicorn_config.py wsgi:app
```

#### 6. Configure Apache/Nginx to proxy to Gunicorn

Contact Afrihost support for help with this step.

## Step 5: Database Setup

### Option A: SQLite (Simplest)

1. Ensure `database/` folder exists and is writable:

```bash
mkdir -p database
chmod 755 database
```

2. Database will auto-create on first run

3. **Important**: Ensure your hosting allows write permissions to this folder

### Option B: MySQL (More Robust)

If SQLite has permission issues, use MySQL:

#### 1. Create MySQL database in cPanel:
- Database Name: `username_ssg`
- User: `username_ssguser`
- Password: Strong password
- Grant all privileges

#### 2. Update `database.py` to use MySQL:

Install MySQL connector:
```bash
pip install mysql-connector-python
```

Update connection in `database.py`:
```python
import mysql.connector

class Database:
    def get_connection(self):
        return mysql.connector.connect(
            host='localhost',
            user='username_ssguser',
            password='your-password',
            database='username_ssg'
        )
```

## Step 6: File Permissions

Ensure correct permissions:

```bash
# Application files
chmod 644 *.py
chmod 644 .env

# Executable
chmod 755 wsgi.py

# Database folder (must be writable)
chmod 755 database/
chmod 666 database/*.db

# Static files
chmod 755 static/
chmod 644 static/**/*
```

## Step 7: Test Your Deployment

1. **Visit your site**: http://www.snowspoiledgifts.co.za
2. **Test homepage**: Should load without errors
3. **Test signup form**: Submit an email
4. **Test admin login**: http://www.snowspoiledgifts.co.za/admin/login
5. **Check database**: Verify signup was recorded

## Step 8: Enable HTTPS/SSL

1. In cPanel, go to "SSL/TLS"
2. Use "Let's Encrypt" (usually free)
3. Install certificate for snowspoiledgifts.co.za
4. Force HTTPS redirect in `.htaccess`:

```apache
RewriteEngine On
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
```

## Step 9: Monitor and Maintain

### Log Files

Check logs for errors:
- **Afrihost Control Panel**: Usually has error log viewer
- **SSH**: `tail -f ~/logs/error_log`

### Backup Database

Regularly backup your signups:
1. Login to admin panel
2. Export CSV of signups
3. Download and save securely

### Update Application

To update content:
1. Edit files locally
2. Test locally
3. Upload changed files via FTP
4. Clear cache if needed

## Troubleshooting

### Issue: 500 Internal Server Error

**Causes**:
- Python version mismatch
- Missing dependencies
- Syntax errors
- File permission issues

**Solutions**:
- Check error logs
- Verify Python version
- Reinstall requirements
- Check file permissions

### Issue: Database Permission Denied

**Solutions**:
- Switch to MySQL instead of SQLite
- Ensure database folder is writable (chmod 755)
- Check user ownership

### Issue: Static Files Not Loading

**Solutions**:
- Verify static files uploaded correctly
- Check .htaccess configuration
- Ensure static/ folder has correct permissions

### Issue: Form Submissions Not Working

**Solutions**:
- Check SECRET_KEY is set in .env
- Verify database is writable
- Check error logs for specific errors

## Alternative: PythonAnywhere (If Afrihost Doesn't Support Python)

If Afrihost doesn't fully support Python/Flask:

### Option: Use PythonAnywhere

1. Sign up at https://www.pythonanywhere.com (free tier available)
2. Upload your files via web interface
3. Set up virtual environment
4. Configure WSGI file
5. Point your domain to PythonAnywhere

### Point Domain to PythonAnywhere

In Afrihost DNS settings:
- Type: CNAME
- Name: www
- Points to: yourusername.pythonanywhere.com

## Getting Help from Afrihost

If stuck, contact Afrihost support with these questions:

1. "Does my hosting plan support Python Flask applications?"
2. "What Python versions are available?"
3. "How do I configure WSGI for a Flask application?"
4. "Can you help me set up a Python app in cPanel?"
5. "What's the best way to deploy a Flask app on my hosting plan?"

## Production Checklist

Before going live:

- [ ] All images uploaded and correct
- [ ] config.py updated with real information
- [ ] Strong SECRET_KEY set
- [ ] Strong admin password set
- [ ] Database working and writable
- [ ] Email signup form tested
- [ ] Admin panel accessible
- [ ] HTTPS/SSL enabled
- [ ] All links working
- [ ] Mobile responsive tested
- [ ] Social media links correct
- [ ] Contact information correct
- [ ] Error pages tested
- [ ] Performance tested (page load speed)

## Post-Launch

After successful deployment:

1. **Announce on social media**: Let people know the site is live
2. **Monitor signups**: Check admin panel regularly
3. **Gather feedback**: Ask friends/family to test
4. **Analytics**: Consider adding Google Analytics
5. **Plan Phase 1**: Start detailed planning for full e-commerce site

## Need More Help?

- **Afrihost Support**: https://www.afrihost.com/support
- **Flask Documentation**: https://flask.palletsprojects.com/
- **cPanel Documentation**: https://docs.cpanel.net/

---

Good luck with your deployment! 🚀
