from datetime import datetime

def validate_task_data(task_data):
    due_date = task_data.due_date
    if due_date and due_date < datetime.utcnow():
        print(due_date, datetime.utcnow())
        raise ValueError("Invalid due date")
    if not task_data.task_name:
        raise ValueError("Task name is required")
    if task_data.status not in [-1, 0, 1]:
        raise ValueError("Invalid status value")