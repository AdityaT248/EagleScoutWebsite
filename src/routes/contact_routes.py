from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.utils.database import (
    add_contact_message,
    get_contact_messages,
    get_contact_message,
    update_contact_message,
    delete_contact_message
)
from src.utils.auth import get_current_user, get_admin_user
from src.utils.whatsapp import send_whatsapp_message

router = APIRouter()
templates = Jinja2Templates(directory="src/templates")

@router.get("/contact", response_class=HTMLResponse)
async def contact_page(request: Request):
    """Contact page"""
    return templates.TemplateResponse(
        "contact.html",
        {"request": request}
    )

@router.post("/contact", response_class=HTMLResponse)
async def submit_contact(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    phone: Optional[str] = Form(None),
    subject: str = Form(...),
    message: str = Form(...)
):
    """Submit contact form"""
    # Create contact message data
    contact_data = {
        "name": name,
        "email": email,
        "phone": phone,
        "subject": subject,
        "message": message,
        "status": "new",
        "created_at": datetime.now().isoformat()
    }
    
    # Add contact message to database
    contact_message = add_contact_message(contact_data)
    
    # Try to send WhatsApp notification to admin
    try:
        await send_whatsapp_message(
            phone_number=None,  # Will use admin phone from config
            template="new_contact_message",
            params={
                "name": name,
                "subject": subject
            }
        )
    except Exception as e:
        # Log error but continue with contact form submission
        print(f"WhatsApp notification error: {str(e)}")
    
    return templates.TemplateResponse(
        "contact_success.html",
        {"request": request, "name": name}
    )

# Admin routes
@router.get("/admin/contacts", response_class=HTMLResponse)
async def admin_contacts_page(
    request: Request,
    status: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_admin_user)
):
    """Admin contacts page"""
    # Get contact messages
    contact_messages = get_contact_messages()
    
    # Filter by status if provided
    if status:
        contact_messages = [c for c in contact_messages if c.get("status") == status]
    
    return templates.TemplateResponse(
        "admin/contacts.html",
        {"request": request, "contacts": contact_messages, "user": current_user}
    )

@router.get("/admin/contacts/{contact_id}", response_class=HTMLResponse)
async def admin_contact_detail(
    request: Request,
    contact_id: int,
    current_user: Dict[str, Any] = Depends(get_admin_user)
):
    """Admin contact detail page"""
    # Get contact message
    contact_message = get_contact_message(contact_id)
    if not contact_message:
        raise HTTPException(status_code=404, detail="Contact message not found")
    
    return templates.TemplateResponse(
        "admin/contact_detail.html",
        {"request": request, "contact": contact_message, "user": current_user}
    )

@router.post("/admin/contacts/{contact_id}/status", response_class=HTMLResponse)
async def update_contact_status(
    request: Request,
    contact_id: int,
    status: str = Form(...),
    current_user: Dict[str, Any] = Depends(get_admin_user)
):
    """Update contact message status"""
    # Get contact message
    contact_message = get_contact_message(contact_id)
    if not contact_message:
        raise HTTPException(status_code=404, detail="Contact message not found")
    
    # Validate status
    valid_statuses = ["new", "in-progress", "resolved", "spam"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    # Update contact message status
    update_contact_message(contact_id, {"status": status})
    
    return RedirectResponse(
        url=f"/admin/contacts/{contact_id}?updated=true",
        status_code=status.HTTP_303_SEE_OTHER
    )

@router.post("/admin/contacts/{contact_id}/reply", response_class=HTMLResponse)
async def reply_to_contact(
    request: Request,
    contact_id: int,
    reply_message: str = Form(...),
    current_user: Dict[str, Any] = Depends(get_admin_user)
):
    """Reply to a contact message"""
    # Get contact message
    contact_message = get_contact_message(contact_id)
    if not contact_message:
        raise HTTPException(status_code=404, detail="Contact message not found")
    
    # Create reply data
    reply_data = {
        "reply": reply_message,
        "replied_at": datetime.now().isoformat(),
        "replied_by": current_user.get("id"),
        "status": "resolved"
    }
    
    # Update contact message with reply
    update_contact_message(contact_id, reply_data)
    
    # Try to send WhatsApp reply notification if phone is available
    phone = contact_message.get("phone")
    if phone:
        try:
            await send_whatsapp_message(
                phone_number=phone,
                template="contact_reply",
                params={
                    "name": contact_message.get("name"),
                    "message": reply_message[:150]  # Truncate if too long
                }
            )
        except Exception as e:
            # Log error but continue with reply submission
            print(f"WhatsApp notification error: {str(e)}")
    
    return RedirectResponse(
        url=f"/admin/contacts/{contact_id}?replied=true",
        status_code=status.HTTP_303_SEE_OTHER
    )

@router.get("/admin/contacts/{contact_id}/delete", response_class=HTMLResponse)
async def delete_contact_handler(
    request: Request,
    contact_id: int,
    current_user: Dict[str, Any] = Depends(get_admin_user)
):
    """Delete a contact message"""
    # Get contact message
    contact_message = get_contact_message(contact_id)
    if not contact_message:
        raise HTTPException(status_code=404, detail="Contact message not found")
    
    # Delete contact message
    delete_contact_message(contact_id)
    
    return RedirectResponse(
        url="/admin/contacts?deleted=true",
        status_code=status.HTTP_303_SEE_OTHER
    )