import pytest
from datetime import datetime, timedelta
from app.services.task_service import (
    create_task,
    get_task,
    get_project_tasks,
    update_task,
    mark_task_done,
    get_new_task_index,
)
from app.schemas.task import TaskCreate


def make_task(**overrides):
    base = {
        "title": "Test task",
        "task_index": 1,
        "project_id": 1,
        "description": "This is a successful test task",
        "due_date": datetime.utcnow() + timedelta(days=1),
        "status": 0,
    }
    base.update(overrides)
    return TaskCreate(**base)


# ==================== create_task ====================

@pytest.mark.asyncio
async def test_create_task_success(db_session):
    task = await create_task(db_session, make_task())
    assert task is not None
    assert task.title == "Test task"

@pytest.mark.asyncio
async def test_create_task_missing_title(db_session):
    with pytest.raises(Exception) as exc_info:
        await create_task(db_session, make_task(title=""))
    assert "Task title is required" in str(exc_info.value)

@pytest.mark.asyncio
async def test_create_task_duplicate_index(db_session):
    await create_task(db_session, make_task())
    with pytest.raises(Exception) as exc_info:
        await create_task(db_session, make_task())
    assert "Duplicate index" in str(exc_info.value)

@pytest.mark.asyncio
async def test_create_task_invalid_status(db_session):
    with pytest.raises(Exception) as exc_info:
        await create_task(db_session, make_task(status=3))
    assert "Invalid status value" in str(exc_info.value)

@pytest.mark.asyncio
async def test_create_task_due_date_in_past(db_session):
    with pytest.raises(Exception) as exc_info:
        await create_task(db_session, make_task(due_date=datetime.utcnow() - timedelta(days=1)))
    assert "Invalid due date" in str(exc_info.value)

# ==================== get_task ====================

@pytest.mark.asyncio
async def test_get_task_found(db_session):
    created = await create_task(db_session, make_task())
    result = get_task(db_session, created.id)
    assert result is not None
    assert result.id == created.id

def test_get_task_not_found(db_session):
    result = get_task(db_session, task_id=9999)
    assert result is None


# ==================== get_project_tasks ====================

@pytest.mark.asyncio
async def test_get_project_tasks_returns_correct_project(db_session):
    await create_task(db_session, make_task(task_index=1, project_id=1))
    await create_task(db_session, make_task(task_index=2, project_id=1))
    await create_task(db_session, make_task(task_index=1, project_id=2))

    results = get_project_tasks(db_session, project_id=1)
    assert len(results) == 2
    assert all(t.project_id == 1 for t in results)

@pytest.mark.asyncio
async def test_get_project_tasks_empty(db_session):
    results = get_project_tasks(db_session, project_id=99)
    assert results == []


# ==================== update_task ====================

@pytest.mark.asyncio
async def test_update_task_success(db_session):
    created = await create_task(db_session, make_task())
    updated = await update_task(db_session, created.id, make_task(title="Updated Title"))
    assert updated.title == "Updated Title"

@pytest.mark.asyncio
async def test_update_task_not_found(db_session):
    result = await update_task(db_session, task_id=9999, task_data=make_task())
    assert result is None

@pytest.mark.asyncio
async def test_update_task_updates_timestamp(db_session):
    created = await create_task(db_session, make_task())
    old_ts = created.updated_at
    updated = await update_task(db_session, created.id, make_task(title="New"))
    assert updated.updated_at != old_ts


# ==================== mark_task_done ====================

@pytest.mark.asyncio
async def test_mark_task_done_success(db_session):
    created = await create_task(db_session, make_task())
    result = await mark_task_done(db_session, created.id)
    assert result.status == 1

@pytest.mark.asyncio
async def test_mark_task_done_not_found(db_session):
    result = await mark_task_done(db_session, task_id=9999)
    assert result is None


# ==================== get_new_task_index ====================

@pytest.mark.asyncio
async def test_get_new_task_index_empty_project(db_session):
    index = get_new_task_index(db_session, project_id=99)
    assert index == 1

@pytest.mark.asyncio
async def test_get_new_task_index_increments(db_session):
    await create_task(db_session, make_task(task_index=1))
    await create_task(db_session, make_task(task_index=2))
    index = get_new_task_index(db_session, project_id=1)
    assert index == 3