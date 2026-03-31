from app.core.database import Base
from sqlalchemy import Boolean, Column, Integer, String

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    is_verified = Column(Boolean, default=0)

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}', is_verified={self.is_verified})>"