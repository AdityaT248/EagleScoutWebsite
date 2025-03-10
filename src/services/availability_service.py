from typing import Dict, Any

class AvailabilityService:
    def __init__(self):
        self.availability = {}

    def check_availability(self, date: str) -> Dict[str, Any]:
        return {"date": date, "available": self.availability.get(date, True)}

    def set_availability(self, date: str, available: bool) -> Dict[str, Any]:
        self.availability[date] = available
        return {"message": "Availability updated", "date": date, "available": available}