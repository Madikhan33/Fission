"""
Notification System Models
"""

from core.database import Base
from datetime import datetime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, ForeignKey, Boolean, Text, Enum, JSON
import enum


class NotificationType(enum.Enum):
    """Types of notifications"""
    TASK_ASSIGNED = "task_assigned"  # When a task is assigned to you
    TASK_UPDATED = "task_updated"    # When a task you're assigned to is updated
    TASK_COMPLETED = "task_completed"  # When someone completes a task
    ROOM_INVITE = "room_invite"      # When you're invited to a room
    AI_ANALYSIS_COMPLETE = "ai_analysis_complete"  # When AI analysis is done
    MENTION = "mention"              # When you're mentioned


class Notification(Base):
    """User notifications"""
    __tablename__ = "notifications"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Who receives the notification
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Notification details
    type: Mapped[NotificationType] = mapped_column(Enum(NotificationType), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Optional link to related entity
    link_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    # JSON payload (renamed from metadata to avoid SQLAlchemy conflict)
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
    # Read status
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    read_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="notifications")
    
    def __repr__(self):
        return f"Notification(id={self.id}, type={self.type.value}, user_id={self.user_id}, is_read={self.is_read})"
