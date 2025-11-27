"""
Enhanced AI Agent API Routes with Owner-only Access
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import datetime

from core.database import get_db
from auth.dep import get_current_user
from auth.models import User
from my_tasks.models import Task, TaskStatus, TaskPriority, TaskAssignment
from rooms.models import Room, RoomMember, RoomRole
from .models import AIAnalysisHistory, AnalysisStatus

from .schemas import (
    ProblemAnalysisRequest,
    ProblemAnalysisResponse,
    TaskBreakdownRequest,
    TaskBreakdownResponse,
    ApplyBreakdownRequest,
    ApplyBreakdownResponse,
    AnalysisHistoryResponse,
    AnalysisHistoryItem,
    SubtaskSuggestion
)
from .agents import ProblemAnalyzer, TaskBreakdownOrchestrator

# Import WebSocket manager and notification service
from notifications.websocket import manager as ws_manager
from notifications.service import create_task_assigned_notification


router = APIRouter(prefix="/ai", tags=["AI Agent"])


async def verify_room_owner(
    room_id: int,
    user_id: int,
    db: AsyncSession
) -> RoomMember:
    """Verify user is the room owner"""
    membership_query = select(RoomMember).where(
        RoomMember.room_id == room_id,
        RoomMember.user_id == user_id
    )
    result = await db.execute(membership_query)
    membership = result.scalar_one_or_none()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this room"
        )
    
    if membership.role != RoomRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only room owner can use AI assistant"
        )
    
    return membership


@router.post("/analyze-problem", response_model=ProblemAnalysisResponse)
async def analyze_problem(
    request: ProblemAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Analyze a problem description using AI
    Quick analysis without room context
    """
    analyzer = ProblemAnalyzer(language=request.language)
    analysis = await analyzer.analyze_problem(request.problem_description)
    
    return ProblemAnalysisResponse(**analysis)


@router.post("/breakdown-task", response_model=TaskBreakdownResponse)
async def create_task_breakdown(
    request: TaskBreakdownRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create AI-powered task breakdown with subtask suggestions
    
    **OWNER ONLY**: Only room owner can request AI analysis
    
    Flow:
    1. AI analyzes problem
    2. Breaks down into subtasks  
    3. Assigns best person for each subtask
    4. Saves to history (status=pending)
    5. Returns for review
    
    User must call /apply-breakdown to create actual tasks
    """
    # Verify owner
    await verify_room_owner(request.room_id, current_user.id, db)
    
    # Send WebSocket update: Starting analysis
    await ws_manager.send_personal_message({
        "type": "ai_progress",
        "status": "analyzing",
        "message": "Analyzing problem..."
    }, current_user.id)
    
    # Analyze problem
    analyzer = ProblemAnalyzer(language=request.language)
    problem_analysis = await analyzer.analyze_problem(request.problem_description)
    
    # Send update: Creating breakdown
    await ws_manager.send_personal_message({
        "type": "ai_progress",
        "status": "breaking_down",
        "message": "Creating task breakdown..."
    }, current_user.id)
    
    # Create breakdown
    orchestrator = TaskBreakdownOrchestrator(
        room_id=request.room_id,
        db=db,
        language=request.language
    )
    
    breakdown = await orchestrator.create_breakdown(
        problem_analysis=problem_analysis,
        problem_description=request.problem_description,
        use_reasoning=request.use_reasoning_model
    )
    
    # Save to history
    analysis_data = {
        "problem_analysis": problem_analysis,
        "suggested_subtasks": breakdown.get("subtasks", []),
        "overall_strategy": breakdown.get("overall_strategy", ""),
        "model_used": breakdown.get("model_used", "gpt-4o")
    }
    
    ai_analysis = AIAnalysisHistory(
        room_id=request.room_id,
        created_by_id=current_user.id,
        problem_description=request.problem_description,
        language=request.language,
        analysis_data=analysis_data,
        status=AnalysisStatus.PENDING
    )
    
    db.add(ai_analysis)
    await db.commit()
    await db.refresh(ai_analysis)
    
    # Send WebSocket update: Analysis complete
    await ws_manager.send_personal_message({
        "type": "ai_progress",
        "status": "complete",
        "message": "Analysis complete!",
        "analysis_id": ai_analysis.id
    }, current_user.id)
    
    return TaskBreakdownResponse(
        analysis_id=ai_analysis.id,
        overall_strategy=breakdown.get("overall_strategy", ""),
        subtasks=[SubtaskSuggestion(**st) for st in breakdown.get("subtasks", [])],
        problem_analysis=problem_analysis,
        model_used=breakdown.get("model_used", "gpt-4o"),
        warnings=breakdown.get("warnings", []),
        status="pending",
        created_at=ai_analysis.created_at.isoformat()
    )


@router.post("/apply-breakdown", response_model=ApplyBreakdownResponse)
async def apply_task_breakdown(
    request: ApplyBreakdownRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Apply AI breakdown - create actual tasks from analysis
    
    **OWNER ONLY**
    
    Creates tasks in database and assigns to suggested people
    Updates analysis status to 'approved'
    """
    # Get analysis
    analysis_query = select(AIAnalysisHistory).where(
        AIAnalysisHistory.id == request.analysis_id
    )
    result = await db.execute(analysis_query)
    analysis = result.scalar_one_or_none()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )
    
    # Verify owner
    await verify_room_owner(analysis.room_id, current_user.id, db)
    
    # Check if already applied
    if analysis.status == AnalysisStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This analysis has already been applied"
        )
    
    # Get subtasks
    subtasks = analysis.analysis_data.get("suggested_subtasks", [])
    
    # Filter by selected indices if provided
    if request.selected_subtask_indices is not None:
        subtasks = [
            st for i, st in enumerate(subtasks)
            if i in request.selected_subtask_indices
        ]
    
    # Create tasks
    created_tasks = []
    task_ids = []
    
    priority_map = {
        "low": TaskPriority.LOW,
        "medium": TaskPriority.MEDIUM,
        "high": TaskPriority.HIGH,
        "urgent": TaskPriority.URGENT
    }
    
    for subtask in subtasks:
        # Calculate deadline if suggested by AI
        due_date = None
        if subtask.get("due_date_days"):
            try:
                from datetime import timedelta
                days = int(subtask["due_date_days"])
                due_date = datetime.utcnow() + timedelta(days=days)
            except (ValueError, TypeError):
                pass  # Skip if invalid
        
        # Create task
        new_task = Task(
            title=subtask["title"],
            description=subtask["description"],
            room_id=analysis.room_id,
            status=TaskStatus.TODO,
            priority=priority_map.get(subtask.get("priority", "medium"), TaskPriority.MEDIUM),
            created_by_id=current_user.id,
            due_date=due_date  # Set deadline from AI suggestion
        )
        
        db.add(new_task)
        await db.flush()
        
        # Assign if user specified
        assignee_id = subtask.get("assigned_to_user_id")
        
        # Fallback: try to find user by username if ID is missing but username is present
        if not assignee_id and subtask.get("assigned_to_username"):
            username = subtask["assigned_to_username"]
            # Find user in room members - FIXED: explicitly specify join condition
            member_query = (
                select(RoomMember)
                .join(User, RoomMember.user_id == User.id)  # Explicit join condition
                .where(
                    RoomMember.room_id == analysis.room_id,
                    User.username == username
                )
            )
            member_result = await db.execute(member_query)
            member = member_result.scalar_one_or_none()
            if member:
                assignee_id = member.user_id

        if assignee_id:
            assignment = TaskAssignment(
                task_id=new_task.id,
                user_id=assignee_id,
                assigned_by_id=current_user.id
            )
            db.add(assignment)
            
            # Create notification for assigned user
            try:
                await create_task_assigned_notification(
                    db=db,
                    user_id=assignee_id,
                    task_id=new_task.id,
                    task_title=new_task.title,
                    assigned_by_name=current_user.username
                )
                
                # Send WebSocket notification
                await ws_manager.notify_task_assigned(
                    user_id=assignee_id,
                    task_data={
                        "task_id": new_task.id,
                        "title": new_task.title,
                        "assigned_by": current_user.username
                    }
                )
            except Exception as e:
                # Don't fail task creation if notification fails
                print(f"Failed to create notification: {e}")
        
        task_ids.append(new_task.id)
        created_tasks.append({
            "task_id": new_task.id,
            "title": new_task.title,
            "assigned_to": subtask.get("assigned_to_username"),
            "priority": subtask.get("priority")
        })
    
    # Update analysis status
    analysis.status = AnalysisStatus.APPROVED
    analysis.applied_at = datetime.utcnow()
    analysis.created_task_ids = task_ids
    
    await db.commit()
    
    # TODO: Send notifications to assigned users
    
    return ApplyBreakdownResponse(
        analysis_id=analysis.id,
        created_tasks=created_tasks,
        total_created=len(created_tasks),
        status="approved",
        applied_at=analysis.applied_at.isoformat()
    )


@router.get("/history/{room_id}", response_model=AnalysisHistoryResponse)
async def get_analysis_history(
    room_id: int,
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get AI analysis history for a room
    
    **OWNER ONLY**
    """
    # Verify owner
    await verify_room_owner(room_id, current_user.id, db)
    
    # Get analyses
    query = (
        select(AIAnalysisHistory)
        .where(AIAnalysisHistory.room_id == room_id)
        .order_by(desc(AIAnalysisHistory.created_at))
        .limit(limit)
        .offset(offset)
    )
    
    result = await db.execute(query)
    analyses = result.scalars().all()
    
    # Count total
    count_query = select(AIAnalysisHistory).where(AIAnalysisHistory.room_id == room_id)
    count_result = await db.execute(count_query)
    total = len(count_result.scalars().all())
    
    items = []
    for analysis in analyses:
        items.append(AnalysisHistoryItem(
            id=analysis.id,
            problem_description=analysis.problem_description[:200] + "..." if len(analysis.problem_description) > 200 else analysis.problem_description,
            status=analysis.status.value,
            overall_strategy=analysis.analysis_data.get("overall_strategy", ""),
            subtasks_count=len(analysis.analysis_data.get("suggested_subtasks", [])),
            created_tasks_count=len(analysis.created_task_ids),
            created_at=analysis.created_at.isoformat(),
            applied_at=analysis.applied_at.isoformat() if analysis.applied_at else None,
            model_used=analysis.analysis_data.get("model_used", "unknown")
        ))
    
    return AnalysisHistoryResponse(
        total=total,
        items=items
    )


@router.delete("/history/{analysis_id}")
async def delete_analysis(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an analysis (owner only)"""
    # Get analysis
    query = select(AIAnalysisHistory).where(AIAnalysisHistory.id == analysis_id)
    result = await db.execute(query)
    analysis = result.scalar_one_or_none()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # Verify owner
    await verify_room_owner(analysis.room_id, current_user.id, db)
    
    await db.delete(analysis)
    await db.commit()
    
    return {"message": "Analysis deleted"}


@router.get("/analysis/{analysis_id}", response_model=TaskBreakdownResponse)
async def get_analysis_details(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed analysis by ID (owner only)"""
    query = select(AIAnalysisHistory).where(AIAnalysisHistory.id == analysis_id)
    result = await db.execute(query)
    analysis = result.scalar_one_or_none()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # Verify owner
    await verify_room_owner(analysis.room_id, current_user.id, db)
    
    return TaskBreakdownResponse(
        analysis_id=analysis.id,
        overall_strategy=analysis.analysis_data.get("overall_strategy", ""),
        subtasks=[SubtaskSuggestion(**st) for st in analysis.analysis_data.get("suggested_subtasks", [])],
        problem_analysis=analysis.analysis_data.get("problem_analysis", {}),
        model_used=analysis.analysis_data.get("model_used", "unknown"),
        warnings=[],
        status=analysis.status.value,
        created_at=analysis.created_at.isoformat()
    )
