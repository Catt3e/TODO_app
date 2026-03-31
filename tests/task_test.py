from datetime import datetime, timedelta

from app.services.task_service import create_task
from app.schemas.task import TaskCreate
import pytest

TEMP=TaskCreate(
        project_id=1,
        task_name="Test task",
        task_index=1,
        description="This is a successful test task",
        due_date=None,
        status=0
    )

# Test 1: Successful create test
def test_create_task_success(db_session):
    temp1 = TEMP.model_copy()
    task = create_task(db_session, temp1)

    assert task is not None

# Test 2: Missing required fields
def test_create_task_missing_fields(db_session):
    temp1 = TEMP.model_copy()
    temp1.task_name = None

    with pytest.raises(Exception) as exc_info:
        create_task(db_session, temp1)
    assert "Task name is required" in str(exc_info.value)

# Test 3: Index duplication
def test_create_task_duplicate_index(db_session):
    temp1 = TEMP.model_copy()
    temp2 = TEMP.model_copy()

    create_task(db_session, temp1)
    
    with pytest.raises(Exception) as exc_info:
        create_task(db_session, temp2)
    assert "Duplicate index" in str(exc_info.value)

# Test 4: Invalid status value
def test_create_task_invalid_status(db_session):
    temp1 = TEMP.model_copy()
    temp1.status = 3

    with pytest.raises(Exception) as exc_info:
        create_task(db_session, temp1)
    assert "Invalid status value" in str(exc_info.value)

# Test 5: Due date in the past
def test_create_task_due_date_in_past(db_session):
    temp1 = TEMP.model_copy()
    temp1.due_date = datetime.utcnow() - timedelta(days=1)

    with pytest.raises(Exception) as exc_info:
        create_task(db_session, temp1)
    assert "Invalid due date" in str(exc_info.value)

