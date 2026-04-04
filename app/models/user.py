from app.core.database import Base
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    birthdate = Column(String, nullable=True)
    contact_number = Column(String, nullable=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_verified = Column(Boolean, default=False)

    verification_code = Column(Integer, nullable=True, default=None)
    code_expire_time = Column(DateTime, nullable=True, default=None)

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}', is_verified={self.is_verified})>"
    
    projects = relationship("Project", back_populates="owner")