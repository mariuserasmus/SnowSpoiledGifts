# Snow's Spoiled Gifts - Coming Soon Website

Phase 0 "Coming Soon" website for www.snowspoiledgifts.co.za

## Features

- ✨ Beautiful, mobile-responsive landing page
- 📧 Email signup with interest tracking
- 🎨 Fun but professional design
- 👨‍💼 Admin panel for managing signups
- 📊 CSV export of email list
- 🔒 Secure admin authentication

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
