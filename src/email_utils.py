import smtplib
import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime
from flask import url_for


def get_logo_embedded():
    """Get the SSG logo as base64 for embedding in emails"""
    logo_path = os.path.join('static', 'images', 'logo', 'SSG-Logo.png')
    try:
        if os.path.exists(logo_path):
            with open(logo_path, 'rb') as f:
                logo_data = base64.b64encode(f.read()).decode()
                return f'data:image/png;base64,{logo_data}'
    except Exception as e:
        print(f"Could not load logo: {e}")
    return None


def add_email_logo_header(config):
    """Generate HTML header with logo for emails"""
    logo_base64 = get_logo_embedded()

    if logo_base64:
        return f'''
        <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);">
            <img src="{logo_base64}" alt="{config['SITE_NAME']}" style="width: 60px; height: 60px; margin-bottom: 10px;">
            <h1 style="color: white; margin: 0; font-size: 24px;">{config['SITE_NAME']}</h1>
            <p style="color: #dbeafe; margin: 5px 0 0 0;">{config['TAGLINE']}</p>
        </div>
        '''
    else:
        return f'''
        <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);">
            <h1 style="color: white; margin: 0; font-size: 24px;">{config['SITE_NAME']}</h1>
            <p style="color: #dbeafe; margin: 5px 0 0 0;">{config['TAGLINE']}</p>
        </div>
        '''


def send_quote_notification(config, quote_data):
    """
    Send email notification when a new quote request is received.

    Args:
        config: Flask app config object
        quote_data: Dictionary containing quote request information

    Returns:
        Tuple (success: bool, message: str)
    """
    # Check if email password is configured
    if not config['MAIL_PASSWORD']:
        print("Warning: Email password not configured. Skipping email notification.")
        return False, "Email not configured"

    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"New Quote Request: {quote_data['service_type']} - {quote_data['name']}"
        msg['From'] = config['MAIL_DEFAULT_SENDER']
        msg['To'] = config['NOTIFICATION_RECIPIENTS'][0]  # Primary recipient

        # Add CC if there are additional recipients
        if len(config['NOTIFICATION_RECIPIENTS']) > 1:
            msg['Cc'] = ', '.join(config['NOTIFICATION_RECIPIENTS'][1:])

        # Create HTML email body
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f9fafb; padding: 20px; border: 1px solid #e5e7eb; }}
                .field {{ margin-bottom: 15px; }}
                .label {{ font-weight: bold; color: #2563eb; }}
                .value {{ margin-top: 5px; padding: 10px; background: white; border-left: 3px solid #2563eb; }}
                .footer {{ background: #f3f4f6; padding: 15px; text-align: center; font-size: 12px; color: #6b7280; border-radius: 0 0 8px 8px; }}
                .button {{ display: inline-block; padding: 10px 20px; background: #2563eb; color: white !important; text-decoration: none; border-radius: 5px; margin-top: 15px; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2 style="margin: 0;">New Quote Request Received</h2>
                    <p style="margin: 10px 0 0 0; opacity: 0.9;">Snow Spoiled Gifts - 3D Printing Services</p>
                </div>

                <div class="content">
                    <div class="field">
                        <div class="label">Service Type:</div>
                        <div class="value">{quote_data['service_type']}</div>
                    </div>

                    <div class="field">
                        <div class="label">Customer Name:</div>
                        <div class="value">{quote_data['name']}</div>
                    </div>

                    <div class="field">
                        <div class="label">Email:</div>
                        <div class="value"><a href="mailto:{quote_data['email']}">{quote_data['email']}</a></div>
                    </div>

                    {f'''<div class="field">
                        <div class="label">Phone:</div>
                        <div class="value">{quote_data['phone']} (Preferred: {quote_data['preferred_contact']})</div>
                    </div>''' if quote_data.get('phone') else ''}

                    <div class="field">
                        <div class="label">Description:</div>
                        <div class="value">{quote_data['description']}</div>
                    </div>

                    {f'''<div class="field">
                        <div class="label">Intended Use:</div>
                        <div class="value">{quote_data['intended_use']}</div>
                    </div>''' if quote_data.get('intended_use') else ''}

                    {f'''<div class="field">
                        <div class="label">Size:</div>
                        <div class="value">{quote_data['size']}</div>
                    </div>''' if quote_data.get('size') else ''}

                    <div class="field">
                        <div class="label">Quantity:</div>
                        <div class="value">{quote_data['quantity']}</div>
                    </div>

                    {f'''<div class="field">
                        <div class="label">Color:</div>
                        <div class="value">{quote_data['color']}</div>
                    </div>''' if quote_data.get('color') else ''}

                    {f'''<div class="field">
                        <div class="label">Material:</div>
                        <div class="value">{quote_data['material']}</div>
                    </div>''' if quote_data.get('material') else ''}

                    {f'''<div class="field">
                        <div class="label">Budget Range:</div>
                        <div class="value">{quote_data['budget']}</div>
                    </div>''' if quote_data.get('budget') else ''}

                    {f'''<div class="field">
                        <div class="label">Additional Notes:</div>
                        <div class="value">{quote_data['additional_notes']}</div>
                    </div>''' if quote_data.get('additional_notes') else ''}

                    {f'''<div class="field">
                        <div class="label">Reference Images:</div>
                        <div class="value">{quote_data['reference_images']} file(s) uploaded</div>
                    </div>''' if quote_data.get('reference_images') else ''}

                    <div class="field">
                        <div class="label">Request Date:</div>
                        <div class="value">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
                    </div>

                    <div class="field">
                        <div class="label">Customer IP:</div>
                        <div class="value">{quote_data.get('ip_address', 'N/A')}</div>
                    </div>

                    <div style="text-align: center; margin-top: 20px;">
                        <a href="http://192.168.0.248:5000/admin/quotes" class="button">View in Admin Panel</a>
                    </div>
                </div>

                <div class="footer">
                    <p>This is an automated notification from Snow Spoiled Gifts.</p>
                    <p>Please respond to the customer within 24-48 hours.</p>
                </div>
            </div>
        </body>
        </html>
        """

        # Create plain text version as fallback
        text_body = f"""
New Quote Request Received - Snow Spoiled Gifts

Service Type: {quote_data['service_type']}
Customer: {quote_data['name']}
Email: {quote_data['email']}
Phone: {quote_data.get('phone', 'N/A')} (Preferred: {quote_data.get('preferred_contact', 'Email')})

Description:
{quote_data['description']}

{'Intended Use: ' + quote_data.get('intended_use', '') if quote_data.get('intended_use') else ''}
{'Size: ' + quote_data.get('size', '') if quote_data.get('size') else ''}
Quantity: {quote_data['quantity']}
{'Color: ' + quote_data.get('color', '') if quote_data.get('color') else ''}
{'Material: ' + quote_data.get('material', '') if quote_data.get('material') else ''}
{'Budget: ' + quote_data.get('budget', '') if quote_data.get('budget') else ''}

{'Additional Notes: ' + quote_data.get('additional_notes', '') if quote_data.get('additional_notes') else ''}

Request Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
IP Address: {quote_data.get('ip_address', 'N/A')}

View in Admin Panel: http://192.168.0.248:5000/admin/quotes
        """

        # Attach both HTML and plain text versions
        part1 = MIMEText(text_body, 'plain')
        part2 = MIMEText(html_body, 'html')
        msg.attach(part1)
        msg.attach(part2)

        # Send email using SSL or TLS
        if config.get('MAIL_USE_SSL'):
            # Use SMTP_SSL for port 465
            with smtplib.SMTP_SSL(config['MAIL_SERVER'], config['MAIL_PORT']) as server:
                server.login(config['MAIL_USERNAME'], config['MAIL_PASSWORD'])

                # Send to all recipients
                all_recipients = config['NOTIFICATION_RECIPIENTS']
                server.send_message(msg, to_addrs=all_recipients)
        else:
            # Use SMTP with STARTTLS for port 587
            with smtplib.SMTP(config['MAIL_SERVER'], config['MAIL_PORT']) as server:
                server.starttls()
                server.login(config['MAIL_USERNAME'], config['MAIL_PASSWORD'])

                # Send to all recipients
                all_recipients = config['NOTIFICATION_RECIPIENTS']
                server.send_message(msg, to_addrs=all_recipients)

        return True, "Email notification sent successfully"

    except Exception as e:
        error_msg = f"Failed to send email notification: {str(e)}"
        print(error_msg)
        return False, error_msg


def send_customer_confirmation(config, quote_data):
    """
    Send confirmation email to customer when their quote request is received.

    Args:
        config: Flask app config object
        quote_data: Dictionary containing quote request information

    Returns:
        Tuple (success: bool, message: str)
    """
    # Check if email password is configured
    if not config['MAIL_PASSWORD']:
        print("Warning: Email password not configured. Skipping customer confirmation email.")
        return False, "Email not configured"

    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Quote Request Received - Snow Spoiled Gifts"
        msg['From'] = config['MAIL_DEFAULT_SENDER']
        msg['To'] = quote_data['email']

        # Create HTML email body
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: white; padding: 30px 20px; border-radius: 8px 8px 0 0; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 28px; }}
                .header p {{ margin: 10px 0 0 0; opacity: 0.9; font-size: 16px; }}
                .content {{ background: #ffffff; padding: 30px; border: 1px solid #e5e7eb; }}
                .message-box {{ background: #f0f9ff; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #2563eb; }}
                .field {{ margin-bottom: 15px; }}
                .label {{ font-weight: bold; color: #2563eb; font-size: 14px; }}
                .value {{ margin-top: 5px; padding: 10px; background: #f9fafb; border-left: 3px solid #2563eb; }}
                .footer {{ background: #f3f4f6; padding: 20px; text-align: center; font-size: 13px; color: #6b7280; border-radius: 0 0 8px 8px; }}
                .footer p {{ margin: 5px 0; }}
                .highlight {{ color: #2563eb; font-weight: bold; }}
                .divider {{ height: 1px; background: #e5e7eb; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Thank You!</h1>
                    <p>Your quote request has been received</p>
                </div>

                <div class="content">
                    <p>Hi <strong>{quote_data['name']}</strong>,</p>

                    <div class="message-box">
                        <p style="margin: 0; font-size: 16px;">
                            Thank you for your interest in <strong>Snow Spoiled Gifts</strong>!
                            We've received your quote request for <strong>{quote_data['service_type']}</strong>
                            and we're excited to help bring your project to life.
                        </p>
                    </div>

                    <p>Our team will carefully review your request and get back to you within <span class="highlight">24-48 hours</span> with a detailed quote.</p>

                    <div class="divider"></div>

                    <h3 style="color: #2563eb; margin-bottom: 15px;">Your Request Summary:</h3>

                    <div class="field">
                        <div class="label">Service Type:</div>
                        <div class="value">{quote_data['service_type']}</div>
                    </div>

                    <div class="field">
                        <div class="label">Description:</div>
                        <div class="value">{quote_data['description']}</div>
                    </div>

                    {f'''<div class="field">
                        <div class="label">Intended Use:</div>
                        <div class="value">{quote_data['intended_use']}</div>
                    </div>''' if quote_data.get('intended_use') else ''}

                    {f'''<div class="field">
                        <div class="label">Size:</div>
                        <div class="value">{quote_data['size']}</div>
                    </div>''' if quote_data.get('size') else ''}

                    <div class="field">
                        <div class="label">Quantity:</div>
                        <div class="value">{quote_data['quantity']}</div>
                    </div>

                    {f'''<div class="field">
                        <div class="label">Color Preference:</div>
                        <div class="value">{quote_data['color']}</div>
                    </div>''' if quote_data.get('color') else ''}

                    {f'''<div class="field">
                        <div class="label">Material:</div>
                        <div class="value">{quote_data['material']}</div>
                    </div>''' if quote_data.get('material') else ''}

                    {f'''<div class="field">
                        <div class="label">Budget Range:</div>
                        <div class="value">{quote_data['budget']}</div>
                    </div>''' if quote_data.get('budget') else ''}

                    {f'''<div class="field">
                        <div class="label">Additional Notes:</div>
                        <div class="value">{quote_data['additional_notes']}</div>
                    </div>''' if quote_data.get('additional_notes') else ''}

                    <div class="divider"></div>

                    <p style="font-size: 14px; color: #6b7280;">
                        <strong>What happens next?</strong><br>
                        Our team will review your request and prepare a customized quote based on your specifications.
                        We'll contact you at <strong>{quote_data['email']}</strong>{f" or <strong>{quote_data['phone']}</strong>" if quote_data.get('phone') else ""}
                        with pricing details and any questions we may have.
                    </p>

                    <div class="message-box" style="margin-top: 20px;">
                        <p style="margin: 0;">
                            <strong>Questions in the meantime?</strong><br>
                            Feel free to reply to this email or contact us directly. We're here to help!
                        </p>
                    </div>
                </div>

                <div class="footer">
                    <p><strong>Snow Spoiled Gifts</strong></p>
                    <p>Premium 3D Printing Services</p>
                    <p style="margin-top: 15px;">This is an automated confirmation email. Please do not reply to this message.</p>
                </div>
            </div>
        </body>
        </html>
        """

        # Create plain text version as fallback
        text_body = f"""
Thank You for Your Quote Request!

Hi {quote_data['name']},

Thank you for your interest in Snow Spoiled Gifts! We've received your quote request for {quote_data['service_type']} and we're excited to help bring your project to life.

Our team will carefully review your request and get back to you within 24-48 hours with a detailed quote.

YOUR REQUEST SUMMARY:
-------------------
Service Type: {quote_data['service_type']}
Description: {quote_data['description']}
{f"Intended Use: {quote_data['intended_use']}" if quote_data.get('intended_use') else ''}
{f"Size: {quote_data['size']}" if quote_data.get('size') else ''}
Quantity: {quote_data['quantity']}
{f"Color: {quote_data['color']}" if quote_data.get('color') else ''}
{f"Material: {quote_data['material']}" if quote_data.get('material') else ''}
{f"Budget Range: {quote_data['budget']}" if quote_data.get('budget') else ''}
{f"Additional Notes: {quote_data['additional_notes']}" if quote_data.get('additional_notes') else ''}

WHAT HAPPENS NEXT?
-----------------
Our team will review your request and prepare a customized quote based on your specifications.
We'll contact you at {quote_data['email']}{f" or {quote_data['phone']}" if quote_data.get('phone') else ""} with pricing details and any questions we may have.

Questions in the meantime?
Feel free to reply to this email or contact us directly. We're here to help!

---
Snow Spoiled Gifts
Premium 3D Printing Services

This is an automated confirmation email.
        """

        # Attach both HTML and plain text versions
        part1 = MIMEText(text_body, 'plain')
        part2 = MIMEText(html_body, 'html')
        msg.attach(part1)
        msg.attach(part2)

        # Send email using SSL or TLS
        if config.get('MAIL_USE_SSL'):
            # Use SMTP_SSL for port 465
            with smtplib.SMTP_SSL(config['MAIL_SERVER'], config['MAIL_PORT']) as server:
                server.login(config['MAIL_USERNAME'], config['MAIL_PASSWORD'])
                server.send_message(msg)
        else:
            # Use SMTP with STARTTLS for port 587
            with smtplib.SMTP(config['MAIL_SERVER'], config['MAIL_PORT']) as server:
                server.starttls()
                server.login(config['MAIL_USERNAME'], config['MAIL_PASSWORD'])
                server.send_message(msg)

        return True, "Customer confirmation email sent successfully"

    except Exception as e:
        error_msg = f"Failed to send customer confirmation: {str(e)}"
        print(error_msg)
        return False, error_msg


def send_signup_confirmation(config, signup_data):
    """
    Send confirmation email to customer when they sign up for notifications.

    Args:
        config: Flask app config object
        signup_data: Dictionary containing signup information (name, email, interests, unsubscribe_token)

    Returns:
        Tuple (success: bool, message: str)
    """
    # Check if email password is configured
    if not config['MAIL_PASSWORD']:
        print("Warning: Email password not configured. Skipping signup confirmation email.")
        return False, "Email not configured"

    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Welcome to Snow Spoiled Gifts - You're All Set!"
        msg['From'] = config['MAIL_DEFAULT_SENDER']
        msg['To'] = signup_data['email']

        # Format interests list
        interest_labels = {
            '3d_printing': '3D Printing',
            'sublimation': 'Sublimation',
            'vinyl': 'Vinyl',
            'giftboxes': 'Giftboxes',
            'candles_soaps': 'Candles and Soaps'
        }

        interests_html = ""
        interests_text = ""
        if signup_data.get('interests'):
            interests_list = [interest_labels.get(i, i) for i in signup_data['interests']]
            interests_html = "<ul style='margin: 10px 0; padding-left: 20px;'>" + \
                           "".join([f"<li style='margin: 5px 0;'>{interest}</li>" for interest in interests_list]) + \
                           "</ul>"
            interests_text = "\n".join([f"  - {interest}" for interest in interests_list])
        else:
            interests_html = "<p style='margin: 10px 0; color: #6b7280;'>All product categories</p>"
            interests_text = "  - All product categories"

        # Build unsubscribe URL
        unsubscribe_url = f"{config.get('BASE_URL', 'http://192.168.0.248:5000')}/unsubscribe?token={signup_data['unsubscribe_token']}"

        # Create HTML email body
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: white; padding: 30px 20px; border-radius: 8px 8px 0 0; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 28px; }}
                .header p {{ margin: 10px 0 0 0; opacity: 0.9; font-size: 16px; }}
                .content {{ background: #ffffff; padding: 30px; border: 1px solid #e5e7eb; }}
                .message-box {{ background: #f0f9ff; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #2563eb; }}
                .interests-section {{ background: #f9fafb; padding: 15px; border-radius: 8px; margin: 20px 0; }}
                .footer {{ background: #f3f4f6; padding: 20px; text-align: center; font-size: 13px; color: #6b7280; border-radius: 0 0 8px 8px; }}
                .footer p {{ margin: 5px 0; }}
                .highlight {{ color: #2563eb; font-weight: bold; }}
                .divider {{ height: 1px; background: #e5e7eb; margin: 20px 0; }}
                .unsubscribe {{ margin-top: 15px; padding-top: 15px; border-top: 1px solid #e5e7eb; }}
                .unsubscribe a {{ color: #6b7280; text-decoration: none; font-size: 12px; }}
                .unsubscribe a:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome! 🎉</h1>
                    <p>You're now on our notification list</p>
                </div>

                <div class="content">
                    <p>Hi <strong>{signup_data['name']}</strong>,</p>

                    <div class="message-box">
                        <p style="margin: 0; font-size: 16px;">
                            Thank you for signing up to receive notifications from <strong>Snow Spoiled Gifts</strong>!
                            We're excited to share our major news and updates with you.
                        </p>
                    </div>

                    <p>You'll be among the first to know when we launch new products, special offers, and exciting updates.</p>

                    <div class="divider"></div>

                    <div class="interests-section">
                        <h3 style="color: #2563eb; margin: 0 0 15px 0; font-size: 18px;">Your Interests:</h3>
                        {interests_html}
                        <p style="margin: 15px 0 0 0; font-size: 14px; color: #6b7280;">
                            We'll keep you updated on products and news related to these categories.
                        </p>
                    </div>

                    <div class="message-box" style="margin-top: 20px;">
                        <p style="margin: 0; font-size: 14px;">
                            <strong>Stay tuned!</strong><br>
                            We'll be in touch soon with exciting updates. In the meantime, feel free to explore our website
                            and see what we're all about.
                        </p>
                    </div>

                    <div class="unsubscribe">
                        <p style="margin: 0; font-size: 12px; color: #6b7280;">
                            If you didn't sign up for this or wish to unsubscribe,
                            <a href="{unsubscribe_url}">click here to unsubscribe</a>.
                        </p>
                    </div>
                </div>

                <div class="footer">
                    <p><strong>Snow Spoiled Gifts</strong></p>
                    <p>Premium 3D Printing & Personalized Gifts</p>
                    <p style="margin-top: 15px;">We respect your privacy. Your email will never be shared.</p>
                </div>
            </div>
        </body>
        </html>
        """

        # Create plain text version as fallback
        text_body = f"""
Welcome to Snow Spoiled Gifts!

Hi {signup_data['name']},

Thank you for signing up to receive notifications from Snow Spoiled Gifts! We're excited to share our major news and updates with you.

You'll be among the first to know when we launch new products, special offers, and exciting updates.

YOUR INTERESTS:
--------------
{interests_text}

We'll keep you updated on products and news related to these categories.

STAY TUNED!
We'll be in touch soon with exciting updates. In the meantime, feel free to explore our website and see what we're all about.

---
Snow Spoiled Gifts
Premium 3D Printing & Personalized Gifts

We respect your privacy. Your email will never be shared.

If you didn't sign up for this or wish to unsubscribe, visit:
{unsubscribe_url}
        """

        # Attach both HTML and plain text versions
        part1 = MIMEText(text_body, 'plain')
        part2 = MIMEText(html_body, 'html')
        msg.attach(part1)
        msg.attach(part2)

        # Send email using SSL or TLS
        if config.get('MAIL_USE_SSL'):
            # Use SMTP_SSL for port 465
            with smtplib.SMTP_SSL(config['MAIL_SERVER'], config['MAIL_PORT']) as server:
                server.login(config['MAIL_USERNAME'], config['MAIL_PASSWORD'])
                server.send_message(msg)
        else:
            # Use SMTP with STARTTLS for port 587
            with smtplib.SMTP(config['MAIL_SERVER'], config['MAIL_PORT']) as server:
                server.starttls()
                server.login(config['MAIL_USERNAME'], config['MAIL_PASSWORD'])
                server.send_message(msg)

        return True, "Signup confirmation email sent successfully"

    except Exception as e:
        error_msg = f"Failed to send signup confirmation: {str(e)}"
        print(error_msg)
        return False, error_msg


def send_cake_topper_notification(config, cake_topper_data):
    """
    Send email notification when a new cake topper request is received.

    Args:
        config: Flask app config object
        cake_topper_data: Dictionary containing cake topper request information

    Returns:
        Tuple (success: bool, message: str)
    """
    # Check if email password is configured
    if not config['MAIL_PASSWORD']:
        print("Warning: Email password not configured. Skipping email notification.")
        return False, "Email not configured"

    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"New Cake Topper Request: {cake_topper_data['occasion']} - {cake_topper_data['name']}"
        msg['From'] = config['MAIL_DEFAULT_SENDER']
        msg['To'] = config['NOTIFICATION_RECIPIENTS'][0]  # Primary recipient

        # Add CC if there are additional recipients
        if len(config['NOTIFICATION_RECIPIENTS']) > 1:
            msg['Cc'] = ', '.join(config['NOTIFICATION_RECIPIENTS'][1:])

        # Create HTML email body
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #ec4899 0%, #db2777 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f9fafb; padding: 20px; border: 1px solid #e5e7eb; }}
                .field {{ margin-bottom: 15px; }}
                .label {{ font-weight: bold; color: #ec4899; }}
                .value {{ margin-top: 5px; padding: 10px; background: white; border-left: 3px solid #ec4899; }}
                .footer {{ background: #f3f4f6; padding: 15px; text-align: center; font-size: 12px; color: #6b7280; border-radius: 0 0 8px 8px; }}
                .button {{ display: inline-block; padding: 10px 20px; background: #ec4899; color: white !important; text-decoration: none; border-radius: 5px; margin-top: 15px; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2 style="margin: 0;">🎂 New Cake Topper Request</h2>
                    <p style="margin: 10px 0 0 0; opacity: 0.9;">Snow Spoiled Gifts - 3D Printing Services</p>
                </div>

                <div class="content">
                    <div class="field">
                        <div class="label">Customer Name:</div>
                        <div class="value">{cake_topper_data['name']}</div>
                    </div>

                    <div class="field">
                        <div class="label">Email:</div>
                        <div class="value"><a href="mailto:{cake_topper_data['email']}">{cake_topper_data['email']}</a></div>
                    </div>

                    {f'''<div class="field">
                        <div class="label">Phone:</div>
                        <div class="value">{cake_topper_data['phone']}</div>
                    </div>''' if cake_topper_data.get('phone') else ''}

                    <div class="field">
                        <div class="label">Occasion/Theme:</div>
                        <div class="value">{cake_topper_data['occasion']}</div>
                    </div>

                    {f'''<div class="field">
                        <div class="label">Event Date:</div>
                        <div class="value">{cake_topper_data['event_date']}</div>
                    </div>''' if cake_topper_data.get('event_date') else ''}

                    <div class="field">
                        <div class="label">Text to Include:</div>
                        <div class="value">{cake_topper_data['text_to_include']}</div>
                    </div>

                    <div class="field">
                        <div class="label">Design Details:</div>
                        <div class="value">{cake_topper_data['design_details']}</div>
                    </div>

                    {f'''<div class="field">
                        <div class="label">Size Preference:</div>
                        <div class="value">{cake_topper_data['size_preference']}</div>
                    </div>''' if cake_topper_data.get('size_preference') else ''}

                    {f'''<div class="field">
                        <div class="label">Color Preferences:</div>
                        <div class="value">{cake_topper_data['color_preferences']}</div>
                    </div>''' if cake_topper_data.get('color_preferences') else ''}

                    {f'''<div class="field">
                        <div class="label">Stand Type:</div>
                        <div class="value">{cake_topper_data['stand_type']}</div>
                    </div>''' if cake_topper_data.get('stand_type') else ''}

                    {f'''<div class="field">
                        <div class="label">Reference Images:</div>
                        <div class="value">{cake_topper_data['reference_images']} file(s) uploaded</div>
                    </div>''' if cake_topper_data.get('reference_images') else ''}

                    {f'''<div class="field">
                        <div class="label">Additional Notes:</div>
                        <div class="value">{cake_topper_data['additional_notes']}</div>
                    </div>''' if cake_topper_data.get('additional_notes') else ''}

                    <div class="field">
                        <div class="label">Request Date:</div>
                        <div class="value">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
                    </div>

                    <div class="field">
                        <div class="label">Customer IP:</div>
                        <div class="value">{cake_topper_data.get('ip_address', 'N/A')}</div>
                    </div>

                    <div style="text-align: center; margin-top: 20px;">
                        <a href="http://192.168.0.248:5000/admin/quotes" class="button">View in Admin Panel</a>
                    </div>
                </div>

                <div class="footer">
                    <p>This is an automated notification from Snow Spoiled Gifts.</p>
                    <p>Please respond to the customer within 24-48 hours.</p>
                </div>
            </div>
        </body>
        </html>
        """

        # Create plain text version as fallback
        text_body = f"""
New Cake Topper Request - Snow Spoiled Gifts

Customer: {cake_topper_data['name']}
Email: {cake_topper_data['email']}
Phone: {cake_topper_data.get('phone', 'N/A')}

Occasion: {cake_topper_data['occasion']}
{f"Event Date: {cake_topper_data['event_date']}" if cake_topper_data.get('event_date') else ''}

Text to Include:
{cake_topper_data['text_to_include']}

Design Details:
{cake_topper_data['design_details']}

{f"Size Preference: {cake_topper_data['size_preference']}" if cake_topper_data.get('size_preference') else ''}
{f"Color Preferences: {cake_topper_data['color_preferences']}" if cake_topper_data.get('color_preferences') else ''}
{f"Stand Type: {cake_topper_data['stand_type']}" if cake_topper_data.get('stand_type') else ''}

{f"Additional Notes: {cake_topper_data['additional_notes']}" if cake_topper_data.get('additional_notes') else ''}

Request Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
IP Address: {cake_topper_data.get('ip_address', 'N/A')}

View in Admin Panel: http://192.168.0.248:5000/admin/quotes
        """

        # Attach both HTML and plain text versions
        part1 = MIMEText(text_body, 'plain')
        part2 = MIMEText(html_body, 'html')
        msg.attach(part1)
        msg.attach(part2)

        # Send email using SSL or TLS
        if config.get('MAIL_USE_SSL'):
            # Use SMTP_SSL for port 465
            with smtplib.SMTP_SSL(config['MAIL_SERVER'], config['MAIL_PORT']) as server:
                server.login(config['MAIL_USERNAME'], config['MAIL_PASSWORD'])

                # Send to all recipients
                all_recipients = config['NOTIFICATION_RECIPIENTS']
                server.send_message(msg, to_addrs=all_recipients)
        else:
            # Use SMTP with STARTTLS for port 587
            with smtplib.SMTP(config['MAIL_SERVER'], config['MAIL_PORT']) as server:
                server.starttls()
                server.login(config['MAIL_USERNAME'], config['MAIL_PASSWORD'])

                # Send to all recipients
                all_recipients = config['NOTIFICATION_RECIPIENTS']
                server.send_message(msg, to_addrs=all_recipients)

        return True, "Email notification sent successfully"

    except Exception as e:
        error_msg = f"Failed to send email notification: {str(e)}"
        print(error_msg)
        return False, error_msg


def send_print_service_notification(config, print_service_data):
    """
    Send email notification when a new 3D print service request is received.

    Args:
        config: Flask app config object
        print_service_data: Dictionary containing print service request information

    Returns:
        Tuple (success: bool, message: str)
    """
    # Check if email password is configured
    if not config['MAIL_PASSWORD']:
        print("Warning: Email password not configured. Skipping email notification.")
        return False, "Email not configured"

    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"New 3D Print Service Request - {print_service_data['name']}"
        msg['From'] = config['MAIL_DEFAULT_SENDER']
        msg['To'] = config['NOTIFICATION_RECIPIENTS'][0]  # Primary recipient

        # Add CC if there are additional recipients
        if len(config['NOTIFICATION_RECIPIENTS']) > 1:
            msg['Cc'] = ', '.join(config['NOTIFICATION_RECIPIENTS'][1:])

        # Create HTML email body
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f9fafb; padding: 20px; border: 1px solid #e5e7eb; }}
                .field {{ margin-bottom: 15px; }}
                .label {{ font-weight: bold; color: #10b981; }}
                .value {{ margin-top: 5px; padding: 10px; background: white; border-left: 3px solid #10b981; }}
                .footer {{ background: #f3f4f6; padding: 15px; text-align: center; font-size: 12px; color: #6b7280; border-radius: 0 0 8px 8px; }}
                .button {{ display: inline-block; padding: 10px 20px; background: #10b981; color: white !important; text-decoration: none; border-radius: 5px; margin-top: 15px; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2 style="margin: 0;">📦 New 3D Print Service Request</h2>
                    <p style="margin: 10px 0 0 0; opacity: 0.9;">Snow Spoiled Gifts - Print Service</p>
                </div>

                <div class="content">
                    <div class="field">
                        <div class="label">Customer Name:</div>
                        <div class="value">{print_service_data['name']}</div>
                    </div>

                    <div class="field">
                        <div class="label">Email:</div>
                        <div class="value"><a href="mailto:{print_service_data['email']}">{print_service_data['email']}</a></div>
                    </div>

                    <div class="field">
                        <div class="label">Uploaded Files:</div>
                        <div class="value">{print_service_data['uploaded_files']}</div>
                    </div>

                    <div class="field">
                        <div class="label">Material:</div>
                        <div class="value">{print_service_data['material']}</div>
                    </div>

                    <div class="field">
                        <div class="label">Color:</div>
                        <div class="value">{print_service_data['color']}</div>
                    </div>

                    {f'''<div class="field">
                        <div class="label">Layer Height:</div>
                        <div class="value">{print_service_data['layer_height']}</div>
                    </div>''' if print_service_data.get('layer_height') else ''}

                    {f'''<div class="field">
                        <div class="label">Infill Density:</div>
                        <div class="value">{print_service_data['infill_density']}</div>
                    </div>''' if print_service_data.get('infill_density') else ''}

                    <div class="field">
                        <div class="label">Quantity:</div>
                        <div class="value">{print_service_data['quantity']}</div>
                    </div>

                    {f'''<div class="field">
                        <div class="label">Supports:</div>
                        <div class="value">{print_service_data['supports']}</div>
                    </div>''' if print_service_data.get('supports') else ''}

                    {f'''<div class="field">
                        <div class="label">Special Instructions:</div>
                        <div class="value">{print_service_data['special_instructions']}</div>
                    </div>''' if print_service_data.get('special_instructions') else ''}

                    <div class="field">
                        <div class="label">Request Date:</div>
                        <div class="value">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
                    </div>

                    <div class="field">
                        <div class="label">Customer IP:</div>
                        <div class="value">{print_service_data.get('ip_address', 'N/A')}</div>
                    </div>

                    <div style="text-align: center; margin-top: 20px;">
                        <a href="http://192.168.0.248:5000/admin/quotes" class="button">View in Admin Panel</a>
                    </div>
                </div>

                <div class="footer">
                    <p>This is an automated notification from Snow Spoiled Gifts.</p>
                    <p>Files have been uploaded to: static/uploads/print_files/</p>
                </div>
            </div>
        </body>
        </html>
        """

        # Create plain text version as fallback
        text_body = f"""
New 3D Print Service Request - Snow Spoiled Gifts

Customer: {print_service_data['name']}
Email: {print_service_data['email']}

Uploaded Files: {print_service_data['uploaded_files']}

Print Configuration:
-------------------
Material: {print_service_data['material']}
Color: {print_service_data['color']}
{f"Layer Height: {print_service_data['layer_height']}" if print_service_data.get('layer_height') else ''}
{f"Infill Density: {print_service_data['infill_density']}" if print_service_data.get('infill_density') else ''}
Quantity: {print_service_data['quantity']}
{f"Supports: {print_service_data['supports']}" if print_service_data.get('supports') else ''}

{f"Special Instructions: {print_service_data['special_instructions']}" if print_service_data.get('special_instructions') else ''}

Request Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
IP Address: {print_service_data.get('ip_address', 'N/A')}

Files location: static/uploads/print_files/

View in Admin Panel: http://192.168.0.248:5000/admin/quotes
        """

        # Attach both HTML and plain text versions
        part1 = MIMEText(text_body, 'plain')
        part2 = MIMEText(html_body, 'html')
        msg.attach(part1)
        msg.attach(part2)

        # Send email using SSL or TLS
        if config.get('MAIL_USE_SSL'):
            # Use SMTP_SSL for port 465
            with smtplib.SMTP_SSL(config['MAIL_SERVER'], config['MAIL_PORT']) as server:
                server.login(config['MAIL_USERNAME'], config['MAIL_PASSWORD'])

                # Send to all recipients
                all_recipients = config['NOTIFICATION_RECIPIENTS']
                server.send_message(msg, to_addrs=all_recipients)
        else:
            # Use SMTP with STARTTLS for port 587
            with smtplib.SMTP(config['MAIL_SERVER'], config['MAIL_PORT']) as server:
                server.starttls()
                server.login(config['MAIL_USERNAME'], config['MAIL_PASSWORD'])

                # Send to all recipients
                all_recipients = config['NOTIFICATION_RECIPIENTS']
                server.send_message(msg, to_addrs=all_recipients)

        return True, "Email notification sent successfully"

    except Exception as e:
        error_msg = f"Failed to send email notification: {str(e)}"
        print(error_msg)
        return False, error_msg

def send_admin_reply_to_customer(config, to_email, to_name, subject, message_body, attachments=None):
    """
    Send a reply email from admin to customer.

    Args:
        config: Flask app config object
        to_email: Customer's email address
        to_name: Customer's name
        subject: Email subject line
        message_body: The message content (plain text)
        attachments: Optional list of dictionaries with 'filename', 'data', and 'mime_type' keys

    Returns:
        Tuple (success: bool, message: str)
    """
    # Check if email password is configured
    if not config['MAIL_PASSWORD']:
        print("Warning: Email password not configured. Skipping email.")
        return False, "Email not configured"

    try:
        # Create message - use 'mixed' if we have attachments, otherwise 'alternative'
        if attachments:
            msg = MIMEMultipart('mixed')
        else:
            msg = MIMEMultipart('alternative')

        msg['Subject'] = subject
        msg['From'] = config['MAIL_DEFAULT_SENDER']
        msg['To'] = to_email
        msg['Reply-To'] = config['MAIL_DEFAULT_SENDER']

        # Convert line breaks to HTML
        html_message_body = message_body.replace('\n', '<br>')

        # Create HTML email body
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: white; padding: 30px 20px; border-radius: 8px 8px 0 0; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 24px; }}
                .header p {{ margin: 10px 0 0 0; opacity: 0.9; font-size: 14px; }}
                .content {{ background: #ffffff; padding: 30px; border: 1px solid #e5e7eb; }}
                .message-box {{ background: #f9fafb; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #2563eb; }}
                .footer {{ background: #f3f4f6; padding: 20px; text-align: center; font-size: 13px; color: #6b7280; border-radius: 0 0 8px 8px; }}
                .footer p {{ margin: 5px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Snow Spoiled Gifts</h1>
                    <p>Premium 3D Printing & Personalized Gifts</p>
                </div>

                <div class="content">
                    <p>Hi <strong>{to_name}</strong>,</p>

                    <div class="message-box">
                        {html_message_body}
                    </div>

                    <p style="margin-top: 20px; font-size: 14px; color: #6b7280;">
                        If you have any questions, feel free to reply to this email.
                    </p>
                </div>

                <div class="footer">
                    <p><strong>Snow Spoiled Gifts</strong></p>
                    <p>Premium 3D Printing & Personalized Gifts</p>
                    <p style="margin-top: 15px;">Contact us: {config['MAIL_DEFAULT_SENDER']}</p>
                </div>
            </div>
        </body>
        </html>
        """

        # Create plain text version as fallback
        text_body = f"""
Hi {to_name},

{message_body}

If you have any questions, feel free to reply to this email.

---
Snow Spoiled Gifts
Premium 3D Printing & Personalized Gifts
Contact us: {config['MAIL_DEFAULT_SENDER']}
        """

        # Create alternative container for text/html parts if we have attachments
        if attachments:
            msg_alternative = MIMEMultipart('alternative')
            msg_alternative.attach(MIMEText(text_body, 'plain'))
            msg_alternative.attach(MIMEText(html_body, 'html'))
            msg.attach(msg_alternative)
        else:
            # Attach both HTML and plain text versions directly
            msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))

        # Attach files if provided
        if attachments:
            from email.mime.application import MIMEApplication
            from email.mime.image import MIMEImage

            for attachment in attachments:
                filename = attachment['filename']
                file_data = attachment['data']
                mime_type = attachment['mime_type']

                # Use appropriate MIME type
                if mime_type.startswith('image/'):
                    # For images, use MIMEImage
                    maintype, subtype = mime_type.split('/', 1)
                    file_part = MIMEImage(file_data, _subtype=subtype)
                else:
                    # For other files, use MIMEApplication
                    file_part = MIMEApplication(file_data, _subtype=mime_type.split('/')[-1] if '/' in mime_type else 'octet-stream')

                file_part.add_header('Content-Disposition', 'attachment', filename=filename)
                msg.attach(file_part)

        # Send email using SSL or TLS
        if config.get('MAIL_USE_SSL'):
            # Use SMTP_SSL for port 465
            with smtplib.SMTP_SSL(config['MAIL_SERVER'], config['MAIL_PORT']) as server:
                server.login(config['MAIL_USERNAME'], config['MAIL_PASSWORD'])
                server.send_message(msg)
        else:
            # Use SMTP with STARTTLS for port 587
            with smtplib.SMTP(config['MAIL_SERVER'], config['MAIL_PORT']) as server:
                server.starttls()
                server.login(config['MAIL_USERNAME'], config['MAIL_PASSWORD'])
                server.send_message(msg)

        return True, "Email sent successfully"

    except Exception as e:
        error_msg = f"Failed to send email: {str(e)}"
        print(error_msg)
        return False, error_msg


def send_order_confirmation(config, order_data, customer_email, customer_name):
    """
    Send order confirmation emails to both customer and admin.
    """
    try:
        # Customer Email
        customer_subject = f"Order Confirmation - {order_data['order_number']}"

        shipping_method_text = {
            'pickup': 'Pickup in George - FREE',
            'own_courier': 'Own Courier - FREE',
            'pudo': f"PUDO Delivery - R{order_data.get('shipping_cost', 0):.2f}"
        }.get(order_data.get('shipping_method', 'pickup'), 'Pickup')

        customer_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #28a745 0%, #20883b 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
                .order-number {{ font-size: 24px; font-weight: bold; color: #28a745; margin: 20px 0; }}
                .details {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .detail-row {{ padding: 10px 0; border-bottom: 1px solid #eee; }}
                .detail-label {{ font-weight: bold; display: inline-block; width: 150px; }}
                .total {{ font-size: 20px; font-weight: bold; color: #28a745; text-align: right; padding-top: 20px; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✓ Order Confirmed!</h1>
                    <p>Thank you for your order</p>
                </div>
                <div class="content">
                    <p>Hi {customer_name},</p>
                    <p>Your order has been successfully placed!</p>

                    <div class="order-number">Order Number: {order_data['order_number']}</div>

                    <div class="details">
                        <h3>Order Details</h3>
                        <div class="detail-row">
                            <span class="detail-label">Order Date:</span>
                            {order_data.get('created_date', datetime.now().strftime('%Y-%m-%d %H:%M'))}
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Shipping Method:</span>
                            {shipping_method_text}
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Subtotal:</span>
                            R{order_data['subtotal']:.2f}
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Shipping:</span>
                            R{order_data.get('shipping_cost', 0):.2f}
                        </div>
                        <div class="total">
                            Total: R{order_data['total_amount']:.2f}
                        </div>
                    </div>

                    <h3>What's Next?</h3>
                    <ul>
                        <li>We'll review your order and contact you shortly</li>
                        <li>You'll receive payment details via email</li>
                        <li>Track your order status in "My Account" on our website</li>
                    </ul>

                    <p>If you have any questions, feel free to reply to this email.</p>

                    <p>Thank you for shopping with Snow Spoiled Gifts!</p>
                </div>
                <div class="footer">
                    <p>Snow Spoiled Gifts<br>
                    Email: info@snowspoiledgifts.co.za<br>
                    This is an automated email, please do not reply directly to this message.</p>
                </div>
            </div>
        </body>
        </html>
        """

        customer_text = f"""
ORDER CONFIRMED!

Hi {customer_name},

Your order has been successfully placed!

Order Number: {order_data['order_number']}
Order Date: {order_data.get('created_date', datetime.now().strftime('%Y-%m-%d %H:%M'))}
Shipping Method: {shipping_method_text}

Subtotal: R{order_data['subtotal']:.2f}
Shipping: R{order_data.get('shipping_cost', 0):.2f}
Total: R{order_data['total_amount']:.2f}

What's Next?
- We'll review your order and contact you shortly
- You'll receive payment details via email
- Track your order status in "My Account" on our website

Thank you for shopping with Snow Spoiled Gifts!

---
Snow Spoiled Gifts
Email: info@snowspoiledgifts.co.za
        """

        # Send to customer
        msg_customer = MIMEMultipart('alternative')
        msg_customer['Subject'] = customer_subject
        msg_customer['From'] = config['MAIL_DEFAULT_SENDER']
        msg_customer['To'] = customer_email

        part1 = MIMEText(customer_text, 'plain')
        part2 = MIMEText(customer_html, 'html')
        msg_customer.attach(part1)
        msg_customer.attach(part2)

        # Admin notification email
        admin_subject = f"New Order Received - {order_data['order_number']}"
        admin_body = f"""
New order received!

Order Number: {order_data['order_number']}
Customer: {customer_name} ({customer_email})
Order Date: {order_data.get('created_date', datetime.now().strftime('%Y-%m-%d %H:%M'))}

Shipping Method: {shipping_method_text}
Total Amount: R{order_data['total_amount']:.2f}

Please log in to the admin panel to view full order details.
        """

        msg_admin = MIMEMultipart('alternative')
        msg_admin['Subject'] = admin_subject
        msg_admin['From'] = config['MAIL_DEFAULT_SENDER']
        msg_admin['To'] = config['ADMIN_EMAIL']
        msg_admin.attach(MIMEText(admin_body, 'plain'))

        # Send emails
        if config.get('MAIL_USE_SSL'):
            with smtplib.SMTP_SSL(config['MAIL_SERVER'], config['MAIL_PORT']) as server:
                server.login(config['MAIL_USERNAME'], config['MAIL_PASSWORD'])
                server.send_message(msg_customer)
                server.send_message(msg_admin)
        else:
            with smtplib.SMTP(config['MAIL_SERVER'], config['MAIL_PORT']) as server:
                server.starttls()
                server.login(config['MAIL_USERNAME'], config['MAIL_PASSWORD'])
                server.send_message(msg_customer)
                server.send_message(msg_admin)

        return True, "Order confirmation emails sent successfully"

    except Exception as e:
        error_msg = f"Failed to send order confirmation: {str(e)}"
        print(error_msg)
        return False, error_msg


def send_order_status_update(config, customer_email, order_number, new_status, customer_name):
    """
    Send order status update email to customer.

    Args:
        config: Flask app config object
        customer_email: Customer's email address
        order_number: Order number
        new_status: New order status (pending, confirmed, shipped, delivered)
        customer_name: Customer's name

    Returns:
        Tuple (success: bool, message: str)
    """
    # Check if email password is configured
    if not config['MAIL_PASSWORD']:
        print("Warning: Email password not configured. Skipping status update email.")
        return False, "Email not configured"

    try:
        # Define status-specific messages
        status_info = {
            'pending': {
                'title': 'Order Received',
                'icon': '⏳',
                'color': '#fbbf24',
                'message': 'We have received your order and will begin processing it shortly.'
            },
            'confirmed': {
                'title': 'Order Confirmed',
                'icon': '✓',
                'color': '#3b82f6',
                'message': 'Your order has been confirmed! An invoice has been sent to your email with payment instructions.'
            },
            'awaiting_payment': {
                'title': 'Awaiting Payment',
                'icon': '💳',
                'color': '#f59e0b',
                'message': 'Your order is confirmed and awaiting payment. Please check your invoice for payment instructions.'
            },
            'paid': {
                'title': 'Payment Received',
                'icon': '✅',
                'color': '#10b981',
                'message': 'Thank you! We have received your payment and will start processing your order.'
            },
            'processing': {
                'title': 'Order Processing',
                'icon': '⚙️',
                'color': '#6366f1',
                'message': 'Your order is currently being prepared and will be shipped soon.'
            },
            'shipped': {
                'title': 'Order Shipped',
                'icon': '📦',
                'color': '#0ea5e9',
                'message': 'Great news! Your order has been shipped and is on its way to you.'
            },
            'delivered': {
                'title': 'Order Delivered',
                'icon': '🎉',
                'color': '#8b5cf6',
                'message': 'Your order has been delivered! We hope you love your purchase.'
            },
            'cancelled': {
                'title': 'Order Cancelled',
                'icon': '❌',
                'color': '#ef4444',
                'message': 'Your order has been cancelled. If you have any questions, please contact us.'
            }
        }

        status_data = status_info.get(new_status, status_info['pending'])

        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"{status_data['title']} - Order {order_number}"
        msg['From'] = config['MAIL_DEFAULT_SENDER']
        msg['To'] = customer_email

        # Create HTML email body
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, {status_data['color']} 0%, {status_data['color']}dd 100%);
                          color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
                .header h1 {{ margin: 0; font-size: 28px; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
                .status-badge {{ background: {status_data['color']}; color: white; padding: 10px 20px;
                               border-radius: 20px; display: inline-block; margin: 20px 0; font-weight: bold; }}
                .order-number {{ font-size: 20px; font-weight: bold; color: {status_data['color']}; margin: 20px 0; }}
                .message-box {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0;
                              border-left: 4px solid {status_data['color']}; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{status_data['icon']} {status_data['title']}</h1>
                </div>
                <div class="content">
                    <p>Hi {customer_name},</p>

                    <div class="order-number">Order: {order_number}</div>

                    <div class="status-badge">{new_status.upper()}</div>

                    <div class="message-box">
                        <p>{status_data['message']}</p>
                    </div>

                    <h3>What's Next?</h3>
                    <ul>
                        {'<li>We will contact you with payment details shortly.</li>' if new_status == 'confirmed' else ''}
                        {'<li>You will receive a tracking number once your order is in transit.</li>' if new_status == 'shipped' else ''}
                        {'<li>If you have any questions or concerns, please contact us.</li>' if new_status == 'delivered' else ''}
                        <li>Track your order status anytime in "My Account" on our website.</li>
                    </ul>

                    <p>Thank you for choosing Snow Spoiled Gifts!</p>
                </div>
                <div class="footer">
                    <p>Snow Spoiled Gifts<br>
                    Email: info@snowspoiledgifts.co.za<br>
                    This is an automated notification.</p>
                </div>
            </div>
        </body>
        </html>
        """

        # Create plain text version as fallback
        text_body = f"""
{status_data['title'].upper()}

Hi {customer_name},

Order: {order_number}
Status: {new_status.upper()}

{status_data['message']}

What's Next?
{'- We will contact you with payment details shortly.' if new_status == 'confirmed' else ''}
{'- You will receive a tracking number once your order is in transit.' if new_status == 'shipped' else ''}
{'- If you have any questions or concerns, please contact us.' if new_status == 'delivered' else ''}
- Track your order status anytime in "My Account" on our website.

Thank you for choosing Snow Spoiled Gifts!

---
Snow Spoiled Gifts
Email: info@snowspoiledgifts.co.za
        """

        # Attach both HTML and plain text versions
        part1 = MIMEText(text_body, 'plain')
        part2 = MIMEText(html_body, 'html')
        msg.attach(part1)
        msg.attach(part2)

        # Send email using SSL or TLS
        if config.get('MAIL_USE_SSL'):
            with smtplib.SMTP_SSL(config['MAIL_SERVER'], config['MAIL_PORT']) as server:
                server.login(config['MAIL_USERNAME'], config['MAIL_PASSWORD'])
                server.send_message(msg)
        else:
            with smtplib.SMTP(config['MAIL_SERVER'], config['MAIL_PORT']) as server:
                server.starttls()
                server.login(config['MAIL_USERNAME'], config['MAIL_PASSWORD'])
                server.send_message(msg)

        return True, "Status update email sent successfully"

    except Exception as e:
        error_msg = f"Failed to send status update email: {str(e)}"
        print(error_msg)
        return False, error_msg


def send_quote_converted_notification(config, customer_email, customer_name, item_name, item_price, user_created=False, temp_password=None):
    """
    Send notification email when quote is converted to cart item.
    If user was auto-created, include login credentials.

    Args:
        config: Flask app config object
        customer_email: Customer's email address
        customer_name: Customer's name
        item_name: Name of the item added to cart
        item_price: Price of the item
        user_created: Whether a new user account was created
        temp_password: Temporary password if account was created

    Returns:
        Tuple (success: bool, message: str)
    """
    if not config['MAIL_PASSWORD']:
        print("Warning: Email password not configured. Skipping quote conversion email.")
        return False, "Email not configured"

    try:
        msg = MIMEMultipart('alternative')

        if user_created and temp_password:
            msg['Subject'] = f"Your Quote is Ready + Account Created - {config['SITE_NAME']}"
        else:
            msg['Subject'] = f"Your Quote is Ready for Checkout - {config['SITE_NAME']}"

        msg['From'] = config['MAIL_DEFAULT_SENDER']
        msg['To'] = customer_email

        # Create HTML email body
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                          color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
                .header h1 {{ margin: 0; font-size: 28px; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
                .item-box {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0;
                           border-left: 4px solid #10b981; }}
                .price-tag {{ font-size: 24px; font-weight: bold; color: #10b981; }}
                .credentials-box {{ background: #fef3c7; border: 2px solid #f59e0b; padding: 20px;
                                   border-radius: 8px; margin: 20px 0; }}
                .button {{ background: #10b981; color: white; padding: 15px 30px; text-decoration: none;
                         border-radius: 5px; display: inline-block; margin: 20px 0; font-weight: bold; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                {add_email_logo_header(config)}
                <div class="header" style="margin-top: 0; border-radius: 0;">
                    <h1>🎉 Your Quote is Ready!</h1>
                </div>
                <div class="content">
                    <p>Hi {customer_name},</p>

                    <p>Great news! We've reviewed your quote request and added it to your cart:</p>

                    <div class="item-box">
                        <h3>{item_name}</h3>
                        <div class="price-tag">R{item_price:.2f}</div>
                    </div>

                    {f'''
                    <div class="credentials-box">
                        <h3>⚠️ New Account Created</h3>
                        <p>We've created an account for you to complete your order:</p>
                        <p><strong>Email:</strong> {customer_email}<br>
                        <strong>Temporary Password:</strong> {temp_password}</p>
                        <p style="font-size: 12px; color: #666;">
                            <em>Please change your password after logging in from "My Account".</em>
                        </p>
                    </div>
                    ''' if user_created and temp_password else ''}

                    <p><strong>Next Steps:</strong></p>
                    <ol>
                        <li>{'Log in with your credentials above' if user_created else 'Log in to your account'}</li>
                        <li>Review the item in your cart</li>
                        <li>Choose your shipping method</li>
                        <li>Complete checkout</li>
                    </ol>

                    <center>
                        <a href="{config['SITE_URL']}/cart" class="button">View My Cart</a>
                    </center>

                    <p>If you have any questions about your quote or need adjustments, please reply to this email.</p>

                    <p>Thank you for choosing {config['SITE_NAME']}!</p>
                </div>
                <div class="footer">
                    <p>{config['SITE_NAME']}<br>
                    Email: {config['MAIL_DEFAULT_SENDER']}<br>
                    This is an automated notification.</p>
                </div>
            </div>
        </body>
        </html>
        """

        # Create plain text version
        text_body = f"""
Your Quote is Ready!

Hi {customer_name},

Great news! We've reviewed your quote request and added it to your cart:

Item: {item_name}
Price: R{item_price:.2f}

{"NEW ACCOUNT CREATED" if user_created else ""}
{"Email: " + customer_email if user_created else ""}
{"Temporary Password: " + temp_password if user_created and temp_password else ""}
{"Please change your password after logging in." if user_created else ""}

Next Steps:
1. {"Log in with your credentials above" if user_created else "Log in to your account"}
2. Review the item in your cart
3. Choose your shipping method
4. Complete checkout

Visit: {config['SITE_URL']}/cart

If you have any questions, please reply to this email.

Thank you for choosing {config['SITE_NAME']}!
        """

        msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))

        # Send email
        if config.get('MAIL_USE_SSL'):
            with smtplib.SMTP_SSL(config['MAIL_SERVER'], config['MAIL_PORT']) as server:
                server.login(config['MAIL_USERNAME'], config['MAIL_PASSWORD'])
                server.send_message(msg)
        else:
            with smtplib.SMTP(config['MAIL_SERVER'], config['MAIL_PORT']) as server:
                server.starttls()
                server.login(config['MAIL_USERNAME'], config['MAIL_PASSWORD'])
                server.send_message(msg)

        return True, "Quote conversion email sent successfully"

    except Exception as e:
        error_msg = f"Failed to send quote conversion email: {str(e)}"
        print(error_msg)
        return False, error_msg


def send_invoice_email(config, customer_email, customer_name, order_number, invoice_number, invoice_path):
    """
    Send invoice PDF via email to customer.

    Args:
        config: Flask app config object
        customer_email: Customer's email address
        customer_name: Customer's name
        order_number: Order number
        invoice_number: Invoice number
        invoice_path: Path to the invoice PDF file

    Returns:
        Tuple (success: bool, message: str)
    """
    if not config['MAIL_PASSWORD']:
        print("Warning: Email password not configured. Skipping invoice email.")
        return False, "Email not configured"

    try:
        msg = MIMEMultipart('mixed')
        msg['Subject'] = f"Invoice {invoice_number} - {config['SITE_NAME']}"
        msg['From'] = config['MAIL_DEFAULT_SENDER']
        msg['To'] = customer_email

        # Create HTML email body
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
                          color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
                .header h1 {{ margin: 0; font-size: 28px; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
                .invoice-box {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0;
                              border-left: 4px solid #2563eb; }}
                .button {{ background: #2563eb; color: white; padding: 15px 30px; text-decoration: none;
                         border-radius: 5px; display: inline-block; margin: 20px 0; font-weight: bold; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                {add_email_logo_header(config)}
                <div class="header" style="margin-top: 0; border-radius: 0;">
                    <h1>📄 Your Invoice</h1>
                </div>
                <div class="content">
                    <p>Hi {customer_name},</p>

                    <p>Thank you for your order! Please find your invoice attached to this email.</p>

                    <div class="invoice-box">
                        <h3>Invoice Details</h3>
                        <p><strong>Invoice Number:</strong> {invoice_number}<br>
                        <strong>Order Number:</strong> {order_number}<br>
                        <strong>Date:</strong> {datetime.now().strftime('%d %B %Y')}</p>
                    </div>

                    <p><strong>Payment Instructions:</strong></p>
                    <ul>
                        <li>Please review the attached invoice for the total amount due</li>
                        <li>Payment methods and details are included in the invoice</li>
                        <li>Once payment is received, we will update your order status</li>
                    </ul>

                    <p>If you have any questions about this invoice, please don't hesitate to contact us.</p>

                    <p>Thank you for your business!</p>
                </div>
                <div class="footer">
                    <p>{config['SITE_NAME']}<br>
                    Email: {config['MAIL_DEFAULT_SENDER']}<br>
                    This is an automated notification.</p>
                </div>
            </div>
        </body>
        </html>
        """

        # Create plain text version
        text_body = f"""
Your Invoice - {invoice_number}

Hi {customer_name},

Thank you for your order! Please find your invoice attached to this email.

Invoice Details:
- Invoice Number: {invoice_number}
- Order Number: {order_number}
- Date: {datetime.now().strftime('%d %B %Y')}

Payment Instructions:
- Please review the attached invoice for the total amount due
- Payment methods and details are included in the invoice
- Once payment is received, we will update your order status

If you have any questions about this invoice, please contact us.

Thank you for your business!

{config['SITE_NAME']}
{config['MAIL_DEFAULT_SENDER']}
        """

        # Attach text and HTML parts
        msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))

        # Attach PDF invoice
        if os.path.exists(invoice_path):
            with open(invoice_path, 'rb') as f:
                from email.mime.application import MIMEApplication
                pdf_attachment = MIMEApplication(f.read(), _subtype='pdf')
                pdf_attachment.add_header('Content-Disposition', 'attachment', filename=f'{invoice_number}.pdf')
                msg.attach(pdf_attachment)
        else:
            return False, "Invoice PDF file not found"

        # Send email
        if config.get('MAIL_USE_SSL'):
            with smtplib.SMTP_SSL(config['MAIL_SERVER'], config['MAIL_PORT']) as server:
                server.login(config['MAIL_USERNAME'], config['MAIL_PASSWORD'])
                server.send_message(msg)
        else:
            with smtplib.SMTP(config['MAIL_SERVER'], config['MAIL_PORT']) as server:
                server.starttls()
                server.login(config['MAIL_USERNAME'], config['MAIL_PASSWORD'])
                server.send_message(msg)

        return True, "Invoice email sent successfully"

    except Exception as e:
        error_msg = f"Failed to send invoice email: {str(e)}"
        print(error_msg)
        return False, error_msg
