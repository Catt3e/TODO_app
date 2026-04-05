# from sys import exc_info
import pytest
from app.services.project_service import (
    create_project,
    get_project_by_id,
    get_all_projects,
    update_project,
)


async def make_project(db, **overrides):
    base = {
        "user_id": 1,
        "title": "Test Project",
        "description": "Test description",
    }
    base.update(overrides)
    return await create_project(db, **base)


# ==================== create_project ====================

@pytest.mark.asyncio
async def test_create_project_success(db_session):
    project = await make_project(db_session)
    assert project.id is not None
    assert project.title == "Test Project"
    assert project.description == "Test description"
    assert project.user_id == 1

@pytest.mark.asyncio
async def test_create_project_no_description(db_session):
    project = await make_project(db_session, description=None)
    assert project.description is None

@pytest.mark.asyncio
async def test_create_project_sets_timestamps(db_session):
    project = await make_project(db_session)
    assert project.created_at is not None
    assert project.updated_at is not None


# ==================== get_project_by_id ====================

@pytest.mark.asyncio
async def test_get_project_by_id_found(db_session):
    created = await make_project(db_session, title="Find Me")
    result = get_project_by_id(db_session, created.id)
    assert result is not None
    assert result.title == "Find Me"

def test_get_project_by_id_not_found(db_session):
    result = get_project_by_id(db_session, project_id=9999)
    assert result is None


# ==================== get_all_projects ====================

@pytest.mark.asyncio
async def test_get_all_projects_returns_only_user_projects(db_session):
    await make_project(db_session, user_id=1, title="P1")
    await make_project(db_session, user_id=1, title="P2")
    await make_project(db_session, user_id=2, title="P3")

    results = get_all_projects(db_session, user_id=1)
    assert len(results) == 2
    assert all(p.user_id == 1 for p in results)

def test_get_all_projects_empty(db_session):
    results = get_all_projects(db_session, user_id=99)
    assert results == []


# ==================== update_project ====================

@pytest.mark.asyncio
async def test_update_project_success(db_session):
    created = await make_project(db_session)
    updated = await update_project(db_session, created.id, {"title": "New Title", "description": "New Desc"})
    assert updated.title == "New Title"
    assert updated.description == "New Desc"

@pytest.mark.asyncio
async def test_update_project_not_found(db_session):
    with pytest.raises(Exception) as exc_info:
        await update_project(db_session, project_id=9999, project_data={"title": "Ghost"})
    assert "Project not found" in str(exc_info.value)

@pytest.mark.asyncio
async def test_update_project_updates_timestamp(db_session):
    created = await make_project(db_session)
    old_ts = created.updated_at
    updated = await update_project(db_session, created.id, {"title": "New"})
    assert updated.updated_at != old_ts