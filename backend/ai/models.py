from core.database import Base
from datetime import datetime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, ForeignKey, Text, Enum, JSON
import enum


class AnalysisStatus(enum.Enum):
    """Status of AI analysis"""
    PENDING = "pending"          # Анализ готов, ждет подтверждения
    APPROVED = "approved"        # Одобрен и применен
    REJECTED = "rejected"        # Отклонен
    PARTIALLY_APPLIED = "partially_applied"  # Частично применен


class AIAnalysisHistory(Base):
    """
    History of AI analyses and decided task breakdowns
    Stores what AI suggested and whether it was applied
    """
    __tablename__ = "ai_analysis_history"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Room and user context
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    # Original problem
    problem_description: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)  # ru, en, kk
    
    # AI Analysis result (stored as JSON)
    analysis_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    # Structure:
    # {
    #   "problem_analysis": {...},
    #   "suggested_subtasks": [
    #     {
    #       "title": "...",
    #       "description": "...",
    #       "assigned_to_user_id": ...,
    #       "assigned_to_username": "...",
    #       "priority": "...",
    #       "estimated_time": "...",
    #       "reasoning": "..."
    #     },
    #     ...
    #   ],
    #   "overall_strategy": "...",
    #   "model_used": "gpt-4o" or "o1-mini"
    # }
    
    # Status tracking
    status: Mapped[AnalysisStatus] = mapped_column(
        Enum(AnalysisStatus),
        default=AnalysisStatus.PENDING,
        nullable=False
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    applied_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # Applied tasks (if approved)
    created_task_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    # List of task IDs that were created from this analysis
    
    # Feedback (optional)
    user_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Relationships
    room: Mapped["Room"] = relationship("Room", back_populates="ai_analyses")
    created_by: Mapped["User"] = relationship("User", foreign_keys=[created_by_id])
    
    def __repr__(self):
        return f"AIAnalysisHistory(id={self.id}, room_id={self.room_id}, status={self.status.value})"
