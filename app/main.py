from typing import Annotated
from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from jose import JWTError, jwt
from app.core.config import settings
from app.models.user import User
from requests import session
from app.core.database import get_db, init_db
from sqlalchemy.orm import Session
from app.routers import auth
from templates import templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="./static"), name="static")
app.include_router(auth.router)

db_dependency = Annotated[Session, Depends(get_db)]

init_db()

@app.get("/", response_class=HTMLResponse)
async def root(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    user = None
    if token:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            email = payload.get("sub")
            if email:
                user = db.query(User).filter(User.email == email).first()
        except JWTError:
            pass
    return templates.TemplateResponse("index.html", {"request": request, "user": user})
    