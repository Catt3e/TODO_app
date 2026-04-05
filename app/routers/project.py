from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
# from templates import templates
from app.services.project_service import(
    create_project,
    get_project_by_id,
    update_project,
) 
from app.utils.helper import get_verified_user

router = APIRouter(prefix="/project", tags=["project"])

# @router.get("/new", response_model=None)
# async def new_project(request: Request):
#     return templates.TemplateResponse("new_project.html", {"request": request})

@router.post("/new", response_model=None)
async def new_project(
    request: Request,
    db: Session = Depends(get_db),
    title: str = Form(...),
    description: str = Form(None)
    ):

    user = get_verified_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    try:
        await create_project(db, user_id=user.id, title=title, description=description)
    except Exception as e:
        print(f"Error creating project: {e}")
    return RedirectResponse(url="/", status_code=303)

@router.post("/{project_id}/edit", response_model=None)
async def edit_project(
    request: Request,
    db: Session = Depends(get_db),
    title: str = Form(...),
    description: str = Form(None)
    ):
    try:
        print("At router, before getting user")
        user = get_verified_user(request, db)
    except Exception as e:
        print(f"Error occurred while verifying user: {e}")
        return RedirectResponse(url="/auth/login", status_code=303)

    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)
    
    project_id = request.path_params["project_id"]
    try:
        get_project_by_id(db, project_id)
    except ValueError as e:
        print(f"Error occurred while fetching project: {e}")
        return RedirectResponse(url="/", status_code=303)
    
    project_data = {
        "title": title,
        "description": description
    }

    print("At router:" + str(project_data))

    try:
        await update_project(db, project_id, project_data=project_data)
    except ValueError as e:
        print(f"Error occurred while updating project: {e}")
    return RedirectResponse(url="/", status_code=303)