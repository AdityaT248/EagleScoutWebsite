from fastapi import APIRouter
from src.controllers.contact_controller import get_contact_info

router = APIRouter()

@router.get("/contact")
async def contact():
    return await get_contact_info()