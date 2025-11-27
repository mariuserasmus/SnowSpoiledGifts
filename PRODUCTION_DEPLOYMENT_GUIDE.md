# Production Deployment Guide - Snow Spoiled Gifts
## WhatsApp Business API & Feature Updates

---

## 📋 OVERVIEW

This deployment includes:
- ✅ WhatsApp Business API integration (verified SA number)
- ✅ Phone number capture on all quote forms
- ✅ Email template updates with WhatsApp contact
- ✅ Admin WhatsApp inbox and messaging
- ✅ Customer-facing WhatsApp support options

---

## 🗄️ DATABASE MIGRATION REQUIRED

### **CRITICAL: Run this SQL on production database BEFORE deploying code**

```sql
-- Add phone column to print_service_requests table
ALTER TABLE print_service_requests ADD COLUMN phone TEXT;

-- Create whatsapp_messages table
CREATE TABLE IF NOT EXISTS whatsapp_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id TEXT UNIQUE,
    direction TEXT NOT NULL,  -- 'inbound' or 'outbound'
    from_phone TEXT NOT NULL,
    to_phone TEXT NOT NULL,
    message_text TEXT,
    message_type TEXT DEFAULT 'text',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_read INTEGER DEFAULT 0,
    conversation_id TEXT,
    user_id INTEGER,
    quote_id INTEGER,
    quote_type TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (quote_id) REFERENCES custom_design_requests(id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_whatsapp_conversation ON whatsapp_messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_whatsapp_timestamp ON whatsapp_messages(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_whatsapp_read ON whatsapp_messages(is_read);
CREATE INDEX IF NOT EXISTS idx_whatsapp_user ON whatsapp_messages(user_id);
```

**How to run on Afrihost:**
1. SSH into your server
2. Navigate to project directory
3. Run: `sqlite3 database/signups.db < migration.sql`

Or use a database management tool to run the SQL directly.

---

## 🔧 ENVIRONMENT VARIABLES (.env)

### **Update your production .env file with these values:**

```bash
# WhatsApp Business API - PRODUCTION
WHATSAPP_PHONE_NUMBER_ID=804077982799067
WHATSAPP_ACCESS_TOKEN=YOUR_PERMANENT_ACCESS_TOKEN_HERE
WHATSAPP_BUSINESS_ACCOUNT_ID=4123964607775539
WHATSAPP_WEBHOOK_VERIFY_TOKEN=ssg_webhook_secret_2024

# WhatsApp Contact Info (Customer-facing)
WHATSAPP_CONTACT_LINK=https://wa.me/27826754285
WHATSAPP_CONTACT_NUMBER=+27 82 675 4285

# Site Configuration - UPDATE THESE
SITE_URL=https://www.snowspoiledgifts.co.za  # YOUR PRODUCTION DOMAIN
SITE_NAME=Snows Spoiled Gifts
```

### **⚠️ IMPORTANT: WhatsApp Access Token**

Your current token will expire. Generate a **permanent token**:

1. Go to: https://developers.facebook.com/apps
2. Select your app → System Users
3. Generate permanent token with permissions:
   - `whatsapp_business_messaging`
   - `whatsapp_business_management`
4. Copy token and update WHATSAPP_ACCESS_TOKEN in production .env

---

## 🔗 META WEBHOOK CONFIGURATION

### **CRITICAL: Update webhook URL to production domain**

1. **Go to:** https://developers.facebook.com/apps
2. **Select:** SSG Client Messaging app
3. **Navigate to:** WhatsApp → Configuration
4. **Update Callback URL to:**
   ```
   https://www.snowspoiledgifts.co.za/webhooks/whatsapp
   ```
   (Replace with your actual production domain)

5. **Verify Token:** `ssg_webhook_secret_2024`

6. **Click:** "Verify and Save"

7. **Subscribe to webhook fields:**
   - ✅ **messages** (REQUIRED for receiving messages)

### **❌ DO NOT USE NGROK IN PRODUCTION**

- ngrok is ONLY for local development
- Production must use your actual domain (www.snowspoiledgifts.co.za)
- Webhook URL must be publicly accessible HTTPS

---

## 📦 DEPLOYMENT STEPS

### **1. Push Code to Git**

```bash
git push origin main
```

### **2. Pull on Production Server**

```bash
ssh your-server
cd /path/to/ssg
git pull origin main
```

### **3. Install Dependencies**

```bash
pip install -r requirements.txt
# or
pip3 install -r requirements.txt
```

New dependency added: `requests>=2.31.0`

### **4. Run Database Migration**

```bash
# Option A: Direct SQL file
sqlite3 database/signups.db < migration.sql

# Option B: Python script (create migration.sql first)
python -c "
import sqlite3
conn = sqlite3.connect('database/signups.db')
cursor = conn.cursor()

# Add phone column
cursor.execute('ALTER TABLE print_service_requests ADD COLUMN phone TEXT')

# Create whatsapp_messages table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS whatsapp_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message_id TEXT UNIQUE,
        direction TEXT NOT NULL,
        from_phone TEXT NOT NULL,
        to_phone TEXT NOT NULL,
        message_text TEXT,
        message_type TEXT DEFAULT 'text',
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_read INTEGER DEFAULT 0,
        conversation_id TEXT,
        user_id INTEGER,
        quote_id INTEGER,
        quote_type TEXT
    )
''')

# Create indexes
cursor.execute('CREATE INDEX IF NOT EXISTS idx_whatsapp_conversation ON whatsapp_messages(conversation_id)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_whatsapp_timestamp ON whatsapp_messages(timestamp DESC)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_whatsapp_read ON whatsapp_messages(is_read)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_whatsapp_user ON whatsapp_messages(user_id)')

conn.commit()
conn.close()
print('✅ Migration complete!')
"
```

### **5. Update .env on Production**

```bash
nano .env
# Update WhatsApp variables as shown above
# Update SITE_URL to production domain
```

### **6. Restart Application**

```bash
# If using systemd
sudo systemctl restart ssg

# If using supervisor
sudo supervisorctl restart ssg

# If running manually
pkill -f "python.*app.py"
python app.py
```

---

## ✅ POST-DEPLOYMENT VERIFICATION

### **1. Check Application Started**

```bash
# Check logs
tail -f /var/log/ssg/error.log

# Or if using systemd
journalctl -u ssg -f
```

### **2. Test Webhook**

Send a WhatsApp message to **+27 82 675 4285** from your phone:
- Message should appear in admin inbox
- Check Flask logs for webhook activity

### **3. Test Admin Panel**

1. Go to: `https://www.snowspoiledgifts.co.za/admin/whatsapp-inbox`
2. Verify message from step 2 appears
3. Reply to the message
4. Confirm reply arrives on your phone

### **4. Test Customer Flow**

1. Go to 3D Print Service quote form
2. Submit quote with phone number
3. Message business on WhatsApp
4. Admin should be able to reply from quotes page

### **5. Verify Email Templates**

Submit a test quote and check confirmation email includes:
- WhatsApp contact info in footer
- Correct SA phone number (+27 82 675 4285)

---

## 🚨 TROUBLESHOOTING

### **Webhooks Not Working**

**Symptom:** Messages sent to +27 82 675 4285 don't appear in admin inbox

**Solutions:**
1. Check webhook URL is set to production domain (NOT ngrok)
2. Verify "messages" field is subscribed in Meta
3. Check Flask logs for webhook errors
4. Test webhook endpoint: `curl https://yourdomain.com/webhooks/whatsapp?hub.mode=subscribe&hub.verify_token=ssg_webhook_secret_2024&hub.challenge=test`
   - Should return: `test`

### **Can't Send Messages**

**Symptom:** Error when trying to send WhatsApp from admin

**Solutions:**
1. Check WHATSAPP_ACCESS_TOKEN is valid (not expired)
2. Verify WHATSAPP_PHONE_NUMBER_ID is correct (804077982799067)
3. Check Flask logs for API error messages
4. Ensure 24-hour window is open (customer must message first)

### **Database Errors**

**Symptom:** SQL errors about missing columns/tables

**Solution:**
- Run the database migration SQL again
- Check database file permissions
- Verify migration completed successfully

### **Phone Number Format Issues**

**Symptom:** "Invalid phone number" errors

**Solution:**
- Phone numbers must be in format: 27xxxxxxxxx (no + or spaces)
- South African numbers: 0825522848 → 27825522848
- Check `format_phone_number()` in src/whatsapp_utils.py

---

## 📊 MONITORING

### **Check WhatsApp Usage**

1. Go to: https://developers.facebook.com/apps
2. Select app → WhatsApp → Analytics
3. Monitor message volumes and delivery rates

### **Database Health**

```bash
# Check message count
sqlite3 database/signups.db "SELECT COUNT(*) FROM whatsapp_messages;"

# Check recent messages
sqlite3 database/signups.db "SELECT direction, from_phone, message_text, timestamp FROM whatsapp_messages ORDER BY timestamp DESC LIMIT 10;"

# Check unread messages
sqlite3 database/signups.db "SELECT COUNT(*) FROM whatsapp_messages WHERE is_read = 0 AND direction = 'inbound';"
```

---

## 🔒 SECURITY NOTES

1. **Never commit .env to git** - Contains sensitive tokens
2. **Rotate access tokens regularly** - Generate new permanent tokens every 90 days
3. **Keep webhook verify token secret** - Used to validate incoming webhooks
4. **Monitor API usage** - Watch for unusual activity in Meta dashboard

---

## 📱 WHATSAPP LIMITATIONS

### **Current Setup (Free-Form Messages):**
- ✅ Can send ANY text message
- ❌ Customer must message FIRST to open 24-hour window
- ❌ Cannot initiate conversations proactively

### **Future: Template Messages (Optional):**
To send proactive messages (e.g., "Your quote is ready!"):
1. Create message templates in Meta Business Manager
2. Submit for approval (24-48 hours)
3. Update code to use template API
4. Requires payment method on file with Meta

---

## 🎯 SUCCESS CRITERIA

After deployment, you should be able to:

✅ Customers can message +27 82 675 4285 on WhatsApp
✅ Messages appear in `/admin/whatsapp-inbox`
✅ Admin can reply from inbox
✅ Admin can send WhatsApp from quotes page
✅ All quote forms capture phone numbers
✅ Email templates show WhatsApp contact
✅ Floating WhatsApp button appears on all pages
✅ Two-way messaging fully functional

---

## 📞 SUPPORT

If you encounter issues:

1. **Check Flask logs first** - Most errors show up here
2. **Verify Meta webhook configuration** - Common issue
3. **Test with curl** - Verify endpoints are accessible
4. **Check database** - Ensure migration completed

---

## 🎉 YOU'RE PRODUCTION READY!

Your WhatsApp Business API integration is fully configured and ready to handle customer inquiries. The system will:

- Automatically capture incoming WhatsApp messages
- Store conversations in database
- Notify admin of new messages
- Allow organized replies from admin panel
- Track message history per customer
- Link conversations to existing users/quotes

**Welcome to professional WhatsApp Business messaging!** 🚀

---

Generated: November 2024
Version: 1.0
System: Snow Spoiled Gifts - SSG
