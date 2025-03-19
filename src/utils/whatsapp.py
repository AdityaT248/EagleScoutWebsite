import json
import httpx
from typing import Dict, Any, Optional
from src.config import (
    WHATSAPP_ENABLED,
    WHATSAPP_PHONE_NUMBER_ID,
    WHATSAPP_ACCESS_TOKEN,
    BUSINESS_NAME
)

# WhatsApp API URL
WHATSAPP_API_URL = f"https://graph.facebook.com/v17.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"

# WhatsApp message templates
BOOKING_CONFIRMATION_TEMPLATE = "booking_confirmation"
BOOKING_STATUS_UPDATE_TEMPLATE = "booking_status_update"
WELCOME_TEMPLATE = "welcome_message"

async def send_whatsapp_message(
    phone_number: Optional[str] = None,
    template: str = "booking_confirmation",
    params: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Send a WhatsApp message using a template.
    
    Args:
        phone_number: Recipient's phone number (optional - will use admin phone if not provided)
        template: Template name to use
        params: Parameters to fill in the template
        
    Returns:
        Dictionary with status of the operation
    """
    if not WHATSAPP_ENABLED:
        # WhatsApp integration is disabled, just log and return
        print(f"[WhatsApp] Not sending message (disabled): template={template}, params={params}")
        return {"success": False, "message": "WhatsApp integration is disabled"}
    
    try:
        # Use the provided phone number or a default (could be from config)
        if not phone_number:
            # In production, you would use a configured admin number
            print(f"[WhatsApp] No phone number provided, using dummy number")
            phone_number = "1234567890"  # Dummy number, will fail in real world
        
        # Format phone number (remove +)
        if phone_number.startswith('+'):
            phone_number = phone_number[1:]
            
        # Prepare template components with parameters
        template_params = []
        if params:
            for key, value in params.items():
                template_params.append({
                    "type": "text",
                    "text": value
                })
        
        # Create WhatsApp message payload
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "template",
            "template": {
                "name": template,
                "language": {
                    "code": "en_US"
                }
            }
        }
        
        # Add parameters if provided
        if template_params:
            payload["template"]["components"] = [
                {
                    "type": "body",
                    "parameters": template_params
                }
            ]
        
        # In a real implementation, you would make an API call:
        # async with httpx.AsyncClient() as client:
        #     response = await client.post(
        #         WHATSAPP_API_URL,
        #         headers={"Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}"},
        #         json=payload
        #     )
        
        # For now, just log and return mock success
        print(f"[WhatsApp] Would send message: template={template}, to={phone_number}, params={params}")
        return {"success": True, "message": "WhatsApp message simulated"}
        
    except Exception as e:
        print(f"[WhatsApp] Error sending message: {str(e)}")
        return {"success": False, "error": str(e)}

async def send_booking_confirmation(
    to_phone: str,
    booking_id: str,
    customer_name: str,
    start_date: str,
    end_date: str
) -> Dict[str, Any]:
    """
    Send a booking confirmation message via WhatsApp
    
    Args:
        to_phone: The customer's phone number
        booking_id: The booking ID
        customer_name: The customer's name
        start_date: Formatted start date of the booking
        end_date: Formatted end date of the booking
        
    Returns:
        The send_whatsapp_message response
    """
    template_params = {
        "1": customer_name,
        "2": booking_id,
        "3": start_date,
        "4": end_date,
        "5": BUSINESS_NAME
    }
    
    return await send_whatsapp_message(
        phone_number=to_phone,
        template=BOOKING_CONFIRMATION_TEMPLATE,
        params=template_params
    )

async def send_booking_status_update(
    to_phone: str,
    booking_id: str,
    customer_name: str,
    status: str,
    message: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send a booking status update via WhatsApp
    
    Args:
        to_phone: The customer's phone number
        booking_id: The booking ID
        customer_name: The customer's name
        status: The new status (approved, rejected, completed)
        message: Optional additional message
        
    Returns:
        The send_whatsapp_message response
    """
    template_params = {
        "1": customer_name,
        "2": booking_id,
        "3": status.upper(),
        "4": message or f"Your booking has been {status}."
    }
    
    return await send_whatsapp_message(
        phone_number=to_phone,
        template=BOOKING_STATUS_UPDATE_TEMPLATE,
        params=template_params
    )

async def send_welcome_message(
    to_phone: str,
    customer_name: str
) -> Dict[str, Any]:
    """
    Send a welcome message via WhatsApp
    
    Args:
        to_phone: The customer's phone number
        customer_name: The customer's name
        
    Returns:
        The send_whatsapp_message response
    """
    template_params = {
        "1": customer_name,
        "2": BUSINESS_NAME
    }
    
    return await send_whatsapp_message(
        phone_number=to_phone,
        template=WELCOME_TEMPLATE,
        params=template_params
    ) 