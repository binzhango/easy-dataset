"""
WebSocket API for streaming LLM responses and task progress updates.

This module provides WebSocket endpoints for real-time communication
with the frontend, supporting LLM streaming and task progress updates.
"""

import asyncio
import json
import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session

from easy_dataset.database.connection import get_db
from easy_dataset.models.task import Task, TaskStatus
from easy_dataset.llm.service import LLMService

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections for streaming."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.task_subscribers: Dict[str, set[str]] = {}  # task_id -> set of connection_ids
    
    async def connect(self, websocket: WebSocket, connection_id: str):
        """Accept and store a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        logger.info(f"WebSocket connection established: {connection_id}")
    
    def disconnect(self, connection_id: str):
        """Remove a WebSocket connection."""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
            logger.info(f"WebSocket connection closed: {connection_id}")
        
        # Remove from task subscriptions
        for task_id, subscribers in list(self.task_subscribers.items()):
            if connection_id in subscribers:
                subscribers.remove(connection_id)
                if not subscribers:
                    del self.task_subscribers[task_id]
    
    def subscribe_to_task(self, connection_id: str, task_id: str):
        """Subscribe a connection to task updates."""
        if task_id not in self.task_subscribers:
            self.task_subscribers[task_id] = set()
        self.task_subscribers[task_id].add(connection_id)
        logger.debug(f"Connection {connection_id} subscribed to task {task_id}")
    
    def unsubscribe_from_task(self, connection_id: str, task_id: str):
        """Unsubscribe a connection from task updates."""
        if task_id in self.task_subscribers:
            self.task_subscribers[task_id].discard(connection_id)
            if not self.task_subscribers[task_id]:
                del self.task_subscribers[task_id]
            logger.debug(f"Connection {connection_id} unsubscribed from task {task_id}")
    
    async def send_personal_message(self, message: Dict[str, Any], connection_id: str):
        """Send a message to a specific connection."""
        if connection_id in self.active_connections:
            try:
                await self.active_connections[connection_id].send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to {connection_id}: {e}")
                self.disconnect(connection_id)
    
    async def broadcast_task_update(self, task_id: str, message: Dict[str, Any]):
        """Broadcast a task update to all subscribed connections."""
        if task_id in self.task_subscribers:
            disconnected = []
            for connection_id in self.task_subscribers[task_id]:
                try:
                    await self.send_personal_message(message, connection_id)
                except Exception as e:
                    logger.error(f"Error broadcasting to {connection_id}: {e}")
                    disconnected.append(connection_id)
            
            # Clean up disconnected connections
            for connection_id in disconnected:
                self.disconnect(connection_id)


# Global connection manager instance
manager = ConnectionManager()


@router.websocket("/ws/llm-stream")
async def llm_stream_endpoint(
    websocket: WebSocket,
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for streaming LLM responses.
    
    Expected message format:
    {
        "type": "generate",
        "provider": "openai",
        "model": "gpt-4",
        "messages": [{"role": "user", "content": "Hello"}],
        "stream": true
    }
    
    Response format:
    {
        "type": "chunk",
        "content": "Hello",
        "done": false
    }
    """
    connection_id = f"llm_{id(websocket)}"
    await manager.connect(websocket, connection_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            if data.get("type") == "generate":
                try:
                    # Extract parameters
                    provider = data.get("provider")
                    model = data.get("model")
                    messages = data.get("messages", [])
                    stream = data.get("stream", True)
                    temperature = data.get("temperature", 0.7)
                    max_tokens = data.get("max_tokens", 2048)
                    
                    # Create LLM service
                    llm_service = LLMService(db)
                    
                    # Get provider configuration
                    config = {
                        "provider": provider,
                        "model": model,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                    }
                    
                    if stream:
                        # Stream response
                        async for chunk in llm_service.chat_stream(config, messages):
                            await websocket.send_json({
                                "type": "chunk",
                                "content": chunk,
                                "done": False
                            })
                        
                        # Send completion message
                        await websocket.send_json({
                            "type": "chunk",
                            "content": "",
                            "done": True
                        })
                    else:
                        # Non-streaming response
                        response = await llm_service.chat(config, messages)
                        await websocket.send_json({
                            "type": "response",
                            "content": response.get("content", ""),
                            "done": True
                        })
                
                except Exception as e:
                    logger.error(f"Error in LLM generation: {e}", exc_info=True)
                    await websocket.send_json({
                        "type": "error",
                        "message": str(e)
                    })
            
            elif data.get("type") == "ping":
                # Respond to ping
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {connection_id}")
        manager.disconnect(connection_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        manager.disconnect(connection_id)


@router.websocket("/ws/task-progress/{task_id}")
async def task_progress_endpoint(
    websocket: WebSocket,
    task_id: str,
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for streaming task progress updates.
    
    Automatically sends updates when task status or progress changes.
    
    Response format:
    {
        "type": "progress",
        "task_id": "abc123",
        "status": "processing",
        "progress": 50,
        "current_count": 50,
        "total_count": 100,
        "message": "Processing..."
    }
    """
    connection_id = f"task_{task_id}_{id(websocket)}"
    await manager.connect(websocket, connection_id)
    manager.subscribe_to_task(connection_id, task_id)
    
    try:
        # Send initial task status
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            await websocket.send_json({
                "type": "progress",
                "task_id": task.id,
                "status": task.status.value if task.status else "unknown",
                "progress": task.progress or 0,
                "current_count": task.current_count or 0,
                "total_count": task.total_count or 0,
                "message": task.note or ""
            })
        else:
            await websocket.send_json({
                "type": "error",
                "message": f"Task {task_id} not found"
            })
            return
        
        # Keep connection alive and poll for updates
        last_progress = task.progress
        last_status = task.status
        
        while True:
            # Wait for a short period
            await asyncio.sleep(1)
            
            # Check for updates
            db.refresh(task)
            
            # Send update if changed
            if task.progress != last_progress or task.status != last_status:
                await websocket.send_json({
                    "type": "progress",
                    "task_id": task.id,
                    "status": task.status.value if task.status else "unknown",
                    "progress": task.progress or 0,
                    "current_count": task.current_count or 0,
                    "total_count": task.total_count or 0,
                    "message": task.note or ""
                })
                
                last_progress = task.progress
                last_status = task.status
            
            # Close connection if task is complete or failed
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELED]:
                await websocket.send_json({
                    "type": "complete",
                    "task_id": task.id,
                    "status": task.status.value,
                    "message": "Task finished"
                })
                break
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {connection_id}")
        manager.disconnect(connection_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        manager.disconnect(connection_id)


async def broadcast_task_update(task_id: str, task_data: Dict[str, Any]):
    """
    Helper function to broadcast task updates to all subscribed connections.
    
    This can be called from task processing code to push updates.
    """
    message = {
        "type": "progress",
        **task_data
    }
    await manager.broadcast_task_update(task_id, message)
