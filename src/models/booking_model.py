from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime, date

class BookingProductItem(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)
    
class BookingBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: str = Field(..., pattern=r"^\+?[0-9\s\-\(\)]+$")
    start_date: date
    end_date: date
    products: List[BookingProductItem]
    message: Optional[str] = None
    
class BookingCreate(BookingBase):
    pass
    
class BookingUpdate(BaseModel):
    status: Optional[str] = None
    admin_notes: Optional[str] = None
    
class Booking(BookingBase):
    id: str
    status: str  # pending, approved, rejected, completed
    created_at: datetime
    updated_at: Optional[datetime] = None
    admin_notes: Optional[str] = None
    
    model_config = {"from_attributes": True}

class BookingResponse(BaseModel):
    booking: Booking
    products_details: List[Dict[str, Any]]
    total_price: float
    
    model_config = {"from_attributes": True} 