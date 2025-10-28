# Deployment Documentation

This folder contains all deployment guides for Snow's Spoiled Gifts.

## 📚 Quick Reference

### For First-Time Deployment
**Start here:** [`AFRIHOST_PASSENGER_SETUP.md`](AFRIHOST_PASSENGER_SETUP.md)
- Complete step-by-step deployment to Afrihost
- Covers file upload, configuration, and testing

### For Email Issues
**Fixing email errors:** [`FIX_PRODUCTION_EMAIL.md`](FIX_PRODUCTION_EMAIL.md)
- Solves "[Errno 99] Cannot assign requested address" error
- Configures Afrihost SMTP instead of Gmail
- Updates to support multiple CC recipients

### For Quick Deployment
**Quick reference:** [`DEPLOYMENT_QUICK_START.md`](DEPLOYMENT_QUICK_START.md)
- 5-minute deployment checklist
- Essential steps only

### For Environment Configuration
**`.env` template:** [`PRODUCTION_ENV_TEMPLATE.md`](PRODUCTION_ENV_TEMPLATE.md)
- Complete production environment configuration
- Afrihost SMTP settings
- Secret key generation guide

---

## 🚀 Deployment Overview

### Method: Manual FTP Upload
Since Git deployment is having issues, use FTP to upload files.

**Files to upload:**
- All Python files (`app.py`, `src/*.py`, `passenger_wsgi.py`)
- All templates (`templates/*.html`)
- All static files (`static/css`, `static/js`, `static/images`)
- Configuration files (`.htaccess`, `requirements.txt`)

**Files NOT to upload:**
- `.env` (create fresh on server)
- `venv/` (virtual environment)
- `.git/` (Git repository)
- `database/*.db` (create on server)
- `__pycache__/` (Python cache)

### Essential Configuration

**Production `.env` must have:**
```env
# Afrihost SMTP (NOT Gmail!)
MAIL_SERVER=mail.snowspoiledgifts.co.za
MAIL_PORT=465
MAIL_USE_SSL=True
MAIL_USE_TLS=False
MAIL_USERNAME=info@snowspoiledgifts.co.za
MAIL_PASSWORD=<info_email_password>
MAIL_DEFAULT_SENDER=info@snowspoiledgifts.co.za
NOTIFICATION_RECIPIENTS=elmienerasmus@gmail.com,mariuserasmus69@gmail.com
```

**After deployment:**
1. Create `database/` folder with permissions 755
2. Restart app: `touch tmp/restart.txt`
3. Test the website
4. Submit a test quote request to verify email

---

## 📖 Document Index

| File | Purpose | Use When |
|------|---------|----------|
| `AFRIHOST_PASSENGER_SETUP.md` | Complete deployment guide | First deployment |
| `FIX_PRODUCTION_EMAIL.md` | Email troubleshooting | Email not sending |
| `DEPLOYMENT_QUICK_START.md` | Quick reference | Re-deploying updates |
| `PRODUCTION_ENV_TEMPLATE.md` | Environment config | Setting up `.env` |

---

## 🆘 Common Issues

### Email Not Sending
**Error:** `[Errno 99] Cannot assign requested address`
**Solution:** See [`FIX_PRODUCTION_EMAIL.md`](FIX_PRODUCTION_EMAIL.md)

### 500 Internal Server Error
**Check:**
1. Passenger logs in cPanel
2. Python version compatibility (3.8+)
3. `.env` file exists and is configured
4. Virtual environment installed dependencies

### Static Files Not Loading
**Check:**
1. File permissions (644 for files, 755 for folders)
2. `.htaccess` configuration
3. Static folder path in Flask config

### Database Errors
**Check:**
1. `database/` folder exists
2. Folder permissions (755)
3. `DATABASE_PATH` in `.env` is correct

---

## 📞 Need Help?

1. Check the appropriate guide above
2. Review `../progress.md` for latest updates
3. Check `../docs/` folder for additional documentation

---

**Last Updated:** 2025-10-28
