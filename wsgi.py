"""
WSGI Entry Point for Production Deployment

This file is used by WSGI servers (like Gunicorn, uWSGI, or mod_wsgi)
to serve the Flask application in production.
"""

from app import app

# This allows the application to be run with:
# gunicorn wsgi:app
# or configured in Apache/Nginx with mod_wsgi/uWSGI

if __name__ == "__main__":
    app.run()
