"""
Configuration settings for the Cutlery Rental application.
"""

# PayPal Configuration
PAYPAL_CLIENT_ID = "YOUR_PAYPAL_CLIENT_ID"  # Replace with your actual PayPal client ID
PAYPAL_CLIENT_SECRET = "YOUR_PAYPAL_CLIENT_SECRET"  # Replace with your actual PayPal client secret

# PayPal Environment - set to 'sandbox' for testing, 'production' for live payments
PAYPAL_ENVIRONMENT = "sandbox"

# Merchant Information
MERCHANT_EMAIL = "your-business-email@example.com"  # The PayPal account email that will receive payments
MERCHANT_NAME = "Cutlery Rental Service"

# Application Settings
DEBUG = True
UPLOAD_FOLDER = "src/static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size 