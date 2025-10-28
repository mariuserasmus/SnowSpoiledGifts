# Snow's Spoiled Gifts - E-Commerce Website

Full-featured Flask e-commerce website for www.snowspoiledgifts.co.za

## Features

### Customer-Facing
- ✨ Beautiful, mobile-responsive design with dark mode
- 🛍️ 3D Printing services showcase (Custom Design, Cookie/Clay Cutters, Cake Toppers, Print Service)
- 🎨 Product catalog with filters, search, and sorting
- 📸 Multi-image product galleries with carousels
- 📝 Quote request forms with file uploads
- 📧 Email signup with interest tracking

### Admin Panel
- 👨‍💼 Comprehensive admin dashboard
- 📦 Cookie & Clay Cutters management (Categories, Types, Items, Photos)
- 📊 Quote request management (Custom Design, Cake Topper, Print Service)
- 📧 Email notification system with multiple recipients
- ✉️ Email customer directly from admin panel (with branded templates)
- 🔒 Secure admin authentication
- 📊 CSV export of signups and quotes
- 🎨 Consistent UI styling (light & dark mode)

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
copy .env.example .env

# Edit .env and update:
# - SECRET_KEY (use a random string)
# - ADMIN_USERNAME
# - ADMIN_PASSWORD
# - Contact information in config.py
```

### 3. Run the Application

```bash
python app.py
```

Visit: http://localhost:5000

---

## 📚 Documentation

### Project Documentation
- **[progress.md](progress.md)** - Complete development history and current status
- **[CHECKPOINT_NEXT_PHASE.md](CHECKPOINT_NEXT_PHASE.md)** - Roadmap for future features (Shopping Cart, Auth, Checkout)

### Deployment
- **[deployment/](deployment/)** - All deployment guides for Afrihost hosting
  - [AFRIHOST_PASSENGER_SETUP.md](deployment/AFRIHOST_PASSENGER_SETUP.md) - Complete deployment guide
  - [FIX_PRODUCTION_EMAIL.md](deployment/FIX_PRODUCTION_EMAIL.md) - Fix email issues
  - [DEPLOYMENT_QUICK_START.md](deployment/DEPLOYMENT_QUICK_START.md) - Quick reference
  - [PRODUCTION_ENV_TEMPLATE.md](deployment/PRODUCTION_ENV_TEMPLATE.md) - Environment configuration

### System Documentation
- **[docs/](docs/)** - Technical documentation
  - [CHECKPOINT_COOKIE_CUTTERS_ADMIN.md](docs/CHECKPOINT_COOKIE_CUTTERS_ADMIN.md) - Cookie & Clay Cutters system
  - [EMAIL_SETUP.md](docs/EMAIL_SETUP.md) - Email configuration guide
  - [NETWORK_TROUBLESHOOTING.md](docs/NETWORK_TROUBLESHOOTING.md) - Network access issues

### Archive
- **[archive/](archive/)** - Historical documentation (older/superseded guides)

---

## 🎯 Current Status

**Production:** ✅ Deployed to www.snowspoiledgifts.co.za

**Completed Features:**
- ✅ Customer landing page with dark mode
- ✅ 3D Printing services showcase
- ✅ Cookie & Clay Cutters shop (admin + frontend)
- ✅ Quote request system (3 types)
- ✅ Email notifications (Afrihost SMTP)
- ✅ Admin panel (signups, quotes, products)
- ✅ Admin email customer functionality (Oct 2025)
- ✅ Consistent UI styling across admin pages (Oct 2025)
- ✅ Version tracking system (Oct 2025)

**Next Phase:**
- 🛒 Shopping Cart (see CHECKPOINT_NEXT_PHASE.md)
- 👤 User Authentication
- 💳 Checkout & Payment
- 📦 Order Management

---

## 🚀 Deployment Workflow

### Production Deployment (Afrihost cPanel)

**Step 1: Commit and Push to GitHub**
```bash
git add .
git commit -m "Your commit message"
git push origin main
```

**Step 2: Deploy via cPanel**
1. Log into cPanel → Git Version Control
2. Click **"Update From Remote"** (pulls from GitHub)
3. Click **"Deploy HEAD Commit"** (copies to app & restarts)
4. Wait 1-2 minutes for deployment to complete

**Step 3: Verify Deployment**
- Visit: https://snowspoiledgifts.co.za/version-check
- Check the version info matches your latest commit
- Hard refresh your browser (Ctrl+Shift+R) to see changes

**Important Paths:**
- Repository: `/home/snowsxtp/repositories/ssg` (where Git pulls code)
- Application: `/home/snowsxtp/ssg` (where the live site runs)

**See also:** [deployment/DEPLOYMENT_QUICK_START.md](deployment/DEPLOYMENT_QUICK_START.md)

---

## 🛠️ Tech Stack

- **Backend:** Flask (Python)
- **Database:** SQLite
- **Frontend:** Bootstrap 5, JavaScript
- **Email:** SMTP (Afrihost mail server)
- **Hosting:** Afrihost (Passenger WSGI)

---

## 📞 Contact

For questions about this codebase, see documentation in `docs/` folder or review `progress.md` for development history.

Visit: http://localhost:5000

### 4. Admin Access

Visit: http://localhost:5000/admin/login

Default credentials (change in .env):
- Username: admin
- Password: changeme123

## Customization

### Update Your Information

Edit `config.py` to update:
- Site name and tagline
- Contact email and phone
- Social media links
- Launch date

### Add Your Images

Place your images in these folders:

- **Logo**: `static/images/logo/logo-main.png` (transparent PNG, ~1000px wide)
- **Favicon**: `static/images/logo/favicon.ico`
- **Hero Banner**: `static/images/hero/hero-banner.jpg` (1920x600px)
- **Category Images**: `static/images/categories/`
  - 3d-printing.jpg
  - sublimation.jpg
  - vinyl.jpg
  - giftboxes.jpg
- **Gallery**: `static/images/gallery/preview-1.jpg` through `preview-6.jpg`

### Update Text Content

Edit `templates/index.html` to change:
- Hero headline and description
- Category descriptions
- About Us text
- Contact information

## Deployment to Afrihost

See `docs/Deployment_Guide.md` for detailed deployment instructions.

### Quick Deployment Checklist

- [ ] Update all content in `config.py`
- [ ] Add your logo and images
- [ ] Update text in `templates/index.html`
- [ ] Set strong SECRET_KEY in `.env`
- [ ] Set strong admin password in `.env`
- [ ] Test locally
- [ ] Upload to Afrihost
- [ ] Configure domain settings
- [ ] Test live site

## Project Structure

```
SSG/
├── app.py                    # Main Flask application
├── config.py                 # Configuration settings
├── database.py               # Database operations
├── forms.py                  # Form definitions
├── requirements.txt          # Python dependencies
├── static/                   # Static files
│   ├── css/
│   ├── js/
│   └── images/
├── templates/                # HTML templates
├── database/                 # SQLite database (auto-created)
└── docs/                     # Documentation
```

## Features Walkthrough

### Email Signup
- Users can sign up with name and email
- Optional: Select product interests
- Duplicate email prevention
- Success/error flash messages
- Redirect to thank you page

### Admin Panel
- View all signups
- See total signup count
- Export to CSV
- Basic analytics

### Responsive Design
- Mobile-first approach
- Works on all devices
- Optimized images
- Smooth animations

## Troubleshooting

### Database Issues
If database errors occur:
```bash
# Delete and recreate database
rm database/signups.db
# Restart the app (database will auto-create)
python app.py
```

### Port Already in Use
Change port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Images Not Loading
- Check image paths in static/images/
- Ensure images are named correctly
- Placeholder images will show if files missing

## Security Notes

- Change default admin credentials before deployment
- Use strong SECRET_KEY in production
- Consider using environment variables for sensitive data
- Enable HTTPS on production (Afrihost usually provides this)

## Current Status - Phase 0.5 (In Progress)

### ✅ Completed
- Phase 0: Coming Soon landing page with email signups
- 3D Printing category page with 4 service types
- Product image gallery modal with carousel
- Quote request forms (custom design, cake toppers, 3D print service)
- Cookie/Clay cutters shop with filters and search
- Admin panel for managing signups

### 🚧 In Progress
- Applying product modals to remaining shop items
- Backend form processing for quote requests

## Next Steps (Phase 1)

After Phase 0.5 is complete:
1. Complete all category pages (Sublimation, Vinyl, Gift Boxes)
2. Implement shopping cart and checkout
3. Payment gateway integration
4. Order management system
5. Email notifications

## Support

For issues or questions:
- Check documentation in `docs/` folder
- Review Flask documentation: https://flask.palletsprojects.com/
- Review Bootstrap documentation: https://getbootstrap.com/

## License

© 2025 Snow's Spoiled Gifts. All rights reserved.
