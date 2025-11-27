from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_db
from auth.dep import get_current_user
from auth.models import User
from .models import ResumeAnalysis

async def get_resume_analysis(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ResumeAnalysis | None:
    """
    Get resume analysis for the current user.
    Returns None if not found.
    """
    query = select(ResumeAnalysis).where(ResumeAnalysis.user_id == user.id)
    result = await db.execute(query)
    analysis = result.scalar_one_or_none()
    
    return analysis

async def get_existing_resume_analysis(
    analysis: ResumeAnalysis | None = Depends(get_resume_analysis)
) -> ResumeAnalysis:
    """
    Dependency to get resume analysis, raising 404 if not found.
    """
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume analysis not found"
        )
    return analysis