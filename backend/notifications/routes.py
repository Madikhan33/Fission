"""
Notification API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from auth.dep import get_current_user
from auth.models import User
from notifications.schemas import NotificationResponse, NotificationMarkRead
from notifications import service


router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/", response_model=list[NotificationResponse])
async def get_notifications(
    unread_only: bool = False,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's notifications"""
    notifications = await service.get_user_notifications(
        db=db,
        user_id=current_user.id,
        unread_only=unread_only,
        limit=limit
    )
    
    return notifications


@router.get("/unread-count", response_model=dict)
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get count of unread notifications"""
    count = await service.get_unread_count(db=db, user_id=current_user.id)
    return {"count": count}


@router.post("/mark-read")
async def mark_as_read(
    data: NotificationMarkRead,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark notifications as read"""
    count = await service.mark_notifications_as_read(
        db=db,
        notification_ids=data.notification_ids,
        user_id=current_user.id
    )
    
    return {"message": f"Marked {count} notifications as read"}


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a notification"""
    from notifications.models import Notification
    from sqlalchemy import select
    
    query = select(Notification).where(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    )
    result = await db.execute(query)
    notification = result.scalar_one_or_none()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    await db.delete(notification)
    await db.commit()
    
    return {"message": "Notification deleted"}


# WebSocket endpoint
from fastapi import WebSocket, WebSocketDisconnect
from notifications.websocket import manager
import json


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str | None = None
):
    """
    WebSocket endpoint for real-time notifications and AI updates
    
    Send token as query parameter: /notifications/ws?token=YOUR_TOKEN
    
    Messages you can send:
    - {"action": "subscribe_analysis", "analysis_id": 123} - Subscribe to AI progress
    
    Messages you'll receive:
    - {"type": "analysis_update", "analysis_id": 123, "status": "...", "message": "..."}
    - {"type": "task_assigned", "data": {...}}
    - {"type": "new_notification", "data": {...}}
    """
    # Verify token and get user
    if not token:
        await websocket.close(code=1008, reason="Missing token")
        return
    
    try:
        from auth.security_service import decode_token
        payload = decode_token(token)
        if not payload:
            await websocket.close(code=1008, reason="Invalid token")
            return
        
        user_id = int(payload.get("sub"))
    except:
        await websocket.close(code=1008, reason="Invalid token")
        return
    
    # Connect the websocket
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different actions
            if message.get("action") == "subscribe_analysis":
                analysis_id = message.get("analysis_id")
                if analysis_id:
                    await manager.subscribe_to_analysis(websocket, analysis_id)
                    await websocket.send_json({
                        "type": "subscribed",
                        "analysis_id": analysis_id
                    })
            
            elif message.get("action") == "ping":
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        manager.disconnect(websocket, user_id)
        print(f"WebSocket error: {e}")
