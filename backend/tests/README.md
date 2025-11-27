# Тесты для API задач (Tasks)

Этот файл содержит полный набор тестов для всех роутов задач в приложении.

## Структура тестов

### 1. **TestTaskCreation** - Тесты создания задач
- ✅ `test_create_task_success` - Успешное создание задачи
- ✅ `test_create_task_with_assignees` - Создание задачи с назначением ответственных
- ✅ `test_create_task_unauthorized` - Попытка создания без авторизации
- ✅ `test_create_task_invalid_data` - Создание с невалидными данными

### 2. **TestTaskRetrieval** - Тесты получения задач
- ✅ `test_get_all_tasks` - Получение всех задач
- ✅ `test_get_tasks_with_pagination` - Получение с пагинацией
- ✅ `test_get_tasks_with_filters` - Получение с фильтрами (статус, приоритет)
- ✅ `test_get_my_tasks` - Получение задач текущего пользователя
- ✅ `test_get_tasks_created_by_me` - Получение задач, созданных пользователем
- ✅ `test_get_overdue_tasks` - Получение просроченных задач
- ✅ `test_get_task_by_id` - Получение задачи по ID
- ✅ `test_get_nonexistent_task` - Попытка получить несуществующую задачу

### 3. **TestTaskUpdate** - Тесты обновления задач
- ✅ `test_update_task_success` - Успешное обновление задачи
- ✅ `test_update_task_status_only` - Обновление только статуса
- ✅ `test_update_nonexistent_task` - Попытка обновить несуществующую задачу

### 4. **TestTaskDeletion** - Тесты удаления задач
- ✅ `test_delete_task_success` - Успешное удаление задачи
- ✅ `test_delete_nonexistent_task` - Попытка удалить несуществующую задачу

### 5. **TestTaskAssignees** - Тесты управления ответственными
- ✅ `test_add_assignee_success` - Добавление ответственного
- ✅ `test_remove_assignee_success` - Удаление ответственного
- ✅ `test_bulk_assign_success` - Массовое назначение ответственных

### 6. **TestTaskStatistics** - Тесты статистики
- ✅ `test_get_my_statistics` - Получение статистики текущего пользователя
- ✅ `test_get_user_statistics_as_lead` - Получение статистики другого пользователя (как лид)
- ✅ `test_get_user_statistics_forbidden` - Запрет получения статистики (не лид)

### 7. **TestTaskSearchAndFilters** - Тесты поиска и фильтрации
- ✅ `test_search_tasks_by_text` - Поиск задач по тексту

## Покрытые роуты

Все роуты из `my_tasks/routes.py`:

1. **POST** `/tasks/` - Создание задачи
2. **GET** `/tasks/` - Получение всех задач с фильтрацией и пагинацией
3. **GET** `/tasks/my` - Получение задач текущего пользователя
4. **GET** `/tasks/created-by-me` - Получение задач, созданных пользователем
5. **GET** `/tasks/overdue` - Получение просроченных задач
6. **GET** `/tasks/{task_id}` - Получение задачи по ID
7. **PUT** `/tasks/{task_id}` - Обновление задачи
8. **PATCH** `/tasks/{task_id}/status` - Обновление статуса задачи
9. **DELETE** `/tasks/{task_id}` - Удаление задачи
10. **POST** `/tasks/{task_id}/assignees` - Добавление ответственного
11. **DELETE** `/tasks/{task_id}/assignees/{user_id}` - Удаление ответственного
12. **POST** `/tasks/{task_id}/assignees/bulk` - Массовое назначение
13. **GET** `/tasks/statistics/me` - Статистика текущего пользователя
14. **GET** `/tasks/statistics/user/{user_id}` - Статистика пользователя (для лидов)

## Запуск тестов

### Запустить все тесты:
```bash
poetry run pytest tests/test_tasks.py -v
```

### Запустить конкретный класс тестов:
```bash
poetry run pytest tests/test_tasks.py::TestTaskCreation -v
```

### Запустить конкретный тест:
```bash
poetry run pytest tests/test_tasks.py::TestTaskCreation::test_create_task_success -v
```

### Запустить с подробным выводом:
```bash
poetry run pytest tests/test_tasks.py -vv
```

### Запустить с покрытием кода:
```bash
poetry run pytest tests/test_tasks.py --cov=my_tasks --cov-report=html
```

### Запустить только неудавшиеся тесты:
```bash
poetry run pytest tests/test_tasks.py --lf
```

## Зависимости

Убедитесь, что установлены следующие пакеты:
- `pytest` - фреймворк для тестирования
- `pytest-asyncio` - поддержка асинхронных тестов
- `httpx` - HTTP клиент для тестирования FastAPI
- `aiosqlite` - асинхронный SQLite для тестовой БД

Установка:
```bash
poetry install
```

## Примечания

- Тесты используют in-memory SQLite базу данных для изоляции
- Каждый тест запускается в отдельной транзакции
- Фикстуры создают тестовых пользователей автоматически
- Все тесты независимы друг от друга
