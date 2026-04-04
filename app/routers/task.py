from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.task import Task
from app.services.project_service import get_project_by_id
from app.services.task_service import(
    mark_task_done,
    create_task,
    get_new_task_index,
    update_task
)
from templates import templates
from app.schemas.task import TaskCreate

router = APIRouter(prefix="/project/{project_id}/task", tags=["task"])

@router.post("/{task_id}/mark-done", response_model=None)
async def mark_done(request: Request, task_id: int, db: Session = Depends(get_db)):
    await mark_task_done(db, task_id)
    return RedirectResponse(url="/", status_code=303)

@router.get("/new", response_model=None)
async def new_task(request: Request, project_id: int, db: Session = Depends(get_db)):
    project = get_project_by_id(db, project_id)
    return templates.TemplateResponse("new_task.html", {"request": request, "project": project})

@router.get("/{task_id}/edit", response_model=None)
async def edit_task(request: Request, project_id: int, task_id: int, db: Session = Depends(get_db)):
    project = get_project_by_id(db, project_id)
    task = db.query(Task).filter(Task.id == task_id).first()
    return templates.TemplateResponse("edit_task.html", {"request": request, "project": project, "task": task})

@router.post("/new", response_model=None)
async def new_task(
    request: Request,
    project_id: int,
    db: Session = Depends(get_db),
    title: str = Form(...),
    description: str = Form(None),
    due_date: str = Form(None)
    ):

    index = get_new_task_index(db, project_id)
    task_data={
        "project_id": project_id,
        "task_index": index,
        "title": title,
        "description": description,
        "due_date": due_date
    }

    print(task_data)
    try:
        await create_task(db, TaskCreate(**task_data))
    except ValueError as e:
        return templates.TemplateResponse("new_task.html", {
            "request": request,
            "project": get_project_by_id(db, project_id),
            "error": str(e)
        })
    return RedirectResponse(url="/", status_code=303)

@router.post("/{task_id}/edit", response_model=None)
async def edit_task(
    request: Request,
    project_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    title: str = Form(...),
    description: str = Form(None),
    due_date: str = Form(...)
    ):

    task_index = db.query(Task).filter(Task.id == task_id).first().task_index

    task_data={
        "project_id": project_id,
        "task_index": task_index,
        "title": title,
        "description": description,
        "due_date": due_date,
        }

    print(task_data)
    try:
        await update_task(db, task_id, TaskCreate(**task_data))
    except ValueError as e:
        return templates.TemplateResponse("edit_task.html", {
            "request": request,
            "project": get_project_by_id(db, project_id),
            "task": db.query(Task).filter(Task.id == task_id).first(),
            "error": str(e)
        })
    return RedirectResponse(url="/", status_code=303)