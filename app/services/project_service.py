from sqlalchemy.orm import Session
from app.models.project import Project
from datetime import datetime

def create_project(db: Session, project_data):
    new_project = Project(**project_data.model_dump())
    new_project.created_at = datetime.utcnow().isoformat()
    new_project.updated_at = datetime.utcnow().isoformat()

    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project

def get_project_by_id(db: Session, project_id: int):
    return db.query(Project).filter(Project.id == project_id).first()

def get_all_projects(db: Session, user_id: int):
    return db.query(Project).filter(Project.user_id == user_id).all()

def update_project(db: Session, project_id: int, project_data):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return None
    for key, value in project_data.dict(exclude_unset=True).items():
        setattr(project, key, value)
    project.updated_at = datetime.utcnow().isoformat()
    db.commit()
    db.refresh(project)
    return project