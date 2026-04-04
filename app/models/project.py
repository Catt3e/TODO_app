from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
import datetime

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    description = Column(String, index=True)
    # status = Column(String, index=True)

    created_at = Column(String, default=lambda: datetime.datetime.now(datetime.UTC).isoformat())
    updated_at = Column(String,
        default=lambda: datetime.datetime.now(datetime.UTC).isoformat(),
        onupdate=lambda: datetime.datetime.now(datetime.UTC).isoformat()
    )

    def __repr__(self):
        return f"<Project(id={self.id}, title='{self.title}', user_id={self.user_id}, description='{self.description}', status='{self.status}', created_at='{self.created_at}', updated_at='{self.updated_at}')>"
    
    owner = relationship("User", back_populates="projects")
    tasks = relationship("Task", back_populates="project")

    def get_summary(self):
        string_summary = f"Project progress: finished {self.get_finished_tasks()} tasks out of {self.get_total_tasks()}."
        return string_summary

    def get_total_tasks(self):
        return len(self.tasks)
    
    def get_finished_tasks(self):
        return len([task for task in self.tasks if task.status == 1])
    
    def get_progress(self):
        total_tasks = self.get_total_tasks()
        if total_tasks == 0:
            return 0
        finished_tasks = self.get_finished_tasks()
        return int((finished_tasks / total_tasks) * 100)
    
    def get_status(self):
        progress = self.get_progress()
        if progress == 100:
            return "Completed"
        elif progress > 0:
            return "In Progress"
        else:
            return "Not Started"