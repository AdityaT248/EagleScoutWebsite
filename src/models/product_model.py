from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)
    category: str = Field(..., min_length=1, max_length=50)
    quantity: int = Field(..., gt=0)
    
class ProductCreate(ProductBase):
    image_url: Optional[str] = None
    
class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=1)
    price: Optional[float] = Field(None, gt=0)
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    image_url: Optional[str] = None
    availability: Optional[str] = None
    quantity: Optional[int] = Field(None, gt=0)
    
class Product(ProductBase):
    id: int
    image_url: str
    availability: str = "in-stock"  # in-stock, limited, out-of-stock
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}

# Category model
class Category(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    
    model_config = {"from_attributes": True} 