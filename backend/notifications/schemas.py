"""
Notification Schemas
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from .models import NotificationType


class NotificationCreate(BaseModel):
    """Create notification"""
    user_id: int
    type: NotificationType
    title: str
    message: str
    link_url: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None


class NotificationResponse(BaseModel):
    """Notification response"""
    id: int
    user_id: int
    type: NotificationType
    title: str
    message: str
    link_url: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class NotificationMarkRead(BaseModel):
    """Mark notification as read"""
    notification_ids: list[int]
