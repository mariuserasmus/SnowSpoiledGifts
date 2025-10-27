# Email Notification Setup Guide

## Overview
The quote request system is now configured to send email notifications to:
- **Primary:** elmienerasmus@gmail.com
- **CC:** mariuserasmus69@gmail.com

## Gmail App Password Setup

To enable email notifications, you need to set up a Gmail App Password. Here's how:

### Step 1: Enable 2-Factor Authentication
1. Go to your Google Account: https://myaccount.google.com/
2. Click on **Security** in the left sidebar
3. Under "Signing in to Google," select **2-Step Verification**
4. Follow the steps to enable 2FA if not already enabled

### Step 2: Generate an App Password
1. Go to: https://myaccount.google.com/apppasswords
2. You may need to sign in again
3. In the "Select app" dropdown, choose **Mail**
4. In the "Select device" dropdown, choose **Other (Custom name)**
5. Enter a name like "Snow Spoiled Gifts Website"
6. Click **Generate**
7. Google will display a 16-character password (like: `abcd efgh ijkl mnop`)
8. **Copy this password** (you won't be able to see it again)

### Step 3: Add Password to .env File
1. Open the `.env` file in the project root
2. Find the line that says `MAIL_PASSWORD=`
3. Paste your App Password after the equals sign (remove spaces)
4. Example: `MAIL_PASSWORD=abcdefghijklmnop`
5. Save the file

### Step 4: Restart the Application
1. Stop the Flask server (Ctrl+C in the terminal)
2. Start it again: `python app.py`

## Testing Email Notifications

1. Go to: http://192.168.0.248:5000/3d-printing
2. Click on "Custom Design"
3. Scroll down to "Request Custom Design Quote"
4. Fill out the form and submit
5. Check both email addresses (elmienerasmus@gmail.com and mariuserasmus69@gmail.com)
6. You should receive a nicely formatted email with all the quote details

## Troubleshooting

### Email not sending?
- Check that `MAIL_PASSWORD` is set correctly in `.env`
- Make sure 2FA is enabled on the Gmail account
- Check the terminal/console for error messages
- Verify the App Password was copied without spaces

### Wrong email addresses?
Edit `config.py` and change the `NOTIFICATION_RECIPIENTS` list:
```python
NOTIFICATION_RECIPIENTS = ['elmienerasmus@gmail.com', 'mariuserasmus69@gmail.com']
```

## Email Features

The notification emails include:
- ✅ Customer name and contact information
- ✅ Full description of the request
- ✅ All form fields (size, quantity, color, material, budget)
- ✅ Additional notes
- ✅ Information about uploaded reference images
- ✅ Timestamp and IP address
- ✅ Direct link to view in admin panel
- ✅ Professional HTML formatting with Snow Spoiled Gifts branding

## Network Access

Your website is accessible from any device on your local network at:
- **URL:** http://192.168.0.248:5000
- This works on phones, tablets, and other computers on the same WiFi

To access from the internet (future), you'll need to:
1. Set up port forwarding on your router
2. Get a dynamic DNS service (like No-IP or DynDNS)
3. Or deploy to a cloud hosting service
