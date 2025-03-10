from fastapi import UploadFile
import os
import shutil

class UploadService:
    @staticmethod
    def save_file(file: UploadFile) -> str:
        file_location = f"uploads/{file.filename}"
        os.makedirs("uploads", exist_ok=True)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return file_location

    @staticmethod
    def delete_file(filename: str) -> bool:
        file_location = f"uploads/{filename}"
        if os.path.exists(file_location):
            os.remove(file_location)
            return True
        return False

    @staticmethod
    def list_files() -> list:
        return os.listdir("uploads") if os.path.exists("uploads") else []