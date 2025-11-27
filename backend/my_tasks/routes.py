from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import math

from core.database import get_db
from auth.dep import get_current_user
from auth.models import User
from my_tasks.schemas import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
    TaskFilterParams,
    TaskStatistics,
    AddAssigneeRequest,
    RemoveAssigneeRequest,
    BulkAssignRequest,
    TaskStatusUpdate,
    TaskAssignmentResponse,
    PaginationParams,
    TaskFilterDependency
)
from my_tasks.models import TaskStatus, TaskPriority
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


router = APIRouter(prefix="/tasks", tags=["Tasks"])


# ============================================
# CRUD эндпоинты для задач
# ============================================

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_new_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Создать новую задачу
    
    - **title**: Название задачи (обязательно)
    - **description**: Описание задачи
    - **status**: Статус задачи (по умолчанию TODO)
    - **priority**: Приоритет задачи (по умолчанию MEDIUM)
    - **due_date**: Срок выполнения
    - **assignee_ids**: Список ID ответственных
    """
    return await create_task(db, task_data, current_user.id)


@router.get("/", response_model=TaskListResponse)
async def get_all_tasks(
    pagination: PaginationParams = Depends(),
    filters: TaskFilterDependency = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить список всех задач с фильтрацией и пагинацией
    
    Поддерживаемые фильтры:
    - По статусу
    - По приоритету
    - По ответственному
    - По создателю
    - Только просроченные
    - Поиск по тексту
    """
    # Конвертируем dependency в TaskFilterParams
    filter_params = filters.to_filter_params()
    
    # Получаем задачи
    tasks, total = await get_tasks(
        db, 
        skip=pagination.skip, 
        limit=pagination.limit, 
        filters=filter_params
    )
    
    # Вычисляем общее количество страниц
    total_pages = math.ceil(total / pagination.page_size) if total > 0 else 1
    
    return TaskListResponse(
        tasks=tasks,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=total_pages
    )


@router.get("/my", response_model=TaskListResponse)
async def get_my_tasks(
    pagination: PaginationParams = Depends(),
    filters: TaskFilterDependency = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить задачи текущего пользователя (где он ответственный)
    """
    # Конвертируем и добавляем фильтр по текущему пользователю
    filter_params = filters.to_filter_params()
    filter_params.assignee_id = current_user.id  # Переопределяем фильтр по ответственному
    
    tasks, total = await get_tasks(
        db, 
        skip=pagination.skip, 
        limit=pagination.limit, 
        filters=filter_params
    )
    total_pages = math.ceil(total / pagination.page_size) if total > 0 else 1
    
    return TaskListResponse(
        tasks=tasks,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=total_pages
    )


@router.get("/created-by-me", response_model=TaskListResponse)
async def get_tasks_created_by_me(
    pagination: PaginationParams = Depends(),
    filters: TaskFilterDependency = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить задачи, созданные текущим пользователем
    """
    # Конвертируем и добавляем фильтр по создателю
    filter_params = filters.to_filter_params()
    filter_params.created_by_id = current_user.id  # Переопределяем фильтр по создателю
    
    tasks, total = await get_tasks(
        db, 
        skip=pagination.skip, 
        limit=pagination.limit, 
        filters=filter_params
    )
    total_pages = math.ceil(total / pagination.page_size) if total > 0 else 1
    
    return TaskListResponse(
        tasks=tasks,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=total_pages
    )


@router.get("/overdue", response_model=list[TaskResponse])
async def get_overdue_tasks_endpoint(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить все просроченные задачи текущего пользователя
    """
    return await get_overdue_tasks(db, user_id=current_user.id)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить задачу по ID
    """
    return await get_task_by_id(db, task_id)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task_endpoint(
    task_id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Обновить задачу
    
    Можно обновить любое поле:
    - title
    - description
    - status
    - priority
    - due_date
    """
    return await update_task(db, task_id, task_data, current_user.id)


@router.patch("/{task_id}/status", response_model=TaskResponse)
async def update_task_status_endpoint(
    task_id: int,
    status_data: TaskStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Обновить только статус задачи
    """
    task_update = TaskUpdate(status=status_data.status)
    return await update_task(db, task_id, task_update, current_user.id)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_endpoint(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Удалить задачу
    
    Только создатель задачи или лид может удалить задачу
    """
    await delete_task(db, task_id, current_user.id)
    return None


# ============================================
# Управление ответственными
# ============================================

@router.post("/{task_id}/assignees", response_model=TaskAssignmentResponse, status_code=status.HTTP_201_CREATED)
async def add_assignee_to_task(
    task_id: int,
    assignee_data: AddAssigneeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Добавить ответственного к задаче
    """
    assignment = await add_assignee(
        db, 
        task_id, 
        assignee_data.user_id, 
        current_user.id
    )
    return assignment


@router.delete("/{task_id}/assignees/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_assignee_from_task(
    task_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Удалить ответственного из задачи
    
    Может удалить:
    - Создатель задачи
    - Сам ответственный
    - Лид
    """
    await remove_assignee(db, task_id, user_id, current_user.id)
    return None


@router.post("/{task_id}/assignees/bulk", response_model=list[TaskAssignmentResponse])
async def bulk_assign_to_task(
    task_id: int,
    bulk_data: BulkAssignRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Массово назначить ответственных на задачу
    """
    assignments = await bulk_assign(
        db,
        task_id,
        bulk_data.user_ids,
        current_user.id
    )
    return assignments


# ============================================
# Статистика
# ============================================

@router.get("/statistics/me", response_model=TaskStatistics)
async def get_my_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить статистику по задачам текущего пользователя
    
    Возвращает:
    - Общее количество задач
    - Количество по каждому статусу
    - Количество просроченных
    - Распределение по приоритетам
    """
    return await get_user_task_statistics(db, current_user.id)


@router.get("/statistics/user/{user_id}", response_model=TaskStatistics)
async def get_user_statistics(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить статистику по задачам конкретного пользователя
    
    Доступно только для лидов
    """
    if not current_user.is_lead:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only leads can view other users' statistics"
        )
    
    return await get_user_task_statistics(db, user_id)
