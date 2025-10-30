# Snow Spoiled Gifts - Deployment Checklist

**Phase 4: Admin Order Management - Complete**
**Date:** 2025-10-30
**Status:** Ready for Production Deployment ✅

---

## Pre-Deployment Checklist

### 1. Database Setup ✅
- [x] Users table includes `is_admin` column
- [x] Orders table fully configured with all shipping fields
- [x] Order items table ready
- [x] Database migrations tested
- [x] Admin users configured:
  - mariuserasmus69@gmail.com ✅
  - elmienerasmus@gmail.com (pending registration)
  - meganmerasmus@gmail.com (pending registration)

### 2. Admin Features ✅
- [x] Admin authentication system
- [x] Admin-specific navbar with orders/quotes/items/signups
- [x] Orders dashboard with status filtering
- [x] Order detail view with full information
- [x] Order status management
- [x] Email notifications for status changes

### 3. Customer Features ✅
- [x] User registration and login
- [x] Shopping cart functionality
- [x] Complete checkout flow
- [x] Multiple shipping methods (Pickup, Own Courier, PUDO)
- [x] Order confirmation page
- [x] Order history in user account
- [x] Dark mode support

### 4. Email System ⚠️
**Action Required: Configure Production SMTP**

#### Required Environment Variables (.env file):
```bash
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_SSL=False
MAIL_USERNAME=info@snowspoiledgifts.co.za
MAIL_PASSWORD=your-app-specific-password
MAIL_DEFAULT_SENDER=info@snowspoiledgifts.co.za
ADMIN_EMAIL=info@snowspoiledgifts.co.za
```

#### Email Templates Ready:
- [x] Order confirmation (customer + admin)
- [x] Order status updates (pending/confirmed/shipped/delivered)
- [x] Quote request notifications
- [x] Signup confirmations

#### Testing Checklist:
- [ ] Send test order confirmation email
- [ ] Test all 4 status update emails
- [ ] Verify admin receives order notifications
- [ ] Check email formatting on mobile devices

---

## Deployment Steps

### Step 1: Server Setup
```bash
# Update server packages
sudo apt update && sudo apt upgrade -y

# Install Python 3.10+
sudo apt install python3 python3-pip python3-venv -y

# Install Git
sudo apt install git -y
```

### Step 2: Clone Repository
```bash
cd /var/www
sudo git clone <your-repo-url> ssg
cd ssg
sudo chown -R $USER:$USER /var/www/ssg
```

### Step 3: Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 4: Configure Environment
```bash
# Create .env file
cp .env.example .env
nano .env
```

**Required .env Contents:**
```bash
# Flask Config
SECRET_KEY=<generate-secure-random-key>
FLASK_ENV=production
DEBUG=False

# Database
DATABASE_PATH=database/signups.db

# Email Configuration (CRITICAL for production!)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_SSL=False
MAIL_USERNAME=info@snowspoiledgifts.co.za
MAIL_PASSWORD=<your-gmail-app-password>
MAIL_DEFAULT_SENDER=info@snowspoiledgifts.co.za
ADMIN_EMAIL=info@snowspoiledgifts.co.za

# Admin Credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD=<secure-password>

# Site Configuration
SITE_NAME=Snow Spoiled Gifts
BASE_URL=https://snowspoiledgifts.co.za
```

### Step 5: Initialize Database
```bash
# Database will auto-create on first run
# Run migrations by starting the app once
python app.py
# Stop with Ctrl+C after database is created
```

### Step 6: Set Admin Users
```bash
# Run the admin setup script
python set_admins.py
```

### Step 7: Configure Gunicorn
```bash
# Install Gunicorn
pip install gunicorn

# Create systemd service
sudo nano /etc/systemd/system/ssg.service
```

**Service File Content:**
```ini
[Unit]
Description=Snow Spoiled Gifts Web Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/ssg
Environment="PATH=/var/www/ssg/venv/bin"
ExecStart=/var/www/ssg/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 app:app

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable ssg
sudo systemctl start ssg
sudo systemctl status ssg
```

### Step 8: Configure Nginx
```bash
sudo nano /etc/nginx/sites-available/ssg
```

**Nginx Configuration:**
```nginx
server {
    listen 80;
    server_name snowspoiledgifts.co.za www.snowspoiledgifts.co.za;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /var/www/ssg/static;
        expires 30d;
    }

    client_max_body_size 50M;
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/ssg /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Step 9: SSL Certificate (Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d snowspoiledgifts.co.za -d www.snowspoiledgifts.co.za
```

### Step 10: Set Permissions
```bash
sudo chown -R www-data:www-data /var/www/ssg
sudo chmod -R 755 /var/www/ssg
sudo chmod 600 /var/www/ssg/.env
```

---

## Post-Deployment Testing

### Critical Tests
- [ ] Admin login works
- [ ] Admin can view orders dashboard
- [ ] Admin can update order status
- [ ] Customer can register/login
- [ ] Customer can add items to cart
- [ ] Customer can complete checkout
- [ ] Order confirmation email sent
- [ ] Admin receives order notification
- [ ] Status update emails work
- [ ] Dark mode toggle works
- [ ] All shipping methods work correctly
- [ ] PUDO options calculate shipping properly

### Performance Tests
- [ ] Page load times < 2 seconds
- [ ] Database queries optimized
- [ ] Static files cached properly
- [ ] Images load correctly

### Security Tests
- [ ] HTTPS enabled and working
- [ ] Admin routes protected
- [ ] SQL injection protected (using parameterized queries)
- [ ] XSS protected (Flask auto-escaping)
- [ ] CSRF tokens in forms
- [ ] Secure password hashing (bcrypt)

---

## Monitoring & Maintenance

### Log Files
```bash
# Application logs
sudo journalctl -u ssg -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Database Backup
```bash
# Create backup script
nano /var/www/ssg/backup.sh
```

**Backup Script:**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/ssg"
mkdir -p $BACKUP_DIR
cp /var/www/ssg/database/signups.db $BACKUP_DIR/signups_$DATE.db
# Keep only last 30 days
find $BACKUP_DIR -name "signups_*.db" -mtime +30 -delete
```

```bash
chmod +x /var/www/ssg/backup.sh

# Add to crontab (daily at 2 AM)
crontab -e
0 2 * * * /var/www/ssg/backup.sh
```

### SSL Certificate Renewal
```bash
# Certbot auto-renewal is enabled by default
# Test renewal
sudo certbot renew --dry-run
```

---

## Quick Reference

### Restart Application
```bash
sudo systemctl restart ssg
```

### View Logs
```bash
sudo journalctl -u ssg -n 100
```

### Update Code
```bash
cd /var/www/ssg
git pull origin main
sudo systemctl restart ssg
```

### Database Management
```bash
# Interactive SQLite shell
sqlite3 database/signups.db

# Common queries:
# List all orders
SELECT order_number, customer_name, status, total_amount FROM orders ORDER BY created_date DESC;

# Count orders by status
SELECT status, COUNT(*) FROM orders GROUP BY status;
```

---

## Troubleshooting

### Email Not Sending
1. Check `.env` has correct MAIL_PASSWORD
2. Verify Gmail App Password is generated
3. Check firewall allows SMTP ports
4. Test SMTP connection:
```bash
python -c "import smtplib; smtplib.SMTP('smtp.gmail.com', 587).starttls()"
```

### Application Won't Start
1. Check logs: `sudo journalctl -u ssg -n 50`
2. Verify virtual environment: `source venv/bin/activate`
3. Test manually: `python app.py`
4. Check file permissions

### Database Errors
1. Ensure database directory exists: `mkdir -p database`
2. Check permissions: `ls -la database/`
3. Run migrations manually (app auto-migrates on startup)

---

## Feature Summary

### Phase 1-3 (Completed Previously)
- ✅ Email signup system
- ✅ Quote request forms (3D printing, cake toppers, print service)
- ✅ Cookie cutter catalog with search/filters
- ✅ Shopping cart system
- ✅ User authentication (register/login)
- ✅ Checkout flow with multiple shipping options
- ✅ Order management database

### Phase 4 (Just Completed)
- ✅ Admin user roles
- ✅ Admin navbar with quick access
- ✅ Orders dashboard with filtering
- ✅ Order detail view with full information
- ✅ Order status management
- ✅ Email notifications for status updates
- ✅ Dark mode throughout admin interface

---

## Next Steps (Future Enhancements)

### Payment Integration (Phase 5 - Optional)
- PayFast integration for online payments
- Payment confirmation handling
- Invoice PDF generation

### Advanced Features (Phase 6 - Optional)
- Order tracking with courier integration
- SMS notifications via Twilio
- Inventory management
- Analytics dashboard
- Customer reviews/ratings

---

## Production URLs

- **Main Site:** https://snowspoiledgifts.co.za
- **Admin Login:** https://snowspoiledgifts.co.za/admin/login
- **Admin Panel:** https://snowspoiledgifts.co.za/admin/orders

---

## Support Contacts

**Admin Users:**
- Marius Erasmus: mariuserasmus69@gmail.com (Active Admin)
- Elmiene Erasmus: elmienerasmus@gmail.com (Pending)
- Megan Erasmus: meganmerasmus@gmail.com (Pending)

**Technical Contact:**
- Developer: [Your Contact]

---

**Deployment Status: READY ✅**

**Estimated Deployment Time:** 45-60 minutes
**Critical Path Item:** Email SMTP configuration

---

*This deployment checklist was generated on 2025-10-30 as part of Phase 4 completion.*
