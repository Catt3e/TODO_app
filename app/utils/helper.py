from datetime import datetime
from requests import Session
from app.models.user import User

def validate_task_data(task_data):
    due_date = task_data.due_date
    if due_date and due_date < datetime.utcnow():
        print(due_date, datetime.utcnow())
        raise ValueError("Invalid due date")
    if not task_data.task_name:
        raise ValueError("Task name is required")
    if task_data.status not in [-1, 0, 1]:
        raise ValueError("Invalid status value")

    
def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()