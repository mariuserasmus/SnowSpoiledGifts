# 🚀 Quick Start: Deploy to Afrihost

**5 commits ready to deploy!**

---

## ✅ What You Have

Your project is **100% ready** for Afrihost deployment with Passenger.

### Key Files for Afrihost:
- ✅ **`passenger_wsgi.py`** - Passenger entry point
- ✅ **`.htaccess`** - Apache/Passenger config
- ✅ **`requirements.txt`** - Python dependencies
- ✅ **`.env.example`** - Template for production .env

---

## 📋 Quick Deploy Steps

### 1. Upload Files via FTP
- Host: `ftp.snowspoiledgifts.co.za`
- Upload everything to `public_html/`
- **Skip:** `venv/`, `.git/`, `__pycache__/`, `.env`, `database/`

### 2. Create `.env` on Server
Copy `.env.example` → `.env` and update:
```env
SECRET_KEY=<generate_new_key>
ADMIN_USERNAME=<your_choice>
ADMIN_PASSWORD=<strong_password>
MAIL_PASSWORD=<gmail_app_password>
```

### 3. Setup Python App in cPanel
- Go to "Setup Python App"
- Python version: 3.8 or higher
- Application root: `/home/username/public_html`
- Startup file: `passenger_wsgi.py`
- Entry point: `application`

### 4. Update Paths
Edit these files with YOUR username and Python version:

**`.htaccess`** (lines 4 & 11):
```apache
PassengerAppRoot /home/YOUR_USERNAME/public_html
PassengerPython /home/YOUR_USERNAME/virtualenv/public_html/3.9/bin/python3
```

**`passenger_wsgi.py`** (line 9):
```python
INTERP = os.path.join(os.environ['HOME'], 'virtualenv', 'public_html', '3.9', 'bin', 'python3')
```

### 5. Install Dependencies
In cPanel Python App:
```bash
pip install -r requirements.txt
```

### 6. Create Database Folder
Via File Manager or SSH:
```bash
mkdir database
chmod 755 database
```

### 7. Restart Application
```bash
touch tmp/restart.txt
```

### 8. Test!
- Visit: https://www.snowspoiledgifts.co.za
- Login: https://www.snowspoiledgifts.co.za/admin/login

---

## 📚 Full Guides Available

- **`AFRIHOST_PASSENGER_SETUP.md`** ← Complete step-by-step (READ THIS!)
- **`DEPLOYMENT_GUIDE_GIT.md`** ← Git deployment options
- **`docs/Deployment_Guide.md`** ← Original guide

---

## 🆘 Need Help?

**Troubleshooting in:** `AFRIHOST_PASSENGER_SETUP.md`

**Common issues:**
- 500 error → Check Passenger logs in cPanel
- Static files not loading → Check permissions
- Database errors → Create `database/` folder

---

## 🎯 After Deployment

1. Test all features
2. Add categories & types
3. Upload products
4. Announce launch!

---

**You've got this! 🚀**
