import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""

    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Database settings
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'database/signups.db')

    # Admin credentials
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'changeme123')

    # Site settings
    SITE_NAME = "Snow Spoiled Gifts"
    SITE_URL = "www.snowspoiledgifts.co.za"
    CONTACT_EMAIL = "elmienerasmus@gmail.com"
    CONTACT_PHONE = "+71 4711 779"

    # Launch settings
    LAUNCH_DATE = "November 2025"
    TAGLINE = "Personalized Gifts, Made with Love"

    # Social Media Links (update these with your actual links)
    SOCIAL_MEDIA = {
        'facebook': 'https://facebook.com/snowspoiledgifts',
        'instagram': 'https://www.instagram.com/sn0w_sp0ild_g1fts',
        'whatsapp': 'https://wa.me/27714711779',  # Replace with your WhatsApp number
    }

    # Email settings for notifications
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'False') == 'True'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'elmienerasmus@gmail.com')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')  # Set in .env file
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'elmienerasmus@gmail.com')

    # Notification recipients (comma-separated in .env, defaults to both emails)
    NOTIFICATION_RECIPIENTS = os.getenv(
        'NOTIFICATION_RECIPIENTS',
        'elmienerasmus@gmail.com,mariuserasmus69@gmail.com'
    ).split(',')

    # Base URL for links in emails (unsubscribe, etc.)
    BASE_URL = os.getenv('BASE_URL', 'http://192.168.0.248:5000')
