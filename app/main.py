from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.core.database import TestingSessionLocal
from fastapi import status
from app.routers import auth
from templates import templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="./static"), name="static")

app.include_router(auth.router)

def get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[TestingSessionLocal, Depends(get_db)]

@app.get("/")
async def read_root():
    return {"message": "Welcome to the TODO app API!"}

@app.get("/", status_code=status.HTTP_200_OK)
async def user(user: None, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return {"User": user}