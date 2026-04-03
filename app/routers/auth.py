from datetime import datetime, timedelta
import random

from fastapi import APIRouter, Depends, Form, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.requests import Request
from sqlalchemy.orm import Session
from sqlalchemy import or_
from jose import JWTError, jwt
from app.models import user
from app.utils.security import (
    get_hashed_password,
    verify_password,
    create_access_token,
    create_verification_token,
)
from app.utils.email import send_verification_email
from app.core.config import settings
from app.utils.helper import get_user_by_email
from app.core.database import get_db
from app.models.user import User
from templates import templates

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    if request.query_params.get("registered") == "true":
        return templates.TemplateResponse("login.html", {
            "request": request,
            "success": "Registration successful! Please check your email to verify your account."
        })
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/register", response_model=None, response_class=HTMLResponse)
async def register(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    email: str = Form(...),
    password: str = Form(...),
    username: str = Form(...),
    first_name: str = Form(""),
    last_name: str = Form(""),
):
    if db.query(User).filter(User.email == email).first():
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Email already registered"
        })

    if db.query(User).filter(User.username == username).first():
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Username already taken"
        })
    
    print(f"Registering user: {email}, {username}")
    print(f"Password: {password}")

    try:
        hashed_password = get_hashed_password(password)
    except ValueError:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Password is too long (max 72 characters)"
        })
    
    verification_code = random.randint(100000, 999999)
    code_expire_time = datetime.utcnow() + timedelta(minutes=settings.VERIFICATION_TOKEN_EXPIRE_MINUTES)

    db_user = User(
        username=username,
        first_name=first_name,
        last_name=last_name,
        email=email,
        birthdate=None,
        contact_number=None,
        hashed_password=hashed_password,
        is_verified=False,
        verification_code=verification_code,
        code_expire_time=code_expire_time
    )

    print(f"Created user object: {db_user}")
    print(f"Verification code: {db_user.verification_code}, expires at: {db_user.code_expire_time}")
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    background_tasks.add_task(send_verification_email, db_user.email, str(db_user.verification_code))

    return RedirectResponse(url=f"/auth/verify-notice?email={db_user.email}", status_code=303)

@router.post("/login", response_model=None, response_class=HTMLResponse)
async def login(
    request: Request,
    db: Session = Depends(get_db),
    email: str = Form(...),
    password: str = Form(...),
):
    if db is None:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Database connection error"
        })
    
    user = db.query(User).filter(or_(User.email == email, User.username == email)).first()

    if not user:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "User not found"
        })

    if not verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Incorrect password"
        })

    if not user.is_verified:
        return templates.TemplateResponse("verify_notice.html", {
            "request": request,
        })

    access_token = create_access_token(data={"sub": user.email})
    
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return RedirectResponse(url="/", status_code=303)

@router.post("/verify-email", response_class=HTMLResponse, response_model=None)
async def verify_email(
    request: Request,
    db: Session = Depends(get_db), 
    code: str = Form(...),
    email: str = Form(...)
    ):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)
    
    if user.verification_code == int(code) and user.code_expire_time > datetime.utcnow():
        user.is_verified = True
        user.verification_code = None
        user.code_expire_time = None
        db.commit()
        return templates.TemplateResponse("verify_success.html", {"request": request})
    else:
        return templates.TemplateResponse("verify_notice.html", {
            "request": request,
            "email": email,
            "error": "Invalid or expired verification code"
        })

@router.get("/verify-notice", response_class=HTMLResponse)
async def verify_notice(request: Request, email: str):
    return templates.TemplateResponse("verify_notice.html", {"request": request, "email": email})

@router.post("/resend-verification", response_class=HTMLResponse)
async def resend_verification(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    email: str = Form(...)
):
    user = db.query(User).filter(User.email == email).first()

    print(f"Retrieved user: {user}")

    verify_code= random.randint(100000, 999999)
    expire_time= datetime.utcnow() + timedelta(minutes=settings.VERIFICATION_TOKEN_EXPIRE_MINUTES)

    user.verification_code = verify_code
    user.code_expire_time = expire_time
    db.commit()
    print(f"Resending verification email for user: {user.email}, code: {user.verification_code}, expires at: {user.code_expire_time}")
    background_tasks.add_task(send_verification_email, user.email, str(user.verification_code))

    return templates.TemplateResponse("verify_notice.html", {
        "request": request,
        "email": email,
        "success": "Verification email resent!"
    })