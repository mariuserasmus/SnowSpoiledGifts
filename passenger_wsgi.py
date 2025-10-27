"""
Passenger WSGI file for Snow's Spoiled Gifts
This file is required for deployment on Afrihost/cPanel with Passenger
"""

import sys
import os

# Add the project directory to Python path
cwd = os.getcwd()
sys.path.insert(0, cwd)

# Add src directory to path
src_path = os.path.join(cwd, 'src')
if os.path.exists(src_path):
    sys.path.insert(0, src_path)

# Import the Flask application
from app import app as application

# Passenger requires the application object to be named 'application'
# Configure production settings
application.config['ENV'] = 'production'
application.config['DEBUG'] = False
