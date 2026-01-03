"""src.services.task_store
Simple in-memory task store for tracking wiki generation status.
"""

import uuid
from typing import Any, Literal

from pydantic import BaseModel

TaskId = str
TaskStatus = Literal["in_progress", "completed", "failed"]


class Task(BaseModel):
    task_id: TaskId
    status: TaskStatus = "in_progress"
    result: Any = None


# In-memory storage for tasks.
# NOTE: This is not suitable for production with multiple workers.
# For that, a shared storage like Redis or a database would be needed.
tasks: dict[TaskId, Task] = {}


def create_task(initial_message: str = "Task started.") -> Task:
    """Creates a new task and stores it."""
    task_id = str(uuid.uuid4())
    task = Task(task_id=task_id, result=initial_message)
    tasks[task_id] = task
    return task


def get_task(task_id: TaskId) -> Task | None:
    """Retrieves a task from storage."""
    return tasks.get(task_id)


def update_task_status(task_id: TaskId, status: TaskStatus, result: Any = None):
    """Updates the status and result of a task."""
    task = get_task(task_id)
    if task:
        task.status = status
        task.result = result
    else:
        print(f"Warning: Task ID {task_id} not found for update.")
