"""
WebSocket Manager for real-time updates
Handles AI analysis progress updates and notifications
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
import asyncio


class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        # user_id -> set of websockets
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        
        #analysis_id -> set of websockets (for AI progress tracking)
        self.analysis_watchers: Dict[int, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """Connect a user's websocket"""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        
        self.active_connections[user_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        """Disconnect a user's websocket"""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        
        # Also remove from analysis watchers
        for analysis_id in list(self.analysis_watchers.keys()):
            self.analysis_watchers[analysis_id].discard(websocket)
            if not self.analysis_watchers[analysis_id]:
                del self.analysis_watchers[analysis_id]
    
    async def send_personal_message(self, message: dict, user_id: int):
        """Send message to specific user"""
        if user_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except:
                    disconnected.append(connection)
            
            # Clean up disconnected connections
            for conn in disconnected:
                self.active_connections[user_id].discard(conn)
    
    async def subscribe_to_analysis(self, websocket: WebSocket, analysis_id: int):
        """Subscribe to AI analysis updates"""
        if analysis_id not in self.analysis_watchers:
            self.analysis_watchers[analysis_id] = set()
        
        self.analysis_watchers[analysis_id].add(websocket)
    
    async def send_analysis_update(self, analysis_id: int, update: dict):
        """Send update to all watchers of an analysis"""
        if analysis_id in self.analysis_watchers:
            disconnected = []
            for connection in self.analysis_watchers[analysis_id]:
                try:
                    await connection.send_json({
                        "type": "analysis_update",
                        "analysis_id": analysis_id,
                        **update
                    })
                except:
                    disconnected.append(connection)
            
            # Clean up disconnected
            for conn in disconnected:
                self.analysis_watchers[analysis_id].discard(conn)
    
    async def notify_task_assigned(self, user_id: int, task_data: dict):
        """Notify user about task assignment"""
        await self.send_personal_message({
            "type": "task_assigned",
            "data": task_data
        }, user_id)
    
    async def notify_new_notification(self, user_id: int, notification_data: dict):
        """Notify user about new notification"""
        await self.send_personal_message({
            "type": "new_notification",
            "data": notification_data
        }, user_id)


# Global connection manager instance
manager = ConnectionManager()
