from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import selectinload
from datetime import datetime
from typing import Optional

from my_tasks.models import Task, TaskAssignment, TaskStatus, TaskPriority
from auth.models import User
from rooms.models import RoomMember
from my_tasks.schemas import (
    TaskCreate, 
    TaskUpdate, 
    TaskFilterParams,
    TaskStatistics
)


# ============================================
# CRUD операции для задач
# ============================================
async def create_task(
    db: AsyncSession,
    task_data: TaskCreate,
    creator_id: int
) -> Task:
    try:
        # 1. Обработка времени
        due_date = task_data.due_date
        if due_date and due_date.tzinfo is not None:
            due_date = due_date.replace(tzinfo=None)

        # 2. Проверка прав СОЗДАТЕЛЯ (если задача в комнате)
        if task_data.room_id:
            member_check = await db.execute(
                select(RoomMember).where(
                    RoomMember.room_id == task_data.room_id,
                    RoomMember.user_id == creator_id
                )
            )
            if not member_check.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not a member of this room and cannot create tasks in it."
                )
        
        # 3. Создаем объект задачи
        new_task = Task(
            title=task_data.title,
            description=task_data.description,
            status=task_data.status,
            priority=task_data.priority,
            due_date=due_date,
            created_by_id=creator_id,
            room_id=task_data.room_id
        )
        db.add(new_task)
        await db.flush()  # Генерируем ID
        
        # 4. Обработка списка ответственных
        assignee_ids = task_data.assignee_ids if task_data.assignee_ids else []
        
        if not assignee_ids:
            assignee_ids = [creator_id]
        
        unique_assignee_ids = list(set(assignee_ids))
        
        # 5. Валидация ответственных
        if unique_assignee_ids:
            if task_data.room_id:
                # ВАРИАНТ А: Задача в комнате -> Проверяем членство в комнате
                # (Тут у вас все отлично, оптимизация не нужна, вы уже выбираете user_id)
                query = select(RoomMember.user_id).where(
                    RoomMember.room_id == task_data.room_id,
                    RoomMember.user_id.in_(unique_assignee_ids)
                )
                result = await db.execute(query)
                found_ids = set(result.scalars().all())
                
                missing_ids = set(unique_assignee_ids) - found_ids
                if missing_ids:
                    await db.rollback()
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Users {list(missing_ids)} are not members of the room."
                    )
            else:
                # ВАРИАНТ Б: Задача личная -> Проверяем существование юзеров
                # ОПТИМИЗАЦИЯ: select(User.id) вместо select(User)
                users_query = select(User.id).where(User.id.in_(unique_assignee_ids))
                users_result = await db.execute(users_query)
                found_ids = set(users_result.scalars().all()) # Тут сразу список int
            
                missing_ids = set(unique_assignee_ids) - found_ids
                if missing_ids:
                    await db.rollback()
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Users with ids {list(missing_ids)} not found"
                    )
        
        # 6. Создаем записи в TaskAssignment
        for assignee_id in unique_assignee_ids:
            assignment = TaskAssignment(
                task_id=new_task.id,
                user_id=assignee_id,
                assigned_by_id=creator_id
            )
            db.add(assignment)
        
        await db.commit()
        
        # 7. Подгружаем связи для ответа API
        query = (
            select(Task)
            .options(
                selectinload(Task.created_by),
                selectinload(Task.assignments).selectinload(TaskAssignment.user)
            )
            .where(Task.id == new_task.id)
        )
        result = await db.execute(query)
        task_with_relations = result.scalar_one()
        
        return task_with_relations
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task: {str(e)}"
        )

        

async def get_task_by_id(
    db: AsyncSession,
    task_id: int
) -> Task:
    """
    Получить задачу по ID со всеми связанными данными
    
    Args:
        db: Сессия базы данных
        task_id: ID задачи
        
    Returns:
        Задача
        
    Raises:
        HTTPException: Если задача не найдена
    """
    try:
        query = (
            select(Task)
            .options(
                selectinload(Task.created_by),
                selectinload(Task.assignments).selectinload(TaskAssignment.user)
            )
            .where(Task.id == task_id)
        )
        result = await db.execute(query)
        task = result.scalar_one_or_none()
        
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id {task_id} not found"
            )
        
        return task
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get task: {str(e)}"
        )


async def get_tasks(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    filters: Optional[TaskFilterParams] = None
) -> tuple[list[Task], int]:
    """
    Получить список задач с фильтрацией и пагинацией
    
    Args:
        db: Сессия базы данных
        skip: Количество пропускаемых записей
        limit: Максимальное количество записей
        filters: Параметры фильтрации
        
    Returns:
        Кортеж (список задач, общее количество)
    """
    try:
        # Базовый запрос
        query = select(Task).options(
            selectinload(Task.created_by),
            selectinload(Task.assignments).selectinload(TaskAssignment.user)
        )
        
        # Применяем фильтры
        conditions = []
        
        if filters:
            if filters.status:
                conditions.append(Task.status == filters.status)
            
            if filters.priority:
                conditions.append(Task.priority == filters.priority)
            
            if filters.created_by_id:
                conditions.append(Task.created_by_id == filters.created_by_id)
            
            if filters.room_id:
                conditions.append(Task.room_id == filters.room_id)
            
            if filters.assignee_id:
                # Фильтр по ответственному через join
                query = query.join(TaskAssignment).where(
                    TaskAssignment.user_id == filters.assignee_id
                )
            
            if filters.is_overdue is not None:
                now = datetime.utcnow()
                if filters.is_overdue:
                    conditions.append(
                        and_(
                            Task.due_date < now,
                            Task.status.not_in([TaskStatus.DONE, TaskStatus.CANCELLED])
                        )
                    )
                else:
                    conditions.append(
                        or_(
                            Task.due_date >= now,
                            Task.due_date.is_(None),
                            Task.status.in_([TaskStatus.DONE, TaskStatus.CANCELLED])
                        )
                    )
            
            if filters.search:
                search_pattern = f"%{filters.search}%"
                conditions.append(
                    or_(
                        Task.title.ilike(search_pattern),
                        Task.description.ilike(search_pattern)
                    )
                )
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Получаем общее количество
        count_query = select(func.count()).select_from(Task)
        
        if filters and filters.assignee_id:
             count_query = count_query.join(TaskAssignment).where(
                 TaskAssignment.user_id == filters.assignee_id
             )

        if conditions:
            count_query = count_query.where(and_(*conditions))
        
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Применяем пагинацию и сортировку
        query = query.order_by(Task.created_at.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        tasks = result.scalars().all()
        
        return list(tasks), total
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tasks: {str(e)}"
        )


async def update_task(
    db: AsyncSession,
    task_id: int,
    task_data: TaskUpdate,
    user_id: int
) -> Task:
    """
    Обновить задачу
    
    Args:
        db: Сессия базы данных
        task_id: ID задачи
        task_data: Данные для обновления
        user_id: ID пользователя, выполняющего обновление
        
    Returns:
        Обновленная задача
    """
    try:
        task = await get_task_by_id(db, task_id)
        
        # Обновляем только переданные поля
        update_data = task_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(task, field, value)
        
        # Если статус изменен на DONE, устанавливаем время завершения
        if task_data.status == TaskStatus.DONE and task.completed_at is None:
            task.completed_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(task)
        
        return await get_task_by_id(db, task_id)
        
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update task: {str(e)}"
        )


async def delete_task(
    db: AsyncSession,
    task_id: int,
    user_id: int
) -> bool:
    """
    Удалить задачу
    
    Args:
        db: Сессия базы данных
        task_id: ID задачи
        user_id: ID пользователя, выполняющего удаление
        
    Returns:
        True если успешно удалено
    """
    try:
        task = await get_task_by_id(db, task_id)
        
        # Проверяем права (только создатель или лид может удалить)
        user_query = select(User).where(User.id == user_id)
        user_result = await db.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if task.created_by_id != user_id and not user.is_lead:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this task"
            )
        
        await db.delete(task)
        await db.commit()
        
        return True
        
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete task: {str(e)}"
        )


# ============================================
# Управление ответственными
# ============================================

async def add_assignee(
    db: AsyncSession,
    task_id: int,
    assignee_id: int,
    assigned_by_id: int
) -> TaskAssignment:
    """
    Добавить ответственного к задаче
    
    Args:
        db: Сессия базы данных
        task_id: ID задачи
        assignee_id: ID нового ответственного
        assigned_by_id: ID пользователя, назначающего ответственного
        
    Returns:
        Созданное назначение
    """
    try:
        # Проверяем существование задачи
        await get_task_by_id(db, task_id)
        
        # Проверяем существование пользователя
        user_query = select(User).where(User.id == assignee_id)
        user_result = await db.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {assignee_id} not found"
            )
        
        # Проверяем, не назначен ли уже
        existing_query = select(TaskAssignment).where(
            TaskAssignment.task_id == task_id,
            TaskAssignment.user_id == assignee_id
        )
        existing_result = await db.execute(existing_query)
        existing = existing_result.scalar_one_or_none()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already assigned to this task"
            )
        
        # Создаем назначение
        assignment = TaskAssignment(
            task_id=task_id,
            user_id=assignee_id,
            assigned_by_id=assigned_by_id
        )
        db.add(assignment)
        await db.commit()
        await db.refresh(assignment)
        
        return assignment
        
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add assignee: {str(e)}"
        )


async def remove_assignee(
    db: AsyncSession,
    task_id: int,
    assignee_id: int,
    user_id: int
) -> bool:
    """
    Удалить ответственного из задачи
    
    Args:
        db: Сессия базы данных
        task_id: ID задачи
        assignee_id: ID ответственного для удаления
        user_id: ID пользователя, выполняющего удаление
        
    Returns:
        True если успешно удалено
    """
    try:
        # Проверяем существование задачи
        task = await get_task_by_id(db, task_id)
        
        # Находим назначение
        assignment_query = select(TaskAssignment).where(
            TaskAssignment.task_id == task_id,
            TaskAssignment.user_id == assignee_id
        )
        assignment_result = await db.execute(assignment_query)
        assignment = assignment_result.scalar_one_or_none()
        
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment not found"
            )
        
        # Проверяем права (создатель задачи, сам ответственный или лид)
        user_query = select(User).where(User.id == user_id)
        user_result = await db.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if task.created_by_id != user_id and assignee_id != user_id and not user.is_lead:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to remove this assignee"
            )
        
        await db.delete(assignment)
        await db.commit()
        
        return True
        
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove assignee: {str(e)}"
        )


async def bulk_assign(
    db: AsyncSession,
    task_id: int,
    assignee_ids: list[int],
    assigned_by_id: int
) -> list[TaskAssignment]:
    """
    Массово назначить ответственных на задачу
    
    Args:
        db: Сессия базы данных
        task_id: ID задачи
        assignee_ids: Список ID ответственных
        assigned_by_id: ID пользователя, назначающего ответственных
        
    Returns:
        Список созданных назначений
    """
    try:
        # Проверяем существование задачи
        await get_task_by_id(db, task_id)
        
        # Проверяем существование всех пользователей
        users_query = select(User).where(User.id.in_(assignee_ids))
        users_result = await db.execute(users_query)
        users = users_result.scalars().all()
        
        if len(users) != len(assignee_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more users not found"
            )
        
        # Получаем уже существующие назначения
        existing_query = select(TaskAssignment).where(
            TaskAssignment.task_id == task_id,
            TaskAssignment.user_id.in_(assignee_ids)
        )
        existing_result = await db.execute(existing_query)
        existing_assignments = existing_result.scalars().all()
        existing_user_ids = {a.user_id for a in existing_assignments}
        
        # Создаем новые назначения только для тех, кто еще не назначен
        new_assignments = []
        for assignee_id in assignee_ids:
            if assignee_id not in existing_user_ids:
                assignment = TaskAssignment(
                    task_id=task_id,
                    user_id=assignee_id,
                    assigned_by_id=assigned_by_id
                )
                db.add(assignment)
                new_assignments.append(assignment)
        
        await db.commit()
        
        # Возвращаем все назначения (существующие + новые)
        all_assignments_query = select(TaskAssignment).where(
            TaskAssignment.task_id == task_id,
            TaskAssignment.user_id.in_(assignee_ids)
        )
        all_result = await db.execute(all_assignments_query)
        return list(all_result.scalars().all())
        
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk assign: {str(e)}"
        )


# ============================================
# Статистика и аналитика
# ============================================

async def get_user_task_statistics(
    db: AsyncSession,
    user_id: int
) -> TaskStatistics:
    """
    Получить статистику по задачам пользователя
    
    Args:
        db: Сессия базы данных
        user_id: ID пользователя
        
    Returns:
        Статистика по задачам
    """
    try:
        # Получаем все задачи пользователя
        query = (
            select(Task)
            .join(TaskAssignment)
            .where(TaskAssignment.user_id == user_id)
        )
        result = await db.execute(query)
        tasks = result.scalars().all()
        
        # Подсчитываем статистику
        now = datetime.utcnow()
        stats = TaskStatistics(
            total=len(tasks),
            todo=len([t for t in tasks if t.status == TaskStatus.TODO]),
            in_progress=len([t for t in tasks if t.status == TaskStatus.IN_PROGRESS]),
            review=len([t for t in tasks if t.status == TaskStatus.REVIEW]),
            done=len([t for t in tasks if t.status == TaskStatus.DONE]),
            cancelled=len([t for t in tasks if t.status == TaskStatus.CANCELLED]),
            overdue=len([
                t for t in tasks 
                if t.due_date and t.due_date < now 
                and t.status not in [TaskStatus.DONE, TaskStatus.CANCELLED]
            ]),
            by_priority={
                "low": len([t for t in tasks if t.priority == TaskPriority.LOW]),
                "medium": len([t for t in tasks if t.priority == TaskPriority.MEDIUM]),
                "high": len([t for t in tasks if t.priority == TaskPriority.HIGH]),
                "urgent": len([t for t in tasks if t.priority == TaskPriority.URGENT]),
            }
        )
        
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )


async def get_overdue_tasks(
    db: AsyncSession,
    user_id: Optional[int] = None
) -> list[Task]:
    """
    Получить просроченные задачи
    
    Args:
        db: Сессия базы данных
        user_id: ID пользователя (опционально, для фильтрации)
        
    Returns:
        Список просроченных задач
    """
    try:
        now = datetime.utcnow()
        
        query = select(Task).options(
            selectinload(Task.created_by),
            selectinload(Task.assignments).selectinload(TaskAssignment.user)
        ).where(
            Task.due_date < now,
            Task.status.not_in([TaskStatus.DONE, TaskStatus.CANCELLED])
        )
        
        if user_id:
            query = query.join(TaskAssignment).where(TaskAssignment.user_id == user_id)
        
        result = await db.execute(query)
        return list(result.scalars().all())
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get overdue tasks: {str(e)}"
        )
