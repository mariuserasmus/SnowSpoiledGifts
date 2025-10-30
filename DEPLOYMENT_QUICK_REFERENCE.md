# 🚀 Deployment Quick Reference Card

**Phase 4 - Admin Order Management**
**Status:** Ready for Production ✅

---

## 🎯 What Changed

### New Features
- ✅ Admin user roles (`is_admin` column)
- ✅ Admin-specific navbar (Orders, Items, Quotes, Signups)
- ✅ Orders dashboard with status filtering
- ✅ Order detail view and status management
- ✅ Email notifications for status updates

### Database Changes
- **Automatic migration:** `users` table gets `is_admin` column
- **No manual SQL needed** - runs on first startup
- **Backward compatible** - existing data unaffected

---

## ⚠️ CRITICAL: Before Deploying

### 1. Backup Live Database
```bash
cp database/signups.db database/signups.db.backup_$(date +%Y%m%d_%H%M%S)
```

### 2. Verify Production .env Has:
```env
MAIL_SERVER=<your-live-smtp-server>
MAIL_PORT=<your-live-smtp-port>
MAIL_USE_TLS=True  # or False, match your setup
MAIL_USERNAME=<your-live-email-username>
MAIL_PASSWORD=<your-live-email-password>
MAIL_DEFAULT_SENDER=info@snowspoiledgifts.co.za
ADMIN_EMAIL=info@snowspoiledgifts.co.za
SECRET_KEY=<random-32-character-string>
```

### 3. Test in DEV First
```bash
cd c:\Claude\SSG
python app.py
# Login as mariuserasmus69@gmail.com
# Test Orders dashboard, status updates, emails
```

---

## 🚀 Deploy Steps

### Quick Version (5 minutes)
```bash
# 1. Backup
cd /var/www/ssg
cp database/signups.db database/signups.db.backup_$(date +%Y%m%d_%H%M%S)

# 2. Update code
git pull origin main

# 3. Restart
sudo systemctl restart ssg

# 4. Check logs
sudo journalctl -u ssg -f
```

### Verify Working
- [ ] Site loads: https://snowspoiledgifts.co.za
- [ ] Login as admin: mariuserasmus69@gmail.com
- [ ] See admin navbar (Orders | Manage Items | etc.)
- [ ] Access `/admin/orders`
- [ ] Update an order status → email sent

---

## 🚨 If Anything Breaks

### Quick Rollback (2 minutes)
```bash
sudo systemctl stop ssg
git reset --hard HEAD~1
cp database/signups.db.backup_YYYYMMDD_HHMMSS database/signups.db
sudo systemctl start ssg
```

### Common Issues

**500 Error:**
```bash
sudo journalctl -u ssg -n 50
# Check for missing modules, syntax errors
```

**Email Not Sending:**
```bash
cat .env | grep MAIL_
# Verify matches live SMTP settings
```

**Admin Features Not Showing:**
```bash
python set_admins.py
# Re-run admin setup script
```

---

## 📍 Important URLs

| URL | Purpose |
|-----|---------|
| `/admin/orders` | **NEW:** Admin orders dashboard |
| `/admin/orders/<number>` | **NEW:** Order detail view |
| `/admin/cutters/items` | Manage cookie cutters |
| `/admin/quotes` | View quote requests |
| `/login` | User/admin login |

---

## 👤 Admin Users

**Currently Set:**
- ✅ mariuserasmus69@gmail.com

**Add More Admins:**
```bash
cd /var/www/ssg
source venv/bin/activate
python set_admins.py
# Or manually:
# python
# >>> from src.database import Database
# >>> db = Database('database/signups.db')
# >>> db.set_user_admin('email@example.com', True)
```

---

## ✅ Post-Deployment Checklist

**Within 5 minutes:**
- [ ] Site loads normally
- [ ] Can browse products
- [ ] Cart works
- [ ] Login works

**Within 15 minutes:**
- [ ] Admin login works
- [ ] Orders dashboard loads
- [ ] Can view order details
- [ ] Can update order status

**Within 30 minutes:**
- [ ] Place test order
- [ ] Verify confirmation email
- [ ] Update order status
- [ ] Verify status email

**Monitor logs:**
```bash
sudo journalctl -u ssg --since "1 hour ago" | grep -i error
```

---

## 📞 Emergency Contacts

**Admin Users:**
- Marius: mariuserasmus69@gmail.com

**Documentation:**
- `PRE_DEPLOYMENT_SAFETY_CHECK.md` - Detailed safety guide
- `EMAIL_SETUP_GUIDE.md` - Email configuration help
- `DEPLOYMENT_CHECKLIST.md` - Full deployment guide

---

## 💡 Key Reminders

1. **Email config is critical** - must match live SMTP exactly
2. **Test in DEV first** - catch issues before production
3. **Backup database** - always have a rollback plan
4. **Monitor logs** - watch for errors after deployment
5. **Off-hours deployment** - less risky during low traffic

---

## 🎉 Success Criteria

✅ Deployment successful when:
- Site loads normally
- Existing features work
- Admin can access orders
- Email notifications send
- No errors in logs

---

**Ready to deploy? Follow PRE_DEPLOYMENT_SAFETY_CHECK.md for detailed steps.**

**Good luck! 🚀**

---

*Version 1.4.0 - Phase 4: Admin Order Management*
*Last Updated: 2025-10-30*
