"""
Notification Service
Handles creating and managing notifications
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from notifications.models import Notification, NotificationType
from datetime import datetime
from typing import Optional, Dict, Any


async def create_notification(
    db: AsyncSession,
    user_id: int,
    notification_type: NotificationType,
    title: str,
    message: str,
    link_url: Optional[str] = None,
    payload: Optional[Dict[str, Any]] = None
) -> Notification:
    """Create a new notification"""
    notification = Notification(
        user_id=user_id,
        type=notification_type,
        title=title,
        message=message,
        link_url=link_url,
        payload=payload or {}
    )
    
    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    
    return notification


async def create_task_assigned_notification(
    db: AsyncSession,
    user_id: int,
    task_id: int,
    task_title: str,
    assigned_by_name: str
) -> Notification:
    """Create notification when task is assigned to user"""
    return await create_notification(
        db=db,
        user_id=user_id,
        notification_type=NotificationType.TASK_ASSIGNED,
        title="New Task Assigned",
        message=f"{assigned_by_name} assigned you to task: {task_title}",
        link_url=f"/tasks/{task_id}",
        payload={
            "task_id": task_id,
            "task_title": task_title,
            "assigned_by": assigned_by_name
        }
    )


async def get_user_notifications(
    db: AsyncSession,
    user_id: int,
    unread_only: bool = False,
    limit: int = 50
) -> list[Notification]:
    """Get user's notifications"""
    query = (
        select(Notification)
        .where(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .limit(limit)
    )
    
    if unread_only:
        query = query.where(Notification.is_read == False)
    
    result = await db.execute(query)
    return list(result.scalars().all())


async def mark_notifications_as_read(
    db: AsyncSession,
    notification_ids: list[int],
    user_id: int
) -> int:
    """Mark notifications as read"""
    stmt = (
        update(Notification)
        .where(
            Notification.id.in_(notification_ids),
            Notification.user_id == user_id
        )
        .values(is_read=True, read_at=datetime.utcnow())
    )
    
    result = await db.execute(stmt)
    await db.commit()
    
    return result.rowcount


async def get_unread_count(db: AsyncSession, user_id: int) -> int:
    """Get count of unread notifications"""
    query = select(Notification).where(
        Notification.user_id == user_id,
        Notification.is_read == False
    )
    
    result = await db.execute(query)
    return len(result.scalars().all())
