from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from src.models.booking_model import BookingCreate, BookingUpdate, Booking
from src.models.product_model import Product
from src.utils.database import (
    get_bookings,
    get_booking,
    add_booking,
    update_booking,
    delete_booking,
    get_product,
    get_products
)
from src.utils.auth import get_current_user
from src.utils.whatsapp import send_whatsapp_message

router = APIRouter()
templates = Jinja2Templates(directory="src/templates")

@router.get("/bookings", response_class=HTMLResponse)
async def bookings_page(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """User's bookings page"""
    user_bookings = get_bookings(user_id=current_user.get("id"))
    
    # Enhance bookings with product details
    for booking in user_bookings:
        for item in booking.get("items", []):
            product_id = item.get("product_id")
            product = get_product(product_id)
            if product:
                item["product"] = product
    
    return templates.TemplateResponse(
        "bookings/index.html",
        {"request": request, "bookings": user_bookings, "user": current_user}
    )

@router.get("/bookings/{booking_id}", response_class=HTMLResponse)
async def booking_detail(
    request: Request,
    booking_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Booking detail page"""
    booking = get_booking(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Check if user is authorized to view this booking
    if booking.get("user_id") != current_user.get("id"):
        raise HTTPException(status_code=403, detail="Not authorized to view this booking")
    
    # Enhance booking with product details
    for item in booking.get("items", []):
        product_id = item.get("product_id")
        product = get_product(product_id)
        if product:
            item["product"] = product
    
    return templates.TemplateResponse(
        "bookings/detail.html",
        {"request": request, "booking": booking, "user": current_user}
    )

@router.get("/book", response_class=HTMLResponse)
async def new_booking_page(
    request: Request,
    product_id: Optional[int] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """New booking page"""
    products_list = get_products()
    selected_product = None
    
    if product_id:
        selected_product = get_product(product_id)
        if not selected_product:
            raise HTTPException(status_code=404, detail="Product not found")
    
    return templates.TemplateResponse(
        "bookings/create.html",
        {
            "request": request, 
            "products": products_list,
            "selected_product": selected_product,
            "user": current_user
        }
    )

@router.post("/book", response_class=HTMLResponse)
async def create_booking(
    request: Request,
    start_date: str = Form(...),
    end_date: str = Form(...),
    product_ids: List[int] = Form(...),
    quantities: List[int] = Form(...),
    delivery_address: str = Form(...),
    notes: Optional[str] = Form(None),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new booking"""
    # Validate dates
    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
        
        if start_date_obj > end_date_obj:
            raise HTTPException(status_code=400, detail="End date must be after start date")
        
        if start_date_obj < datetime.now():
            raise HTTPException(status_code=400, detail="Start date cannot be in the past")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")
    
    # Create booking items
    items = []
    for i, product_id in enumerate(product_ids):
        product = get_product(product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")
        
        quantity = quantities[i]
        if quantity <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be greater than 0")
        
        items.append({
            "product_id": product_id,
            "quantity": quantity,
            "price": product.get("price", 0) * quantity
        })
    
    # Calculate total price
    total_price = sum(item.get("price", 0) for item in items)
    
    # Calculate days
    days = (end_date_obj - start_date_obj).days + 1
    
    # Create booking data
    booking_data = {
        "user_id": current_user.get("id"),
        "start_date": start_date,
        "end_date": end_date,
        "days": days,
        "items": items,
        "total_price": total_price,
        "delivery_address": delivery_address,
        "notes": notes,
        "status": "pending"
    }
    
    # Add booking to database
    new_booking = add_booking(booking_data)
    
    # Send WhatsApp confirmation message
    try:
        await send_whatsapp_message(
            phone_number=current_user.get("phone"),
            template="booking_confirmation",
            params={
                "customer_name": current_user.get("name"),
                "booking_id": str(new_booking.get("id")),
                "start_date": start_date,
                "end_date": end_date,
                "total_price": f"{total_price:.2f}"
            }
        )
    except Exception as e:
        # Log error but continue with booking process
        print(f"WhatsApp notification error: {str(e)}")
    
    return RedirectResponse(
        url=f"/bookings/{new_booking.get('id')}",
        status_code=status.HTTP_303_SEE_OTHER
    )

@router.get("/bookings/{booking_id}/cancel", response_class=HTMLResponse)
async def cancel_booking_page(
    request: Request,
    booking_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Cancel booking confirmation page"""
    booking = get_booking(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Check if user is authorized to cancel this booking
    if booking.get("user_id") != current_user.get("id"):
        raise HTTPException(status_code=403, detail="Not authorized to cancel this booking")
    
    # Check if booking can be cancelled
    if booking.get("status") not in ["pending", "confirmed"]:
        raise HTTPException(status_code=400, detail="This booking cannot be cancelled")
    
    # Get start date
    start_date = datetime.strptime(booking.get("start_date"), "%Y-%m-%d")
    # If the booking is less than 24 hours away, don't allow cancellation
    if start_date - datetime.now() < timedelta(hours=24):
        raise HTTPException(status_code=400, detail="Bookings must be cancelled at least 24 hours in advance")
    
    return templates.TemplateResponse(
        "bookings/cancel.html",
        {"request": request, "booking": booking, "user": current_user}
    )

@router.post("/bookings/{booking_id}/cancel", response_class=HTMLResponse)
async def cancel_booking(
    request: Request,
    booking_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Cancel a booking"""
    booking = get_booking(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Check if user is authorized to cancel this booking
    if booking.get("user_id") != current_user.get("id"):
        raise HTTPException(status_code=403, detail="Not authorized to cancel this booking")
    
    # Check if booking can be cancelled
    if booking.get("status") not in ["pending", "confirmed"]:
        raise HTTPException(status_code=400, detail="This booking cannot be cancelled")
    
    # Update booking status
    update_booking(booking_id, {"status": "cancelled"})
    
    # Send WhatsApp cancellation message
    try:
        await send_whatsapp_message(
            phone_number=current_user.get("phone"),
            template="booking_cancellation",
            params={
                "customer_name": current_user.get("name"),
                "booking_id": str(booking_id)
            }
        )
    except Exception as e:
        # Log error but continue with cancellation process
        print(f"WhatsApp notification error: {str(e)}")
    
    return RedirectResponse(
        url="/bookings?cancelled=true",
        status_code=status.HTTP_303_SEE_OTHER
    )

# Admin routes
@router.get("/admin/bookings", response_class=HTMLResponse)
async def admin_bookings_page(
    request: Request,
    status: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Admin bookings page"""
    # Check if user is admin
    if not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get all bookings
    bookings_list = get_bookings()
    
    # Filter by status if provided
    if status:
        bookings_list = [b for b in bookings_list if b.get("status") == status]
    
    return templates.TemplateResponse(
        "admin/bookings.html",
        {"request": request, "bookings": bookings_list, "user": current_user}
    )

@router.get("/admin/bookings/{booking_id}", response_class=HTMLResponse)
async def admin_booking_detail(
    request: Request,
    booking_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Admin booking detail page"""
    # Check if user is admin
    if not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    booking = get_booking(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Enhance booking with product details
    for item in booking.get("items", []):
        product_id = item.get("product_id")
        product = get_product(product_id)
        if product:
            item["product"] = product
    
    return templates.TemplateResponse(
        "admin/booking_detail.html",
        {"request": request, "booking": booking, "user": current_user}
    )

@router.post("/admin/bookings/{booking_id}/status", response_class=HTMLResponse)
async def update_booking_status(
    request: Request,
    booking_id: int,
    status: str = Form(...),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update booking status"""
    # Check if user is admin
    if not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    booking = get_booking(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Validate status
    valid_statuses = ["pending", "confirmed", "in-progress", "completed", "cancelled", "rejected"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    # Update booking status
    update_booking(booking_id, {"status": status})
    
    return RedirectResponse(
        url=f"/admin/bookings/{booking_id}?updated=true",
        status_code=status.HTTP_303_SEE_OTHER
    )

# API endpoints for AJAX requests
@router.get("/api/bookings")
async def api_get_bookings(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """API endpoint to get user's bookings"""
    user_bookings = get_bookings(user_id=current_user.get("id"))
    return {"bookings": user_bookings}

@router.get("/api/bookings/{booking_id}")
async def api_get_booking(
    booking_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """API endpoint to get a specific booking"""
    booking = get_booking(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Check if user is authorized to view this booking
    if booking.get("user_id") != current_user.get("id") and not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Not authorized to view this booking")
    
    return {"booking": booking} 