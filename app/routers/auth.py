from datetime import datetime, timedelta
import random

from fastapi import APIRouter, Depends, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.requests import Request
from sqlalchemy.orm import Session
from app.utils.security import (
    get_hashed_password,
    verify_password,
    create_access_token,
)
from app.utils.email import send_verification_email
from app.core.config import settings
from app.utils.helper import get_user_by_email, get_user_by_username
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

@router.get("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    request.cookies.clear()
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="access_token")
    return response

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
    except ValueError as e:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": str(e)
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
    
    db_user = get_user_by_email(db, email) or get_user_by_username(db, email)

    if not db_user:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "User not found"
        })

    if not verify_password(password, db_user.hashed_password):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Incorrect password"
        })

    if not db_user.is_verified:
        return templates.TemplateResponse("verify_notice.html", {
            "request": request,
        })

    access_token = create_access_token(data={"sub": db_user.email})
    
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response

@router.post("/verify-email", response_class=HTMLResponse, response_model=None)
async def verify_email(
    request: Request,
    db: Session = Depends(get_db), 
    code: str = Form(...),
    email: str = Form(...)
    ):
    db_user = get_user_by_email(db, email)

    if not db_user:
        return RedirectResponse(url="/auth/login", status_code=303)
    
    if db_user.verification_code == int(code) and db_user.code_expire_time > datetime.utcnow():
        db_user.is_verified = True
        db_user.verification_code = None
        db_user.code_expire_time = None
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
    db_user = get_user_by_email(db, email)
    if not db_user:
        return templates.TemplateResponse("verify_notice.html", {
            "request": request,
            "email": email,
            "error": "User not found"
        })

    print(f"Retrieved user: {db_user}")

    verify_code= random.randint(100000, 999999)
    expire_time= datetime.utcnow() + timedelta(minutes=settings.VERIFICATION_TOKEN_EXPIRE_MINUTES)

    db_user.verification_code = verify_code
    db_user.code_expire_time = expire_time
    db.commit()
    print(f"Resending verification email for user: {db_user.email}, code: {db_user.verification_code}, expires at: {db_user.code_expire_time}")
    background_tasks.add_task(send_verification_email, db_user.email, str(db_user.verification_code))

    return templates.TemplateResponse("verify_notice.html", {
        "request": request,
        "email": email,
        "success": "Verification email resent!"
    })