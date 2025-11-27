"""
Enhanced AI

 Agents with Reasoning Models and Multi-language Support
"""

from typing import List, Dict, Optional, Any, TypedDict, Annotated, Literal
from operator import add
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
from sqlalchemy.ext.asyncio import AsyncSession
import json

from core.config import settings
from .tools import (
    get_room_members as db_get_room_members,
    find_employees_by_skills as db_find_employees_by_skills,
    get_recent_tasks as db_get_recent_tasks,
    get_user_resume as db_get_user_resume,
    get_room_info as db_get_room_info
)


# Language-specific prompts
SYSTEM_PROMPTS = {
    "en": {
        "problem_analyzer": """You are a problem analyzer for a task management system.
Extract the following from the problem description:
1. problem_summary: Brief 1-2 sentence summary
2. problem_type: Category (bug, feature, infrastructure, database, frontend, backend, etc.)
3. priority: low, medium, high, or urgent
4. required_skills: List of skills needed
5. estimated_complexity: simple, moderate, complex
6. keywords: Important keywords

Return ONLY a valid JSON object.""",
        
        "task_orchestrator": """You are a task assignment AI agent for project management in room {room_id}.

Your goal: Analyze the problem and create a DETAILED BREAKDOWN into subtasks, assigning each to the most suitable person.

AVAILABLE TOOLS - You MUST use these to gather information:
1. get_room_members_tool() - Get all members of the room with their roles
2. find_employees_by_skills_tool(required_skills, role, min_experience_years) - Find members with specific skills
3. get_recent_tasks_tool(topic, limit) - Get recent tasks to see past work
4. get_user_resume_tool(user_id) - Get detailed resume for a specific user

WORKFLOW:
1. FIRST: Call get_room_members_tool() to see all available team members
2. THEN: For each required skill, call find_employees_by_skills_tool() to find the best match
3. OPTIONALLY: Call get_user_resume_tool() for detailed info about candidates
4. FINALLY: Create breakdown with assignments based on the data you collected

RULES:
1. ONLY assign to room members (room_id: {room_id})
2. Break down complex problems into clear subtasks (2-5 subtasks)
3. For EACH subtask, assign the best person based on skills and workload
4. Consider past experience with similar tasks
5. Provide clear reasoning for each assignment

You MUST call tools to gather data before making assignments. DO NOT guess or assume."""
    },
    
    "ru": {
        "problem_analyzer": """Ты анализатор проблем для системы управления задачами.
Извлеки из описания проблемы:
1. problem_summary: Краткое резюме в 1-2 предложения
2. problem_type: Категория (bug, feature, infrastructure, database, frontend, backend и т.д.)
3. priority: low, medium, high или urgent
4. required_skills: Список необходимых навыков
5. estimated_complexity: simple, moderate, complex
6. keywords: Важные ключевые слова

Верни ТОЛЬКО валидный JSON объект.""",
        
        "task_orchestrator": """Ты AI-агент для назначения задач в комнате {room_id}.

Цель: Проанализировать проблему и создать ДЕТАЛЬНУЮ РАЗБИВКУ на подзадачи, назначив каждую наиболее подходящему человеку.

ДОСТУПНЫЕ ИНСТРУМЕНТЫ - Ты ДОЛЖЕН их использовать для сбора информации:
1. get_room_members_tool() - Получить всех участников комнаты с их ролями
2. find_employees_by_skills_tool(required_skills, role, min_experience_years) - Найти участников с нужными навыками
3. get_recent_tasks_tool(topic, limit) - Получить недавние задачи для понимания прошлой работы
4. get_user_resume_tool(user_id) - Получить детальное резюме конкретного пользователя

WORKFLOW:
1. СНАЧАЛА: Вызови get_room_members_tool() чтобы увидеть всех доступных членов команды
2. ЗАТЕМ: Для каждого требуемого навыка вызови find_employees_by_skills_tool() чтобы найти лучшее совпадение
3. ОПЦИОНАЛЬНО: Вызови get_user_resume_tool() для детальной информации о кандидатах
4. В КОНЦЕ: Создай разбивку с назначениями на основе собранных данных

ПРАВИЛА:
1. Назначай ТОЛЬКО участникам комнаты (room_id: {room_id})
2. Разбивай сложные проблемы на чёткие подзадачи (2-5 подзадач)
3. Для КАЖДОЙ подзадачи назначай лучшего человека на основе навыков и загрузки
4. Учитывай прошлый опыт с похожими задачами
5. Предоставляй четкое обоснование каждого назначения

Ты ДОЛЖЕН вызывать инструменты для сбора данных перед назначениями. НЕ угадывай и не предполагай."""
    }
}


def get_model_for_complexity(complexity: str, use_reasoning: bool = False) -> ChatOpenAI:
    """
    Select appropriate model based on task complexity
    
    Args:
        complexity: simple, moderate, or complex
        use_reasoning: Force use of reasoning model
        
    Returns:
        ChatOpenAI instance with appropriate model
    """
    if use_reasoning or complexity == "complex":
        # Use reasoning model for complex tasks
     
        return ChatOpenAI(
            model="gpt-5",
            temperature=0.7,
            api_key=settings.openai_api_key
        )
    else:
        # Use fast model for simple/moderate tasks
        return ChatOpenAI(
            model="gpt-5-mini",
            temperature=0.3,
            api_key=settings.openai_api_key
        )


class ProblemAnalyzer:
    """Analyzes problem with multi-language support"""
    
    def __init__(self, language: str = "en"):
        self.language = language if language in SYSTEM_PROMPTS else "en"
        self.llm = ChatOpenAI(
            model="gpt-4.1-nano",
            temperature=0.3,
            api_key=settings.openai_api_key
        )
    
    async def analyze_problem(self, problem_description: str) -> Dict:
        """Analyze problem and extract structured information"""
        system_prompt = SYSTEM_PROMPTS[self.language]["problem_analyzer"]
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Analyze this problem:\n\n{problem_description}")
        ]
        
        response = await self.llm.ainvoke(
            messages,
            response_format={"type": "json_object"}
        )
        
        try:
            analysis = json.loads(response.content)
            analysis["language"] = self.language
            return analysis
        except json.JSONDecodeError:
            return {
                "problem_summary": problem_description[:200],
                "problem_type": "general",
                "priority": "medium",
                "required_skills": [],
                "estimated_complexity": "moderate",
                "keywords": [],
                "language": self.language
            }


# Enhanced state for subtask breakdown
class EnhancedAgentState(TypedDict):
    """State for enhanced task breakdown agent"""
    room_id: int
    problem_description: str
    problem_analysis: Dict
    language: str
    messages: Annotated[List, add]
    subtasks: List[Dict]  # List of suggested subtasks
    overall_strategy: str
    model_used: str
    reasoning_steps: List[str]


class TaskBreakdownOrchestrator:
    """
    Enhanced LangGraph agent that breaks down complex problems into subtasks
    with intelligent assignment using proper StateGraph workflow
    """
    
    def __init__(self, room_id: int, db: AsyncSession, language: str = "en"):
        self.room_id = room_id
        self.db = db
        self.language = language if language in SYSTEM_PROMPTS else "en"
        
        # Create tools
        self.tools = self._create_tools()
        self.graph = None  # Will be created in create_breakdown
    
    def _create_tools(self):
        """Create LangChain tools"""
        
        @tool
        async def get_room_members_tool() -> List[Dict]:
            """Get all members of the current room with their roles and basic information"""
            return await db_get_room_members(self.room_id, self.db)
        
        @tool
        async def find_employees_by_skills_tool(
            required_skills: List[str],
            role: Optional[str] = None,
            min_experience_years: Optional[int] = None
        ) -> List[Dict]:
            """Find room members who have specific skills. Returns members sorted by match score."""
            return await db_find_employees_by_skills(
                room_id=self.room_id,
                required_skills=required_skills,
                db=self.db,
                role=role,
                min_experience_years=min_experience_years
            )
        
        @tool
        async def get_recent_tasks_tool(
            topic: Optional[str] = None,
            limit: int = 20
        ) -> List[Dict]:
            """Get recent tasks from the room to understand what has been done before"""
            return await db_get_recent_tasks(
                room_id=self.room_id,
                db=self.db,
                topic=topic,
                limit=limit
            )
        
        @tool
        async def get_user_resume_tool(user_id: int) -> Optional[Dict]:
            """Get detailed resume and experience for a specific user"""
            return await db_get_user_resume(user_id=user_id, db=self.db)
        
        return [
            get_room_members_tool,
            find_employees_by_skills_tool,
            get_recent_tasks_tool,
            get_user_resume_tool
        ]
    
    def _should_continue(self, state: EnhancedAgentState) -> Literal["tools", "end"]:
        """Determine if agent should continue or finish"""
        messages = state["messages"]
        last_message = messages[-1]
        
        # If last message has tool calls, continue to tools
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        
        # Otherwise end
        return "end"
    
    async def _call_model(self, state: EnhancedAgentState, llm_with_tools: ChatOpenAI) -> EnhancedAgentState:
        """Call the LLM with current state"""
        messages = state["messages"]
        response = await llm_with_tools.ainvoke(messages)
        
        # Add to reasoning steps if available
        reasoning_steps = state.get("reasoning_steps", [])
        if hasattr(response, "content") and response.content:
            reasoning_steps.append(response.content)
        
        return {
            **state,
            "messages": [response],
            "reasoning_steps": reasoning_steps
        }
    
    async def _call_tools(self, state: EnhancedAgentState) -> EnhancedAgentState:
        """Execute tool calls from the last message"""
        messages = state["messages"]
        last_message = messages[-1]
        
        tool_messages = []
        
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            for tool_call in last_message.tool_calls:
                # Execute the tool
                function_name = tool_call["name"]
                function_args = tool_call["args"]
                
                result = await self._execute_tool(function_name, function_args)
                
                # Create tool message
                from langchain_core.messages import ToolMessage
                tool_message = ToolMessage(
                    content=json.dumps(result),
                    tool_call_id=tool_call["id"],
                    name=function_name
                )
                tool_messages.append(tool_message)
        
        return {
            **state,
            "messages": tool_messages
        }
    
    async def create_breakdown(
        self,
        problem_analysis: Dict,
        problem_description: str,
        use_reasoning: bool = None
    ) -> Dict:
        """
        Create detailed task breakdown with assignments using LangGraph
        
        Args:
            problem_analysis: Analysis from ProblemAnalyzer
            problem_description: Original problem text
            use_reasoning: Force reasoning model (auto if complex)
            
        Returns:
            Complete breakdown with subtasks and assignments
        """
        # Determine model to use
        complexity = problem_analysis.get("estimated_complexity", "moderate")
        if use_reasoning is None:
            use_reasoning = complexity == "complex"
        
        llm = get_model_for_complexity(complexity, use_reasoning)
        llm_with_tools = llm.bind_tools(self.tools)
        
        # Build system prompt
        system_content = SYSTEM_PROMPTS[self.language]["task_orchestrator"].format(
            room_id=self.room_id
        )
        
        # Build user message
        user_content = self._build_user_prompt(problem_description, problem_analysis)
        
        # Create the graph
        workflow = StateGraph(EnhancedAgentState)
        
        # Define nodes
        async def call_model_node(state: EnhancedAgentState) -> EnhancedAgentState:
            return await self._call_model(state, llm_with_tools)
        
        async def call_tools_node(state: EnhancedAgentState) -> EnhancedAgentState:
            return await self._call_tools(state)
        
        # Add nodes
        workflow.add_node("agent", call_model_node)
        workflow.add_node("tools", call_tools_node)
        
        # Add edges
        workflow.set_entry_point("agent")
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "tools": "tools",
                "end": END
            }
        )
        workflow.add_edge("tools", "agent")
        
        # Compile the graph
        app = workflow.compile()
        
        # Initialize state
        initial_state: EnhancedAgentState = {
            "room_id": self.room_id,
            "problem_description": problem_description,
            "problem_analysis": problem_analysis,
            "language": self.language,
            "messages": [
                SystemMessage(content=system_content),
                HumanMessage(content=user_content)
            ],
            "subtasks": [],
            "overall_strategy": "",
            "model_used": llm.model_name,
            "reasoning_steps": []
        }
        
        # Run the graph
        final_state = await app.ainvoke(initial_state)
        
        # Parse final response
        breakdown = await self._parse_breakdown(final_state["messages"], llm)
        breakdown["model_used"] = llm.model_name
        breakdown["reasoning_steps"] = final_state.get("reasoning_steps", [])
        
        return breakdown
    
    def _build_user_prompt(self, problem_description: str, analysis: Dict) -> str:
        """Build detailed user prompt"""
        if self.language == "ru":
            return f"""Задача для анализа и разбивки:

Описание: {problem_description}

Анализ проблемы:
- Тип: {analysis.get('problem_type')}
- Приоритет: {analysis.get('priority')}
- Необходимые навыки: {', '.join(analysis.get('required_skills', []))}
- Сложность: {analysis.get('estimated_complexity')}
- Резюме: {analysis.get('problem_summary')}

Создай ДЕТАЛЬНУЮ РАЗБИВКУ этой проблемы на подзадачи (от 2 до 5 подзадач).
Для КАЖДОЙ подзадачи:
1. Определи четкое название и описание
2. Найди и назначь лучшего исполнителя из комнаты
3. Укажи приоритет и оценку времени
4. Объясни почему выбран именно этот человек

Используй доступные инструменты для сбора информации о участниках."""
        else:  # en
            return f"""Task to analyze and break down:

Description: {problem_description}

Problem Analysis:
- Type: {analysis.get('problem_type')}
- Priority: {analysis.get('priority')}
- Required Skills: {', '.join(analysis.get('required_skills', []))}
- Complexity: {analysis.get('estimated_complexity')}
- Summary: {analysis.get('problem_summary')}

Create a DETAILED BREAKDOWN of this problem into subtasks (2-5 subtasks).
For EACH subtask:
1. Define clear title and description
2. Find and assign the best person from the room
3. Specify priority and time estimate
4. Explain why this person was chosen

Use available tools to gather information about room members."""
    
    async def _execute_tool(self, function_name: str, arguments: Dict) -> Any:
        """Execute a tool function"""
        for tool in self.tools:
            if tool.name == function_name:
                return await tool.ainvoke(arguments)
        return {"error": f"Unknown tool: {function_name}"}
    
    async def _parse_breakdown(self, messages: List, llm: ChatOpenAI) -> Dict:
        """Parse agent's response into structured breakdown"""
        last_message = messages[-1]
        
        # Language-specific prompts
        if self.language == "ru":
            parse_prompt = """На основе твоего анализа, предоставь разбивку задач в этом JSON формате:
{
    "overall_strategy": "Краткое объяснение общего подхода",
    "subtasks": [
        {
            "title": "Название подзадачи",
            "description": "Детальное описание",
            "assigned_to_user_id": <user_id или null>,
            "assigned_to_username": "<username или null>",
            "priority": "low|medium|high|urgent",
            "estimated_time": "оценка времени (например '2-3 дня')",
            "estimated_hours": <число часов, например 16>,
            "due_date_days": <через сколько дней дедлайн, например 3>,
            "complexity_score": <1-10: 1=тривиальная, 3=простая, 5=средняя, 7=сложная, 10=очень сложная>,
            "required_skills": ["навык1", "навык2"],
            "reasoning": "Почему выбран этот человек и такая оценка"
        }
    ],
    "warnings": ["любые предупреждения или заметки"]
}

ВАЖНО при оценке сложности:
- 1-2: Простые изменения, не требует глубоких знаний (например, изменение текста, small fix)
- 3-4: Простая задача, требует базовых знаний (например, добавление кнопки, простой компонент)
- 5-6: Средняя сложность, требует хорошего понимания системы (например, новая фича с интеграцией)
- 7-8: Сложная задача, требует глубоких знаний (например, рефакторинг архитектуры, сложная логика)
- 9-10: Очень сложная, критическая задача (например, полная переработка модуля, нестандартная проблема)

Дедлайн определяй на основе:
- Сложности задачи
- Опыта назначенного человека
- Приоритета задачи
- Зависимостей от других задач

Твой анализ:
""" + last_message.content + "\n\nВерни ТОЛЬКО JSON, без дополнительного текста. Все текстовые поля должны быть на русском языке."
        else:  # en
            parse_prompt = """Based on your analysis, provide the task breakdown in this JSON format:
{
    "overall_strategy": "Brief explanation of the overall approach",
    "subtasks": [
        {
            "title": "Subtask title",
            "description": "Detailed description",
            "assigned_to_user_id": <user_id or null>,
            "assigned_to_username": "<username or null>",
            "priority": "low|medium|high|urgent",
            "estimated_time": "time estimate (e.g. '2-3 days')",
            "estimated_hours": <number of hours, e.g. 16>,
            "due_date_days": <days from now for deadline, e.g. 3>,
            "complexity_score": <1-10: 1=trivial, 3=simple, 5=moderate, 7=complex, 10=very complex>,
            "required_skills": ["skill1", "skill2"],
            "reasoning": "Why this person was chosen and the estimation rationale"
        }
    ],
    "warnings": ["any concerns or notes"]
}

IMPORTANT for complexity scoring:
- 1-2: Simple changes, no deep knowledge needed (e.g., text change, small fix)
- 3-4: Simple task, requires basic knowledge (e.g., adding button, simple component)
- 5-6: Moderate complexity, requires good system understanding (e.g., new feature with integration)
- 7-8: Complex task, requires deep knowledge (e.g., architecture refactoring, complex logic)
- 9-10: Very complex, critical task (e.g., full module rebuild, non-standard problem)

Deadline should be based on:
- Task complexity
- Assignee's experience level
- Task priority
- Dependencies on other tasks

Your analysis:
""" + last_message.content + "\n\nReturn ONLY the JSON, no additional text."
        
        response = await llm.ainvoke(
            [HumanMessage(content=parse_prompt)],
            response_format={"type": "json_object"}
        )
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {
                "overall_strategy": last_message.content,
                "subtasks": [],
                "warnings": ["Failed to parse structured breakdown"]
            }
