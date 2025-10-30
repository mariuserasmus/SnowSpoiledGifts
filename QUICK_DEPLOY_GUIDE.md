# 🚀 Quick Deploy Guide - Snow Spoiled Gifts

**Status:** Ready for Production ✅
**Estimated Time:** 45-60 minutes
**Critical Dependency:** Email SMTP Configuration

---

## ⚡ Quick Start (For Experienced Admins)

```bash
# 1. Server Setup
sudo apt update && sudo apt install python3 python3-pip python3-venv git nginx certbot -y

# 2. Clone & Setup
cd /var/www
git clone <repo-url> ssg && cd ssg
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt gunicorn

# 3. Configure Environment
cp .env.example .env
nano .env  # Add MAIL_PASSWORD and SECRET_KEY

# 4. Initialize & Set Admins
python app.py  # Ctrl+C after database created
python set_admins.py

# 5. Deploy
sudo cp deployment/ssg.service /etc/systemd/system/
sudo cp deployment/nginx.conf /etc/nginx/sites-available/ssg
sudo ln -s /etc/nginx/sites-available/ssg /etc/nginx/sites-enabled/
sudo systemctl enable ssg && sudo systemctl start ssg
sudo nginx -t && sudo systemctl reload nginx

# 6. SSL
sudo certbot --nginx -d snowspoiledgifts.co.za

# 7. Permissions
sudo chown -R www-data:www-data /var/www/ssg
sudo chmod 600 /var/www/ssg/.env
```

---

## 🔑 Critical Configuration

### .env File (MUST CONFIGURE)
```bash
SECRET_KEY=<run: python -c 'import secrets; print(secrets.token_hex(32))'>
MAIL_PASSWORD=<gmail-app-specific-password>
ADMIN_PASSWORD=<secure-admin-password>
BASE_URL=https://snowspoiledgifts.co.za
```

### Gmail App Password Setup
1. Go to: https://myaccount.google.com/apppasswords
2. Generate new app password for "Mail"
3. Copy 16-character password to `.env` as `MAIL_PASSWORD`

---

## 🧪 Post-Deployment Tests

```bash
# Test application
curl http://localhost:8000

# Test HTTPS
curl https://snowspoiledgifts.co.za

# Check logs
sudo journalctl -u ssg -f
```

### Must Test Features:
- [ ] Admin login at `/admin/login`
- [ ] Customer registration
- [ ] Add to cart
- [ ] Complete checkout
- [ ] Verify order confirmation email received
- [ ] Admin can see order in `/admin/orders`
- [ ] Update order status sends email

---

## 📍 Important URLs

| URL | Purpose |
|-----|---------|
| `/` | Homepage (customer view) |
| `/login` | Customer login |
| `/register` | Customer registration |
| `/cart` | Shopping cart |
| `/checkout` | Checkout flow |
| `/account` | User account & order history |
| `/admin/login` | Legacy admin login (quotes system) |
| `/admin/orders` | **NEW:** Admin orders dashboard |
| `/admin/cutters/items` | Manage cookie cutters |
| `/admin/quotes` | View quote requests |
| `/admin/signups` | View email signups |

---

## 👤 Admin Users

**Set as Admin (Phase 4):**
- ✅ mariuserasmus69@gmail.com

**Pending Registration:**
- elmienerasmus@gmail.com (will be admin once registered)
- meganmerasmus@gmail.com (will be admin once registered)

**To Add More Admins Later:**
```bash
cd /var/www/ssg
source venv/bin/activate
python
>>> from src.database import Database
>>> db = Database('database/signups.db')
>>> db.set_user_admin('email@example.com', True)
>>> exit()
```

---

## 🔧 Common Commands

### Application Management
```bash
# Restart app
sudo systemctl restart ssg

# View logs (last 100 lines)
sudo journalctl -u ssg -n 100

# Follow logs in real-time
sudo journalctl -u ssg -f

# Check app status
sudo systemctl status ssg
```

### Update Code
```bash
cd /var/www/ssg
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart ssg
```

### Database Backup
```bash
# Manual backup
cp database/signups.db database/backup_$(date +%Y%m%d).db

# Automated (add to crontab)
crontab -e
# Add: 0 2 * * * cp /var/www/ssg/database/signups.db /var/backups/ssg_$(date +\%Y\%m\%d).db
```

---

## 🚨 Troubleshooting

### App Won't Start
```bash
# Check logs
sudo journalctl -u ssg -n 50

# Test manually
cd /var/www/ssg
source venv/bin/activate
python app.py
```

### Email Not Sending
```bash
# Test SMTP connection
python -c "import smtplib; s=smtplib.SMTP('smtp.gmail.com', 587); s.starttls(); print('SMTP OK')"

# Check .env
cat .env | grep MAIL_
```

### Permission Errors
```bash
# Fix ownership
sudo chown -R www-data:www-data /var/www/ssg

# Fix permissions
sudo chmod -R 755 /var/www/ssg
sudo chmod 600 /var/www/ssg/.env
```

### Database Locked
```bash
# Stop app
sudo systemctl stop ssg

# Check for stale locks
fuser database/signups.db

# Restart app
sudo systemctl start ssg
```

---

## 📊 Monitoring

### Key Metrics to Watch
- Order completion rate
- Email delivery success
- Average page load time
- Error rate in logs

### Log Locations
```bash
# Application
sudo journalctl -u ssg

# Nginx Access
/var/log/nginx/access.log

# Nginx Errors
/var/log/nginx/error.log
```

---

## 🎯 Success Checklist

**Pre-Deployment:**
- [x] Phase 1-4 complete
- [x] Database schema finalized
- [ ] Production `.env` configured
- [ ] SMTP credentials added
- [ ] SSL certificate ready

**Deployment:**
- [ ] Application running on port 8000
- [ ] Nginx proxy configured
- [ ] SSL certificate installed
- [ ] Permissions set correctly
- [ ] Admin users configured

**Post-Deployment:**
- [ ] Customer can register/login
- [ ] Cart and checkout work
- [ ] Order confirmation email sent
- [ ] Admin can view orders
- [ ] Status update emails work
- [ ] All pages load in < 2s

---

## 📞 Emergency Contacts

**Admin Users:**
- Marius: mariuserasmus69@gmail.com

**Technical Issues:**
- Check `DEPLOYMENT_CHECKLIST.md` (detailed guide)
- Check `PHASE4_SUMMARY.md` (feature overview)

---

## 🎉 You're Ready!

Everything is prepared for production deployment. The only remaining task is configuring the production email SMTP credentials.

**Next Step:** Follow `DEPLOYMENT_CHECKLIST.md` for detailed deployment instructions.

**Good luck with the launch! 🚀**

---

*Last Updated: 2025-10-30*
