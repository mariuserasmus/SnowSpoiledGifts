"""
WhatsApp Business API Utilities
Send messages via WhatsApp Cloud API
"""

import requests
import logging
from typing import Tuple, Optional

# Set up logging
logger = logging.getLogger(__name__)

def send_whatsapp_message(
    to: str,
    message: str,
    config: dict
) -> Tuple[bool, str]:
    """
    Send a text message via WhatsApp Business API

    Args:
        to: Recipient phone number (no + sign, with country code)
        message: Message text to send
        config: Flask config object with WhatsApp credentials

    Returns:
        (success: bool, message: str)
    """
    # Check if WhatsApp is enabled
    if not config.get('WHATSAPP_ENABLED'):
        return False, "WhatsApp is not configured"

    phone_number_id = config['WHATSAPP_PHONE_NUMBER_ID']
    access_token = config['WHATSAPP_ACCESS_TOKEN']

    # API endpoint
    url = f"https://graph.facebook.com/v22.0/{phone_number_id}/messages"

    # Headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Message payload - text message
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {
            "body": message
        }
    }

    try:
        print(f"\n=== WhatsApp Send Attempt ===")
        print(f"To: {to}")
        print(f"Message: {message[:50]}...")
        print(f"Sending to API: {url}")

        response = requests.post(url, headers=headers, json=payload, timeout=10)

        # Log full response for debugging
        print(f"API Response Status: {response.status_code}")
        print(f"API Response Body: {response.text}")
        logger.info(f"WhatsApp API Response ({response.status_code}): {response.text}")

        if response.status_code == 200:
            result = response.json()
            message_id = result.get('messages', [{}])[0].get('id', 'unknown')
            print(f"✅ SUCCESS! Message ID: {message_id}")
            logger.info(f"WhatsApp sent to {to}: {message_id}")

            # Check for warnings (test number limitations)
            if 'error' in result:
                warning = result['error'].get('message', '')
                print(f"⚠️ Warning: {warning}")
                logger.warning(f"WhatsApp warning: {warning}")

            print(f"=== End WhatsApp Request ===\n")
            return True, f"Message sent successfully (ID: {message_id})"
        else:
            error_data = response.json()
            error_msg = error_data.get('error', {}).get('message', 'Unknown error')
            print(f"❌ ERROR: {error_msg}")
            logger.error(f"WhatsApp API error: {error_msg}")
            print(f"=== End WhatsApp Request ===\n")
            return False, f"API Error: {error_msg}"

    except requests.exceptions.Timeout:
        print(f"❌ TIMEOUT!")
        logger.error("WhatsApp API timeout")
        return False, "Request timeout - please try again"
    except requests.exceptions.RequestException as e:
        print(f"❌ REQUEST ERROR: {e}")
        logger.error(f"WhatsApp request failed: {e}")
        return False, f"Connection error: {str(e)}"
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        logger.error(f"Unexpected error sending WhatsApp: {e}")
        return False, f"Unexpected error: {str(e)}"


def send_template_message(
    to: str,
    template_name: str,
    config: dict,
    language_code: str = "en_US"
) -> Tuple[bool, str]:
    """
    Send a template message via WhatsApp Business API

    Args:
        to: Recipient phone number (no + sign, with country code)
        template_name: Name of approved template (e.g., "hello_world")
        config: Flask config object
        language_code: Template language code (default: en_US)

    Returns:
        (success: bool, message: str)
    """
    # Check if WhatsApp is enabled
    if not config.get('WHATSAPP_ENABLED'):
        return False, "WhatsApp is not configured"

    phone_number_id = config['WHATSAPP_PHONE_NUMBER_ID']
    access_token = config['WHATSAPP_ACCESS_TOKEN']

    # API endpoint
    url = f"https://graph.facebook.com/v22.0/{phone_number_id}/messages"

    # Headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Template message payload
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {
                "code": language_code
            }
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)

        if response.status_code == 200:
            result = response.json()
            message_id = result.get('messages', [{}])[0].get('id', 'unknown')
            logger.info(f"WhatsApp template '{template_name}' sent to {to}: {message_id}")
            return True, f"Template sent successfully (ID: {message_id})"
        else:
            error_data = response.json()
            error_msg = error_data.get('error', {}).get('message', 'Unknown error')
            logger.error(f"WhatsApp API error: {error_msg}")
            return False, f"API Error: {error_msg}"

    except Exception as e:
        logger.error(f"Error sending WhatsApp template: {e}")
        return False, f"Error: {str(e)}"


def format_phone_number(phone: str) -> Optional[str]:
    """
    Format phone number for WhatsApp API (remove + and spaces)

    Handles South African numbers starting with 0 (converts to 27)

    Args:
        phone: Phone number (various formats)

    Returns:
        Formatted number or None if invalid
    """
    if not phone:
        return None

    # Remove common separators
    cleaned = phone.replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')

    # Check if it's all digits
    if not cleaned.isdigit():
        return None

    # Handle South African numbers starting with 0 (e.g., 0825522848)
    if cleaned.startswith('0') and len(cleaned) == 10:
        # Replace leading 0 with country code 27
        cleaned = '27' + cleaned[1:]

    # Validate minimum length
    if len(cleaned) >= 10:
        return cleaned

    return None


def send_quote_notification(
    customer_name: str,
    customer_phone: str,
    quote_message: str,
    config: dict
) -> Tuple[bool, str]:
    """
    Send quote notification to customer via WhatsApp

    Args:
        customer_name: Customer's name
        customer_phone: Customer's phone number
        quote_message: The quote/message text
        config: Flask config object

    Returns:
        (success: bool, message: str)
    """
    # Format phone number
    formatted_phone = format_phone_number(customer_phone)
    if not formatted_phone:
        return False, "Invalid phone number format"

    # Create message
    message = f"Hello {customer_name}!\n\n{quote_message}\n\n- Snow Spoiled Gifts Team"

    # Send message
    return send_whatsapp_message(formatted_phone, message, config)


def send_quote_ready_template(
    to: str,
    customer_name: str,
    quote_type: str,
    amount: str,
    quote_url: str,
    config: dict
) -> Tuple[bool, str]:
    """
    Send Quote Ready Notification template

    Template: quote_ready_notification
    Variables: {{1}} Name, {{2}} Quote Type, {{3}} Amount
    Buttons: View Quote (URL), Call Us (Phone)

    Args:
        to: Recipient phone number
        customer_name: Customer's name
        quote_type: Type of quote (e.g., "Custom Cake", "3D Printing")
        amount: Quote amount (e.g., "R450.00")
        quote_url: Full URL to view quote
        config: Flask config object

    Returns:
        (success: bool, message: str)
    """
    if not config.get('WHATSAPP_ENABLED'):
        return False, "WhatsApp is not configured"

    phone_number_id = config['WHATSAPP_PHONE_NUMBER_ID']
    access_token = config['WHATSAPP_ACCESS_TOKEN']

    url = f"https://graph.facebook.com/v22.0/{phone_number_id}/messages"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": "quote_ready_notification",
            "language": {
                "code": "en"
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": customer_name},
                        {"type": "text", "text": quote_type},
                        {"type": "text", "text": amount}
                    ]
                }
            ]
        }
    }

    try:
        logger.info(f"Sending quote_ready_notification to {to}")
        response = requests.post(url, headers=headers, json=payload, timeout=10)

        if response.status_code == 200:
            result = response.json()
            message_id = result.get('messages', [{}])[0].get('id', 'unknown')
            logger.info(f"Quote ready template sent to {to}: {message_id}")
            return True, f"Quote notification sent (ID: {message_id})"
        else:
            error_data = response.json()
            error_msg = error_data.get('error', {}).get('message', 'Unknown error')
            logger.error(f"WhatsApp API error: {error_msg}")
            return False, f"API Error: {error_msg}"

    except Exception as e:
        logger.error(f"Error sending quote ready template: {e}")
        return False, f"Error: {str(e)}"


def send_payment_reminder_template(
    to: str,
    customer_name: str,
    order_number: str,
    amount: str,
    order_url: str,
    config: dict
) -> Tuple[bool, str]:
    """
    Send Payment Reminder template

    Template: payment_reminder
    Variables: {{1}} Name, {{2}} Order Number, {{3}} Amount
    Buttons: View Order (URL), Quick Replies (Resend Bank Details, Already Paid)

    Args:
        to: Recipient phone number
        customer_name: Customer's name
        order_number: Order number
        amount: Outstanding amount
        order_url: Full URL to view order
        config: Flask config object

    Returns:
        (success: bool, message: str)
    """
    if not config.get('WHATSAPP_ENABLED'):
        return False, "WhatsApp is not configured"

    phone_number_id = config['WHATSAPP_PHONE_NUMBER_ID']
    access_token = config['WHATSAPP_ACCESS_TOKEN']

    url = f"https://graph.facebook.com/v22.0/{phone_number_id}/messages"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": "payment_reminder",
            "language": {
                "code": "en"
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": customer_name},
                        {"type": "text", "text": order_number},
                        {"type": "text", "text": amount}
                    ]
                }
            ]
        }
    }

    try:
        logger.info(f"Sending payment_reminder to {to}")
        response = requests.post(url, headers=headers, json=payload, timeout=10)

        if response.status_code == 200:
            result = response.json()
            message_id = result.get('messages', [{}])[0].get('id', 'unknown')
            logger.info(f"Payment reminder sent to {to}: {message_id}")
            return True, f"Payment reminder sent (ID: {message_id})"
        else:
            error_data = response.json()
            error_msg = error_data.get('error', {}).get('message', 'Unknown error')
            logger.error(f"WhatsApp API error: {error_msg}")
            return False, f"API Error: {error_msg}"

    except Exception as e:
        logger.error(f"Error sending payment reminder: {e}")
        return False, f"Error: {str(e)}"


def send_order_status_update_template(
    to: str,
    customer_name: str,
    order_number: str,
    status: str,
    details: str,
    order_url: str,
    config: dict
) -> Tuple[bool, str]:
    """
    Send Order Status Update template

    Template: order_status_update
    Variables: {{1}} Name, {{2}} Order Number, {{3}} Status, {{4}} Details
    Buttons: Track Order (URL), Need Help (Phone)

    Args:
        to: Recipient phone number
        customer_name: Customer's name
        order_number: Order number
        status: New status (e.g., "Processing", "Ready")
        details: Additional details about the status
        order_url: Full URL to view order
        config: Flask config object

    Returns:
        (success: bool, message: str)
    """
    if not config.get('WHATSAPP_ENABLED'):
        return False, "WhatsApp is not configured"

    phone_number_id = config['WHATSAPP_PHONE_NUMBER_ID']
    access_token = config['WHATSAPP_ACCESS_TOKEN']

    url = f"https://graph.facebook.com/v22.0/{phone_number_id}/messages"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": "order_status_update",
            "language": {
                "code": "en"
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": customer_name},
                        {"type": "text", "text": order_number},
                        {"type": "text", "text": status},
                        {"type": "text", "text": details}
                    ]
                }
            ]
        }
    }

    try:
        logger.info(f"Sending order_status_update to {to}")
        response = requests.post(url, headers=headers, json=payload, timeout=10)

        if response.status_code == 200:
            result = response.json()
            message_id = result.get('messages', [{}])[0].get('id', 'unknown')
            logger.info(f"Order status update sent to {to}: {message_id}")
            return True, f"Status update sent (ID: {message_id})"
        else:
            error_data = response.json()
            error_msg = error_data.get('error', {}).get('message', 'Unknown error')
            logger.error(f"WhatsApp API error: {error_msg}")
            return False, f"API Error: {error_msg}"

    except Exception as e:
        logger.error(f"Error sending order status update: {e}")
        return False, f"Error: {str(e)}"


def send_order_ready_template(
    to: str,
    customer_name: str,
    order_number: str,
    details: str,
    order_url: str,
    location_url: str,
    config: dict
) -> Tuple[bool, str]:
    """
    Send Order Ready Notification template

    Template: order_ready_notification
    Variables: {{1}} Name, {{2}} Order Number, {{3}} Details
    Buttons: View Order (URL), Pickup Location (Maps), Confirmed (Quick Reply)

    Args:
        to: Recipient phone number
        customer_name: Customer's name
        order_number: Order number
        details: Pickup/shipping details
        order_url: Full URL to view order
        location_url: Google Maps URL for pickup location
        config: Flask config object

    Returns:
        (success: bool, message: str)
    """
    if not config.get('WHATSAPP_ENABLED'):
        return False, "WhatsApp is not configured"

    phone_number_id = config['WHATSAPP_PHONE_NUMBER_ID']
    access_token = config['WHATSAPP_ACCESS_TOKEN']

    url = f"https://graph.facebook.com/v22.0/{phone_number_id}/messages"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": "order_ready_notification",
            "language": {
                "code": "en"
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": customer_name},
                        {"type": "text", "text": order_number},
                        {"type": "text", "text": details}
                    ]
                }
            ]
        }
    }

    try:
        logger.info(f"Sending order_ready_notification to {to}")
        response = requests.post(url, headers=headers, json=payload, timeout=10)

        if response.status_code == 200:
            result = response.json()
            message_id = result.get('messages', [{}])[0].get('id', 'unknown')
            logger.info(f"Order ready notification sent to {to}: {message_id}")
            return True, f"Order ready notification sent (ID: {message_id})"
        else:
            error_data = response.json()
            error_msg = error_data.get('error', {}).get('message', 'Unknown error')
            logger.error(f"WhatsApp API error: {error_msg}")
            return False, f"API Error: {error_msg}"

    except Exception as e:
        logger.error(f"Error sending order ready notification: {e}")
        return False, f"Error: {str(e)}"
