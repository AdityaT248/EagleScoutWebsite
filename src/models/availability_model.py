from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date

class AvailabilityBase(BaseModel):
    date: date
    status: str = Field(..., pattern=r"^(available|unavailable|limited)$")
    note: Optional[str] = None
    
class AvailabilityCreate(AvailabilityBase):
    pass
    
class AvailabilityUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern=r"^(available|unavailable|limited)$")
    note: Optional[str] = None
    
class Availability(AvailabilityBase):
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}

class AvailabilityResponse(BaseModel):
    availability: List[Availability]
    
class DateRangeRequest(BaseModel):
    start_date: date
    end_date: date
    quantity: Optional[int] = 1