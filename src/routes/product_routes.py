from fastapi import APIRouter, Depends, HTTPException, status, Request, File, UploadFile, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Dict, Any, List, Optional

from src.models.product_model import ProductCreate, ProductUpdate, Product
from src.utils.database import (
    get_products, 
    get_product, 
    add_product, 
    update_product, 
    delete_product
)
from src.utils.auth import get_current_user, get_admin_user
from src.config import PRODUCT_IMAGES_DIR

import os
import shutil
from pathlib import Path
from uuid import uuid4

router = APIRouter()
templates = Jinja2Templates(directory="src/templates")

@router.get("/products", response_class=HTMLResponse)
async def products_page(
    request: Request,
    category: Optional[str] = None,
    available: Optional[bool] = None
):
    """Product listing page"""
    products_list = get_products()
    
    # Filter by category if provided
    if category:
        products_list = [p for p in products_list if p.get("category") == category]
    
    # Filter by availability if provided
    if available is not None:
        products_list = [p for p in products_list if p.get("availability") == ("in-stock" if available else "out-of-stock")]
    
    return templates.TemplateResponse(
        "products/index.html",
        {"request": request, "products": products_list}
    )

@router.get("/products/{product_id}", response_class=HTMLResponse)
async def product_detail(
    request: Request,
    product_id: int
):
    """Product detail page"""
    product = get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return templates.TemplateResponse(
        "products/detail.html",
        {"request": request, "product": product}
    )

@router.get("/admin/products", response_class=HTMLResponse)
async def admin_products_page(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_admin_user)
):
    """Admin product management page"""
    products_list = get_products()
    
    return templates.TemplateResponse(
        "admin/products.html",
        {"request": request, "products": products_list, "user": current_user}
    )

@router.get("/admin/products/new", response_class=HTMLResponse)
async def new_product_page(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_admin_user)
):
    """New product page"""
    return templates.TemplateResponse(
        "admin/product_form.html",
        {"request": request, "user": current_user}
    )

@router.post("/admin/products/new", response_class=HTMLResponse)
async def create_product(
    request: Request,
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    category: str = Form(...),
    quantity: int = Form(...),
    image: Optional[UploadFile] = File(None),
    current_user: Dict[str, Any] = Depends(get_admin_user)
):
    """Create a new product"""
    # Process uploaded image if provided
    image_url = None
    if image and image.filename:
        # Create unique filename to avoid collisions
        file_extension = Path(image.filename).suffix
        unique_filename = f"{uuid4()}{file_extension}"
        file_path = PRODUCT_IMAGES_DIR / unique_filename
        
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        # URL for the saved image (relative to static directory)
        image_url = f"/static/images/products/{unique_filename}"
    
    # Create product data
    product_data = {
        "name": name,
        "description": description,
        "price": price,
        "category": category,
        "quantity": quantity,
        "image_url": image_url or "/static/images/products/default.jpg"
    }
    
    # Add product to database
    new_product = add_product(product_data)
    
    return RedirectResponse(
        url=f"/admin/products/{new_product['id']}",
        status_code=status.HTTP_303_SEE_OTHER
    )

@router.get("/admin/products/{product_id}", response_class=HTMLResponse)
async def edit_product_page(
    request: Request,
    product_id: int,
    current_user: Dict[str, Any] = Depends(get_admin_user)
):
    """Edit product page"""
    product = get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return templates.TemplateResponse(
        "admin/product_form.html",
        {"request": request, "product": product, "user": current_user}
    )

@router.post("/admin/products/{product_id}", response_class=HTMLResponse)
async def update_product_handler(
    request: Request,
    product_id: int,
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    category: str = Form(...),
    quantity: int = Form(...),
    availability: str = Form(...),
    image: Optional[UploadFile] = File(None),
    current_user: Dict[str, Any] = Depends(get_admin_user)
):
    """Update a product"""
    # Get existing product
    product = get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Process uploaded image if provided
    image_url = product.get("image_url")  # Use existing image URL by default
    if image and image.filename:
        # Create unique filename to avoid collisions
        file_extension = Path(image.filename).suffix
        unique_filename = f"{uuid4()}{file_extension}"
        file_path = PRODUCT_IMAGES_DIR / unique_filename
        
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        # URL for the saved image (relative to static directory)
        image_url = f"/static/images/products/{unique_filename}"
    
    # Update product data
    product_data = {
        "name": name,
        "description": description,
        "price": price,
        "category": category,
        "quantity": quantity,
        "availability": availability
    }
    
    if image_url:
        product_data["image_url"] = image_url
    
    # Update product in database
    updated_product = update_product(product_id, product_data)
    
    return RedirectResponse(
        url=f"/admin/products/{product_id}?updated=true",
        status_code=status.HTTP_303_SEE_OTHER
    )

@router.get("/admin/products/{product_id}/delete")
async def delete_product_handler(
    request: Request,
    product_id: int,
    current_user: Dict[str, Any] = Depends(get_admin_user)
):
    """Delete a product"""
    product = get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    delete_product(product_id)
    
    return RedirectResponse(
        url="/admin/products?deleted=true",
        status_code=status.HTTP_303_SEE_OTHER
    )

# API endpoints for AJAX requests
@router.get("/api/products")
async def api_get_products(
    category: Optional[str] = None,
    available: Optional[bool] = None
):
    """API endpoint to get products"""
    products_list = get_products()
    
    # Filter by category if provided
    if category:
        products_list = [p for p in products_list if p.get("category") == category]
    
    # Filter by availability if provided
    if available is not None:
        products_list = [p for p in products_list if p.get("availability") == ("in-stock" if available else "out-of-stock")]
    
    return {"products": products_list}

@router.get("/api/products/{product_id}")
async def api_get_product(product_id: int):
    """API endpoint to get a specific product"""
    product = get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {"product": product} 