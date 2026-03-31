import datetime
from sqlalchemy import Column, Integer, String, DateTime
from app.core.database import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, index=True)
    task_index = Column(Integer, index=True)
    task_name = Column(String, index=True)
    description = Column(String, index=True)
    due_date = Column(DateTime, index=True)
    status = Column(Integer, default=0) # 0: pending, 1: completed, -1: overdue

    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String,
        default=lambda: datetime.utcnow().isoformat(),
        onupdate=lambda: datetime.utcnow().isoformat()
    )

    def __repr__(self):
        return f"<Task(id={self.id}, project_id={self.project_id}, task_index={self.task_index}, task_name='{self.task_name}', description='{self.description}', due_date='{self.due_date}', status={self.status}, created_at='{self.created_at}', updated_at='{self.updated_at}')>"