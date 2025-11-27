from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime
from typing import List

# --- Resume Analysis Schemas ---


class ResumeExtraction(BaseModel):
    full_name: str = Field(description="Full name of the candidate")
    email: Optional[str] = Field(description="Email address")
    phone: Optional[str] = Field(description="Phone number")
    location: Optional[str] = Field(description="City, Country")
    current_position: Optional[str] = Field(description="Current job title")
    years_of_experience: Optional[int] = Field(description="Total years of experience")
    career_level: Optional[str] = Field(description="Junior, Middle, Senior, Lead, etc.")
    professional_summary: Optional[str] = Field(description="Brief professional summary (2-3 sentences)")
    core_skills: List[str] = Field(description="Top 10-15 key skills")
    work_experience_summary: Optional[str] = Field(description="Summary of work experience (companies + roles)")
    project_experience_summary: Optional[str] = Field(description="Summary of key projects")
    education_summary: Optional[str] = Field(description="Degree + University")
    languages: List[str] = Field(description="Languages with proficiency, e.g., 'English: fluent'")





class ResumeAnalysisBase(BaseModel):
    full_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    current_position: Optional[str] = None
    years_of_experience: Optional[int] = None
    career_level: Optional[str] = None
    professional_summary: Optional[str] = None
    core_skills: Optional[str] = None
    work_experience_summary: Optional[str] = None
    project_experience_summary: Optional[str] = None
    education_summary: Optional[str] = None
    languages: Optional[str] = None

class ResumeAnalysisCreate(ResumeAnalysisBase):
    pass

class ResumeAnalysisUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    current_position: Optional[str] = None
    years_of_experience: Optional[int] = None
    career_level: Optional[str] = None
    professional_summary: Optional[str] = None
    core_skills: Optional[str] = None
    work_experience_summary: Optional[str] = None
    project_experience_summary: Optional[str] = None
    education_summary: Optional[str] = None
    languages: Optional[str] = None

class ResumeAnalysisResponse(ResumeAnalysisBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)