from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from app.core.config import Settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=Settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, Settings.SECRET_KEY, algorithm=Settings.ALGORITHM)

def create_verification_token(email: str) -> str:
    expires_delta = timedelta(minutes=Settings.VERIFICATION_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": email, "type": "verification"}
    return create_access_token(to_encode, expires_delta)