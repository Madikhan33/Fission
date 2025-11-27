"""
Comprehensive tests for AI Agent System with LangGraph
Tests routes, agents, tools, and complete workflows
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from ai.agents import ProblemAnalyzer, TaskBreakdownOrchestrator
from ai.models import AIAnalysisHistory, AnalysisStatus
from rooms.models import Room, RoomMember, RoomRole
from resume_ai.models import ResumeAnalysis
from auth.models import User
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage


# ========================================
# UNIT TESTS: AI Agents
# ========================================

@pytest.mark.asyncio
async def test_problem_analyzer():
    """Test ProblemAnalyzer extracts correct information"""
    
    with patch("ai.agents.ChatOpenAI") as MockChatOpenAI:
        # Mock LLM response
        mock_llm = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = """{
            "problem_summary": "Database performance issue",
            "problem_type": "infrastructure",
            "priority": "high",
            "required_skills": ["Database", "PostgreSQL"],
            "estimated_complexity": "moderate",
            "keywords": ["performance", "database", "slow queries"]
        }"""
        mock_llm.ainvoke.return_value = mock_response
        MockChatOpenAI.return_value = mock_llm
        
        analyzer = ProblemAnalyzer(language="en")
        result = await analyzer.analyze_problem("Our database is slow")
        
        assert result["problem_type"] == "infrastructure"
        assert result["priority"] == "high"
        assert "Database" in result["required_skills"]
        assert result["estimated_complexity"] == "moderate"


@pytest.mark.asyncio
async def test_langgraph_workflow():
    """Test TaskBreakdownOrchestrator uses LangGraph StateGraph correctly"""
    
    mock_db = AsyncMock()
    
    orchestrator = TaskBreakdownOrchestrator(room_id=1, db=mock_db, language="en")
    
    # Mock tools
    orchestrator._execute_tool = AsyncMock(return_value=[
        {"user_id": 1, "username": "dev1", "matching_skills": ["Python", "FastAPI"]}
    ])
    
    with patch("ai.agents.get_model_for_complexity") as mock_get_model:
        # Mock LLM
        mock_llm = AsyncMock()
        mock_llm.model_name = "gpt-4o"
        
        # First call: agent returns tool call
        # Second call: agent returns final response
        call_count = 0
        async def mock_ainvoke(messages, **kwargs):
            nonlocal call_count
            call_count += 1
            
            if call_count == 1:
                # Agent decides to call tool
                return AIMessage(
                    content="Let me check room members",
                    tool_calls=[{
                        "name": "get_room_members_tool",
                        "args": {},
                        "id": "call_123"
                    }]
                )
            else:
                # Agent returns final breakdown
                return AIMessage(
                    content="""Based on the team info, here's the breakdown:
                    Subtask 1: Implement feature X (assigned to dev1)"""
                )
        
        mock_bound_llm = MagicMock()
        mock_bound_llm.ainvoke = mock_ainvoke
        mock_llm.bind_tools.return_value = mock_bound_llm
        mock_get_model.return_value = mock_llm
        
        # Mock final parsing
        with patch.object(orchestrator, '_parse_breakdown') as mock_parse:
            mock_parse.return_value = {
                "overall_strategy": "Test strategy",
                "subtasks": [
                    {
                        "title": "Implement feature X",
                        "description": "Description here",
                        "assigned_to_user_id": 1,
                        "assigned_to_username": "dev1",
                        "priority": "high",
                        "estimated_time": "2 days",
                        "required_skills": ["Python"],
                        "reasoning": "Best developer"
                    }
                ],
                "warnings": []
            }
            
            problem_analysis = {"estimated_complexity": "simple"}
            result = await orchestrator.create_breakdown(
                problem_analysis=problem_analysis,
                problem_description="Test problem"
            )
            
            assert result["overall_strategy"] == "Test strategy"
            assert len(result["subtasks"]) == 1
            assert result["subtasks"][0]["assigned_to_username"] == "dev1"


# ========================================
# INTEGRATION TESTS: API Routes
# ========================================

@pytest.mark.asyncio
async def test_analyze_problem_endpoint(client: AsyncClient, test_user: User):
    """Test /ai/analyze-problem endpoint"""
    
    with patch("ai.agents.ChatOpenAI") as MockChatOpenAI:
        mock_llm = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = """{
            "problem_summary": "Need to fix bug",
            "problem_type": "bug",
            "priority": "medium",
            "required_skills": ["Python"],
            "estimated_complexity": "simple",
            "keywords": ["bug", "fix"]
        }"""
        mock_llm.ainvoke.return_value = mock_response
        MockChatOpenAI.return_value = mock_llm
        
        response = await client.post(
            "/ai/analyze-problem",
            json={
                "problem_description": "There's a bug in login",
                "language": "en"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["problem_type"] == "bug"
        assert data["priority"] == "medium"


@pytest.mark.asyncio
async def test_breakdown_task_endpoint_owner_only(
    client: AsyncClient,
    test_user: User,
    test_db: AsyncSession
):
    """Test that only room owner can use /ai/breakdown-task"""
    
    # Create room owned by another user
    other_user = User(
        username="owner",
        email="owner@test.com",
        hashed_password="hash",
        is_active=True
    )
    test_db.add(other_user)
    await test_db.commit()
    await test_db.refresh(other_user)
    
    room = Room(
        name="Test Room",
        description="Test",
        created_by_id=other_user.id
    )
    test_db.add(room)
    await test_db.commit()
    await test_db.refresh(room)
    
    # Add test_user as member (not owner)
    membership = RoomMember(
        room_id=room.id,
        user_id=test_user.id,
        role=RoomRole.MEMBER
    )
    test_db.add(membership)
    await test_db.commit()
    
    # Try to create breakdown (should fail)
    response = await client.post(
        "/ai/breakdown-task",
        json={
            "room_id": room.id,
            "problem_description": "Test problem",
            "language": "en"
        }
    )
    
    assert response.status_code == 403
    assert "owner" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_breakdown_and_apply_workflow(
    client: AsyncClient,
    test_user: User,
    test_db: AsyncSession
):
    """Test complete workflow: breakdown -> review -> apply"""
    
    # Create room owned by test_user
    room = Room(
        name="Test Room",
        description="Test",
        created_by_id=test_user.id
    )
    test_db.add(room)
    await test_db.commit()
    await test_db.refresh(room)
    
    # Add test_user as owner
    membership = RoomMember(
        room_id=room.id,
        user_id=test_user.id,
        role=RoomRole.OWNER
    )
    test_db.add(membership)
    await test_db.commit()
    
    # Mock AI responses
    with patch("ai.agents.ChatOpenAI") as MockChatOpenAI:
        mock_llm = AsyncMock()
        
        # Mock analysis
        mock_analysis_response = MagicMock()
        mock_analysis_response.content = """{
            "problem_summary": "Feature request",
            "problem_type": "feature",
            "priority": "medium",
            "required_skills": ["Python"],
            "estimated_complexity": "simple",
            "keywords": ["feature"]
        }"""
        
        # Mock breakdown
        call_count = 0
        async def mock_ainvoke(messages, **kwargs):
            nonlocal call_count
            call_count += 1
            
            if call_count == 1:
                return mock_analysis_response
            elif call_count == 2:
                # First breakdown call
                return AIMessage(content="Breakdown in progress")
            else:
                # Final parse call
                return MagicMock(content="""{
                    "overall_strategy": "Simple implementation",
                    "subtasks": [{
                        "title": "Task 1",
                        "description": "Implement X",
                        "assigned_to_user_id": null,
                        "assigned_to_username": null,
                        "priority": "medium",
                        "estimated_time": "1 day",
                        "required_skills": ["Python"],
                        "reasoning": "Straightforward"
                    }],
                    "warnings": []
                }""")
        
        mock_llm.ainvoke = mock_ainvoke
        mock_llm.model_name = "gpt-4o"
        mock_llm.bind_tools.return_value = mock_llm
        MockChatOpenAI.return_value = mock_llm
        
        # Step 1: Create breakdown
        response = await client.post(
            "/ai/breakdown-task",
            json={
                "room_id": room.id,
                "problem_description": "Add user export feature",
                "language": "en"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        analysis_id = data["analysis_id"]
        assert data["status"] == "pending"
        assert len(data["subtasks"]) > 0
        
        # Step 2: Apply breakdown
        response = await client.post(
            "/ai/apply-breakdown",
            json={
                "analysis_id": analysis_id,
                "selected_subtask_indices": [0]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "approved"
        assert data["total_created"] == 1


@pytest.mark.asyncio
async def test_get_analysis_history(
    client: AsyncClient,
    test_user: User,
    test_db: AsyncSession
):
    """Test /ai/history/{room_id} endpoint"""
    
    # Create room
    room = Room(
        name="Test Room",
        description="Test",
        created_by_id=test_user.id
    )
    test_db.add(room)
    await test_db.commit()
    await test_db.refresh(room)
    
    membership = RoomMember(
        room_id=room.id,
        user_id=test_user.id,
        role=RoomRole.OWNER
    )
    test_db.add(membership)
    
    # Create analysis history
    analysis = AIAnalysisHistory(
        room_id=room.id,
        created_by_id=test_user.id,
        problem_description="Test problem",
        language="en",
        analysis_data={
            "overall_strategy": "Test",
            "suggested_subtasks": [],
            "model_used": "gpt-4o"
        },
        status=AnalysisStatus.PENDING
    )
    test_db.add(analysis)
    await test_db.commit()
    
    # Get history
    response = await client.get(f"/ai/history/{room.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["status"] == "pending"


# ========================================
# TOOLS TESTS
# ========================================

@pytest.mark.asyncio
async def test_find_employees_by_skills(test_db: AsyncSession, test_user: User):
    """Test find_employees_by_skills tool"""
    
    from ai.tools import find_employees_by_skills
    
    # Create room
    room = Room(
        name="Dev Room",
        description="Developers",
        created_by_id=test_user.id
    )
    test_db.add(room)
    await test_db.commit()
    await test_db.refresh(room)
    
    # Add user to room
    membership = RoomMember(
        room_id=room.id,
        user_id=test_user.id,
        role=RoomRole.MEMBER
    )
    test_db.add(membership)
    
    # Create resume with skills
    resume = ResumeAnalysis(
        user_id=test_user.id,
        full_name="Test Developer",
        email=test_user.email,
        current_position="Backend Developer",
        years_of_experience=3,
        career_level="Middle",
        core_skills='["Python", "FastAPI", "PostgreSQL"]'
    )
    test_db.add(resume)
    await test_db.commit()
    
    # Find by skills
    results = await find_employees_by_skills(
        room_id=room.id,
        required_skills=["Python", "FastAPI"],
        db=test_db
    )
    
    assert len(results) == 1
    assert results[0]["user_id"] == test_user.id
    assert "Python" in results[0]["matching_skills"]
    assert results[0]["match_score"] == 100.0  # 2/2 skills matched


if __name__ == "__main__":
    # Helper to run tests directly
    import asyncio
    pytest.main([__file__, "-v"])
