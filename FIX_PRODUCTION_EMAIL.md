# Fix Production Email on Afrihost - Step by Step

## 🚨 Problem
**Error:** `[Errno 99] Cannot assign requested address`

**Cause:** Afrihost blocks Gmail SMTP. You need to use Afrihost's email server instead.

---

## ✅ Solution (5 Minutes)

### Step 1: Edit `.env` File on Server

1. **Login to cPanel**
2. Go to **File Manager** → Navigate to `public_html/`
3. Find `.env` file and click **Edit**

### Step 2: Update Email Settings

Replace the Gmail settings with Afrihost SMTP:

**CHANGE FROM (Gmail - DOESN'T WORK):**
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=elmienerasmus@gmail.com
MAIL_PASSWORD=your_gmail_app_password
MAIL_DEFAULT_SENDER=elmienerasmus@gmail.com
MAIL_CC_RECIPIENT=mariuserasmus69@gmail.com
```

**CHANGE TO (Afrihost - WORKS):**
```env
MAIL_SERVER=mail.snowspoiledgifts.co.za
MAIL_PORT=465
MAIL_USE_TLS=False
MAIL_USE_SSL=True
MAIL_USERNAME=info@snowspoiledgifts.co.za
MAIL_PASSWORD=<YOUR_INFO_EMAIL_PASSWORD>
MAIL_DEFAULT_SENDER=info@snowspoiledgifts.co.za

# Multiple recipients (comma-separated, NO SPACES!)
NOTIFICATION_RECIPIENTS=elmienerasmus@gmail.com,mariuserasmus69@gmail.com
```

### Step 3: Fill in Your Email Password

Replace `<YOUR_INFO_EMAIL_PASSWORD>` with the actual password for `info@snowspoiledgifts.co.za`

**Where to find it:**
- Go to cPanel → **Email Accounts**
- Find `info@snowspoiledgifts.co.za`
- Click **Manage** → **Change Password** (or use existing password)

### Step 4: Upload Updated Code

The code has been updated to support Afrihost SMTP. You need to upload these files to your server:

**Files to upload:**
1. `src/config.py` - Added MAIL_USE_SSL support and NOTIFICATION_RECIPIENTS from .env
2. `src/email_utils.py` - Updated all email functions to support SSL (port 465)

**How to upload:**
- Via **FTP** (FileZilla): Upload to `public_html/src/`
- Via **cPanel File Manager**: Upload → Select files → Upload to `public_html/src/`
- Via **Git** (if configured): `git pull` or push latest changes

### Step 5: Restart Application

In **cPanel Terminal** or **SSH**:
```bash
cd public_html
touch tmp/restart.txt
```

Or in cPanel → **Setup Python App** → Click **Restart**

### Step 6: Test Email

1. Visit your website
2. Submit a quote request form
3. Check `elmienerasmus@gmail.com` AND `mariuserasmus69@gmail.com` for emails
4. Both should receive the notification!

---

## 🔍 How to Check if it Worked

### Check Application Logs

In cPanel → **Metrics** → **Errors** or via SSH:
```bash
tail -f logs/error.log
```

**Success:** No email errors in logs

**Still failing?** Check troubleshooting below

---

## 🐛 Troubleshooting

### Error: "Authentication failed"
**Fix:**
- Verify `info@snowspoiledgifts.co.za` password is correct
- Try resetting password in cPanel → Email Accounts

### Error: "Connection refused" or "Timeout"
**Fix:**
- Verify `MAIL_PORT=465` (not 587)
- Verify `MAIL_USE_SSL=True` (not MAIL_USE_TLS)
- Verify `MAIL_SERVER=mail.snowspoiledgifts.co.za`

### Only one person receiving emails (not both)
**Fix:**
- Check `NOTIFICATION_RECIPIENTS=elmienerasmus@gmail.com,mariuserasmus69@gmail.com`
- **Important:** NO SPACES between emails!
- Comma-separated only

### Still not working?
**Test email from cPanel:**
1. Go to cPanel → **Email Accounts**
2. Click **Check Email** next to `info@snowspoiledgifts.co.za`
3. Try sending a test email to yourself
4. If this fails, contact Afrihost support

---

## 📝 Summary of Changes

### What Changed in Code:

1. **`src/config.py`:**
   - Added `MAIL_USE_SSL` configuration
   - Changed `NOTIFICATION_RECIPIENTS` to read from `.env` (comma-separated)

2. **`src/email_utils.py`:**
   - Updated all 5 email functions to support SSL (SMTP_SSL for port 465)
   - Kept TLS support for future use (STARTTLS for port 587)

3. **`.env` file (production):**
   - Changed from Gmail to Afrihost SMTP
   - Added both email addresses to `NOTIFICATION_RECIPIENTS`

### What You Get:

✅ Emails send from `info@snowspoiledgifts.co.za` (more professional!)
✅ Both `elmienerasmus@gmail.com` AND `mariuserasmus69@gmail.com` receive notifications
✅ No more "[Errno 99]" errors
✅ Works with Afrihost's SMTP restrictions

---

## 🎯 Quick Checklist

- [ ] Edit `.env` on server
- [ ] Set `MAIL_SERVER=mail.snowspoiledgifts.co.za`
- [ ] Set `MAIL_PORT=465`
- [ ] Set `MAIL_USE_SSL=True`
- [ ] Set `MAIL_USE_TLS=False`
- [ ] Set `MAIL_USERNAME=info@snowspoiledgifts.co.za`
- [ ] Set `MAIL_PASSWORD=<your_actual_password>`
- [ ] Set `NOTIFICATION_RECIPIENTS=elmienerasmus@gmail.com,mariuserasmus69@gmail.com`
- [ ] Upload updated `src/config.py`
- [ ] Upload updated `src/email_utils.py`
- [ ] Restart application (`touch tmp/restart.txt`)
- [ ] Test by submitting a quote request
- [ ] Verify both emails received notification

---

**Need Help?** Check `PRODUCTION_ENV_TEMPLATE.md` for complete `.env` example

**Done!** 🎉 Your email notifications should now work perfectly!
