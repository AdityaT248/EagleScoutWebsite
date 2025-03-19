"""
Configuration settings for the Zero Waste Cutlery Rental application.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Application settings
APP_NAME = os.getenv("APP_NAME", "Zero Waste Cutlery Rental")
APP_DESCRIPTION = os.getenv("APP_DESCRIPTION", "Sustainable cutlery rental for eco-conscious events")
DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
SECRET_KEY = os.getenv("SECRET_KEY", "insecure-secret-key-change-in-production")

# JWT settings for authentication
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = 60 * 24  # 24 hours

# Database settings
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./zerowastedb.sqlite")

# Upload settings
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
UPLOADS_DIR = BASE_DIR / UPLOAD_FOLDER
UPLOADS_DIR.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))  # 16MB max upload size

# Images subdirectories
PRODUCT_IMAGES_DIR = UPLOADS_DIR / "products"
PRODUCT_IMAGES_DIR.mkdir(exist_ok=True)
USER_IMAGES_DIR = UPLOADS_DIR / "user_uploads"
USER_IMAGES_DIR.mkdir(exist_ok=True)
COMMENT_IMAGES_DIR = UPLOADS_DIR / "comments"
COMMENT_IMAGES_DIR.mkdir(exist_ok=True)

# WhatsApp Business API settings
WHATSAPP_ENABLED = bool(os.getenv("WHATSAPP_PHONE_NUMBER_ID", ""))
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
WHATSAPP_BUSINESS_ACCOUNT_ID = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID", "")
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN", "")

# Business information
BUSINESS_NAME = "Zero Waste Cutlery Rental"
BUSINESS_EMAIL = "contact@zerowasterentals.com"
BUSINESS_PHONE = "+1 (555) 123-4567"
BUSINESS_ADDRESS = "123 Eco Street, Green City, 12345"
BUSINESS_HOURS = "Monday - Friday: 9:00 AM - 6:00 PM, Saturday: 10:00 AM - 4:00 PM, Sunday: Closed"
BUSINESS_WHATSAPP = "https://wa.me/15551234567"

# Social media links
SOCIAL_LINKS = {
    "facebook": "https://facebook.com/zerowasterentals",
    "instagram": "https://instagram.com/zerowasterentals",
    "twitter": "https://twitter.com/zerowasterentals"
}

# Create necessary directories
for directory in [UPLOADS_DIR, PRODUCT_IMAGES_DIR, USER_IMAGES_DIR, COMMENT_IMAGES_DIR]:
    directory.mkdir(exist_ok=True)

# Database directory
DB_DIR = UPLOADS_DIR / "db"
DB_DIR.mkdir(exist_ok=True)

# Email settings
MAIL_SERVER = os.getenv("MAIL_SERVER", "")
MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
MAIL_FROM = os.getenv("MAIL_FROM", "")
MAIL_TLS = os.getenv("MAIL_TLS", "True").lower() in ("true", "1", "t")
MAIL_SSL = os.getenv("MAIL_SSL", "False").lower() in ("true", "1", "t")

# PayPal Configuration
PAYPAL_CLIENT_ID = "YOUR_PAYPAL_CLIENT_ID"  # Replace with your actual PayPal client ID
PAYPAL_CLIENT_SECRET = "YOUR_PAYPAL_CLIENT_SECRET"  # Replace with your actual PayPal client secret

# PayPal Environment - set to 'sandbox' for testing, 'production' for live payments
PAYPAL_ENVIRONMENT = "sandbox"

# Merchant Information
MERCHANT_EMAIL = "your-business-email@example.com"  # The PayPal account email that will receive payments
MERCHANT_NAME = "Cutlery Rental Service"

# Create additional necessary directories
# Static files directory
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)

# Templates directory
TEMPLATES_DIR = BASE_DIR / "templates"
TEMPLATES_DIR.mkdir(exist_ok=True) 