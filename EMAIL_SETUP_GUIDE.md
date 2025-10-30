# Email Configuration Guide

## Overview

The application uses different email configurations for **DEV** and **PRODUCTION** environments:

| Environment | Email Account | Current Status |
|-------------|---------------|----------------|
| **DEV** | mariuserasmus69@gmail.com | ✅ Configured & Working |
| **PRODUCTION** | info@snowspoiledgifts.co.za | ⏳ Needs Configuration |

---

## DEV Environment (Current Setup)

### ✅ Already Configured
Your development environment is **already set up** and working with Gmail:

**Current `.env` Configuration:**
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=mariuserasmus69@gmail.com
MAIL_PASSWORD=zuccnyjdmlufveue
MAIL_DEFAULT_SENDER=elmienerasmus@gmail.com
ADMIN_EMAIL=elmienerasmus@gmail.com
```

### Email Flow in DEV:
1. **Customer Emails** → Sent from `elmienerasmus@gmail.com`
2. **Admin Notifications** → Sent to `elmienerasmus@gmail.com`
3. **SMTP Authentication** → Uses `mariuserasmus69@gmail.com` credentials

**This setup is working and should not be changed for development.**

---

## PRODUCTION Environment (Needs Setup)

### Option 1: Domain Email via Hosting Provider (Recommended)

Most hosting providers (cPanel, Plesk, etc.) include email hosting.

#### Steps:
1. **Check Your Hosting Control Panel**
   - Log into your hosting account (where snowspoiledgifts.co.za is hosted)
   - Look for "Email Accounts" or "Email" section

2. **Get SMTP Details**
   - Server: Usually `mail.snowspoiledgifts.co.za` or `smtp.snowspoiledgifts.co.za`
   - Port: Usually `587` (TLS) or `465` (SSL)
   - Username: `info@snowspoiledgifts.co.za`
   - Password: Set in hosting panel

3. **Update `.env` in Production:**
```env
MAIL_SERVER=mail.snowspoiledgifts.co.za
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=info@snowspoiledgifts.co.za
MAIL_PASSWORD=<password-from-hosting-panel>
MAIL_DEFAULT_SENDER=info@snowspoiledgifts.co.za
ADMIN_EMAIL=info@snowspoiledgifts.co.za
```

---

### Option 2: Google Workspace (If Using Gmail for Domain)

If `info@snowspoiledgifts.co.za` is hosted on Google Workspace:

#### Steps:
1. **Enable 2FA** on Google Workspace admin account
2. **Generate App Password:**
   - Go to: https://myaccount.google.com/apppasswords
   - App: Mail
   - Device: Web App
   - Copy the 16-character password

3. **Update `.env` in Production:**
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=info@snowspoiledgifts.co.za
MAIL_PASSWORD=<16-char-app-password>
MAIL_DEFAULT_SENDER=info@snowspoiledgifts.co.za
ADMIN_EMAIL=info@snowspoiledgifts.co.za
```

---

### Option 3: Keep Using Gmail (Not Recommended for Production)

If you want to keep using `mariuserasmus69@gmail.com` in production (not ideal):

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=mariuserasmus69@gmail.com
MAIL_PASSWORD=zuccnyjdmlufveue
MAIL_DEFAULT_SENDER=info@snowspoiledgifts.co.za  # Display as domain email
ADMIN_EMAIL=elmienerasmus@gmail.com
```

**Why not recommended:**
- Less professional (emails come from Gmail instead of your domain)
- Gmail daily sending limits (500 emails/day)
- May trigger spam filters

---

## Email Types Sent by Application

### 1. Order Confirmation Emails
**Sent to:** Customer + Admin
**When:** Customer completes checkout
**From:** `MAIL_DEFAULT_SENDER`
**Template:** HTML + Plain Text

### 2. Order Status Update Emails
**Sent to:** Customer
**When:** Admin updates order status
**From:** `MAIL_DEFAULT_SENDER`
**Statuses:** Pending → Confirmed → Shipped → Delivered

### 3. Quote Request Notifications
**Sent to:** Admin
**When:** Customer submits quote request
**From:** `MAIL_DEFAULT_SENDER`

### 4. Signup Confirmations
**Sent to:** Customer
**When:** User signs up for email list
**From:** `MAIL_DEFAULT_SENDER`

---

## Testing Email Configuration

### Test in DEV (Already Working)
```bash
cd c:\Claude\SSG
python
>>> from flask import Flask
>>> from src.config import Config
>>> app = Flask(__name__)
>>> app.config.from_object(Config)
>>> from src.email_utils import send_order_status_update
>>> send_order_status_update(app.config, 'your-test-email@gmail.com', 'SSG-202510-001', 'confirmed', 'Test User')
>>> exit()
```

### Test in Production
```bash
# After deployment
cd /var/www/ssg
source venv/bin/activate
python
>>> from flask import Flask
>>> from src.config import Config
>>> app = Flask(__name__)
>>> app.config.from_object(Config)
>>> from src.email_utils import send_order_status_update
>>> send_order_status_update(app.config, 'elmienerasmus@gmail.com', 'TEST-001', 'confirmed', 'Elmiene')
>>> exit()
```

---

## Troubleshooting

### "Failed to send email" Error

**Check 1: SMTP Credentials**
```bash
python -c "import smtplib; s=smtplib.SMTP('smtp.gmail.com', 587); s.starttls(); s.login('your-email', 'your-password'); print('SMTP OK')"
```

**Check 2: Firewall**
```bash
# Test port 587 (TLS)
telnet smtp.gmail.com 587

# Test port 465 (SSL)
telnet smtp.gmail.com 465
```

**Check 3: Environment Variables Loaded**
```python
from src.config import Config
print(f"Mail Server: {Config.MAIL_SERVER}")
print(f"Mail Username: {Config.MAIL_USERNAME}")
print(f"Mail Password Set: {'Yes' if Config.MAIL_PASSWORD else 'No'}")
```

---

### Gmail-Specific Issues

**Error: "Username and Password not accepted"**
- Ensure 2FA is enabled on Gmail account
- Use App Password, not regular password
- App Password should be 16 characters (xxxx xxxx xxxx xxxx)

**Error: "SMTP AUTH extension not supported"**
- Ensure you're using `starttls()` with port 587
- OR use SSL on port 465

**Daily Limit Exceeded:**
- Gmail has 500 emails/day limit for regular accounts
- Google Workspace has 2000 emails/day limit
- Consider using domain email for higher limits

---

### Domain Email Issues

**Error: "Connection refused"**
- Verify SMTP server address with hosting provider
- Check if port 587 or 465 is correct
- Ensure firewall allows outbound SMTP

**Error: "Authentication failed"**
- Verify email account exists in hosting panel
- Check username format (full email vs just username)
- Reset password in hosting panel

---

## Security Best Practices

### ✅ DO:
- Use App Passwords for Gmail (never use main password)
- Set `MAIL_PASSWORD` only in `.env` (never commit to git)
- Use TLS/SSL for SMTP connections
- Restrict `.env` file permissions: `chmod 600 .env`
- Use different passwords for DEV and PRODUCTION

### ❌ DON'T:
- Commit `.env` files to git (already in `.gitignore`)
- Share SMTP credentials in Slack/email
- Use weak passwords for email accounts
- Disable TLS/SSL for SMTP

---

## Configuration Checklist

### DEV Environment ✅
- [x] SMTP server configured
- [x] Gmail app password set
- [x] Email sending works
- [x] `.env` file secured

### PRODUCTION Environment
- [ ] Domain email account created (`info@snowspoiledgifts.co.za`)
- [ ] SMTP credentials obtained from hosting provider
- [ ] `.env.production` configured
- [ ] Test email sent successfully
- [ ] Admin notification email received
- [ ] Customer confirmation email received

---

## Quick Reference

### DEV Configuration (Current)
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=mariuserasmus69@gmail.com
MAIL_PASSWORD=zuccnyjdmlufveue
MAIL_DEFAULT_SENDER=elmienerasmus@gmail.com
ADMIN_EMAIL=elmienerasmus@gmail.com
```

### PRODUCTION Configuration (Template)
```env
MAIL_SERVER=mail.snowspoiledgifts.co.za  # OR smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=info@snowspoiledgifts.co.za
MAIL_PASSWORD=<get-from-hosting-provider>
MAIL_DEFAULT_SENDER=info@snowspoiledgifts.co.za
ADMIN_EMAIL=info@snowspoiledgifts.co.za
```

---

## Support

**Hosting Provider SMTP Help:**
- Contact your hosting provider's support
- Ask for "SMTP settings for outgoing mail"
- Mention you need it for a web application

**Google Workspace Help:**
- https://support.google.com/a/answer/176600
- Google Workspace SMTP settings

**Gmail App Password:**
- https://myaccount.google.com/apppasswords
- Requires 2FA to be enabled

---

**Last Updated:** 2025-10-30
**Version:** 1.4.0 (Phase 4)
