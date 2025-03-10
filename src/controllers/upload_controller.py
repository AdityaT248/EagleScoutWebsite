from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
import os
import shutil

router = APIRouter()

@router.post("/upload_image/")
async def upload_image(file: UploadFile = File(...)):
    try:
        file_location = f"uploads/{file.filename}"
        os.makedirs("uploads", exist_ok=True)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return JSONResponse(content={"message": "File uploaded", "filename": file.filename}, status_code=201)
    except Exception as e:
        return JSONResponse(content={"message": "File upload failed", "error": str(e)}, status_code=500)