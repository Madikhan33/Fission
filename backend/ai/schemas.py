"""
Enhanced Pydantic schemas for AI agent endpoints
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


class ProblemAnalysisRequest(BaseModel):
    """Request to analyze a problem"""
    problem_description: str = Field(..., description="Problem description text")
    language: str = Field("en", description="Language code: en, ru, kk")


class ProblemAnalysisResponse(BaseModel):
    """Response from problem analysis"""
    problem_summary: str
    problem_type: str
    priority: str
    required_skills: List[str]
    estimated_complexity: str
    keywords: List[str]
    language: str


class SubtaskSuggestion(BaseModel):
    """Single subtask suggestion"""
    title: str
    description: str
    assigned_to_user_id: Optional[int]
    assigned_to_username: Optional[str]
    priority: str
    estimated_time: str  # Human-readable like "2-3 days"
    estimated_hours: Optional[int] = Field(None, description="Estimated hours for completion")
    due_date_days: Optional[int] = Field(None, description="Days from now for deadline")
    complexity_score: Optional[int] = Field(None, description="Complexity: 1=trivial, 3=simple, 5=moderate, 7=complex, 10=very complex")
    required_skills: List[str]
    reasoning: str


class TaskBreakdownRequest(BaseModel):
    """Request for AI task breakdown"""
    room_id: int = Field(..., description="Room ID")
    problem_description: str = Field(..., description="Problem to analyze and break down")
    language: str = Field("en", description="Language: en, ru, kk")
    use_reasoning_model: Optional[bool] = Field(None, description="Force use of reasoning model (o1-mini)")


class TaskBreakdownResponse(BaseModel):
    """Response with complete task breakdown"""
    analysis_id: int = Field(..., description="ID of saved analysis")
    overall_strategy: str
    subtasks: List[SubtaskSuggestion]
    problem_analysis: dict
    model_used: str
    warnings: List[str]
    status: str = Field("pending", description="Analysis status")
    created_at: str


class ApplyBreakdownRequest(BaseModel):
    """Request to apply (create tasks from) a breakdown"""
    analysis_id: int = Field(..., description="ID of the analysis to apply")
    selected_subtask_indices: Optional[List[int]] = Field(
        None,
        description="Indices of subtasks to create (None = all)"
    )


class ApplyBreakdownResponse(BaseModel):
    """Response after applying breakdown"""
    analysis_id: int
    created_tasks: List[dict]
    total_created: int
    status: str
    applied_at: str


class AnalysisHistoryItem(BaseModel):
    """Single analysis history item"""
    id: int
    problem_description: str
    status: str
    overall_strategy: str
    subtasks_count: int
    created_tasks_count: int
    created_at: str
    applied_at: Optional[str]
    model_used: str


class AnalysisHistoryResponse(BaseModel):
    """List of analysis history"""
    total: int
    items: List[AnalysisHistoryItem]
