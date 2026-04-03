from pydantic import BaseModel, EmailStr
# from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    hashed_password: str
    first_name: str
    last_name: str
    birthdate: str
    contact_number: str
    verification_code: int
    code_expire_time: str

class UserLogin(BaseModel):
    email: EmailStr
    username: str
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class Message(BaseModel):
    message: str