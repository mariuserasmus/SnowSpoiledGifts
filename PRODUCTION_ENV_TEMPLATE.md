# Production .env Configuration for Afrihost

## Create this file on your Afrihost server at: `public_html/.env`

Copy and paste this template, then fill in the values marked with `<...>`:

```env
# Flask Configuration
SECRET_KEY=<GENERATE_NEW_KEY_SEE_BELOW>
FLASK_ENV=production
DEBUG=False

# Admin Credentials - CHANGE THESE!
ADMIN_USERNAME=<your_chosen_admin_username>
ADMIN_PASSWORD=<your_strong_password>

# Database
DATABASE_PATH=database/signups.db

# Email Configuration (Afrihost SMTP - RECOMMENDED)
MAIL_SERVER=mail.snowspoiledgifts.co.za
MAIL_PORT=465
MAIL_USE_TLS=False
MAIL_USE_SSL=True
MAIL_USERNAME=info@snowspoiledgifts.co.za
MAIL_PASSWORD=<your_info_email_password>
MAIL_DEFAULT_SENDER=info@snowspoiledgifts.co.za

# Notification Recipients (comma-separated, no spaces)
NOTIFICATION_RECIPIENTS=elmienerasmus@gmail.com,mariuserasmus69@gmail.com

# Site Configuration
SITE_URL=https://www.snowspoiledgifts.co.za
SITE_NAME=Snow's Spoiled Gifts
BASE_URL=https://www.snowspoiledgifts.co.za
```

---

## How to Fill In the Values

### 1. SECRET_KEY

Generate a secure random key. Run this command on your local machine or server:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Example output: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2`

Paste the result into `SECRET_KEY=`

### 2. ADMIN_USERNAME

Choose a secure username (NOT "admin"):

```env
ADMIN_USERNAME=elmien_admin
```

### 3. ADMIN_PASSWORD

Create a strong password with:
- At least 12 characters
- Mix of uppercase, lowercase, numbers, symbols

Example: `Sn0w$G1ft$2025!Secure`

```env
ADMIN_PASSWORD=YourStrongPasswordHere
```

### 4. MAIL_PASSWORD (Afrihost Email Password)

Use the password for your `info@snowspoiledgifts.co.za` email account:

**Where to find/set it:**

1. Go to: **cPanel → Email Accounts**
2. Find: `info@snowspoiledgifts.co.za`
3. Click "Manage" or "Change Password"
4. Either use existing password or set a new strong password
5. Copy the password

```env
MAIL_PASSWORD=YourEmailPasswordHere
```

**Important:** This is the password you use to check email for `info@snowspoiledgifts.co.za`, not your cPanel password.

---

## Complete Example (CHANGE ALL VALUES!)

```env
# Flask Configuration
SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2
FLASK_ENV=production
DEBUG=False

# Admin Credentials
ADMIN_USERNAME=elmien_admin
ADMIN_PASSWORD=Sn0w$G1ft$2025!Secure

# Database
DATABASE_PATH=database/signups.db

# Email Configuration (Afrihost SMTP)
MAIL_SERVER=mail.snowspoiledgifts.co.za
MAIL_PORT=465
MAIL_USE_TLS=False
MAIL_USE_SSL=True
MAIL_USERNAME=info@snowspoiledgifts.co.za
MAIL_PASSWORD=YourInfoEmailPassword123
MAIL_DEFAULT_SENDER=info@snowspoiledgifts.co.za

# Notification Recipients (comma-separated, no spaces)
NOTIFICATION_RECIPIENTS=elmienerasmus@gmail.com,mariuserasmus69@gmail.com

# Site Configuration
SITE_URL=https://www.snowspoiledgifts.co.za
SITE_NAME=Snow's Spoiled Gifts
BASE_URL=https://www.snowspoiledgifts.co.za
```

---

## Security Checklist

After creating the `.env` file on Afrihost:

1. **Set file permissions to 600** (only owner can read/write):
   ```bash
   chmod 600 .env
   ```

2. **Verify .env is NOT publicly accessible:**
   - Try visiting: `https://www.snowspoiledgifts.co.za/.env`
   - Should get 403 Forbidden error
   - The `.htaccess` file already protects it

3. **Never commit .env to Git** (already in .gitignore)

4. **Keep backup copy** of production .env file securely offline

---

## Testing Email Configuration

After deployment, test the email system:

1. Visit your site and submit a quote request form
2. Check if email arrives at `elmienerasmus@gmail.com`
3. Check if CC arrives at `mariuserasmus69@gmail.com`
4. Check server logs if email fails

---

## Troubleshooting Email Issues

### "Authentication failed" error:
- ✅ Verify you're using the correct `info@snowspoiledgifts.co.za` password
- ✅ Check password has no spaces or special characters that need escaping
- ✅ Try resetting the email password in cPanel
- ✅ Confirm MAIL_USERNAME is the full email address

### "[Errno 99] Cannot assign requested address" error:
- ✅ This means Gmail SMTP is blocked by Afrihost
- ✅ **Solution:** Use Afrihost SMTP (mail.snowspoiledgifts.co.za) as shown above
- ✅ Make sure MAIL_PORT=465 and MAIL_USE_SSL=True

### "Connection timeout" error:
- ✅ Verify MAIL_PORT=465
- ✅ Verify MAIL_USE_SSL=True (not MAIL_USE_TLS)
- ✅ Verify MAIL_SERVER=mail.snowspoiledgifts.co.za
- ✅ Check if port 465 is open (should be on Afrihost)

### Emails not sending but no error:
- ✅ Check spam folder in recipient email
- ✅ Verify MAIL_DEFAULT_SENDER email exists (info@snowspoiledgifts.co.za)
- ✅ Check Flask logs: `tail -f logs/error.log` or cPanel error logs
- ✅ Test sending email from cPanel webmail first

---

## Need Help?

- **Gmail App Passwords:** https://support.google.com/accounts/answer/185833
- **2-Factor Auth Setup:** https://myaccount.google.com/security

---

**This is your complete production environment configuration! 🚀**
