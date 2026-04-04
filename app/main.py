from typing import Annotated
from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from jose import JWTError, jwt
from app.core.config import settings
from app.models.user import User
from app.core.database import get_db, init_db
from sqlalchemy.orm import Session
from app.routers import auth, task, project
from templates import templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="./static"), name="static")
app.include_router(auth.router)
app.include_router(project.router)
app.include_router(task.router)

db_dependency = Annotated[Session, Depends(get_db)]

init_db()

@app.get("/", response_class=HTMLResponse)
async def root(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    user = None
    projects = []
    if token:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            email = payload.get("sub")
            if email:
                user = db.query(User).filter(User.email == email).first()
        except JWTError:
            pass
    
    if user:
        from app.services.project_service import get_all_projects
        projects = get_all_projects(db, user_id=user.id)

    # return user's projects and tasks here.
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "user": user, 
        "projects": projects}
        )
    