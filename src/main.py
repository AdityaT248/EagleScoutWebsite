from fastapi import FastAPI, File, UploadFile, Request, Form, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from src.routes.availability_routes import router as availability_router
from src.routes.comments_routes import router as comments_router
from src.routes.contact_routes import router as contact_router
from src.routes.upload_routes import router as upload_router
import os
from pathlib import Path
from datetime import datetime, timedelta
from . import config
import requests
import json
import asyncio
import secrets
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.templating import _TemplateResponse

products = [
    {
        "id": 1,
        "name": "Stainless Steel Cutlery",
        "description": "A premium set of stainless steel cutlery.",
        "price": 29.99,
        "image_url": "https://media.istockphoto.com/id/185307922/photo/cutlery.jpg?s=2048x2048&w=is&k=20&c=f5xqneU46sZ9XvZAQDyybreTiodP1eCS-ardrV4NdzA=",
        "category": "cutlery",
        "availability": "in-stock",
        "rating": 4.5,
        "reviews": 38
    },
    {
        "id": 2,
        "name": "Eco-friendly Kitchenware",
        "description": "Sustainable kitchenware for eco-conscious cooking.",
        "price": 19.99,
        "image_url": "https://media.istockphoto.com/id/1220650125/photo/bunner-eco-friendly-disposable-kitchenware-utensils-on-white-background-wooden-forks-and.jpg?s=2048x2048&w=is&k=20&c=mPXodqihyVw8OCf2Dxnolxr4xVjFrE9QURAk7QRLbqA=",
        "category": "kitchenware",
        "availability": "in-stock",
        "rating": 4.2,
        "reviews": 25
    },
    {
        "id": 3,
        "name": "Elegant Cutlery Set",
        "description": "Elegant cutlery set for fine dining.",
        "price": 34.99,
        "image_url": "https://media.istockphoto.com/id/105863327/photo/cutlery.jpg?s=2048x2048&w=is&k=20&c=TPZ4bUTdDnbv9V-HYSltl9pkoRfjqETJBpnMaG0xM6k=",
        "category": "cutlery",
        "availability": "in-stock",
        "rating": 4.8,
        "reviews": 45
    },
    {
        "id": 4,
        "name": "Gas Stove Saucepans",
        "description": "A versatile set of saucepans for your gas stove.",
        "price": 24.99,
        "image_url": "https://media.istockphoto.com/id/1223414833/photo/clean-saucepan-on-a-gas-stove-in-kitchen.jpg?s=1024x1024&w=is&k=20&c=4GcTkhHYC_79aZ0FAYCDV2sb4qVrMJViFs_RbIsvDl0=",
        "category": "cookware",
        "availability": "in-stock",
        "rating": 4.0,
        "reviews": 18
    },
    {
        "id": 5,
        "name": "Empty Pan Set",
        "description": "Set of pans ideal for most cooking needs.",
        "price": 14.99,
        "image_url": "https://media.istockphoto.com/id/1408070003/photo/empty-pans-setting-on-a-gray-granite-background-table.jpg?s=1024x1024&w=is&k=20&c=QvFl3zGPUCX72_ws_LfYCaxraF9ARhzb5nlzcG3i5AQ=",
        "category": "cookware",
        "availability": "limited",
        "rating": 3.9,
        "reviews": 12
    },
    {
        "id": 6,
        "name": "Barbecue Tools",
        "description": "Essential barbecue tools for a perfect grill experience.",
        "price": 39.99,
        "image_url": "https://media.istockphoto.com/id/1146833253/photo/barbecue-tools-on-wooden-table-flat-lay-top-view.jpg?s=1024x1024&w=is&k=20&c=8AWu_6dTnu_2vm9P9ZK0v0HOW79ypEcjL04v2XO-BQo=",
        "category": "grilling",
        "availability": "in-stock",
        "rating": 4.7,
        "reviews": 32
    }
]

comments = []

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add session middleware (only once)
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

# Include routers
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

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admintest"

# Function to check if user is authenticated as admin
def is_admin(request: Request):
    return request.session.get("is_admin", False)

# Admin login page
@app.get("/admin/login", include_in_schema=False)
def admin_login_page(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request, "error": None})

# Admin login handler
@app.post("/admin/login", include_in_schema=False)
async def admin_login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        request.session["is_admin"] = True
        return RedirectResponse(url="/admin/dashboard", status_code=303)
    else:
        return templates.TemplateResponse("admin_login.html", {
            "request": request, 
            "error": "Invalid username or password"
        })

# Admin logout
@app.get("/admin/logout", include_in_schema=False)
def admin_logout(request: Request):
    request.session.pop("is_admin", None)
    return RedirectResponse(url="/", status_code=303)

# Admin dashboard
@app.get("/admin/dashboard", include_in_schema=False)
def admin_dashboard(request: Request):
    if not is_admin(request):
        return RedirectResponse(url="/admin/login", status_code=303)
    return templates.TemplateResponse("admin_dashboard.html", {"request": request, "products": products})

@app.get("/", include_in_schema=False)
def home(request: Request):
    images = [f"/uploads/{file.name}" for file in uploads_dir.iterdir() if file.is_file()]
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "images": images, 
        "products": products
    })

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
    return RedirectResponse(url="/comments", status_code=303)

@app.get("/availability/events")
async def get_availability_events():
    # Return a list of availability events
    return [
        {"title": "Available", "start": "2025-03-10"},
        {"title": "Unavailable", "start": "2025-03-11"}
    ]

@app.get("/availability", include_in_schema=False)
def availability_page(request: Request):
    return templates.TemplateResponse("availability.html", {"request": request})

@app.get("/checkout", include_in_schema=False)
def checkout_page(request: Request, product_id: str = None, name: str = None, price: float = None, image_url: str = None):
    # Get today's date for the date picker minimum value
    today_date = datetime.now().strftime("%Y-%m-%d")
    
    # Get product image if available
    product_image = image_url
    if not product_image and product_id and product_id.isdigit():
        # Try to find the product in the products list
        for product in products:
            if product.get("id") == int(product_id):
                product_image = product.get("image_url")
                break
    
    return templates.TemplateResponse("checkout.html", {
        "request": request,
        "product_id": product_id,
        "product_name": name,
        "product_price": price,
        "product_image": product_image,
        "today_date": today_date,
        "paypal_client_id": config.PAYPAL_CLIENT_ID,
        "merchant_email": config.MERCHANT_EMAIL,
        "merchant_name": config.MERCHANT_NAME,
        "paypal_environment": config.PAYPAL_ENVIRONMENT
    })

@app.get("/comments", include_in_schema=False)
def comments_page(request: Request):
    return templates.TemplateResponse("comments.html", {"request": request, "comments": comments})

@app.get("/contact", include_in_schema=False)
def contact_page(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})

@app.get("/home_page", include_in_schema=False)
def home_page_old(request: Request):
    return RedirectResponse(url="/", status_code=301)
    

@app.get("/add_product", include_in_schema=False)
def add_product_form(request: Request):
    if not is_admin(request):
        return RedirectResponse(url="/admin/login", status_code=303)
    return templates.TemplateResponse("add_product.html", {"request": request})

@app.post("/add_product", include_in_schema=False)
async def add_product(
    request: Request,
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    category: str = Form(...),
    availability: str = Form(...),
    file: UploadFile = File(...)
):
    if not is_admin(request):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Generate a unique ID for the new product
    new_id = max([p.get("id", 0) for p in products], default=0) + 1
    
    # Save the uploaded image
    file_location = uploads_dir / file.filename
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
    
    # Create the new product
    new_product = {
        "id": new_id,
        "name": name,
        "description": description,
        "price": float(price),
        "image_url": f"/uploads/{file.filename}",
        "category": category,
        "availability": availability,
        "rating": 4.0,  # Default rating
        "reviews": 0  # Default number of reviews
    }
    
    # Add the product to the list
    products.append(new_product)
    
    return RedirectResponse(url="/", status_code=303)

# Keep the old routes for backward compatibility
@app.get("/availability_page", include_in_schema=False)
def availability_page_old(request: Request):
    return RedirectResponse(url="/availability", status_code=301)

@app.get("/comments_page", include_in_schema=False)
def comments_page_old(request: Request):
    return RedirectResponse(url="/comments", status_code=301)

@app.get("/contact_page", include_in_schema=False)
def contact_page_old(request: Request):
    return RedirectResponse(url="/contact", status_code=301)

@app.post("/api/chatbot", include_in_schema=False)
async def chatbot_api(request: Request):
    data = await request.json()
    user_message = data.get("message", "")
    message_history = data.get("history", [])
    
    if not user_message:
        return JSONResponse({"error": "No message provided"}, status_code=400)
    
    # Process the user message and generate a response
    response = await generate_ai_response(user_message, message_history)
    
    return JSONResponse({
        "response": response,
        "timestamp": datetime.now().isoformat()
    })

async def generate_ai_response(message, history=None):
    """
    Generate a response using an AI model.
    This function uses a simple fallback mechanism if the AI service is unavailable.
    """
    try:
        # Try to get a response from the AI service
        ai_response = await call_ai_service(message, history)
        return ai_response
    except Exception as e:
        print(f"Error calling AI service: {e}")
        # Fall back to rule-based responses if AI service fails
        return generate_rule_based_response(message)

async def call_ai_service(message, history=None):
    """
    Call an external AI service to generate a response.
    This example uses a mock API call. In production, replace with actual API.
    """
    try:
        # This is where you would integrate with an actual AI service like OpenAI
        # For demonstration, we're using a simulated response based on the message content
        
        # Simulate API call delay
        await asyncio.sleep(1)
        
        # Create a context about the cutlery rental business
        context = """
        I am an AI assistant for Cutlery Rental, a premium cutlery rental service.
        We offer high-quality cutlery for weddings, parties, corporate events, and more.
        Our products include silver forks, steak knives, spoons, and complete dining sets.
        Rental prices start from $15 per day for basic sets and go up to $50 per day for premium collections.
        We offer delivery within a 30-mile radius and have a damage protection policy.
        Customers can contact us at (123) 456-7890 or email at info@cutleryrental.com.
        """
        
        # Use message history to provide more context-aware responses
        if history and len(history) > 0:
            # In a real implementation, you would use the history to provide context to the AI model
            # For this example, we'll just check if certain topics were discussed before
            
            # Check if user has asked about products before
            product_questions = [h for h in history if h.get('role') == 'user' and any(word in h.get('content', '').lower() for word in ['product', 'cutlery', 'fork', 'knife', 'spoon'])]
            
            # Check if user has asked about pricing before
            pricing_questions = [h for h in history if h.get('role') == 'user' and any(word in h.get('content', '').lower() for word in ['price', 'cost', 'how much', 'pricing'])]
            
            # If they've asked about both products and pricing, they might be ready to rent
            if product_questions and pricing_questions and 'rent' in message.lower():
                return "Based on your interest in our products and pricing, I think you're ready to make a reservation! You can select items on our website and proceed to checkout. Would you like me to guide you through the process or do you have any other questions before renting?"
        
        # Process the message to generate a relevant response
        if "product" in message.lower() or "cutlery" in message.lower():
            return "We offer a wide range of premium cutlery for rent, including silver forks, steak knives, and complete dining sets. Our most popular items are our Silver Fork Set ($25/day) and Premium Steak Knives ($35/day). Would you like more information about any specific product?"
        
        elif "price" in message.lower() or "cost" in message.lower():
            return "Our rental prices vary based on the quality and quantity of cutlery you need. Basic sets start at $15 per day, while our premium collections go up to $50 per day. We also offer weekly rates with a 20% discount. Can I help you find something specific within your budget?"
        
        elif "delivery" in message.lower() or "shipping" in message.lower():
            return "We offer delivery within a 30-mile radius of our location. Delivery fees start at $10, but we waive the fee for orders over $100. We can also arrange for expedited delivery if you need the items urgently. Would you like to check if your location is within our delivery area?"
        
        elif "reservation" in message.lower() or "book" in message.lower() or "rent" in message.lower():
            return "Making a reservation is easy! You can browse our collection on the website, select the items you want, choose your rental dates, and complete the checkout process. We recommend booking at least 3-5 days in advance, especially for large events. Would you like help with making a reservation?"
        
        elif "return" in message.lower():
            return "Returns are simple. You can either bring the items back to our location by the agreed return date or schedule a pickup (additional fees may apply). All items should be cleaned before return, though we do offer a cleaning service for an additional fee. Is there anything specific about the return process you'd like to know?"
        
        elif "damage" in message.lower() or "broken" in message.lower():
            return "We understand accidents happen! Our damage protection policy covers minor wear and tear. For significant damage or loss, there may be additional charges. You can add our Premium Protection Plan during checkout for $5, which covers up to $200 in potential damages. Would you like more details about our protection plans?"
        
        elif any(greeting in message.lower() for greeting in ["hello", "hi", "hey", "greetings"]):
            return "Hello! Welcome to Cutlery Rental. I'm your virtual assistant, here to help with any questions about our premium cutlery rental service. How can I assist you today?"
        
        elif "thank" in message.lower():
            return "You're very welcome! I'm glad I could help. Is there anything else you'd like to know about our cutlery rental services?"
        
        elif "bye" in message.lower() or "goodbye" in message.lower():
            return "Thank you for chatting with me today! If you have any more questions later, feel free to come back. Have a great day!"
        
        elif "help" in message.lower():
            return "I'd be happy to help! I can provide information about our products, pricing, delivery options, rental process, and more. What specific aspect of our cutlery rental service would you like to learn about?"
        
        else:
            return "Thank you for your message. If you have specific questions about our cutlery rental service, please let me know. I'm here to help!"
            
    except Exception as e:
        print(f"Error in AI service call: {e}")
        raise e

def generate_rule_based_response(message):
    """
    Generate a response based on the user's message using simple rules.
    This is a fallback when the AI service is unavailable.
    """
    message = message.lower()
    
    # Greeting patterns
    if any(greeting in message for greeting in ["hello", "hi", "hey", "greetings"]):
        return "Hello! Welcome to Cutlery Rental. How can I help you today?"
    
    # Questions about products
    if any(word in message for word in ["product", "cutlery", "fork", "knife", "spoon"]):
        return "We offer a wide range of premium cutlery for rent, including silver forks, steak knives, and complete dining sets. You can browse our collection on the home page."
    
    # Questions about pricing
    if any(word in message for word in ["price", "cost", "how much", "pricing"]):
        return "Our rental prices start from $15 per day for basic sets and go up to $50 per day for premium collections. The price depends on the type and quantity of cutlery you need."
    
    # Questions about availability
    if any(word in message for word in ["available", "availability", "when", "date"]):
        return "You can check our availability calendar on the Availability page. Most of our products are available with 2-3 days' notice, but we recommend booking in advance for special occasions."
    
    # Questions about rental process
    if any(word in message for word in ["rent", "book", "order", "process", "how to"]):
        return "Renting is easy! Browse our collection, select the items you want, choose your rental dates, and complete the checkout process. We offer delivery and pickup options."
    
    # Questions about payment
    if any(word in message for word in ["pay", "payment", "credit card", "paypal"]):
        return "We accept various payment methods including credit/debit cards and PayPal. Payment is processed securely at checkout."
    
    # Questions about delivery
    if any(word in message for word in ["deliver", "delivery", "shipping"]):
        return "We offer delivery within a 30-mile radius for a small fee. For larger orders, delivery might be free. You can also pick up your rental items from our location."
    
    # Questions about return
    if any(word in message for word in ["return", "give back"]):
        return "Returns are simple. Just bring the items back to our location by the agreed return date, or we can arrange a pickup for a small fee."
    
    # Questions about damage
    if any(word in message for word in ["damage", "broken", "lost"]):
        return "We have a damage protection policy. Minor wear and tear is covered, but significant damage or loss may incur additional charges. You can add damage protection during checkout."
    
    # Contact information
    if any(word in message for word in ["contact", "phone", "email", "reach", "talk"]):
        return "You can reach us at (123) 456-7890 or email us at info@cutleryrental.com. Our customer service team is available Monday to Friday, 9am to 5pm."
    
    # Default response
    return "Thank you for your message. If you have specific questions about our cutlery rental service, please let me know. I'm here to help!"

# Create a context processor for templates
@app.middleware("http")
async def add_admin_status_to_templates(request: Request, call_next):
    response = await call_next(request)
    if isinstance(response, _TemplateResponse):
        response.context["is_admin"] = is_admin(request)
    return response