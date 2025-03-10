from fastapi import APIRouter

router = APIRouter()

@router.get("/contact")
def get_contact_info():
    return {
        "whatsapp": "https://wa.me/yourbusinessnumber",
        "email": "info@cutleryrental.com"
    }