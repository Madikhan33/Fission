from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
from fastapi import Query
from my_tasks.models import TaskStatus, TaskPriority


# ============================================
# User Schemas (для вложенных данных)
# ============================================

class UserBrief(BaseModel):
    """Краткая информация о пользователе"""
    id: int
    username: str
    email: str
    
    class Config:
        from_attributes = True


# ============================================
# Task Assignment Schemas
# ============================================

class TaskAssignmentBase(BaseModel):
    """Базовая схема назначения"""
    user_id: int


class TaskAssignmentCreate(TaskAssignmentBase):
    """Схема для создания назначения"""
    pass


class TaskAssignmentResponse(BaseModel):
    """Схема ответа для назначения"""
    task_id: int
    user_id: int
    assigned_at: datetime
    assigned_by_id: Optional[int] = None
    user: UserBrief
    
    class Config:
        from_attributes = True


# ============================================
# Task Schemas
# ============================================

class TaskBase(BaseModel):
    """Базовая схема задачи"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None
    room_id: Optional[int] = None


class TaskCreate(TaskBase):
    """Схема для создания задачи"""
    assignee_ids: list[int] = Field(
        default_factory=list, 
        description="Список ID ответственных. Если не указан или пустой, создатель автоматически становится ответственным",
        examples=[[1, 2, 3], []]
    )
    
    @field_validator('assignee_ids')
    @classmethod
    def filter_invalid_ids(cls, v: list[int]) -> list[int]:
        """Фильтруем невалидные ID (0 и отрицательные)"""
        if v is None:
            return []
        # Убираем 0 и отрицательные ID
        return [id for id in v if id > 0]
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Разработать новую функцию",
                "description": "Добавить экспорт в Excel",
                "status": "todo",
                "priority": "high",
                "due_date": "2025-12-01T12:00:00",
                "assignee_ids": []  # Пустой массив - создатель станет ответственным
            }
        }


class TaskUpdate(BaseModel):
    """Схема для обновления задачи"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None


class TaskResponse(TaskBase):
    """Схема ответа для задачи"""
    id: int
    created_by_id: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    created_by: UserBrief
    assignments: list[TaskAssignmentResponse] = []
    
    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Схема для списка задач с пагинацией"""
    tasks: list[TaskResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================
# Task Filter Schemas
# ============================================

class TaskFilterParams(BaseModel):
    """Параметры фильтрации задач"""
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignee_id: Optional[int] = None
    created_by_id: Optional[int] = None
    room_id: Optional[int] = None
    is_overdue: Optional[bool] = None
    search: Optional[str] = None  # Поиск по названию и описанию


# ============================================
# Dependency Classes для Query параметров
# ============================================

class PaginationParams:
    """
    Dependency класс для параметров пагинации
    
    Использование:
        @router.get("/tasks/")
        async def get_tasks(pagination: PaginationParams = Depends()):
            ...
    """
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Номер страницы"),
        page_size: int = Query(20, ge=1, le=100, description="Размер страницы")
    ):
        self.page = page
        self.page_size = page_size
        self.skip = (page - 1) * page_size
        self.limit = page_size


class TaskFilterDependency:
    """
    Dependency класс для параметров фильтрации задач
    
    Использование:
        @router.get("/tasks/")
        async def get_tasks(filters: TaskFilterDependency = Depends()):
            ...
    """
    def __init__(
        self,
        status: Optional[TaskStatus] = Query(None, description="Фильтр по статусу"),
        priority: Optional[TaskPriority] = Query(None, description="Фильтр по приоритету"),
        assignee_id: Optional[int] = Query(None, description="Фильтр по ответственному"),
        created_by_id: Optional[int] = Query(None, description="Фильтр по создателю"),
        room_id: Optional[int] = Query(None, description="Фильтр по комнате"),
        is_overdue: Optional[bool] = Query(None, description="Только просроченные"),
        search: Optional[str] = Query(None, description="Поиск по названию и описанию")
    ):
        self.status = status
        self.priority = priority
        self.assignee_id = assignee_id
        self.created_by_id = created_by_id
        self.room_id = room_id
        self.is_overdue = is_overdue
        self.search = search
    
    def to_filter_params(self) -> TaskFilterParams:
        """Конвертировать в TaskFilterParams для использования в функциях"""
        return TaskFilterParams(
            status=self.status,
            priority=self.priority,
            assignee_id=self.assignee_id,
            created_by_id=self.created_by_id,
            room_id=self.room_id,
            is_overdue=self.is_overdue,
            search=self.search
        )


# ============================================
# Task Statistics Schemas
# ============================================

class TaskStatistics(BaseModel):
    """Статистика по задачам"""
    total: int
    todo: int
    in_progress: int
    review: int
    done: int
    cancelled: int
    overdue: int
    by_priority: dict[str, int] = {
        "low": 0,
        "medium": 0,
        "high": 0,
        "urgent": 0
    }


# ============================================
# Assignee Management Schemas
# ============================================

class AddAssigneeRequest(BaseModel):
    """Запрос на добавление ответственного"""
    user_id: int


class RemoveAssigneeRequest(BaseModel):
    """Запрос на удаление ответственного"""
    user_id: int


class BulkAssignRequest(BaseModel):
    """Запрос на массовое назначение"""
    user_ids: list[int] = Field(..., min_items=1)


# ============================================
# Status Update Schema
# ============================================

class TaskStatusUpdate(BaseModel):
    """Схема для обновления статуса задачи"""
    status: TaskStatus
