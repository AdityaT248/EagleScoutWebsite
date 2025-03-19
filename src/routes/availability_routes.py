from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from src.models.availability_model import AvailabilityCreate, AvailabilityUpdate, Availability, DateRangeRequest
from src.utils.database import (
    get_availabilities, 
    get_availability, 
    add_availability, 
    update_availability, 
    delete_availability,
    get_product,
    get_bookings
)
from src.utils.auth import get_current_user, get_admin_user

router = APIRouter()
templates = Jinja2Templates(directory="src/templates")

@router.get("/api/products/{product_id}/availability")
async def get_product_availability(
    product_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """API endpoint to get product availability"""
    # Get product
    product = get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get availability records for this product
    availabilities = get_availabilities(product_id=product_id)
    
    # Get bookings that affect this product's availability
    bookings = get_bookings(product_id=product_id)
    
    # Parse date range if provided
    date_range = {}
    if start_date:
        try:
            date_range["start_date"] = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start date format")
    
    if end_date:
        try:
            date_range["end_date"] = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end date format")
    
    # If date range provided, filter availability records
    if date_range:
        filtered_availabilities = []
        for avail in availabilities:
            avail_start = datetime.strptime(avail.get("start_date"), "%Y-%m-%d")
            avail_end = datetime.strptime(avail.get("end_date"), "%Y-%m-%d")
            
            # Check if availability overlaps with the requested date range
            if ("start_date" not in date_range or avail_end >= date_range["start_date"]) and \
               ("end_date" not in date_range or avail_start <= date_range["end_date"]):
                filtered_availabilities.append(avail)
        
        availabilities = filtered_availabilities
    
    # Calculate available quantity for each date
    available_dates = {}
    
    # Start with total quantity from product
    total_quantity = product.get("quantity", 0)
    
    # Process availability records
    for avail in availabilities:
        avail_start = datetime.strptime(avail.get("start_date"), "%Y-%m-%d")
        avail_end = datetime.strptime(avail.get("end_date"), "%Y-%m-%d")
        
        # For each date in the availability range
        current_date = avail_start
        while current_date <= avail_end:
            date_str = current_date.strftime("%Y-%m-%d")
            
            # Initialize if needed
            if date_str not in available_dates:
                available_dates[date_str] = total_quantity
            
            # Apply availability adjustment
            available_dates[date_str] = avail.get("available_quantity", total_quantity)
            
            current_date += timedelta(days=1)
    
    # Process bookings to reduce available quantities
    for booking in bookings:
        if booking.get("status") in ["pending", "confirmed", "in-progress"]:
            booking_start = datetime.strptime(booking.get("start_date"), "%Y-%m-%d")
            booking_end = datetime.strptime(booking.get("end_date"), "%Y-%m-%d")
            
            # Find booking item for this product
            booked_quantity = 0
            for item in booking.get("items", []):
                if item.get("product_id") == product_id:
                    booked_quantity = item.get("quantity", 0)
                    break
            
            if booked_quantity > 0:
                # For each date in the booking range
                current_date = booking_start
                while current_date <= booking_end:
                    date_str = current_date.strftime("%Y-%m-%d")
                    
                    # Initialize if needed
                    if date_str not in available_dates:
                        available_dates[date_str] = total_quantity
                    
                    # Reduce available quantity by booked quantity
                    available_dates[date_str] -= booked_quantity
                    
                    current_date += timedelta(days=1)
    
    # Convert to array of objects for API response
    availability_array = [
        {"date": date, "available": qty} for date, qty in available_dates.items()
    ]
    
    # Sort by date
    availability_array.sort(key=lambda x: x["date"])
    
    return {"product_id": product_id, "availability": availability_array}

@router.post("/api/products/{product_id}/check-availability")
async def check_product_availability(
    product_id: int,
    date_range: DateRangeRequest
):
    """API endpoint to check if product is available for the given date range"""
    # Get product
    product = get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get availability for the product
    availability_response = await get_product_availability(
        product_id=product_id,
        start_date=date_range.start_date,
        end_date=date_range.end_date
    )
    
    # Check if the product is available for the entire date range
    availability_array = availability_response.get("availability", [])
    
    # Calculate required quantity
    required_quantity = date_range.quantity or 1
    
    # Check if all dates have enough availability
    is_available = all(
        item["available"] >= required_quantity for item in availability_array
    )
    
    # Find dates with insufficient availability
    unavailable_dates = [
        item["date"] for item in availability_array
        if item["available"] < required_quantity
    ]
    
    return {
        "product_id": product_id,
        "is_available": is_available,
        "unavailable_dates": unavailable_dates if unavailable_dates else None
    }

# Admin routes for managing availability
@router.get("/admin/products/{product_id}/availability", response_class=HTMLResponse)
async def admin_availability_page(
    request: Request,
    product_id: int,
    current_user: Dict[str, Any] = Depends(get_admin_user)
):
    """Admin page for managing product availability"""
    # Get product
    product = get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get availability records for this product
    availabilities = get_availabilities(product_id=product_id)
    
    return templates.TemplateResponse(
        "admin/availability.html",
        {
            "request": request,
            "product": product,
            "availabilities": availabilities,
            "user": current_user
        }
    )

@router.post("/admin/products/{product_id}/availability", response_class=HTMLResponse)
async def create_availability(
    request: Request,
    product_id: int,
    start_date: str = Form(...),
    end_date: str = Form(...),
    available_quantity: int = Form(...),
    current_user: Dict[str, Any] = Depends(get_admin_user)
):
    """Create a new availability record"""
    # Get product
    product = get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Validate dates
    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
        
        if start_date_obj > end_date_obj:
            raise HTTPException(status_code=400, detail="End date must be after start date")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")
    
    # Validate quantity
    if available_quantity < 0:
        raise HTTPException(status_code=400, detail="Available quantity cannot be negative")
    
    # Create availability data
    availability_data = {
        "product_id": product_id,
        "start_date": start_date,
        "end_date": end_date,
        "available_quantity": available_quantity
    }
    
    # Add availability to database
    new_availability = add_availability(availability_data)
    
    return RedirectResponse(
        url=f"/admin/products/{product_id}/availability?created=true",
        status_code=status.HTTP_303_SEE_OTHER
    )

@router.get("/admin/availabilities/{availability_id}/delete", response_class=HTMLResponse)
async def delete_availability_handler(
    request: Request,
    availability_id: int,
    current_user: Dict[str, Any] = Depends(get_admin_user)
):
    """Delete an availability record"""
    # Get availability
    availability = get_availability(availability_id)
    if not availability:
        raise HTTPException(status_code=404, detail="Availability record not found")
    
    # Get product ID for redirection
    product_id = availability.get("product_id")
    
    # Delete availability
    delete_availability(availability_id)
    
    return RedirectResponse(
        url=f"/admin/products/{product_id}/availability?deleted=true",
        status_code=status.HTTP_303_SEE_OTHER
    )

@router.get("/admin/availabilities/{availability_id}", response_class=HTMLResponse)
async def edit_availability_page(
    request: Request,
    availability_id: int,
    current_user: Dict[str, Any] = Depends(get_admin_user)
):
    """Edit availability page"""
    # Get availability
    availability = get_availability(availability_id)
    if not availability:
        raise HTTPException(status_code=404, detail="Availability record not found")
    
    # Get product
    product_id = availability.get("product_id")
    product = get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return templates.TemplateResponse(
        "admin/availability_form.html",
        {
            "request": request,
            "product": product,
            "availability": availability,
            "user": current_user
        }
    )

@router.post("/admin/availabilities/{availability_id}", response_class=HTMLResponse)
async def update_availability_handler(
    request: Request,
    availability_id: int,
    start_date: str = Form(...),
    end_date: str = Form(...),
    available_quantity: int = Form(...),
    current_user: Dict[str, Any] = Depends(get_admin_user)
):
    """Update an availability record"""
    # Get availability
    availability = get_availability(availability_id)
    if not availability:
        raise HTTPException(status_code=404, detail="Availability record not found")
    
    # Get product ID for redirection
    product_id = availability.get("product_id")
    
    # Validate dates
    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
        
        if start_date_obj > end_date_obj:
            raise HTTPException(status_code=400, detail="End date must be after start date")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")
    
    # Validate quantity
    if available_quantity < 0:
        raise HTTPException(status_code=400, detail="Available quantity cannot be negative")
    
    # Update availability data
    availability_data = {
        "start_date": start_date,
        "end_date": end_date,
        "available_quantity": available_quantity
    }
    
    # Update availability in database
    updated_availability = update_availability(availability_id, availability_data)
    
    return RedirectResponse(
        url=f"/admin/products/{product_id}/availability?updated=true",
        status_code=status.HTTP_303_SEE_OTHER
    )