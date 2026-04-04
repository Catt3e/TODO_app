import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from app.services.project_service import (
    create_project,
    get_project_by_id,
    get_all_projects,
    update_project,
)
from app.models.project import Project


# ==================== create_project ====================

@pytest.mark.asyncio
async def test_create_project_success(db_session):
    project = await create_project(db_session, user_id=1, title="Test Project", description="Test desc")
    assert project.id is not None
    assert project.title == "Test Project"
    assert project.description == "Test desc"
    assert project.user_id == 1

@pytest.mark.asyncio
async def test_create_project_no_description(db_session):
    project = await create_project(db_session, user_id=1, title="No Desc Project")
    assert project.description is None

@pytest.mark.asyncio
async def test_create_project_sets_timestamps(db_session):
    project = await create_project(db_session, user_id=1, title="Timestamp Test")
    assert project.created_at is not None
    assert project.updated_at is not None


# ==================== get_project_by_id ====================

def test_get_project_by_id_found(db_session):
    # seed data
    p = Project(user_id=1, title="Find Me", created_at="2024-01-01", updated_at="2024-01-01")
    db_session.add(p)
    db_session.commit()

    result = get_project_by_id(db_session, p.id)
    assert result is not None
    assert result.title == "Find Me"

def test_get_project_by_id_not_found(db_session):
    result = get_project_by_id(db_session, project_id=9999)
    assert result is None


# ==================== get_all_projects ====================

def test_get_all_projects_returns_only_user_projects(db_session):
    # 2 project của user 1, 1 project của user 2
    db_session.add_all([
        Project(user_id=1, title="P1", created_at="2024-01-01", updated_at="2024-01-01"),
        Project(user_id=1, title="P2", created_at="2024-01-01", updated_at="2024-01-01"),
        Project(user_id=2, title="P3", created_at="2024-01-01", updated_at="2024-01-01"),
    ])
    db_session.commit()

    results = get_all_projects(db_session, user_id=1)
    assert len(results) == 2
    assert all(p.user_id == 1 for p in results)

def test_get_all_projects_empty(db_session):
    results = get_all_projects(db_session, user_id=99)
    assert results == []


# ==================== update_project ====================

@pytest.mark.asyncio
async def test_update_project_success(db_session):
    p = Project(user_id=1, title="Old Title", created_at="2024-01-01", updated_at="2024-01-01")
    db_session.add(p)
    db_session.commit()

    updated = await update_project(db_session, p.id, {"title": "New Title", "description": "New Desc"})
    assert updated.title == "New Title"
    assert updated.description == "New Desc"

@pytest.mark.asyncio
async def test_update_project_not_found(db_session):
    result = await update_project(db_session, project_id=9999, project_data={"title": "Ghost"})
    assert result is None

@pytest.mark.asyncio
async def test_update_project_updates_timestamp(db_session):
    p = Project(user_id=1, title="TS Test", created_at="2024-01-01", updated_at="2024-01-01")
    db_session.add(p)
    db_session.commit()
    old_updated_at = p.updated_at

    updated = await update_project(db_session, p.id, {"title": "New"})
    assert updated.updated_at != old_updated_at