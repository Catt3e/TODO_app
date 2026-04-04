from pydantic import BaseModel
from typing import Optional

class ProjectBase(BaseModel):
    title: str
    user_id: int
    description: Optional[str] = None
    # status: Optional[int] = 0 # 0: active, 1: archived, -1: deleted

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: int
    created_at: str
    updated_at: str

    class Config:
        orm_mode = True