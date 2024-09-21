"""
CORS Headers Settings
GitHub: https://github.com/adamchainz/django-cors-headers
"""

CORS_ORIGIN_WHITELIST = [
    'https://web-app-marketplace-sviy.vercel.app',
]
CORS_ALLOW_METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
CORS_ALLOW_HEADERS = ['Content-Type', 'Authorization']
CORS_ALLOW_CREDENTIALS = True
