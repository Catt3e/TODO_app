from datetime import datetime
from requests import Session
from app.models.user import User
from jose import JWTError, jwt
from app.core.config import settings
from fastapi import Request

from app.schemas.task import TaskCreate

def validate_task_data(task_data: TaskCreate):
    if not task_data.title or task_data.title.strip() == "":
        raise ValueError("Task title is required")
    if task_data.status not in [-1, 0, 1]:
        raise ValueError("Invalid status value")
    if task_data.due_date and task_data.due_date < datetime.utcnow():
        raise ValueError("Invalid due date")

    
def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()

def get_verified_user(request: Request, db: Session) -> User | None:
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")
        if email is None:
            return None
        user = get_user_by_email(db, email)
        return user
    except JWTError:
        return None