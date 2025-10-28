#!/usr/bin/env python3
"""
Simple version checker to verify which code is running
Add this as a route to check deployment
"""

VERSION_INFO = {
    'version': '2024-10-28-cosmetic-updates',
    'commit': '4885e72',
    'changes': [
        'Homepage: "What We Offer" (not "What We\'ll Offer")',
        'Admin buttons: outline style (not solid)',
        'Email customer: modal form (not mailto link)',
        'Fixed cPanel deployment pip error'
    ],
    'last_updated': '2024-10-28'
}

def get_version_info():
    """Return version information"""
    return VERSION_INFO
