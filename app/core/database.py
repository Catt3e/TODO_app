from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

Base = declarative_base()

def init_db():
    Base.metadata.create_all(bind=engine)