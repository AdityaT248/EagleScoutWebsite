from fastapi import APIRouter, Depends, HTTPException, status, Request, Form, File, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Dict, Any, List, Optional
from datetime import datetime
import shutil
from pathlib import Path
from uuid import uuid4

from src.models.comments_model import CommentCreate, CommentUpdate, Comment, CommentResponse, CommentsResponse, ImageUpload
from src.utils.database import (
    get_comments,
    get_comment,
    add_comment,
    update_comment,
    delete_comment,
    get_product
)
from src.utils.auth import get_current_user, get_admin_user
from src.config import COMMENT_IMAGES_DIR

router = APIRouter()
templates = Jinja2Templates(directory="src/templates")

@router.get("/products/{product_id}/comments", response_class=HTMLResponse)
async def comments_page(
    request: Request,
    product_id: int
):
    """Product comments page"""
    # Get product
    product = get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get comments for this product
    comments_list = get_comments(product_id=product_id)
    
    return templates.TemplateResponse(
        "products/comments.html",
        {"request": request, "product": product, "comments": comments_list}
    )

@router.get("/products/{product_id}/comments/new", response_class=HTMLResponse)
async def new_comment_page(
    request: Request,
    product_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """New comment page"""
    # Get product
    product = get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return templates.TemplateResponse(
        "products/comment_form.html",
        {"request": request, "product": product, "user": current_user}
    )

@router.post("/products/{product_id}/comments", response_class=HTMLResponse)
async def create_comment(
    request: Request,
    product_id: int,
    content: str = Form(...),
    rating: int = Form(...),
    image: Optional[UploadFile] = File(None),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new comment"""
    # Get product
    product = get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Validate rating
    if rating < 1 or rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    # Process uploaded image if provided
    image_url = None
    if image and image.filename:
        # Create unique filename to avoid collisions
        file_extension = Path(image.filename).suffix
        unique_filename = f"{uuid4()}{file_extension}"
        file_path = COMMENT_IMAGES_DIR / unique_filename
        
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        # URL for the saved image (relative to static directory)
        image_url = f"/static/images/comments/{unique_filename}"
    
    # Create comment data
    comment_data = {
        "product_id": product_id,
        "user_id": current_user.get("id"),
        "user_name": current_user.get("name"),
        "content": content,
        "rating": rating,
        "image_url": image_url,
        "created_at": datetime.now().isoformat()
    }
    
    # Add comment to database
    new_comment = add_comment(comment_data)
    
    return RedirectResponse(
        url=f"/products/{product_id}/comments?created=true",
        status_code=status.HTTP_303_SEE_OTHER
    )

@router.get("/comments/{comment_id}/edit", response_class=HTMLResponse)
async def edit_comment_page(
    request: Request,
    comment_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Edit comment page"""
    # Get comment
    comment = get_comment(comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Check if user is authorized to edit this comment
    if comment.get("user_id") != current_user.get("id") and not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Not authorized to edit this comment")
    
    # Get product
    product_id = comment.get("product_id")
    product = get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return templates.TemplateResponse(
        "products/comment_edit_form.html",
        {
            "request": request,
            "product": product,
            "comment": comment,
            "user": current_user
        }
    )

@router.post("/comments/{comment_id}/edit", response_class=HTMLResponse)
async def update_comment_handler(
    request: Request,
    comment_id: int,
    content: str = Form(...),
    rating: int = Form(...),
    image: Optional[UploadFile] = File(None),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update a comment"""
    # Get comment
    comment = get_comment(comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Check if user is authorized to edit this comment
    if comment.get("user_id") != current_user.get("id") and not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Not authorized to edit this comment")
    
    # Get product ID for redirection
    product_id = comment.get("product_id")
    
    # Validate rating
    if rating < 1 or rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    # Process uploaded image if provided
    image_url = comment.get("image_url")  # Use existing image URL by default
    if image and image.filename:
        # Create unique filename to avoid collisions
        file_extension = Path(image.filename).suffix
        unique_filename = f"{uuid4()}{file_extension}"
        file_path = COMMENT_IMAGES_DIR / unique_filename
        
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        # URL for the saved image (relative to static directory)
        image_url = f"/static/images/comments/{unique_filename}"
    
    # Update comment data
    comment_data = {
        "content": content,
        "rating": rating,
        "updated_at": datetime.now().isoformat()
    }
    
    if image_url:
        comment_data["image_url"] = image_url
    
    # Update comment in database
    updated_comment = update_comment(comment_id, comment_data)
    
    return RedirectResponse(
        url=f"/products/{product_id}/comments?updated=true",
        status_code=status.HTTP_303_SEE_OTHER
    )

@router.get("/comments/{comment_id}/delete")
async def delete_comment_handler(
    request: Request,
    comment_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete a comment"""
    # Get comment
    comment = get_comment(comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Check if user is authorized to delete this comment
    if comment.get("user_id") != current_user.get("id") and not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
    
    # Get product ID for redirection
    product_id = comment.get("product_id")
    
    # Delete comment
    delete_comment(comment_id)
    
    return RedirectResponse(
        url=f"/products/{product_id}/comments?deleted=true",
        status_code=status.HTTP_303_SEE_OTHER
    )

# Admin routes
@router.get("/admin/comments", response_class=HTMLResponse)
async def admin_comments_page(
    request: Request,
    product_id: Optional[int] = None,
    current_user: Dict[str, Any] = Depends(get_admin_user)
):
    """Admin comments page"""
    # Get comments
    comments_list = get_comments(product_id=product_id)
    
    # Get product if product_id is provided
    product = None
    if product_id:
        product = get_product(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
    
    return templates.TemplateResponse(
        "admin/comments.html",
        {
            "request": request,
            "comments": comments_list,
            "product": product,
            "user": current_user
        }
    )

# API endpoints for AJAX requests
@router.get("/api/products/{product_id}/comments")
async def api_get_product_comments(product_id: int):
    """API endpoint to get comments for a product"""
    # Get product
    product = get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get comments for this product
    comments_list = get_comments(product_id=product_id)
    
    return CommentsResponse(
        product_id=product_id,
        comments=[CommentResponse(**comment) for comment in comments_list]
    )

@router.post("/api/products/{product_id}/comments")
async def api_create_comment(
    product_id: int,
    comment: CommentCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """API endpoint to create a new comment"""
    # Get product
    product = get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Create comment data
    comment_data = {
        "product_id": product_id,
        "user_id": current_user.get("id"),
        "user_name": current_user.get("name"),
        "content": comment.content,
        "rating": comment.rating,
        "created_at": datetime.now().isoformat()
    }
    
    # Add comment to database
    new_comment = add_comment(comment_data)
    
    return CommentResponse(**new_comment)

@router.post("/api/comments/{comment_id}/images")
async def api_upload_comment_image(
    comment_id: int,
    image: ImageUpload,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """API endpoint to upload an image for a comment"""
    # Get comment
    comment = get_comment(comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Check if user is authorized to edit this comment
    if comment.get("user_id") != current_user.get("id") and not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Not authorized to edit this comment")
    
    # Create unique filename to avoid collisions
    image_data = image.image
    
    # Save image data to file
    file_extension = ".jpg"  # Default extension
    unique_filename = f"{uuid4()}{file_extension}"
    file_path = COMMENT_IMAGES_DIR / unique_filename
    
    # Save image data to file
    with open(file_path, "wb") as f:
        f.write(image_data)
    
    # URL for the saved image (relative to static directory)
    image_url = f"/static/images/comments/{unique_filename}"
    
    # Update comment with image URL
    update_comment(comment_id, {"image_url": image_url})
    
    return {"image_url": image_url}