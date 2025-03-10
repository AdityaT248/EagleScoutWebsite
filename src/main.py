from fastapi import FastAPI, File, UploadFile, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from src.routes.availability_routes import router as availability_router
from src.routes.comments_routes import router as comments_router
from src.routes.contact_routes import router as contact_router
from src.routes.upload_routes import router as upload_router
import os
from pathlib import Path

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(availability_router, prefix="/availability", tags=["availability"])
app.include_router(comments_router, prefix="/comments", tags=["comments"])
app.include_router(contact_router, prefix="/contact", tags=["contact"])
app.include_router(upload_router, prefix="/upload", tags=["upload"])

# Create the uploads directory if it doesn't exist
uploads_dir = Path("uploads")
uploads_dir.mkdir(exist_ok=True)

# Serve static files from the uploads directory
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Serve static files from the src/static directory
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="src/templates")

@app.get("/", include_in_schema=False)
def home(request: Request):
    images = [f"/uploads/{file.name}" for file in uploads_dir.iterdir() if file.is_file()]
    return templates.TemplateResponse("index.html", {"request": request, "images": images})

@app.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    file_location = uploads_dir / file.filename
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
    return RedirectResponse(url="/", status_code=303)

@app.post("/comments/")
async def post_comment(comment: str = Form(...)):
    # Save the comment to a database or a file
    return RedirectResponse(url="/", status_code=303)

@app.get("/availability/events")
async def get_availability_events():
    # Return a list of availability events
    return [
        {"title": "Available", "start": "2025-03-10"},
        {"title": "Unavailable", "start": "2025-03-11"}
    ]

@app.get("/availability_page", include_in_schema=False)
def availability_page(request: Request):
    return templates.TemplateResponse("availability.html", {"request": request})

@app.get("/comments_page", include_in_schema=False)
def comments_page(request: Request):
    return templates.TemplateResponse("comments.html", {"request": request})

@app.get("/contact_page", include_in_schema=False)
def contact_page(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})

@app.get("/home_page", include_in_schema=False)
def contact_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})