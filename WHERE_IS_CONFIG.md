# Where is config.py? Do I need to edit it?

## Quick Answer

✅ **Location:** `src/config.py`

✅ **Already uploaded when you upload your files**

✅ **No editing required** - It reads from `.env` automatically!

---

## What is config.py?

`src/config.py` is a Python file that contains application configuration. It's **already in your project** at:

```
SSG/
├── src/
│   ├── config.py    ← HERE!
│   ├── database.py
│   ├── email_utils.py
│   └── forms.py
├── app.py
└── ...
```

---

## Do I Need to Edit It?

**99% of the time: NO!**

The `config.py` file automatically reads values from your `.env` file:

```python
# Example from src/config.py
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
```

This means:
- If `.env` has `SECRET_KEY=abc123`, it uses `abc123`
- If `.env` is missing that value, it uses the default

---

## What's Already Configured in config.py?

### ✅ Automatic from .env (No editing needed):
- `SECRET_KEY` - From `.env`
- `DATABASE_PATH` - From `.env`
- `ADMIN_USERNAME` - From `.env`
- `ADMIN_PASSWORD` - From `.env`
- `MAIL_SERVER` - From `.env`
- `MAIL_PORT` - From `.env`
- `MAIL_USERNAME` - From `.env`
- `MAIL_PASSWORD` - From `.env`
- All email settings!

### ✅ Hard-coded (Already correct):
- `SITE_NAME` - "Snow Spoiled Gifts"
- `CONTACT_EMAIL` - "elmienerasmus@gmail.com"
- `CONTACT_PHONE` - "+71 4711 779"
- `SOCIAL_MEDIA` links (Facebook, Instagram, WhatsApp)

---

## When WOULD You Edit config.py?

Only edit `src/config.py` if you want to change:

### 1. Site Information
```python
# Line 21-24 in src/config.py
SITE_NAME = "Snow Spoiled Gifts"
SITE_URL = "www.snowspoiledgifts.co.za"
CONTACT_EMAIL = "elmienerasmus@gmail.com"
CONTACT_PHONE = "+71 4711 779"
```

### 2. Launch Date
```python
# Line 27
LAUNCH_DATE = "November 2025"
```

### 3. Social Media Links
```python
# Line 31-35
SOCIAL_MEDIA = {
    'facebook': 'https://facebook.com/snowspoiledgifts',
    'instagram': 'https://www.instagram.com/sn0w_sp0ild_g1fts',
    'whatsapp': 'https://wa.me/27714711779',
}
```

**Current values are already correct for your business!**

---

## What You MUST Do for Afrihost

### ✅ Required: Create `.env` file on server

This is the **ONLY** file you need to create/edit:

**Location:** `public_html/.env`

**Content:** See `PRODUCTION_ENV_TEMPLATE.md`

```env
SECRET_KEY=<your_generated_key>
ADMIN_USERNAME=<your_choice>
ADMIN_PASSWORD=<strong_password>
MAIL_PASSWORD=<gmail_app_password>
# etc...
```

---

## Deployment Checklist

When uploading to Afrihost:

- [x] Upload `src/config.py` (already exists, no changes needed)
- [x] Upload entire `src/` folder
- [x] Upload `app.py`
- [x] Upload `templates/` folder
- [x] Upload `static/` folder
- [ ] **CREATE** `.env` file on server (use PRODUCTION_ENV_TEMPLATE.md)
- [ ] Set `.env` permissions to 600

---

## File Upload Structure

When you upload to Afrihost via FTP:

```
public_html/
├── .env                     ← CREATE THIS on server
├── .htaccess                ← Upload
├── passenger_wsgi.py        ← Upload
├── app.py                   ← Upload
├── requirements.txt         ← Upload
├── src/                     ← Upload entire folder
│   ├── __init__.py
│   ├── config.py           ← Already here, no editing!
│   ├── database.py
│   ├── email_utils.py
│   └── forms.py
├── templates/               ← Upload entire folder
├── static/                  ← Upload entire folder
└── database/                ← CREATE empty folder on server
```

---

## Summary

### What You Need to Do:

1. ✅ Upload all files including `src/config.py` as-is
2. ✅ Create `.env` file on server with your secrets
3. ✅ That's it!

### What You DON'T Need to Do:

- ❌ Edit `src/config.py` (unless changing social links)
- ❌ Create `src/config.py` (already exists)
- ❌ Put config values in multiple places

---

## Still Confused?

**Think of it this way:**

- **`.env`** = Your private secrets (passwords, keys) - Create on server
- **`src/config.py`** = Application settings - Already exists, upload as-is

**config.py reads from .env automatically!**

---

## Quick Reference

| File | Location | Action Needed |
|------|----------|---------------|
| `config.py` | `src/config.py` | Upload as-is (no editing) |
| `.env` | `public_html/.env` | **CREATE on server** |
| `.env.example` | `public_html/.env.example` | Upload (template only) |

---

**Bottom line: Just upload everything and create .env on the server! 🚀**
