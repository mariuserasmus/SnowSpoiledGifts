# Passenger Troubleshooting Guide

## Your Current Error: FileNotFoundError

**Error:** `FileNotFoundError: [Errno 2] No such file or directory`

**Location:** `/home/snowsxtp/ssg/passenger_wsgi.py`

**Cause:** The old `passenger_wsgi.py` was trying to find a virtualenv that doesn't exist.

**Solution:** Upload the NEW simplified `passenger_wsgi.py` file (already fixed in your project).

---

## Steps to Fix

### 1. Upload New passenger_wsgi.py

Re-upload the updated `passenger_wsgi.py` file to `/home/snowsxtp/ssg/`

The new version doesn't try to find a virtualenv - it uses cPanel's Python environment directly.

### 2. Install Python Packages

**Option A: Via cPanel "Setup Python App"**

1. Login to cPanel
2. Go to "Setup Python App"
3. Click on your application
4. Look for "Configuration files" or "Run Pip Install" section
5. Click "Run" or enter: `pip install -r requirements.txt`

**Option B: Via SSH (if available)**

```bash
cd /home/snowsxtp/ssg
python3 -m pip install --user -r requirements.txt
```

**Required packages from requirements.txt:**
- Flask==3.0.0
- Flask-WTF==1.2.1
- WTForms==3.1.1
- email-validator==2.1.0
- python-dotenv==1.0.0

### 3. Restart Passenger

**Via cPanel:**
- Go to "Setup Python App"
- Click "Restart" button

**Via SSH/FTP:**
```bash
mkdir -p /home/snowsxtp/ssg/tmp
touch /home/snowsxtp/ssg/tmp/restart.txt
```

**Via File Manager:**
- Create folder: `tmp`
- Inside `tmp`, create file: `restart.txt`

### 4. Check Logs Again

**View logs in cPanel:**
- Setup Python App → Your App → "View Logs"

**Or via SSH:**
```bash
tail -f ~/logs/error_log
```

---

## Common Errors After This Fix

### Error: "No module named 'flask'"

**Cause:** Python packages not installed

**Solution:**
```bash
python3 -m pip install --user Flask Flask-WTF WTForms email-validator python-dotenv
```

### Error: "No module named 'dotenv'"

**Cause:** python-dotenv not installed

**Solution:**
```bash
python3 -m pip install --user python-dotenv
```

### Error: "ModuleNotFoundError: No module named 'src'"

**Cause:** Project structure issue

**Solution:** Verify you uploaded the entire `src/` folder with all files:
- src/__init__.py
- src/config.py
- src/database.py
- src/email_utils.py
- src/forms.py

### Error: "FileNotFoundError: [Errno 2] No such file or directory: '.env'"

**Cause:** `.env` file missing

**Solution:** Create `.env` file in `/home/snowsxtp/ssg/.env` (see PRODUCTION_ENV_TEMPLATE.md)

---

## Your Current Setup

Based on the error logs:

- **Username:** `snowsxtp`
- **Home Directory:** `/home/snowsxtp`
- **Application Path:** `/home/snowsxtp/ssg/`
- **Python Version:** Python 3.9 (from `/opt/alt/python39/`)

---

## Correct File Structure on Server

Verify this structure exists on your server:

```
/home/snowsxtp/ssg/
├── .env                      ← Must create this!
├── .htaccess
├── passenger_wsgi.py         ← Upload NEW version
├── app.py
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── email_utils.py
│   └── forms.py
├── templates/
│   └── (all .html files)
├── static/
│   ├── css/
│   ├── js/
│   ├── images/
│   └── uploads/
├── database/                 ← Create empty folder
└── tmp/                      ← Create for restarts
    └── restart.txt
```

---

## Quick Fix Checklist

- [ ] Upload NEW `passenger_wsgi.py` (without virtualenv code)
- [ ] Create `.env` file with production settings
- [ ] Install Python packages: `pip install -r requirements.txt`
- [ ] Create `database/` folder (chmod 755)
- [ ] Create `tmp/` folder
- [ ] Touch `tmp/restart.txt` to restart
- [ ] Check logs for new errors

---

## Testing Installation

After fixing, test these URLs:

1. **Homepage:** https://www.snowspoiledgifts.co.za
   - Should load without 500 error

2. **Static files:** https://www.snowspoiledgifts.co.za/static/css/style.css
   - Should show CSS code

3. **Admin login:** https://www.snowspoiledgifts.co.za/admin/login
   - Should show login page

---

## Need More Help?

**If you still get errors after these steps:**

1. Check the FULL error message in logs
2. Look for these specific errors:
   - "No module named..." → Install that Python package
   - "FileNotFoundError: '.env'" → Create .env file
   - "Permission denied" → Check file permissions
   - "ImportError" → Check file structure

3. Common fixes:
   ```bash
   # Install all packages
   python3 -m pip install --user Flask Flask-WTF WTForms email-validator python-dotenv

   # Fix permissions
   chmod 644 /home/snowsxtp/ssg/passenger_wsgi.py
   chmod 600 /home/snowsxtp/ssg/.env
   chmod 755 /home/snowsxtp/ssg/database

   # Restart
   touch /home/snowsxtp/ssg/tmp/restart.txt
   ```

---

## Contact Afrihost Support

If nothing works, contact Afrihost and provide:

1. **Error message** from Passenger logs
2. **Python version** being used
3. Ask them to verify:
   - Python packages are installed
   - File permissions are correct
   - `.htaccess` configuration is correct

---

**The simplified passenger_wsgi.py should fix your immediate error! 🚀**
