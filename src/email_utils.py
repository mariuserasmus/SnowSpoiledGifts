import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from flask import url_for


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

        # Send email
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

        # Send email
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

        # Send email
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

        # Send email
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

        # Send email
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
