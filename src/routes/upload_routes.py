from fastapi import APIRouter, UploadFile, File
from src.controllers.upload_controller import upload_image

router = APIRouter()

@router.post("/upload_image/")
async def upload_image_route(file: UploadFile = File(...)):
    return await upload_image(file)