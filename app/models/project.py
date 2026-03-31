from sqlalchemy import Column, Integer, String
from tomlkit import datetime
from app.core.database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    user_id = Column(Integer, index=True)
    description = Column(String, index=True)
    status = Column(String, index=True)

    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String,
        default=lambda: datetime.utcnow().isoformat(),
        onupdate=lambda: datetime.utcnow().isoformat()
    )

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', user_id={self.user_id}, description='{self.description}', status='{self.status}', created_at='{self.created_at}', updated_at='{self.updated_at}')>"