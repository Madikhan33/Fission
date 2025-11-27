"""
AI Agent Tools
Functions that the AI agent can call to gather information
All tools work within a specific room context
"""

from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import joinedload

from auth.models import User
from rooms.models import Room, RoomMember
from my_tasks.models import Task, TaskStatus, TaskAssignment
from resume_ai.models import ResumeAnalysis
import json


async def get_room_members(
    room_id: int,
    db: AsyncSession
) -> List[Dict]:
    """
    Get all members of a specific room with their basic info
    
    Args:
        room_id: ID of the room
        db: Database session
        
    Returns:
        List of room members with their roles and basic info
    """
    query = (
        select(RoomMember)
        .where(RoomMember.room_id == room_id)
        .options(joinedload(RoomMember.user))
    )
    
    result = await db.execute(query)
    members = result.scalars().all()
    
    return [
        {
            "user_id": member.user.id,
            "username": member.user.username,
            "email": member.user.email,
            "role_in_room": member.role.value,
            "is_lead": member.user.is_lead,
            "joined_at": member.joined_at.isoformat()
        }
        for member in members
    ]


async def find_employees_by_skills(
    room_id: int,
    required_skills: List[str],
    db: AsyncSession,
    role: Optional[str] = None,
    min_experience_years: Optional[int] = None
) -> List[Dict]:
    """
    Find room members with specific skills
    Uses resume analysis data to match skills
    
    Args:
        room_id: ID of the room (only search within this room)
        required_skills: List of required skills (e.g., ["Python", "FastAPI"])
        db: Database session
        role: Optional role filter (e.g., "backend", "frontend")
        min_experience_years: Minimum years of experience
        
    Returns:
        List of matching users with their skills and experience
    """
    # Get room members first
    members_query = (
        select(RoomMember.user_id)
        .where(RoomMember.room_id == room_id)
    )
    members_result = await db.execute(members_query)
    room_member_ids = [row[0] for row in members_result.all()]
    
    if not room_member_ids:
        return []
    
    # Now find users with matching skills from room members only
    query = (
        select(User, ResumeAnalysis)
        .join(ResumeAnalysis, User.id == ResumeAnalysis.user_id)
        .where(User.id.in_(room_member_ids))
    )
    
    # Add experience filter if specified
    if min_experience_years is not None:
        query = query.where(
            ResumeAnalysis.years_of_experience >= min_experience_years
        )
    
    result = await db.execute(query)
    users_with_resume = result.all()
    
    matched_users = []
    
    for user, resume in users_with_resume:
        # Parse skills from core_skills JSON field
        try:
            if resume.core_skills:
                user_skills = json.loads(resume.core_skills)
            else:
                user_skills = []
        except:
            user_skills = []
        
        # Check if user has any of the required skills (case-insensitive)
        user_skills_lower = [skill.lower() for skill in user_skills]
        required_skills_lower = [skill.lower() for skill in required_skills]
        
        matching_skills = [
            skill for skill in user_skills 
            if skill.lower() in required_skills_lower
        ]
        
        # Also check role if specified
        if role and resume.current_position:
            role_match = role.lower() in resume.current_position.lower()
        else:
            role_match = True
        
        if matching_skills and role_match:
            matched_users.append({
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "current_position": resume.current_position,
                "years_of_experience": resume.years_of_experience,
                "career_level": resume.career_level,
                "matching_skills": matching_skills,
                "all_skills": user_skills,
                "professional_summary": resume.professional_summary,
                "match_score": len(matching_skills) / len(required_skills) * 100
            })
    
    # Sort by match score (highest first)
    matched_users.sort(key=lambda x: x["match_score"], reverse=True)
    
    return matched_users


async def get_recent_tasks(
    room_id: int,
    db: AsyncSession,
    topic: Optional[str] = None,
    limit: int = 20,
    status: Optional[TaskStatus] = None
) -> List[Dict]:
    """
    Get recent tasks from the room, optionally filtered by topic/status
    
    Args:
        room_id: ID of the room
        db: Database session
        topic: Optional topic to filter by (searches in title and description)
        limit: Maximum number of tasks to return
        status: Optional status filter
        
    Returns:
        List of recent tasks with details
    """
    query = (
        select(Task)
        .where(Task.room_id == room_id)
        .options(
            joinedload(Task.created_by),
            joinedload(Task.assignments).joinedload(TaskAssignment.user)  # Added proper eager loading
        )
        .order_by(Task.created_at.desc())
        .limit(limit)
    )
    
    # Add status filter if specified
    if status:
        query = query.where(Task.status == status)
    
    # Add topic filter if specified
    if topic:
        query = query.where(
            or_(
                Task.title.ilike(f"%{topic}%"),
                Task.description.ilike(f"%{topic}%")
            )
        )
    
    result = await db.execute(query)
    tasks = result.scalars().all()
    
    return [
        {
            "task_id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status.value,
            "priority": task.priority.value,
            "created_by": task.created_by.username,
            "created_at": task.created_at.isoformat(),
            "assignees": [
                {
                    "user_id": assignment.user.id,
                    "username": assignment.user.username
                }
                for assignment in task.assignments
            ],
            "due_date": task.due_date.isoformat() if task.due_date else None
        }
        for task in tasks
    ]


async def get_user_resume(
    user_id: int,
    db: AsyncSession
) -> Optional[Dict]:
    """
    Get detailed resume information for a specific user
    
    Args:
        user_id: ID of the user
        db: Database session
        
    Returns:
        User's resume data or None if not found
    """
    query = select(ResumeAnalysis).where(ResumeAnalysis.user_id == user_id)
    result = await db.execute(query)
    resume = result.scalar_one_or_none()
    
    if not resume:
        return None
    
    try:
        core_skills = json.loads(resume.core_skills) if resume.core_skills else []
    except:
        core_skills = []
    
    try:
        languages = json.loads(resume.languages) if resume.languages else []
    except:
        languages = []
    
    return {
        "user_id": user_id,
        "full_name": resume.full_name,
        "email": resume.email,
        "phone": resume.phone,
        "location": resume.location,
        "current_position": resume.current_position,
        "years_of_experience": resume.years_of_experience,
        "career_level": resume.career_level,
        "professional_summary": resume.professional_summary,
        "core_skills": core_skills,
        "work_experience_summary": resume.work_experience_summary,
        "project_experience_summary": resume.project_experience_summary,
        "education_summary": resume.education_summary,
        "languages": languages
    }


async def get_room_info(
    room_id: int,
    db: AsyncSession
) -> Optional[Dict]:
    """
    Get detailed information about a room
    
    Args:
        room_id: ID of the room
        db: Database session
        
    Returns:
        Room information or None if not found
    """
    query = (
        select(Room)
        .where(Room.id == room_id)
        .options(
            joinedload(Room.created_by),
            joinedload(Room.members)
        )
    )
    
    result = await db.execute(query)
    room = result.scalar_one_or_none()
    
    if not room:
        return None
    
    return {
        "room_id": room.id,
        "name": room.name,
        "description": room.description,
        "created_by": room.created_by.username,
        "created_at": room.created_at.isoformat(),
        "total_members": len(room.members)
    }
