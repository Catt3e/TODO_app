from datetime import datetime, timedelta
from unittest.mock import patch
from app.models.user import User
from app.models.project import Project
from app.models.task import Task


MOCK_USER = User(id=1, email="test@test.com", username="testuser", is_verified=True)


def seed_project(db, user_id=1, title="Test Project"):
    p = Project(user_id=user_id, title=title, created_at="2024-01-01", updated_at="2024-01-01")
    db.add(p)
    db.commit()
    return p

def seed_task(db, project_id, task_index=1, title="Test Task"):
    t = Task(
        project_id=project_id,
        task_index=task_index,
        title=title,
        status=0,
        due_date=datetime.utcnow() + timedelta(days=1),
        created_at="2024-01-01",
        updated_at="2024-01-01"
    )
    db.add(t)
    db.commit()
    return t


# ==================== GET /project/{id}/task/new ====================

def test_get_new_task_page_success(client, db_session):
    p = seed_project(db_session)
    with patch("app.routers.task.verify_user", return_value=None):
        response = client.get(f"/project/{p.id}/task/new")
    assert response.status_code == 200

def test_get_new_task_page_unauthorized(client, db_session):
    p = seed_project(db_session) 
    with patch("app.routers.task.verify_user", side_effect=ValueError("Unauthorized")):
        response = client.get(f"/project/{p.id}/task/new")
    assert response.status_code == 200
    assert "Unauthorized" in response.text

def test_get_new_task_page_project_not_found(client, db_session):
    with patch("app.routers.task.verify_user", return_value=None):
        response = client.get("/project/9999/task/new")
    assert response.status_code == 200
    assert "Project not found" in response.text


# ==================== POST /project/{id}/task/new ====================

def test_post_new_task_success(client, db_session):
    p = seed_project(db_session)
    with patch("app.routers.task.verify_user", return_value=None):
        response = client.post(f"/project/{p.id}/task/new", data={
            "title": "New Task",
            "description": "Some desc",
            "due_date": (datetime.utcnow() + timedelta(days=1)).isoformat()
        }, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/"

def test_post_new_task_no_due_date(client, db_session):
    p = seed_project(db_session)
    with patch("app.routers.task.verify_user", return_value=None):
        response = client.post(f"/project/{p.id}/task/new", data={
            "title": "No Due Date Task",
        }, follow_redirects=False)
    assert response.status_code == 303

def test_post_new_task_invalid_due_date(client, db_session):
    p = seed_project(db_session)
    with patch("app.routers.task.verify_user", return_value=None):
        response = client.post(f"/project/{p.id}/task/new", data={
            "title": "Past Due Task",
            "due_date": (datetime.utcnow() - timedelta(days=1)).isoformat()
        }, follow_redirects=False)
    assert response.status_code == 200
    assert "Invalid due date" in response.text


# ==================== GET /project/{id}/task/{task_id}/edit ====================

def test_get_edit_task_page_success(client, db_session):
    p = seed_project(db_session)
    t = seed_task(db_session, p.id)
    response = client.get(f"/project/{p.id}/task/{t.id}/edit")
    assert response.status_code == 200

def test_get_edit_task_page_project_not_found(client, db_session):
    response = client.get("/project/9999/task/1/edit")
    assert response.status_code == 200
    assert "Project not found" in response.text

def test_get_edit_task_page_task_not_found(client, db_session):
    p = seed_project(db_session)
    response = client.get(f"/project/{p.id}/task/9999/edit")
    assert response.status_code == 200
    assert "Task not found" in response.text


# ==================== POST /project/{id}/task/{task_id}/edit ====================

def test_post_edit_task_success(client, db_session):
    p = seed_project(db_session)
    t = seed_task(db_session, p.id)
    response = client.post(f"/project/{p.id}/task/{t.id}/edit", data={
        "title": "Updated Task",
        "description": "Updated desc",
        "due_date": (datetime.utcnow() + timedelta(days=2)).isoformat()
    }, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/"

def test_post_edit_task_not_found(client, db_session):
    p = seed_project(db_session)
    response = client.post(f"/project/{p.id}/task/9999/edit", data={
        "title": "Ghost Task",
        "due_date": (datetime.utcnow() + timedelta(days=1)).isoformat()
    }, follow_redirects=False)
    assert response.status_code == 303


# ==================== POST /project/{id}/task/{task_id}/mark-done ====================

def test_mark_done_success(client, db_session):
    p = seed_project(db_session)
    t = seed_task(db_session, p.id)
    with patch("app.routers.task.verify_user", return_value=None):
        response = client.post(f"/project/{p.id}/task/{t.id}/mark-done",
                               follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/"

def test_mark_done_task_not_found(client, db_session):
    p = seed_project(db_session)
    with patch("app.routers.task.verify_user", return_value=None):
        response = client.post(f"/project/{p.id}/task/9999/mark-done",
                               follow_redirects=False)
    assert response.status_code == 200
    assert "Task not found" in response.text

def test_mark_done_unauthorized(client, db_session):
    p = seed_project(db_session)
    t = seed_task(db_session, p.id)
    with patch("app.routers.task.verify_user", side_effect=ValueError("Unauthorized")):
        response = client.post(f"/project/{p.id}/task/{t.id}/mark-done",
                               follow_redirects=False)
    assert response.status_code == 200
    assert "Unauthorized" in response.text