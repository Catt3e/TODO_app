from unittest.mock import patch
from app.models.user import User
from app.models.project import Project


MOCK_USER = User(id=1, email="test@test.com", username="testuser", is_verified=True)



# ==================== POST /project/new ====================

def test_create_project_success(client):
    with patch("app.routers.project.get_verified_user", return_value=MOCK_USER):
        response = client.post("/project/new", data={
            "title": "Test Project",
            "description": "Test desc"
        }, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/"

def test_create_project_no_auth(client):
    with patch("app.routers.project.get_verified_user", return_value=None):
        response = client.post("/project/new", data={
            "title": "Test Project",
        }, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/auth/login"

def test_create_project_no_description(client):
    with patch("app.routers.project.get_verified_user", return_value=MOCK_USER):
        response = client.post("/project/new", data={
            "title": "No Desc Project"
        }, follow_redirects=False)
    assert response.status_code == 303


# ==================== POST /project/{id}/edit ====================

def test_edit_project_success(client, db_session):
    # seed project
    p = Project(user_id=1, title="Old Title")
    db_session.add(p)
    db_session.commit()

    with patch("app.routers.project.get_verified_user", return_value=MOCK_USER):
        response = client.post(f"/project/{p.id}/edit", data={
            "title": "New Title",
            "description": "New Desc"
        }, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/"

def test_edit_project_no_auth(client, db_session):
    p = Project(user_id=1, title="Old Title", created_at="2024-01-01", updated_at="2024-01-01")
    db_session.add(p)
    db_session.commit()

    with patch("app.routers.project.get_verified_user", return_value=None):
        response = client.post(f"/project/{p.id}/edit", data={
            "title": "New Title"
        }, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/auth/login"

def test_edit_project_wrong_owner(client, db_session):
    # project thuộc user 2, nhưng mock user là user 1
    p = Project(user_id=2, title="Not Mine", created_at="2024-01-01", updated_at="2024-01-01")
    db_session.add(p)
    db_session.commit()

    with patch("app.routers.project.get_verified_user", return_value=MOCK_USER):
        response = client.post(f"/project/{p.id}/edit", data={
            "title": "Hacked"
        }, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/"

def test_edit_project_not_found(client):
    with patch("app.routers.project.get_verified_user", return_value=MOCK_USER):
        response = client.post("/project/9999/edit", data={
            "title": "Ghost"
        }, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/"