"""
Модуль управления задачами (Tasks)
"""

from my_tasks.models import Task, TaskAssignment, TaskStatus, TaskPriority
from my_tasks.schemas import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
    TaskFilterParams,
    TaskStatistics,
    TaskAssignmentResponse,
    AddAssigneeRequest,
    RemoveAssigneeRequest,
    BulkAssignRequest,
    TaskStatusUpdate,
    PaginationParams,
    TaskFilterDependency
)
from my_tasks.dep import (
    create_task,
    get_task_by_id,
    get_tasks,
    update_task,
    delete_task,
    add_assignee,
    remove_assignee,
    bulk_assign,
    get_user_task_statistics,
    get_overdue_tasks
)

__all__ = [
    # Models
    "Task",
    "TaskAssignment",
    "TaskStatus",
    "TaskPriority",
    
    # Schemas
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "TaskListResponse",
    "TaskFilterParams",
    "TaskStatistics",
    "TaskAssignmentResponse",
    "AddAssigneeRequest",
    "RemoveAssigneeRequest",
    "BulkAssignRequest",
    "TaskStatusUpdate",
    "PaginationParams",
    "TaskFilterDependency",
    
    # Functions
    "create_task",
    "get_task_by_id",
    "get_tasks",
    "update_task",
    "delete_task",
    "add_assignee",
    "remove_assignee",
    "bulk_assign",
    "get_user_task_statistics",
    "get_overdue_tasks",
]
