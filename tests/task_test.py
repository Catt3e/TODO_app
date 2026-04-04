import pytest
from datetime import datetime, timedelta
from app.services.task_service import create_task
from app.schemas.task import TaskCreate


def make_task(**overrides):
    base = {
        "title": "Test task",
        "task_index": 1,
        "project_id": 1,
        "description": "This is a successful test task",
        "due_date": datetime.utcnow() + timedelta(days=1),
    }
    base.update(overrides)
    return TaskCreate(**base)


# Test 1: Successful create
@pytest.mark.asyncio
async def test_create_task_success(db_session):
    task = await create_task(db_session, make_task())
    assert task is not None
    assert task.title == "Test task"

# Test 2: Missing required fields
@pytest.mark.asyncio
async def test_create_task_missing_fields(db_session):
    with pytest.raises(Exception) as exc_info:
        await create_task(db_session, make_task(title=None))
    assert "Task title is required" in str(exc_info.value)

# Test 3: Duplicate index
@pytest.mark.asyncio
async def test_create_task_duplicate_index(db_session):
    await create_task(db_session, make_task())
    with pytest.raises(Exception) as exc_info:
        await create_task(db_session, make_task())
    assert "Duplicate index" in str(exc_info.value)

# Test 4: Invalid status
@pytest.mark.asyncio
async def test_create_task_invalid_status(db_session):
    with pytest.raises(Exception) as exc_info:
        await create_task(db_session, make_task(status=3))
    assert "Invalid status value" in str(exc_info.value)

# Test 5: Due date in the past
@pytest.mark.asyncio
async def test_create_task_due_date_in_past(db_session):
    with pytest.raises(Exception) as exc_info:
        await create_task(db_session, make_task(due_date=datetime.utcnow() - timedelta(days=1)))
    assert "Invalid due date" in str(exc_info.value)