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
    update_task,
    get_task
)
from templates import templates
from app.schemas.task import TaskCreate
from app.utils.helper import get_verified_user

router = APIRouter(prefix="/project/{project_id}/task", tags=["task"])

def verify_user(db: Session, project_id: int, request: Request):

    project = get_project_by_id(db, project_id)
    user = get_verified_user(request, db)
    if not user:
        raise ValueError("Unauthorized")
    if project.user_id != user.id:
        raise ValueError("Unauthorized")

@router.post("/{task_id}/mark-done", response_model=None)
async def mark_done(request: Request, task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        return templates.TemplateResponse("index.html", {"request": request, "error": "Task not found"})
    try:
        verify_user(db, task.project_id, request)
    except ValueError:
        return templates.TemplateResponse("index.html", {"request": request, "error": "Unauthorized"})
    await mark_task_done(db, task_id)
    return RedirectResponse(url="/", status_code=303)

@router.get("/new", response_model=None)
async def new_task(request: Request, project_id: int, db: Session = Depends(get_db)):
    try:
        verify_user(db, project_id, request)
        project = get_project_by_id(db, project_id)
    except ValueError as e:
        error = "Unauthorized" if "Unauthorized" in str(e) else "Project not found"
        return templates.TemplateResponse("new_task.html", {"request": request, "error": error})
    return templates.TemplateResponse("new_task.html", {"request": request, "project": project})

@router.get("/{task_id}/edit", response_model=None)
async def edit_task(request: Request, project_id: int, task_id: int, db: Session = Depends(get_db)):
    try:
        project = get_project_by_id(db, project_id)
    except Exception:
        return templates.TemplateResponse("edit_task.html", {"request": request, "error": "Project not found"})
    task = get_task(db, task_id)
    if not task:
        return templates.TemplateResponse("edit_task.html", {"request": request, "error": "Task not found"})
    return templates.TemplateResponse("edit_task.html", {"request": request, "project": project, "task": task})

@router.post("/new", response_model=None)
async def post_new_task(
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
        print(str(e))
        return templates.TemplateResponse("new_task.html", {
            "request": request,
            "project": get_project_by_id(db, project_id),
            "error": str(e)
        })
    return RedirectResponse(url="/", status_code=303)

@router.post("/{task_id}/edit", response_model=None)
async def post_edit_task(
    request: Request,
    project_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    title: str = Form(...),
    description: str = Form(None),
    due_date: str = Form(...)
    ):

    task = get_task(db, task_id)
    if not task:
        return RedirectResponse(url="/", status_code=303)

    task_data={
        "project_id": project_id,
        "task_index": task.task_index,
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
            "task": task,
            "error": str(e)
        })
    return RedirectResponse(url="/", status_code=303)