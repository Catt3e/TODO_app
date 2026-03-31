from sqlalchemy.orm import Session
from app.models.task import Task
from datetime import datetime
from app.utils.helper import validate_task_data

def create_task(db: Session, task_data):
    validate_task_data(task_data)

    new_task = Task(**task_data.model_dump())
    new_task.created_at = datetime.utcnow().isoformat()
    new_task.updated_at = datetime.utcnow().isoformat()

    index_check(db, task_data.project_id, task_data.task_index)

    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

def get_task(db: Session, task_id: int):
    return db.query(Task).filter(Task.id == task_id).first()

def get_project_tasks(db: Session, project_id: int):
    return db.query(Task).filter(Task.project_id == project_id, Task.status != 2).all()

def update_task(db: Session, task_id: int, task_data):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        return None
    validate_task_data(task_data)
    for key, value in task_data.dict(exclude_unset=True).items():
        setattr(task, key, value)
    task.updated_at = datetime.utcnow().isoformat()
    db.commit()
    db.refresh(task)
    return task

def index_check(db: Session, project_id: int, task_index: int):
    if task_index is None:
        task_index = get_new_task_index(db, project_id)
    elif any(task.task_index == task_index for task in get_project_tasks(db, project_id)):
        raise ValueError("Duplicate index")
    
def get_new_task_index(db: Session, project_id: int):
    tasks = get_project_tasks(db, project_id)
    return max(task.task_index for task in tasks) + 1 if tasks else 1