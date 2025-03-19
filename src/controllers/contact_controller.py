from fastapi import APIRouter
import os
from typing import Optional
from src.utils.database import save_contact_message as db_save_contact

router = APIRouter()

# Directory for storing contact messages
CONTACT_DIR = "uploads/contact"
os.makedirs(CONTACT_DIR, exist_ok=True)

@router.get("/contact")
def get_contact_info():
    return {
        "whatsapp": "https://wa.me/yourbusinessnumber",
        "email": "info@cutleryrental.com"
    }

async def save_contact_message(name: str, email: str, phone: Optional[str], subject: str, message: str):
    """Save a contact message using the database utility"""
    return db_save_contact(name, email, phone, subject, message)