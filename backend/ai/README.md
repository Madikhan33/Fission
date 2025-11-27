# AI Agent System 2.0 🚀

Улучшенная система AI-агентов с использованием **LangGraph State Machine**, **Reasoning Models (GPT-4o)**, **Мультиязычности** и **Workflow владельца комнаты**.

## ✨ Ключевые Возможности

### 1. LangGraph State Machine ⚙️
Агент использует правильную реализацию LangGraph с StateGraph:
- **Узлы (Nodes)**: `agent` (вызов LLM), `tools` (выполнение инструментов)
- **Рёбра (Edges)**: Условные переходы между узлами
- **Состояние (State)**: `EnhancedAgentState` с messages, subtasks, reasoning_steps

```python
workflow = StateGraph(EnhancedAgentState)
workflow.add_node("agent", call_model_node)
workflow.add_node("tools", call_tools_node)
workflow.add_conditional_edges("agent", should_continue, {...})
workflow.add_edge("tools", "agent")
```

### 2. Инструменты (Tools) 🛠
AI имеет доступ к 4 инструментам для сбора информации:

1. **get_room_members_tool()** 
   - Получить всех участников комнаты
   - Возвращает: user_id, username, email, role, is_lead
   
2. **find_employees_by_skills_tool(skills, role, experience)**
   - Найти участников с определёнными навыками
   - Использует resume_analysis для сопоставления
   - Возвращает список с match_score (% совпадения)
   
3. **get_recent_tasks_tool(topic, limit)**
   - Получить недавние задачи в комнате
   - Помогает понять прошлый опыт команды
   
4. **get_user_resume_tool(user_id)**
   - Получить детальное резюме пользователя
   - Включает skills, experience, projects

### 3. Умный Выбор Модели (Model Selection)
Система автоматически выбирает модель на основе сложности:
- **Simple/Moderate**: `gpt-4o` (быстро, эффективно)
- **Complex**: `gpt-4o` с повышенной temperature (глубокий анализ)
- **Force Reasoning**: Пользователь может принудительно включить reasoning mode

### 4. Мультиязычность 🌍
Полная поддержка русского и английского:
- Промпты переведены
- AI генерирует ответы на выбранном языке
- Параметр: `language: "ru" | "en"`

### 5. Workflow Владельца (Owner-Only) 👑
Только владелец комнаты может использовать AI:

**Процесс:**
```
1. Owner: Описывает проблему
2. AI: Анализирует (ProblemAnalyzer)
3. AI: Вызывает tools для сбора данных о команде
4. AI: Создаёт breakdown с назначениями
5. Owner: Просматривает предложения (status=pending)
6. Owner: Выбирает нужные подзадачи
7. Owner: Нажимает "Apply"
8. System: Создаёт задачи в БД (status=approved)
```

---

## 🛠 API Endpoints

### Создание разбивки задачи

```http
POST /ai/breakdown-task
Content-Type: application/json
Authorization: Bearer {token}
```

**Request:**
```json
{
  "room_id": 1,
  "problem_description": "У нас проблемы с производительностью на бэкенде при загрузке отчетов.",
  "language": "ru",
  "use_reasoning_model": true
}
```

**Response:**
```json
{
  "analysis_id": 42,
  "overall_strategy": "Проблема связана с N+1 запросами. Предлагаю разделить оптимизацию на БД и кэширование.",
  "model_used": "gpt-4o",
  "subtasks": [
    {
      "title": "Оптимизация SQL запросов в ReportsService",
      "description": "Использовать joinedload для связей...",
      "assigned_to_user_id": 5,
      "assigned_to_username": "ivan_backend",
      "priority": "high",
      "estimated_time": "2 дня",
      "required_skills": ["Python", "SQLAlchemy", "PostgreSQL"],
      "reasoning": "Иван - эксперт в SQLAlchemy с 3+ годами опыта. У него есть опыт оптимизации подобных запросов."
    },
    {
      "title": "Внедрение Redis кэша",
      "description": "Добавить кэш для часто запрашиваемых отчетов...",
      "assigned_to_user_id": 7,
      "assigned_to_username": "maria_fullstack",
      "priority": "medium",
      "estimated_time": "1 день",
      "required_skills": ["Redis", "Python"],
      "reasoning": "Мария работала с Redis в предыдущем проекте."
    }
  ],
  "status": "pending",
  "created_at": "2025-11-27T14:30:00Z",
  "warnings": []
}
```

### Применение разбивки

```http
POST /ai/apply-breakdown
```

```json
{
  "analysis_id": 42,
  "selected_subtask_indices": [0, 1]  // Выбираем первые 2 подзадачи
}
```

**Response:**
```json
{
  "analysis_id": 42,
  "created_tasks": [
    {"task_id": 101, "title": "Оптимизация SQL запросов...", "assigned_to": "ivan_backend"},
    {"task_id": 102, "title": "Внедрение Redis кэша", "assigned_to": "maria_fullstack"}
  ],
  "total_created": 2,
  "status": "approved",
  "applied_at": "2025-11-27T14:35:00Z"
}
```

### История анализов

```http
GET /ai/history/1?limit=20&offset=0
```

### Детали анализа

```http
GET /ai/analysis/42
```

---

## 🏗 Архитектура

### Database Schema

**Таблица `ai_analysis_history`:**
```sql
CREATE TABLE ai_analysis_history (
    id SERIAL PRIMARY KEY,
    room_id INTEGER REFERENCES rooms(id) ON DELETE CASCADE,
    created_by_id INTEGER REFERENCES users(id),
    problem_description TEXT NOT NULL,
    language VARCHAR(10) DEFAULT 'en',
    analysis_data JSONB NOT NULL,  -- Хранит весь ответ AI
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    applied_at TIMESTAMP NULL,
    created_task_ids JSONB DEFAULT '[]'::jsonb,
    user_feedback TEXT NULL
);
```

**Структура `analysis_data` (JSONB):**
```json
{
  "problem_analysis": {
    "problem_type": "infrastructure",
    "priority": "high",
    "required_skills": ["Python", "PostgreSQL"],
    "estimated_complexity": "complex"
  },
  "suggested_subtasks": [ ... ],
  "overall_strategy": "...",
  "model_used": "gpt-4o"
}
```

### Agent Logic Flow

```
┌─────────────────────┐
│ ProblemAnalyzer     │
│  (Mini-model)       │
└──────┬──────────────┘
       │  Extracts metadata:
       │  - type, priority
       │  - required_skills  
       │  - complexity
       v
┌─────────────────────────────────────┐
│ TaskBreakdownOrchestrator           │
│                                     │
│  ┌──────────────────┐               │
│  │  StateGraph      │               │
│  │                  │               │
│  │  ┌────────┐      │      ┌─────┐ │
│  │  │ Agent  │◄────►│◄────►│Tools│ │
│  │  └────────┘      │      └─────┘ │
│  │      ▼           │               │
│  │  ┌────────┐      │               │
│  │  │ Tools  │      │               │
│  │  └────────┘      │               │
│  │      ▼           │               │
│  │  ┌────────┐      │               │
│  │  │ Agent  │  (loop until done)   │
│  │  └────────┘      │               │
│  └──────────────────┘               │
└──────────┬──────────────────────────┘
           │
           v
    ┌──────────────┐
    │ JSON Parser  │  Structured output
    └──────────────┘
```

### System Prompts

Промпты содержат:
1. **Роль агента**
2. **Список доступных инструментов** (ВАЖНО!)
3. **Workflow**: Какие инструменты вызывать и когда
4. **Правила**: Ограничения и требования
5. **Императив**: "Ты ДОЛЖЕН вызывать инструменты"

Это гарантирует, что LLM знает о tools и активно их использует.

---

## 🧪 Тестирование

```bash
# Запуск всех AI тестов
poetry run pytest tests/test_ai_agent.py -v

# Конкретный тест
poetry run pytest tests/test_ai_agent.py::test_langgraph_workflow -v

# С выводом логов
poetry run pytest tests/test_ai_agent.py -v -s
```

### Основные Тесты

1. **test_problem_analyzer** - Тестирует ProblemAnalyzer
2. **test_langgraph_workflow** - Проверяет StateGraph и вызов tools
3. **test_breakdown_task_endpoint_owner_only** - Проверяет owner-only access
4. **test_breakdown_and_apply_workflow** - Полный workflow
5. **test_find_employees_by_skills** - Сопоставление навыков

---

## 🚀 Как запустить

### 1. Установка зависимостей

```bash
poetry install
```

### 2. Настройка .env

```env
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql+asyncpg://...
```

### 3. Запуск миграций

```bash
poetry run alembic upgrade head
```

### 4. Запуск сервера

```bash
poetry run granian main:app --reload
```

---

## 📝 Примеры Использования

### Python (Backend)

```python
from ai.agents import ProblemAnalyzer, TaskBreakdownOrchestrator

# Анализ
analyzer = ProblemAnalyzer(language="ru")
analysis = await analyzer.analyze_problem("Медленная БД")

# Разбивка
orchestrator = TaskBreakdownOrchestrator(
    room_id=1, 
    db=session, 
    language="ru"
)
breakdown = await orchestrator.create_breakdown(
    problem_analysis=analysis,
    problem_description="Медленная БД",
    use_reasoning=True
)
```

### TypeScript (Frontend)

```typescript
import { aiService } from '@/services/ai.service';

// Создание разбивки
const result = await aiService.createBreakdown({
  room_id: 1,
  problem_description: "Slow database queries",
  language: "en",
  use_reasoning_model: true
});

// Применение
await aiService.applyBreakdown({
  analysis_id: result.analysis_id,
  selected_subtask_indices: [0, 1, 2]
});
```

---

## 🔧 Troubleshooting

### AI не вызывает tools
- **Проверьте**: System prompt содержит описание tools
- **Решение**: Обновили prompts с явным указанием инструментов

### Ошибка "AttributeError: 'dict' object has no attribute 'function'"
- **Причина**: Неправильная обработка tool_calls
- **Решение**: Используем tool_call["name"] вместо tool_call.function.name

### Модель не возвращает JSON
- **Проверьте**: Используете ли `response_format={"type": "json_object"}`
- **Решение**: Добавлено в parse_breakdown

---

## 📚 Ссылки

- [LangChain Docs](https://python.langchain.com/)
- [LangGraph Tutorial](https://langchain-ai.github.io/langgraph/)
- [OpenAI API](https://platform.openai.com/docs/api-reference)

---

**Powered by** LangGraph + OpenAI GPT-4o ⚡

