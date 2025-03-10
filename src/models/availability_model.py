from pydantic import BaseModel
from typing import Optional

class AvailabilityModel(BaseModel):
    date: str
    available: bool

class AvailabilityResponse(BaseModel):
    message: str
    date: str
    available: bool

class AvailabilityCheckResponse(BaseModel):
    date: str
    available: bool

class AvailabilityUpdateRequest(BaseModel):
    available: bool

class AvailabilityListResponse(BaseModel):
    availability: list[AvailabilityCheckResponse]

class Availability:
    # Define the attributes and methods for the Availability class
    def __init__(self, id: int, available: bool):
        self.id = id
        self.available = available

    def __repr__(self):
        return f"<Availability(id={self.id}, available={self.available})>"