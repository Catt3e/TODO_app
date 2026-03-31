from fastapi import APIRouter, Depends, Form, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.requests import Request
from sqlalchemy.orm import Session
from jose import JWTError, jwt
# from app.schemas.user import UserCreate, UserLogin, Token, Message
from app.utils.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_verification_token,
)
from app.utils.email import send_verification_email
from app.core.config import settings
from app.utils.helper import get_user_by_email
from app.core.database import TestingSessionLocal
from app.models.user import User
from templates import templates

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/register", response_model=None)
async def register(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(TestingSessionLocal),
    email: str = Form(...),
    password: str = Form(...),
):
    if db.query(User).filter(User.email == email).first():
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Email already registered"
        })

    hashed_password = get_password_hash(password)
    db_user = User(email=email, hashed_password=hashed_password, is_verified=False)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    verify_token = create_verification_token(db_user.email)
    background_tasks.add_task(send_verification_email, db_user.email, verify_token)

    return templates.TemplateResponse("register.html", {
        "request": request,
        "success": "Account created! Please check your email to verify."
    })

@router.get("/verify-email")
async def verify_email(token: str, db: Session = Depends(TestingSessionLocal)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        token_type: str = payload.get("type")
        if email is None or token_type != "verification":
            raise HTTPException(status_code=400, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_verified:
        return {"message": "Email already verified"}

    user.is_verified = True
    db.commit()
    return {"message": "Email verified successfully! You can now log in."}

@router.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    db: Session = Depends(TestingSessionLocal),
    email: str = Form(...),
    password: str = Form(...),
):
    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Incorrect email or password"
        })

    if not user.is_verified:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Please verify your email first"
        })

    access_token = create_access_token(data={"sub": user.email})
    
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response