from fastapi import APIRouter
from src.controllers.availability_controller import check_availability, set_availability

router = APIRouter()

router.get("/availability/{date}", response_model=dict)(check_availability)
router.post("/set_availability/{date}", response_model=dict)(set_availability)