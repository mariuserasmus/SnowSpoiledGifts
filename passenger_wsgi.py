"""
Passenger WSGI file for Snow's Spoiled Gifts
This file is required for deployment on Afrihost/cPanel with Passenger
"""

import sys
import os

# Add your project directory to the sys.path
INTERP = os.path.join(os.environ['HOME'], 'virtualenv', 'public_html', '3.9', 'bin', 'python3')
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

# Add the project directory to Python path
cwd = os.getcwd()
sys.path.insert(0, cwd)

# Import the Flask application
from app import app as application

# Passenger requires the application object to be named 'application'
# If your Flask app is named 'app' in app.py, we alias it here
# application = app  # Already done in the import above

# Optional: Configure production settings
application.config['ENV'] = 'production'
application.config['DEBUG'] = False

# Optional: Log startup
import logging
logging.basicConfig(level=logging.INFO)
logging.info('Snow\'s Spoiled Gifts application starting via Passenger WSGI')
