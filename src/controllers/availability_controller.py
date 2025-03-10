from fastapi import APIRouter, HTTPException
from src.models.availability_model import Availability
from src.services.availability_service import AvailabilityService

router = APIRouter()
availability_service = AvailabilityService()

@router.get("/{date}")
def check_availability(date: str):
    available = availability_service.check_availability(date)
    return {"date": date, "available": available}

@router.post("/{date}")
def set_availability(date: str, available: bool):
    try:
        availability_service.set_availability(date, available)
        return {"message": "Availability updated", "date": date, "available": available}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))