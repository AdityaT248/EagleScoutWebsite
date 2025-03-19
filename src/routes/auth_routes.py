from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from datetime import timedelta
from typing import Dict, Any

from src.models.user_model import UserCreate, User, UserLogin
from src.utils.auth import (
    authenticate_user, 
    create_access_token, 
    get_password_hash,
    get_current_user,
    get_admin_user
)
from src.utils.database import get_user, create_user
from src.config import JWT_EXPIRATION_MINUTES

router = APIRouter()
templates = Jinja2Templates(directory="src/templates")

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Get an access token for authentication"""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(minutes=JWT_EXPIRATION_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    return templates.TemplateResponse("auth/login.html", {"request": request})

@router.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    response: Response,
    user_login: UserLogin
):
    """Process login form"""
    user = authenticate_user(user_login.email, user_login.password)
    if not user:
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "Invalid email or password"}
        )
    
    access_token_expires = timedelta(minutes=JWT_EXPIRATION_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    
    # Set cookie with JWT token
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=JWT_EXPIRATION_MINUTES * 60,
        samesite="lax",
    )
    
    return response

@router.get("/logout")
async def logout():
    """Log out user by clearing cookie"""
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(key="access_token")
    return response

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Registration page"""
    return templates.TemplateResponse("auth/register.html", {"request": request})

@router.post("/register", response_class=HTMLResponse)
async def register(
    request: Request,
    user_create: UserCreate
):
    """Process registration form"""
    # Check if user already exists
    existing_user = get_user(user_create.email)
    if existing_user:
        return templates.TemplateResponse(
            "auth/register.html",
            {"request": request, "error": "Email already registered"}
        )
    
    # Hash password and create user
    hashed_password = get_password_hash(user_create.password)
    user_data = user_create.dict()
    user_data["password_hash"] = hashed_password
    user_data.pop("password")
    user_data["role"] = "user"  # Default role
    
    try:
        new_user = create_user(user_data)
        return RedirectResponse(url="/login?registered=true", status_code=303)
    except Exception as e:
        return templates.TemplateResponse(
            "auth/register.html",
            {"request": request, "error": f"Registration error: {str(e)}"}
        )

@router.get("/profile", response_class=HTMLResponse)
async def profile(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """User profile page"""
    return templates.TemplateResponse(
        "auth/profile.html",
        {"request": request, "user": current_user}
    ) 