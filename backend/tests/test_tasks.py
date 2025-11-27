"""
Тесты для всех роутов задач (Tasks)
Все роуты протестированы с правильной аутентификацией
"""
import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import User
from my_tasks.models import Task, TaskStatus, TaskPriority, TaskAssignment


# ============================================
# Тесты создания задач (POST /tasks/)
# ============================================

@pytest.mark.asyncio
async def test_create_task_success(client: AsyncClient, test_user: User):
    """Тест успешного создания задачи"""
    task_data = {
        "title": "Тестовая задача",
        "description": "Описание тестовой задачи",
        "status": "todo",
        "priority": "high",
        "assignee_ids": []
    }
    
    response = await client.post("/tasks/", json=task_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == task_data["title"]
    assert data["description"] == task_data["description"]
    assert data["created_by_id"] == test_user.id


@pytest.mark.asyncio
async def test_create_task_with_assignees(
    client: AsyncClient, 
    test_user: User,
    test_user_2: User
):
    """Тест создания задачи с ответственными"""
    task_data = {
        "title": "Задача с ответственными",
        "description": "Тест",
        "assignee_ids": [test_user_2.id]
    }
    
    response = await client.post("/tasks/", json=task_data)
    
    assert response.status_code == 201
    data = response.json()
    assert len(data["assignments"]) > 0


@pytest.mark.asyncio
async def test_create_task_unauthorized(client_unauthorized: AsyncClient):
    """Тест создания задачи без авторизации"""
    task_data = {
        "title": "Тестовая задача",
        "description": "Описание"
    }
    
    response = await client_unauthorized.post("/tasks/", json=task_data)
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_task_invalid_data(client: AsyncClient):
    """Тест создания задачи с невалидными данными"""
    task_data = {
        "title": "",  # Пустой title
        "description": "Описание"
    }
    
    response = await client.post("/tasks/", json=task_data)
    
    assert response.status_code == 422


# ============================================
# Тесты получения задач (GET /tasks/)
# ============================================

@pytest.mark.asyncio
async def test_get_all_tasks(client: AsyncClient, test_user: User, test_db: AsyncSession):
    """Тест получения всех задач"""
    # Создаем задачи
    for i in range(3):
        task = Task(
            title=f"Задача {i}",
            description=f"Описание {i}",
            created_by_id=test_user.id,
            status=TaskStatus.TODO,
            priority=TaskPriority.MEDIUM
        )
        test_db.add(task)
    await test_db.commit()
    
    response = await client.get("/tasks/")
    
    assert response.status_code == 200
    data = response.json()
    assert "tasks" in data
    assert "total" in data
    assert data["total"] >= 3


@pytest.mark.asyncio
async def test_get_tasks_with_pagination(
    client: AsyncClient, 
    test_user: User,
    test_db: AsyncSession
):
    """Тест получения задач с пагинацией"""
    # Создаем 25 задач
    for i in range(25):
        task = Task(
            title=f"Задача {i}",
            created_by_id=test_user.id,
            status=TaskStatus.TODO,
            priority=TaskPriority.MEDIUM
        )
        test_db.add(task)
    await test_db.commit()
    
    response = await client.get("/tasks/?page=1&page_size=10")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["tasks"]) == 10
    assert data["page"] == 1
    assert data["total_pages"] == 3


@pytest.mark.asyncio
async def test_get_tasks_with_filters(
    client: AsyncClient, 
    test_user: User,
    test_db: AsyncSession
):
    """Тест получения задач с фильтрами"""
    # Создаем задачи с разными статусами
    task1 = Task(
        title="TODO задача",
        created_by_id=test_user.id,
        status=TaskStatus.TODO,
        priority=TaskPriority.HIGH
    )
    task2 = Task(
        title="IN_PROGRESS задача",
        created_by_id=test_user.id,
        status=TaskStatus.IN_PROGRESS,
        priority=TaskPriority.MEDIUM
    )
    test_db.add_all([task1, task2])
    await test_db.commit()
    
    # Фильтр по статусу
    response = await client.get("/tasks/?status=todo")
    assert response.status_code == 200
    data = response.json()
    assert all(task["status"] == "todo" for task in data["tasks"])


# ============================================
# Тесты получения конкретных задач
# ============================================

@pytest.mark.asyncio
async def test_get_my_tasks(
    client: AsyncClient, 
    test_user: User,
    test_db: AsyncSession
):
    """Тест получения задач текущего пользователя"""
    task = Task(
        title="Моя задача",
        created_by_id=test_user.id,
        status=TaskStatus.TODO,
        priority=TaskPriority.MEDIUM
    )
    test_db.add(task)
    await test_db.commit()
    await test_db.refresh(task)
    
    # Назначаем задачу на пользователя
    assignment = TaskAssignment(
        task_id=task.id,
        user_id=test_user.id,
        assigned_by_id=test_user.id
    )
    test_db.add(assignment)
    await test_db.commit()
    
    response = await client.get("/tasks/my")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_get_tasks_created_by_me(
    client: AsyncClient, 
    test_user: User,
    test_db: AsyncSession
):
    """Тест получения задач, созданных пользователем"""
    task = Task(
        title="Созданная мной задача",
        created_by_id=test_user.id,
        status=TaskStatus.TODO,
        priority=TaskPriority.MEDIUM
    )
    test_db.add(task)
    await test_db.commit()
    
    response = await client.get("/tasks/created-by-me")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_get_task_by_id(
    client: AsyncClient, 
    test_user: User,
    test_db: AsyncSession
):
    """Тест получения задачи по ID"""
    task = Task(
        title="Конкретная задача",
        created_by_id=test_user.id,
        status=TaskStatus.TODO,
        priority=TaskPriority.MEDIUM
    )
    test_db.add(task)
    await test_db.commit()
    await test_db.refresh(task)
    
    response = await client.get(f"/tasks/{task.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task.id
    assert data["title"] == task.title


@pytest.mark.asyncio
async def test_get_nonexistent_task(client: AsyncClient):
    """Тест получения несуществующей задачи"""
    response = await client.get("/tasks/99999")
    
    assert response.status_code == 404


# ============================================
# Тесты обновления задач (PUT/PATCH /tasks/{id})
# ============================================

@pytest.mark.asyncio
async def test_update_task_success(
    client: AsyncClient, 
    test_user: User,
    test_db: AsyncSession
):
    """Тест успешного обновления задачи"""
    task = Task(
        title="Старое название",
        description="Старое описание",
        created_by_id=test_user.id,
        status=TaskStatus.TODO,
        priority=TaskPriority.MEDIUM
    )
    test_db.add(task)
    await test_db.commit()
    await test_db.refresh(task)
    
    update_data = {
        "title": "Новое название",
        "description": "Новое описание",
        "status": "in_progress",
        "priority": "high"
    }
    
    response = await client.put(f"/tasks/{task.id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["status"] == update_data["status"]


@pytest.mark.asyncio
async def test_update_task_status_only(
    client: AsyncClient, 
    test_user: User,
    test_db: AsyncSession
):
    """Тест обновления только статуса"""
    task = Task(
        title="Задача",
        created_by_id=test_user.id,
        status=TaskStatus.TODO,
        priority=TaskPriority.MEDIUM
    )
    test_db.add(task)
    await test_db.commit()
    await test_db.refresh(task)
    
    status_data = {"status": "done"}
    
    response = await client.patch(f"/tasks/{task.id}/status", json=status_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "done"


# ============================================
# Тесты удаления задач (DELETE /tasks/{id})
# ============================================

@pytest.mark.asyncio
async def test_delete_task_success(
    client: AsyncClient, 
    test_user: User,
    test_db: AsyncSession
):
    """Тест успешного удаления задачи"""
    task = Task(
        title="Задача для удаления",
        created_by_id=test_user.id,
        status=TaskStatus.TODO,
        priority=TaskPriority.MEDIUM
    )
    test_db.add(task)
    await test_db.commit()
    await test_db.refresh(task)
    
    response = await client.delete(f"/tasks/{task.id}")
    
    assert response.status_code == 204


# ============================================
# Тесты управления ответственными
# ============================================

@pytest.mark.asyncio
async def test_add_assignee_success(
    client: AsyncClient, 
    test_user: User,
    test_user_2: User,
    test_db: AsyncSession
):
    """Тест добавления ответственного"""
    task = Task(
        title="Задача",
        created_by_id=test_user.id,
        status=TaskStatus.TODO,
        priority=TaskPriority.MEDIUM
    )
    test_db.add(task)
    await test_db.commit()
    await test_db.refresh(task)
    
    assignee_data = {"user_id": test_user_2.id}
    
    response = await client.post(f"/tasks/{task.id}/assignees", json=assignee_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == test_user_2.id


@pytest.mark.asyncio
async def test_remove_assignee_success(
    client: AsyncClient, 
    test_user: User,
    test_user_2: User,
    test_db: AsyncSession
):
    """Тест удаления ответственного"""
    task = Task(
        title="Задача",
        created_by_id=test_user.id,
        status=TaskStatus.TODO,
        priority=TaskPriority.MEDIUM
    )
    test_db.add(task)
    await test_db.commit()
    await test_db.refresh(task)
    
    assignment = TaskAssignment(
        task_id=task.id,
        user_id=test_user_2.id,
        assigned_by_id=test_user.id
    )
    test_db.add(assignment)
    await test_db.commit()
    
    response = await client.delete(f"/tasks/{task.id}/assignees/{test_user_2.id}")
    
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_bulk_assign_success(
    client: AsyncClient, 
    test_user: User,
    test_user_2: User,
    test_lead_user: User,
    test_db: AsyncSession
):
    """Тест массового назначения"""
    task = Task(
        title="Задача",
        created_by_id=test_user.id,
        status=TaskStatus.TODO,
        priority=TaskPriority.MEDIUM
    )
    test_db.add(task)
    await test_db.commit()
    await test_db.refresh(task)
    
    bulk_data = {"user_ids": [test_user_2.id, test_lead_user.id]}
    
    response = await client.post(f"/tasks/{task.id}/assignees/bulk", json=bulk_data)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


# ============================================
# Тесты статистики
# ============================================

@pytest.mark.asyncio
async def test_get_my_statistics(
    client: AsyncClient, 
    test_user: User,
    test_db: AsyncSession
):
    """Тест получения статистики текущего пользователя"""
    # Создаем задачи
    tasks = [
        Task(
            title="TODO задача",
            created_by_id=test_user.id,
            status=TaskStatus.TODO,
            priority=TaskPriority.MEDIUM
        ),
        Task(
            title="IN_PROGRESS задача",
            created_by_id=test_user.id,
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.HIGH
        ),
        Task(
            title="DONE задача",
            created_by_id=test_user.id,
            status=TaskStatus.DONE,
            priority=TaskPriority.LOW
        )
    ]
    test_db.add_all(tasks)
    await test_db.commit()
    
    # Назначаем задачи на пользователя
    for task in tasks:
        await test_db.refresh(task)
        assignment = TaskAssignment(
            task_id=task.id,
            user_id=test_user.id,
            assigned_by_id=test_user.id
        )
        test_db.add(assignment)
    await test_db.commit()
    
    response = await client.get("/tasks/statistics/me")
    
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "todo" in data
    assert "in_progress" in data
    assert "done" in data


@pytest.mark.asyncio
async def test_get_user_statistics_as_lead(
    client_lead: AsyncClient, 
    test_user: User,
    test_db: AsyncSession
):
    """Тест получения статистики другого пользователя (как лид)"""
    task = Task(
        title="Задача пользователя",
        created_by_id=test_user.id,
        status=TaskStatus.TODO,
        priority=TaskPriority.MEDIUM
    )
    test_db.add(task)
    await test_db.commit()
    await test_db.refresh(task)
    
    assignment = TaskAssignment(
        task_id=task.id,
        user_id=test_user.id,
        assigned_by_id=test_user.id
    )
    test_db.add(assignment)
    await test_db.commit()
    
    response = await client_lead.get(f"/tasks/statistics/user/{test_user.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert "total" in data


@pytest.mark.asyncio
async def test_get_user_statistics_forbidden(
    client: AsyncClient, 
    test_user_2: User
):
    """Тест запрета получения статистики (не лид)"""
    response = await client.get(f"/tasks/statistics/user/{test_user_2.id}")
    
    assert response.status_code == 403
