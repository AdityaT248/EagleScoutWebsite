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

products = [
    {
        "name": "Stainless Steel Cutlery",
        "description": "A premium set of stainless steel cutlery.",
        "price": 29.99,
        "image_url": "https://media.istockphoto.com/id/185307922/photo/cutlery.jpg?s=2048x2048&w=is&k=20&c=f5xqneU46sZ9XvZAQDyybreTiodP1eCS-ardrV4NdzA="
    },
    {
        "name": "Eco-friendly Kitchenware",
        "description": "Sustainable kitchenware for eco-conscious cooking.",
        "price": 19.99,
        "image_url": "https://media.istockphoto.com/id/1220650125/photo/bunner-eco-friendly-disposable-kitchenware-utensils-on-white-background-wooden-forks-and.jpg?s=2048x2048&w=is&k=20&c=mPXodqihyVw8OCf2Dxnolxr4xVjFrE9QURAk7QRLbqA="
    },
    {
        "name": "Elegant Cutlery Set",
        "description": "Elegant cutlery set for fine dining.",
        "price": 34.99,
        "image_url": "https://media.istockphoto.com/id/105863327/photo/cutlery.jpg?s=2048x2048&w=is&k=20&c=TPZ4bUTdDnbv9V-HYSltl9pkoRfjqETJBpnMaG0xM6k="
    },
    {
        "name": "Gas Stove Saucepans",
        "description": "A versatile set of saucepans for your gas stove.",
        "price": 24.99,
        "image_url": "https://media.istockphoto.com/id/1223414833/photo/clean-saucepan-on-a-gas-stove-in-kitchen.jpg?s=1024x1024&w=is&k=20&c=4GcTkhHYC_79aZ0FAYCDV2sb4qVrMJViFs_RbIsvDl0="
    },
    {
        "name": "Empty Pan Set",
        "description": "Set of pans ideal for most cooking needs.",
        "price": 14.99,
        "image_url": "https://media.istockphoto.com/id/1408070003/photo/empty-pans-setting-on-a-gray-granite-background-table.jpg?s=1024x1024&w=is&k=20&c=QvFl3zGPUCX72_ws_LfYCaxraF9ARhzb5nlzcG3i5AQ="
    },
    {
        "name": "Barbecue Tools",
        "description": "Essential barbecue tools for a perfect grill experience.",
        "price": 39.99,
        "image_url": "https://media.istockphoto.com/id/1146833253/photo/barbecue-tools-on-wooden-table-flat-lay-top-view.jpg?s=1024x1024&w=is&k=20&c=8AWu_6dTnu_2vm9P9ZK0v0HOW79ypEcjL04v2XO-BQo="
    }
]

comments = []

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
    return templates.TemplateResponse("index.html", {"request": request, "images": images, "products": products})

@app.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    file_location = uploads_dir / file.filename
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
    return RedirectResponse(url="/", status_code=303)

@app.post("/comments/")
async def post_comment(author: str = Form(...), comment: str = Form(...)):
    new_comment = {"author": author, "content": comment}
    comments.append(new_comment)
    return RedirectResponse(url="/comments_page", status_code=303)

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
    return templates.TemplateResponse("comments.html", {"request": request, "comments": comments})

@app.get("/contact_page", include_in_schema=False)
def contact_page(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})

@app.get("/home_page", include_in_schema=False)
def contact_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/add_product", include_in_schema=False)
def add_product_form(request: Request):
    return templates.TemplateResponse("add_product.html", {"request": request})

@app.post("/add_product", include_in_schema=False)
async def add_product(
    request: Request,
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    file: UploadFile = File(...)
):
    file_location = uploads_dir / file.filename
    with open(file_location, "wb+") as file_object:
        file_object.write(await file.read())
    product = {
        "name": name,
        "description": description,
        "price": price,
        "image_url": f"/uploads/{file.filename}"
    }
    products.append(product)
    return RedirectResponse(url="/", status_code=303)