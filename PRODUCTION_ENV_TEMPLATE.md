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

# Email Configuration (Gmail)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=elmienerasmus@gmail.com
MAIL_PASSWORD=<your_gmail_app_password>
MAIL_DEFAULT_SENDER=elmienerasmus@gmail.com
MAIL_CC_RECIPIENT=mariuserasmus69@gmail.com

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

### 4. MAIL_PASSWORD (Gmail App Password)

You need a Gmail App Password (not your regular Gmail password):

**Steps to get App Password:**

1. Go to: https://myaccount.google.com/apppasswords
2. Sign in to the Gmail account: `elmienerasmus@gmail.com`
3. Make sure 2-Factor Authentication is enabled
4. Click "Generate" under App Passwords
5. Select "Mail" and "Other (Custom name)"
6. Name it: "Snow's Spoiled Gifts Website"
7. Click "Generate"
8. Copy the 16-character password (example: `abcd efgh ijkl mnop`)
9. Remove spaces and paste: `abcdefghijklmnop`

```env
MAIL_PASSWORD=abcdefghijklmnop
```

**Note:** If you can't access App Passwords, you need to:
- Enable 2-Factor Authentication on Gmail first
- Then App Passwords option will appear

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

# Email Configuration (Gmail)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=elmienerasmus@gmail.com
MAIL_PASSWORD=abcdefghijklmnop
MAIL_DEFAULT_SENDER=elmienerasmus@gmail.com
MAIL_CC_RECIPIENT=mariuserasmus69@gmail.com

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
- ✅ Make sure you're using an **App Password**, not regular Gmail password
- ✅ Verify 2-Factor Authentication is enabled on Gmail
- ✅ Check password has no spaces
- ✅ Try generating a new App Password

### "Connection timeout" error:
- ✅ Verify MAIL_PORT=587
- ✅ Verify MAIL_USE_TLS=True
- ✅ Check Afrihost doesn't block port 587

### Emails not sending but no error:
- ✅ Check spam folder
- ✅ Verify MAIL_DEFAULT_SENDER email is correct
- ✅ Check Flask logs for errors

---

## Need Help?

- **Gmail App Passwords:** https://support.google.com/accounts/answer/185833
- **2-Factor Auth Setup:** https://myaccount.google.com/security

---

**This is your complete production environment configuration! 🚀**
