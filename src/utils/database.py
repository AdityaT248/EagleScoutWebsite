import json
import os
import uuid
from datetime import datetime, date
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from src.config import DB_DIR

# Database files
REVIEWS_FILE = DB_DIR / "reviews.json"
CONTACT_FILE = DB_DIR / "contact.json"
PRODUCTS_FILE = DB_DIR / "products.json"
AVAILABILITY_FILE = DB_DIR / "availability.json"
BOOKINGS_FILE = DB_DIR / "bookings.json"
USERS_FILE = DB_DIR / "users.json"

def _ensure_file(filename: Union[str, Path], default_content: Any) -> None:
    """Ensure that a database file exists with default content if needed"""
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            json.dump(default_content, f, indent=2)

def _load_data(filename: Union[str, Path]) -> Any:
    """Load data from a JSON file"""
    _ensure_file(filename, {})
    with open(filename, "r") as f:
        return json.load(f)

def _save_data(filename: Union[str, Path], data: Any) -> None:
    """Save data to a JSON file"""
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

# Product functions
def get_products() -> List[Dict]:
    """Get all products"""
    _ensure_file(PRODUCTS_FILE, {"products": []})
    data = _load_data(PRODUCTS_FILE)
    return data.get("products", [])

def get_product(product_id: int) -> Optional[Dict]:
    """Get a specific product by ID"""
    products = get_products()
    for product in products:
        if product.get("id") == product_id:
            return product
    return None

def add_product(product_data: Dict) -> Dict:
    """Add a new product to the database"""
    _ensure_file(PRODUCTS_FILE, {"products": []})
    data = _load_data(PRODUCTS_FILE)
    products = data.get("products", [])
    
    # Generate new ID
    product_id = max([p.get("id", 0) for p in products], default=0) + 1
    
    new_product = {
        "id": product_id,
        "name": product_data.get("name", ""),
        "description": product_data.get("description", ""),
        "price": product_data.get("price", 0.0),
        "image_url": product_data.get("image_url", ""),
        "category": product_data.get("category", "other"),
        "availability": product_data.get("availability", "in-stock"),
        "quantity": product_data.get("quantity", 1),
        "created_at": datetime.now().isoformat()
    }
    
    products.append(new_product)
    data["products"] = products
    _save_data(PRODUCTS_FILE, data)
    
    return new_product

def update_product(product_id: int, product_data: Dict) -> Optional[Dict]:
    """Update an existing product"""
    _ensure_file(PRODUCTS_FILE, {"products": []})
    data = _load_data(PRODUCTS_FILE)
    products = data.get("products", [])
    
    for i, product in enumerate(products):
        if product.get("id") == product_id:
            products[i].update(product_data)
            products[i]["updated_at"] = datetime.now().isoformat()
            data["products"] = products
            _save_data(PRODUCTS_FILE, data)
            return products[i]
    
    return None

def delete_product(product_id: int) -> bool:
    """Delete a product by ID"""
    _ensure_file(PRODUCTS_FILE, {"products": []})
    data = _load_data(PRODUCTS_FILE)
    products = data.get("products", [])
    
    for i, product in enumerate(products):
        if product.get("id") == product_id:
            del products[i]
            data["products"] = products
            _save_data(PRODUCTS_FILE, data)
            return True
    
    return False

# Reviews functions
def get_reviews(product_id: Optional[int] = None) -> List[Dict]:
    """Get all reviews or reviews for a specific product"""
    _ensure_file(REVIEWS_FILE, {"reviews": []})
    data = _load_data(REVIEWS_FILE)
    reviews = data.get("reviews", [])
    
    if product_id is not None:
        reviews = [r for r in reviews if r.get("product_id") == product_id]
    
    # Sort by date, newest first
    reviews.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    return reviews

def add_review(content: str, author: Optional[str], product_id: Optional[int], rating: Optional[float], image_path: Optional[str] = None) -> Dict:
    """Add a new review to the database"""
    _ensure_file(REVIEWS_FILE, {"reviews": []})
    data = _load_data(REVIEWS_FILE)
    reviews = data.get("reviews", [])
    
    new_review = {
        "id": len(reviews) + 1,
        "content": content,
        "author": author or "Anonymous",
        "product_id": product_id,
        "rating": rating or 5.0,
        "created_at": datetime.now().isoformat(),
        "approved": False  # All reviews start unapproved
    }
    
    if image_path:
        new_review["image_path"] = image_path
    
    reviews.append(new_review)
    data["reviews"] = reviews
    _save_data(REVIEWS_FILE, data)
    
    return new_review

def update_review(review_id: int, update_data: Dict) -> Optional[Dict]:
    """Update a review (for moderation)"""
    _ensure_file(REVIEWS_FILE, {"reviews": []})
    data = _load_data(REVIEWS_FILE)
    reviews = data.get("reviews", [])
    
    for i, review in enumerate(reviews):
        if review.get("id") == review_id:
            reviews[i].update(update_data)
            reviews[i]["updated_at"] = datetime.now().isoformat()
            data["reviews"] = reviews
            _save_data(REVIEWS_FILE, data)
            return reviews[i]
    
    return None

def delete_review(review_id: int) -> bool:
    """Delete a review"""
    _ensure_file(REVIEWS_FILE, {"reviews": []})
    data = _load_data(REVIEWS_FILE)
    reviews = data.get("reviews", [])
    
    for i, review in enumerate(reviews):
        if review.get("id") == review_id:
            del reviews[i]
            data["reviews"] = reviews
            _save_data(REVIEWS_FILE, data)
            return True
    
    return False

def get_product_ratings(product_id: int) -> Dict:
    """Get the average rating and review count for a product"""
    reviews = get_reviews(product_id)
    if not reviews:
        return {"average": 0, "count": 0}
    
    ratings = [r.get("rating", 5.0) for r in reviews if r.get("rating") is not None]
    if not ratings:
        return {"average": 0, "count": 0}
    
    return {
        "average": sum(ratings) / len(ratings),
        "count": len(ratings)
    }

# Availability and Calendar functions
def get_availability(start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict]:
    """Get availability data for a date range"""
    _ensure_file(AVAILABILITY_FILE, {"dates": []})
    data = _load_data(AVAILABILITY_FILE)
    dates = data.get("dates", [])
    
    if start_date and end_date:
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        return [d for d in dates if (
            datetime.fromisoformat(d.get("date", "").replace('Z', '+00:00')) >= start and
            datetime.fromisoformat(d.get("date", "").replace('Z', '+00:00')) <= end
        )]
    
    return dates

def update_availability(date_str: str, status: str, note: Optional[str] = None) -> Dict:
    """Update availability for a specific date"""
    _ensure_file(AVAILABILITY_FILE, {"dates": []})
    data = _load_data(AVAILABILITY_FILE)
    dates = data.get("dates", [])
    
    # Check if date already exists
    for i, d in enumerate(dates):
        if d.get("date") == date_str:
            dates[i]["status"] = status
            if note:
                dates[i]["note"] = note
            dates[i]["updated_at"] = datetime.now().isoformat()
            data["dates"] = dates
            _save_data(AVAILABILITY_FILE, data)
            return dates[i]
    
    # If date doesn't exist, add it
    new_date = {
        "date": date_str,
        "status": status,
        "note": note,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    dates.append(new_date)
    data["dates"] = dates
    _save_data(AVAILABILITY_FILE, data)
    
    return new_date

def is_date_available(date_str: str) -> bool:
    """Check if a specific date is available"""
    _ensure_file(AVAILABILITY_FILE, {"dates": []})
    data = _load_data(AVAILABILITY_FILE)
    dates = data.get("dates", [])
    
    for d in dates:
        if d.get("date") == date_str and d.get("status") == "unavailable":
            return False
    
    return True

# Booking functions
def get_bookings(status: Optional[str] = None) -> List[Dict]:
    """Get all bookings or bookings with a specific status"""
    _ensure_file(BOOKINGS_FILE, {"bookings": []})
    data = _load_data(BOOKINGS_FILE)
    bookings = data.get("bookings", [])
    
    if status:
        bookings = [b for b in bookings if b.get("status") == status]
    
    # Sort by date, newest first
    bookings.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    return bookings

def create_booking(booking_data: Dict) -> Dict:
    """Create a new booking request"""
    _ensure_file(BOOKINGS_FILE, {"bookings": []})
    data = _load_data(BOOKINGS_FILE)
    bookings = data.get("bookings", [])
    
    booking_id = str(uuid.uuid4())
    
    new_booking = {
        "id": booking_id,
        "name": booking_data.get("name", ""),
        "email": booking_data.get("email", ""),
        "phone": booking_data.get("phone", ""),
        "start_date": booking_data.get("start_date", ""),
        "end_date": booking_data.get("end_date", ""),
        "products": booking_data.get("products", []),
        "message": booking_data.get("message", ""),
        "status": "pending",  # pending, approved, rejected, completed
        "created_at": datetime.now().isoformat()
    }
    
    bookings.append(new_booking)
    data["bookings"] = bookings
    _save_data(BOOKINGS_FILE, data)
    
    return new_booking

def update_booking(booking_id: str, update_data: Dict) -> Optional[Dict]:
    """Update a booking"""
    _ensure_file(BOOKINGS_FILE, {"bookings": []})
    data = _load_data(BOOKINGS_FILE)
    bookings = data.get("bookings", [])
    
    for i, booking in enumerate(bookings):
        if booking.get("id") == booking_id:
            bookings[i].update(update_data)
            bookings[i]["updated_at"] = datetime.now().isoformat()
            data["bookings"] = bookings
            _save_data(BOOKINGS_FILE, data)
            return bookings[i]
    
    return None

# Contact functions
def save_contact_message(name: str, email: str, phone: Optional[str], subject: str, message: str) -> Dict:
    """Save a contact message to the database"""
    _ensure_file(CONTACT_FILE, {"messages": []})
    data = _load_data(CONTACT_FILE)
    messages = data.get("messages", [])
    
    new_message = {
        "id": len(messages) + 1,
        "name": name,
        "email": email,
        "phone": phone,
        "subject": subject,
        "message": message,
        "created_at": datetime.now().isoformat()
    }
    
    messages.append(new_message)
    data["messages"] = messages
    _save_data(CONTACT_FILE, data)
    
    return new_message

def get_contact_messages() -> List[Dict]:
    """Get all contact messages"""
    _ensure_file(CONTACT_FILE, {"messages": []})
    data = _load_data(CONTACT_FILE)
    messages = data.get("messages", [])
    
    # Sort by date, newest first
    messages.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    return messages

# User management functions
def get_users() -> List[Dict]:
    """Get all users"""
    _ensure_file(USERS_FILE, {"users": []})
    data = _load_data(USERS_FILE)
    return data.get("users", [])

def get_user(email: str) -> Optional[Dict]:
    """Get a user by email"""
    users = get_users()
    for user in users:
        if user.get("email") == email:
            return user
    return None

def create_user(user_data: Dict) -> Dict:
    """Create a new user"""
    _ensure_file(USERS_FILE, {"users": []})
    data = _load_data(USERS_FILE)
    users = data.get("users", [])
    
    # Check if user already exists
    for user in users:
        if user.get("email") == user_data.get("email"):
            raise ValueError("User with this email already exists")
    
    new_user = {
        "id": str(uuid.uuid4()),
        "name": user_data.get("name", ""),
        "email": user_data.get("email", ""),
        "password_hash": user_data.get("password_hash", ""),  # Should be hashed before calling this function
        "role": user_data.get("role", "user"),  # user, admin
        "created_at": datetime.now().isoformat()
    }
    
    users.append(new_user)
    data["users"] = users
    _save_data(USERS_FILE, data)
    
    # Don't return the password hash
    user_copy = new_user.copy()
    user_copy.pop("password_hash", None)
    
    return user_copy

# Availabilities functions
def get_availabilities(product_id: Optional[int] = None) -> List[Dict]:
    """Get all availabilities or availabilities for a specific product"""
    _ensure_file(AVAILABILITY_FILE, {"availabilities": []})
    data = _load_data(AVAILABILITY_FILE)
    availabilities = data.get("availabilities", [])
    
    if product_id is not None:
        availabilities = [a for a in availabilities if a.get("product_id") == product_id]
    
    return availabilities

def get_availability(availability_id: int) -> Optional[Dict]:
    """Get a specific availability by ID"""
    _ensure_file(AVAILABILITY_FILE, {"availabilities": []})
    data = _load_data(AVAILABILITY_FILE)
    availabilities = data.get("availabilities", [])
    
    for availability in availabilities:
        if availability.get("id") == availability_id:
            return availability
    
    return None

def add_availability(availability_data: Dict) -> Dict:
    """Add a new availability record to the database"""
    _ensure_file(AVAILABILITY_FILE, {"availabilities": []})
    data = _load_data(AVAILABILITY_FILE)
    availabilities = data.get("availabilities", [])
    
    # Generate new ID
    availability_id = max([a.get("id", 0) for a in availabilities], default=0) + 1
    
    new_availability = {
        "id": availability_id,
        "product_id": availability_data.get("product_id"),
        "start_date": availability_data.get("start_date"),
        "end_date": availability_data.get("end_date"),
        "available_quantity": availability_data.get("available_quantity"),
        "created_at": datetime.now().isoformat()
    }
    
    availabilities.append(new_availability)
    data["availabilities"] = availabilities
    _save_data(AVAILABILITY_FILE, data)
    
    return new_availability

def update_availability(availability_id: int, availability_data: Dict) -> Optional[Dict]:
    """Update an existing availability record"""
    _ensure_file(AVAILABILITY_FILE, {"availabilities": []})
    data = _load_data(AVAILABILITY_FILE)
    availabilities = data.get("availabilities", [])
    
    for i, availability in enumerate(availabilities):
        if availability.get("id") == availability_id:
            availabilities[i].update(availability_data)
            availabilities[i]["updated_at"] = datetime.now().isoformat()
            data["availabilities"] = availabilities
            _save_data(AVAILABILITY_FILE, data)
            return availabilities[i]
    
    return None

def delete_availability(availability_id: int) -> bool:
    """Delete an availability record by ID"""
    _ensure_file(AVAILABILITY_FILE, {"availabilities": []})
    data = _load_data(AVAILABILITY_FILE)
    availabilities = data.get("availabilities", [])
    
    for i, availability in enumerate(availabilities):
        if availability.get("id") == availability_id:
            del availabilities[i]
            data["availabilities"] = availabilities
            _save_data(AVAILABILITY_FILE, data)
            return True
    
    return False

# Comments/reviews functions
def get_comments(product_id: Optional[int] = None) -> List[Dict]:
    """Get all comments or comments for a specific product"""
    _ensure_file(REVIEWS_FILE, {"comments": []})
    data = _load_data(REVIEWS_FILE)
    comments = data.get("comments", [])
    
    if product_id is not None:
        comments = [c for c in comments if c.get("product_id") == product_id]
    
    # Sort by date, newest first
    comments.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    return comments

def get_comment(comment_id: int) -> Optional[Dict]:
    """Get a specific comment by ID"""
    _ensure_file(REVIEWS_FILE, {"comments": []})
    data = _load_data(REVIEWS_FILE)
    comments = data.get("comments", [])
    
    for comment in comments:
        if comment.get("id") == comment_id:
            return comment
    
    return None

def add_comment(comment_data: Dict) -> Dict:
    """Add a new comment to the database"""
    _ensure_file(REVIEWS_FILE, {"comments": []})
    data = _load_data(REVIEWS_FILE)
    comments = data.get("comments", [])
    
    # Generate new ID
    comment_id = max([c.get("id", 0) for c in comments], default=0) + 1
    
    new_comment = {
        "id": comment_id,
        "product_id": comment_data.get("product_id"),
        "user_id": comment_data.get("user_id"),
        "user_name": comment_data.get("user_name", "Anonymous"),
        "content": comment_data.get("content", ""),
        "rating": comment_data.get("rating", 5),
        "image_url": comment_data.get("image_url"),
        "created_at": comment_data.get("created_at", datetime.now().isoformat())
    }
    
    comments.append(new_comment)
    data["comments"] = comments
    _save_data(REVIEWS_FILE, data)
    
    return new_comment

def update_comment(comment_id: int, comment_data: Dict) -> Optional[Dict]:
    """Update an existing comment"""
    _ensure_file(REVIEWS_FILE, {"comments": []})
    data = _load_data(REVIEWS_FILE)
    comments = data.get("comments", [])
    
    for i, comment in enumerate(comments):
        if comment.get("id") == comment_id:
            comments[i].update(comment_data)
            if "updated_at" not in comment_data:
                comments[i]["updated_at"] = datetime.now().isoformat()
            data["comments"] = comments
            _save_data(REVIEWS_FILE, data)
            return comments[i]
    
    return None

def delete_comment(comment_id: int) -> bool:
    """Delete a comment by ID"""
    _ensure_file(REVIEWS_FILE, {"comments": []})
    data = _load_data(REVIEWS_FILE)
    comments = data.get("comments", [])
    
    for i, comment in enumerate(comments):
        if comment.get("id") == comment_id:
            del comments[i]
            data["comments"] = comments
            _save_data(REVIEWS_FILE, data)
            return True
    
    return False

# Booking functions
def get_bookings(user_id: Optional[int] = None, product_id: Optional[int] = None) -> List[Dict]:
    """Get all bookings or bookings for a specific user or product"""
    _ensure_file(BOOKINGS_FILE, {"bookings": []})
    data = _load_data(BOOKINGS_FILE)
    bookings = data.get("bookings", [])
    
    if user_id is not None:
        bookings = [b for b in bookings if b.get("user_id") == user_id]
    
    if product_id is not None:
        bookings = [b for b in bookings if any(item.get("product_id") == product_id for item in b.get("items", []))]
    
    # Sort by date, newest first
    bookings.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    return bookings

def get_booking(booking_id: int) -> Optional[Dict]:
    """Get a specific booking by ID"""
    _ensure_file(BOOKINGS_FILE, {"bookings": []})
    data = _load_data(BOOKINGS_FILE)
    bookings = data.get("bookings", [])
    
    for booking in bookings:
        if booking.get("id") == booking_id:
            return booking
    
    return None

def add_booking(booking_data: Dict) -> Dict:
    """Add a new booking to the database"""
    _ensure_file(BOOKINGS_FILE, {"bookings": []})
    data = _load_data(BOOKINGS_FILE)
    bookings = data.get("bookings", [])
    
    # Generate new ID
    booking_id = max([b.get("id", 0) for b in bookings], default=0) + 1
    
    new_booking = {
        "id": booking_id,
        "user_id": booking_data.get("user_id"),
        "start_date": booking_data.get("start_date"),
        "end_date": booking_data.get("end_date"),
        "days": booking_data.get("days", 1),
        "items": booking_data.get("items", []),
        "total_price": booking_data.get("total_price", 0),
        "delivery_address": booking_data.get("delivery_address", ""),
        "notes": booking_data.get("notes", ""),
        "status": booking_data.get("status", "pending"),
        "created_at": datetime.now().isoformat()
    }
    
    bookings.append(new_booking)
    data["bookings"] = bookings
    _save_data(BOOKINGS_FILE, data)
    
    return new_booking

def update_booking(booking_id: int, booking_data: Dict) -> Optional[Dict]:
    """Update an existing booking"""
    _ensure_file(BOOKINGS_FILE, {"bookings": []})
    data = _load_data(BOOKINGS_FILE)
    bookings = data.get("bookings", [])
    
    for i, booking in enumerate(bookings):
        if booking.get("id") == booking_id:
            bookings[i].update(booking_data)
            bookings[i]["updated_at"] = datetime.now().isoformat()
            data["bookings"] = bookings
            _save_data(BOOKINGS_FILE, data)
            return bookings[i]
    
    return None

def delete_booking(booking_id: int) -> bool:
    """Delete a booking by ID"""
    _ensure_file(BOOKINGS_FILE, {"bookings": []})
    data = _load_data(BOOKINGS_FILE)
    bookings = data.get("bookings", [])
    
    for i, booking in enumerate(bookings):
        if booking.get("id") == booking_id:
            del bookings[i]
            data["bookings"] = bookings
            _save_data(BOOKINGS_FILE, data)
            return True
    
    return False

# Contact message functions
def get_contact_messages() -> List[Dict]:
    """Get all contact messages"""
    _ensure_file(CONTACT_FILE, {"messages": []})
    data = _load_data(CONTACT_FILE)
    messages = data.get("messages", [])
    
    # Sort by date, newest first
    messages.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    return messages

def get_contact_message(message_id: int) -> Optional[Dict]:
    """Get a specific contact message by ID"""
    _ensure_file(CONTACT_FILE, {"messages": []})
    data = _load_data(CONTACT_FILE)
    messages = data.get("messages", [])
    
    for message in messages:
        if message.get("id") == message_id:
            return message
    
    return None

def add_contact_message(message_data: Dict) -> Dict:
    """Add a new contact message to the database"""
    _ensure_file(CONTACT_FILE, {"messages": []})
    data = _load_data(CONTACT_FILE)
    messages = data.get("messages", [])
    
    # Generate new ID
    message_id = max([m.get("id", 0) for m in messages], default=0) + 1
    
    new_message = {
        "id": message_id,
        "name": message_data.get("name", ""),
        "email": message_data.get("email", ""),
        "phone": message_data.get("phone"),
        "subject": message_data.get("subject", ""),
        "message": message_data.get("message", ""),
        "status": message_data.get("status", "new"),
        "created_at": message_data.get("created_at", datetime.now().isoformat())
    }
    
    messages.append(new_message)
    data["messages"] = messages
    _save_data(CONTACT_FILE, data)
    
    return new_message

def update_contact_message(message_id: int, message_data: Dict) -> Optional[Dict]:
    """Update an existing contact message"""
    _ensure_file(CONTACT_FILE, {"messages": []})
    data = _load_data(CONTACT_FILE)
    messages = data.get("messages", [])
    
    for i, message in enumerate(messages):
        if message.get("id") == message_id:
            messages[i].update(message_data)
            if "updated_at" not in message_data:
                messages[i]["updated_at"] = datetime.now().isoformat()
            data["messages"] = messages
            _save_data(CONTACT_FILE, data)
            return messages[i]
    
    return None

def delete_contact_message(message_id: int) -> bool:
    """Delete a contact message by ID"""
    _ensure_file(CONTACT_FILE, {"messages": []})
    data = _load_data(CONTACT_FILE)
    messages = data.get("messages", [])
    
    for i, message in enumerate(messages):
        if message.get("id") == message_id:
            del messages[i]
            data["messages"] = messages
            _save_data(CONTACT_FILE, data)
            return True
    
    return False 