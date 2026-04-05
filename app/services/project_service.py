from sqlalchemy.orm import Session
from app.models.project import Project
from datetime import datetime

async def create_project(db: Session, user_id: int, title: str, description: str = None):
    new_project = Project(
        user_id=user_id,
        title=title,
        description=description,
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat()
    )

    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project

def get_project_by_id(db: Session, project_id: int):
    return db.query(Project).filter(Project.id == project_id).first()

def get_all_projects(db: Session, user_id: int):
    return db.query(Project).filter(Project.user_id == user_id).all()

async def update_project(db: Session, project_id: int, project_data):
    project = get_project_by_id(db, project_id)
    if not project:
        raise ValueError("Project not found")
    for key, value in project_data.items():
        setattr(project, key, value)
    project.updated_at = datetime.utcnow().isoformat()
    db.commit()
    db.refresh(project)
    return project