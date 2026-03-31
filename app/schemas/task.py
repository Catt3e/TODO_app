from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TaskBase(BaseModel):
    task_name: str
    project_id: int
    task_index: int
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    status: Optional[int] = 0 # 0: pending, 1: completed, -1: overdue

class TaskCreate(TaskBase):
    pass

class TaskUpdate(TaskBase):
    pass

class TaskResponse(TaskBase):
    id: int
    created_at: str
    updated_at: str
    deleted_at: Optional[str] = None

    class Config:
        orm_mode = True