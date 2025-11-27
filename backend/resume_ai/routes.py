from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_db
from auth.dep import get_current_user
from auth.models import User
from .models import ResumeAnalysis
from .schemas import (
    ResumeAnalysisCreate,
    ResumeAnalysisUpdate,
    ResumeAnalysisResponse
)
from .dep import get_resume_analysis
from .ai import extract_data_from_pdf

router = APIRouter(prefix="/resume-ai", tags=["Resume AI"])

# --- Resume Analysis Routes ---

@router.post("/upload", response_model=ResumeAnalysisResponse)
async def upload_resume(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a PDF resume, extract data using AI, and save/update the user's resume profile.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    
    content = await file.read()
    
    try:
        # Extract data using AI
        extracted_data = await extract_data_from_pdf(content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred during AI processing.")

    # Check if analysis already exists
    query = select(ResumeAnalysis).where(ResumeAnalysis.user_id == user.id)
    result = await db.execute(query)
    existing_analysis = result.scalar_one_or_none()

    if existing_analysis:
        # Update existing
        for key, value in extracted_data.items():
            setattr(existing_analysis, key, value)
        db.add(existing_analysis)
        await db.commit()
        await db.refresh(existing_analysis)
        return existing_analysis
    else:
        # Create new
        new_analysis = ResumeAnalysis(**extracted_data, user_id=user.id)
        db.add(new_analysis)
        await db.commit()
        await db.refresh(new_analysis)
        return new_analysis

@router.get("/", response_model=ResumeAnalysisResponse | None)
async def get_my_resume_analysis(
    analysis: ResumeAnalysis | None = Depends(get_resume_analysis)
):
    """
    Get the current user's resume analysis data.
    """
    return analysis

@router.patch("/", response_model=ResumeAnalysisResponse)
async def update_resume_analysis(
    resume_update: ResumeAnalysisUpdate,
    analysis: ResumeAnalysis | None = Depends(get_resume_analysis),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Manually update specific fields of the resume analysis.
    """
    if not analysis:
        raise HTTPException(status_code=404, detail="Resume analysis not found. Please upload a resume first.")

    update_data = resume_update.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(analysis, key, value)

    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)
    return analysis
